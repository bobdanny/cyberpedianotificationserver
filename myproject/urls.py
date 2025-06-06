from django.contrib import admin
from django.urls import path, include
from attendancemanagementsystem.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('attendancemanagementsystem/', include('attendancemanagementsystem.urls')),
    path('', HomeView.as_view(), name='home'),
]
