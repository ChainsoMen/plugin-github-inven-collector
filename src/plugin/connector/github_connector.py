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
                    'workflows': {'name': '', 'id': '', 'state': '', 'created_at': '', 'updated_at': '', 'file': '', 'content': ''}
                }
                try:
                    # 워크플로 정보 추가
                    workflows = repo.get_workflows()
                
                    if workflows.totalCount > 0:
                        # 가장 최신 워크플로 가져오기
                        latest_workflow = workflows[0]
                        
                        repo_info['workflows'] = {
                            'name': latest_workflow.name,
                            'id': latest_workflow.id,
                            'state': latest_workflow.state,
                            'created_at': latest_workflow.created_at.isoformat(),
                            'updated_at': latest_workflow.updated_at.isoformat(),
                            'file': latest_workflow.path,
                            'content': repo.get_contents(latest_workflow.path).decoded_content.decode('utf-8')
                        }
                        
                except Exception as e:
                    _LOGGER.error(f"Error fetching workflows from GitHub: {e}")
                    
                    

                repo_list.append(repo_info)
            return repo_list
        except Exception as e:
            _LOGGER.error(f"Error fetching repositories from GitHub: {e}")
            return []