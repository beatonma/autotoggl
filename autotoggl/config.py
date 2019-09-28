import json
import os
import re

from argparse import ArgumentParser
from datetime import datetime, timedelta
from typing import Optional

from autotoggl.util import midnight


class InvalidConfig(Exception):
    """
    Config was loaded but did not pass validation
    """

    pass


class ConfigError(Exception):
    """
    Config could not be loaded
    """

    pass


class Config:
    def __init__(self, file=None, json_data=None, clargs=None):
        self.filepath = file

        self.api_key: Optional[str] = None
        self.default_workspace = None
        self.classifiers: dict = {}
        self.default_day: str = "today"
        self.minimum_event_seconds: int = 60
        self.day_ends_at: int = 3
        self.date = None
        self.local: bool = False
        self.render: bool = False
        self.reset: bool = False
        self.showall: bool = False
        self.clean: bool = False
        self.config: bool = False
        self.catchup: bool = False

        if file:
            self._load_from_file(file)
        elif json_data:
            self._load_from_json(json_data)

        print(json.dumps(self.as_json(), indent=2))

        self._load_from_clargs(clargs)
        print(json.dumps(self.as_json(), indent=2))
        self._process_args()
        self._validate_config()

    def defs(self):
        return self.classifiers

    def _load_from_file(self, filename):
        if not os.path.exists(filename):
            raise ConfigError("Error reading JSON from file {}".format(filename))

        with open(filename, "r") as f:
            try:
                config = json.load(f)
                self._load_from_json(config)
            except Exception as e:
                raise ConfigError(
                    "Error reading JSON from file {}: {}".format(filename, e)
                )

    def _load_from_json(self, config):
        defs = {}
        for x in config.get("project_definitions", []):
            defs[x["process"]] = ProcessClassifier(x)

        self.classifiers = defs

        self.api_key = config.get("api_key")

        # Name or numeric workspace ID
        self.default_workspace = config.get("default_workspace")

        # Which day should be processed if not overriden by clargs
        # Accepts 'today' or 'yesterday'
        self.default_day = config.get("default_day", "yesterday")

        # Events shorter than this will be ignored or merged with
        # any previous ongoing event
        self.minimum_event_seconds = config.get("minimum_event_seconds", 60)

        # What hour should be considered the end of the day
        # Useful if you tend to stay up into the wee hours
        self.day_ends_at = config.get("day_ends_at", 3)

    def _load_from_clargs(self, args=None):
        if args is None:
            parser = ArgumentParser()
            subparsers = parser.add_subparsers(dest="ns")

            parser.add_argument(
                "--day",
                choices=["today", "yesterday", ""],
                default="yesterday",
                nargs="?",
            )

            parser.add_argument(
                "--date", type=str, default=None, help="(yy)yy-mm-dd format"
            )

            parser.add_argument(
                "--default_workspace",
                help="The workspace on which any new projects should be created.",
            )

            parser.add_argument("--key", type=str, help="Toggl API key")

            parser.add_argument(
                "--minimum_event_seconds",
                type=int,
                help="Ignore any events that are shorter than this.",
            )

            parser.add_argument(
                "--day_ends_at",
                type=int,
                help="Hour at which one day rolls over into the next.",
            )

            parser.add_argument(
                "-catchup",
                action="store_true",
                default=False,
                help="Reprocess any pending events that occurred before today",
            )

            parser.add_argument(
                "-local",
                action="store_true",
                default=False,
                help="Do a 'dry run' without sending anything to Toggl",
            )

            parser.add_argument(
                "-render",
                action="store_true",
                default=False,
                help="Contruct a simple HTML preview of event data",
            )

            parser.add_argument(
                "-reset",
                action="store_true",
                default=False,
                help="Reset database entries for the given day to " "consumed=False",
            )

            parser.add_argument(
                "-showall",
                action="store_true",
                default=False,
                help="Show all events for the given day without any " "filtering",
            )

            cleanup_parser = subparsers.add_parser("clean")
            cleanup_parser.add_argument(
                "-before", action="store_true", help="Remove any entries before --date"
            )
            cleanup_parser.add_argument(
                "--older_than",
                type=int,
                default=2,
                help="Remove any entries that are at least this many " "days old",
            )
            cleanup_parser.add_argument(
                "-all",
                action="store_true",
                help="Remove entries even if they have not been consumed",
            )

            config_parser = subparsers.add_parser("config")

            args = parser.parse_args()

        if not args:
            return

        for attr in [
            "date",
            "default_workspace",
            "minimum_event_seconds",
            "day_ends_at",
            "catchup",
        ]:
            if hasattr(args, attr) and getattr(args, attr) is not None:
                setattr(self, attr, getattr(args, attr))

        if hasattr(args, "day") and args.day is not None:
            self.default_day = args.day
        if hasattr(args, "key") and args.key is not None:
            setattr(self, "api_key", args.key)

        self.local = args.local
        self.render = args.render
        self.reset = args.reset
        self.showall = args.showall

        self.clean = None
        if args.ns == "clean":
            self.clean = {
                "before": args.before,
                "older_than": args.older_than,
                "all": args.all,
            }
        elif args.ns == "config":
            self.config = True

    def _process_args(self):
        if self.date:
            m = re.match(
                r"(\d{2})?(\d{2})"  # year
                "[./\-]{1}"  # separator
                "(\d{2})"  # month
                "[./\-]{1}"  # separator
                "(\d{2})",  # day
                self.date,
            )
            if m:
                self.date = datetime(
                    year=int("{}{}".format(m.group(1) or "20", m.group(2))),
                    month=int(m.group(3)),
                    day=int(m.group(4)),
                )
        else:
            if self.default_day == "today":
                self.date = datetime.today()
            elif self.default_day == "yesterday":
                self.date = datetime.today() - timedelta(days=1)

        self.date = self.date if self.date else datetime.today()
        self.date = midnight(self.date)

        self.day_starts = self.date.replace(
            hour=self.day_ends_at, minute=0, second=0, microsecond=0
        )
        self.day_ends = self.day_starts + timedelta(days=1)

        if self.clean and self.clean["before"]:
            self.clean["before"] = self.date

        if self.default_workspace:
            # Try to parse given workspace as an integer ID
            try:
                self.default_workspace = int(self.default_workspace)
            except:
                pass

    def _validate_config(self):
        if not self.api_key:
            raise InvalidConfig("API key is not configured")

        if not self.date or type(self.date) != datetime:
            raise InvalidConfig("Date could not be interpreted")

        for attr in [
            'minimum_event_seconds',
            'day_ends_at',
        ]:
            if not isinstance(getattr(self, attr), int):
                raise InvalidConfig(f"{attr} is invalid: '{self.day_ends_at}'")

    def day_starts(self):
        return self.day_starts

    def day_ends(self):
        return self.day_ends

    def as_json(self):
        date = int(self.date.timestamp()) if self.date else None
        return {
            "api_key": self.api_key,
            "default_workspace": self.default_workspace,
            "default_day": self.default_day,
            "minimum_event_seconds": self.minimum_event_seconds,
            "day_ends_at": self.day_ends_at,
            "date": date,
            "project_definitions": [x.as_json() for _, x in self.classifiers.items()],
            "local": self.local,
            "render": self.render,
            "reset": self.reset,
            "showall": self.showall,
            "clean": self.clean,
            "config": self.config,
            "catchup": self.catchup,
        }

    def _create_example_file(self, filename):
        d = os.path.dirname(filename)
        if not os.path.exists:
            os.makedirs(d)

        with open(filename, "w") as f:
            json.dump(
                {
                    "api_key": "Enter the API token from your profile at https://toggl.com/app/profile",
                    "default_workspace": "workspace name or id",
                    "default_day": "yesterday",
                    "minimum_event_seconds": 60,
                    "day_ends_at": 3,
                    "project_definitions": [
                        {
                            "process": "sublime_text",
                            "project_pattern": ".*\\((.*?)\\) - Sublime Text.*",
                            "description_pattern": "(.*?) . \\(.*?\\) - Sublime Text.*",
                        },
                        {
                            "process": "studio64",
                            "project_pattern": "(.*?) - \\[.*\\].*",
                            "description_pattern": ".*? - \\[.*?\\] - (.*?) - .*",
                        },
                        {
                            "process": "chrome",
                            "projects": [
                                {
                                    "project_title": "Duolingo",
                                    "description": "German",
                                    "window_contains": ["duolingo"],
                                },
                                {
                                    "project_title": "Casual",
                                    "description": "Internetting",
                                    "description_pattern": "(.*)",
                                    "window_contains": [
                                        "reddit",
                                        "politics",
                                        "starcraft",
                                        "news",
                                        "guardian",
                                        "netflix",
                                    ],
                                },
                            ],
                        },
                    ],
                },
                f,
            )


class ClassifierResult:
    def __init__(self, **kwargs):
        self.project = kwargs.get("project")
        self.description = kwargs.get("description")
        self.tags = kwargs.get("tags", [])


class Classifier:
    # Special value for self.description
    # If the project is matched using window_contains then the matching
    # value will be used as the description value
    # e.g.
    # description: '_',
    # tags: ['_'],
    # window_contains: ['netflix', 'iplayer']
    # -> If the window title contains 'netflix' then the description
    #    will be set to 'netflix' and a 'netflix' tag will be added
    USE_MATCH = "_"

    def __init__(self, json_data):
        self.project_title = json_data.get("project_title")
        self.project_pattern = json_data.get("project_pattern")
        self.description = json_data.get("description")
        self.description_pattern = json_data.get("description_pattern", [])
        self.window_contains = json_data.get("window_contains", [])
        self.project_alias = json_data.get("alias", {})
        self.tags = json_data.get("tags", [])
        self.tag_pattern = json_data.get("tag_pattern", [])

    def get(self, window_title):
        project = None
        description = None
        tags = self.tags[:]

        if self.project_pattern:
            project = self._match_patterns([self.project_pattern], window_title)
        description = self._match_patterns(self.description_pattern, window_title)
        tags += self._match_multi_patterns(self.tag_pattern, window_title)

        for x in self.window_contains:
            if x in window_title.lower():
                project = project or self.project_title
                description = description or self.description
                if description == Classifier.USE_MATCH:
                    description = x
                tags = [x if t == Classifier.USE_MATCH else t for t in tags]
                break

        if not self.project_pattern and not self.window_contains:
            project = self.project_title

        if not self.description_pattern and not self.window_contains:
            description = self.description

        tags = list(set(tags))  # Remove any duplicates

        if project:
            return ClassifierResult(
                project=self._alias(project), description=description, tags=tags
            )

    def _match_patterns(self, patterns, text) -> str:
        """Get the first matching group."""
        for p in patterns:
            m = re.match(p, text)
            if m:
                return m.group(1)

    def _match_multi_patterns(self, patterns, text) -> list:
        """Return the first matching group for multiple patterns."""
        results = []
        for p in patterns:
            m = re.match(p, text)
            if m:
                results.append(m.group(1))
        return results

    def _alias(self, projectname):
        """
        If projectname has an alias registered then return that instead,
        otherwise return the original project name
        """
        return (
            self.project_alias[projectname]
            if projectname in self.project_alias
            else projectname
        )

    def as_json(self):
        return {
            "project_title": self.project_title,
            "project_pattern": self.project_pattern,
            "description": self.description,
            "description_pattern": self.description_pattern,
            "window_contains": self.window_contains,
            "tags": self.tags,
            "tag_pattern": self.tag_pattern,
        }


class Project(Classifier):
    """
    Alias of Classifier that is used as a child object of
    ProcessClassifier
    """

    pass


class ProcessClassifier(Classifier):
    """
    Implementation of Classifier with added fields
    for a process name and a list of Projects
    Represents an item in the Config.classifiers list
    """

    def __init__(self, json_data):
        super().__init__(json_data)

        self.process = json_data.get("process")
        self.projects = [Project(x) for x in json_data.get("projects", [])]

    def get(self, window_title):
        result = None
        for x in self.projects:
            result = x.get(window_title)
            if result:
                break

        if result:
            result.tags += self.tags
            return result

        return super().get(window_title)

    def __repr__(self):
        return json.dumps(
            {
                "process": self.process,
                "project_pattern": self.project_pattern,
                "projects": self.projects,
            },
            indent=2,
        )

    def as_json(self):
        j = super().as_json()
        j["process"] = self.process
        j["projects"] = [x.as_json() for x in self.projects]
        return j
