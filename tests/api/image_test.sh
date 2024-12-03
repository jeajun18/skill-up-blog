#!/bin/bash

# 기본 설정
API_URL="http://localhost:8000/api/v1"
CONTENT_TYPE="Content-Type: multipart/form-data"
AUTH_TOKEN=$(cat tests/api/token.txt)

# 색상 설정
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 테스트 이미지 경로
TEST_IMAGE="tests/api/assets/test.png"

# 이미지가 있는 게시글 작성
echo "Testing post creation with image..."
POST_RESPONSE=$(curl -s -X POST "${API_URL}/posts/" \
-H "Authorization: Bearer ${AUTH_TOKEN}" \
-F "title=이미지 테스트" \
-F "content=이미지 업로드 테스트입니다." \
-F "board_type=free" \
-F "category=python" \
-F "image=@${TEST_IMAGE}")

if [[ $POST_RESPONSE == *"id"* ]]; then
    echo -e "${GREEN}✓ Post creation with image successful${NC}"
    echo "$POST_RESPONSE" | jq '.'
else
    echo -e "${RED}✗ Post creation with image failed${NC}"
    echo "$POST_RESPONSE"
fi 