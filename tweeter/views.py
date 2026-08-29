from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib import messages
from django.core.cache import cache

from .models import Group, Topic, Tweet, TweetImage, TweetLike, TweetStatusChoices
from .forms import GroupForm, TopicForm, TweetForm, TweetImageForm, TweetModerationForm

MAX_TWEET_IMAGES = 5

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def increment_tweet_views(request, tweets):
    ip = get_client_ip(request)
    for tweet in tweets:
        cache_key = f"tweet_view_{tweet.id}_{ip}"
        if not cache.get(cache_key):
            tweet.views_count += 1
            tweet.save(update_fields=['views_count'])
            cache.set(cache_key, True, 60 * 60 * 6)


class NoTemplateActionMixin:
    def get(self, request, *args, **kwargs):
        return redirect(self.get_success_url())

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', '/')

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return redirect(self.get_success_url())


class GroupListView(ListView):
    model = Group
    template_name = 'tweeter/group_list.html'
    context_object_name = 'groups'
    ordering = ['-created_at']


class GroupDetailView(DetailView):
    model = Group
    template_name = 'tweeter/group_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topics'] = self.object.topics.all().order_by('-created_at')
        return context


class GroupCreateView(LoginRequiredMixin, NoTemplateActionMixin, CreateView):
    model = Group
    form_class = GroupForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "انجمن با موفقیت ساخته شد.")
        return super().form_valid(form)


class GroupUpdateView(LoginRequiredMixin, UserPassesTestMixin, NoTemplateActionMixin, UpdateView):
    model = Group
    form_class = GroupForm

    def test_func(self):
        group = self.get_object()
        return group.owner == self.request.user or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, "انجمن با موفقیت ویرایش شد.")
        return super().form_valid(form)


class GroupDeleteView(LoginRequiredMixin, UserPassesTestMixin, NoTemplateActionMixin, DeleteView):
    model = Group

    def test_func(self):
        group = self.get_object()
        return group.owner == self.request.user or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, "انجمن حذف شد.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('group_list')


class TopicDetailView(DetailView):
    model = Topic
    template_name = 'tweeter/topic_detail.html'
    context_object_name = 'topic'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tweets = Tweet.objects.filter(
            topic=self.object,
            status=TweetStatusChoices.APPROVED
        ).select_related('user', 'user__profile').prefetch_related('images', 'likes', 'retweets').order_by('-created_at')
        increment_tweet_views(self.request, tweets)
        context['tweets'] = tweets
        return context


class TopicCreateView(LoginRequiredMixin, NoTemplateActionMixin, CreateView):
    model = Topic
    form_class = TopicForm

    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(Group, pk=self.kwargs.get('group_id'))
        if self.group.owner != request.user and not request.user.is_staff:
            messages.error(request, "شما اجازه ساخت تاپیک در این انجمن را ندارید.")
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['group'] = self.group
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "تاپیک با موفقیت ایجاد شد.")
        return super().form_valid(form)


class TopicUpdateView(LoginRequiredMixin, UserPassesTestMixin, NoTemplateActionMixin, UpdateView):
    model = Topic
    form_class = TopicForm

    def test_func(self):
        topic = self.get_object()
        return topic.group.owner == self.request.user or self.request.user.is_staff

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['group'] = self.get_object().group
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "تاپیک ویرایش شد.")
        return super().form_valid(form)


class TopicDeleteView(LoginRequiredMixin, UserPassesTestMixin, NoTemplateActionMixin, DeleteView):
    model = Topic

    def test_func(self):
        topic = self.get_object()
        return topic.group.owner == self.request.user or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, "تاپیک حذف شد.")
        return super().form_valid(form)

    def get_success_url(self):
        topic = self.get_object()
        return reverse('group_detail', kwargs={'pk': topic.group.pk})


class TweetFeedView(ListView):
    model = Tweet
    template_name = 'tweeter/tweet_feed.html'
    context_object_name = 'tweets'
    paginate_by = 20

    def get_queryset(self):
        return Tweet.objects.filter(
            status=TweetStatusChoices.APPROVED,
            parent_tweet__isnull=True
        ).select_related('user', 'user__profile', 'topic', 'topic__group', 'retweet_of', 'retweet_of__user', 'retweet_of__user__profile').prefetch_related('images', 'likes', 'retweets').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_tweets = context.get('tweets', [])
        increment_tweet_views(self.request, page_tweets)
        context['latest_groups'] = Group.objects.all().order_by('-created_at')[:6]
        context['popular_topics'] = Topic.objects.all().order_by('-created_at')[:8]
        return context


class TweetDetailView(DetailView):
    model = Tweet
    template_name = 'tweeter/tweet_detail.html'
    context_object_name = 'tweet'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        increment_tweet_views(self.request, [obj])
        return obj

    def get_queryset(self):
        return Tweet.objects.select_related('user', 'user__profile', 'topic', 'retweet_of', 'retweet_of__user').prefetch_related('images', 'likes', 'retweets')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        replies = self.object.replies.filter(
            status=TweetStatusChoices.APPROVED
        ).select_related('user', 'user__profile', 'retweet_of', 'retweet_of__user').prefetch_related('images', 'likes', 'retweets').order_by('created_at')
        increment_tweet_views(self.request, replies)
        context['replies'] = replies
        return context


class TweetCreateView(LoginRequiredMixin, NoTemplateActionMixin, CreateView):
    model = Tweet
    form_class = TweetForm

    def form_valid(self, form):
        form.instance.user = self.request.user

        topic_id = self.request.POST.get('topic_id') or self.kwargs.get('topic_id')
        if topic_id:
            form.instance.topic_id = topic_id

        parent_id = self.kwargs.get('parent_id')
        if parent_id:
            form.instance.parent_tweet_id = parent_id

        retweet_of_id = self.request.POST.get('retweet_of_id')
        if retweet_of_id:
            form.instance.retweet_of_id = retweet_of_id

        response = super().form_valid(form)

        images = self.request.FILES.getlist('images')
        if not images:
            single = self.request.FILES.get('image')
            if single:
                images = [single]

        for image in images[:MAX_TWEET_IMAGES]:
            TweetImage.objects.create(tweet=self.object, image=image)

        if self.object.status == TweetStatusChoices.PENDING:
            messages.warning(self.request, "توییت شما ثبت شد و پس از تایید مدیر انجمن نمایش داده می‌شود.")
        else:
            messages.success(self.request, "توییت شما با موفقیت منتشر شد.")

        return response


class TweetUpdateView(LoginRequiredMixin, UserPassesTestMixin, NoTemplateActionMixin, UpdateView):
    model = Tweet
    form_class = TweetForm

    def test_func(self):
        tweet = self.get_object()
        return tweet.user == self.request.user or self.request.user.is_staff

    def form_valid(self, form):
        response = super().form_valid(form)
        
        delete_images_ids = self.request.POST.getlist('delete_images')
        if delete_images_ids:
            TweetImage.objects.filter(id__in=delete_images_ids, tweet=self.object).delete()
            
        new_images = self.request.FILES.getlist('new_images')
        current_count = self.object.images.count()
        
        for image in new_images:
            if current_count < MAX_TWEET_IMAGES:
                TweetImage.objects.create(tweet=self.object, image=image)
                current_count += 1
            else:
                break

        messages.success(self.request, "توییت با موفقیت ویرایش شد.")
        return response


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, NoTemplateActionMixin, DeleteView):
    model = Tweet

    def test_func(self):
        tweet = self.get_object()
        return tweet.user == self.request.user or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, "توییت با موفقیت حذف شد.")
        return super().form_valid(form)


class TweetLikeToggleView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        tweet = get_object_or_404(Tweet, pk=pk)
        like_qs = TweetLike.objects.filter(tweet=tweet, user=request.user)
        if like_qs.exists():
            like_qs.delete()
        else:
            TweetLike.objects.create(tweet=tweet, user=request.user)
        return redirect(request.META.get('HTTP_REFERER', reverse('tweet_feed')))


class PendingTweetsModerationView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'tweeter/moderation_list.html'
    context_object_name = 'pending_tweets'

    def test_func(self):
        self.group = get_object_or_404(Group, pk=self.kwargs.get('group_id'))
        return self.group.owner == self.request.user or self.request.user.is_staff

    def get_queryset(self):
        return Tweet.objects.filter(
            topic__group=self.group,
            status=TweetStatusChoices.PENDING
        ).select_related('user', 'topic').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        return context


class TweetStatusUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        self.tweet = get_object_or_404(Tweet, pk=self.kwargs.get('pk'))
        return (
            (self.tweet.topic and self.tweet.topic.group.owner == self.request.user)
            or self.request.user.is_staff
        )

    def post(self, request, pk, *args, **kwargs):
        new_status = request.POST.get('status')
        if new_status in TweetStatusChoices.values:
            self.tweet.status = new_status
            self.tweet.save(update_fields=['status'])
            messages.success(request, "وضعیت توییت بروزرسانی شد.")
        return redirect(request.META.get('HTTP_REFERER', '/'))