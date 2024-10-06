from spaceone.inventory.plugin.collector.lib.server import CollectorPluginServer

from typing import Generator
# from plugin.manager.github_repository.github_manager import GithubManager
# from plugin.manager.github_actions.github_actions_manager import GithubActionsManager
from plugin.manager.github_manager import GithubManager
from plugin.manager.github_actions_manager import GithubActionsManager

app = CollectorPluginServer()


@app.route('Collector.init')
def collector_init(params: dict) -> dict:
    """ init plugin by options

    Args:
        params (CollectorInitRequest): {
            'options': 'dict',    # Required
            'domain_id': 'str'
        }

    Returns:
        PluginResponse: {
            'metadata': 'dict'
        }
    """
    return {"metadata": {"options_schema": {}}}


@app.route('Collector.verify')
def collector_verify(params: dict) -> None:
    """ Verifying collector plugin

    Args:
        params (CollectorVerifyRequest): {
            'options': 'dict',      # Required
            'secret_data': 'dict',  # Required
            'schema': 'str',
            'domain_id': 'str'
        }

    Returns:
        None
    """
    pass


@app.route('Collector.collect')
# def collector_collect(params: dict) -> dict:
def collector_collect(params: dict) -> Generator[dict, None, None]:
    """ Collect external data

    Args:
        params (CollectorCollectRequest): {
            'options': 'dict',      # Required
            'secret_data': 'dict',  # Required
            'schema': 'str',
            'task_options': 'dict',
            'domain_id': 'str'
        }

    Returns:
        Generator[ResourceResponse, None, None]
        {
            'state': 'SUCCESS | FAILURE',
            'resource_type': 'inventory.CloudService | inventory.CloudServiceType | inventory.Region',
            'cloud_service_type': CloudServiceType,
            'cloud_service': CloudService,
            'region': Region,
            'match_keys': 'list',
            'error_message': 'str'
            'metadata': 'dict'
        }

        CloudServiceType
        {
            'name': 'str',           # Required
            'group': 'str',          # Required
            'provider': 'str',       # Required
            'is_primary': 'bool',
            'is_major': 'bool',
            'metadata': 'dict',      # Required
            'service_code': 'str',
            'tags': 'dict'
            'labels': 'list'
        }

        CloudService
        {
            'name': 'str',
            'cloud_service_type': 'str',  # Required
            'cloud_service_group': 'str', # Required
            'provider': 'str',            # Required
            'ip_addresses' : 'list',
            'account' : 'str',
            'instance_type': 'str',
            'instance_size': 'float',
            'region_code': 'str',
            'data': 'dict'               # Required
            'metadata': 'dict'           # Required
            'reference': 'dict'
            'tags' : 'dict'
        }

        Region
        {
            'name': 'str',
            'region_code': 'str',        # Required
            'provider': 'str',           # Required
            'tags': 'dict'
        }

        Only one of the cloud_service_type, cloud_service and region fields is required.
    """
    
    options = params["options"]
    secret_data = params["secret_data"]
    schema = params.get("schema")

    github_mgr = GithubManager()
    github_actions_mgr = GithubActionsManager()
    
    # GithubManager의 리소스 수집 (리포지토리 관련 데이터)
    for resource in github_mgr.collect_resources(options, secret_data, schema):
        yield resource

    # GithubActionsManager의 리소스 수집 (Actions 관련 데이터)
    for resource in github_actions_mgr.collect_resources(options, secret_data, schema):
        yield resource
        
    # return github_mgr.collect_resources(options, secret_data, schema)


@app.route('Job.get_tasks')
def job_get_tasks(params: dict) -> dict:
    """ Get job tasks

    Args:
        params (JobGetTaskRequest): {
            'options': 'dict',      # Required
            'secret_data': 'dict',  # Required
            'domain_id': 'str'
        }

    Returns:
        TasksResponse: {
            'tasks': 'list'
        }

    """
    pass
