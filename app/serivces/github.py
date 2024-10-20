import aiohttp
import logging

logger = logging.getLogger(__name__)


class GitHub:
    def __init__(self, token, organization, repo, pull_request_number):
        self.token = token
        self.organization = organization
        self.repo = repo
        self.pull_request_number = pull_request_number

    async def make_github_request(self, url):
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Error fetching data from GitHub: {response.status}")
                    return {}

    async def get_user_email(self, user_login):
        user_url = f"https://api.github.com/users/{user_login}"
        user_response = await self.make_github_request(user_url)
        return user_response.get("email", "No public email")
    

    def build_url(self):
        return f"https://api.github.com/repos/{self.organization}/{self.repo}"
    

    def build_pull_request_url(self):
        return f"{self.build_url()}/pulls/{self.pull_request_number}"
    

    async def get_pr_details(self):
        return await self.make_github_request(self.build_pull_request_url())


    async def get_pr_reviewers(self):
        pr_api_url = f"{self.build_pull_request_url()}/requested_reviewers"
        response = await self.make_github_request(pr_api_url)
        teams = response.get("teams", [])
        return ", ".join([f"@{team['name']}" for team in teams])
