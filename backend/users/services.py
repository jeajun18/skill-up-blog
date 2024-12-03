from typing import List, Optional
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from core.base_service import BaseService
from users.models import User


class UserService(BaseService[User]):
    """사용자 관련 비즈니스 로직을 처리하는 서비스
    
    BaseService를 상속받아 기본적인 CRUD 작업을 수행하며,
    사용자 관련 추가 비즈니스 로직을 구현합니다.
    """
    model = User

    def get_by_email(self, email: str) -> User | None:
        """이메일로 사용자를 조회합니다.
        
        Args:
            email: 조회할 사용자의 이메일
            
        Returns:
            User: 찾은 경우 User 객체
            None: 찾지 못한 경우
        """
        return self.get(email=email)

    def get_by_username(self, username: str) -> User | None:
        """사용자 이름으로 사용자를 조회합니다.
        
        Args:
            username: 조회할 사용자의 이름
            
        Returns:
            User: 찾은 경우 User 객체
            None: 찾지 못한 경우
        """
        return self.get(username=username)

    def create_user(self, username: str, email: str, password: str, **extra_fields) -> User:
        """새로운 사용자를 생성합니다.
        
        비밀번호 유효성을 검사하고, 이메일/사용자명 중복을 확인합니다.
        """
        # 비밀번호 유효성 검사
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError({"password": e.messages})

        # 이메일 중복 확인
        if self.get_by_email(email):
            raise ValidationError({"email": "이미 사용 중인 이메일입니다."})

        # 사용자명 중복 확인
        if self.get_by_username(username):
            raise ValidationError({"username": "이미 사용 중인 사용자명입니다."})

        # 사용자 생성
        user = User(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def update_profile(
        self, 
        user: User, 
        bio: Optional[str] = None,
        profile_image: Optional[str] = None
    ) -> User:
        """사용자 프로필을 업데이트합니다."""
        if bio is not None:
            user.bio = bio
        if profile_image is not None:
            user.profile_image = profile_image
        user.save()
        return user

    def change_password(self, user: User, old_password: str, new_password: str) -> User:
        """사용자 비밀번호를 변경합니다."""
        if not user.check_password(old_password):
            raise ValidationError({"old_password": "현재 비밀번호가 일치하지 않습니다."})

        try:
            validate_password(new_password)
        except ValidationError as e:
            raise ValidationError({"new_password": e.messages})

        user.set_password(new_password)
        user.save()
        return user

    def get_active_users(self) -> List[User]:
        """활성 상태인 사용자 목록을 반환합니다."""
        return self.filter(is_active=True)
  