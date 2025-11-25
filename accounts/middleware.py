from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def staff_required(login_url=None):
    """
    Decorator for views that checks that the user is logged in and is staff,
    redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=login_url,
    )
    return actual_decorator

class AdminAccessMiddleware:
    """
    Middleware to ensure only staff users can access Django admin.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if request.path == '/admin/login/':
                return self.get_response(request)
            if request.user.is_authenticated and not request.user.is_staff:
                raise PermissionDenied("You must be a staff member to access the admin area.")
        return self.get_response(request)