from django.urls import path
from posts.views import (
    PostListCreateView, PostDetailView, PostLikeView,
    CommentListCreateView, CommentDetailView, PopularPostsView,
    TechPostListView, FreeBoardView, GuestBookView
)

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/popular/', PopularPostsView.as_view(), name='popular-posts'),
    path('posts/<int:pk>/like/', PostLikeView.as_view(), name='post-like'),
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('posts/tech/', TechPostListView.as_view(), name='tech-posts'),
    path('posts/free/', FreeBoardView.as_view(), name='free-board'),
    path('posts/guestbook/', GuestBookView.as_view(), name='guest-book'),
] 