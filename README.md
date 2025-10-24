# MusicManager

수집한 음반을 관리하기 위한 시스템입니다. 다음과 같이 구성하려고 합니다. 

* Flask 프레임워크를 사용하고, Supabase를 데이터베이스로 활용합니다. 
* 음반 추가, 조회, 검색 기능을 지원합니다. 

## 개발 환경 구성

### 1. Python 가상 환경 생성

Python 3.13 버전 사용을 권장합니다. 다음 명령어로 가상 환경을 생성합니다.

```bash
python3 -m venv .venv
```

### 2. 가상 환경 활성화

```bash
source .venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

## 환경 변수

애플리케이션 실행에 필요한 환경 변수는 다음과 같습니다. `activate` 스크립트에 `export` 명령으로 설정하거나, 실행 환경에 직접 설정해 주세요.

* `SUPABASE_URL`: Supabase 프로젝트 URL
* `SUPABASE_KEY`: Supabase 프로젝트 API Key
* `DOMAIN`: 애플리케이션이 배포되는 도메인 주소

## 애플리케이션 실행

```bash
flask run --host=0.0.0.0 --port=8080
```

로컬 환경에서 확인하려면 `localhost:8080/health` 로 정상 동작을 확인할 수 있습니다.

## 컨테이너 이미지 빌드

이 프로젝트는 GCP의 Cloud Run으로 배포합니다. Cloud Run이 AMD64 아키텍처만 지원하기 때문에, AMD64 플랫폼으로 컨테이너 이미지를 빌드하여야 합니다. 컨테이너를 빌드하기 위해 아래 명령을 실행해 주세요.

```bash
docker build --platform=linux/amd64 -t musicmanager .
```

## 컨테이너 이미지 배포

GCP의 Artifact Registry로 컨테이너 이미지를 배포하는 방법은 다음과 같습니다.

### 1. gcloud CLI 인증

GCP 서울 리전(asia-northeast3)에 배포한다고 가정합니다. 

```bash
gcloud auth login
gcloud auth configure-docker asia-northeast3-docker.pkg.dev
```

### 2. 이미지 태그 지정

* PROJECT_NAME: 본인의 프로젝트 이름으로 대체합니다. 
* REPOSITORY_NAME: Artifact Registry에 등록한 저장소 이름으로 대체합니다. 
* PACKAGE_NAME: 원하는 패키지 이름으로 대체합니다.

```bash
docker tag musicmanager asia-northeast3-docker.pkg.dev/PROJECT_NAME/REPOSITORY_NAME/PACKAGE_NAME
```

### 3. 이미지 푸시

```bash
docker push asia-northeast3-docker.pkg.dev/PROJECT_NAME/REPOSITORY_NAME/PACKAGE_NAME
```
