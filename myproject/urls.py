from django.contrib import admin
from django.urls import path, include
from hostelallocation.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hostelallocation/', include('hostelallocation.urls')),
    path('', HomeView.as_view(), name='home'),
]
