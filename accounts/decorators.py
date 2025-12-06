from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def role_required(required_role):
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            user = request.user

            if user.role != required_role:
                # Redirect to user's correct dashboard
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                elif user.role == 'patient':
                    return redirect('patient_dashboard')
                elif user.role == 'provider':
                    return redirect('provider_dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
