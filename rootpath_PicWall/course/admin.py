from django.contrib import admin

# Register your models here.
from .models import Course

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'user','slug','created')
    ordering = ('created',)


admin.site.register(Course, CourseAdmin)