from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Dashboard, MealOff
from django.utils import timezone

# @receiver(post_save, sender=Dashboard)
# def create_meal_off(sender, instance, created, **kwargs):
#     if created:
#         MealOff.objects.create(
#             meal_off='None',
#             status=False,
#         )

