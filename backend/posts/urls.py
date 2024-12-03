from django.urls import path
from posts.views import (
    PostListCreateView, PostDetailView, PostLikeView,
    CommentListCreateView, CommentDetailView, PopularPostsView,
    TechPostListView, FreeBoardView, GuestBookView
)

urlpatterns = [
    # 게시글 관련 URL
    path('', PostListCreateView.as_view(), name='post-list'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('popular/', PopularPostsView.as_view(), name='popular-posts'),
    path('<int:pk>/like/', PostLikeView.as_view(), name='post-like'),
    
    # 댓글 관련 URL
    path('<int:post_id>/comments/', CommentListCreateView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    
    # 기존 URL들...
    path('tech/', TechPostListView.as_view(), name='tech-posts'),
    path('free/', FreeBoardView.as_view(), name='free-board'),
    path('guestbook/', GuestBookView.as_view(), name='guest-book'),
] 