from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from users.serializers import UserSerializer, UserCreateSerializer
from users.services import UserService
from users.models import User

User = get_user_model()


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
    service = UserService()  # 추가
    
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            # create_user 메서드 사용
            user = self.service.create_user(**serializer.validated_data)
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)


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
    service = UserService()  # 비즈니스 로직을 처리할 서비스 클래스
    
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
        serializer.is_valid(raise_exception=True)
        try:
            # update_profile 메서드 사용
            user = self.service.update_profile(
                request.user,
                **serializer.validated_data
            )
            return Response(UserSerializer(user).data)
        except ValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)


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


class LoginView(TokenObtainPairView):
    """로그인 API View"""
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            # 토큰에서 user_id를 추출하여 사용자 정보 조회
            from rest_framework_simplejwt.tokens import AccessToken
            token = response.data['access']
            user_id = AccessToken(token)['user_id']
            user = User.objects.get(id=user_id)

            return Response({
                'token': {
                    'access': response.data['access'],
                    'refresh': response.data['refresh']
                },
                'user': UserSerializer(user).data
            }, status=response.status_code)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
