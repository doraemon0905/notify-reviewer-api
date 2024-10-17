# main.py

from fastapi import FastAPI, Form, Request
from pydantic import BaseModel
import logging.config
import logging
import sys
import re
import requests
import base64
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import validators
from pydantic_settings import BaseSettings
from starlette.responses import Response
from datetime import datetime
import logging
import json

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Constants
class Settings(BaseSettings):
    github_token: str = ""
    bot_token: str = ""
    channel_id: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
# Initialize Slack client and logger
client = WebClient(token=settings.bot_token)
logger = logging.getLogger(__name__)

SPECIFIC_CASES = {
    "@ai-hero-bot": "S06N42PMKEF"  # Example: Slack ID for @ai-hero-bot is hardcoded to "ABC"
}

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Slack bot request review", debug=True)

class SlackCommand(BaseModel):
    token: str = Form(...)
    team_id: str = Form(...)
    team_domain: str = Form(...)
    channel_id: str = Form(...)
    channel_name: str = Form(...)
    user_id: str = Form(...)
    user_name: str = Form(...)
    command: str = Form(...)
    text: str = Form(...)
    response_url: str = Form(...)
    trigger_id: str = Form(...)

@app.middleware("http")
async def log_traffic(request: Request, call_next):
    start_time = datetime.now()
    request_body = await request.body()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    client_host = request.client.host
    log_params = {
        "request_method": request.method,
        "request_url": str(request.url),
        "request_size": request.headers.get("content-length"),
        "request_headers": dict(request.headers),
        "request_body": request_body.decode("utf-8"),
        "response_status": response.status_code,
        "response_size": response.headers.get("content-length"),
        "response_headers": dict(response.headers),
        "process_time": process_time,
        "client_host": client_host
    }
    logger.info(log_params)
    return response

@app.post("/")
async def root(token: str = Form(...),
    team_id: str = Form(...),
    team_domain: str = Form(...),
    channel_id: str = Form(...),
    channel_name: str = Form(...),
    user_id: str = Form(...),
    user_name: str = Form(...),
    command: str = Form(...),
    text: str = Form(...),
    response_url: str = Form(...),
    trigger_id: str = Form(...)
):
    parts = text.split()
    if len(parts) == 2:
        pr_url, channel_id = parts
    elif len(parts) == 1:
        pr_url = parts[0]
        channel_id = ""

    if not validators.url(pr_url):
        return {
            "response_type": "ephemeral",
            "text": ":alert: Please provide a valid URL"
        }
    validate_env_vars()
    try:
        if re.match(r"^https://github.com/[^/]+/[^/]+/pull/\d+$", pr_url):
            logger.info("Processing Pull Request...")
            get_pr_details(pr_url, user_id, channel_id)
            logger.info("Notification sent to Slack!")
            response_text = f"Hi {'<@' + user_id + '>'}, your review request have been submitted."
        else:
            response_text = f":alert: Invalid Pull Request URL. Please provide a valid GitHub PR URL."
    except Exception as e:
        return {
            "response_type": "ephemeral",  # Message is only visible to the user
            "text": ":alert: " + str(e)
        }

    return {
        "response_type": "ephemeral",  # Message is only visible to the user
        "text": response_text
    }

def validate_env_vars():
    if not settings.github_token:
        raise ValueError("Invalid GITHUB_TOKEN.")
    if not settings.bot_token:
        raise ValueError("Invalid BOT_TOKEN.")
    if not settings.channel_id:
        raise ValueError("Invalid CHANNEL_ID.")


def make_github_request(url):
    headers = {
        "Authorization": f"token {settings.github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Error fetching data from GitHub: {response.status_code}")
        return {}


def convert_reviewers_to_subteam_format(reviewers, usergroup_map):
    subteams = []
    for reviewer in reviewers.split(", "):
        external_id = SPECIFIC_CASES.get(reviewer, usergroup_map.get(reviewer.strip()))
        subteams.append(f"<!subteam^{external_id}>" if external_id else reviewer)
    return " ".join(subteams)


def find_user_id_by_email(email):
    try:
        result = client.users_lookupByEmail(email=email)
        return result["user"]["id"]
    except SlackApiError as e:
        logger.error(f"Error looking up user: {e}")


def send_to_slack(title, reviewers, pr_url, user_id, usergroup_map, channel_id):
    formatted_reviewers = convert_reviewers_to_subteam_format(reviewers, usergroup_map)
    message = f"Hi team, please help {'<@' + user_id + '> ' if user_id else ''}review this PR {pr_url} \nSummary: {title} \ncc {formatted_reviewers}\nThank you! :pepe_love:"

    try:
        return client.chat_postMessage(channel=channel_id, text=message)
    except SlackApiError as e:
        logger.error(f"Error posting message: {e}")


def get_user_email(user_login):
    user_url = f"https://api.github.com/users/{user_login}"
    user_response = make_github_request(user_url)
    return user_response.get("email", "No public email")


def contains_reviewer(reviewers, reviewer_to_check):
    return reviewer_to_check in reviewers


def get_pr_details(pr_url, user_id, channel_id):
    match = re.match(r"https://github.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        raise ValueError("Invalid GitHub Pull Request URL format.")
    organization, repo, pr_number = match.groups()
    pr_api_url = f"https://api.github.com/repos/{organization}/{repo}/pulls/{pr_number}"
    response = make_github_request(pr_api_url)
    state = response.get("state", "unknown")
    if state != "open":
        raise ValueError("Pull Request is not open.")
    
    title = response.get("title", "No title")
    reviewers = get_reviewers(pr_api_url + "/requested_reviewers")

    usergroup_map = get_slack_usergroups()

    if not channel_id:
        channel_id = settings.channel_id

    send_to_slack(title, reviewers, pr_url, user_id, usergroup_map, channel_id)

def get_reviewers(pr_url):
    response = make_github_request(pr_url)
    teams = response.get("teams", [])
    return ", ".join([f"@{team['name']}" for team in teams])

def get_slack_usergroups():
    try:
        result = client.usergroups_list()
        return {f"@{ug['handle']}": ug["id"] for ug in result["usergroups"]}
    except SlackApiError as e:
        logger.error(f"Error fetching Slack user groups: {e}")
        return {}
