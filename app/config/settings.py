from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    github_token: str = ""
    bot_token: str = ""
    channel_id: str = ""
    slack_signing_secret: str = ""
    
    class Config:
        env_file = ".env"


settings = Settings()
