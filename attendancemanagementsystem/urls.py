from django.urls import path
from .views import (
    HomeView,
    landing_page,
    change_password,
    password_change_done,
    login,
    signup,
    notification,
    FAQ,
    transaction,
    marketplace,
    market,
    initiate_payment,
    kyc,
    courses,
    courseregistrationform,
    adminpage,
    available_courses,
    upload_course,
    register_course,
    user_profile,
    get_private_key,
    allreg,
    logout_view,
    sa,
    shared_apartment,
    pet_friendlyapa, 
    near_library,
    get_secret_key,
    attendance,
    start_session_view,
    student_sessions_view,
    mark_attendance_view,
    get_private_key,
    mark_attendance_by_code,
    show_qr_for_active_session,
    ajax_export_attendance_pdf,
    send_notification,
    test_feeds,
    FCMTokenView,
    get_feed_by_id,
)

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('home/', HomeView.as_view(), name='home'),
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('change_password/', change_password, name='change_password'),
    path('password_change_done/', password_change_done, name='password_change_done'),
    path('notification/', notification, name='notification'),
    path('FAQ/', FAQ, name='FAQ'),
    path('transaction/', transaction, name='transaction'),
    path('marketplace/', marketplace, name='marketplace'),
    path('market/', market, name='market'),
    path('initiate_payment/', initiate_payment, name='initiate_payment'),
    path('kyc/', kyc, name='kyc'),
    path('courses/', courses, name='courses'),
    path('courseregistrationform/', courseregistrationform, name='courseregistrationform'),
    path('adminpage/', adminpage, name='adminpage'),
    path('admin/upload-course/', upload_course, name='upload_course'),
    path('student/available-courses/', available_courses, name='available_courses'),
    path('register-course/<int:course_id>/', register_course, name='register_course'),
    path('profile/', user_profile, name='user_profile'),
    path('allreg/', allreg, name='allreg'),
    path('get-private-key/', get_private_key, name='get_private_key'),
    path('logout/', logout_view, name='logout'),
    path('shared_apartment/', shared_apartment, name='shared_apartment'),  # Shared apartments view
    path('pet_friendlyapa/', pet_friendlyapa, name='pet_friendlyapa'), 
    path('near_library/', near_library, name='near_library'),
    
    path('attendance/', attendance, name='attendance'),
 
    path('sa/', sa, name='sa'),
    path('api/secret-key/', get_secret_key, name='get_secret_key'),

    path('start-session/', start_session_view, name='start_session'),
    path('get-private-key/', get_private_key, name='get_private_key'),
    path('sessions/', student_sessions_view, name='student_sessions'),
    path('sessions/mark/<int:session_id>/', mark_attendance_view, name='mark_attendance'),
    path('mark-attendance/<str:session_code>/', mark_attendance_by_code, name='mark_attendance_by_code'),
    path('qr/', show_qr_for_active_session, name='show_qr'),
    # urls.py
    path('ajax/download-attendance/', ajax_export_attendance_pdf, name='ajax_download_attendance_pdf'),

    path("send-notification/", send_notification, name="send_notification"),

    path("test-feeds/", test_feeds, name="test-feeds"),



    path('save-fcm/', FCMTokenView.as_view(), name='save_fcm'),

    path('feed/<int:feed_id>/', get_feed_by_id, name='get_feed_by_id'),
    
]   
   