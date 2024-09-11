from math import e
from django.core.management.base import BaseCommand
from demolog.models import Dashboard, Payment
from django.utils import timezone
import schedule
import time


class Command(BaseCommand):
    help = 'Switch active status to expired for payments with expired expire_date and run balance reduction'

    def handle(self, *args, **options):
        pass
        # def switch_expired_payments():
        #     expired_payments = Payment.objects.filter(status='active', expire_date__lte=timezone.localtime())
        #     expired_payments.update(status='expired')
            
            

        #     self.stdout.write(self.style.SUCCESS('Successfully updated expired payments.'))

        # Define the task to reduce balance
        # def reduce_balance():
        #     dashboards = Dashboard.objects.filter(reduce_balance=True)
        #     for dashboard in dashboards:
        #         if dashboard.current_plan and dashboard.balance > 0:
        #             per_meal = dashboard.current_plan.per_meal
        #             if per_meal is not None:
        #                 reduce_amount = min(dashboard.balance, per_meal)
        #                 dashboard.balance -= reduce_amount
        #                 if dashboard.balance == 0:
        #                     dashboard.current_plan = None
        #                 dashboard.save()

        #             self.stdout.write(self.style.SUCCESS("Balance successfully reduced by plan's meal rate"))
                    
        # def reset_flexibility():
        #     dashboards = Dashboard.objects.all()
        #     for dashboard in dashboards:
        #         if dashboard.balance == 0:
        #             dashboard.flexibility = 0
        #             dashboard.flexibility_used = 0
        #             dashboard.save()
        #         self.stdout.write(self.style.SUCCESS("Flexibility reset successfully"))

        # schedule.every(12).hours.do(reduce_balance)
        # schedule.every(12).hours.do(switch_expired_payments)
        # schedule.every(12).hours.do(reset_flexibility)

        # while True:
        #     schedule.run_pending()
        #     time.sleep(1)