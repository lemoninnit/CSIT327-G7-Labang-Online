from django.urls import path
from . import views


app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('register/', views.register, name='register'),
    path('verify/', views.verify, name='verify'),
    path('welcome/', views.welcome, name='welcome'),
    path('barangay-certification/', views.barangay_certification, name='barangay_certification'),
    path('personal_info/', views.personal_info, name='personal_info'),
    path('logout_confirm/', views.logout_confirm, name='logout_confirm'),

]


