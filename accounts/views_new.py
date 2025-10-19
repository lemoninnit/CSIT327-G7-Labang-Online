"""
Main views module for Labang Online
Imports and exposes views from organized modules
"""

# Import all views from organized modules
from .views.auth_views import login, logout_confirm
from .views.user_views import register, welcome, personal_info, edit_profile, complete_profile
from .views.password_views import forgot_password, verify_code, reset_password

# Export all views for URL configuration
__all__ = [
    'login',
    'logout_confirm', 
    'register',
    'welcome',
    'personal_info',
    'edit_profile',
    'complete_profile',
    'forgot_password',
    'verify_code',
    'reset_password',
]
