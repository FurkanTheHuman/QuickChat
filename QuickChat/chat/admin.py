from django.contrib import admin
from .models import ChatModel, BlockingModel, LogModel, EventLogModel
from userauth.models import UserModel
# Register your models here.

class LogModelAdmin(admin.ModelAdmin):
    model = LogModel
    empty_value_display = '-un-registered-'
    list_display = ('error_message', 'location', 'responsible_user')
    

class EventLogModelAdmin(admin.ModelAdmin):
    model = EventLogModel
    empty_value_display = '-un-registered-'
    list_display = ('event', 'user', 'happened_at')
    

admin.site.register(ChatModel)
admin.site.register(UserModel)
admin.site.register(BlockingModel)
admin.site.register(LogModel, LogModelAdmin)
admin.site.register(EventLogModel, EventLogModelAdmin)