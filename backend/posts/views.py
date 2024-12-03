from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated, 
    IsAuthenticatedOrReadOnly,
    AllowAny
)

from posts.models import Comment
from posts.serializers import (
    PostSerializer, 
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    CommentSerializer
)
from posts.services import PostService


class PostListCreateView(APIView):
    """게시글 목록 조회 및 생성 API View
    
    게시글 목록을 조회하거나 새 게시글을 생성하는 엔드포인트를 제공합니다.
    목록 조회는 모든 사용자가 가능하지만, 생성은 인증된 사용자만 가능합니다.
    
    Endpoints:
        GET /api/v1/posts/ - 게시글 목록 조회
        POST /api/v1/posts/ - 새 게시글 생성
    
    Query Parameters (GET):
        page: int - 페이지 번호 (default: 1)
        size: int - 페이지 크기 (default: 10)
        
    Request Body (POST):
        title: str - 게시글 제목
        content: str - 게시글 내용
        
    Returns:
        GET - 200 OK: 게시글 목록
        POST - 201 Created: 생성된 게시글
        401 Unauthorized: 인증되지 않은 사용자 (POST 시)
        400 Bad Request: 유효하지 않은 데이터
    """
    permission_classes = [IsAuthenticatedOrReadOnly]  # GET은 모두 허용, POST는 인증 필요
    service = PostService()
    
    def get(self, request):
        """게시글 목록 조회
        최신순으로 정렬된 게시글 목록을 반환합니다.
        """
        query = request.query_params.get('search')
        if query:
            posts = self.service.search_posts(query)
        else:
            posts = self.service.get_recent_posts()
            
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """새 게시글 생성
        현재 로그인한 사용자를 작성자로 하여 게시글을 생성합니다.
        """
        serializer = PostCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            post = self.service.create_post(
                author=request.user,
                **serializer.validated_data
            )
            return Response(
                PostSerializer(post).data,
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    """게시글 상세 조회, 수정, 삭제 API View
    
    특정 게시글의 상세 정보를 조회하고, 수정하거나 삭제하는 엔드포인트를 제공합니다.
    조회는 모든 사용자가 가능하지만, 수정과 삭제는 작성자만 가능합니다.
    
    Endpoints:
        GET /api/v1/posts/<int:pk>/ - 게시글 상세 조회
        PUT /api/v1/posts/<int:pk>/ - 게시글 수정
        DELETE /api/v1/posts/<int:pk>/ - 게시글 삭제
        
    Path Parameters:
        pk: int - 게시글 ID
        
    Request Body (PUT):
        title: str - 게시글 제목
        content: str - 게시글 내용
        
    Returns:
        GET - 200 OK: 게시글 상세 정보
        PUT - 200 OK: 수정된 게시글 정보
        DELETE - 204 No Content: 삭제 성공
        404 Not Found: 게시글이 존재하지 않음
        403 Forbidden: 권한 없음 (다른 사용자의 게시글 수정/삭제 시도)
    """
    permission_classes = [IsAuthenticatedOrReadOnly]  # GET은 모두 허용, 나머지는 인증 필요
    service = PostService()
    
    def get(self, request, pk):
        """게시글 상세 조회"""
        post = self.service.get(id=pk)
        if not post:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(PostSerializer(post).data)
    
    def put(self, request, pk):
        """게시글 수정 (작성자만 가능)"""
        post = self.service.get(id=pk)
        if not post:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if post.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        serializer = PostCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_post = self.service.update(post, **serializer.validated_data)
        return Response(PostSerializer(updated_post).data)
    
    def delete(self, request, pk):
        """게시글 삭제 (작성자만 가능)"""
        post = self.service.get(id=pk)
        if not post:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if post.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        self.service.delete(post)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PopularPostsView(APIView):
    """인기 게시글 API View"""
    permission_classes = [AllowAny]
    service = PostService()

    def get(self, request):
        posts = self.service.get_popular_posts()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class PostLikeView(APIView):
    """게시글 좋아요 API View
    
    POST /api/v1/posts/<int:pk>/like/ - 좋아요 토글
    
    Returns:
        200 OK: {"liked": true/false} - true면 좋아요 생성, false면 취소
        404 Not Found: 게시글이 존재하지 않음
        400 Bad Request: 자신의 게시글에 좋아요 시도 등
    """
    permission_classes = [IsAuthenticated]
    service = PostService()
    
    def post(self, request, pk):
        post = self.service.get(id=pk)
        if not post:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        try:
            liked = self.service.toggle_like(post, request.user)
            return Response({"liked": liked})
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CommentListCreateView(APIView):
    """댓글 목록 조회 및 생성 API View
    
    GET /api/v1/posts/<int:post_id>/comments/ - 댓글 목록 조회
    POST /api/v1/posts/<int:post_id>/comments/ - 새 댓글 작성
    
    Request Body (POST):
        content: str - 댓글 내용
        parent_id: int (optional) - 부모 댓글 ID (대댓글인 경우)
        
    Returns:
        GET - 200 OK: 댓글 목록
        POST - 201 Created: 생성된 댓글
        404 Not Found: 게시글이 존재하지 않음
        400 Bad Request: 유효하지 않은 데이터
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    service = PostService()
    
    def get(self, request, post_id):
        post = self.service.get(id=post_id)
        if not post:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        # 최상위 댓글만 조회 (대댓글은 각 댓글 내에 포함)
        comments = post.comments.filter(parent=None)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def post(self, request, post_id):
        """새 댓글 작성"""
        print(f"Creating comment for post {post_id}")  # 디버그 로그
        print(f"Request data: {request.data}")  # 요청 데이터 확인
        
        post = self.service.get(id=post_id)
        if not post:
            print(f"Post {post_id} not found")  # 디버그 로��
            return Response(
                {"error": "게시글을 찾을 수 없습니다."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            comment = self.service.add_comment(
                post=post,
                author=request.user,
                content=request.data.get('content'),
                parent_id=request.data.get('parent_id')
            )
            return Response(
                CommentSerializer(comment).data,
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            print(f"Validation error: {e}")  # 디버그 로그
            return Response(
                {"error": str(e)} if isinstance(e, str) else e.message_dict,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"Unexpected error: {e}")  # 디버그 로그
            return Response(
                {"error": "댓글 작성 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CommentDetailView(APIView):
    """댓글 수정 및 삭제 API View
    
    PUT /api/v1/comments/<int:pk>/ - 댓글 수정
    DELETE /api/v1/comments/<int:pk>/ - 댓글 삭제
    
    Request Body (PUT):
        content: str - 수정할 내용
        
    Returns:
        PUT - 200 OK: 수정된 댓글
        DELETE - 204 No Content: 삭제 성공
        404 Not Found: 댓글이 존재하지 않음
        403 Forbidden: 권한 없음
    """
    permission_classes = [IsAuthenticated]
    service = PostService()
    
    def put(self, request, pk):
        comment = Comment.objects.filter(id=pk).first()
        if not comment:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        try:
            updated_comment = self.service.update_comment(
                comment=comment,
                author=request.user,
                content=request.data.get('content')
            )
            return Response(CommentSerializer(updated_comment).data)
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
    
    def delete(self, request, pk):
        comment = Comment.objects.filter(id=pk).first()
        if not comment:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        try:
            self.service.delete_comment(comment, request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class TechPostListView(APIView):
    """기술 블로그 목록"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    service = PostService()

    def get(self, request):
        category = request.query_params.get('category')
        posts = self.service.get_tech_posts(category)
        return Response(PostSerializer(posts, many=True).data)


class FreeBoardView(APIView):
    """자유게시판"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    service = PostService()

    def get(self, request):
        posts = self.service.get_free_posts()
        return Response(PostSerializer(posts, many=True).data)


class GuestBookView(APIView):
    """방명록"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    service = PostService()

    def get(self, request):
        posts = self.service.get_guest_posts()
        return Response(PostSerializer(posts, many=True).data)
