import json
import os
import re

from argparse import ArgumentParser
from datetime import datetime, timedelta

from autotoggl.util import midnight


class InvalidConfig(Exception):
    '''
    Config was loaded but did not pass validation
    '''
    pass


class ConfigError(Exception):
    '''
    Config could not be loaded
    '''
    pass


class Config:
    def __init__(self, file=None, json_data=None, clargs=None):
        self.filepath = file

        self.api_key = None
        self.default_workspace = None
        self.project_definitions = {}
        self.default_day = None
        self.minimum_event_seconds = None
        self.day_ends_at = None
        self.date = None
        self.local = False
        self.render = False

        if file:
            self._load_from_file(file)
        elif json_data:
            self._load_from_json(json_data)

        self._load_from_clargs(clargs)
        self._process_args()
        self._validate_config()

    def defs(self):
        return self.project_definitions

    def _load_from_file(self, filename):
        if not os.path.exists(filename):
            raise ConfigError(
                    'Error reading JSON from file {}'.format(filename))

        with open(filename, 'r') as f:
            try:
                config = json.load(f)
                self._load_from_json(config)
            except Exception as e:
                raise ConfigError(
                    'Error reading JSON from file {}: {}'.format(filename, e))

    def _load_from_json(self, config):
        defs = {}
        for x in config.get('project_definitions', []):
            defs[x['process']] = ProcessClassifier(x)

        self.project_definitions = defs

        self.api_key = config.get('api_key')

        # Name or numeric workspace ID
        self.default_workspace = config.get('default_workspace')

        # Which day should be processed if not overriden by clargs
        # Accepts 'today' or 'yesterday'
        self.default_day = config.get('default_day', 'yesterday')

        # Events shorter than this will be ignored or merged with
        # any previous ongoing event
        self.minimum_event_seconds = config.get('minimum_event_seconds', 60)

        # What hour should be considered the end of the day
        # Useful if you tend to stay up into the wee hours
        self.day_ends_at = config.get('day_ends_at', 3)

    def _load_from_clargs(self, args=None):
        if args is None:
            parser = ArgumentParser()
            parser.add_argument(
                'day',
                choices=[
                    'today',
                    'yesterday',
                    '',
                ],
                default='',
                nargs='?',
            )

            parser.add_argument(
                '--date',
                type=str,
                default=None,
                help='(yy)yy-mm-dd format',
            )

            parser.add_argument(
                '--default_workspace',
                help='The workspace on which any new projects should be created.',)

            parser.add_argument(
                '--key',
                type=str,
                help='Toggl API key')

            parser.add_argument(
                '--minimum_event_seconds',
                type=int,
                help='Ignore any events that are shorter than this.',)

            parser.add_argument(
                '--day_ends_at',
                type=int,
                help='Hour at which one day rolls over into the next.',)

            parser.add_argument(
                '-local',
                action='store_true',
                default=False,
                help='Do a \'dry run\' without sending anything to Toggl',)

            parser.add_argument(
                '-render',
                action='store_true',
                default=False,
                help='Contruct a simple HTML preview of event data',)

            args = parser.parse_args()

        if not args:
            return

        if args.day:
            self.default_day = args.day
        if args.date:
            self.date = args.date
        if args.default_workspace:
            self.default_workspace = args.default_workspace
        if args.key:
            self.api_key = args.key
        if args.minimum_event_seconds:
            self.minimum_event_seconds = args.minimum_event_seconds
        if args.day_ends_at:
            self.day_ends_at = args.day_ends_at

        self.local = args.local
        self.render = args.render

    def _process_args(self):
        if self.date:
            m = re.match(
                r'(\d{2})?(\d{2})'  # year
                '[./\-]{1}'         # separator
                '(\d{2})'           # month
                '[./\-]{1}'         # separator
                '(\d{2})',          # day
                self.date)
            if m:
                self.date = datetime(
                    year=int('{}{}'.format(m.group(1) or '20', m.group(2))),
                    month=int(m.group(3)),
                    day=int(m.group(4)))
        else:
            if self.default_day == 'today':
                self.date = datetime.today()
            elif self.default_day == 'yesterday':
                self.date = datetime.today() - timedelta(days=1)
        self.date = midnight(self.date)

        if self.default_workspace:
            # Try to parse given workspace as an integer ID
            try:
                self.default_workspace = int(self.default_workspace)
            except:
                pass

    def _validate_config(self):
        if not self.api_key:
            raise InvalidConfig('API key is not configured')

        if not self.date or type(self.date) != datetime:
            raise InvalidConfig('Date could not be interpreted')

    def as_json(self):
        return {
            'api_key': self.api_key,
            'default_workspace': self.default_workspace,
            'default_day': self.default_day,
            'minimum_event_seconds': self.minimum_event_seconds,
            'day_ends_at': self.day_ends_at,
            'date': int(self.date.timestamp()),
            'project_definitions': [
                x.as_json() for _, x in self.project_definitions.items()
            ],
            'local': self.local,
            'render': self.render,
        }

    def _create_example_file(self, filename):
        d = os.path.dirname(filename)
        if not os.path.exists:
            os.makedirs(d)

        with open(filename, 'w') as f:
            json.dump({
                'api_key': 'Enter the API token from your profile at https://toggl.com/app/profile',
                'default_workspace': 'workspace name or id',
                'default_day': 'yesterday',
                'minimum_event_seconds': 60,
                'day_ends_at': 3,
                'project_definitions': [
                    {
                        'process': 'sublime_text',
                        'project_pattern': '.*\\((.*?)\\) - Sublime Text.*',
                        'description_pattern': '(.*?) . \\(.*?\\) - Sublime Text.*'
                    },
                    {
                        'process': 'studio64',
                        'project_pattern': '(.*?) - \\[.*\\].*',
                        'description_pattern': '.*? - \\[.*?\\] - (.*?) - .*'
                    },
                    {
                        'process': 'chrome',
                        'projects': [
                            {
                                'project_title': 'Duolingo',
                                'description': 'German',
                                'window_contains': [
                                    'duolingo'
                                ]
                            },
                            {
                                'project_title': 'Casual',
                                'description': 'Internetting',
                                'description_pattern': '(.*)',
                                'window_contains': [
                                    'reddit',
                                    'politics',
                                    'starcraft',
                                    'news',
                                    'guardian',
                                    'netflix'
                                ]
                            }
                        ]
                    }
                ]
            }, f)


class Classifier:
    # Special value for self.description
    # If the project is matched using window_contains then the matching
    # value will be used as the description value
    # e.g.
    # description: '_',
    # window_contains: ['netflix', 'iplayer']
    # -> If the window title contains 'netflix' then the description
    #    will be set to 'netflix'
    USE_MATCH = '_'

    def __init__(self, json_data):
        self.project_title = json_data.get('project_title')
        self.project_pattern = json_data.get('project_pattern')
        self.description = json_data.get('description')
        self.description_pattern = json_data.get('description_pattern', [])
        self.window_contains = json_data.get('window_contains', [])
        self.project_alias = json_data.get('alias', {})

    def get_project(self, window_title):
        if self.project_pattern:
            m = re.match(self.project_pattern, window_title)
            if m:
                return self._alias(m.group(1))

        for x in self.window_contains:
            if x in window_title.lower():
                return self._alias(self.project_title)

    def get_description(self, window_title):
        for p in self.description_pattern:
            m = re.match(p, window_title)
            if m:
                return m.group(1)

        for x in self.window_contains:
            if x in window_title.lower():
                if self.description == Classifier.USE_MATCH:
                    return x

                return self.description

    def _alias(self, project):
        '''
        If projectname  has an alias registered then return that instead,
        otherwise return the original project name
        '''
        return (self.project_alias[project]
                if project in self.project_alias
                else project)

    def as_json(self):
        return {
            'project_title': self.project_title,
            'project_pattern': self.project_pattern,
            'description': self.description,
            'description_pattern': self.description_pattern,
            'window_contains': self.window_contains,
        }


class Project(Classifier):
    '''
    Alias of Classifier that is used as a child object of
    ProcessClassifier
    '''
    pass


class ProcessClassifier(Classifier):
    '''
    Implementation of Classifier with added fields
    for a process name and a list of Projects
    Represents an item in the Config.project_definitions list
    '''
    def __init__(self, json_data):
        super().__init__(json_data)

        self.process = json_data.get('process')
        self.projects = [Project(x) for x in json_data.get('projects', [])]

    def get_project(self, window_title):
        for x in self.projects:
            p = x.get_project(window_title)
            if p:
                return p

        return super().get_project(window_title)

    def get_description(self, window_title):
        for x in self.projects:
            d = x.get_description(window_title)
            if d:
                return d

        return super().get_description(window_title)

    def __repr__(self):
        return json.dumps(
            {
                'process': self.process,
                'project_pattern': self.project_pattern,
                'projects': self.projects,
            }, indent=2)

    def as_json(self):
        j = super().as_json()
        j['process'] = self.process
        j['projects'] = [x.as_json() for x in self.projects]
        return j
