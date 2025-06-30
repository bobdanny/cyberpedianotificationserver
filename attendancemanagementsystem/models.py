from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from django.db import models
from django.utils import timezone
import uuid

DEPARTMENT_CHOICES = [
    ('cs', 'Computer Science'),
    ('mc', 'Mass Communication'),
    ('journalism', 'Journalism'),
    ('eee', 'Electrical Electronics Engineering'),
    ('ba', 'Business Administration'),
    ('se', 'Software Engineering'),
]

LEVEL_CHOICES = [
    ('100', '100'),
    ('200', '200'),
    ('300', '300'),
    ('400', '400'),
]

SEMESTER_CHOICES = [
    ('1st', '1st'),
    ('2nd', '2nd'),
]

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, full_name=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, full_name=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, full_name, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)

    # New fields added here
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    level = models.CharField(max_length=3, choices=LEVEL_CHOICES, blank=True, null=True)
    semester = models.CharField(max_length=3, choices=SEMESTER_CHOICES, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # Override groups and user_permissions to avoid clashes
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",  # Unique related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",  # Unique related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
        related_query_name="customuser",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def first_name(self):
        return self.full_name.split()[0] if self.full_name else ''









# models.py

from django.db import models
from django.conf import settings

class Course(models.Model):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    level = models.CharField(max_length=3, choices=LEVEL_CHOICES)
    semester = models.CharField(max_length=3, choices=SEMESTER_CHOICES)
    credit_units = models.IntegerField()

    def __str__(self):
        return f"{self.code} - {self.title}"

class RegisteredCourse(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='registered_courses'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_registered = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')  # prevents duplicate registrations

    def __str__(self):
        return f"{self.student.email} registered {self.course.code}"



class CourseRegistration(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.email} - {self.course.title}"
    


from django.db import models
from django.conf import settings
from django.utils import timezone

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    # Optional fields for categorizing or linking
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Notification to {self.user.email}: {self.message[:50]}"



from django.db import models
from django.conf import settings

class Apartment(models.Model):
    CATEGORY_CHOICES = [
        ('studio', 'Studio'),
        ('shared', 'Shared Rooms'),
        ('pet_friendly', 'Pet Friendly'),
        ('near_library', 'Near Library'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    hot = models.BooleanField(default=False)
    image1 = models.URLField(blank=True, null=True)
    image2 = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name








# models.py

from django.contrib.auth.models import User
from django.db import models

# models.py
from django.conf import settings

class AttendanceRecord(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class_session = models.ForeignKey('ClassSession', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'class_session')


class ClassSession(models.Model):
    course = models.CharField(max_length=100)
    session_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    level = models.CharField(max_length=3, choices=LEVEL_CHOICES)
    semester = models.CharField(max_length=3, choices=SEMESTER_CHOICES)
    max_students = models.PositiveIntegerField(default=30, help_text="Maximum number of students allowed to mark attendance for this session.")

    def __str__(self):
        # You can customize this to show any info, e.g. course + session code
        return f"{self.course} ({self.session_code})"
