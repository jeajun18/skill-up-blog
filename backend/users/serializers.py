from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """일반적인 사용자 정보를 직렬화하는 Serializer
    
    주로 사용자 정보 조회, 프로필 표시 등에 사용
    비밀번호는 포함하지 않음
    """
    class Meta:
        model = User
        fields = [
            'id',           # 사용자 고유 ID
            'username',     # 사용자 이름
            'email',        # 이메일
            'profile_image',   # 프로필 이미지
            'bio',          # 자기소개
            'created_at'    # 계정 생성일
        ]
        read_only_fields = ['id', 'created_at']  # 수정 불가능한 필드


class UserCreateSerializer(serializers.ModelSerializer):
    """회원가입을 위한 Serializer
    
    비밀번호를 안전하게 처리하며, 새로운 사용자 생성에 사용
    """
    # write_only=True로 설정하여 비밀번호가 응답에 포함되지 않도록 함
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id',           # 사용자 고유 ID
            'username',     # 사용자 이름
            'email',        # 이메일
            'password',     # 비밀번호 (write_only)
            'profile_image',   # 프로필 이미지
            'bio'           # 자기소개
        ]
        read_only_fields = ['id']  # 자동 생성되는 ID는 읽기 전용

    def create(self, validated_data):
        """비밀번호를 암호화하여 새로운 사용자를 생성"""
        password = validated_data.pop('password')  # 비밀번호 분리
        user = User(**validated_data)  # 나머지 데이터로 사용자 인스턴스 생성
        user.set_password(password)    # 비밀번호 암호화하여 설정
        user.save()
        return user
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    