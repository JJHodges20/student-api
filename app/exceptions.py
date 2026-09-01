"""
Custom application exceptions.
"""


class NotFoundException(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class DuplicateException(Exception):
    """Raised when a unique value already exists."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class BadRequestException(Exception):
    """Raised when a request violates business rules."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)