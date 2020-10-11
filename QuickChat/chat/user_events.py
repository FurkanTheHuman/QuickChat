from .models import EventLogModel 

LOGIN = 'login'
REGISTER = 'register'
SEND_MESSAGE = 'send message'
BLOCK_USER = 'block user'
UNBLOCK_USER = 'unblock user'
TOKEN_VERFIED = 'token verified'
SESSION_UPDATE = 'session update'
SHOW_MESSAGES = 'show message'
LIST_USERS = 'list users'

def log_event(event, user=None):
    EventLogModel(event=event, user=user).save()
