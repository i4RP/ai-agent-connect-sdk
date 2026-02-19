from __future__ import annotations


class AgentSDKError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(AgentSDKError):
    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, status_code=401)


class AuthorizationError(AgentSDKError):
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message, status_code=403)


class NotFoundError(AgentSDKError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class RateLimitError(AgentSDKError):
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: float | None = None,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, status_code=429)


class ValidationError(AgentSDKError):
    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message, status_code=422)


class TransportError(AgentSDKError):
    def __init__(self, message: str = "Transport error") -> None:
        super().__init__(message)


class ProviderError(AgentSDKError):
    def __init__(self, message: str = "Provider error", provider: str = "unknown") -> None:
        self.provider = provider
        super().__init__(message)


class ConfigurationError(AgentSDKError):
    def __init__(self, message: str = "Configuration error") -> None:
        super().__init__(message)


def raise_for_status(status_code: int, body: str) -> None:
    if status_code == 401:
        raise AuthenticationError(body)
    if status_code == 403:
        raise AuthorizationError(body)
    if status_code == 404:
        raise NotFoundError(body)
    if status_code == 422:
        raise ValidationError(body)
    if status_code == 429:
        raise RateLimitError(body)
    if status_code >= 400:
        raise AgentSDKError(body, status_code=status_code)
