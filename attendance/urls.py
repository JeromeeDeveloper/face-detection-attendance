# attendance/urls.py
from django.contrib import admin
from django.urls import path
from attendance_logs.views import Home, video_feed
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', Home, name='main-view'),
    path('video_feed/', video_feed, name='video-feed'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)