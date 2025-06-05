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

    # Total courses registered
    total_courses = user.registered_courses.count()

    # Total credits registered
    total_registered_credits = user.registered_courses.aggregate(
        total_credits=Sum('course__credit_units')
    )['total_credits'] or 0

    # Total available credits for the student's department, level, and semester
    total_available_credits = 0
    if user.department and user.level and user.semester:
        total_available_credits = Course.objects.filter(
            department=user.department,
            level=user.level,
            semester=user.semester
        ).aggregate(total_credits=Sum('credit_units'))['total_credits'] or 0

    # Calculate progress percentage
    progress_percentage = 0
    if total_available_credits > 0:
        progress_percentage = (total_registered_credits / total_available_credits) * 100

    context = {
        'total_courses': total_courses,
        'total_registered_credits': total_registered_credits,
        'total_available_credits': total_available_credits,
        'progress_percentage': progress_percentage
    }

    return render(request, 'landing_page.html', context)



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
def registration_history(request):
    user = request.user
    registered_courses = user.registered_courses.select_related('course').order_by('-date_registered')
    # registered_courses is a queryset of RegisteredCourse objects with related Course prefetched

    return render(request, 'registration_history.html', {
        'registered_courses': registered_courses,
    })







@login_required
def registration_success(request):
    return render(request, 'success.html')




from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()

@login_required
def user_profile(request):
    user = request.user  # current logged-in user
    return render(request, 'user_profile.html', {'user': user})


@login_required
def application(request):
    user = request.user  # current logged-in user
    return render(request, 'application.html', {'user': user})


@login_required
def applications(request):
    user = request.user
    # Get all applications by this user, ordered by newest first
    user_applications = ApartmentApplication.objects.filter(user=user).order_by('-applied_at')
    return render(request, 'applications.html', {'applications': user_applications})

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

    apartments = Apartment.objects.all()
    applications = ApartmentApplication.objects.select_related('user', 'apartment').all().order_by('-applied_at')

    # Prepare applications with sent messages by current user
    applications_with_sent_messages = []
    for app in applications:
        sent_messages = app.messages.filter(sender=request.user)
        applications_with_sent_messages.append({
            'application': app,
            'sent_messages': sent_messages,
        })

    return render(request, 'adminpage.html', {
        'form': form,
        'apartments': apartments,
        'applications_with_sent_messages': applications_with_sent_messages,
    })





def apartment_detail(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    return render(request, 'apartment_detail.html', {'apartment': apartment})








@require_GET
def search_apartments(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        apartments = Apartment.objects.filter(name__icontains=query)
        for apt in apartments:
            results.append({
                'id': apt.id,
                'name': apt.name,
                'location': apt.location,
                'price': str(apt.price),  # serialize decimal
                'category': apt.category,
                'image1': apt.image1,
            })

    return JsonResponse({'results': results})


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Apartment, ApartmentApplication

@login_required
@require_POST
def apply_for_apartment(request):
    apartment_id = request.POST.get('apartment_id')
    message = request.POST.get('message', '')
    
    try:
        apartment = Apartment.objects.get(id=apartment_id)
    except Apartment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Apartment not found.'}, status=404)

    # Check if user has already applied (optional)
    if ApartmentApplication.objects.filter(user=request.user, apartment=apartment).exists():
        return JsonResponse({'success': False, 'error': 'You have already applied.'}, status=400)

    application = ApartmentApplication.objects.create(
        user=request.user,
        apartment=apartment,
        message=message
    )

    return JsonResponse({'success': True, 'message': 'Application submitted successfully.'})





from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from .models import ApartmentApplication, Message

@login_required
def reply_to_application(request, application_id):
    if request.method == "POST":
        application = get_object_or_404(ApartmentApplication, id=application_id)
        reply_message = request.POST.get('reply_message', '').strip()
        if reply_message:
            Message.objects.create(
                sender=request.user,
                recipient=application.user,
                apartment_application=application,
                content=reply_message
            )
            messages.success(request, f'Reply sent to {application.user.first_name}.')
        else:
            messages.error(request, 'Reply message cannot be empty.')
    return redirect('adminpage')




@login_required
def inbox(request):
    user = request.user
    incoming_messages = Message.objects.filter(recipient=user).order_by('-sent_at')
    return render(request, 'inbox.html', {'user': user, 'messages': incoming_messages})