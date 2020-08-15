# MusicManager

MusicManager와 함께 자신의 음반을 관리하고 취향을 공유해 보세요!

아래와 같은 사항을 지원합니다.

* Bugs, Naver Music, Melon, AllMusic의 음반 주소를 통해 음반 등록 가능
* 등록된 앨범에 대한 댓글 달기 기능
* 사용자별 음반 등록/삭제 기능
* 별점 기능
* 두 사용자 간 동일한 앨범 존재 여부 확인 기능

## 배포 가이드

1. Zappa 환 초기화: `zappa init`
2. 데이터베이스 설정: `zappa manage production migrate --settings=MusicManager.settings.production`
3. 최초 배포 수행: `zappa deploy production`
4. 업데이트 배포: `zappa update production`
5. Lambda 함수 및 API Gateway 삭제: `zappa undeploy production`

(English Version)

Manage and share your interest of music with MusicManager!

I support these below:

* Register album with URL of Bugs, Naver Music, Melon, AllMusic
* Write comment to registered albums
* Add/delete album per a user
* Star ratings
* See similar interest between logged user and another user

## Deployment Guide

1. Initialize configuration: `zappa init`
2. Configure database: `zappa manage production migrate --settings=MusicManager.settings.production`
3. First deployment: `zappa deploy production`
4. Update application: `zappa update production`
5. Remove Lambda functions & API Gateway: `zappa undeploy production`