# main.py

from fastapi import FastAPI, Request
import os
import re
import requests
import base64
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

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

@app.post("/")
async def root(request: Request):
    return {"received_request_body": await request.json()}
