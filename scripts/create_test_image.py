import base64

# 1x1 투명 PNG 이미지 (base64로 인코딩됨)
PNG_DATA = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

# 이미지 파일 생성
with open("tests/api/assets/test.png", "wb") as f:
    f.write(base64.b64decode(PNG_DATA)) 