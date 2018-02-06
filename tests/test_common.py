import logging

from autotoggl.config import Config
from tests.test_credentials import (
    TEST_WORKSPACE,
    TEST_WORKSPACE_ID,
    TEST_API_KEY,
)


def get_logger(name=__file__, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(logging.StreamHandler())
    return logger


logger = get_logger()


def get_test_config():
    return Config(clargs={}, json_data={
        'api_key': TEST_API_KEY,
        'default_workspace': TEST_WORKSPACE,
        'default_day': 'today',
        'minimum_event_seconds': 60,
        'day_ends_at': 3,
        'project_definitions': [
            {
                'process': 'sublime_text',

                # If this pattern matches, the first group will be used
                # as the project title
                'project_pattern': '.*\\((.*?)\\) - Sublime Text.*',

                # If this pattern matches, the first group will be used
                # as the event description
                'description_pattern': ['(.*?) . \\(.*?\\) - Sublime Text.*'],
            },
            {
                'process': 'studio64',
                'project_pattern': '(.*?) - \\[.*\\].*',
                'description_pattern': ['.*? - \\[.*?\\] - (.*?) - .*'],
            },
            {
                'process': 'chrome',
                'projects': [
                    # List of projects that might match this process
                    {
                        # If any of the strings in window_contains are
                        # found in the window title then this will
                        # be the project title
                        'project_title': 'Duolingo',

                        # If any of the strings in window_contains are
                        # found in the window title then this will
                        # be the event description
                        'description': 'German practice',

                        'window_contains': [
                            'duolingo',
                        ],
                    },
                    {
                        'project_title': 'Casual',
                        'description': 'Internetting',

                        # If this pattern matches the window title then
                        # the first group will provide the event
                        # description. If there is no match, the value
                        # of `description` will be returned
                        'description_pattern': [],
                        'window_contains': [
                            'guardian'
                            'news',
                            'politics',
                            'reddit',
                            'starcraft',
                        ],
                    },

                    {
                        'project_title': 'Casual',
                        'description': '_',

                        'description_pattern': [
                            'BBC iPlayer - (.*)',
                        ],
                        'window_contains': [
                            'netflix',
                            'iplayer',
                        ],
                    },
                ]
            },
        ]
    })
