from django.urls import path
from . import views

urlpatterns = [
    path("dashboard", views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path("dashboard/daily_meals", views.DailyMeals.as_view(), name="daily_meals"),
]
