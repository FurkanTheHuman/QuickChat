from .models import LogModel
NOT_AUTHENTICATED = 'not authenticated'
USER_NOT_FOUND = 'user not found'
REPEATED_BLOCKING_ATTEMPT = 'repeated blocking attempt'
REPEATED_UNBLOCKING_ATTEMPT = 'repeated unblocking attempt'
USER_ALREADY_EXISTS = "user already exists"
TOKEN_EXPIRED = "token expired"
WRONG_TOKEN = "wrong token requested"
WRONG_PASSWORD = "wrong password requested"


def log_error(error_message, location, responsible_user=None):
    LogModel(error_message=error_message, location=location, responsible_user=responsible_user).save()
