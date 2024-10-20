import validators
from app.serivces.github import GitHub
from app.config.settings import settings
from app.serivces.slack import Slack
from app.decorators.review_message import ReviewMessageDecorator
import logging
import re

logger = logging.getLogger(__name__)

SPECIFIC_CASES = {
    "@ai-hero-bot": "S06N42PMKEF",  # Example: Slack ID for @ai-hero-bot is hardcoded to "ABC"
    "@engineering-managers": "S05FPFUQKK6",
}

class SendMessage:
    def __init__(self, user_id: str, message: str):
        self.message = message
        self.user_id = user_id

    def send_message(self):
        user_ids, channel_ids, pr_url = self._parse_slack_message()
        if not validators.url(pr_url):
             raise ValueError("Please provide a valid URL")
        
        if self.user_id in user_ids:
            user_ids.remove(self.user_id)

        if re.match(r"^https://github.com/[^/]+/[^/]+/pull/\d+$", pr_url):
            return self._execute_send_message(channel_ids, user_ids, pr_url)
        else:
            raise ValueError("Invalid Pull Request URL. Please provide a valid GitHub PR URL.")
        
    def _parse_slack_message(self):
        # Regular expression to find user IDs
        user_id_pattern = r"<@([A-Z0-9]+)\|"
        user_ids = re.findall(user_id_pattern, self.message)

        # Regular expression to find channel ID
        channel_id_pattern = r"<#([A-Z0-9]+)\|"
        channel_ids = re.findall(channel_id_pattern, self.message)

        # Regular expression to find GitHub pull request URL
        pr_url_pattern = r"https://github.com/[^/]+/[^/]+/pull/\d+"
        pr_url_match = re.search(pr_url_pattern, self.message)
        pr_url = pr_url_match.group(0) if pr_url_match else None

        return user_ids, channel_ids, pr_url

    def valid_pr_url(self, pr_detail):
        state = pr_detail.get("state")
        if state != "open":
            raise ValueError("Pull request is not open.")
        title = pr_detail.get("title")
        if not title:
            raise ValueError("Pull request do not have a title.")

    def convert_reviewers_to_subteam_format(self, reviewers, usergroup_map):
        subteams = []
        for reviewer in reviewers.split(", "):
            external_id = SPECIFIC_CASES.get(reviewer, usergroup_map.get(reviewer.strip()))
            subteams.append(f"<!subteam^{external_id}>" if external_id else reviewer)
        return " ".join(subteams)
    
    def convert_reviewers_user_format(self, user_ids):
        subteams = []
        for reviewer in user_ids:
            subteams.append(f"<@{reviewer}>")
        return " ".join(subteams)
    
    def _execute_send_message(self, channel_ids, user_ids, pr_url):
        match = re.match(r"https://github.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
        organization, repo, pr_number = match.groups()
        github = GitHub(settings.github_token, organization, repo, pr_number)
        pr_detail = github.get_pr_details()
        pr_reviewers = github.get_pr_reviewers()
        self.valid_pr_url(pr_detail)

        if not channel_ids:
            channel_ids = [settings.channel_id]
        slack = Slack(settings.bot_token, channel_ids)

        usergroup_map = slack.get_slack_usergroups()
        if user_ids:
            reviewers = self.convert_reviewers_user_format(user_ids)
        else:
            reviewers = self.convert_reviewers_to_subteam_format(pr_reviewers, usergroup_map)
        
        message = ReviewMessageDecorator(
            review_message = {
                "id": pr_number,
                "user_id": self.user_id,
                "pr_url": pr_url,
                "title": pr_detail.get("title"),
                "formatted_reviewers": reviewers,
                "user_ids": user_ids,
            }
        )

        slack.chat_post_message(message.message())
