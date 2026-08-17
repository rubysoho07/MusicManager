# AGENTS.md: AI 개발 에이전트 가이드

이 문서는 AI 기반 개발 도우미가 이 프로젝트를 이해하고 효과적으로 기여할 수 있도록 돕기 위한 가이드입니다.

## 1. 프로젝트 개요

**MusicManager**는 수집한 음반을 관리하기 위한 웹 애플리케이션입니다. 사용자는 음반을 추가, 조회, 검색할 수 있습니다. 또한, Slack 슬래시 명령어를 통해 음반을 검색하고 추가하는 기능도 제공합니다.

## 2. 기술 스택

-   **언어**: Python 3.13
-   **프레임워크**: Flask
-   **데이터베이스**: Supabase
-   **코드 스타일 및 린팅**: Ruff, pre-commit
-   **의존성**: `Flask`, `supabase`, `Flask-Cors`

## 3. 프로젝트 구조

-   `.gitignore`: Git에서 추적하지 않을 파일 및 디렉터리를 지정합니다.
-   `.pre-commit-config.yaml`: `pre-commit` 훅 설정을 통해 커밋 전에 코드 품질(Ruff)을 검사합니다.
-   `app.py`: 주 애플리케이션 파일입니다. Flask 앱을 생성하고 모든 API 엔드포인트와 비즈니스 로직을 포함합니다.
-   `Dockerfile`: 애플리케이션을 컨테이너화하기 위한 설정 파일입니다.
-   `pyproject.toml`: Ruff의 린팅 및 포매팅 규칙을 설정합니다.
-   `README.md`: 프로젝트에 대한 일반적인 정보를 제공합니다.

## 4. 개발 환경 설정

1.  **Python 가상 환경 생성 및 활성화**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **의존성 설치**:
    ```bash
    pip install .
    ```

3.  **환경 변수 설정**:
    애플리케이션 실행을 위해 다음 환경 변수가 필요합니다.
    -   `SUPABASE_URL`: Supabase 프로젝트 URL
    -   `SUPABASE_KEY`: Supabase 프로젝트 API Key
    -   `DOMAIN`: 애플리케이션이 배포되는 도메인 주소

## 5. 주요 명령어

-   **애플리케이션 실행**:
    ```bash
    flask run --host=0.0.0.0 --port=8080
    ```

-   **Docker 이미지 빌드 (AMD64)**:
    ```bash
    docker build --platform=linux/amd64 -t musicmanager .
    ```

-   **코드 스타일 검사 및 수정**:
    ```bash
    ruff check --fix .
    ruff format .
    ```

## 6. 테스트

현재 프로젝트에는 자동화된 테스트가 없습니다. 새로운 기능을 추가하거나 버그를 수정할 때는 관련 테스트 코드를 작성하는 것을 권장합니다.

## 7. 코딩 컨벤션

-   Ruff를 사용하여 코드 스타일과 포맷을 유지합니다. (`pyproject.toml` 참고)
-   `pre-commit`을 통해 커밋 시점에 자동으로 코드 품질을 검사합니다.
