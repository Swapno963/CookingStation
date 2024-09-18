from io import BytesIO
import pstats
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.db.models import Count, Q, F
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View

from django.contrib.auth.mixins import UserPassesTestMixin

from demolog.models import Dashboard, Package, UserAccount

from datetime import time

from demolog.views import dashboard

from blabel import LabelWriter
from django.conf import settings
from django.template.loader import render_to_string

from weasyprint import HTML
import os
import base64

# Create your views here.


class AdminDashboardView(UserPassesTestMixin, View):

    
    template_name = "adminDashboard.html"
 

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect("home")

    def get(self, request, *args, **kwargs):

        dashboards = Dashboard.objects.all()
        users = UserAccount.objects.all()
        total_registrations = users.filter(is_staff=False, is_superuser=False).count()
        # total_active_users = users.filter(
        #     is_active=True, is_staff=False, is_superuser=False
        # ).count()
        
        total_active_users = 0
        for user in dashboards:
            if user.current_plan:
                total_active_users += 1

        # print('Total users:', total_registrations)
        # print('Total active users:', total_active_users)

        total_regular_packages = (
            dashboards.filter(current_plan__type="Regular")
            .values("current_plan__plan")
            .annotate(count=Count("current_plan__plan"))
        )

        total_premium_packages = (
            dashboards.filter(current_plan__type="Premium")
            .values("current_plan__plan")
            .annotate(count=Count("current_plan__plan"))
        )

        total_regular_counts = 0
        total_premium_counts = 0
        # Example to check distinct values for debugging
        # Filter out dashboards where current_plan is not None
        for dashboard in dashboards:
            if dashboard.current_plan is not None:
                if dashboard.current_plan.type == 'Regular' and dashboard.meal_status.status == False:
                    total_regular_counts += 2
                elif dashboard.current_plan.type == 'Premium' and dashboard.meal_status.status == False:
                    total_premium_counts += 2
                else:
                    pass

        

        total_lunch_regular = total_regular_counts // 2
        total_dinner_regular = total_regular_counts // 2

        total_lunch_premium = total_premium_counts // 2
        total_dinner_premium = total_premium_counts // 2

        subscriber_stats = {
            "regular": {
                # 'lunch' : 0,
                # 'dinner' : 0,
                # 'total': 0
            },
            "premium": {
                # 'lunch' : 0,
                # 'dinner' : 0,
                # 'total': 0
            },
        }
        subscriber_stats_total = {"regular": 0, "premium": 0}

        for entry in total_regular_packages:
            subscriber_stats["regular"][entry["current_plan__plan"]] = entry["count"]
            subscriber_stats_total["regular"] += entry["count"]

        for entry in total_premium_packages:
            subscriber_stats["premium"][entry["current_plan__plan"]] = entry["count"]
            subscriber_stats_total["premium"] += entry["count"]

            # suscriber_stats['Premium']['lunch'] = total_lunch_premium
            # print(suscriber_stats['Premium'][entry['current_plan__plan']])

        context = {
            "total_registrations": total_registrations,
            "total_active_users": total_active_users,
            "total_lunch_regular": total_lunch_regular,
            "total_dinner_regular": total_dinner_regular,
            "total_lunch_premium": total_lunch_premium,
            "total_dinner_premium": total_dinner_premium,
            "subscriber_stats": subscriber_stats,
            "subscriber_stats_total": subscriber_stats_total,
            # 'total_regular_counts' : total_regular_counts,
            # 'total_premium_counts' : total_premium_counts,
        }

        # print(context)

        return render(request, self.template_name, context)


class DailyMeals(UserPassesTestMixin, View):

    template_name = "dailyMeals.html"
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser 

    def handle_no_permission(self):
        return redirect("home")
    
    
    users_list = UserAccount.objects.filter(
        Q(is_active=True)
        & Q(is_staff=False)
        & Q(is_superuser=False)
        & Q(payments__status="active")
    ).annotate(plan_type=F("dashboard__current_plan__type"), service_id=F("dashboard__service_id"))

    def get(self, request):

        # Fetch data from the database

        current_time = timezone.localtime().time()
        current_dt = time(current_time.hour, current_time.minute)

        context = {
            "lunch": False,
            "dinner": False,
            "todays_lunch_list": [],
            "todays_dinner_list": [],
        }

        if current_dt >= time(9, 1):
            context["todays_lunch_list"] = self.users_list.filter(
                Q(dashboard__meal_status__meal_off="None")
                | Q(dashboard__meal_status__meal_off="Dinner")
                & Q(dashboard__balance__gte=F("dashboard__current_plan__per_meal"))
            )

            # print()
            # print("lunch:", context["todays_lunch_list"])
            # print()

            context["lunch"] = True
        if current_dt >= time(15, 1):
            context["todays_dinner_list"] = self.users_list.filter(
                Q(dashboard__meal_status__meal_off="None")
                | Q(dashboard__meal_status__meal_off="Lunch")
                & Q(dashboard__balance__gte=F("dashboard__current_plan__per_meal"))
            )
            # print()
            # print("dinner:", context["todays_dinner_list"])
            # print()
            context["dinner"] = True

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        meal_type = request.POST.get("meal_type")
        current_date = timezone.now().date()

        if meal_type == "lunch":
            meal_list = self.users_list.filter(
                Q(dashboard__meal_status__meal_off="None")
                | Q(dashboard__meal_status__meal_off="Dinner")
                & Q(dashboard__balance__gte=F("dashboard__current_plan__per_meal"))
            )
        elif meal_type == "dinner":
            meal_list = self.users_list.filter(
                Q(dashboard__meal_status__meal_off="None")
                | Q(dashboard__meal_status__meal_off="Lunch")
                & Q(dashboard__balance__gte=F("dashboard__current_plan__per_meal"))
            )

        else:
            return HttpResponse("Invalid meal type", status=400)

        data = [
            {
                "name": user.name,
                "service_id": user.service_id, # type: ignore
                "plan": user.plan_type,  # type: ignore
                "address": user.address,
            }
            for user in meal_list
        ]

        logo_path = os.path.join(settings.STATICFILES_DIRS[1], "assets/img/cs-logo.jpg")

        with open(logo_path, "rb") as logo_file:
            logo_base64 = base64.b64encode(logo_file.read()).decode("utf-8")

        css_path = os.path.join(settings.STATICFILES_DIRS[1], "assets/css/label.css")

        html_string = render_to_string(
            "label.html",
            {"users": data, "logo_base64": logo_base64, "css_path": css_path},
        )
        buffer = BytesIO()
        HTML(string=html_string).write_pdf(buffer, stylesheets=[css_path])

        # Set the response headers
        buffer.seek(0)
        response = HttpResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{current_date}_{meal_type}_labels.pdf"'
        )
        return response
