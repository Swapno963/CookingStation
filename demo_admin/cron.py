from django.utils import timezone
from django.db.models import Q, F
from django.db import transaction
from demolog.models import UserAccount, Dashboard, Payment
from datetime import time
from django.db.models.functions import Least


# def reset_flexibility():
#     dashboards = Dashboard.objects.filter(balance__lte=0)
#     dashboards.update(flexibility=0, flexibility_used=0)
def payment_expiration():
    expired_payments = Payment.objects.filter(Q(status='active') & Q(expire_date__lte=timezone.localtime()))
    expired_payments.update(status='expired')

def reduce_balance():

    dashboards = Dashboard.objects.filter(
        Q(reduce_balance=True)
        & Q(current_plan__isnull=False)
        & Q(balance__gte=F("current_plan__per_meal"))
    )
    with transaction.atomic():
        for dashboard in dashboards:
            min_value = min(dashboard.current_plan.per_meal, dashboard.balance) # type: ignore
            dashboard.balance -= min_value
            dashboard.save()


    dashboard_no_balance = Dashboard.objects.filter(
        Q(current_plan__isnull=False) & Q(balance__lte=0)
    )
    dashboard_no_balance.update(flexibility=0, flexibility_used=0, current_plan=None)


def update_meals():
    current_time = timezone.localtime().time()
    current_dt = time(current_time.hour, current_time.minute)
    dashboard = Dashboard.objects.all()
    # print(current_dt)

    if current_dt >= time(9, 1):
        payment_expiration()
        todays_lunch_list = UserAccount.objects.filter(
            Q(dashboard__meal_status__meal_off="None")
            | Q(dashboard__meal_status__meal_off="Dinner")
            & Q(dashboard__balance__gte=F("dashboard__current_plan__per_meal"))
        )
        dashboard.filter(Q(meal_status__meal_off="Dinner") & Q(reduce_balance=False))
        dashboard.update(reduce_balance=True)
        reduce_balance()
        dashboard.update(reduce_balance=False)

    if current_dt >= time(15, 1):
        todays_dinner_list = UserAccount.objects.filter(
            Q(dashboard__meal_status__meal_off="None")
            | Q(dashboard__meal_status__meal_off="Lunch")
            & Q(dashboard__balance__gte=F("dashboard__current_plan__per_meal"))
        )
        dashboard.filter(Q(meal_status__meal_off="Lunch") & Q(reduce_balance=False))
        dashboard.update(reduce_balance=True)
        reduce_balance()
        dashboard.update(reduce_balance=False)
