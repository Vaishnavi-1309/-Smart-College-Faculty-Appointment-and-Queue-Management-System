from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Student, Faculty

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    list_display = ['username', 'email', 'role', 'is_active']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'prn_number', 'department', 'email']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Faculty)