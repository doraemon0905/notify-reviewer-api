import requests
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
logger = logging.getLogger(__name__)

class Slack:
    def __init__(self, token, channel_id):
        self.token = token
        self.client = self.init_client()

    def init_client(self):
        return WebClient(token=self.token)

    
    def get_slack_usergroups(self):
        result = self.client.usergroups_list()
        return {f"@{ug['handle']}": ug["id"] for ug in result["usergroups"]}
    
    def chat_post_message(self, channel_id, message):
        return self.client.chat_postMessage(channel=channel_id, text=message)
