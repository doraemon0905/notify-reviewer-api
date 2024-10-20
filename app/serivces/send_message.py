import validators
from serivces.github import GitHub
import re

class SendMessage:
    def send_message(self, text):
        parts = text.split()
        if len(parts) == 2:
            pr_url, channel_id = parts
        elif len(parts) == 1:
            pr_url = parts[0]
            channel_id = ""
        
        if not validators.url(pr_url):
             raise ValueError("Please provide a valid URL")

        if re.match(r"^https://github.com/[^/]+/[^/]+/pull/\d+$", pr_url):
            return self._execute_send_message(pr_url, channel_id)
        else:
            raise ValueError("Invalid Pull Request URL. Please provide a valid GitHub PR URL.")

    def _execute_send_message(self, pr_url, channel_id):
        github = GitHub()
        match = re.match(r"https://github.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
        organization, repo, pr_number = match.groups()
        pr_details = github.get_pr_details(pr_url)
        pr_reviewers = github.get_pr_reviewers(pr_url)
