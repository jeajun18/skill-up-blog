#!/bin/bash

# 기본 설정
API_URL="http://localhost:8000/api/v1"
AUTH_TOKEN=$(cat tests/api/token.txt)

# 색상 설정
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 이미지 URL 접근성 체크 함수
check_image_url() {
    local url=$1
    if [ -n "$url" ] && [ "$url" != "null" ]; then
        echo -e "\nChecking image accessibility for: $url"
        local status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000$url")
        if [ "$status" -eq 200 ]; then
            echo -e "${GREEN}✓ Image accessible${NC}"
        else
            echo -e "${RED}✗ Image not accessible (status: $status)${NC}"
        fi
    fi
}

# 응답 처리 함수
handle_response() {
    local response=$1
    local test_name=$2
    local status_code=$3
    
    echo -e "\n=== $test_name ==="
    echo "Status code: $status_code"
    
    if [ -z "$response" ]; then
        echo -e "${RED}✗ Empty response${NC}"
        return
    fi
    
    if echo "$response" | jq -e . >/dev/null 2>&1; then
        if [[ $(echo "$response" | jq -r '.error') != "null" ]]; then
            echo -e "${RED}✗ Failed${NC}"
            echo "Error: $(echo "$response" | jq -r '.error')"
        else
            echo -e "${GREEN}✓ Success${NC}"
            echo "Response:"
            echo "$response" | jq '.'
            
            # 이미지 URL이 있는 경우 접근성 체크
            local image_url=$(echo "$response" | jq -r '.image')
            check_image_url "$image_url"
        fi
    else
        echo -e "${RED}✗ Invalid JSON response${NC}"
        echo "Raw response: $response"
    fi
}

# API 호출 함수
make_request() {
    local method=$1
    local url=$2
    shift 2
    
    # 응답 저장할 임시 파일
    local response_file=$(mktemp)
    local headers_file=$(mktemp)
    
    # curl 요청 실행
    curl -s -D "$headers_file" "$@" "$url" > "$response_file"
    
    # 상태 코드 추출
    local status_code=$(grep "HTTP/" "$headers_file" | tail -n1 | awk '{print $2}')
    
    # 응답 본문 읽기
    local response=$(cat "$response_file")
    
    # 임시 파일 삭제
    rm "$response_file" "$headers_file"
    
    # 결과 반환
    echo "$response"
    echo "$status_code"
}

# 1. 이미지 없이 게시글 작성
echo "Testing post creation without image..."
IFS=$'\n' read -r -d '' response status_code << EOF
$(make_request POST "${API_URL}/posts/" \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "이미지 없는 테스트",
        "content": "이미지가 없는 게시글입니다.",
        "board_type": "free",
        "category": "python"
    }')
EOF
handle_response "$response" "Post without image" "$status_code"

# 2. 다양한 이미지 포맷 테스트
for format in "png" "jpg" "gif"; do
    echo -e "\nTesting $format format..."
    IFS=$'\n' read -r -d '' response status_code << EOF
$(make_request POST "${API_URL}/posts/" \
        -H "Authorization: Bearer ${AUTH_TOKEN}" \
        -F "title=$format 이미지 테스트" \
        -F "content=$format 이미지 업로드 테스트입니다." \
        -F "board_type=free" \
        -F "category=python" \
        -F "image=@tests/api/assets/test.$format")
EOF
    handle_response "$response" "$format image upload" "$status_code"
done

# 3. 잘못된 파일 형식 테스트
echo -e "\nTesting invalid file format..."
IFS=$'\n' read -r -d '' response status_code << EOF
$(make_request POST "${API_URL}/posts/" \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -F "title=잘못된 파일 테스트" \
    -F "content=잘못된 파일 업로드 테스트입니다." \
    -F "board_type=free" \
    -F "category=python" \
    -F "image=@tests/api/assets/invalid.txt")
EOF
handle_response "$response" "Invalid file upload" "$status_code" 