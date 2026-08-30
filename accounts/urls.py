from django.urls import path
from . import views
from .views import ToggleFollowView

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('account/delete/', views.SoftDeleteAccountView.as_view(), name='account_delete'),
    path('follow/', ToggleFollowView.as_view(), name='toggle_follow'),

    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/me/', views.ProfileDetailView.as_view(), name='profile_detail_me'),
    path('profile/<str:username>/', views.ProfileDetailView.as_view(), name='profile_detail_public'),

    path('profile/work/add/', views.WorkExperienceCreateView.as_view(), name='work_add'),
    path('profile/work/<int:pk>/edit/', views.WorkExperienceUpdateView.as_view(), name='work_edit'),
    path('profile/work/<int:pk>/delete/', views.WorkExperienceDeleteView.as_view(), name='work_delete'),

    path('profile/education/add/', views.EducationCreateView.as_view(), name='education_add'),
    path('profile/education/<int:pk>/edit/', views.EducationUpdateView.as_view(), name='education_edit'),
    path('profile/education/<int:pk>/delete/', views.EducationDeleteView.as_view(), name='education_delete'),

    path('profile/skill/add/', views.SkillCreateView.as_view(), name='skill_add'),
    path('profile/skill/<int:pk>/edit/', views.SkillUpdateView.as_view(), name='skill_edit'),
    path('profile/skill/<int:pk>/delete/', views.SkillDeleteView.as_view(), name='skill_delete'),

    path('profile/certificate/add/', views.CertificateCreateView.as_view(), name='certificate_add'),
    path('profile/certificate/<int:pk>/edit/', views.CertificateUpdateView.as_view(), name='certificate_edit'),
    path('profile/certificate/<int:pk>/delete/', views.CertificateDeleteView.as_view(), name='certificate_delete'),

    path('profile/language/add/', views.LanguageCreateView.as_view(), name='language_add'),
    path('profile/language/<int:pk>/edit/', views.LanguageUpdateView.as_view(), name='language_edit'),
    path('profile/language/<int:pk>/delete/', views.LanguageDeleteView.as_view(), name='language_delete'),

    path('profile/project/add/', views.ProjectCreateView.as_view(), name='project_add'),
    path('profile/project/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
    path('profile/project/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
]