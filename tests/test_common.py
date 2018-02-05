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
    return Config(json_data={
        'api_key': TEST_API_KEY,
        'default_workspace': TEST_WORKSPACE,
        'default_day': 'today',
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
                        'title': 'Duolingo',
                        'description': 'German practice',
                        'window_contains': [
                            'duolingo',
                        ]
                    },
                    {
                        'title': 'Casual',
                        'description': 'Internetting',
                        'description_pattern': '(.*)',
                        'window_contains': [
                            'guardian'
                            'netflix'
                            'news',
                            'politics',
                            'reddit',
                            'starcraft',
                        ]
                    },
                ]
            },
        ]
    })
