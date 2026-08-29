import sys
import uuid
from io import BytesIO
from PIL import Image

from django.db import models
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile


class ChatRoomTypeChoices(models.TextChoices):
    DIRECT = 'direct', 'Direct'
    GROUP = 'group', 'Group'


class MessageTypeChoices(models.TextChoices):
    TEXT = 'text', 'Text'
    IMAGE = 'image', 'Image'
    STICKER = 'sticker', 'Sticker'


def compress_chat_image(image_field, upload_prefix, max_size=(1000, 1000), quality=75):
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


class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(
        max_length=10,
        choices=ChatRoomTypeChoices.choices,
        default=ChatRoomTypeChoices.DIRECT
    )
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatRoom ({self.type}) - {self.id}"


class Sticker(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    image_file = models.FileField(upload_to='stickers/')

    def __str__(self):
        return self.title


class Message(models.Model):
    id = models.BigAutoField(primary_key=True)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(
        max_length=10,
        choices=MessageTypeChoices.choices,
        default=MessageTypeChoices.TEXT
    )
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    sticker = models.ForeignKey(Sticker, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        if self.image:
            self.image = compress_chat_image(self.image, f"chat_{self.room_id}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender} -> {self.room_id}: {self.message_type}"