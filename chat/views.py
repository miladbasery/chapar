from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import ChatRoom, Message, Sticker, ChatRoomTypeChoices
from .forms import DirectChatRoomCreationForm, MessageForm


class ChatRoomListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = 'chat/room_list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        return self.request.user.chat_rooms.prefetch_related('participants', 'messages').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DirectChatRoomCreationForm(user=self.request.user)
        return context


class ChatRoomDetailView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = 'chat/room_detail.html'
    context_object_name = 'room'
    pk_url_kwarg = 'room_id'

    def get_queryset(self):
        return self.request.user.chat_rooms.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat_messages'] = self.object.messages.select_related('sender', 'sticker').order_by('created_at')
        context['stickers'] = Sticker.objects.all()
        return context


class StartDirectChatView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = DirectChatRoomCreationForm(request.POST, user=request.user)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            room = ChatRoom.objects.filter(
                type=ChatRoomTypeChoices.DIRECT,
                participants=request.user
            ).filter(participants=recipient).first()

            if not room:
                room = ChatRoom.objects.create(type=ChatRoomTypeChoices.DIRECT)
                room.participants.add(request.user, recipient)

            return redirect('chat:room_detail', room_id=room.id)
        return redirect('chat:room_list')


class UploadChatImageView(LoginRequiredMixin, View):
    def post(self, request, room_id, *args, **kwargs):
        room = get_object_or_404(request.user.chat_rooms, id=room_id)
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.room = room
            msg.sender = request.user
            msg.save()
            return JsonResponse({
                'status': 'success',
                'image_url': msg.image.url if msg.image else None,
                'created_at': msg.created_at.strftime('%H:%M')
            })
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)