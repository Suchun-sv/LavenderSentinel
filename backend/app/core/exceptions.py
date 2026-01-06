"""Custom exceptions for LavenderSentinel."""

from typing import Any, Optional


class LavenderSentinelError(Exception):
    """Base exception for LavenderSentinel."""

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(LavenderSentinelError):
    """Resource not found error."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
    ) -> None:
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' not found",
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class ValidationError(LavenderSentinelError):
    """Data validation error."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
    ) -> None:
        super().__init__(
            message=message,
            details={"field": field} if field else {},
        )


class AuthenticationError(LavenderSentinelError):
    """Authentication failed error."""

    def __init__(
        self,
        message: str = "Authentication failed",
    ) -> None:
        super().__init__(message=message)


class RateLimitError(LavenderSentinelError):
    """Rate limit exceeded error."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(
            message=message,
            details={"retry_after": retry_after} if retry_after else {},
        )


class ExternalAPIError(LavenderSentinelError):
    """External API error."""

    def __init__(
        self,
        service: str,
        message: str,
        status_code: Optional[int] = None,
    ) -> None:
        super().__init__(
            message=f"Error from {service}: {message}",
            details={"service": service, "status_code": status_code},
        )

