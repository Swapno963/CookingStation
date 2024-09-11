from math import pi
from django.test import TestCase
from django.urls import reverse
from .models import *
from freezegun import freeze_time
from django.utils import timezone

# # Create your tests here.
# def test_registration_redirects_to_dashboard_if_authenticated(self):
#     # Create a user and login
#     user = UserAccount.objects.create_user(phone='01683152495', password='testpassword')
#     self.client.force_login(user)

#     # Make a POST request to the registration view
#     response = self.client.post(reverse('registration'))

#     # Assert that the response redirects to the dashboard
#     self.assertRedirects(response, reverse('dashboard'))


# def test_registration_renders_form_if_not_authenticated(self):
#     # Make a GET request to the registration view
#     response = self.client.get(reverse('registration'))

#     # Assert that the response renders the registration form
#     self.assertTemplateUsed(response, 'customer-reg.html')
#     self.assertContains(response, '<form')

import json
from django.test import TestCase, Client
from demolog.models import MealOff, Dashboard, UserAccount
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time


class ToggleMealStateTestCase(TestCase):

    def setUp(self):
        # Set up initial data

        self.client = Client()

        self.user = UserAccount.objects.create_user(  # type: ignore
            phone='01123456789',
            name='Test User',
            password='password',
            country='Bangladesh',
            city='Dhaka',
            address='Test Address',
            you_are='Student'
        )

        self.package = Package.objects.create(
            plan=3,
            type='Regular',
            per_meal=100
        )

        # self.meal_off_1 = MealOff.objects.create()
        # self.meal_off_2 = MealOff.objects.create()
        # self.meal_off_3 = MealOff.objects.create()

        self.dashboard = Dashboard.objects.get(
            user=self.user,
        )
        self.dashboard.service_id = self.user.phone[1:]
        self.dashboard.current_plan = self.package
        self.dashboard.balance = 1000
        self.dashboard.flexibility = 10
        # self.dashboard.meal_status = self.meal_off_1
        self.dashboard.save()
        self.client.login(phone='01123456789', password='password')

        # self.package_2 = Package.objects.create(
        #     plan=7,
        #     type='Premium',
        #     per_meal=200
        # )

        # self.package_3 = Package.objects.create(
        #     plan=15,
        #     type='Premium',
        #     per_meal=300
        # )
    @freeze_time("2024-06-28 08:30:00")
    def test_toggle_meal_state_valid_time(self):
        response = self.client.post(reverse('toggle_meal_state'), {
            'user_id': self.user.id,
            'meal_off_choice': 'Lunch'
        })
        # curr_time = timezone.now().time()
        # print(curr_time)
        self.dashboard.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Meal status toggled')
        self.assertEqual(self.dashboard.meal_status.meal_off, 'Lunch')
        self.assertTrue(self.dashboard.meal_status.status)
    
    @freeze_time("2024-06-28 15:00:00")
    def test_toggle_meal_state_invalid_time(self):
        response = self.client.post(reverse('toggle_meal_state'), {
            'user_id': self.user.id,
            'meal_off_choice': 'Lunch'
        })
        self.dashboard.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertEqual(
            response.json()['message'], 'Invalid time for meal off')

    # def test_toggle_meal_state_no_user_id(self):
    #     response = self.client.post(reverse('toggle_meal_state'), {
    #         'meal_off_choice': 'Lunch'
    #     })
    #     self.assertEqual(response.status_code, 400)

    # def test_toggle_meal_state_invalid_user_id(self):
    #     response = self.client.post(reverse('toggle_meal_state'), {
    #         'user_id': 9999,
    #         'meal_off_choice': 'Lunch'
    #     })
    #     self.assertEqual(response.status_code, 404)

    # def test_toggle_meal_state_get_request(self):
    #     response = self.client.get(reverse('toggle_meal_state'))
    #     self.assertEqual(response.status_code, 405)

    # @freeze_time("2024-07-04 07:00:00")
    # def test_toggle_meal_state_lunch(self):
    #     url = reverse('toggle_meal_state')
    #     data = {
    #         'user_id': self.user.id,
    #         'meal_off_choice': 'Lunch'
    #     }

    #     print('----------------------------------------------------------------')
    #     # Simulate a POST request within the valid time frame for lunch
    #     print("time:", timezone.localtime().time())
    #     print('----------------------------------------------------------------')

    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertJSONEqual(response.content, {  # type: ignore
    #         'success': True, 'message': 'Meal status toggled'})

    #     # Check if meal status and reduce_balance are updated
    #     self.dashboard.refresh_from_db()
    #     self.assertEqual(self.dashboard.meal_status.meal_off, 'Lunch')
    #     self.assertTrue(self.dashboard.meal_status.status)
    #     self.assertFalse(self.dashboard.reduce_balance)

    # @freeze_time("2024-07-04 10:00:00")
    # def test_toggle_meal_state_invalid_time(self):
    #     url = reverse('toggle_meal_state')
    #     data = {
    #         'user_id': self.user.id,
    #         'meal_off_choice': 'Lunch'
    #     }

    #     # Simulate a POST request outside the valid time frame for lunch
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertJSONEqual(response.content, {  # type: ignore
    #         'success': False, 'message': 'Invalid time for meal off'})

    #     # Check if meal status and reduce_balance are not updated
    #     self.dashboard.refresh_from_db()
    #     self.assertEqual(self.dashboard.meal_status.meal_off, 'None')
    #     self.assertFalse(self.dashboard.meal_status.status)
    #     self.assertTrue(self.dashboard.reduce_balance)


# class PaymentProcessorTestCase(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = UserAccount.objects.create_user(username='testuser', password='testpassword') # type: ignore
#         # self.dashboard = Dashboard.objects.create(user=self.user)

#     def test_save_payment_details_with_valid_data(self):
#         data = {
#             "payment_processor": "PayPal",
#             "sender_number": "1234567890",
#             "transaction_id": "123456789012345678901234567890",
#             "planName": "7 Days",
#             "type": "Regular",
#             "totalAmount": 100
#         }
#         response = self.client.post('/save-payment-details/', json.dumps(data), content_type='application/json')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(Payment.objects.count(), 1)
#         payment = Payment.objects.first()
#         self.assertEqual(payment.payment_method, "PayPal")
#         self.assertEqual(payment.sender_number, "1234567890")
#         self.assertEqual(payment.transaction_id, "123456789012345678901234567890")
#         self.assertEqual(payment.plan, "7 Days")
#         self.assertEqual(payment.type, "Regular")
#         self.assertEqual(payment.total_amount, 100)

#     def test_save_payment_details_with_invalid_data(self):
#         data = {
#             "payment_processor": "",
#             "sender_number": "",
#             "transaction_id": "",
#             "planName": "",
#             "type": "",
#             "totalAmount": ""
#         }
#         response = self.client.post('/save-payment-details/', json.dumps(data), content_type='application/json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(Payment.objects.count(), 0)

#     def test_save_payment_details_with_invalid_payment_processor(self):
#         data = {
#             "payment_processor": "Invalid",
#             "sender_number": "1234567890",
#             "transaction_id": "123456789012345678901234567890",
#             "planName": "Monthly",
#             "type": "Regular",
#             "totalAmount": 100
#         }
#         response = self.client.post('/save-payment-details/', json.dumps(data), content_type='application/json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(Payment.objects.count(), 0)

#     def test_save_payment_details_with_invalid_sender_number(self):
#         data = {
#             "payment_processor": "PayPal",
#             "sender_number": "",
#             "transaction_id": "123456789012345678901234567890",
#             "planName": "3 Days",
#             "type": "Regular",
#             "totalAmount": 100
#         }
#         response = self.client.post('/save-payment-details/', json.dumps(data), content_type='application/json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(Payment.objects.count(), 0)

#     def test_save_payment_details_with_invalid_transaction_id(self):
#         data = {
#             "payment_processor": "PayPal",
#             "sender_number": "1234567890",
#             "transaction_id": "",
#             "planName": "3 Days",
#             "type": "Regular",
#             "totalAmount": 100
#         }
#         response = self.client.post('/save-payment-details/', json.dumps(data), content_type='application/json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(Payment.objects.count(), 0)
