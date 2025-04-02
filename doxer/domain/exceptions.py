class DomainException(Exception):
    """Base exception for all domain errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class NotFoundError(DomainException):
    """Base exception for all not found errors."""

class ConflictError(DomainException):
    """Base exception for all conflict errors."""

class ValidationError(DomainException):
    """Base exception for all validation errors."""

class AuthenticationError(DomainException):
    """Base exception for all authentication errors."""

class TokenInvalidError(AuthenticationError):
    """Raised when a token is invalid or has been used."""
    def __init__(self, message: str = "Invalid token or token has already been used"):
        super().__init__(message)

class LinkNameExistsError(ConflictError):
    """Raised when attempting to create a link with a name that already exists."""
    def __init__(self, name: str):
        super().__init__(f"Link with name '{name}' already exists")

class LinkNotFoundError(NotFoundError):
    """Raised when a link with the given name is not found."""
    def __init__(self, name: str):
        super().__init__(f"Link with name '{name}' not found")

class UserDataNotFoundError(NotFoundError):
    """Raised when user data with the given token is not found."""
    def __init__(self, token: str):
        super().__init__(f"User data with token '{token}' not found")

