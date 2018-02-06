from time import sleep
from datetime import datetime, timezone, timedelta

from autotoggl import toggl_api
from tests import test_common
from tests.test_common import equal
from tests.test_credentials import (
    TEST_WORKSPACE,
    TEST_WORKSPACE_ID,
    TEST_API_KEY,
)


logger = test_common.get_logger(name=__name__)


def test_api_interface(config=None):
    config = test_common.get_test_config()
    interface = toggl_api.TogglApiInterface(config)

    interface.get_all_projects()

    project_id = _test_api_create_project(interface)
    _test_api_create_time_entry(interface, project_id)
    _test_api_delete_project(interface, project_id)


def _test_api_create_project(interface):
    j = interface.create_project('API_TEST_PROJECT', TEST_WORKSPACE_ID)
    equal(j['data']['wid'], TEST_WORKSPACE_ID)

    pid = j['data']['id']
    return pid


def _test_api_create_time_entry(interface, pid):
    interface.create_time_entry(
        pid,
        (datetime.now(timezone.utc).astimezone() - timedelta(hours=1))
        .replace(microsecond=0).timestamp(),
        120
    )


def _test_api_delete_project(interface, pid):
    sleep(5)
    deleted = interface.delete_project(pid)
    equal(deleted, True)
