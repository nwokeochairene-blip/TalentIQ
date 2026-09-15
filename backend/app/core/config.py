from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TalentIQ AI Recruitment & Career Intelligence API"
    app_version: str = "1.0.0"
    environment: str = "development"

    model_name: str = "TalentIQ Hybrid V2"
    model_feature_count: int = 100019

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
