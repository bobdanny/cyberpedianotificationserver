# myapp/views.py
import json
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt

from .forms import CustomUserCreationForm, CustomAuthenticationForm

def generate_tx_ref():
    # Implement your logic for generating a unique transaction reference
    import uuid
    return str(uuid.uuid4())

@csrf_exempt
@login_required
def initiate_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get('amount')
        country = data.get('country')
        currency = data.get('currency')

        # Generate unique transaction reference
        tx_ref = generate_tx_ref()

        # Flutterwave payment link creation
        flutterwave_url = "https://api.flutterwave.com/v3/charges?type=banktransfer"
        headers = {
            'Authorization': 'Bearer FLWSECK_TEST-7d3a34940a220702dcfb6a3f085304d5-X',
            'Content-Type': 'application/json'
        }
        payload = {
            "tx_ref": tx_ref,
            "amount": amount,
            "currency": currency,
            "email": request.user.email,
            "payment_type": "banktransfer",
            "redirect_url": "https://yourwebsite.com/payment-completion",  # Update with your redirect URL
        }

        response = requests.post(flutterwave_url, headers=headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("status") == "success":
                payment_url = response_data['data']['link']  # Extract the payment link
                return JsonResponse({'success': True, 'payment_url': payment_url})
        
        return JsonResponse({'success': False, 'message': 'Payment initiation failed.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})


@login_required
def payment_completion(request):
    tx_ref = request.GET.get('tx_ref')
    
    # Call Flutterwave API to check transaction status
    flutterwave_url = f"https://api.flutterwave.com/v3/transactions/{tx_ref}/verify"
    headers = {
        'Authorization': 'Bearer YOUR_FLUTTERWAVE_SECRET_KEY',
        'Content-Type': 'application/json'
    }

    response = requests.get(flutterwave_url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        if response_data.get('status') == 'success':
            # Payment was successful
            amount = response_data['data']['amount']
            transaction = Transaction.objects.create(
                user=request.user,
                amount=amount,
                tx_ref=tx_ref,
                status='success'
            )
            # Update user balance
            profile = request.user.profile
            profile.balance += amount
            profile.save()
            return render(request, 'payment_success.html', {'amount': amount})

    return render(request, 'payment_failed.html', {'tx_ref': tx_ref})






















































from django.db.models import Sum
@login_required
def landing_page(request):
    user = request.user

    # Filter sessions that:
    # 1. Match the student's department, level, and semester.
    # 2. Are not expired yet.
    sessions = ClassSession.objects.filter(
        department=user.department,
        level=user.level,
        semester=user.semester,
        expires_at__gt=timezone.now()
    ).order_by('-created_at')

    context = {
        'sessions': sessions
    }

    return render(request, 'landing_page.html', context)





from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DEPARTMENT_CHOICES, LEVEL_CHOICES, SEMESTER_CHOICES
from .utils import start_class_session  # import the function you wrote earlier











@login_required
def start_session_view(request):
    if request.method == "POST":
        course = request.POST.get("course")
        session_code = request.POST.get("session_code")
        department = request.POST.get("department")
        level = request.POST.get("level")
        semester = request.POST.get("semester")
        duration = request.POST.get("duration")
        max_students = request.POST.get("max_students")

        # Basic validation
        if not all([course, session_code, department, level, semester, duration, max_students]):
            messages.error(request, "All fields are required.")
            return redirect("start_session")

        try:
            duration = int(duration)
        except ValueError:
            messages.error(request, "Duration must be a number.")
            return redirect("start_session")

        try:
            max_students = int(max_students)
        except ValueError:
            messages.error(request, "Maximum students must be a number.")
            return redirect("start_session")

        try:
            # Create the session
            session = start_class_session(
                course=course,
                session_code=session_code,
                department=department,
                level=level,
                semester=semester,
                duration_minutes=duration,
                max_students=max_students
            )
            messages.success(request, f"Class session '{session.session_code}' started successfully!")
            return redirect("start_session")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect("start_session")

    # GET request: render the session form and attendance records table
    department_filter = request.GET.get("department", "")
    level_filter = request.GET.get("level", "")
    semester_filter = request.GET.get("semester", "")

    # Fetch attendance records
    attendance_records = AttendanceRecord.objects.select_related('student', 'class_session').all()

    if department_filter:
        attendance_records = attendance_records.filter(class_session__department=department_filter)
    if level_filter:
        attendance_records = attendance_records.filter(class_session__level=level_filter)
    if semester_filter:
        attendance_records = attendance_records.filter(class_session__semester=semester_filter)

    attendance_records = attendance_records.order_by('-timestamp')  # latest first

    context = {
        "departments": DEPARTMENT_CHOICES,
        "levels": LEVEL_CHOICES,
        "semesters": SEMESTER_CHOICES,
        "attendance_records": attendance_records,
        "selected_department": department_filter,
        "selected_level": level_filter,
        "selected_semester": semester_filter,
    }
    return render(request, "start_session.html", context)

































@login_required  # Remove if you don't want to require login
def get_private_key(request):
    # NEVER send the raw key in production — this is for demo only.
    private_key = "secret123"  # Ideally, store in settings or environment variable
    return JsonResponse({"private_key": private_key})









@login_required
def allreg(request):
    User = get_user_model()
    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_registered_courses = RegisteredCourse.objects.count()
    total_course_registrations = CourseRegistration.objects.count()

    # Fetch all course registrations, ordered by date desc
    all_registrations = CourseRegistration.objects.select_related('student', 'course') \
                                                 .order_by('-registered_at')

    context = {
        'total_users': total_users,
        'total_courses': total_courses,
        'total_registered_courses': total_registered_courses,
        'total_course_registrations': total_course_registrations,
        'all_registrations': all_registrations,
    }
    return render(request, 'allreg.html', context)




@login_required
def courseregistrationform(request):
    return render(request, 'courseregistrationform.html')






@login_required
def courses(request):
    return render(request, 'courses.html')


# Password Change View
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            return redirect('password_change_done')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
def password_change_done(request):
    return render(request, 'password_change_done.html')

from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect
from .forms import CustomAuthenticationForm  # adjust import path as needed

def login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)  # pass request to form for authenticate
        if form.is_valid():
            auth_login(request, form.get_user())
            next_url = request.GET.get('next') or 'home'
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})

from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect

def logout_view(request):
    auth_logout(request)
    return redirect('login')

# Signup View
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from .forms import CustomUserCreationForm

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Automatically log in after signup
            return redirect('home')  # Redirect wherever you want
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

from django.views.generic import TemplateView
from .models import Apartment

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hot_apartments'] = Apartment.objects.filter(hot=True)
        context['all_apartments'] = Apartment.objects.all()
        return context
    




def sa(request):
    studio_apartments = Apartment.objects.filter(category='studio')
    return render(request, 'sa.html', {'apartments': studio_apartments})




def shared_apartment(request):
    shared_rooms = Apartment.objects.filter(category='shared')
    return render(request, 'shared_apartment.html', {'apartments': shared_rooms})



def get_secret_key(request):
    return JsonResponse({'secret_key': settings.MY_SECRET_KEY})



def pet_friendlyapa(request):
    pet_friendly_apartments = Apartment.objects.filter(category='pet_friendly')
    return render(request, 'pet_friendlyapa.html', {'apartments': pet_friendly_apartments})

def near_library(request):
    near_library_apartments = Apartment.objects.filter(category='near_library')
    return render(request, 'near_library.html', {'apartments': near_library_apartments})



@login_required
def notification(request):
    return render(request, 'notification.html')

@login_required
def FAQ(request):
    return render(request, 'FAQ.html')

@login_required
def transaction(request):
    return render(request, 'transaction.html')

@login_required
def marketplace(request):
    return render(request, 'marketplace.html')

@login_required
def market(request):
    return render(request, 'market.html')
 
@login_required
def kyc(request):
    return render(request, 'kyc')
 







from django.shortcuts import render, redirect
from .forms import CourseForm


def upload_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('upload_course_success')  # Point this to a success URL or message
    else:
        form = CourseForm()
    return render(request, 'upload_course.html', {'form': form})




from django.contrib.auth.decorators import login_required
from .models import Course



@login_required
def available_courses(request):
    user = request.user

    if not user.department or not user.level or not user.semester:
        return render(request, 'error.html', {'message': 'Your profile is incomplete. Please contact support.'})

    courses = Course.objects.filter(
        department=user.department,
        level=user.level,
        semester=user.semester
    )

    registered_course_ids = set(
        RegisteredCourse.objects.filter(student=user).values_list('course_id', flat=True)
    )

    for course in courses:
        course.registered = course.id in registered_course_ids

    # Also get full registered courses queryset for the user
    registered_courses = RegisteredCourse.objects.filter(student=user).select_related('course')

    return render(request, 'available_courses.html', {
        'courses': courses,
        'registered_courses': registered_courses,
    })



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Course, RegisteredCourse
from .models import Course, CourseRegistration




@login_required
def register_course(request, course_id):
    user = request.user
    course = get_object_or_404(Course, id=course_id)

    # Check if already registered
    already_registered = RegisteredCourse.objects.filter(student=user, course=course).exists()

    if already_registered:
        messages.info(request, f"You have already registered for {course.title}.")
    else:
        # Create registration
        RegisteredCourse.objects.create(student=user, course=course)
        messages.success(request, f"Successfully registered for {course.title}!")

    return redirect('registration_success')






from django.shortcuts import render







@login_required
def registration_success(request):
    return render(request, 'success.html')

@login_required
def attendance(request):
    student = request.user

    now = timezone.now()
    sessions = ClassSession.objects.filter(
        department=student.department,
        level=student.level,
        expires_at__gt=now
    )

    if request.method == "POST":
        session_id = request.POST.get("session_id")
        entered_code = request.POST.get("session_code", "").strip()

        try:
            session = ClassSession.objects.get(id=session_id)
        except ClassSession.DoesNotExist:
            messages.error(request, "Selected session does not exist.")
            return redirect('attendance')

        # Check if entered code matches
        if session.session_code != entered_code:
            messages.error(request, "Incorrect session code.")
            return redirect('attendance')

        # Check if session expired
        if timezone.now() > session.expires_at:
            messages.error(request, "This session has expired.")
            return redirect('attendance')

        # Check if max students reached
        current_count = AttendanceRecord.objects.filter(class_session=session).count()
        if current_count >= session.max_students:
            messages.error(request, "This session has reached the maximum number of students allowed to mark attendance.")
            return redirect('attendance')

        # Check if student already marked attendance
        already_marked = AttendanceRecord.objects.filter(
            student=student,
            class_session=session
        ).exists()

        if already_marked:
            messages.info(request, "You have already marked attendance for this session.")
        else:
            AttendanceRecord.objects.create(student=student, class_session=session)
            messages.success(request, "Attendance marked successfully!")

        return redirect('attendance')

    # Build session_data list with attendance_marked
    session_data_list = []
    for session in sessions:
        attendance_marked = AttendanceRecord.objects.filter(
            student=student,
            class_session=session
        ).exists()
        session_data = {
            'id': session.id,
            'course': session.course,
            'session_code': session.session_code,
            'department': session.department,
            'level': session.level,
            'semester': session.semester,
            'expires_at': session.expires_at,
            'attendance_marked': attendance_marked,
            'max_students': session.max_students,   # optional, if you want to pass it to the template
            'current_attendance': AttendanceRecord.objects.filter(class_session=session).count()
        }
        session_data_list.append(session_data)

    return render(request, 'attendance.html', {'sessions': session_data_list})



from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()

@login_required
def user_profile(request):
    user = request.user  # current logged-in user
    return render(request, 'user_profile.html', {'user': user})


from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def get_private_key(request):
    return JsonResponse({"private_key": settings.PRIVATE_KEY})




# views.py
import cloudinary.uploader
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Apartment
from .forms import ApartmentForm


@login_required
def adminpage(request):
    if request.method == 'POST':
        # Handle delete apartment request
        if 'delete_apartment_id' in request.POST:
            apartment_id = request.POST.get('delete_apartment_id')
            apartment = get_object_or_404(Apartment, id=apartment_id, user=request.user)
            apartment.delete()
            messages.success(request, f'Apartment "{apartment.name}" has been deleted.')
            return redirect('adminpage')

        # Handle apartment upload form submission
        form = ApartmentForm(request.POST, request.FILES)
        if form.is_valid():
            apartment = form.save(commit=False)
            apartment.user = request.user
            for i in range(1, 3):
                file = request.FILES.get(f'image{i}')
                if file:
                    result = cloudinary.uploader.upload(file)
                    setattr(apartment, f'image{i}', result['secure_url'])
            apartment.save()
            return redirect('adminpage')
    else:
        form = ApartmentForm()

  





























from .models import ClassSession
from .models import AttendanceRecord
# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from .models import AttendanceRecord, ClassSession



from django.db.models import Count

from django.shortcuts import redirect
from django.contrib import messages

from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


@csrf_exempt
@login_required
def mark_attendance(request, code):
    try:
        session = ClassSession.objects.get(session_code=code)
        print(f"[DEBUG] Session found: {session}, max_students={session.max_students}")

        # Check if session has expired
        if timezone.now() > session.expires_at:
            print("[DEBUG] Session expired.")
            messages.error(request, "This session has expired.")
            return redirect('attendance')  # Replace with your actual attendance page/view

        # Count current attendance
        current_count = AttendanceRecord.objects.filter(class_session=session).count()
        print(f"[DEBUG] Current attendance count: {current_count}")

        # Check if max students reached
        if current_count >= session.max_students:
            print("[DEBUG] Max students reached.")
            messages.error(request, "This session has reached the maximum number of students allowed to mark attendance.")
            return redirect('attendance')

        student = request.user
        print(f"[DEBUG] Current student: {student}")

        # Check if student has already marked attendance
        attendance, created = AttendanceRecord.objects.get_or_create(
            student=student,
            class_session=session
        )
        print(f"[DEBUG] Attendance record created: {created}")

        if not created:
            messages.info(request, "You have already marked attendance for this session.")
        else:
            messages.success(request, "Attendance marked successfully!")

        return redirect('attendance')

    except ClassSession.DoesNotExist:
        print("[DEBUG] ClassSession.DoesNotExist exception caught.")
        messages.error(request, "Invalid session code or session does not exist.")
        return redirect('attendance')

    except Exception as e:
        print(f"[DEBUG] Exception caught: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('attendance')





import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings

























from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import ClassSession, AttendanceRecord

def student_sessions_view(request):
    user = request.user
    now = timezone.now()

    # Filter active sessions for student's department and level
    sessions = ClassSession.objects.filter(
        department=user.department,
        level=user.level,
        expires_at__gt=now
    )

    # Get all session IDs student has marked attendance for
    attended_session_ids = AttendanceRecord.objects.filter(student=user).values_list('class_session_id', flat=True)

    context = {
        'sessions': sessions,
        'attended_session_ids': attended_session_ids,
    }
    return render(request, 'student_sessions.html', context)

def mark_attendance_view(request, session_id):
    user = request.user
    session = get_object_or_404(ClassSession, id=session_id)

    # Check if session matches user dept and level and is active
    if session.department != user.department or session.level != user.level or session.expires_at <= timezone.now():
        messages.error(request, "You cannot mark attendance for this session.")
        return redirect('student_sessions')

    # Check if already marked attendance
    if AttendanceRecord.objects.filter(student=user, class_session=session).exists():
        messages.info(request, "You have already marked attendance for this session.")
    else:
        AttendanceRecord.objects.create(student=user, class_session=session)
        messages.success(request, f"Attendance marked for session {session.session_code}.")

    return redirect('student_sessions')
