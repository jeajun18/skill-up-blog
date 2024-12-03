#!/bin/bash

# 기본 설정
API_URL="http://localhost:8000/api/v1"
CONTENT_TYPE="Content-Type: application/json"

# 색상 설정
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 토큰 읽기 및 검증
if [ ! -f tests/api/token.txt ]; then
    echo -e "${RED}✗ Token not found. Please run auth_test.sh first${NC}"
    exit 1
fi

AUTH_TOKEN=$(cat tests/api/token.txt)
if [ -z "$AUTH_TOKEN" ]; then
    echo -e "${RED}✗ Token is empty${NC}"
    exit 1
fi

# 게시글 작성 테스트
echo "Testing post creation..."
POST_RESPONSE=$(curl -s -X POST "${API_URL}/posts/" \
-H "${CONTENT_TYPE}" \
-H "Authorization: Bearer ${AUTH_TOKEN}" \
-d '{
    "title": "테스트 게시글",
    "content": "# 마크다운 테스트\n\n- 항목 1\n- 항목 2\n\n```python\nprint(\"Hello, World!\")\n```"
}')

if [[ $POST_RESPONSE == *"id"* ]]; then
    echo -e "${GREEN}✓ Post creation successful${NC}"
    echo $POST_RESPONSE | python -m json.tool
    POST_ID=$(echo $POST_RESPONSE | jq -r '.id')
    echo "Extracted POST_ID: $POST_ID"  # 디버그용
else
    echo -e "${RED}✗ Post creation failed${NC}"
    echo $POST_RESPONSE | python -m json.tool
    exit 1
fi

# 댓글 작성 테스트
echo -e "\nTesting comment creation..."
echo "Using POST_ID: ${POST_ID}"

# URL 구성
COMMENT_URL="${API_URL}/posts/${POST_ID}/comments"
echo "Request URL: ${COMMENT_URL}"

# POST 요청
COMMENT_RESPONSE=$(curl -s -X POST "${COMMENT_URL}/" \
-H "${CONTENT_TYPE}" \
-H "Authorization: Bearer ${AUTH_TOKEN}" \
-d '{
    "content": "테스트 댓글입니다."
}')

# 응답 확인
if [[ $COMMENT_RESPONSE == *"id"* ]]; then
    echo -e "${GREEN}✓ Comment creation successful${NC}"
    echo "$COMMENT_RESPONSE" | jq '.'
else
    echo -e "${RED}✗ Comment creation failed${NC}"
    echo "Response: $COMMENT_RESPONSE"
fi 