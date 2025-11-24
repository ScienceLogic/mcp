from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    SKY_COMP_ENABLE: bool = True
    SKY_COMP_API_URL: Optional[str] = Field(pattern=r'\/$', default=None)
    SKY_COMP_API_KEY: Optional[str] = Field(min_length=1, default=None)
    SKY_COMP_PREFIX: Optional[str] = Field(default="sc_")
    SKY_ONE_ENABLE: bool = True
    SKY_ONE_API_URL: Optional[str] = Field(pattern=r'\/$', default=None)
    SKY_ONE_API_KEY: Optional[str] = Field(min_length=1, default=None)
    SKY_ONE_PREFIX: Optional[str] = Field(default="s1_")
    MAX_QUERY_LIMIT: Optional[int] = 50
    LOG_LEVEL: str = "INFO"
    TOOL_TIMEOUT_MS: int = 10000
    SUPPORT_ELICITATION: bool = True

_CONFIG = None

def get_config() -> Config:
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = Config()
    return _CONFIG
