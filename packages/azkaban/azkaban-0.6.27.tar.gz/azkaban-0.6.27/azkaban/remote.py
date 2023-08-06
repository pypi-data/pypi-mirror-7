#!/usr/bin/env python
# encoding: utf-8

"""Azkaban remote interaction module.

This contains the `Session` class which will be used for all interactions with
a remote Azkaban server.

"""

from .util import AzkabanError, Config, InstanceLogger, MultipartForm, flatten
from getpass import getpass, getuser
from os.path import basename, exists
from requests.exceptions import HTTPError
from six import string_types
from six.moves.configparser import NoOptionError, NoSectionError
from time import sleep
import logging as lg
import requests as rq


logger = lg.getLogger(__name__)

def _azkaban_request(method, url, **kwargs):
  """Make request to azkaban server and catch common errors.

  :param method: GET, POST, etc.
  :param url: Endpoint url.
  :param **kwargs: Arguments forwarded to the request handler.

  This function is meant to handle common errors and return a more helpful
  message than the default one.

  """
  try:
    handler = getattr(rq, method.lower())
  except AttributeError:
    raise ValueError('Invalid HTTP method: %r.' % (method, ))
  else:
    try:
      response = handler(url, verify=False, **kwargs)
    except rq.ConnectionError:
      raise AzkabanError('Unable to connect to Azkaban server %r.', url)
    except rq.exceptions.MissingSchema:
      raise AzkabanError('Invalid Azkaban server url: %r.', url)
    else:
      return response

def _extract_json(response):
  """Extract JSON from Azkaban response, gracefully handling errors.

  :param response: Request response object.

  """
  try:
    json = response.json()
  except ValueError as err: # this should never happen
    logger.error('No JSON decoded from response:\n%s', response.text)
    raise err
  else:
    if 'error' in json:
      raise AzkabanError(json['error'])
    elif json.get('status') == 'error':
      raise AzkabanError(json['message'])
    else:
      return json

def _parse_url(url):
  """Parse url.

  :param url: HTTP endpoint (including protocol, port and optional user).

  """
  parsed_url = url.rstrip('/').split('@')
  if len(parsed_url) == 1:
    user = getuser()
    url = parsed_url[0]
  elif len(parsed_url) == 2:
    user = parsed_url[0]
    url = parsed_url[1]
  else:
    raise AzkabanError('Malformed url: %r' % (url, ))
  return (user, url)

def _resolve_alias(config, alias):
  """Get url associated with an alias.

  :param alias: Alias name.

  """
  try:
    return config.parser.get('alias', alias)
  except (NoOptionError, NoSectionError):
    raise AzkabanError('Alias %r not found.', alias)

def _get_session_id(config, url):
  """Retrieve session id associated with url.

  :param url: HTTP endpoint (including protocol, port and optional user).

  """
  try:
    return config.parser.get('session_id', url)
  except NoSectionError:
    config.parser.add_section('session_id')
  except NoOptionError:
    pass


class Session(object):

  """Azkaban session.

  :param url: HTTP endpoint (including protocol, port and optional user).
  :param alias: Alias name.
  :param attempts: Maximum number of attempts to refresh session.

  This class contains mostly low-level methods that translate directly into
  Azkaban API calls. The :class:`~azkaban.remote.Execution` class should be
  preferred for interacting with workflow executions.

  Note that each session's ID is lazily updated. In particular, instantiating
  the :class:`Session` doesn't guarantee that its current ID (e.g. loaded from
  the configuration file) is valid.

  """

  def __init__(self, url=None, alias=None, attempts=3):
    self.attempts = attempts
    self.config = Config()
    if not url:
      alias = alias or self.config.get_option('azkaban', 'alias')
      url = _resolve_alias(self.config, alias)
    self.user, self.url = _parse_url(url)
    self.id = _get_session_id(self.config, str(self).replace(':', '.'))
    self.logger = InstanceLogger(self, logger)
    self.logger.debug('Instantiated.')

  def __repr__(self):
    return '<Session(url=\'%s@%s\')>' % (self.user, self.url)

  def __str__(self):
    return '%s@%s' % (self.user, self.url)

  def is_valid(self, response=None):
    """Check if the current session ID is valid.

    :param response: If passed, this reponse will be used to determine the
      validity of the session. Otherwise a simple test request will be emitted.

    """
    if not response and self.id:
      self.logger.debug('Checking if ID %s is valid.', self.id)
      # this request will return a 200 empty response if the current session
      # ID is valid and a 500 response otherwise
      response = _azkaban_request(
        'POST',
        '%s/manager' % (self.url, ),
        data={'session.id': self.id},
      )
    if (
      response is None or # 500 responses evaluate to False
      '<!-- /.login -->' in response.text or # usual non API error response
      'Login error' in response.text or # special case for API
      '"error" : "session"' in response.text # error when running a flow's jobs
    ):
      self.logger.warning('ID %s is invalid:\n%s', self.id, response.text)
      return False
    else:
      return True

  def get_execution_status(self, exec_id):
    """Get status of an execution.

    :param exec_id: Execution ID.

    """
    self.logger.debug('Fetching status for execution %s.', exec_id)
    return _extract_json(self._request(
      method='GET',
      endpoint='executor',
      params={
        'execid': exec_id,
        'ajax': 'fetchexecflow',
      },
    ))

  def get_execution_logs(self, exec_id, offset=0, limit=50000):
    """Get execution logs.

    :param exec_id: Execution ID.
    :param offset: Log offset.
    :param limit: Size of log to download.

    """
    self.logger.debug('Fetching logs for execution %s.', exec_id)
    return _extract_json(self._request(
      method='GET',
      endpoint='executor',
      params={
        'execid': exec_id,
        'ajax': 'fetchExecFlowLogs',
        'offset': offset,
        'length': limit,
      },
    ))

  def get_job_logs(self, exec_id, job, offset=0, limit=50000):
    """Get logs from a job execution.

    :param exec_id: Execution ID.
    :param job: Job name.
    :param offset: Log offset.
    :param limit: Size of log to download.

    """
    self.logger.debug('Fetching logs for execution %s, job %s.', exec_id, job)
    return _extract_json(self._request(
      method='GET',
      endpoint='executor',
      params={
        'execid': exec_id,
        'jobId': job,
        'ajax': 'fetchExecJobLogs',
        'offset': offset,
        'length': limit,
      },
    ))

  def cancel_execution(self, exec_id):
    """Cancel workflow execution.

    :param exec_id: Execution ID.

    """
    self.logger.debug('Cancelling execution %s.', exec_id)
    res = _extract_json(self._request(
      method='GET',
      endpoint='executor',
      params={
        'execid': exec_id,
        'ajax': 'cancelFlow',
      },
    ))
    if 'error' in res:
      raise AzkabanError('Execution %s is not running.', exec_id)
    else:
      self.logger.info('Execution %s cancelled.', exec_id)
    return res

  def create_project(self, name, description):
    """Create project.

    :param name: Project name.
    :param description: Project description.

    """
    self.logger.debug('Creating project %s.', name)
    return _extract_json(self._request(
      method='POST',
      endpoint='manager',
      data={
        'action': 'create',
        'name': name,
        'description': description,
      },
    ))

  def delete_project(self, name):
    """Delete a project on Azkaban.

    :param name: Project name.

    """
    self.logger.debug('Deleting project %s.', name)
    res = self._request(
      method='GET',
      endpoint='manager',
      params={
        'project': name,
        'delete': 'true',
      },
    )
    msg = "Project '%s' was successfully deleted" % (name, )
    if not msg in res.text:
      raise AzkabanError('Delete failed. Check permissions and existence.')
    return res

  def run_workflow(self, name, flow, jobs=None, concurrent=True,
    properties=None, on_failure='finish', notify_early=False, emails=None):
    """Launch a workflow.

    :param name: Name of the project.
    :param flow: Name of the workflow.
    :param jobs: List of names of jobs to run (run entire workflow by default).
    :param concurrent: Run workflow concurrently with any previous executions.
    :param properties: Dictionary that will override global properties in this
      execution of the workflow. This dictionary will be flattened similarly to
      how :class:`~azkaban.job.Job` options are handled.
    :param on_failure: Set the execution behavior on job failure. Available
      options: `'finish'` (finish currently running jobs, but do not start any
      others), `'continue'` (continue executing jobs as long as dependencies
      are met),`'cancel'` (cancel all jobs immediately).
    :param notify_early: Send any notification emails when the first job fails
      rather than when the entire workflow finishes.
    :param emails: List of emails or pair of list of emails to be notified
      when the flow fails. Note that this will override any properties set in
      the worfklow. If a single list is passed, the emails will be used for
      both success and failure events. If a pair of lists is passed, the first
      will receive failure emails, the second success emails.

    Note that in order to run a workflow on Azkaban, it must already have been
    uploaded and the corresponding user must have permissions to run it.

    """
    self.logger.debug('Starting project %s workflow %s.', name, flow)
    if not jobs:
      disabled = '[]'
    else:
      all_names = set(
        n['id']
        for n in self.get_workflow_info(name, flow)['nodes']
      )
      run_names = set(jobs)
      missing_names = run_names - all_names
      if missing_names:
        raise AzkabanError(
          'Jobs not found in flow %r: %s.' %
          (flow, ', '.join(missing_names))
        )
      else:
        disabled = (
          '[%s]'
          % (','.join('"%s"' % (n, ) for n in all_names - run_names), )
        )
    try:
      failure_action = {
        'finish': 'finishCurrent',
        'continue': 'finishPossible',
        'cancel': 'cancelImmediately',
      }[on_failure]
    except KeyError:
      raise ValueError('Invalid `on_failure` value: %r.' % (on_failure, ))
    request_data = {
      'ajax': 'executeFlow',
      'project': name,
      'flow': flow,
      'disabled': disabled,
      'concurrentOption': 'concurrent' if concurrent else 'skip',
      'failureAction': failure_action,
      'notifyFailureFirst': 'true' if notify_early else 'false',
    }
    if properties:
      request_data.update(dict(
        ('flowOverride[%s]' % (key, ), value)
        for key, value in flatten(properties).items()
      ))
    if emails:
      if isinstance(emails[0], string_types):
        failure_emails = ','.join(emails)
        success_emails = failure_emails
      else:
        failure_emails = ','.join(emails[0])
        success_emails = ','.join(emails[1])
      request_data.update({
        'failureEmails': failure_emails,
        'failureEmailsOverride': 'true',
        'successEmails': success_emails,
        'successEmailsOverride': 'true',
      })
    res = _extract_json(self._request(
      method='POST',
      endpoint='executor',
      include_session='params',
      data=request_data,
    ))
    self.logger.info('Started project %s workflow %s.', name, flow)
    return res

  def upload_project(self, name, path, archive_name=None, callback=None):
    """Upload project archive.

    :param name: Project name.
    :param path: Local path to zip archive.
    :param archive_name: Filename used for the archive uploaded to Azkaban.
      Defaults to `basename(path)`.
    :param callback: Callback forwarded to the streaming upload.

    """
    self.logger.debug('Uploading archive %r to project %s.', path, name)
    if not exists(path):
      raise AzkabanError('Unable to find archive at %r.' % (path, ))
    if not self.is_valid():
      self._refresh() # ensure that the ID is valid
    archive_name = archive_name or basename(path)
    form = MultipartForm(
      files=[{
        'path': path,
        'name': archive_name,
        'type': 'application/zip' # force this (tempfiles don't have extension)
      }],
      params={
        'ajax': 'upload',
        'project': name,
        'session.id': self.id,
      },
      callback=callback
    )
    # note that we have made sure the ID is valid, for two reasons:
    # + to avoid reuploading large files
    # + to simplify the custom ID update process (form parameter)
    res = _extract_json(self._request(
      method='POST',
      endpoint='manager',
      include_session=False,
      headers=form.headers,
      data=form,
    ))
    self.logger.info(
      'Archive %s for project %s uploaded as %s.', path, name, archive_name
    )
    return res

  def get_workflow_info(self, name, flow):
    """Get list of jobs corresponding to a workflow.

    :param name: Project name.
    :param flow: Name of flow in project.

    """
    self.logger.debug(
      'Fetching infos for workflow %s in project %s', flow, name
    )
    try:
      res = self._request(
        method='GET',
        endpoint='manager',
        params={
          'ajax': 'fetchflowjobs',
          'project': name,
          'flow': flow,
        },
      )
    except HTTPError:
      # the Azkaban server throws a NullPointerException if the flow doesn't
      # exist in the project, which causes a 500 response
      raise AzkabanError('Worklow %s not found in project %s.', flow, name)
    else:
      try:
        return _extract_json(res)
      except ValueError:
        # but sends a 200 empty response if the project doesn't exist
        raise AzkabanError('Project %s not found.', name)

  def _refresh(self, password=None):
    """Refresh session ID.

    :param password: Password used to log into Azkaban. If not specified,
      will prompt for one.

    Also caches the session ID for future use.

    """
    self.logger.debug('Refreshing.')
    attempts = self.attempts
    while True:
      password = password or getpass('Azkaban password for %s: ' % (self, ))
      try:
        res = _extract_json(_azkaban_request(
          'POST',
          self.url,
          data={
            'action': 'login',
            'username': self.user,
            'password': password,
          },
        ))
      except AzkabanError as err:
        if not 'Incorrect Login.' in err.message:
          raise err
        self.logger.warning('Invalid login attempt.')
        attempts -= 1
        password = None
        if attempts <= 0:
          raise AzkabanError('Too many unsuccessful login attempts. Aborting.')
      else:
        break
    self.id = res['session.id']
    self.config.parser.set('session_id', str(self).replace(':', '.'), self.id)
    self.config.save()
    self.logger.info('Refreshed.')

  def _request(self, method, endpoint, include_session='cookies', **kwargs):
    """Make a request to Azkaban using this session.

    :param method: HTTP method.
    :param endpoint: Server endpoint (e.g. manager).
    :param include_session: Where to include the `session_id` (possible values:
      `'cookies'`, `'params'`, `False`).
    :param kwargs: Keyword arguments passed to :func:`_azkaban_request`.

    If the session expired, will prompt for a password to refresh.

    """
    full_url = '%s/%s' % (self.url, endpoint.lstrip('/'))

    if not self.id:
      self.logger.debug('No ID found.')
      self._refresh()

    def _send_request():
      """Try sending the request with the appropriate credentials."""
      if include_session == 'cookies':
        kwargs.setdefault('cookies', {})['azkaban.browser.session.id'] = self.id
      elif include_session == 'params':
        kwargs.setdefault('data', {})['session.id'] = self.id
      elif include_session:
        raise ValueError('Invalid `include_session`: %r' % (include_session, ))
      return _azkaban_request(method, full_url, **kwargs)

    response = _send_request()
    if not self.is_valid(response):
      self._refresh()
      response = _send_request()

    # `_refresh` raises an exception rather than letting an unauthorized second
    # request happen. this means that something is wrong with the server.
    if not self.is_valid(response):
      raise AzkabanError('Azkaban server is unavailable.')

    try:
      response.raise_for_status() # check that we get a 2XX response back
    except HTTPError as err: # catch, log, and reraise
      self.logger.warning(
        'Received invalid response from %s:\n%s',
        response.request.url, response.content
      )
      raise err
    else:
      return response


class Execution(object):

  """Remote workflow execution.

  :param session: :class:`Session` instance.
  :param exec_id: Execution ID.

  """

  def __init__(self, session, exec_id):
    self._session = session
    self.exec_id = exec_id

  @property
  def status(self):
    """Execution status."""
    return self._session.get_execution_status(self.exec_id)

  @property
  def url(self):
    """Execution URL."""
    return '%s/executor?execid=%s' % (self._session.url, self.exec_id)

  def cancel(self):
    """Cancel execution."""
    self._session.cancel_execution(self.exec_id)

  def logs(self, delay=5):
    """Execution log generator.

    :param delay: time in seconds between each server poll

    Yields line by line.

    """
    finishing = False
    offset = 0
    while True:
      logs = self._session.get_execution_logs(
        exec_id=self.exec_id,
        offset=offset,
      )
      if logs['length']:
        offset += logs['length']
        lines = (e for e in logs['data'].split('\n') if e)
        for line in lines:
          yield line
      elif finishing:
        break
      else:
        if self.status['status'] != 'RUNNING':
          finishing = True
      sleep(delay)

  def job_logs(self, job, delay=5):
    """Job log generator.

    :param job: job name
    :param delay: time in seconds between each server poll

    Yields line by line.

    """
    finishing = False
    offset = 0
    while True:
      try:
        logs = self._session.get_job_logs(
          exec_id=self.exec_id,
          job=job,
          offset=offset,
        )
      except HTTPError as err:
        # if Azkaban is hanging, the job might be stuck in preparing stage
        preparing = False
        while True:
          sleep(delay)
          preparing_jobs = set(
            e['id']
            for e in self.status['nodes']
            if e['status'] == 'PREPARING'
          )
          if job in preparing_jobs:
            if not preparing:
              preparing = True
              logger.debug(
                'Job %s in execution %s is still preparing.', job, self.exec_id
              )
          else:
            break
        if not preparing:
          # something else is causing the error
          raise err
      else:
        if logs['length']:
          offset += logs['length']
          lines = (e for e in logs['data'].split('\n') if e)
          for line in lines:
            yield line
        elif finishing:
          break
        else:
          running_jobs = set(
            e['id']
            for e in self.status['nodes']
            if e['status'] == 'RUNNING'
          )
          if job not in running_jobs:
            finishing = True
      sleep(delay)

  @classmethod
  def start(cls, session, *args, **kwargs):
    """Convenience method to start a new execution.

    :param session: :class:`Session` instance.
    :param args: Cf. :meth:`Session.run_workflow`.
    :param kwargs: Cf. :meth:`Session.run_workflow`.

    """
    res = session.run_workflow(*args, **kwargs)
    return cls(session, res['execid'])
