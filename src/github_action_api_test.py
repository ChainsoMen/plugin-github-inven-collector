import unittest
from unittest.mock import patch, MagicMock
from plugin.connector.github_connector import GithubConnector

class TestGithubConnector(unittest.TestCase):
    def setUp(self):
        # GitHub 액세스 토큰을 설정
        self.github_access_token = "test_token"
        self.github_connector = GithubConnector(github_access_token=self.github_access_token)

    @patch('plugin.connector.github_connector.Github')
    def test_list_repositories(self, mock_github):
        # Mock GitHub 객체 생성
        mock_repo = MagicMock()
        mock_repo.name = "TestRepo"
        mock_repo.full_name = "test_user/TestRepo"
        mock_repo.private = False
        mock_repo.description = "Test description"
        mock_repo.html_url = "https://github.com/test_user/TestRepo"
        mock_repo.created_at.isoformat.return_value = "2024-01-01T12:00:00Z"
        mock_repo.updated_at.isoformat.return_value = "2024-01-02T12:00:00Z"
        mock_repo.pushed_at.isoformat.return_value = "2024-01-03T12:00:00Z"
        mock_repo.get_pulls.return_value.totalCount = 5
        mock_repo.get_branches.return_value = [MagicMock(name="main")]

        mock_github.return_value.get_user().get_repos.return_value = [mock_repo]

        # get_workflows와 get_actions도 mock으로 설정
        with patch.object(self.github_connector, 'get_workflows', return_value=[]):
            with patch.object(self.github_connector, 'get_actions', return_value=[]):
                repos = self.github_connector.list_repositories()

        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0]['name'], "TestRepo")
        self.assertEqual(repos[0]['full_name'], "test_user/TestRepo")
        self.assertEqual(repos[0]['private'], False)
        self.assertEqual(repos[0]['description'], "Test description")
        self.assertEqual(repos[0]['html_url'], "https://github.com/test_user/TestRepo")
        self.assertEqual(repos[0]['created_at'], "2024-01-01T12:00:00Z")
        self.assertEqual(repos[0]['updated_at'], "2024-01-02T12:00:00Z")
        self.assertEqual(repos[0]['pushed_at'], "2024-01-03T12:00:00Z")
        self.assertEqual(repos[0]['pull_requests'], 5)
        self.assertEqual(repos[0]['branches'], ["main"])

    @patch('plugin.connector.github_connector.Github')
    def test_get_jobs(self, mock_github):
        # Mock GitHub 객체 생성
        mock_run = MagicMock()
        mock_job = MagicMock()

        # Mock Job 객체 설정
        mock_job.name = "Test Job"
        mock_job.status = "completed"
        mock_job.conclusion = "success"
        mock_job.started_at.isoformat.return_value = "2024-01-01T12:00:00Z"
        mock_job.completed_at.isoformat.return_value = "2024-01-01T12:10:00Z"
        mock_run.get_jobs.return_value = [mock_job]

        # Mock steps 메서드 설정
        with patch.object(self.github_connector, 'get_steps', return_value=[]):
            jobs = self.github_connector.get_jobs(mock_run)

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['name'], "Test Job")
        self.assertEqual(jobs[0]['status'], "completed")
        self.assertEqual(jobs[0]['conclusion'], "success")
        self.assertEqual(jobs[0]['started_at'], "2024-01-01T12:00:00Z")
        self.assertEqual(jobs[0]['completed_at'], "2024-01-01T12:10:00Z")

    @patch('plugin.connector.github_connector.Github')
    def test_get_steps(self, mock_github):
        # Mock Job 객체 생성
        mock_job = MagicMock()
        mock_step = MagicMock()

        # Mock Step 객체 설정
        mock_step.name = "Test Step"
        mock_step.status = "completed"
        mock_step.conclusion = "success"
        mock_step.number = 1
        mock_step.started_at.isoformat.return_value = "2024-01-01T12:01:00Z"
        mock_step.completed_at.isoformat.return_value = "2024-01-01T12:02:00Z"
        mock_job.get_steps.return_value = [mock_step]

        steps = self.github_connector.get_steps(mock_job)

        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0]['name'], "Test Step")
        self.assertEqual(steps[0]['status'], "completed")
        self.assertEqual(steps[0]['conclusion'], "success")
        self.assertEqual(steps[0]['number'], 1)
        self.assertEqual(steps[0]['started_at'], "2024-01-01T12:01:00Z")
        self.assertEqual(steps[0]['completed_at'], "2024-01-01T12:02:00Z")


if __name__ == '__main__':
    unittest.main()
