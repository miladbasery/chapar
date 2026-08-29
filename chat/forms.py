from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, Sticker, MessageTypeChoices


def sanitize_chat_text(text, max_len=2000):
    if not text:
        return text
    text = str(text).strip()
    if len(text) > max_len:
        raise ValidationError(f"متن پیام نمی‌تواند بیشتر از {max_len} کاراکتر باشد.")
    return escape(text)


class DirectChatRoomCreationForm(forms.Form):
    recipient = forms.ModelChoiceField(
        queryset=None,
        required=True,
        empty_label="انتخاب مخاطب"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        User = get_user_model()
        if user:
            self.fields['recipient'].queryset = User.objects.filter(is_active=True, is_deleted=False).exclude(pk=user.pk)


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('message_type', 'text', 'image', 'sticker')

    def clean_text(self):
        return sanitize_chat_text(self.cleaned_data.get('text'))

    def clean(self):
        cleaned_data = super().clean()
        msg_type = cleaned_data.get('message_type')
        text = cleaned_data.get('text')
        image = cleaned_data.get('image')
        sticker = cleaned_data.get('sticker')

        if msg_type == MessageTypeChoices.TEXT:
            if not text:
                raise ValidationError("متن پیام نمی‌تواند خالی باشد.")
        elif msg_type == MessageTypeChoices.IMAGE:
            if not image:
                raise ValidationError("لطفاً تصویر مورد نظر را بارگذاری کنید.")
        elif msg_type == MessageTypeChoices.STICKER:
            if not sticker:
                raise ValidationError("لطفاً یک استیکر انتخاب کنید.")

        return cleaned_data


class StickerForm(forms.ModelForm):
    class Meta:
        model = Sticker
        fields = ('title', 'image_file')

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title) > 100:
            raise ValidationError("عنوان استیکر نمی‌تواند بیشتر از ۱۰۰ کاراکتر باشد.")
        return escape(title)