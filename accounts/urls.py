from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('register/', views.register, name='register'),
    path('welcome/', views.welcome, name='welcome'),
    path('logout_confirm/', views.logout_confirm, name='logout_confirm'),
    path('personal_info/', views.personal_info, name='personal_info'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('complete_profile/', views.complete_profile, name='complete_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('complete_profile/', views.complete_profile, name='complete_profile'),
    path('personal_info/', views.personal_info, name='personal_info'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    
]
