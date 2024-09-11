from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('accounts/login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.registration, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/toggle_meal_state/', views.toggle_meal_state, name='toggle_meal_state'), # type: ignore
    path('upload_image/', views.upload_image, name='upload_image'),
    path('dashboard/checkout/', views.checkout, name='checkout'),
    path('save-payment-details/', views.save_payment_details, name='save_payment_details'), # type: ignore
    path('dashboard/checkout/payment_confirmed/', views.payment_confirmed, name='payment_confirmed'),
    path('change_password', views.change_password, name='change_password'),
    path('about/', views.about, name='about'),
    path('bd_menu/', views.bd_menu, name='bd_menu'),
    path('uk_menu/', views.uk_menu, name='uk_menu'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('event/', views.event, name='event'),
    path('chef_registration/', views.chef_registration, name='chef_registration'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
    # path('toggle_reduce_balance/', views.toggle_reduce_balance, name='toggle_reduce_balance'),
    path('feedback/', views.feedback, name='feedback'),
]
