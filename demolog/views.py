import json
from datetime import time
import string
import random
from traceback import print_tb
import requests
import re

from django.shortcuts import render, redirect
from demolog.forms import *
from demolog.models import *
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from datetime import tzinfo
from django.core.management import call_command
from demo_admin.management.commands import generate_data

def index(request):
    return render(request, "index.html")


def registration(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                # you_are = form.cleaned_data.get('you_are')
                # members_value = form.cleaned_data.get('members')

                # # if you_are != 'Family':
                # #     # If 'You Are' is not 'Family', set members_value to None
                # #     members_value = 1

                # # Save the form with updated members_value
                # instance = form.save(commit=False)
                # instance.members = members_value
                form.save()

                messages.success(request, "Registration successful! Please log in.")
                return redirect("login")
        else:
            form = UserRegisterForm()
        return render(request, "customer-reg.html", {"form": form})
    return redirect("dashboard")


def user_login(request):
    if not request.user.is_authenticated:
        try:
            if request.method == "POST":
                form = UserLoginForm(request.POST)
                if form.is_valid():
                    phone = form.cleaned_data.get("phone")
                    password = form.cleaned_data.get("password")
                    user = authenticate(request, phone=phone, password=password)
                    print(user)
                    if user is not None:
                        login(request, user)
                        # messages.success(request, "You are successfully logged in!")
                        return redirect("dashboard")
                        print("You are logged in")

                    else:
                        print("You are not logged in")
                        messages.error(request, "Invalid user or password")
                        return redirect("login")
            else:
                form = UserLoginForm()
            return render(request, "customer-login.html", {"form": form})
        except Exception:
            messages.error(request, "An error occurred. Please try again")
            return redirect("login")
    return redirect("dashboard")


@login_required
def user_logout(request):
    logout(request)
    # messages.success(request, "You have logged out!")
    return redirect("/")


@login_required
def dashboard(request):
    
    try:    
        user_dashboard = Dashboard.objects.get(user=request.user)
    except Dashboard.DoesNotExist:
        messages.error(request, "Dashboard not available for the current user")
        return redirect("home")

    current_plan = None
    if user_dashboard.current_plan:
        current_plan = (
            f"{user_dashboard.current_plan.plan} - {user_dashboard.current_plan.type}"
        )

    # Get all unique plan durations
    durations = Package.objects.values_list("plan", flat=True).distinct()
    # Retrieve regular and premium plans for each duration
    current_plans = []
    for duration in durations:
        regular_plan = Package.objects.filter(plan=duration, type="Regular").first()
        premium_plan = Package.objects.filter(plan=duration, type="Premium").first()

        # print(duration)
        # print(regular_plan)
        # print(premium_plan)

        if regular_plan and premium_plan:
            current_plans.append(
                {
                    "duration": duration,
                    "regular_plan": regular_plan,
                    "premium_plan": premium_plan,
                }
            )


    context = {
        "user_dashboard": user_dashboard,
        "current_plans": current_plans,
        "current_plan": current_plan,
    }

    return render(request, "dashboard.html", context)


def is_valid_time(meal_off_choice, current_time):

    if meal_off_choice == "Lunch":
        return time(20, 0) <= current_time or current_time <= time(9, 0)
    elif meal_off_choice == "Dinner":
        return time(20, 0) <= current_time or current_time <= time(18, 0)
    elif meal_off_choice == "Both":
        return time(20, 0) <= current_time <= time(9, 0)


def meal_status_on_time(meal_off_choice, current_time, previous_choice):
    if meal_off_choice == "None":
        return is_valid_time(previous_choice, current_time)


def toggle_meal_state(request):

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        dashboard = Dashboard.objects.get(user=user_id)
        meal_off_choice = request.POST.get("meal_off_choice")
        meal = dashboard.meal_status
        current_time = timezone.localtime().time()
        to_dt = time(current_time.hour, current_time.minute)

        
        if meal_off_choice == "None":
            current_status = meal.meal_off  # type: ignore
            print(current_status)
            if meal_status_on_time(meal_off_choice, current_time, current_status):
                meal.meal_off = meal_off_choice  # type: ignore
                meal.status = False  # type: ignore
                meal.save()  # type: ignore
                dashboard.save() # type: ignore
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Meal status toggled",
                    }
                )
            else: 
                print('Invalid Time to meal on')
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Invalid time for meal on",
                    }
                )
        elif is_valid_time(meal_off_choice, to_dt) and dashboard.flexibility > 0:
            meal.meal_off = meal_off_choice  # type: ignore
            meal.status = True  # type: ignore
            meal.save()  # type: ignore
            dashboard.toggle_flexibility()  # type: ignore
            remaining_flexibility = dashboard.flexibility
            used_flexibility = dashboard.flexibility_used
            dashboard.save()  # type: ignore
            return JsonResponse(
                {
                    "success": True,
                    "message": "Meal status toggled",
                    "remaining_flexibility": remaining_flexibility,
                    "used_flexibility": used_flexibility,
                }
            )
        elif dashboard.flexibility <= 0:
            return JsonResponse(
                {"success": False, "message": "Flexibility not available"}
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid time for meal off",
                }
            )


# def toggle_reduce_balance(request):
#     if request.method == 'POST':
#         user_id = request.POST.get('user_id')

#         # Ensure user_id is provided and valid
#         if user_id:
#             try:
#                 user_dashboard = Dashboard.objects.get(user_id=user_id)
#             except Dashboard.DoesNotExist:
#                 return JsonResponse({'success': False, 'error': 'Dashboard not found for the given user'})

#             # Toggle the reduce_balance field
#             user_dashboard.toggle_balance_reduction()

#             # Prepare data to send in the response
#             response_data = {
#                 'success': True,
#                 'reduce_balance': user_dashboard.reduce_balance,
#                 'flexibility': user_dashboard.flexibility,
#                 'flexibility_used': user_dashboard.flexibility_used,
#             }

#             return JsonResponse(response_data)

#         else:
#             return JsonResponse({'success': False, 'error': 'User ID not provided'})

#     else:
#         return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'})


@login_required
def upload_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        image_file = request.FILES["image"]

        dashboard_instance, created = Dashboard.objects.get_or_create(user=request.user)
        dashboard_instance.user = request.user
        # Check if the user already has a profile picture, delete it if exists
        if dashboard_instance.image:
            dashboard_instance.image.delete()
        dashboard_instance.image = image_file
        dashboard_instance.save()
        # messages.success(request, "Image updated successfully")
        return JsonResponse({"success": True}, status=200)
    else:
        return JsonResponse({"success": False}, status=400)


@login_required
def checkout(request):
    user = request.user
    context = {
        "users": user,
    }
    return render(request, "checkout.html", context)


def extract_number(text):
    match = re.search(r"\d+", text)
    if match:
        return int(match.group())
    return None


@login_required
@csrf_exempt
def save_payment_details(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            payment_processor = data.get("payment_processor")
            sender_number = data.get("sender_number")
            transaction_id = data.get("transaction_id")
            plan = data.get("planName")
            type = data.get("type")
            total_amount = data.get("totalAmount")
            total_amount_int = extract_number(total_amount)
            # print(total_amount_int)
            user = request.user
            dashboard = user.dashboard
            # Save payment details to the Payment model
            payment = Payment.objects.create(
                user=user,
                dashboard=dashboard,
                payment_method=payment_processor,
                sender_number=sender_number,
                transaction_id=transaction_id,
                plan=plan,
                type=type,
                total_amount=total_amount_int,
            )

            return JsonResponse({"message": "Payment details saved successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user
        if user.check_password(current_password) and new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully")
            return redirect("change_password")
        else:
            if not user.check_password(current_password):
                messages.error(request, "Invalid current password")
            elif new_password != confirm_password:
                messages.error(request, "New passwords do not match")
            return redirect("change_password")

    return render(request, "change-password.html")


def send_otp(phone_number, otp):
    api_key = settings.BULK_SMS_API_KEY
    sender_id = settings.BULK_SMS_SENDER_ID
    message = f"Your Cooking Station OTP for password reset: {otp}"
    url = f"http://bulksmsbd.net/api/smsapi?api_key=${api_key}&type=text&number={phone_number}&senderid={sender_id}&message={message}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True  # SMS sent successfully
        else:
            # Log or handle the error appropriately
            print(f"SMS API request failed with status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        # Log or handle the exception
        print(f"Error sending SMS: {e}")
        return False


def generate_otp(request):
    # Generate a pool of characters for the OTP
    otp_characters = string.digits  # Using digits 0-9 for OTP

    # Ensure uniqueness by combining random numbers and session data
    # Assuming 'user_id' is a unique identifier for the user
    user_id = request.session.get("user_id", "")
    # Extract last 5 digits of current timestamp
    timestamp = str(int(time.time()))[-5:]  # type: ignore
    unique_string = (
        user_id + timestamp + "".join(random.choice(otp_characters) for _ in range(6))
    )

    # Shuffle the characters to ensure randomness
    otp = "".join(random.sample(unique_string, 6))

    request.session["reset_otp"] = otp
    request.session.modified = True
    return otp


def forgot_password(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            phone_number = request.POST.get("phone_number")
            user = UserAccount.objects.filter(phone=phone_number).first()
            if user:
                otp = generate_otp(request)
                if send_otp(phone_number, otp):
                    request.session["reset_phone"] = phone_number
                    request.session["reset_flow"] = True
                    # Indicate reset process started
                    request.session["reset_started"] = True
                    return redirect("verify_otp")
                else:
                    messages.error(request, "Failed to send OTP. Please try again")
            else:
                messages.error(request, "User not found with this phone number")
        return render(request, "forgot-password.html")
    return redirect("change_password")


def verify_otp(request):
    if not request.user.is_authenticated:
        if not (
            request.session.get("reset_flow") and request.session.get("reset_started")
        ):
            return redirect("forgot_password")

        if request.method == "POST":
            entered_otp = request.POST.get("otp")
            saved_otp = request.session.get("reset_otp")
            if entered_otp == saved_otp:
                del request.session["reset_otp"]
                request.session["reset_verified"] = True
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False})

        return render(request, "verify-otp.html")
    return redirect("change_password")


def reset_password(request):
    if "reset_verified" not in request.session:
        return redirect("forgot_password")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        if new_password == confirm_password:
            user = UserAccount.objects.get(phone=request.session.get("reset_phone"))
            user.set_password(new_password)
            user.save()
            del request.session["reset_phone"]
            del request.session["reset_verified"]
            del request.session["reset_flow"]
            messages.success(request, "Password reset successfully")
            return redirect("login")
        else:
            messages.error(request, "Password do not match!")
            return redirect("reset_password")
    return render(request, "reset-password.html")


def chef_registration(request):
    if request.method == "POST":
        form = ChefRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Thank you for registering. We will contact you soon!"
            )
            return redirect("chef_registration")
    form = ChefRegistrationForm()
    return render(request, "chef-reg.html", {"form": form})


def event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Thank you for contacting us. We will reach out to you soon!"
            )
            return redirect("event")
    else:
        form = EventForm()
    return render(request, "event.html", {"form": form})


@login_required
def payment_confirmed(request):
    return render(request, "payment-success.html")


def bd_menu(request):
    return render(request, "BD-menu.html")


def uk_menu(request):
    return render(request, "UK-menu.html")


def terms(request):
    return render(request, "terms-condition.html")


def privacy(request):
    return render(request, "privacy.html")


def about(request):
    return render(request, "about.html")


@login_required
def feedback(request):
    if request.method == "POST":
        full_name = request.POST.get("fullName")
        email_or_phone = request.POST.get("emailOrPhone")
        complaint_reason = request.POST.get("complaintReason")
        complaint = request.POST.get("complaint")

        user_feedback = Feedback.objects.create(
            full_name=full_name,
            email_or_phone=email_or_phone,
            complaint_reason=complaint_reason,
            complaint=complaint,
        )
        messages.success(
            request, "Thanks for your feedback. We'll be in touch shortly!"
        )
        return redirect("feedback")

    return render(request, "feedback.html")
