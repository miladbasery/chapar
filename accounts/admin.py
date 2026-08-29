from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Profile, RegistrationCode,
    WorkExperience, Education, Skill,
    Certificate, Language, Project
)


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 0


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0


class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 0


class LanguageInline(admin.TabularInline):
    model = Language
    extra = 0


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'پروفایل'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ('username', 'email', 'role', 'is_deleted', 'is_staff', 'is_active')
    list_filter = ('role', 'is_deleted', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('اطلاعات اختصاصی پلتفرم', {
            'fields': ('role', 'used_invite_code', 'is_deleted', 'deleted_at')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('اطلاعات اختصاصی پلتفرم', {
            'fields': ('role', 'used_invite_code')
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'stack_choice')
    search_fields = ('user__username', 'first_name', 'last_name', 'email')
    list_filter = ('stack_choice',)
    inlines = [
        WorkExperienceInline,
        EducationInline,
        SkillInline,
        CertificateInline,
        LanguageInline,
        ProjectInline
    ]


@admin.register(RegistrationCode)
class RegistrationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'created_by', 'used_count', 'max_uses', 'expires_at', 'is_active', 'is_valid_status')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('code', 'created_by__username')
    readonly_fields = ('used_count', 'created_at')

    @admin.display(boolean=True, description='معتبر')
    def is_valid_status(self, obj):
        return obj.is_valid