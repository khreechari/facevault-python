"""FaceVault SDK exceptions."""


class FaceVaultError(Exception):
    """Base exception for FaceVault API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AuthError(FaceVaultError):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(message, status_code=401)


class NotFoundError(FaceVaultError):
    """Raised when a resource is not found (404)."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class RateLimitError(FaceVaultError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)
