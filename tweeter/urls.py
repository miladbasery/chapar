from django.urls import path
from . import views

urlpatterns = [
    path('', views.TweetFeedView.as_view(), name='tweet_feed'),

    path('groups/', views.GroupListView.as_view(), name='group_list'),
    path('groups/<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('groups/create/', views.GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/edit/', views.GroupUpdateView.as_view(), name='group_edit'),
    path('groups/<int:pk>/delete/', views.GroupDeleteView.as_view(), name='group_delete'),

    path('topics/<int:pk>/', views.TopicDetailView.as_view(), name='topic_detail'),
    path('groups/<int:group_id>/topics/create/', views.TopicCreateView.as_view(), name='topic_create'),
    path('topics/<int:pk>/edit/', views.TopicUpdateView.as_view(), name='topic_edit'),
    path('topics/<int:pk>/delete/', views.TopicDeleteView.as_view(), name='topic_delete'),

    path('tweet/<int:pk>/', views.TweetDetailView.as_view(), name='tweet_detail'),
    path('tweet/create/', views.TweetCreateView.as_view(), name='tweet_create'),
    path('topics/<int:topic_id>/tweet/create/', views.TweetCreateView.as_view(), name='topic_tweet_create'),
    path('tweet/<int:parent_id>/reply/', views.TweetCreateView.as_view(), name='tweet_reply_create'),
    
    path('tweet/<int:pk>/edit/', views.TweetUpdateView.as_view(), name='tweet_edit'),
    path('tweet/<int:pk>/delete/', views.TweetDeleteView.as_view(), name='tweet_delete'),
    path('tweet/<int:pk>/like/', views.TweetLikeToggleView.as_view(), name='tweet_like_toggle'),

    path('groups/<int:group_id>/moderation/', views.PendingTweetsModerationView.as_view(), name='group_moderation'),
    path('tweet/<int:pk>/status/', views.TweetStatusUpdateView.as_view(), name='tweet_status_update'),
]