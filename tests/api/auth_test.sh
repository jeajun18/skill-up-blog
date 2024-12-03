#!/bin/bash

# 기본 설정
API_URL="http://localhost:8000/api/v1"
CONTENT_TYPE="Content-Type: application/json"

# 색상 설정
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 회원가입 테스트
echo "Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/users/register/" \
-H "${CONTENT_TYPE}" \
-d '{
    "username": "testuser_'$(date +%s)'",
    "email": "test_'$(date +%s)'@example.com",
    "password": "Test123!@#",
    "bio": "Hello, I am a test user"
}')

if [[ $REGISTER_RESPONSE == *"id"* ]]; then
    echo -e "${GREEN}✓ Registration successful${NC}"
    echo $REGISTER_RESPONSE | jq '.'
    
    # Django 관리자 권한 부여
    USER_ID=$(echo $REGISTER_RESPONSE | jq -r '.id')
    docker compose exec -T backend python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
user = User.objects.get(id=$USER_ID);
user.is_staff = True;
user.save()
"
    echo -e "${GREEN}✓ Admin privileges granted${NC}"
else
    echo -e "${RED}✗ Registration failed${NC}"
    echo $REGISTER_RESPONSE | jq '.'
fi

# 로그인 테스트
echo -e "\nTesting login..."
USERNAME=$(echo $REGISTER_RESPONSE | jq -r '.username')
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/users/login/" \
-H "${CONTENT_TYPE}" \
-d '{
    "username": "'$USERNAME'",
    "password": "Test123!@#"
}')

if [[ $LOGIN_RESPONSE == *"token"* ]]; then
    echo -e "${GREEN}✓ Login successful${NC}"
    echo $LOGIN_RESPONSE | jq '.'
    
    # 토큰 저장 (jq 사용)
    mkdir -p tests/api
    echo $LOGIN_RESPONSE | jq -r '.token.access' > tests/api/token.txt
    
    # 토큰 확인
    TOKEN_SAVED=$(cat tests/api/token.txt)
    if [ ! -z "$TOKEN_SAVED" ]; then
        echo -e "${GREEN}✓ Token saved successfully${NC}"
    else
        echo -e "${RED}✗ Failed to save token${NC}"
    fi
else
    echo -e "${RED}✗ Login failed${NC}"
    echo $LOGIN_RESPONSE | jq '.'
fi 