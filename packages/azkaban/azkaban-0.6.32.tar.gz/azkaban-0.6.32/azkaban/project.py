#!/usr/bin/env python
# encoding: utf-8

"""Project definition module."""

from os import sep
from os.path import (abspath, basename, dirname, exists, isabs, isdir, join,
  realpath, relpath, splitext)
from traceback import format_exc
from weakref import WeakValueDictionary
from zipfile import ZipFile
from .util import AzkabanError, Adapter, flatten, temppath, write_properties
import logging
import sys


_logger = logging.getLogger(__name__)


class _JobDict(dict):

  """Simple dictionary subclass for jobs.

  It disables the default `__setitem__` method and implements a custom
  `KeyError` exception. Note that this isn't completely fool-proof but enough
  for our purpose.

  """

  def __getitem__(self, key):
    try:
      return super(_JobDict, self).__getitem__(key)
    except KeyError:
      raise AzkabanError('Job %r not found.', key)

  def __setitem__(self, key, value):
    raise AzkabanError('Cannot insert job. Use `Project.add_job` instead.')


class Project(object):

  """Azkaban project.

  :param name: Name of the project.
  :param register: Add project to registry. Setting this to `False` will make
    it invisible to the CLI.
  :param root: Path to a root file or directory used to enable adding files
    using relative paths (typically used with `root=__file__`).
  :param version: Project version, currently only used for setting the name
    of the archive uploaded to Azkaban.

  The `properties` attribute of a project is a dictionary which can be used to
  pass Azkaban options which will then be available to all jobs in the project.
  This can be used for example to set project wide defaults.

  To avoid undefined behavior, both the `name` and `root` attributes should not
  be altered after instantiation.

  """

  root = None
  _registry = WeakValueDictionary()

  def __init__(self, name, root=None, register=True, version=None):
    self.name = name
    self.version = version
    if root:
      self.root = abspath(root if isdir(root) else dirname(root))
    if register:
      self._registry[name] = self
    self._jobs = {}
    self._files = {}
    self.properties = {}
    self._logger = Adapter(repr(self), _logger)
    self._logger.debug('Instantiated.')

  def __repr__(self):
    return '<%s(name=%r, root=%r)>' % (
      self.__class__.__name__, self.name, self.root
    )

  def __str__(self):
    return self.name

  @property
  def versioned_name(self):
    """Project name, including version if present."""
    return '%s-%s' % (self.name, self.version) if self.version else self.name

  @property
  def files(self):
    """Returns a list of tuples of files included in the project archive.

    The first element of each tuple is the absolute local path to the file, the
    second the path of the file in the archive.

    .. note::

      This property should not be used to add files. Use :meth:`add_file`
      instead.

    """
    return [(e[1][0], e[0]) for e in self._files.items()]

  @property
  def jobs(self):
    """Returns a dictionary of all jobs in the project, keyed by name.

    .. note::

      This property should not be used to add jobs. Use :meth:`add_job`
      instead.

    """
    return _JobDict(self._jobs)

  def add_file(self, path, archive_path=None, overwrite=False):
    """Include a file in the project archive.

    :param path: Path to file. If no project `root` exists, only absolute paths
      are allowed. Otherwise, this path can also be relative to said `root`.
    :param archive_path: Path to file in archive (defaults to same as `path`).
    :param overwrite: Allow overwriting any previously existing file in this
      archive path.

    If the current project has its `root` parameter specified, this method will
    allow relative paths (and join those with the project's `root`), otherwise
    it will throw an error. Furthermore, when a project `root` exists, adding
    files above it without specifying an `archive_path` will raise an error.
    This is done to avoid having files in the archive with lower level
    destinations than the base root directory.

    """
    if not isabs(path):
      if not self.root:
        raise AzkabanError(
          'Relative path not allowed without specifying a project root: %r.'
          % (path, )
        )
      path = join(self.root, path)
    # disambiguate (symlinks, pardirs, etc.)
    path = realpath(path)
    if archive_path:
      frozen = True
    else:
      frozen = False
      if self.root:
        if not path.startswith(self.root):
          raise AzkabanError(
            'Cannot add a file outside of the project root directory without\n'
            'specifying an archive path: %r' % (path, )
          )
        archive_path = relpath(path, self.root)
      else:
        archive_path = path
    # leading separator meaningless inside archive (trimmed automatically)
    archive_path = archive_path.lstrip('/')
    if (
      archive_path in self._files and
      self._files[archive_path][0] != path and
      not overwrite
    ):
      raise AzkabanError('Inconsistent duplicate file: %r.' % (path, ))
    if not exists(path):
      raise AzkabanError('File not found: %r.' % (path, ))
    self._files[archive_path] = (path, frozen)
    self._logger.info('Added file %r as %r.', path, archive_path)

  def add_job(self, name, job, **kwargs):
    """Include a job in the project.

    :param name: Name assigned to job (must be unique).
    :param job: :class:`~azkaban.job.Job` instance.
    :param kwargs: Keyword arguments that will be forwarded to the
      :meth:`~azkaban.job.Job.on_add` handler.

    This method triggers the :meth:`~azkaban.job.Job.on_add` method on the
    added job (passing the project and name as arguments, along with any
    `kwargs`). The handler will be called right after the job is added.

    """
    if not job is self._jobs.get(name, job):
      raise AzkabanError('Inconsistent duplicate job: %r.' % (name, ))
    job.on_add(self, name, **kwargs)
    self._jobs[name] = job
    self._logger.info('Added job %r.', name)

  def merge_into(self, project, overwrite=False, unregister=False):
    """Merge one project with another.

    :param project: Target :class:`Project` to merge into.
    :param overwrite: Overwrite any existing files.
    :param unregister: Unregister project after merging it.

    The current project remains unchanged while the target project gains all
    the current project's jobs and files.

    """
    self._logger.debug('Merging into %r.', project)
    for name, job in self._jobs.items():
      project.add_job(name, job, merging=self)
    for archive_path, (path, frozen) in self._files.items():
      if frozen:
        # propagate the archive path
        project.add_file(path, archive_path=archive_path, overwrite=overwrite)
      else:
        # autogenerate a new archive_path
        project.add_file(path, overwrite=overwrite)
    if unregister:
      self._registry.pop(self.name)

  def build(self, path, overwrite=False):
    """Create the project archive.

    :param path: Destination path.
    :param overwrite: Don't throw an error if a file already exists at `path`.

    """
    self._logger.debug('Building.')
    # not using a with statement for compatibility with older python versions
    if exists(path) and not overwrite:
      raise AzkabanError('Path %r already exists.' % (path, ))
    if not (len(self._jobs) or len(self._files)):
      raise AzkabanError('Building empty project.')
    writer = ZipFile(path, 'w')
    try:
      if self.properties:
        with temppath() as fpath:
          write_properties(flatten(self.properties), fpath)
          writer.write(fpath, 'project.properties')
      for name, job in self._jobs.items():
        with temppath() as fpath:
          job.build(fpath)
          writer.write(fpath, '%s.job' % (name, ))
      for archive_path, (fpath, _) in self._files.items():
        writer.write(fpath, archive_path)
    finally:
      writer.close()
    self._logger.info('Built as %s.', path)

  @classmethod
  def load(cls, module, path=None, name=None):
    """Load project from script.

    :param module: Name of the module where the project is defined.
    :param path: If the module isn't on the $PYTHONPATH, this argument can be
      used to make the module accessible.
    :param name: Project name. If not specified and a single project is found
      while loading the script, that project is returned. In any other case
      (no/multiple projects found), an error is thrown.

    Note that only registered projects (i.e. instantiated with `register=True`)
    can be loaded via this method.

    """
    if path:
      sys.path.insert(0, path)
    __import__(module)
    if name:
      try:
        return cls._registry[name]
      except KeyError:
        raise AzkabanError(
          'Unable to find a registered project with name %r in module %r.\n'
          'Available projects: %s.'
          % (name, path, ', '.join(cls._registry))
        )
    else:
      if len(cls._registry) == 1:
        return cls._registry.popitem()[1]
      elif not cls._registry:
        raise AzkabanError('No registered project found in %r.' % (path, ))
      else:
        raise AzkabanError(
          'Multiple registered projects found in %r: %s.\n'
          'Disambiguate using --project=%s:project_name.'
          % (path, ', '.join(cls._registry), path)
        )
