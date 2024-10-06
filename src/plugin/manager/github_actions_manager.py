import logging
import os
from spaceone.core.manager import BaseManager
from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service_with_metadata,
    make_error_response,
    make_response,
)
from plugin.connector.github_connector import GithubConnector

_LOGGER = logging.getLogger(__name__)
_CURRENT_DIR = os.path.dirname(__file__)
_METADATA_DIR = os.path.join(_CURRENT_DIR, "../metadata/")

class GithubActionsManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = "github"
        self.cloud_service_group = "Actions"
        self.cloud_service_type = "GitHub Actions"
        self.metadata_path = os.path.join(_METADATA_DIR, "github/github_actions.yaml")

    def collect_resources(self, options, secret_data, schema):
        try:
            yield from self.collect_cloud_service_type(options, secret_data, schema)
            yield from self.collect_cloud_service(options, secret_data, schema)
        except Exception as e:
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
            )

    def collect_cloud_service_type(self, options, secret_data, schema):
        cloud_service_type = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
        )

        yield make_response(
            cloud_service_type=cloud_service_type,
            match_keys=[["name", "reference.resource_id", "account", "provider"]],
            resource_type="inventory.CloudServiceType",
        )

    def collect_cloud_service(self, options, secret_data, schema):
        github_connector = GithubConnector(github_access_token=secret_data['github_access_token'])
        repositories = github_connector.list_repositories()

        for repo in repositories:
            # 각 리포지토리의 액션 정보를 처리
            actions = repo.get('actions', [])
            for action in actions:
                # 액션 데이터를 기반으로 클라우드 서비스 생성
                action_cloud_service = make_cloud_service_with_metadata(
                    name=repo['name'] + ' - ' + action['name'],
                    cloud_service_type=self.cloud_service_type,
                    cloud_service_group=self.cloud_service_group,
                    provider=self.provider,
                    data=action,  # 액션 데이터를 전달
                    data_format='dict',
                    metadata_path=self.metadata_path,
                )
                
                # 각 액션에 대해 응답 생성
                yield make_response(
                    cloud_service=action_cloud_service,
                    match_keys=[['name', 'reference.resource_id', 'account', 'provider']],
                )
                
                # 각 액션의 작업(Job)을 처리
                jobs = action.get('jobs', [])
                for job in jobs:
                    job_cloud_service = make_cloud_service_with_metadata(
                        name=repo['name'] + ' - ' + action['name'] + ' - ' + job['name'],
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=job,  # Job 데이터를 전달
                        data_format='dict',
                        metadata_path=self.metadata_path,
                    )

                    # 각 Job에 대해 응답 생성
                    yield make_response(
                        cloud_service=job_cloud_service,
                        match_keys=[['name', 'reference.resource_id', 'account', 'provider']],
                    )
