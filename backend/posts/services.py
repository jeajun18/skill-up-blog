from typing import List, Optional
from django.core.exceptions import ValidationError
from django.db.models import Q

from core.base_service import BaseService
from posts.models import Post, Like, Comment, BoardType
from users.models import User


class PostService(BaseService[Post]):
    """게시글 관련 비즈니스 로직을 처리하는 서비스
    
    BaseService를 상속받아 기본적인 CRUD 작업을 수행하며,
    게시글 관련 추가 비즈니스 로직을 구현합니다.
    """
    model = Post

    def get_user_posts(self, user: User) -> List[Post]:
        """특정 사용자가 작성한 게시글 목록을 조회합니다.
        
        Args:
            user: 게시글을 조회할 사용자
            
        Returns:
            List[Post]: 해당 사용자가 작성한 게시글 목록
        """
        return self.filter(author=user)

    def get_recent_posts(self, limit: int = 10) -> List[Post]:
        """최근 게시글 목록을 조회합니다.
        
        Args:
            limit: 조회할 게시글 수 (기본값: 10)
            
        Returns:
            List[Post]: 최근 게시글 목록
        """
        return self.get_queryset().order_by('-created_at')[:limit]

    def create_post(
        self, 
        author: User, 
        title: str, 
        content: str,
        **extra_fields
    ) -> Post:
        """새 게시글을 생성합니다."""
        # 제목 길이 검증
        if len(title) < 2:
            raise ValidationError({"title": "제목은 최소 2자 이상이어야 합니다."})
        
        # 내용 길이 검증 (방명록은 제외)
        board_type = extra_fields.get('board_type', BoardType.FREE)
        if board_type != BoardType.GUEST and len(content) < 10:
            raise ValidationError({"content": "내용은 최소 10자 이상이어야 합니다."})

        return self.create(
            author=author,
            title=title,
            content=content,
            **extra_fields
        )

    def search_posts(self, query: str) -> List[Post]:
        """게시글을 검색합니다."""
        return self.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    def get_posts_by_date_range(
        self, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Post]:
        """특정 기간의 게시글을 조회합니다."""
        queryset = self.get_queryset()
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        return queryset

    def get_popular_posts(self, days: int = 7, limit: int = 10) -> List[Post]:
        """인기 게시글을 조회합니다.
        (나중에 좋아요/조회수 기능 추가 시 구현)
        """
        # TODO: 좋아요/조회수 기준으로 수정
        return self.get_recent_posts(limit)

    def toggle_like(self, post: Post, user: User) -> bool:
        """게시글 좋아요 토글
        
        Args:
            post: 좋아요/취소할 게시글
            user: 요청한 사용자
            
        Returns:
            bool: True면 좋아요 생성, False면 좋아요 취소
            
        Raises:
            ValidationError: 자신의 게시글에 좋아요를 시도할 경우
        """
        if post.author == user:
            raise ValidationError("자신의 게시글에는 좋아요할 수 없습니다.")
            
        like, created = Like.objects.get_or_create(
            post=post,
            user=user,
            defaults={'post': post, 'user': user}
        )
        
        if not created:  # 이미 좋아요가 있으면 취소
            like.delete()
            
        return created

    def add_comment(
        self, 
        post: Post,
        author: User,
        content: str,
        parent_id: Optional[int] = None
    ) -> Comment:
        """댓글 작성
        
        Args:
            post: 댓글을 작성할 게시글
            author: 댓글 작성자
            content: 댓글 내용
            parent_id: 부모 댓글 ID (대댓글인 경우)
            
        Returns:
            Comment: 생성된 댓글
            
        Raises:
            ValidationError: 댓글 내용이 비어있거나, 부모 댓글이 존재하지 않는 경우
        """
        if not content.strip():
            raise ValidationError({"content": "댓글 내용을 입력해주세요."})

        # 대댓글인 경우 부모 댓글 확인
        parent = None
        if parent_id:
            parent = Comment.objects.filter(id=parent_id, post=post).first()
            if not parent:
                raise ValidationError({"parent": "존재하지 않는 댓글입니다."})
            if parent.parent:  # 대댓글의 대댓글 방지
                raise ValidationError({"parent": "대댓글에는 답글을 달 수 없습니다."})

        return Comment.objects.create(
            post=post,
            author=author,
            content=content,
            parent=parent
        )

    def update_comment(
        self,
        comment: Comment,
        author: User,
        content: str
    ) -> Comment:
        """댓글 수정
        
        Args:
            comment: 수정할 댓글
            author: 수정 요청한 사용자
            content: 수정할 내용
            
        Returns:
            Comment: 수정된 댓글
            
        Raises:
            ValidationError: 권한이 없거나 내용이 비어있는 경우
        """
        if comment.author != author:
            raise ValidationError("댓글 작성자만 수정할 수 있습니다.")
            
        if not content.strip():
            raise ValidationError({"content": "댓글 내용을 입력해주세요."})
            
        comment.content = content
        comment.save()
        return comment

    def delete_comment(self, comment: Comment, author: User) -> None:
        """댓글 삭제
        
        Args:
            comment: 삭제할 댓글
            author: 삭제 요청한 사용자
            
        Raises:
            ValidationError: 권한이 없는 경우
        """
        if comment.author != author:
            raise ValidationError("댓글 작성자만 삭제할 수 있습니다.")
            
        comment.delete()

    def get_tech_posts(self, category=None):
        """기술 블로그 글 목록"""
        queryset = self.filter(board_type=BoardType.TECH)
        if category:
            queryset = queryset.filter(category=category)
        return queryset.order_by('-created_at')
    
    def get_free_posts(self):
        """자유게시판 글 목록"""
        return self.filter(
            board_type=BoardType.FREE
        ).order_by('-created_at')
    
    def get_guest_posts(self):
        """방명록 목록"""
        return self.filter(
            board_type=BoardType.GUEST
        ).order_by('-created_at')
  