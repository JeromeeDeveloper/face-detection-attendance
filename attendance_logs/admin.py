from django.contrib import admin
from .models import Member, AttendanceLog  # Ensure you import the correct model names

# Register your models here.
admin.site.register(Member)
admin.site.register(AttendanceLog)  # Use the correct model name
