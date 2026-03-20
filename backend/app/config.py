from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "NarrativeAI"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://narrativeai:narrativeai_dev@localhost:5432/narrativeai"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Elasticsearch
    elasticsearch_url: str = "http://localhost:9200"

    # Anthropic
    anthropic_api_key: str = ""

    # Agent settings
    agent_timeout: int = 60
    max_retries: int = 3

    # Scraping
    scrape_rate_limit: float = 1.0  # requests per second
    scrape_user_agent: str = "NarrativeAI/0.1 (Research)"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
