from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from functools import wraps

def group_required(*group_name):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name__in=group_name).exists():
                return view_func(request, *args, **kwargs)
            else :
                raise PermissionDenied
        return _wrapped_view
    return decorator