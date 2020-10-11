from django.db import models
import uuid
from datetime import datetime, timedelta
import pytz

# Create your models here.

class UserModel(models.Model):
    username = models.CharField(max_length=120, blank=False, unique=True)
    password = models.CharField(max_length=120, blank=False)
    email = models.CharField(max_length=120, blank=False, unique=True)
    token = models.UUIDField(default = uuid.uuid4) 
    expiration_date = models.DateTimeField(default=datetime.utcnow().replace(tzinfo=pytz.utc) + timedelta(days=1))

    def __str__(self):
        return self.username
    
    def is_exists(self):
        return self != None