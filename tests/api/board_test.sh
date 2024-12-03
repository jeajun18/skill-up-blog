#!/bin/bash

# 기본 설정
API_URL="http://localhost:8000/api/v1"
CONTENT_TYPE="Content-Type: application/json"

# 색상 설정
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 토큰 확인
if [ ! -f tests/api/token.txt ]; then
    echo -e "${RED}✗ Token not found. Please run auth_test.sh first${NC}"
    exit 1
fi

AUTH_TOKEN=$(cat tests/api/token.txt)

# 1. 기술 블로그 게시글 작성
echo "Testing tech blog post creation..."
TECH_POST_RESPONSE=$(curl -s -X POST "${API_URL}/posts/" \
-H "${CONTENT_TYPE}" \
-H "Authorization: Bearer ${AUTH_TOKEN}" \
-d '{
    "title": "Python 테스트 코드 작성하기",
    "content": "# 테스트 코드 작성\n\n테스트는 중요합니다...",
    "board_type": "tech",
    "category": "python"
}')

if [[ $TECH_POST_RESPONSE == *"id"* ]]; then
    echo -e "${GREEN}✓ Tech blog post creation successful${NC}"
    echo "$TECH_POST_RESPONSE" | jq '.'
else
    echo -e "${RED}✗ Tech blog post creation failed${NC}"
    echo "$TECH_POST_RESPONSE"
fi

# 2. 자유게시판 글 작성
echo -e "\nTesting free board post creation..."
FREE_POST_RESPONSE=$(curl -s -X POST "${API_URL}/posts/" \
-H "${CONTENT_TYPE}" \
-H "Authorization: Bearer ${AUTH_TOKEN}" \
-d '{
    "title": "자유게시판 테스트",
    "content": "자유롭게 작성하는 글입니다.",
    "board_type": "free"
}')

if [[ $FREE_POST_RESPONSE == *"id"* ]]; then
    echo -e "${GREEN}✓ Free board post creation successful${NC}"
    echo $FREE_POST_RESPONSE | jq '.'
else
    echo -e "${RED}✗ Free board post creation failed${NC}"
    echo $FREE_POST_RESPONSE | jq '.'
fi

# 3. 방명록 작성
echo -e "\nTesting guestbook post creation..."
GUEST_POST_RESPONSE=$(curl -s -X POST "${API_URL}/posts/" \
-H "${CONTENT_TYPE}" \
-H "Authorization: Bearer ${AUTH_TOKEN}" \
-d '{
    "title": "방명록 테스트",
    "content": "방문했어요! 좋은 블로그네요 :)",
    "board_type": "guest"
}')

if [[ $GUEST_POST_RESPONSE == *"id"* ]]; then
    echo -e "${GREEN}✓ Guestbook post creation successful${NC}"
    echo $GUEST_POST_RESPONSE | jq '.'
else
    echo -e "${RED}✗ Guestbook post creation failed${NC}"
    echo $GUEST_POST_RESPONSE | jq '.'
fi

# 4. 게시판별 목록 조회
echo -e "\nTesting board listings..."

# 기술 블로그 목록
echo -e "\nTech blog posts:"
curl -s "${API_URL}/posts/tech/" | jq '.'

# 자유게시판 목록
echo -e "\nFree board posts:"
curl -s "${API_URL}/posts/free/" | jq '.'

# 방명록 목록
echo -e "\nGuestbook posts:"
curl -s "${API_URL}/posts/guestbook/" | jq '.'

# 카테고리별 기술 블로그 목록
echo -e "\nPython category posts:"
curl -s "${API_URL}/posts/tech/?category=python" | jq '.' 