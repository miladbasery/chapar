from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.ChatRoomListView.as_view(), name='room_list'),
    path('start/', views.StartDirectChatView.as_view(), name='start_direct'),
    path('<uuid:room_id>/', views.ChatRoomDetailView.as_view(), name='room_detail'),
    path('<uuid:room_id>/upload-image/', views.UploadChatImageView.as_view(), name='upload_image'),
]