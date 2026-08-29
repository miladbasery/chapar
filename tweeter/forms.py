import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import escape
from accounts.models import RoleChoices
from .models import Group, Topic, Tweet, TweetImage


def sanitize_text(text, max_len=None):
    if not text:
        return text
    text = str(text).strip()
    if max_len and len(text) > max_len:
        raise ValidationError(f"تعداد کاراکتر مجاز نیست. (حداکثر {max_len} حرف)")
    return escape(text)


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('title', 'name', 'category', 'description', 'photo')

    def clean_title(self):
        return sanitize_text(self.cleaned_data.get('title'), max_len=100)

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not re.match(r'^[a-zA-Z0-9_]+$', name):
            raise ValidationError("شناسه یکتا فقط می‌تواند شامل حروف انگلیسی، اعداد و زیرخط باشد.")
        if len(name) > 30:
            raise ValidationError("شناسه یکتا نمی‌تواند بیشتر از ۳۰ کاراکتر باشد.")
        return name.lower()

    def clean_description(self):
        return sanitize_text(self.cleaned_data.get('description'), max_len=500)


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        return sanitize_text(self.cleaned_data.get('name'), max_len=80)

    def clean(self):
        cleaned_data = super().clean()
        if self.group and self.user:
            if self.group.owner != self.user and self.user.role != RoleChoices.ADMIN:
                raise ValidationError("فقط مالک انجمن یا ادمین مجاز به ایجاد یا ویرایش تاپیک در این انجمن است.")
        return cleaned_data

    def save(self, commit=True):
        topic = super().save(commit=False)
        if self.group:
            topic.group = self.group
        if self.user:
            topic.created_by = self.user
        if commit:
            topic.save()
        return topic


class TweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ('topic', 'description', 'stack_choice')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['topic'].required = False
        self.fields['stack_choice'].required = False

    def clean_description(self):
        return sanitize_text(self.cleaned_data.get('description'), max_len=1000)


class TweetImageForm(forms.ModelForm):
    class Meta:
        model = TweetImage
        fields = ('image',)


class TweetModerationForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ('status',)