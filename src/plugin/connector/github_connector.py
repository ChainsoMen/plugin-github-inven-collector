import logging
from typing import Dict, List
from github import Github
from spaceone.core.connector import BaseConnector

_LOGGER = logging.getLogger(__name__)

class GithubConnector(BaseConnector):
    def __init__(self, github_access_token: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = Github(github_access_token)

    def list_repositories(self) -> List[Dict]:
        try:
            repos = self.client.get_user().get_repos()
            repo_list = []
            for repo in repos:
                repo_info = {
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'private': repo.private,
                    'description': repo.description,
                    'html_url': repo.html_url,
                    'created_at': repo.created_at.isoformat(),
                    'updated_at': repo.updated_at.isoformat(),
                    'pushed_at': repo.pushed_at.isoformat(),
                    'pull_requests': repo.get_pulls().totalCount,
                    'branches': [branch.name for branch in repo.get_branches()],
                    'workflows': self.get_workflows(repo),
                    'actions': self.get_actions(repo)
                }
                repo_list.append(repo_info)
            return repo_list
        except Exception as e:
            _LOGGER.error(f"Error fetching repositories from GitHub: {e}")
            return []

    def get_workflows(self, repo):
        try:
            workflows = repo.get_workflows()
            workflow_list = []
            for wf in workflows:
                workflow_list.append({
                    'name': wf.name,
                    'id': wf.id,
                    'state': wf.state,
                    'created_at': wf.created_at.isoformat(),
                    'updated_at': wf.updated_at.isoformat(),
                    'file': wf.path,
                    'content': repo.get_contents(wf.path).decoded_content.decode('utf-8')
                })
            return workflow_list
        except Exception as e:
            _LOGGER.error(f"Error fetching workflows: {e}")
            return []

    def get_actions(self, repo):
        try:
            actions = []
            workflows = repo.get_workflows()
            for workflow in workflows:
                runs = workflow.get_runs()
                for run in runs:
                    action_info = {
                        'name': run.name,
                        'status': run.status,
                        'conclusion': run.conclusion,
                        'created_at': run.created_at.isoformat(),
                        'updated_at': run.updated_at.isoformat(),
                        'url': run.html_url,
                        'jobs': self.get_jobs(run)
                    }
                    actions.append(action_info)
            return actions
        except Exception as e:
            _LOGGER.error(f"Error fetching actions: {e}")
            return []

    def get_jobs(self, run):
        try:
            # GitHub API 호출을 통해 Job 정보를 가져옵니다.
            jobs_url = run.jobs_url
            response = self.client._Github__requester.requestJsonAndCheck("GET", jobs_url)
            jobs = response[1].get('jobs', [])
            job_list = []
            for job in jobs:
                job_info = {
                    'action_id': run.id,  # 해당하는 action ID 추가
                    'name': job['name'],
                    'status': job['status'],
                    'conclusion': job['conclusion'],
                    'started_at': job['started_at'],
                    'completed_at': job['completed_at'],
                }
                job_list.append(job_info)
            return job_list
        except Exception as e:
            _LOGGER.error(f"Error fetching jobs: {e}")
            return []

