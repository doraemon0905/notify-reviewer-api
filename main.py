# main.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
import re
import requests
import base64
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import validators

# Constants
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Initialize Slack client and logger
client = WebClient(token=BOT_TOKEN)
logger = logging.getLogger(__name__)

SPECIFIC_CASES = {
    "@ai-hero-bot": "S06N42PMKEF"  # Example: Slack ID for @ai-hero-bot is hardcoded to "ABC"
}

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

class SlackCommand(BaseModel):
    token: str
    team_id: str
    team_domain: str
    channel_id: str
    channel_name: str
    user_id: str
    user_name: str
    command: str
    text: str
    response_url: str
    trigger_id: str

@app.post("/")
async def root(slack_command: SlackCommand):
    print(validators.url(slack_command.text))
    if not validators.url(slack_command.text):
        return {
            "response_type": "ephemeral",
            "text": "Please provide a valid URL"
        }

    response_text = f"Hello {slack_command.user_name}, this is a private message just for you!"

    return {
        "response_type": "ephemeral",  # Message is only visible to the user
        "text": response_text
    }
