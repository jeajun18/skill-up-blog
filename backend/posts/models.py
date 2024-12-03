from django.db import models
from django.conf import settings
import markdown
from django.utils.html import escape


class BoardType(models.TextChoices):
    """게시판 종류"""
    TECH = 'tech', '기술 블로그'
    FREE = 'free', '자유 게시판'
    GUEST = 'guest', '방명록'


class ProgrammingLanguage(models.TextChoices):
    """프로그래밍 언어 카테고리"""
    PYTHON = 'python', 'Python'
    JAVASCRIPT = 'javascript', 'JavaScript'
    JAVA = 'java', 'Java'
    CPP = 'cpp', 'C++'
    GO = 'go', 'Go'
    RUST = 'rust', 'Rust'
    OTHER = 'other', '기타'


class Post(models.Model):
    """Blog Post Model"""

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    board_type = models.CharField(
        max_length=10,
        choices=BoardType.choices,
        default=BoardType.FREE
    )
    category = models.CharField(
        max_length=20,
        choices=ProgrammingLanguage.choices,
        null=True,
        blank=True,  # 자유게시판/방명록은 카테고리 선택 불필요
        help_text='기술 블로그 작성 시 필수 선택'
    )
    image = models.ImageField(
        upload_to='posts/%Y/%m/%d/',
        null=True,
        blank=True
    )
    views = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "posts"
        ordering = ["-created_at"]

    @property
    def html_content(self):
        """마크다운 내용을 HTML로 변환"""
        return markdown.markdown(
            escape(self.content),
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.tables',
                'markdown.extensions.codehilite'
            ]
        )

    def increase_views(self):
        """조회수 증가"""
        self.views = models.F('views') + 1
        self.save(update_fields=['views'])


class Like(models.Model):
    """게시글 좋아요 모델"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='liked_posts'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'likes'
        unique_together = ['post', 'user']  # 한 사용자가 한 게시글에 한 번만 좋아요 가능


class Comment(models.Model):
    """댓글 모델"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
