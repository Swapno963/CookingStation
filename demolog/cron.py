from django_cron import CronJobBase, Schedule
from demolog.models import Dashboard, Payment
from django.utils import timezone


class ReduceBalanceCronJob(CronJobBase):
    RUN_EVERY_MINS = 720  # Every 12 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'demolog.reduce_balance_cron_job'

    def do(self):
        dashboards = Dashboard.objects.filter(reduce_balance=True)
        for dashboard in dashboards:
            if dashboard.current_plan and dashboard.balance > 0:
                per_meal = dashboard.current_plan.per_meal
                if per_meal is not None:
                    reduce_amount = min(dashboard.balance, per_meal)
                    dashboard.balance -= reduce_amount
                    if dashboard.balance == 0:
                        dashboard.current_plan = None
                    dashboard.save()
        print("Balance successfully reduced by plan's meal rate")

class ExpiredPaymentsCronJob(CronJobBase):
    RUN_EVERY_MINS = 720  # Every 12 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'demolog.switch_expired_payments_cron_job'

    def do(self):
        expired_payments = Payment.objects.filter(status='active', expire_date__lte=timezone.localtime())
        expired_payments.update(status='expired')
        print("Expired payments updated.")

class ResetFlexibilityCronJob(CronJobBase):
    RUN_EVERY_MINS = 720  # Every 12 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'demolog.reset_flexibility_cron_job'

    def do(self):
        dashboards = Dashboard.objects.all()
        for dashboard in dashboards:
            if dashboard.balance == 0:
                dashboard.flexibility = 0
                dashboard.flexibility_used = 0
                dashboard.save()
        print("Flexibility reset successfully.")
