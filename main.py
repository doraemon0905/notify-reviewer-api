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
from pydantic_settings import BaseSettings
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
    if not validators.url(slack_command.text):
        return {
            "response_type": "ephemeral",
            "text": "Please provide a valid URL"
        }

    validate_env_vars()
    pr_url = slack_command.text

    if re.match(r"^https://github.com/[^/]+/[^/]+/pull/\d+$", pr_url):
        logger.info("Processing Pull Request...")
        get_pr_details(pr_url)
        logger.info("Notification sent to Slack!")
        response_text = f"Hi {slack_command.user_name}, your review request have been submitted."
    else:
        response_text = f"Invalid Pull Request URL. Please provide a valid GitHub PR URL."
    

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


def send_to_slack(title, reviewers, pr_url, email, usergroup_map):
    user_id = find_user_id_by_email(email) if email else ""
    formatted_reviewers = convert_reviewers_to_subteam_format(reviewers, usergroup_map)
    message = f"Hi team, please help {'<@' + user_id + '> ' if user_id else ''}review this PR {pr_url} \nSummary: {title} \ncc {formatted_reviewers}\nThank you! :pepe_love:"

    try:
        return client.chat_postMessage(channel=settings.channel_id, text=message)
    except SlackApiError as e:
        logger.error(f"Error posting message: {e}")


def get_user_email(user_login):
    user_url = f"https://api.github.com/users/{user_login}"
    user_response = make_github_request(user_url)
    return user_response.get("email", "No public email")


def get_changed_files(repo_owner, repo_name, pr_number):
    pr_files_url = (
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
    )
    return make_github_request(pr_files_url)


def get_codeowners(repo_owner, repo_name):
    codeowners_url = (
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/CODEOWNERS"
    )
    response = make_github_request(codeowners_url)
    content = response.get("content", "")
    return base64.b64decode(content).decode("utf-8") if content else ""


def parse_codeowners(content):
    codeowners = {}
    for line in content.splitlines():
        if line and not line.startswith("#"):
            parts = line.split()
            if len(parts) >= 2:
                file_path = parts[0]
                owners = [owner.replace("@Thinkei/", "") for owner in parts[1:]]
                codeowners[file_path] = owners
    return codeowners


def match_files_to_owners(changed_files, codeowners):
    file_owners = {}
    for file_info in changed_files:
        filename = file_info["filename"]
        if filename == "CODEOWNERS":
            file_owners[filename] = ["squad-eternals"]
        elif filename.startswith("db/"):
            file_owners[filename] = ["squad-alchemist"]
        else:
            if filename in codeowners:
                file_owners[filename] = codeowners[filename]
            else:
                folder_matched = False
                for path, owners in codeowners.items():
                    if path.endswith("/") and filename.startswith(path):
                        file_owners[filename] = owners
                        folder_matched = True
                        break
                if not folder_matched:
                    continue
    return file_owners


def get_reviewers_ats(repo_owner, repo_name, pr_number):
    changed_files = get_changed_files(repo_owner, repo_name, pr_number)
    codeowners_content = get_codeowners(repo_owner, repo_name)
    codeowners = parse_codeowners(codeowners_content)
    file_owners = match_files_to_owners(changed_files, codeowners)

    pr_owners = {f"@{owner}" for owners in file_owners.values() for owner in owners}
    return ", ".join(pr_owners)


def contains_reviewer(reviewers, reviewer_to_check):
    return reviewer_to_check in reviewers


def get_pr_details(pr_url):
    match = re.match(r"https://github.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        raise ValueError("Invalid GitHub Pull Request URL format.")
    organization, repo, pr_number = match.groups()
    pr_api_url = f"https://api.github.com/repos/{organization}/{repo}/pulls/{pr_number}"
    response = make_github_request(pr_api_url)

    title = response.get("title", "No title")
    reviewers = (
        get_reviewers_ats(organization, repo, pr_number)
        if repo == "ats"
        else ", ".join(
            [f"@{team['name']}" for team in response.get("requested_teams", [])]
        )
    )

    if not contains_reviewer(reviewers, "@squad-eternals"):
        reviewers += ", @squad-eternals"

    user_login = response["user"]["login"]
    email = get_user_email(user_login)
    usergroup_map = get_slack_usergroups()

    send_to_slack(title, reviewers, pr_url, email, usergroup_map)


def get_slack_usergroups():
    try:
        result = client.usergroups_list()
        return {f"@{ug['handle']}": ug["id"] for ug in result["usergroups"]}
    except SlackApiError as e:
        logger.error(f"Error fetching Slack user groups: {e}")
        return {}
