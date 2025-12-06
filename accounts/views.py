from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import models

from .forms import PatientSignupForm
from .decorators import role_required
from .models import User, Appointment
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from datetime import datetime, time
from django.utils import timezone
from datetime import datetime, date as dt_date
from .models import Appointment, User
from django.contrib import messages
from .decorators import role_required
import calendar
from datetime import date, datetime
from django.urls import reverse


User = get_user_model()


# ---------------------------
# Authentication Views
# ---------------------------

def patient_signup(request):
    if request.method == 'POST':
        form = PatientSignupForm(request.POST)
        if form.is_valid():
            form.save()

            # Pass a flag to template
            return render(request, 'accounts/patient_signup.html', {
                'form': PatientSignupForm(),
                'signup_success': True
            })

    else:
        form = PatientSignupForm()

    return render(request, 'accounts/patient_signup.html', {'form': form})



def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.role == 'provider':
            return redirect('provider_dashboard')
        else:
            return redirect('patient_dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # Redirect based on role
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'provider':
                return redirect('provider_dashboard')
            elif user.role == 'patient':
                return redirect('patient_dashboard')

        return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ---------------------------
# Dashboard Views
# ---------------------------

@role_required('admin')
def admin_dashboard(request):
    return render(request, 'accounts/admin_home.html')


@role_required('patient')
def patient_dashboard(request):
    return render(request, 'accounts/patient_home.html')


@role_required('provider')
def provider_dashboard(request):
    return render(request, 'accounts/provider_home.html')


# ---------------------------
# Admin — Manage Providers
# ---------------------------

@role_required('admin')
def provider_list(request):
    providers = User.objects.filter(role='provider')
    return render(request, 'accounts/provider_list.html', {'providers': providers})


@role_required('admin')
def provider_add(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        designation = request.POST['designation']

        User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password),
            role='provider',
            designation=designation,
            is_staff=False,
            is_superuser=False
        )

        messages.success(request, "Healthcare provider created successfully!")
        return redirect('provider_list')

    return render(request, 'accounts/provider_add.html')


@role_required('admin')
def provider_update(request, user_id):
    provider = User.objects.get(id=user_id, role='provider')

    if request.method == 'POST':
        provider.username = request.POST['username']
        provider.first_name = request.POST['first_name']
        provider.last_name = request.POST['last_name']
        provider.email = request.POST['email']
        provider.designation = request.POST['designation']

        new_password = request.POST['password']
        if new_password.strip():
            provider.password = make_password(new_password)

        provider.save()
        messages.success(request, "Provider updated successfully!")
        return redirect('provider_list')

    return render(request, 'accounts/provider_update.html', {
        'provider': provider
    })


@role_required('admin')
def provider_delete(request, user_id):
    provider = User.objects.get(id=user_id, role='provider')
    provider.delete()
    return redirect('provider_list')


# ---------------------------
# Patient — Appointment System
# ---------------------------

@role_required('patient')
def appointment_list(request):
    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by("date", "start_time")

    return render(request, 'accounts/appointment_list.html', {"appointments": appointments})


@role_required('patient')
def appointment_add(request):
    providers = User.objects.filter(role='provider')

    if request.method == 'POST':
        provider_id = request.POST['provider']
        date_str = request.POST['date']
        start_str = request.POST['start_time']
        end_str = request.POST['end_time']
        reason = request.POST['reason']

        # Convert inputs to Python objects
        try:
            appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_time_obj = datetime.strptime(start_str, "%H:%M").time()
            end_time_obj = datetime.strptime(end_str, "%H:%M").time()
        except ValueError:
            return render(request, 'accounts/appointment_add.html', {
                "providers": providers,
                "today": dt_date.today().isoformat(),
                "popup": "❌ Invalid date or time format."
            })

        now = timezone.localtime()
        today = now.date()

        # -----------------------------
        # Past date
        # -----------------------------
        if appt_date < today:
            return render(request, 'accounts/appointment_add.html', {
                "providers": providers,
                "today": today.isoformat(),
                "popup": "❌ You cannot select a past date."
            })

        # -----------------------------
        # Booking today — start time must be >= current time
        # -----------------------------
        if appt_date == today and start_time_obj < now.time():
            return render(request, 'accounts/appointment_add.html', {
                "providers": providers,
                "today": today.isoformat(),
                "popup": "❌ Start time cannot be earlier than the current time."
            })

        # -----------------------------
        # End must be AFTER start
        # -----------------------------
        if end_time_obj <= start_time_obj:
            return render(request, 'accounts/appointment_add.html', {
                "providers": providers,
                "today": today.isoformat(),
                "popup": "❌ End time must be AFTER start time."
            })

        # -----------------------------
        # Check for patient conflict
        # -----------------------------
        conflict = Appointment.objects.filter(
            patient=request.user,
            date=appt_date,
            start_time__lt=end_time_obj,
            end_time__gt=start_time_obj
        ).exists()

        if conflict:
            return render(request, 'accounts/appointment_add.html', {
                "providers": providers,
                "today": today.isoformat(),
                "popup": "❌ You already have an appointment during this time range."
            })

        provider = User.objects.get(id=provider_id)

        # Create appointment
        Appointment.objects.create(
            patient=request.user,
            provider=provider,
            date=appt_date,
            start_time=start_time_obj,
            end_time=end_time_obj,
            reason=reason,
            status='pending'
        )

        # SUCCESS POPUP — then redirect
        return render(request, 'accounts/appointment_add.html', {
            "providers": providers,
            "today": today.isoformat(),
            "success_popup": "✅ Appointment Request Submitted!"
        })

    # Normal GET request
    return render(request, 'accounts/appointment_add.html', {
        "providers": providers,
        "today": dt_date.today().isoformat()
    })


@role_required('patient')
def appointment_reschedule(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id, patient=request.user)

    context = {
        "appointment": appointment,
        "today": dt_date.today().isoformat(),
        "success": False,
        "error": None
    }

    if request.method == 'POST':
        date_str = request.POST['date']
        start_str = request.POST['start_time']
        end_str = request.POST['end_time']

        try:
            new_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            new_start = datetime.strptime(start_str, "%H:%M").time()
            new_end = datetime.strptime(end_str, "%H:%M").time()
        except:
            context["error"] = "invalid"
            return render(request, 'accounts/appointment_update.html', context)

        now = timezone.localtime()
        today = now.date()

        if new_date < today:
            context["error"] = "past"
            return render(request, 'accounts/appointment_update.html', context)

        if new_date == today and new_start < now.time():
            context["error"] = "startpast"
            return render(request, 'accounts/appointment_update.html', context)

        if new_end <= new_start:
            context["error"] = "endbeforestart"
            return render(request, 'accounts/appointment_update.html', context)

        conflict = Appointment.objects.filter(
            patient=request.user,
            date=new_date,
            start_time__lt=new_end,
            end_time__gt=new_start
        ).exclude(id=appointment.id).exists()

        if conflict:
            context["error"] = "conflict"
            return render(request, 'accounts/appointment_update.html', context)

        # Save reschedule request
        appointment.date = new_date
        appointment.start_time = new_start
        appointment.end_time = new_end
        appointment.status = "reschedule_requested"
        appointment.save()

        context["success"] = True
        return render(request, 'accounts/appointment_update.html', context)

    return render(request, 'accounts/appointment_update.html', context)

@role_required('patient')
def appointment_delete(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id, patient=request.user)
    appointment.delete()
    return redirect('appointment_list')
@role_required('patient')
def patient_change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully!")
            return redirect('patient_profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/patient_change_password.html", {"form": form})

@role_required('provider')
def provider_appointments(request):
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    # UPCOMING: future OR ongoing today
    upcoming = Appointment.objects.filter(
        provider=request.user
    ).filter(
        models.Q(date__gt=today) |
        models.Q(date=today, end_time__gte=current_time)
    ).order_by("date", "start_time")

    # COMPLETED: past OR already finished today
    completed = Appointment.objects.filter(
        provider=request.user
    ).filter(
        models.Q(date__lt=today) |
        models.Q(date=today, end_time__lt=current_time)
    ).order_by("-date", "-start_time")

    return render(request, "accounts/provider_appointment_list.html", {
        "upcoming": upcoming,
        "completed": completed,
    })

@role_required('provider')
def approve_appointment(request, appt_id):
    appt = Appointment.objects.get(id=appt_id, provider=request.user)

    # Check provider time conflict
    conflict = Appointment.objects.filter(
        provider=request.user,
        date=appt.date,
        start_time__lt=appt.end_time,
        end_time__gt=appt.start_time,
        status="approved"
    ).exclude(id=appt.id).exists()

    if conflict:
        # Redirect with query parameter (NOT Django messages)
        return redirect('/provider/appointments/?clash=1')

    # If no conflict → approve
    appt.status = "approved"
    appt.save()

    return redirect('/provider/appointments/?approved=1')

@role_required('provider')
def reject_appointment(request, appt_id):
    appt = Appointment.objects.get(id=appt_id, provider=request.user)

    appt.status = "rejected"
    appt.save()

    messages.success(request, "❌ Appointment Rejected.")
    return redirect('provider_appointments')
@role_required('provider')
def provider_profile(request):
    provider = request.user

    if request.method == "POST":
        provider.username = request.POST["username"]
        provider.first_name = request.POST["first_name"]
        provider.last_name = request.POST["last_name"]
        provider.email = request.POST["email"]
        provider.designation = request.POST["designation"]
        provider.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("provider_profile")

    return render(request, "accounts/provider_profile.html", {
        "provider": provider
    })

@role_required('provider')
def provider_change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevent logout
            messages.success(request, "Password updated successfully!")
            return redirect("provider_profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/provider_change_password.html", {
        "form": form
    })

@role_required('provider')
def provider_calendar(request):
    today = date.today()

    # Selected year/month from query params
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    # Handle month overflow/underflow
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    cal = calendar.Calendar()

    # Get provider's appointments for that month
    appointments = Appointment.objects.filter(
        provider=request.user,
        date__year=year,
        date__month=month
    )

    # Dictionary: "day" -> [appointments]
    appointment_map = {}
    for appt in appointments:
        key = str(appt.date.day)  # string key for template
        appointment_map.setdefault(key, []).append(appt)

    # Calendar grid
    month_days = cal.monthdayscalendar(year, month)

    return render(request, "accounts/provider_calendar.html", {
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "month_days": month_days,
        "appointment_map": appointment_map,
        "today": today
    })


@role_required('provider')
def provider_calendar_day(request, year, month, day):
    appts = Appointment.objects.filter(
        provider=request.user,
        date=date(year, month, day)
    ).order_by("start_time")

    return render(request, "accounts/provider_calendar_day.html", {
        "appts": appts,
        "day": day,
        "month": calendar.month_name[month],
        "year": year
    })
@role_required('patient')
def patient_profile(request):
    patient = request.user

    if request.method == "POST":
        patient.first_name = request.POST["first_name"]
        patient.last_name = request.POST["last_name"]
        patient.username = request.POST["username"]
        patient.email = request.POST["email"]
        patient.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("patient_profile")

    return render(request, "accounts/patient_profile.html", {
        "patient": patient
    })
@role_required('admin')
def admin_profile(request):
    admin = request.user

    if request.method == "POST":
        admin.username = request.POST["username"]
        admin.first_name = request.POST["first_name"]
        admin.last_name = request.POST["last_name"]
        admin.email = request.POST["email"]
        admin.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("admin_profile")

    return render(request, "accounts/admin_profile.html", {
        "admin": admin
    })


@role_required('admin')
def admin_change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully!")
            return redirect("admin_profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/admin_change_password.html", {
        "form": form
    })
