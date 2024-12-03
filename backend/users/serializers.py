from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 직렬화"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_image', 'bio', 'created_at')
        read_only_fields = ('id', 'created_at')


class UserRegisterSerializer(serializers.ModelSerializer):
    """회원가입을 위한 Serializer"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    