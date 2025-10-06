from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('verify/', views.verify, name='verify'),
    path('welcome/', views.welcome, name='welcome'),
    path('barangay-certification/', views.barangay_certification, name='barangay_certification'),
]


