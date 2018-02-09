import json
import logging
import requests

from base64 import b64encode
from datetime import datetime, timezone
from time import sleep


API_BASE = 'https://www.toggl.com/api/v8/'


def _init_logger(name=__file__, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(logging.StreamHandler())
    return logger


logger = _init_logger()


class ApiError(Exception):
    '''
    Raised whenever an API request receives a response
    with any 4xx status code.
    '''
    pass


class TogglApiInterface:
    def __init__(self, config, mock=False):

        # If true, network requests will be disabled and empty data
        # will be returned
        self.mock = mock

        self.default_workspace = config.default_workspace

        self.api_token = b64encode(
            (config.api_key + ':api_token').encode()).decode()

        self.headers = {
            'Authorization': 'Basic ' + self.api_token,
            'Content-Type': 'application/json'
        }

        self.cached = {
            # 'workspace_id': {
            #     'project_id' {
            #         ...
            #     },
            #     ...
            # },
            # ...
        }
        self.projects = {
            # 'project_name': {
            #   'wid': workspace_id,
            #   'pid': project_id,
            # },
            # ...
        }

    def __repr__(self):
        return (
            'Default workspace: {}\nHeaders: {}\nProjects: {}\nCache: {}'
            .format(
                self.default_workspace,
                self.headers,
                json.dumps(self.projects, indent=2, sort_keys=True),
                json.dumps(self.cached, indent=2, sort_keys=True),))

    def _set_default_workspace(self):
        '''
        Try to get an integer workspace id.
        '''

        if type(self.default_workspace) is int:
            return

        if self.cached:
            if self.default_workspace:
                # Try to get an ID for the given workspace name
                for _, w in self.cached.items():
                    if w.get('name', '') == self.default_workspace:
                        self.default_workspace = w.get('id')
                        return
            else:
                # If there is only one workspace then set it as the default
                if len(self.cached) == 1:
                    self.default_workpace = next(iter(self.cached)).get('id')
                    return
        logger.warn(
            'Unable to set default workspace - '
            'please check your configuration')

    def get_workspaces(self):
        '''
        Get all workspaces associated with the API token
        '''
        j = self._get('workspaces')
        self._cache_workspaces(j)
        self._set_default_workspace()

        return j

    def get_projects(self, workspace_id):
        '''
        Get all projects associated with the workspace
        '''
        j = self._get(
            'workspaces/{}/projects'.format(workspace_id))
        self._cache_projects(j)

        return j

    def get_all_projects(self):
        '''
        Get all projects associated with all workspaces for our API token
        '''
        projects = []
        workspaces = self.get_workspaces()
        if not workspaces:
            return
        for w in workspaces:
            projects += self.get_projects(w['id']) or []
        return projects

    def create_project(self, project_name, workspace_id=None):
        '''
        Create a new project on the given (or default) workspace
        '''
        if not workspace_id:
            workspace_id = self.default_workspace
            if not workspace_id:
                raise Exception(
                    'Cannot create project without a valid workspace ID')

        j = self._post('projects', {
            'project': {
                'wid': workspace_id,
                'name': project_name,
            }
        })
        logger.debug(j)
        self._cache_projects([j['data']])

        return j

    def delete_project(self, pid):
        '''
        Delete the given project. Currently only used for testing.
        '''
        return self._delete('projects/' + str(pid))

    def create_time_entry(self,
                          project_id, description,
                          start_timestamp, duration,
                          tags=[], ):
        if type(project_id) is str:
            project_id = self.projects[project_id]['pid']

        logger.debug('Creating time entry')

        start = (datetime.fromtimestamp(start_timestamp, timezone.utc)
                 .astimezone()
                 .isoformat())

        j = self._post('time_entries', {
                'time_entry': {
                    'pid': project_id,
                    'description': description,
                    'start': start,
                    'duration': duration,
                    'tags': tags,
                    'created_with': 'autotoggl',
                }
            })
        logger.debug(j)
        return j

    def _get(self, url_stub):
        if self.mock:
            return {}

        r = requests.get(
            API_BASE + url_stub,
            headers=self.headers,
        )
        self._show_response(r)
        sleep(1)
        return r.json()

    def _post(self, url_stub, data):
        if self.mock:
            return {}

        r = requests.post(
            API_BASE + url_stub,
            headers=self.headers,
            data=json.dumps(data),
        )
        self._show_response(r)
        sleep(1)
        return r.json()

    def _delete(self, url_stub):
        if self.mock:
            return True

        r = requests.delete(
            API_BASE + url_stub,
            headers=self.headers,
        )
        self._show_response(r)
        sleep(1)
        return r.status_code == 200

    def _show_response(self, r):
        logger.info('[{}] {}'.format(r.status_code, r.request.url))
        if r.status_code >= 400:
            raise ApiError('[error:{}] {}'.format(r.status_code, r.text))

    def _cache_workspaces(self, workspaces):
        if not workspaces:
            return
        for w in workspaces:
            wid = str(w['id'])
            self.cached[wid] = w

    def _cache_projects(self, projects):
        if not projects:
            return
        for p in projects:
            wid = str(p['wid'])
            pid = str(p['id'])
            name = str(p['name'])
            if wid not in self.cached:
                self.cached[wid] = {}
            self.cached[wid][pid] = p

            self.projects[name] = {
                'pid': p['id'],
                'wid': p['wid']
            }
