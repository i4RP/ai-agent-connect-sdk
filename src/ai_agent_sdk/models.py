from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AuthStrategy(str, Enum):
    BEARER = "bearer"
    HEADER = "header"
    QUERY = "query"


class AgentProfile(BaseModel):
    id: str
    name: str
    description: str = ""
    avatar_url: str = ""
    karma: int = 0
    is_verified: bool = False
    created_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentIdentityToken(BaseModel):
    token: str
    agent_id: str
    expires_at: datetime
    scopes: list[str] = Field(default_factory=list)


class IdentityVerificationResult(BaseModel):
    valid: bool
    agent: AgentProfile | None = None
    error: str | None = None


class AppCapability(BaseModel):
    name: str
    description: str = ""
    endpoint: str = ""
    method: str = "POST"
    parameters: dict[str, Any] = Field(default_factory=dict)
    required_scopes: list[str] = Field(default_factory=list)


class AppRegistration(BaseModel):
    app_id: str
    name: str
    description: str = ""
    base_url: str = ""
    capabilities: list[AppCapability] = Field(default_factory=list)
    auth_strategy: AuthStrategy = AuthStrategy.BEARER
    auth_header: str = "Authorization"
    created_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AppInfo(BaseModel):
    app_id: str
    name: str
    description: str = ""
    base_url: str = ""
    capabilities: list[AppCapability] = Field(default_factory=list)
    agent_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class RateLimitInfo(BaseModel):
    limit: int
    remaining: int
    reset_at: datetime | None = None


class APIResponse(BaseModel):
    success: bool
    data: Any = None
    error: str | None = None
    rate_limit: RateLimitInfo | None = None


class PaginatedResponse(BaseModel):
    items: list[Any] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 25
    has_next: bool = False
