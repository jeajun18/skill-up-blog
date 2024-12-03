FROM python:3.12-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    libjpeg62-turbo-dev \
    libwebp-dev \
    jq \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN pip install poetry

# Poetry 설정
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# 의존성 파일 복사 및 설치
COPY pyproject.toml poetry.lock ./
RUN poetry lock --no-update && \
    poetry install --only main

# 소스코드 복사
COPY . .

# 미디어 디렉토리 생성 및 권한 설정
RUN mkdir -p media/posts/2024/12/03 && \
    chown -R 1000:1000 media && \
    chmod -R 777 media

# 포트 설정
EXPOSE 8000

# 스크립트 복사 및 권한 설정
COPY scripts/wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

# 실행 명령 수정
CMD ["/wait-for-db.sh", "python", "manage.py", "runserver", "0.0.0.0:8000"] 