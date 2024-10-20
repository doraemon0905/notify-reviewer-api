import requests
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
logger = logging.getLogger(__name__)

class Slack:
    def __init__(self, token, channel_ids):
        self.token = token
        self.channel_ids = channel_ids
        self.client = self.init_client()

    def init_client(self):
        return WebClient(token=self.token)

    
    def get_slack_usergroups(self):
        result = self.client.usergroups_list()
        return {f"@{ug['handle']}": ug["id"] for ug in result["usergroups"]}
    
    def chat_post_message(self, message):
        for channel in self.channel_ids:
            return self.client.chat_postMessage(channel=channel, text=message)
