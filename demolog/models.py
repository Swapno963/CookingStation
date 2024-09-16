from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.core.exceptions import ValidationError
# from django.core.management import call_command

# CustomManager
class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone Number field must be set')
        extra_fields.setdefault('members', 0)
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone, password, **extra_fields)


class UserAccount(AbstractBaseUser):
    YOU_ARE_CHOICES = (
        ('', 'You are'),
        ('Family', 'Family'),
        ('Bachelor', 'Bachelor'),
        ('Student', 'Student'),
        ('official', 'official'),
    )

    COUNTRY_CHOICES = (
        ('', 'Choose Country'),
        ('Bangladesh', 'Bangladesh'),
        ('United Kingdom', 'United Kingdom')
    )

    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=30, choices=COUNTRY_CHOICES)
    city = models.CharField(max_length=30)
    address = models.CharField(max_length=150)
    you_are = models.CharField(max_length=20, choices=YOU_ARE_CHOICES)
    members = models.CharField(max_length=55, null=True, blank=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_agreed = models.BooleanField(default=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def save(self, *args, **kwargs):
        # Creating a dashboard for registerd user
        created = not self.pk  # Check if the user is being created for the first time
        super().save(*args, **kwargs)
        # call_command('generate_data')

        if created and not self.is_superuser:
            Dashboard.objects.create(
                user=self,
                name=self.name,
                phone=self.phone
            )


class Package(models.Model):
    DURATION_CHOICES = (
        (3, '3 Days'),
        (7, '7 Days'),
        (15, '15 Days'),
        (30, '30 Days'),
    )

    TYPE_CHOICES = (
        ('Regular', 'Regular'),
        ('Premium', 'Premium'),
    )

    plan = models.IntegerField(choices=DURATION_CHOICES)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    per_meal = models.IntegerField()

    @property
    def total_amount(self):
        # numeric_part = int(''.join(filter(str.isdigit, self.plan)))
        return self.per_meal * self.plan * 2

    def total_meals(self):
        # numeric_part = int(''.join(filter(str.isdigit, self.plan)))
        return self.plan * 2 

    def __str__(self):
        return f"{self.get_plan_display()}"  # type: ignore


# def validate_image_size(value):
#     max_size = 1 * 1024 * 1024  # 1 MB
#     print("Image size:", value.size)
#     if value.size > max_size:
#         raise ValidationError("The maximum file size allowed is 1 MB")


class MealOff(models.Model):

    TOGGLE_CHOICES = (
        ('None', 'None'),
        ('Both', 'Both'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
    )
    STATUS_CHOICES = (
        (True, 'OFF'),
        (False, 'ON'),
    )

    meal_off = models.CharField(
        max_length=20, choices=TOGGLE_CHOICES, default='None')
    status = models.BooleanField(default=False, choices=STATUS_CHOICES)
    updated_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class Dashboard(models.Model):
    ACTIVE_CHOICES = (
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('red', 'Red')
    )

    user = models.OneToOneField(
        UserAccount, related_name='dashboard', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15, unique=True)
    service_id = models.CharField(max_length=10, unique=True)
    current_plan = models.ForeignKey(
        Package, on_delete=models.CASCADE, null=True, blank=True)
    balance = models.IntegerField(default=0)
    image = models.ImageField(
        upload_to='uploads/profile', null=True, blank=True)
    meal_status = models.OneToOneField(
        MealOff, related_name='dashboard', on_delete=models.CASCADE, null=True, blank=True)
    flexibility = models.IntegerField(default=0)
    flexibility_used = models.IntegerField(default=0)
    reduce_balance = models.BooleanField(
        default=True, help_text="Uncheck to stop balance reduction of this user")

    def save(self, *args, **kwargs):
        # Check if the instance is being created (not yet saved)
        if not self.pk:
            if len(self.phone) > 10:
                last_10_digit = self.phone[-10:]
            else:
                last_10_digit = self.phone
            self.service_id = last_10_digit

        if not self.meal_status:
            meal_off = MealOff.objects.create()
            self.meal_status = meal_off
        elif self.meal_status and self.meal_status.status == True:
            self.reduce_balance = False
        elif self.meal_status == 'None' and self.meal_status.status == False:
            self.reduce_balance = True
        super().save(*args, **kwargs)

    @property
    def active(self):

        current_plan_per_meal = self.current_plan.per_meal
        if self.balance > current_plan_per_meal * 3:
            return 'green'
        elif self.balance > current_plan_per_meal:
            return 'yellow'
        else:
            return ' red'

    def toggle_flexibility(self):
        if not self.reduce_balance:
            # Check if there is remaining flexibility
            if self.flexibility > 0:
                self.flexibility -= 1
                self.flexibility_used += 1  # Increase flexibility_used by 1

        self.save()

    def __str__(self):
        return self.phone


class Payment(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
    )

    user = models.ForeignKey(
        UserAccount, related_name='payments', on_delete=models.PROTECT)
    dashboard = models.ForeignKey(
        Dashboard, related_name='payments', on_delete=models.PROTECT)
    payment_method = models.CharField(max_length=10)
    sender_number = models.CharField(max_length=15)
    transaction_id = models.CharField(max_length=30)
    plan = models.CharField(max_length=100) 
    type = models.CharField(max_length=20, blank=True, null=True)
    total_amount = models.IntegerField(default=0)
    started_date = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='active', null=True, blank=True)
    confirmed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:  # type: ignore
            # If this is a new instance, set started_date to the current time
            self.started_date = timezone.now()
            # self.expire_date = self.started_date + timezone.timedelta(days=self.plan)
            if self.plan == '3 Days':
                self.expire_date = self.started_date + \
                    timezone.timedelta(days=3)
            elif self.plan == '7 Days':
                self.expire_date = self.started_date + \
                    timezone.timedelta(days=7)
            elif self.plan == '15 Days':
                self.expire_date = self.started_date + \
                    timezone.timedelta(days=15)
            elif self.plan == '30 Days':
                self.expire_date = self.started_date + \
                    timezone.timedelta(days=30)

        if not self.id:  # type: ignore # If it's a new instance
            # Check if the user already has an active plan
            active_plan_exists = self.dashboard.current_plan
            if active_plan_exists != None and not self.user.is_staff:
                raise ValueError('You already have an active plan. Please wait until it expire')
           
        super().save(*args, **kwargs)
        
        if self.confirmed and self.status == 'active':
            try:
                req_plan = Package.objects.get(plan=int(self.plan.split()[0]), type=self.type)
                self.dashboard.current_plan = req_plan
                self.dashboard.balance += self.total_amount 
                self.dashboard.reduce_balance = True
                self.dashboard.save() 
            except Package.DoesNotExist:
                raise ValueError("The specified package does not exist")

       
                
            
            
    def __str__(self):
        return f"Payment - User: {self.user}, Method: {self.payment_method}, Transaction ID: {self.transaction_id}"


class Event(models.Model):
    COUNTRY = (
        ('', 'Choose'),
        ('Bangladesh', 'Bangladesh'),
        ('United Kingdom', 'United Kingdom')
    )
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50, null=True, blank=True)
    date_and_time = models.DateTimeField(auto_now=False)
    country = models.CharField(max_length=30, choices=COUNTRY)
    address = models.CharField(max_length=250)
    people = models.CharField(max_length=5)
    message = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.phone


class ChefRegistraton(models.Model):
    COUNTRY_CHOICES = (
        ('', 'Choose'),
        ('Bangladesh', 'Bangladesh'),
        ('United Kingdom', 'United Kingdom')
    )
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    Email = models.EmailField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=30, choices=COUNTRY_CHOICES)
    city = models.CharField(max_length=30)
    Address = models.CharField(max_length=50)
    people_you_can_serve = models.CharField(max_length=5)

    def __str__(self):
        return self.name


class Feedback(models.Model):
    full_name = models.CharField(max_length=50)
    email_or_phone = models.CharField(max_length=50)
    complaint_reason = models.CharField(max_length=100)
    complaint = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
