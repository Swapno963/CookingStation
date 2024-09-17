from django_cron import CronJobBase, Schedule
from demolog.models import Dashboard, Payment, Package
from django.utils import timezone
import pytz



class ExpiredPaymentsCronJob(CronJobBase):
    RUN_EVERY_MINS = 720  # Every 12 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'demolog.switch_expired_payments_cron_job'

    def do(self):
        expired_payments = Payment.objects.filter(status='active')

        for payment in expired_payments:
            try:
                current_plan = Package.objects.get(
                    plan=int(payment.plan.split()[0]), 
                    type=payment.type
                )

                if payment.dashboard.balance < current_plan.per_meal:
                    print(f"Payment {payment.id} expired due to low balance.")
                    
                    payment.status = 'expired'
                    payment.save()

                    payment.dashboard.current_plan = None
                    payment.dashboard.reduce_balance = False
                    payment.dashboard.flexibility = 0
                    payment.dashboard.flexibility_used = 0 
                    payment.dashboard.save()

            except (Package.DoesNotExist, ValueError, IndexError) as e:
                print(f"Error processing payment ID {payment.id}: {e}")

        print("Expired payments check completed.")


class ReduceBalanceLunchCronJob(CronJobBase):
    RUN_AT_TIMES = ['09:00']  # Run at 9:00 AM

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'demolog.reduce_balance_lunch_cron_job'

    def do(self):

        now_utc = timezone.now()
        local_tz = pytz.timezone('Asia/Dhaka')
        now_local = now_utc.astimezone(local_tz)
        current_hour = now_local.hour
        
        if  current_hour <= 9:
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
            print("Balance successfully reduced by plan's meal rate for lunch.")
        
        
class ReduceBalanceDinnerCronJob(CronJobBase):
    RUN_AT_TIMES = ['14:30']  # Run at 2:30 PM

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'demolog.reduce_balance_dinner_cron_job'

    def do(self):
        now_utc = timezone.now()
        local_tz = pytz.timezone('Asia/Dhaka')
        now_local = now_utc.astimezone(local_tz)
        current_hour = now_local.hour

        if current_hour <= 14:
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
            print("Balance successfully reduced by plan's meal rate for dinner.") 
        
    


