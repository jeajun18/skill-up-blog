from rest_framework.permissions import BasePermission, SAFE_METHODS
from posts.models import BoardType

class BoardTypePermission(BasePermission):
    """게시판 유형별 권한 설정"""
    
    def has_permission(self, request, view):
        # GET 요청은 모두 허용
        if request.method in SAFE_METHODS:
            return True
            
        # POST 요청일 때 게시판별 권한 체크
        if request.method == 'POST':
            board_type = request.data.get('board_type')
            
            # 기술 블로그는 관리자만 작성 가능
            if board_type == BoardType.TECH:
                return request.user.is_staff
                
            # 방명록은 모든 사용자 작성 가능
            if board_type == BoardType.GUEST:
                return True
                
            # 자유게시판은 로그인한 사용자만 작성 가능
            return request.user.is_authenticated
            
        return True 