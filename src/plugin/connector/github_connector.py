import logging
from typing import Dict, List

from github import Github
from spaceone.core.connector import BaseConnector

_LOGGER = logging.getLogger(__name__)

class GithubConnector(BaseConnector):
    def __init__(self, github_access_token: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = Github(github_access_token)

    # # 예시 코드 나중에 지워도 됨
    # def list_cryptocurrencies(self) -> List[Dict]:
    #     try:
    #         coins = self.client.get_coins_markets(
    #             vs_currency="krw", order="market_cap_desc", per_page=5, page=1
    #         )

    #         filtered_coins = list()
    #         for coin in coins:
    #             filtered_coins.append(
    #                 {
    #                     "name": coin["name"],
    #                     "current_price": coin["current_price"],
    #                     "market_cap_rank": coin["market_cap_rank"],
    #                     "price_change_percentage_24h": coin[
    #                         "price_change_percentage_24h"
    #                     ],
    #                     "high_24h": coin["high_24h"],
    #                     "low_24h": coin["low_24h"],
    #                     "last_updated": coin["last_updated"],
    #                 }
    #             )
    #         return filtered_coins
    #     except Exception as e:
    #         _LOGGER.error(f"Error fetching cryptocurrency data: {e}")
    #         return []

    def list_repositories(self) -> List[Dict]:
        try:
            repos = self.client.get_user().get_repos()
            repo_list = []
            for repo in repos:
                repo_list.append({
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'private': repo.private,
                    'description': repo.description,
                    'html_url': repo.html_url,
                    'created_at': repo.created_at.isoformat(),
                    'updated_at': repo.updated_at.isoformat(),
                    'pushed_at': repo.pushed_at.isoformat(),
                    'branches': [branch.name for branch in repo.get_branches()],
                })
            return repo_list
        except Exception as e:
            _LOGGER.error(f"Error fetching repositories from GitHub: {e}")
            return []