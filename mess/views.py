from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import MessSubscription
from .forms import MessSubscribeForm
from students.models import Student


# ── Decorators ──
def admin_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "admin":
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "student":
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


# ── South Indian Mess Menu Data ──
MESS_MENU = {
    "Monday": {
        "breakfast": {"time": "7:30 AM – 9:30 AM", "items": ["Idli (4 pcs)", "Sambar", "Coconut Chutney", "Medu Vada (2 pcs)", "Filter Coffee / Tea"]},
        "lunch":     {"time": "12:30 PM – 2:30 PM", "items": ["Rice", "Sambar", "Rasam", "Beans Poriyal", "Curd", "Pickle", "Papadam", "Buttermilk"]},
        "dinner":    {"time": "7:30 PM – 9:30 PM", "items": ["Chapati (4 pcs)", "Vegetable Kurma", "Rice", "Tomato Rasam", "Payasam"]},
    },
    "Tuesday": {
        "breakfast": {"time": "7:30 AM – 9:30 AM", "items": ["Dosa (3 pcs)", "Sambar", "Tomato Chutney", "Pongal", "Filter Coffee / Tea"]},
        "lunch":     {"time": "12:30 PM – 2:30 PM", "items": ["Rice", "Kootu", "Rasam", "Cabbage Thoran", "Curd", "Pickle", "Papadam", "Buttermilk"]},
        "dinner":    {"time": "7:30 PM – 9:30 PM", "items": ["Parotta (3 pcs)", "Egg Curry", "Rice", "Pepper Rasam", "Banana"]},
    },
    "Wednesday": {
        "breakfast": {"time": "7:30 AM – 9:30 AM", "items": ["Puttu & Kadala Curry", "Appam (3 pcs)", "Stew", "Banana", "Filter Coffee / Tea"]},
        "lunch":     {"time": "12:30 PM – 2:30 PM", "items": ["Rice", "Sambar", "Rasam", "Avial", "Curd", "Pickle", "Papadam", "Buttermilk"]},
        "dinner":    {"time": "7:30 PM – 9:30 PM", "items": ["Chapati (4 pcs)", "Paneer Butter Masala", "Rice", "Dal Fry", "Gulab Jamun (2 pcs)"]},
    },
    "Thursday": {
        "breakfast": {"time": "7:30 AM – 9:30 AM", "items": ["Idiyappam (4 pcs)", "Coconut Milk", "Upma", "Boiled Egg", "Filter Coffee / Tea"]},
        "lunch":     {"time": "12:30 PM – 2:30 PM", "items": ["Chicken Biryani / Veg Biryani", "Raita", "Onion Salad", "Chicken Gravy", "Buttermilk"]},
        "dinner":    {"time": "7:30 PM – 9:30 PM", "items": ["Dosa (3 pcs)", "Sambar", "Chutney Varieties", "Rice", "Curd Rice"]},
    },
    "Friday": {
        "breakfast": {"time": "7:30 AM – 9:30 AM", "items": ["Poori (4 pcs)", "Potato Masala", "Kesari Bath", "Banana", "Filter Coffee / Tea"]},
        "lunch":     {"time": "12:30 PM – 2:30 PM", "items": ["Rice", "Fish Curry / Sambar", "Rasam", "Thoran", "Curd", "Pickle", "Papadam", "Buttermilk"]},
        "dinner":    {"time": "7:30 PM – 9:30 PM", "items": ["Chapati (4 pcs)", "Chole Masala", "Rice", "Tomato Rasam", "Ice Cream"]},
    },
    "Saturday": {
        "breakfast": {"time": "7:30 AM – 9:30 AM", "items": ["Rava Dosa (3 pcs)", "Sambar", "Peanut Chutney", "Upma", "Filter Coffee / Tea"]},
        "lunch":     {"time": "12:30 PM – 2:30 PM", "items": ["Lemon Rice", "Sambar", "Rasam", "Poriyal", "Curd", "Pickle", "Papadam", "Buttermilk"]},
        "dinner":    {"time": "7:30 PM – 9:30 PM", "items": ["Parotta (3 pcs)", "Chicken Curry / Paneer Masala", "Rice", "Rasam", "Fruit Salad"]},
    },
    "Sunday": {
        "breakfast": {"time": "7:30 AM – 9:30 AM", "items": ["Uttapam (3 pcs)", "Sambar", "Coconut Chutney", "Pongal", "Filter Coffee / Tea"]},
        "lunch":     {"time": "12:30 PM – 2:30 PM", "items": ["Mutton Biryani / Veg Dum Biryani", "Raita", "Onion Salad", "Gravy", "Payasam"]},
        "dinner":    {"time": "7:30 PM – 9:30 PM", "items": ["Chapati (4 pcs)", "Mixed Veg Curry", "Rice", "Dal Tadka", "Kheer"]},
    },
}


# ════════════════════════════════
#       STUDENT VIEWS
# ════════════════════════════════

@login_required
@student_required
def student_mess_menu(request):
    """View the weekly mess menu and manage subscription."""
    student = get_object_or_404(Student, user=request.user)
    active_sub = MessSubscription.objects.filter(student=student, status="Active").first()

    # Auto-expire if date has passed
    if active_sub and active_sub.is_expired:
        active_sub.status = "Expired"
        active_sub.save()
        active_sub = None

    # Get current day menu
    import calendar
    today_name = calendar.day_name[timezone.now().weekday()]
    today_menu = MESS_MENU.get(today_name, {})

    # Determine current meal
    now = timezone.now()
    hour = now.hour
    if 6 <= hour < 10:
        current_meal = "breakfast"
    elif 11 <= hour < 15:
        current_meal = "lunch"
    elif 18 <= hour < 22:
        current_meal = "dinner"
    else:
        current_meal = None

    # Past subscriptions
    past_subs = MessSubscription.objects.filter(
        student=student
    ).exclude(status="Active").order_by("-end_date")[:5]

    context = {
        "student": student,
        "active_sub": active_sub,
        "menu": MESS_MENU,
        "today_name": today_name,
        "today_menu": today_menu,
        "current_meal": current_meal,
        "past_subs": past_subs,
    }
    return render(request, "student_panel/mess/menu.html", context)


@login_required
@student_required
def student_mess_subscribe(request):
    """Subscribe to a mess plan."""
    student = get_object_or_404(Student, user=request.user)

    # Check if already has active subscription
    active_sub = MessSubscription.objects.filter(student=student, status="Active").first()
    if active_sub and not active_sub.is_expired:
        messages.warning(request, f"You already have an active mess subscription ({active_sub.get_plan_display()}) until {active_sub.end_date.strftime('%d %b %Y')}.")
        return redirect("student_mess_menu")

    if request.method == "POST":
        form = MessSubscribeForm(request.POST)
        if form.is_valid():
            plan = form.cleaned_data["plan"]
            start_date = form.cleaned_data["start_date"]
            days = 30 if plan == "30_days" else 15
            amount = 3000 if plan == "30_days" else 1800
            end_date = start_date + timedelta(days=days)

            sub = MessSubscription(
                student=student,
                plan=plan,
                amount=amount,
                start_date=start_date,
                end_date=end_date,
                status="Active",
            )
            sub.save()
            messages.success(request, f"🎉 Mess subscription activated! Plan: {sub.get_plan_display()} — Valid until {sub.end_date.strftime('%d %b %Y')}.")
            return redirect("student_mess_menu")
    else:
        form = MessSubscribeForm(initial={"start_date": timezone.now().date()})

    return render(request, "student_panel/mess/subscribe.html", {
        "form": form,
        "student": student,
    })


@login_required
@student_required
def student_mess_cancel(request):
    """Cancel an active mess subscription."""
    student = get_object_or_404(Student, user=request.user)
    active_sub = MessSubscription.objects.filter(student=student, status="Active").first()

    if not active_sub:
        messages.warning(request, "You don't have an active mess subscription to cancel.")
        return redirect("student_mess_menu")

    if request.method == "POST":
        active_sub.status = "Cancelled"
        active_sub.save()
        messages.success(request, "Your mess subscription has been cancelled successfully.")
        return redirect("student_mess_menu")

    return render(request, "student_panel/mess/cancel.html", {
        "sub": active_sub,
        "student": student,
    })


# ════════════════════════════════
#       ADMIN VIEWS
# ════════════════════════════════

@login_required
@admin_required
def admin_mess_dashboard(request):
    """Admin view — overview of all mess subscriptions."""
    total_active = MessSubscription.objects.filter(status="Active").count()
    total_expired = MessSubscription.objects.filter(status="Expired").count()
    total_cancelled = MessSubscription.objects.filter(status="Cancelled").count()
    total_revenue = sum(
        s.amount for s in MessSubscription.objects.filter(status__in=["Active", "Expired"])
    )

    # Active subscriptions with student details
    active_subs = MessSubscription.objects.filter(
        status="Active"
    ).select_related("student", "student__user").order_by("-start_date")

    all_subs = MessSubscription.objects.select_related(
        "student", "student__user"
    ).order_by("-created_at")[:20]

    # Plan breakdown
    plan_30 = MessSubscription.objects.filter(plan="30_days", status="Active").count()
    plan_15 = MessSubscription.objects.filter(plan="15_days", status="Active").count()

    context = {
        "total_active": total_active,
        "total_expired": total_expired,
        "total_cancelled": total_cancelled,
        "total_revenue": total_revenue,
        "active_subs": active_subs,
        "all_subs": all_subs,
        "plan_30": plan_30,
        "plan_15": plan_15,
        "menu": MESS_MENU,
    }
    return render(request, "admin_panel/mess/dashboard.html", context)
