import sys
from io import BytesIO
from PIL import Image
from django.utils import timezone

from django.db import models
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from accounts.models import RoleChoices, StackChoices


class GroupCategoryChoices(models.TextChoices):
    PROGRAMMING = 'programming', 'برنامه‌نویسی و توسعه نرم‌افزار'
    PERSONAL_GROWTH = 'personal_growth', 'توسعه فردی و مهارت‌های نرم'
    NETWORK_INFRASTRUCTURE = 'network_infrastructure', 'شبکه، امنیت و زیرساخت'
    AI_DATA = 'ai_data', 'هوش مصنوعی و علم داده'
    DESIGN_PRODUCT = 'design_product', 'طراحی محصول و تجربه کاربری'
    DEVOPS_CLOUD = 'devops_cloud', 'دواپس و رایانش ابری'
    GENERAL_COMMUNITY = 'general_community', 'گفتگو و جامعه آزاد'


class TweetStatusChoices(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


def compress_image(image_field, upload_prefix, max_size=(800, 800), quality=75):
    if not image_field:
        return image_field
    img = Image.open(image_field)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality)
    output.seek(0)
    return InMemoryUploadedFile(
        output,
        'ImageField',
        f"{upload_prefix}_{image_field.name.split('/')[-1].split('.')[0]}.jpg",
        'image/jpeg',
        sys.getsizeof(output),
        None
    )


class Group(models.Model):
    id = models.BigAutoField(primary_key=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_groups')
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=40, choices=GroupCategoryChoices.choices)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='groups/', blank=True, null=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='joined_groups', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if self.photo:
            self.photo = compress_image(self.photo, f"group_{self.name}")
        super().save(*args, **kwargs)
        if is_new and self.owner.role == RoleChoices.USER:
            self.owner.role = RoleChoices.WRITER
            self.owner.save(update_fields=['role'])

    def __str__(self):
        return f"{self.title} (@{self.name})"


class Topic(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='topics')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_topics')
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.group.title} -> {self.name}"


class Tweet(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tweets')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='tweets')
    status = models.CharField(
        max_length=15,
        choices=TweetStatusChoices.choices,
        default=TweetStatusChoices.APPROVED
    )
    description = models.TextField()
    stack_choice = models.CharField(max_length=50, choices=StackChoices.choices, blank=True)
    parent_tweet = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    retweet_of = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='retweets')
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def shamsi_date(self):
        try:
            import jdatetime
            months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
            local_time = timezone.localtime(self.created_at)
            jdate = jdatetime.datetime.fromgregorian(datetime=local_time)
            return f"{jdate.day} {months[jdate.month - 1]} {jdate.year} | {jdate.hour:02d}:{jdate.minute:02d}"
        except ImportError:
            local_time = timezone.localtime(self.created_at)
            return local_time.strftime("%Y/%m/%d | %H:%M")
        
    def save(self, *args, **kwargs):
        if not self.pk and self.topic is not None:
            if self.topic.group.owner_id != self.user_id:
                self.status = TweetStatusChoices.PENDING
            else:
                self.status = TweetStatusChoices.APPROVED
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Tweet by {self.user} - {self.id}"


class TweetImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tweets/')

    def save(self, *args, **kwargs):
        if self.image:
            self.image = compress_image(self.image, f"tweet_{self.tweet_id}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for Tweet #{self.tweet_id}"


class TweetLike(models.Model):
    id = models.BigAutoField(primary_key=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='liked_tweets')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tweet', 'user'], name='unique_tweet_like')
        ]

    def __str__(self):
        return f"{self.user} liked #{self.tweet_id}"