import logging
from typing import Dict, List
from github import Github
from spaceone.core.connector import BaseConnector
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

_LOGGER = logging.getLogger(__name__)

class GithubConnector(BaseConnector):
    def __init__(self, github_access_token: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = Github(github_access_token)
    
    # 캐싱
    @lru_cache(maxsize=128)
    def list_repositories(self, actions: bool) -> List[Dict]:
        return self._list_repositories(actions)

    def _list_repositories(self, actions: bool) -> List[Dict]:
        try:
            repos = self.client.get_user().get_repos()
            repo_list = []

            # ThreadPoolExecutor를 사용하여 병렬 처리
            # 각 리포지토리에 대해 스레드 풀에서 비동기적으로 처리
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_repo = {executor.submit(self.get_repo_info, repo, actions): repo for repo in repos}
                # future: 스레드 풀에서 작업의 완료 상태나 결과를 확인할 수 있는 객체
                for future in as_completed(future_to_repo): # 작업이 완료되는 순서대로 future 객체를 반환
                    try:
                        repo_info = future.result()
                        if repo_info:
                            repo_list.append(repo_info)
                    except Exception as e:
                        _LOGGER.error(f"Error fetching repository info: {e}")

            return repo_list
        except Exception as e:
            _LOGGER.error(f"Error fetching repositories from GitHub: {e}")
            return []
    
    
    def get_repo_info(self, repo, fetch_actions: bool) -> Dict:
        try:
            actions_data = []
            if fetch_actions:
                actions_data = self.get_actions(repo)
            
            repo_info = {
                'name': repo.name,
                'full_name': repo.full_name,
                'private': repo.private,
                'description': repo.description,
                'html_url': repo.html_url,
                'created_at': repo.created_at.isoformat(),
                'updated_at': repo.updated_at.isoformat(),
                'pushed_at': repo.pushed_at.isoformat(),
                'branches': [branch.name for branch in repo.get_branches()],
                'workflows': self.get_workflows(repo),
                'actions': actions_data
            }
            return repo_info
        except Exception as e:
            _LOGGER.error(f"Error fetching repository info for {repo.name}: {e}")
            return {}
        
    def get_workflows(self, repo):
        try:
            workflow_list = []
            workflows = repo.get_workflows()
            for wf in workflows:
                workflow_list.append({
                    'name': wf.name,
                    'id': str(wf.id),
                    'state': wf.state,
                    'created_at': wf.created_at.isoformat(),
                    'updated_at': wf.updated_at.isoformat(),
                    'file': wf.path,
                })
            return workflow_list
        except Exception as e:
            _LOGGER.error(f"Error fetching workflows: {e}")
            return []

    def get_actions(self, repo: List[Dict]) -> List[Dict]:
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

    def get_jobs(self, run) -> List[Dict]:
        try:
            # GitHub API 호출을 통해 Job 정보를 가져옵니다.
            job_list = []
            jobs_url = run.jobs_url
            response = self.client._Github__requester.requestJsonAndCheck("GET", jobs_url)
            jobs = response[1].get('jobs', [])
            
            for job in jobs:
                job_info = {
                    'action_id': str(run.id),  # 해당하는 action ID 추가
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
