from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.html import escape
from .models import (
    User, Profile, RegistrationCode,
    WorkExperience, Education, Skill,
    Certificate, Language, Project
)


def sanitize_input(text, max_len=None):
    if not text:
        return text
    text = str(text).strip()
    if max_len and len(text) > max_len:
        raise ValidationError(f"تعداد کاراکتر مجاز نیست. (حداکثر {max_len} حرف)")
    return escape(text)


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="نام کاربری",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام کاربری خود را وارد کنید'})
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'رمز عبور خود را وارد کنید'})
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            if User.objects.filter(username=username, is_deleted=True).exists():
                raise ValidationError(
                    "حساب کاربری شما غیرفعال شده است. لطفاً با ادمین در ارتباط باشید."
                )

            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserRegistrationForm(UserCreationForm):
    invite_code = forms.CharField(max_length=50, required=True, label="کد دعوت")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'invite_code')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username, is_deleted=True).exists():
            raise ValidationError(
                "این حساب کاربری غیرفعال شده است. برای بازیابی اکانت خود با ادمین در ارتباط باشید."
            )
        return username

    def clean_invite_code(self):
        code_str = self.cleaned_data.get('invite_code')
        try:
            invite_code = RegistrationCode.objects.get(code=code_str)
        except RegistrationCode.DoesNotExist:
            raise ValidationError("کد دعوت وارد شده نامعتبر است.")

        if not invite_code.is_active:
            raise ValidationError("این کد دعوت غیرفعال شده است.")

        if invite_code.used_count >= invite_code.max_uses:
            raise ValidationError("ظرفیت استفاده از این کد دعوت به پایان رسیده است.")

        if timezone.now() > invite_code.expires_at:
            raise ValidationError("مهلت استفاده از این کد دعوت منقضی شده است.")

        self.invite_code_obj = invite_code
        return code_str

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.used_invite_code = getattr(self, 'invite_code_obj', None)
        
        if commit:
            with transaction.atomic():
                user.save()
                if user.used_invite_code:
                    RegistrationCode.objects.filter(
                        pk=user.used_invite_code.pk
                    ).update(used_count=F('used_count') + 1)
                
                Profile.objects.get_or_create(user=user)
                
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'first_name', 'last_name', 'email', 'age',
            'address', 'stack_choice', 'linkedin',
            'github', 'telegram', 'summary', 'photo'
        )

    def clean_first_name(self):
        return sanitize_input(self.cleaned_data.get('first_name'), max_len=20)

    def clean_last_name(self):
        return sanitize_input(self.cleaned_data.get('last_name'), max_len=30)

    def clean_summary(self):
        return sanitize_input(self.cleaned_data.get('summary'), max_len=500)


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ('title', 'company', 'start_date', 'end_date', 'is_current')

    def clean_title(self):
        return sanitize_input(self.cleaned_data.get('title'), max_len=50)

    def clean_company(self):
        return sanitize_input(self.cleaned_data.get('company'), max_len=50)


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ('school_name', 'degree', 'field_of_study')

    def clean_school_name(self):
        return sanitize_input(self.cleaned_data.get('school_name'), max_len=60)

    def clean_degree(self):
        return sanitize_input(self.cleaned_data.get('degree'), max_len=50)

    def clean_field_of_study(self):
        return sanitize_input(self.cleaned_data.get('field_of_study'), max_len=50)


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ('name',)

    def clean_name(self):
        return sanitize_input(self.cleaned_data.get('name'), max_len=30)


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ('title', 'issuer', 'issue_date')

    def clean_title(self):
        return sanitize_input(self.cleaned_data.get('title'), max_len=60)

    def clean_issuer(self):
        return sanitize_input(self.cleaned_data.get('issuer'), max_len=60)


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ('name', 'level')

    def clean_name(self):
        return sanitize_input(self.cleaned_data.get('name'), max_len=30)

    def clean_level(self):
        return sanitize_input(self.cleaned_data.get('level'), max_len=30)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('title', 'description', 'link')

    def clean_title(self):
        return sanitize_input(self.cleaned_data.get('title'), max_len=60)

    def clean_description(self):
        return sanitize_input(self.cleaned_data.get('description'), max_len=300)