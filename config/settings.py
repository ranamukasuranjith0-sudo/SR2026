from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List


class Settings(BaseSettings):
    # Telegram
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    allowed_telegram_ids: List[int] = Field(default=[], env="ALLOWED_TELEGRAM_IDS")

    # Anthropic
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    claude_model: str = Field(default="claude-sonnet-4-6", env="CLAUDE_MODEL")

    # Tavily
    tavily_api_key: str = Field(..., env="TAVILY_API_KEY")

    # LinkedIn
    linkedin_access_token: Optional[str] = Field(default=None, env="LINKEDIN_ACCESS_TOKEN")
    linkedin_person_urn: Optional[str] = Field(default=None, env="LINKEDIN_PERSON_URN")

    # Google
    google_token_path: str = Field(default="config/google_token.json", env="GOOGLE_TOKEN_PATH")
    google_credentials_path: str = Field(
        default="config/google_credentials.json", env="GOOGLE_CREDENTIALS_PATH"
    )
    google_user_email: Optional[str] = Field(default=None, env="GOOGLE_USER_EMAIL")
    timezone: str = Field(default="Europe/Paris", env="TIMEZONE")

    # Assistant personality
    assistant_name: str = Field(default="Alex", env="ASSISTANT_NAME")
    assistant_language: str = Field(default="fr", env="ASSISTANT_LANGUAGE")
    assistant_tone: str = Field(default="friendly", env="ASSISTANT_TONE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def is_restricted(self) -> bool:
        return len(self.allowed_telegram_ids) > 0

    def is_allowed(self, user_id: int) -> bool:
        return not self.is_restricted or user_id in self.allowed_telegram_ids


settings = Settings()
