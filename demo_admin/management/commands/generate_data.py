import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from demolog.models import UserAccount, Package, Dashboard
from datetime import datetime, timedelta
from django.utils import timezone
from operator import *
import uuid

fake = Faker()
operators = [add, sub, mul]


def generate_random_number(length):
    if length < 1:
        raise ValueError("Length must be at least 1")
    start = 10 ** (length - 1)
    end = 10**length - 1
    return random.randint(start, end)


def random_city(country):
    cities_of_bangladesh = [
        "Dhaka",
        "Chittagong",
        "Khulna",
        "Rajshahi",
        "Sylhet",
        "Barisal",
        "Rangpur",
        "Mymensingh",
        "Comilla",
        "Narayanganj",
        "Gazipur",
        "Jessore",
        "Cox's Bazar",
        "Nawabganj",
        "Bogura",
        "Saidpur",
        "Feni",
        "Kushtia",
        "Satkhira",
        "Tangail",
    ]
    if country == "Bangladesh":
        return random.choice(cities_of_bangladesh)


class Command(BaseCommand):
    help = "Generate fake data for testing"

    def handle(self, *args, **options):
        # self.create_users()
        self.create_subscriptions()
        self.create_packages()
        # self.create_payments()
        # self.create_events()
        # self.create_chef_registrations()
        # self.create_feedback()
        # self.create_dashboard()

    def create_users(self):
        code = [4, 5, 6, 7, 8, 9]
        for i in range(100):

            number = generate_random_number(9)

            UserAccount.objects.create(
                name=fake.first_name() + " " + fake.last_name(),
                phone=f"01{random.choice(code)}{number}",
                email=f"{fake.first_name()}.{fake.last_name()}@{fake.free_email_domain()}",
                country="Bangladesh",
                city=random_city("Bangladesh"),
                address=fake.address(),
                you_are=random.choice(["Bachelor", "Student", "official"]),
                is_active=random.choice([True, False]),
            )

        self.stdout.write(self.style.SUCCESS("Users created"))

    def create_packages(self):

        durations = [3, 7, 15, 30]

        for i in range(4):
            Package.objects.create(
                plan=durations[i], type="Regular", per_meal=random.randrange(25, 40)
            )

        for i in range(4):
            Package.objects.create(
                plan=durations[i], type="Premium", per_meal=random.randrange(50, 75)
            )

        self.stdout.write(self.style.SUCCESS("Packages created"))

    def create_subscriptions(self):

        users = UserAccount.objects.all()
        packages = Package.objects.all()

        for user in users:
            dashboard, created = Dashboard.objects.get_or_create(
                name=user.name,
                phone=user.phone,
            )

            dashboard.service_id = user.phone[2:]
            dashboard.current_plan = random.choice(list(packages))
            dashboard.balance = random.randrange(0, 500)
            dashboard.reduce_balance = random.choice([True, False])
            dashboard.flexibility = random.randrange(0, 10)

            dashboard.save()

        self.stdout.write(self.style.SUCCESS("Dashboard udpated"))
