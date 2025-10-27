# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from .models import User, Project


# # =======================
# # Custom User Admin
# # =======================
# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     list_display = ("username", "email", "first_name", "last_name", "is_active", "is_staff")
#     list_filter = ("is_active", "is_staff", "is_superuser")
#     search_fields = ("username", "email", "first_name", "last_name")
#     ordering = ("email",)

#     fieldsets = (
#         (None, {"fields": ("username", "email", "password")}),
#         ("Personal info", {"fields": ("first_name", "last_name", "phone")}),
#         ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
#         ("Important dates", {"fields": ("last_login", "date_joined")}),
#     )


# # =======================
# # Custom Project Admin
# # =======================
# @admin.register(Project)
# class ProjectAdmin(admin.ModelAdmin):
#     list_display = ("title", "author", "department", "category", "approved", "created_at")
#     list_filter = ("department", "category", "approved")
#     search_fields = ("title", "author", "department")
#     actions = ["approve_projects"]

#     def approve_projects(self, request, queryset):
#         """Custom action to bulk approve projects"""
#         updated = queryset.update(approved=True)
#         self.message_user(request, f"{updated} project(s) approved successfully.")

#     approve_projects.short_description = "Approve selected projects"


# # =======================
# # Admin Site Branding
# # =======================
# admin.site.site_header = "Super Admin Dashboard"
# admin.site.site_title = "Super Admin Dashboard"
# admin.site.index_title = "Welcome to the Super Admin Dashboard"
