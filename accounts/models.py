import uuid
import sys
from io import BytesIO
from PIL import Image

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.files.uploadedfile import InMemoryUploadedFile


class RoleChoices(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    WRITER = 'writer', 'Writer'
    USER = 'user', 'User'


class StackChoices(models.TextChoices):
    BACKEND_PYTHON_DEV = 'backend_python_dev', 'Python / Django Developer'
    BACKEND_NODE_DEV = 'backend_node_dev', 'Node.js Developer'
    BACKEND_GO_RUST_DEV = 'backend_go_rust_dev', 'Go / Rust Developer'
    BACKEND_JAVA_DEV = 'backend_java_dev', 'Java Developer'
    BACKEND_DOTNET_DEV = 'backend_dotnet_dev', '.NET / C# Developer'
    BACKEND_PHP_DEV = 'backend_php_dev', 'PHP / Laravel Developer'
    FRONTEND_REACT_DEV = 'frontend_react_dev', 'React / Next.js Developer'
    FRONTEND_VUE_ANGULAR_DEV = 'frontend_vue_angular_dev', 'Vue / Angular Developer'
    MOBILE_CROSS_DEV = 'mobile_cross_dev', 'Mobile Developer'
    MOBILE_NATIVE_DEV = 'mobile_native_dev', 'Mobile Native Developer'
    DEVOPS_SRE_ENG = 'devops_sre_eng', 'DevOps / SRE Engineer'
    CLOUD_ENG = 'cloud_eng', 'Cloud Infrastructure Engineer'
    AI_ML_ENG = 'ai_ml_eng', 'AI / ML Engineer'
    DATA_ENG = 'data_eng', 'Data Engineer'
    DATA_ANALYST = 'data_analyst', 'Data Analyst / BI Specialist'
    SECURITY_PENTESTER = 'security_pentester', 'Security Researcher / Pentester'
    BLOCKCHAIN_DEV = 'blockchain_dev', 'Blockchain / Web3 Developer'
    GAME_DEV = 'game_dev', 'Game Developer'
    EMBEDDED_IOT_ENG = 'embedded_iot_eng', 'Embedded & IoT Engineer'
    QA_AUTOMATION_ENG = 'qa_automation_eng', 'QA / Automation Engineer'
    UI_UX_DESIGNER = 'ui_ux_designer', 'UI/UX Product Designer'
    PRODUCT_MANAGER = 'product_manager', 'Product Manager / Owner'
    SCRUM_MASTER_PM = 'scrum_master_pm', 'Scrum Master / Agile PM'
    DBA_SPECIALIST = 'dba_specialist', 'Database Administrator / DBA'
    SYSTEM_ARCHITECT = 'system_architect', 'System Architect'
    OPEN_SOURCE_CONTRIBUTOR = 'open_source_contributor', 'Open Source Contributor'
    SELF_GROWTH_EXPLORER = 'self_growth_explorer', 'کاوشگر رشد فردی و روانشناسی'
    DEEP_WORKER = 'deep_worker', 'Deep Work Practitioner'
    PRODUCTIVITY_ENTHUSIAST = 'productivity_enthusiast', 'خوره بهره‌وری و سیستم‌های عادات'
    MENTOR_ADVISOR = 'mentor_advisor', 'راهنما و مشاور مسیر شغلی'
    TECH_BURNOUT_SURVIVOR = 'tech_burnout_survivor', 'دغدغه‌مند سلامت روان و غلبه بر فرسودگی'
    OPTIMIST_VIBER = 'optimist_viber', 'انرژی‌بخش و مثبت‌اندیش'
    BOOK_WORM = 'book_worm', 'کتاب‌خوان و نقدکننده کتاب'
    PODCASTER_CRITIC = 'podcaster_critic', 'شنونده پادکست و نقدگر محتوا'
    MUSIC_ART_LOVER = 'music_art_lover', 'دوست‌دار هنر و موسیقی'
    TECH_MEMER = 'tech_memer', 'خالق و علاقه‌مند به میم‌های دنیای تک'
    CURIOUS_ASKER = 'curious_asker', 'کنجکاو و پرسش‌گر جامعه'


class RegistrationCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_codes'
    )
    max_uses = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_valid(self):
        return (
            self.is_active
            and self.used_count < self.max_uses
            and timezone.now() <= self.expires_at
        )

    def __str__(self):
        return self.code


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=10,
        choices=RoleChoices.choices,
        default=RoleChoices.USER
    )
    used_invite_code = models.ForeignKey(
        RegistrationCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_users'
    )
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.is_deleted = True
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True, null=True)
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    address = models.TextField(blank=True)
    stack_choice = models.CharField(max_length=50, choices=StackChoices.choices, blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    telegram = models.CharField(max_length=100, blank=True)
    summary = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='covers/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.photo:
            img = Image.open(self.photo)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.thumbnail((500, 500), Image.Resampling.LANCZOS)
            output = BytesIO()
            img.save(output, format='JPEG', quality=70)
            output.seek(0)
            self.photo = InMemoryUploadedFile(
                output, 'ImageField', 
                f"{self.user.username}_profile.jpg", 
                'image/jpeg', sys.getsizeof(output), None
            )
            
        if self.cover_photo:
            img_c = Image.open(self.cover_photo)
            if img_c.mode != 'RGB':
                img_c = img_c.convert('RGB')
            img_c.thumbnail((1500, 500), Image.Resampling.LANCZOS)
            output_c = BytesIO()
            img_c.save(output_c, format='JPEG', quality=75)
            output_c.seek(0)
            self.cover_photo = InMemoryUploadedFile(
                output_c, 'ImageField', 
                f"{self.user.username}_cover.jpg", 
                'image/jpeg', sys.getsizeof(output_c), None
            )
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class WorkExperience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='work_experiences')
    title = models.CharField(max_length=150)
    company = models.CharField(max_length=150)
    start_date = models.CharField(max_length=50)
    end_date = models.CharField(max_length=50, null=True, blank=True)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} @ {self.company}"


class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    school_name = models.CharField(max_length=150)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.degree} in {self.field_of_study}"


class Skill(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Certificate(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='certificates')
    title = models.CharField(max_length=150)
    issuer = models.CharField(max_length=150)
    issue_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class Language(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(max_length=50)
    level = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.level})"


class Project(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    link = models.URLField(blank=True)

    def __str__(self):
        return self.title


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'following'], name='unique_follow')
        ]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"