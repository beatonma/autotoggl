import json
import logging

from autotoggl.config import Config
from tests.test_credentials import (
    TEST_WORKSPACE,
    TEST_WORKSPACE_ID,
    TEST_API_KEY,
)


def get_logger(name=__name__, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(logging.StreamHandler())
    return logger


logger = get_logger()


def equal(actual, expected, comment='', data=None):
    try:
        if type(expected) is list:
            assert(len(expected) == len(actual))
            assert(sorted(expected) == sorted(actual))
        else:
            assert(expected == actual)

        logger.info(
            '[EQUAL]{} {}'.format(
                ' (' + comment + ')' if comment else '',
                actual))
    except AssertionError as e:
        logger.warn('ASSERTION ERROR (NOT EQUAL):')
        logger.warn('  Expected: {}'.format(expected))
        logger.warn('    Actual: {}'.format(actual))
        if comment:
            logger.warn('   Comment: {}'.format(comment))
        if data:
            try:
                logger.warn(
                    '      Data: {}'.format(json.dumps(data, indent=2)))
            except:
                logger.warn('   Data: {}'.format(data))
        raise SystemExit()


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

                # If the resolved project name has an entry in this
                # dictionary then that name will be used instead
                'alias': {
                    'gassistant': 'Home Assistant',
                },

                # If this pattern matches, the first group will be used
                # as the event description
                'description_pattern': [
                    '.*?([\\w\\d\\-]+\\.[\\w\\d\\-]+) .*?\\(.*?\\) - Sublime Text.*'
                ],

                'tag_pattern': [
                    '.*?[\\w\\d\\-]+\\.([\\w\\d\\-]+) .*?\\(.*?\\) - Sublime Text.*'
                ]
            },
            {
                'process': 'studio64',
                'project_pattern': '(.*?) - \\[.*\\].*',
                'description_pattern': ['.*? - \\[.*?\\] - (.*?) - .*'],

                'tags': [
                    'android',
                    'dev'
                ],
            },
            {
                'process': 'chrome',
                'tags': [
                    'chrome',
                ],
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
                        'tags': [
                            'language',
                        ],

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
                        'tags': [
                            '_',
                        ],
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
