from autotoggl import toggl_api
from tests import test_common


logger = test_common.get_logger(__name__)


def test_api_interface(config=None):
    config = test_common.get_test_config()
    interface = toggl_api.TogglApiInterface(config)
    # j = interface.get_workspaces()
    # logger.info(json.dumps(j, indent=2))
    # test_api_get_projects(interface)
    # pid = test_api_create_project(interface)
    # test_api_create_time_entry(interface, pid)
    # test_api_delete_project(interface, pid)
    logger.info(interface)


# def test_api_get_projects(interface):
#     j = interface.get_all_projects()


# def test_api_create_project(interface):
#     j = interface.create_project('API_TEST_PROJECT', TEST_WORKSPACE_ID)
#     _equal(j['data']['wid'], TEST_WORKSPACE_ID)

#     pid = j['data']['id']
#     return pid


# def test_api_create_time_entry(interface, pid):
#     j = interface.create_time_entry(
#         pid,
#         (datetime.datetime.now(timezone.utc).astimezone() - timedelta(hours=1))
#         .replace(microsecond=0).isoformat(),
#         120
#     )
#     logger.debug('Time entry response: {}'.format(j))


# def test_api_delete_project(interface, pid):
#     sleep(10)
#     deleted = interface.delete_project(pid)
#     _equal(deleted, True)