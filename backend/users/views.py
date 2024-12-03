from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import UserSerializer, UserRegisterSerializer
from users.models import User
from users.services import UserService


class UserRegisterView(APIView):
    """회원가입 API View
    
    새로운 사용자를 생성하는 엔드포인트를 제공합니다.
    누구나 접근 가능합니다. (인증 불필요)
    
    Endpoint:
        POST /api/v1/users/register/
        
    Request Body:
        username: str - 사용자 이름
        email: str - 이메일
        password: str - 비밀번호
        profile_image: file (optional) - 프로필 이미지
        bio: str (optional) - 자기소개
    
    Returns:
        201 Created - 회원가입 성공
        400 Bad Request - 유효하지 않은 데이터
    """
    permission_classes = [AllowAny]  # 인증되지 않은 사용자도 접근 가능
    
    def post(self, request):
        try:
            serializer = UserRegisterSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                return Response(
                    UserSerializer(user).data,
                    status=status.HTTP_201_CREATED
                )
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileView(APIView):
    """사용자 프로필 API View
    
    인증된 사용자의 프로필 정보를 조회하고 수정하는 엔드포인트를 제공합니다.
    인증된 사용자만 접근 가능합니다.
    
    Endpoints:
        GET /api/v1/users/me/ - 내 프로필 정보 조회
        PUT /api/v1/users/me/ - 내 프로필 정보 수정
    
    Request Body (PUT):
        username: str (optional) - 사용자 이름
        email: str (optional) - 이메일
        profile_image: file (optional) - 프로필 이미지
        bio: str (optional) - 자기소개
        
    Returns:
        200 OK - 요청 성공
        401 Unauthorized - 인증되지 않은 사용자
        400 Bad Request - 유효하지 않은 데이터
    """
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능
    
    def get(self, request):
        """현재 로그인한 사용자의 프로필 정보를 조회"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """현재 로그인한 사용자의 프로필 정보를 수정
        
        partial=True 설정으로 일부 필드만 업데이트 가능
        """
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True  # 부분 업데이트 허용
        )
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """비밀번호 변경 API View"""
    permission_classes = [IsAuthenticated]
    service = UserService()

    def post(self, request):
        try:
            self.service.change_password(
                request.user,
                old_password=request.data.get('old_password'),
                new_password=request.data.get('new_password')
            )
            return Response({"message": "비밀번호가 변경되었습니다."})
        except ValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError({
                'detail': '이메일과 비밀번호를 모두 입력해주세요.'
            })

        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                raise serializers.ValidationError({
                    'detail': '이메일 또는 비밀번호가 올바르지 않습니다.'
                })

            refresh = RefreshToken.for_user(user)
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }

        except User.DoesNotExist:
            raise serializers.ValidationError({
                'detail': '이메일 또는 비밀번호가 올바르지 않습니다.'
            })


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
