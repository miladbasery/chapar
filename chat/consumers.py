import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils.html import escape
from .models import ChatRoom, Message, Sticker, MessageTypeChoices

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"
        self.user = self.scope.get('user')

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        is_member = await self.check_participant(self.user.id, self.room_id)
        if not is_member:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('message_type', MessageTypeChoices.TEXT)
        text_content = data.get('text', '')
        sticker_id = data.get('sticker_id')

        sanitized_text = escape(text_content.strip()) if text_content else None

        msg_obj = await self.save_message(
            user_id=self.user.id,
            room_id=self.room_id,
            msg_type=message_type,
            text=sanitized_text,
            sticker_id=sticker_id
        )

        if msg_obj:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': msg_obj['id'],
                    'sender_id': str(self.user.id),
                    'sender_username': self.user.username,
                    'message_type': message_type,
                    'text': msg_obj['text'],
                    'image_url': msg_obj['image_url'],
                    'sticker_url': msg_obj['sticker_url'],
                    'created_at': msg_obj['created_at'],
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def check_participant(self, user_id, room_id):
        return ChatRoom.objects.filter(id=room_id, participants__id=user_id).exists()

    @database_sync_to_async
    def save_message(self, user_id, room_id, msg_type, text=None, sticker_id=None):
        try:
            room = ChatRoom.objects.get(id=room_id)
            user = User.objects.get(id=user_id)
            sticker = Sticker.objects.filter(id=sticker_id).first() if sticker_id else None

            if msg_type == MessageTypeChoices.TEXT and not text:
                return None
            if msg_type == MessageTypeChoices.STICKER and not sticker:
                return None

            msg = Message.objects.create(
                room=room,
                sender=user,
                message_type=msg_type,
                text=text,
                sticker=sticker
            )

            return {
                'id': msg.id,
                'text': msg.text,
                'image_url': msg.image.url if msg.image else None,
                'sticker_url': msg.sticker.image_file.url if msg.sticker else None,
                'created_at': msg.created_at.strftime('%H:%M')
            }
        except Exception:
            return None