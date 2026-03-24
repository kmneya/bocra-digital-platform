from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def citizen_required(function=None):
    """
    Decorator for views that checks that the user is a citizen
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.role == 'citizen',
        login_url='/auth/login/',
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def officer_required(function=None):
    """
    Decorator for views that checks that the user is an officer
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.role == 'officer',
        login_url='/auth/login/',
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def admin_required(function=None):
    """
    Decorator for views that checks that the user is an admin
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.role == 'admin',
        login_url='/auth/login/',
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator