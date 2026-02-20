from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


@dataclass
class SDKConfig:
    api_key: str = ""
    app_key: str = ""
    base_url: str = ""
    timeout: float = 30.0
    retries: int = 3
    retry_delay: float = 1.0
    retry_max_delay: float = 60.0
    retry_backoff_factor: float = 2.0
    rate_limit_enabled: bool = True
    rate_limit_max_requests: int = 100
    rate_limit_window: float = 60.0
    log_requests: bool = False
    log_responses: bool = False
    custom_headers: dict[str, str] = field(default_factory=dict)
    provider: str = "generic"

    @classmethod
    def from_env(cls, prefix: str = "AGENT_SDK") -> SDKConfig:
        load_dotenv()
        return cls(
            api_key=os.getenv(f"{prefix}_API_KEY", ""),
            app_key=os.getenv(f"{prefix}_APP_KEY", ""),
            base_url=os.getenv(f"{prefix}_BASE_URL", ""),
            timeout=float(os.getenv(f"{prefix}_TIMEOUT", "30.0")),
            retries=int(os.getenv(f"{prefix}_RETRIES", "3")),
            retry_delay=float(os.getenv(f"{prefix}_RETRY_DELAY", "1.0")),
            rate_limit_enabled=os.getenv(f"{prefix}_RATE_LIMIT", "true").lower() == "true",
            log_requests=os.getenv(f"{prefix}_LOG_REQUESTS", "false").lower() == "true",
            log_responses=os.getenv(f"{prefix}_LOG_RESPONSES", "false").lower() == "true",
            provider=os.getenv(f"{prefix}_PROVIDER", "generic"),
        )
