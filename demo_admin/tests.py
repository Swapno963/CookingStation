from os import name
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from demolog.models import Dashboard, UserAccount, Package, MealOff
from django.utils import timezone
from .views import DailyMeals
from freezegun import freeze_time
# class AdminDashboardViewTest(TestCase):
#     def setUp(self):
#         # Create packages
#         regular_package = Package.objects.create(
#             plan=7, type='Regular', per_meal=20)
#         premium_package = Package.objects.create(
#             plan=7, type='Premium', per_meal=30)

#         # Create users
#         user_1 = UserAccount.objects.create(
#             name="User1", phone="1234567890", country='Bangladesh', city='Dhaka', address='Mirpur', you_are='Student', is_active=True
#         )
#         self.user_2 = UserAccount.objects.create(
#             name="User2", phone="0987654321", country='Bangladesh', city='Barishal', address='Chormonai', you_are='Bachelor', is_active=False
#         )

#         # Create dashboards
#         dashboards_1 = Dashboard.objects.get(name='User1')
#         dashboards_1.current_plan = regular_package
#         dashboards_1.balance = 100
#         dashboards_1.save()

#         dashboards_2 = Dashboard.objects.get(name='User2')
#         dashboards_2.current_plan = premium_package
#         dashboards_2.balance = 50
#         dashboards_2.save()

#         self.client = Client()

#     def test_daily_meals_view(self):
#         response = self.client.get(reverse('daily_meals'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'adminDashboard.html')

#         # Check context data
#         self.assertEqual(response.context['total_registrations'], 2)
#         self.assertEqual(response.context['total_active_users'], 1)
#         self.assertEqual(response.context['total_regular_counts'], 1)
#         self.assertEqual(response.context['total_premium_counts'], 1)

#         suscriber_stats = response.context['subscriber_stats']
#         self.assertIn('regular', suscriber_stats)
#         self.assertIn('premium', suscriber_stats)
#         self.assertEqual(suscriber_stats['regular'][7], 1)
#         self.assertEqual(suscriber_stats['premium'][7], 1)

class DailyMealsViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user_1 = UserAccount.objects.create(
            name="User1", phone="01234567890", country='Bangladesh', city='Dhaka', address='Mirpur', you_are='Student', is_active=True
        )
        self.user_2 = UserAccount.objects.create(
            name="User2", phone="01987654321", country='Bangladesh', city='Barishal', address='Chormonai', you_are='Bachelor', is_active=True
        )
        
        self.user_3 = UserAccount.objects.create(
            name="User3", phone="01187654321", country='Bangladesh', city='Chandpur', address='Motlob', you_are='Office', is_active=True
        )

        regular_package = Package.objects.create(
            plan=7, type='Regular', per_meal=20)
        
        premium_package_1 = Package.objects.create(
            plan=7, type='Premium', per_meal=30)

        premium_package_2 = Package.objects.create(
            plan=15, type='Premium', per_meal=50)

        dashboards_1 = Dashboard.objects.get(name='User1')
        dashboards_1.current_plan = regular_package
        dashboards_1.balance = 1000
        meal_off_1 = dashboards_1.meal_status
        meal_off_1.meal_off = 'Dinner' # type: ignore
        meal_off_1.status = True
        meal_off_1.save()
        dashboards_1.save()

        dashboards_2 = Dashboard.objects.get(name='User2')
        dashboards_2.current_plan = premium_package_1
        dashboards_2.balance = 1500
        meal_off_2 = dashboards_2.meal_status
        meal_off_2.meal_off = 'Lunch' # type: ignore
        meal_off_2.status = True
        meal_off_2.save()
        dashboards_2.save()

        dashboards_3 = Dashboard.objects.get(name='User3')
        dashboards_3.current_plan = premium_package_2
        dashboards_3.balance = 1500
        meal_off_3 = dashboards_3.meal_status
        meal_off_3.meal_off = 'None' # type: ignore
        meal_off_3.status = False
        meal_off_3.save()
        dashboards_3.save()

    # @patch('demolog.views.timezone.localtime')
    # def test_template_rendered(self):
    #     request = self.factory.get('/dashboard/daily_meals/')
    #     response = self.view(request)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'dailyMeals.html')

    # def test_lunch_list(self):
    #     # Simulate a GET request to the view at lunch time
    #     with timezone.override(timezone.now().replace(hour=10, minute=0)):
    #         response = self.client.get(reverse('daily_meals'))  # Adjust the URL name accordingly

    #         self.assertEqual(response.status_code, 200)
    #         self.assertTrue(response.context['lunch'])
    #         self.assertIn(self.user_1, response.context['todays_lunch_list'])
    #         self.assertIn(self.user_2, response.context['todays_lunch_list'])

    # def test_dinner_list(self):
    #     # Simulate a GET request to the view at dinner time
    #     with timezone.override(timezone.localtime().replace(hour=15, minute=0)):
    #         response = self.client.get(reverse('daily_meals'))  # Adjust the URL name accordingly

    #         self.assertEqual(response.status_code, 200)
    #         self.assertTrue(response.context['dinner'])
    #         self.assertIn(self.user_1, response.context['todays_dinner_list'])
    #         self.assertNotIn(self.user_2, response.context['todays_dinner_list'])  # User 2 has dinner off

    @freeze_time("2024-06-28 09:00:00")
    def test_context_keys(self):
        response = self.client.get(reverse('daily_meals'))

        self.assertIn('lunch', response.context)
        self.assertIn('dinner', response.context)
        self.assertIn('todays_lunch_list', response.context)
        self.assertIn('todays_dinner_list', response.context)

    @freeze_time("2024-06-28 08:00:00")
    def test_context_values_before_lunch(self):
        response = self.client.get(reverse('daily_meals'))

        self.assertFalse(response.context['lunch'])
        self.assertFalse(response.context['dinner'])
        self.assertEqual(len(response.context['todays_lunch_list']), 0)
        self.assertEqual(len(response.context['todays_dinner_list']), 0)

    @freeze_time("2024-06-28 10:00:00")
    def test_context_values_during_lunch(self):
        response = self.client.get(reverse('daily_meals'))

        self.assertTrue(response.context['lunch'])
        self.assertFalse(response.context['dinner'])
        self.assertEqual(len(response.context['todays_lunch_list']), 2)
        self.assertEqual(len(response.context['todays_dinner_list']), 0)

    @freeze_time("2024-06-28 15:00:00")
    def test_context_values_during_dinner(self):
        response = self.client.get(reverse('daily_meals'))

        self.assertTrue(response.context['lunch'])
        self.assertTrue(response.context['dinner'])
        self.assertEqual(len(response.context['todays_lunch_list']), 2)
        self.assertEqual(len(response.context['todays_dinner_list']), 2)