import json
import requests

from base64 import b64encode


API_BASE = 'https://www.toggl.com/api/v8/'


class TogglApiInterface:
    def __init__(self, api_key):
        self.api_token = b64encode(
            (api_key + ':api_token').encode()).decode()

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

        print(self.headers)

    def get_workspaces(self):
        j = self._get('workspaces')
        self._cache_workspaces(j)

        return j

    def get_projects(self, workspace_id):
        j = self._get(
            'workspaces/{}/projects'.format(workspace_id))
        self._cache_projects(j)

        return j

    def get_all_projects(self):
        projects = []
        workspaces = self.get_workspaces()
        if not workspaces:
            return
        for w in workspaces:
            projects += self.get_projects(w['id']) or []
        return projects

    def create_project(self, project_name, workspace_id):
        j = self._post('projects', {
            'project': {
                'wid': workspace_id,
                'name': project_name,
            }
        })
        print(j)
        self._cache_projects([j['data']])

        return j

    def delete_project(self, pid):
        return self._delete('projects/' + str(pid))

    def create_time_entry(self, project_id, start, duration):
        j = self._post('time_entries', {
                'time_entry': {
                    'pid': project_id,
                    'start': start,
                    'duration': duration,
                    'created_with': 'autotoggl'
                }
            })
        print(j)
        return j

    def _get(self, url_stub):
        r = requests.get(
            API_BASE + url_stub,
            headers=self.headers,
        )
        self._show_response(r)
        return r.json()

    def _post(self, url_stub, data):
        r = requests.post(
            API_BASE + url_stub,
            headers=self.headers,
            data=json.dumps(data),
        )
        self._show_response(r)
        return r.json()

    def _delete(self, url_stub):
        r = requests.delete(
            API_BASE + url_stub,
            headers=self.headers,
        )
        self._show_response(r)
        return r.status_code == 200

    def _show_response(self, r):
        print('[{}] {}'.format(r.status_code, r.request.url))
        if r.status_code >= 400:
            print('Error [{}]: {}'.format(r.status_code, r))
            print(r.text)

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
            if wid not in self.cached:
                self.cached[wid] = {}
            self.cached[wid][pid] = p
