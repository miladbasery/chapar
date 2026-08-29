from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DetailView, View, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from .models import (
    User, Profile, WorkExperience, Education,
    Skill, Certificate, Language, Project
)
from .forms import (
    UserRegistrationForm, UserLoginForm, ProfileForm,
    WorkExperienceForm, EducationForm, SkillForm,
    CertificateForm, LanguageForm, ProjectForm
)



class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('profile_detail_me')


class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('profile_detail_me')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect(self.success_url)


class UserLogoutView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')


class SoftDeleteAccountView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        user.soft_delete()
        logout(request)
        messages.success(
            request,
            "حساب کاربری شما حذف شد. در صورت نیاز به بازگردانی با پشتیبانی تماس بگیرید."
        )
        return redirect('login')



class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'accounts/profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        if username:
            return get_object_or_404(
                Profile, 
                user__username__iexact=username, 
                user__is_deleted=False
            )
        return get_object_or_404(
            Profile, 
            user=self.request.user, 
            user__is_deleted=False
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile_form.html'
    success_url = reverse_lazy('profile_detail_me')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)



class WorkExperienceCreateView(LoginRequiredMixin, CreateView):
    model = WorkExperience
    form_class = WorkExperienceForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_detail_me')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class WorkExperienceUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkExperience
    form_class = WorkExperienceForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_detail_me')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class WorkExperienceDeleteView(LoginRequiredMixin, DeleteView):
    model = WorkExperience
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('profile_detail_me')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)



class EducationCreateView(LoginRequiredMixin, CreateView):
    model = Education
    form_class = EducationForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_detail_me')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class EducationUpdateView(LoginRequiredMixin, UpdateView):
    model = Education
    form_class = EducationForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_detail_me')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class EducationDeleteView(LoginRequiredMixin, DeleteView):
    model = Education
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('profile_detail_me')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)



class SkillCreateView(LoginRequiredMixin, CreateView):
    model = Skill
    form_class = SkillForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_detail_me')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class SkillUpdateView(LoginRequiredMixin, UpdateView):
    model = Skill
    form_class = SkillForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_detail_me')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class SkillDeleteView(LoginRequiredMixin, DeleteView):
    model = Skill
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('profile_detail_me')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class CertificateCreateView(LoginRequiredMixin, CreateView):
    model = Certificate
    form_class = CertificateForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_detail_me')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class CertificateUpdateView(LoginRequiredMixin, UpdateView):
    model = Certificate
    form_class = CertificateForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_detail_me')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class CertificateDeleteView(LoginRequiredMixin, DeleteView):
    model = Certificate
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('profile_detail_me')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class LanguageCreateView(LoginRequiredMixin, CreateView):
    model = Language
    form_class = LanguageForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_detail_me')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class LanguageUpdateView(LoginRequiredMixin, UpdateView):
    model = Language
    form_class = LanguageForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_detail_me')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class LanguageDeleteView(LoginRequiredMixin, DeleteView):
    model = Language
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('profile_detail_me')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_detail_me')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_detail_me')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('profile_detail_me')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)