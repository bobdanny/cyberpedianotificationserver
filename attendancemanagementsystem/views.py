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




  




from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .models import ClassSession, AttendanceRecord

@login_required 
def mark_attendance_by_code(request, session_code):
    session = get_object_or_404(ClassSession, session_code=session_code)

    if timezone.now() > session.expires_at:
        messages.error(request, "This session has expired.")
        return redirect('attendance')

    current_count = AttendanceRecord.objects.filter(class_session=session).count()
    if current_count >= session.max_students:
        messages.error(request, "This session has reached the maximum attendance limit.")
        return redirect('attendance')

    student = request.user

    if AttendanceRecord.objects.filter(student=student, class_session=session).exists():
        messages.info(request, "You have already marked attendance for this session.")
    else:
        AttendanceRecord.objects.create(student=student, class_session=session)
        messages.success(request, "Attendance marked successfully!")

    return redirect('attendance')












import qrcode
import io
import base64
from django.utils import timezone
from django.shortcuts import render
from django.conf import settings
from .models import ClassSession

@login_required
def show_qr_for_active_session(request):
    # Get active session (you can customize this filter)
    session = ClassSession.objects.filter(expires_at__gt=timezone.now()).order_by('-created_at').first()

    if not session:
        return render(request, 'no_active_session.html')

    # Build full attendance URL
    session_code = session.session_code
    domain = settings.SITE_URL  # Define this in settings.py (e.g., "https://yourdomain.com")
    url = f"{domain}/attendancemanagementsystem/mark-attendance/{session_code}/"



    # Generate QR code image
    qr = qrcode.make(url)
    buffer = io.BytesIO()
    qr.save(buffer, format='PNG')
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'show_qr.html', {
        'session': session,
        'qr_image': qr_image_base64,
        'url': url
    })















from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import AttendanceRecord

def ajax_export_attendance_pdf(request):
    # Fetch attendance records with related student and class_session
    records = AttendanceRecord.objects.select_related('student', 'class_session')

    # Load the HTML template and render it with the records
    template = get_template('attendance_pdf.html')
    html = template.render({'records': records})

    # Create an HTTP response with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance.pdf"'

    # Create PDF and write it directly to the response
    pisa_status = pisa.CreatePDF(html, dest=response)

    # If error occurs, return HTML with error info (optional)
    if pisa_status.err:
        return HttpResponse(f"Error generating PDF: {pisa_status.err}", status=500)

    return response









from django.http import JsonResponse
import requests
import firebase_admin
from firebase_admin import credentials, messaging

# 🔐 Firebase service account embedded as dictionary
firebase_config = {
    "type": "service_account",
    "project_id": "cyberpediawithflutter",
    "private_key_id": "6150ad8739456edf939714cbd1cd732f74bfb9f8",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDKfDt2Dqz/VmwW\nEzwvBAoG+FqSbVsKY0uHdPI9jQGvuujcy+UCsp74ekREUVO5m7/Ld5PwEZi339lT\ndngqg7k1uDEOhf2BMlbuvB7qngGxKsU9tjGxoSqw0QXiyHKTvEkjXWedSUtYj2DI\nBFeFzakYbkN60AcGhwDiID1Wjx8ozfuimZxMp3pIqXcF/daZ9EvnxDNgZ4tNd5j3\nPuYXaJZxkZc/jNmNNgV+JeyFb0KwPWYfoaVDQ4NwQECOCOBJOw37vsG1vS6sMjLX\nDwBm8kw0/QkXHry2lH63KwcZCPATJVS+Zt7A++PH5IcAesQGTx5kH704TMjvG226\nppklBbxjAgMBAAECggEAKp3qH+dn1tf4KM9El/qoJ55m5bG5ex65+1kMURMX+0YC\nE9KgMSiqF88YBi79ya9ztx3EV79EXtLw2UWydfRCa4GIZa+i0unm7RlQAn5eCc1g\nNSRfIi0zIILl07zvjJOQ6y4SDEMsZgfLTV3IlANcpyUx86vMBr4sW+uALXMzEjGk\nUV1IVpXuWN2o9r0Foy5RIVwrl+pCUOsSIYXV6x9Gd8A/61Ni9XPe9DONSbos1LJL\ngu7MdC8oBmKh+RiAAm8MduBwAjj8dHYshq3Bj2rjlt82Da1R+Ad7xQcfjYOVw9sT\nbH7kogFAKp8jnWXZCpQLIGTmrICPbMr/fE1LM9qy/QKBgQDyYiC43L0OAeQjmKBs\nInD/tOAsWm/E6JXEIu/UXLTgwI2P0zf+oD9yBNZmLHWhbGXwSGSGWcFtUAFepTSK\nhBdtIgniSDN8+KzCJdSnkYwcbp6ckHufZL4hOTqNvCKaXBGJ9BfNpx3vtHEQ11hC\nIbdiKmoDcPTwRKevEBbU36U3TQKBgQDV3E4PBso22PatvU0AmZICcLAsU4V2gsY2\nxnIQcLFJOr3THKZmcwyZPpkAfdNb92Iyn5na8DvhoTZihbjuFr57KrOthLy/eS1b\nccby93wMrvDzyhWpLWWQgv+w+6oFSe6aYsc8qXkZHR/FxVT7Ik+Gnhj2P0nkF4cM\n/azLKcDKbwKBgG0KXiQsEdT6XtLwt8LN3735dhwd90hDRhT9jp0fs7OkjErWv8sJ\n9mDp8jX27FhZdqaZOrgCKvVtV6Bne/KQqCVNedrVlmwzRyz0be2QmdK0pSBUE3lK\njgpOP5xBteNxZeaE7Cx1cQ9EQtVLu4XMuz4rTJQNvfNVP4aPG2Za0m3FAoGBALS+\nCEqy1lwcaf7UKiwDnl7pljsgK3/JbnQEq4oxc+QL/Tpa0FdtjIxHV1APB36GSTu3\nn3Rl7HX4pdoGYhD2r+2wXUKdGFhKtYa/VgEqIHEnuQSRGlVsxJWp4SdWyo7FuR5J\ntVETegE7mAqxh+znRobjPv1+55gaOk1EZ7EcjI+JAoGBAOBTqbnDxFbVOUBEAA4F\nSo+wtYKcNa0j6KR4RjMm/JcMBJ+GyfaTUQw8KOeJMJKtMnLgm56pPEP+CKqB0GOY\nc7//51KSCE44bWBeRNs6YbovIQanGp0WAxnYsfuJFMyEvxyJwnXVCy/M6yc06X1I\nLnIKB1XybQTY32cirbFN0PKl\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-fbsvc@cyberpediawithflutter.iam.gserviceaccount.com",
    "client_id": "100409226041708107080",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40cyberpediawithflutter.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# ✅ Initialize Firebase Admin only once
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)










def send_notification(request):
    device_token = "dWfKLWg0S9SdENx0ah0HyZ:APA91bHNnNc2h9yT3Pt--gzCU4QflIYAqkNTRV5KzuKQ0IQB6To5MlNdhDbEAgimwQ3nXSibiuhRV038HdywhOHvF0KlE-XcxjtBclKCKCQ2w8q2l8kiY7Q"

    try:
        url = "https://cyberpedia-api.onrender.com/feeds?q=&limit=5"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        print("Full API response data:", data)  # Debug print

        feeds = data.get("data", {}).get("feeds", [])
        print(f"Extracted feeds: {feeds}")  # Debug print

        # Print each feed's ID
        for feed in feeds:
            print(f"Feed ID: {feed.get('id')}")

        if not feeds:
            return JsonResponse({"success": False, "error": "No feeds found in API response"})

        results = []
        for feed in feeds:
            title = feed.get("title", "Cyber Feed")
            body = feed.get("description", "")[:100]
            image = feed.get("image", "")

            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body if body else "New feed available",
                    image=image if image else None,
                ),
                data={
                    "route": "cyber_feeds",
                    "feed_id": str(feed.get("id", "")),
                    "image": image or "",
                    "provider": feed.get("provider", ""),
                    "pubDate": feed.get("pub_date", ""),
                },
                token=device_token,
            )

            res = messaging.send(message)
            results.append(res)

        return JsonResponse({"success": True, "responses": results})

    except Exception as e:
        print("Error occurred:", e)
        return JsonResponse({"success": False, "error": str(e)})


def get_feed_by_id(request, feed_id):
    try:
        # Fetch list of feeds
        url = "https://cyberpedia-api.onrender.com/feeds?q=&limit=50"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        feeds = data.get("data", {}).get("feeds", [])

        print(f"Searching {len(feeds)} feeds for ID: {feed_id}")

        # Search for feed by ID
        for feed in feeds:
            if str(feed.get("id")) == str(feed_id):
                return JsonResponse({"status": "success", "feed": feed})

        return JsonResponse({
            "status": "error",
            "message": "Feed not found",
            "data": {}
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "data": {}
        })








def get_feed_by_id(request, feed_id):
    try:
        # Fetch list of feeds
        url = "https://cyberpedia-api.onrender.com/feeds?q=&limit=50"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        feeds = data.get("data", {}).get("feeds", [])
        print(f"Searching {len(feeds)} feeds for ID: {feed_id}")

        # Search for feed by ID
        for feed in feeds:
            if str(feed.get("id")) == str(feed_id):
                return JsonResponse({"status": "success", "feed": feed})

        return JsonResponse({
            "status": "error",
            "message": "Feed not found",
            "data": {}
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "data": {}
        })














import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

BASE_URL = "https://cyberpedia-api.onrender.com"
import requests
from django.http import HttpResponse
from django.shortcuts import render

def test_feeds(request):
    url = "https://cyberpedia-api.onrender.com/feeds"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise error if not 200

        # Try parsing JSON safely
        try:
            data = response.json()
        except ValueError:
            return HttpResponse("<h2>API did not return JSON</h2><pre>" + response.text[:500] + "</pre>")

        # Safely navigate structure
        feeds = (
            data.get("data", {})
                .get("feeds", [])
        )

        return render(request, "feeds.html", {"feeds": feeds})

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"<h2>Failed to fetch feeds: {e}</h2>", status=500)









# attendancemanagementsystem/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FCMToken
from rest_framework import serializers

# Serializer
class FCMTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMToken
        fields = ['token']

# API View
class FCMTokenView(APIView):
    def post(self, request):
        serializer = FCMTokenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Token saved successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  


