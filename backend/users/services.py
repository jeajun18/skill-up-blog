from django.core.exceptions import ValidationError
from users.models import User

class UserService:
    @staticmethod
    def change_password(user, old_password, new_password):
        """사용자 비밀번호 변경"""
        if not user.check_password(old_password):
            raise ValidationError({'old_password': '현재 비밀번호가 일치하지 않습니다.'})
        
        user.set_password(new_password)
        user.save()
        return user
  