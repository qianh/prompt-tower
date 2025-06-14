import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 显式加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()


class Settings(BaseSettings):
    # 基础配置
    APP_NAME: str = "Prompt Management System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8010
    API_PREFIX: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 文件存储配置
    PROMPT_TEMPLATE_DIR: Path = Path("prompt-template")

    # LLM配置
    GEMINI_API_KEY: Optional[str] = None
    QWEN_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    DEFAULT_LLM: str = "gemini"

    # LLM模型配置
    GEMINI_MODEL: str = "gemini-pro"
    QWEN_MODEL: str = "qwen-turbo"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # LLM请求配置
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000
    LLM_TIMEOUT: int = 60  # 改为60秒，之前是30秒

    # MCP Server配置
    MCP_SERVER_HOST: str = "0.0.0.0"
    MCP_SERVER_PORT: int = 8011

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "logs/app.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.PROMPT_TEMPLATE_DIR.mkdir(exist_ok=True)

        if self.LOG_FILE:
            log_dir = Path(self.LOG_FILE).parent
            log_dir.mkdir(exist_ok=True)


settings = Settings()
