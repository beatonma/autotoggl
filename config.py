import json
import os
import re

from argparse import ArgumentParser
from datetime import datetime, timedelta

from util import midnight


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
        if not args:
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

            args = parser.parse_args()

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

    def _process_args(self):
        if self.date:
            m = re.match(r'(\d{2})?(\d{2})-(\d{2})-(\d{2})', self.date)
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
                as_int = int(self.default_workspace)
                self.default_workspace = as_int
            except:
                pass

    def _validate_config(self):
        if not self.api_key:
            raise InvalidConfig('API key is not configured')


class ProcessClassifier:
    def __init__(self, json_data=None):
        if json:
            self._from_json(json_data)
        else:
            self.process = ''

    def _from_json(self, j):
        self.process = j.get('process')
        self.project_pattern = j.get('project_pattern')
        self.description_pattern = j.get('description_pattern')
        self.projects = j.get('projects')

    def get_project(self, window_title):
        if self.project_pattern:
            m = re.match(self.project_pattern, window_title)
            if m:
                return m.group(1)
        if self.projects:
            for p in self.projects:
                if [x for x in p.get('window_contains')
                        if x in window_title.lower()]:
                    return p.get('title')

    def get_description(self, window_title):
        if self.description_pattern:
            m = re.match(self.description_pattern, window_title)
            if m:
                return m.group(1)

    def __repr__(self):
        return json.dumps({
                'process': self.process,
                'project_pattern': self.project_pattern,
                'projects': self.projects,
            }, indent=2)
