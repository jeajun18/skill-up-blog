from rest_framework import serializers
from posts.models import Post, Like, Comment, BoardType
from users.serializers import UserSerializer
from django.core.exceptions import ValidationError
from django.conf import settings


class PostSerializer(serializers.ModelSerializer):
    """게시글 조회를 위한 Serializer
    
    게시글 목록이나 상세 조회에 사용
    작성자 정보를 포함
    """
    # 작성자 정보를 중첩하여 표시 (UserSerializer 사용)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',           # 게시글 ID
            'title',        # 제목
            'content',      # 내용
            'author',       # 작성자 (중첩된 정보)
            'board_type',    # 추가
            'category',      # 추가
            'image',         # 추가
            'created_at',   # 작성일
            'updated_at'    # 수정일
        ]
        # 자동으로 설정되는 필드들은 읽기 전용
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """게시글 생성/수정을 위한 Serializer"""
    image = serializers.ImageField(required=False)
    
    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'board_type',
            'category',
            'image'
        ]
        extra_kwargs = {
            'category': {
                'required': False,
                'allow_null': True
            }
        }

    def validate(self, data):
        if data.get('board_type') == BoardType.TECH and not data.get('category'):
            raise ValidationError({
                'category': '기술 블로그 작성 시 카테고리 선택은 필수입니다.'
            })
        return data

    def validate_image(self, value):
        """이미지 파일 유효성 검사"""
        if value and value.size > settings.MAX_UPLOAD_SIZE:
            raise ValidationError(f'이미지 크기는 {settings.MAX_UPLOAD_SIZE/1024/1024}MB를 초과할 수 없습니다.')
        return value


class CommentSerializer(serializers.ModelSerializer):
    """댓글 Serializer
    
    댓글 정보를 직렬화/역직렬화합니다.
    작성자 정보를 포함하며, 대댓글 정보도 함께 제공합니다.
    """
    author = UserSerializer(read_only=True)  # 작성자 정보
    reply_count = serializers.IntegerField(read_only=True)  # 대댓글 수
    replies = serializers.SerializerMethodField()  # 대댓글 목록

    class Meta:
        model = Comment
        fields = [
            'id',           # 댓글 ID
            'post',         # 게시글 ID
            'author',       # 작성자 정보
            'content',      # 댓글 내용
            'parent',       # 부모 댓글 ID (대댓글인 경우)
            'reply_count',  # 대댓글 수
            'replies',      # 대댓글 목록
            'created_at',   # 작성일
            'updated_at'    # 수정일
        ]
        read_only_fields = [
            'id', 'author', 'reply_count', 
            'replies', 'created_at', 'updated_at'
        ]

    def get_reply_count(self, obj):
        """대댓글 수를 계산합니다."""
        return obj.replies.count()

    def get_replies(self, obj):
        """대댓글 목록을 가져옵니다."""
        # 첫 레벨 댓글인 경우에만 대댓글을 포함
        if obj.parent is None:
            replies = obj.replies.all()
            return CommentSerializer(replies, many=True).data
        return []


class PostDetailSerializer(serializers.ModelSerializer):
    """게시글 상세 정보 Serializer
    
    게시글의 상세 정보를 직렬화합니다.
    작성자 정보, 좋아요 수, HTML 변환된 내용을 포함합니다.
    """
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)  # 좋아요 수
    is_liked = serializers.SerializerMethodField()  # 현재 사용자의 좋아요 여부
    html_content = serializers.CharField(read_only=True)  # 마크다운 -> HTML
    comments = CommentSerializer(many=True, read_only=True)  # 댓글 목록

    class Meta:
        model = Post
        fields = [
            'id',           # 게시글 ID
            'title',        # 제목
            'content',      # 원본 내용
            'html_content', # HTML 변환된 내용
            'author',       # 작성자 정보
            'like_count',   # 좋아요 수
            'is_liked',     # 현재 사용자 좋아요 여부
            'comments',     # 댓글 목록
            'created_at',   # 작성일
            'updated_at'    # 수정일
        ]
        read_only_fields = [
            'id', 'author', 'like_count', 'is_liked',
            'html_content', 'comments', 'created_at', 'updated_at'
        ]

    def get_like_count(self, obj):
        """게시글의 좋아요 수를 계산합니다."""
        return obj.likes.count()

    def get_is_liked(self, obj):
        """현재 사용자의 좋아요 여부를 확인합니다."""
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.likes.filter(user=user).exists()
        return False