class SecureAuthApiException(Exception):
    default_message = "Something went wrong"
    error_code = "ErrorCodeNotDefined"

    def __init__(self, message=None):
        self.message = message if message else self.default_message
        self.error_code = self.error_code


class AuthenticationError(SecureAuthApiException):
    default_message = "Wrong login or password"
    error_code = "AuthenticationError"


class NotFoundException(SecureAuthApiException):
    message = "Not found"
    error_code = "NotFoundError"


class AlreadyExistsException(SecureAuthApiException):
    message = "Already Exists"
    error_code = "DataAlreadyExistsError"
