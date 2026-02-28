from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models.User import User
from core.models.Category import Category
from core.models.Worker import Worker
from core.models.Review import Review
from core.models.OTP import OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "phone", "role", "is_staff"]
    list_filter = ["role", "is_staff"]
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {"fields": ("phone", "role", "avatar")}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ["user", "category", "is_verified", "experience_years"]
    list_filter = ["category", "is_verified"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["worker", "author", "rating", "created_at"]
    list_filter = ["rating"]


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ["phone", "code", "expires_at", "created_at"]
