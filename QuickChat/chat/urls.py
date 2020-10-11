from . import views
from django.urls import path

app_name = 'chat'

urlpatterns = [
    
    path('send_message/', views.SendMessage.as_view()),
    path('chat/history/', views.ChatHistory.as_view()),
    path('chat/last_messages/', views.LastMessages.as_view()),
    path('block/user/', views.BlockUser.as_view()),
    path('unblock/user/', views.UnBlockUser.as_view()),
    
]