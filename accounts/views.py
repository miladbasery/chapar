from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DetailView, View, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from tweeter.models import Tweet 

from .models import (
    User, Profile, WorkExperience, Education,
    Skill, Certificate, Language, Project, Follow
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


class ToggleFollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        target_user_id = request.POST.get('user_id')
        target_user = get_object_or_404(User, pk=target_user_id)
        
        if target_user != request.user:
            follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
            if not created:
                follow.delete()
                
        return redirect(request.META.get('HTTP_REFERER', '/'))


class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'accounts/profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        if username:
            return get_object_or_404(Profile, user__username__iexact=username, user__is_deleted=False)
        return get_object_or_404(Profile, user=self.request.user, user__is_deleted=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_obj = self.object.user
        
        context['followers_count'] = user_obj.followers.count()
        context['following_count'] = user_obj.following.count()
        
        if self.request.user.is_authenticated:
            context['is_following'] = Follow.objects.filter(follower=self.request.user, following=user_obj).exists()
        else:
            context['is_following'] = False
            
        base_tweets = Tweet.objects.filter(user=user_obj, status='approved').select_related('topic', 'parent_tweet', 'retweet_of').order_by('-created_at')
        
        context['all_tweets_count'] = base_tweets.count()
        context['tweets'] = base_tweets.filter(parent_tweet__isnull=True, retweet_of__isnull=True)
        context['replies'] = base_tweets.filter(parent_tweet__isnull=False)
        context['retweets'] = base_tweets.filter(retweet_of__isnull=False)
        context['stack_tweets'] = base_tweets.exclude(stack_choice='')
        
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile_settings.html'
    success_url = reverse_lazy('profile_detail_me')
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)


class WorkExperienceCreateView(LoginRequiredMixin, CreateView):
    model = WorkExperience
    form_class = WorkExperienceForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_edit')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class WorkExperienceUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkExperience
    form_class = WorkExperienceForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_edit')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class WorkExperienceDeleteView(LoginRequiredMixin, DeleteView):
    model = WorkExperience
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('profile_edit')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class EducationCreateView(LoginRequiredMixin, CreateView):
    model = Education
    form_class = EducationForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_edit')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class EducationUpdateView(LoginRequiredMixin, UpdateView):
    model = Education
    form_class = EducationForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_edit')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class EducationDeleteView(LoginRequiredMixin, DeleteView):
    model = Education
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('profile_edit')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class SkillCreateView(LoginRequiredMixin, CreateView):
    model = Skill
    form_class = SkillForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_edit')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class SkillUpdateView(LoginRequiredMixin, UpdateView):
    model = Skill
    form_class = SkillForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_edit')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class SkillDeleteView(LoginRequiredMixin, DeleteView):
    model = Skill
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('profile_edit')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class CertificateCreateView(LoginRequiredMixin, CreateView):
    model = Certificate
    form_class = CertificateForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_edit')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class CertificateUpdateView(LoginRequiredMixin, UpdateView):
    model = Certificate
    form_class = CertificateForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_edit')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class CertificateDeleteView(LoginRequiredMixin, DeleteView):
    model = Certificate
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('profile_edit')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class LanguageCreateView(LoginRequiredMixin, CreateView):
    model = Language
    form_class = LanguageForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_edit')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class LanguageUpdateView(LoginRequiredMixin, UpdateView):
    model = Language
    form_class = LanguageForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_edit')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class LanguageDeleteView(LoginRequiredMixin, DeleteView):
    model = Language
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('profile_edit')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_edit')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'accounts/form_item.html'
    success_url = reverse_lazy('profile_edit')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('profile_edit')

    def get_queryset(self):
        return self.model.objects.filter(profile__user=self.request.user)