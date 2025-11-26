from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Attendance, Catalog, Circulation, Acquisition, Duty, Message
)


# ================================
#   CUSTOM USER ADMIN CONFIG
# ================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("username", "email", "first_name", "last_name", "phone", "faculty", "department", "user_category", "staff_category", "is_staff")
    list_filter = ("user_category", "staff_category", "faculty", "department", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name", "phone", "student_id")
    ordering = ("username",)

    fieldsets = (
        ("Login Credentials", {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email", "phone")}),
        ("School/Library Info", {"fields": ("student_id", "faculty", "department", "user_category", "staff_category", "barcode", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "first_name", "last_name", "phone",
                       "student_id", "faculty", "department",
                       "user_category", "staff_category", "barcode",
                       "password1", "password2", "is_staff", "is_superuser")
        }),
    )


# ================================
#   ATTENDANCE ADMIN
# ================================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "purpose", "items", "method", "created_at")
    list_filter = ("method", "created_at")
    search_fields = ("user__username", "purpose", "items")
    ordering = ("-created_at",)


# ================================
#   CATALOG ADMIN
# ================================
@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "barcode", "isbn", "quantity", "can_be_borrowed", "year")
    search_fields = ("title", "author", "isbn", "issn", "barcode")
    list_filter = ("can_be_borrowed", "year", "language")
    ordering = ("title",)
    readonly_fields = ("created_at", "updated_at")


# ================================
#   CIRCULATION ADMIN
# ================================
@admin.register(Circulation)
class CirculationAdmin(admin.ModelAdmin):
    list_display = ("book", "borrower", "borrow_date", "return_date", "actual_return", "fine", "status")
    search_fields = ("book__title", "borrower", "status")
    list_filter = ("status", "borrow_date", "return_date")


# ================================
#   ACQUISITION ADMIN
# ================================
@admin.register(Acquisition)
class AcquisitionAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "supplier", "amount", "date_acquired", "added_by")
    search_fields = ("title", "supplier", "added_by__username")
    list_filter = ("source", "date_acquired")


# ================================
#   DUTY ADMIN
# ================================
@admin.register(Duty)
class DutyAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "shift")
    list_filter = ("shift", "date")
    search_fields = ("user__username", "shift")


# ================================
#   MESSAGES ADMIN
# ================================
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "sent_at")
    search_fields = ("sender__username", "receiver__username", "content")
    list_filter = ("sent_at",)
