from . import views
from django.urls import path
app_name = 'auth'


urlpatterns = [
    path('register/', views.CreateUser.as_view()),
    path('login/', views.LoginUser.as_view()),
    path('contacts/all/', views.ListUsers.as_view()),
    # path('contacts/*', views.LoginUser.as_view()),
]