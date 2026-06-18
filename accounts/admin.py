from django.contrib import admin
from .models import CustomUser, Student, Faculty

admin.site.register(CustomUser)
admin.site.register(Student)

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    verbose_name_plural = "Faculties"  # fixes "Facultys" spelling
    list_display = ['name', 'department', 'status', 'employee_id']