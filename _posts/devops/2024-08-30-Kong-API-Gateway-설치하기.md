---
layout: post
title: Kong API Gateway 설치하기
date: '2024-08-30'
description: null
categories: [devops, api-gateway]
img: null
tags: [devops, api-gateway, kong, konga]
toc: true
toc_sticky: true
toc_label: 목차
---
# 개요

여러 API 서버들이 존재할 때 이를 편하게 관리하기 위해서는 여러대의 Nginx 같은 reverse proxy를 두는거 보다 하나의 API Gateway로 들어오는 모든 Client 요청들을 관리하는게 편하다. 특히 MSA 같은 환경을 구성할때 API Gateway는 필수 요소다.

Kong, KrakenD, SCG 등 여러 API Gateway 솔루션이 있다. 본 글에서는 Kong API Gateway를 활용해 보겠다.

Kong API Gateway는 Nginx + Cassandra + Lua Script 기반으로 동작하며 다양한 기능들을 가지고 있다.

Konga는 Kong Admin을 위한 UI이며 주로 아래 [panstel/konga](https://github.com/pantsel/konga) 많이 사용한다.

## 설치 방법

- 배포판
- Docker
- K8S Ingress Controller

> 본 글에서는 Docker로 설치하는 방법으로 진행하겠다.

## 구성 요소

### Database

서비스, 라우팅, 각종 인증, 플로그인들의 사용 정보를 저장하기 위해 **PostgreSQL** 또는 **Cassandra**를 선택해 사용한다.

### Kong API Gateway

클라이언트 요청을 받아 서비스로 라우팅하는 핵심 역할을 수행한다.

## Docker network 설정

Kong과 Database를 동일한 Docker network 상에서 설치해야 한다.

```
docker network create kong-net
```

`kong-net`이라는 네트워크를 설정 했다.


## Kong DB 설정

### PostgreSQL 설치

```
docker run -d --name kong-database \
               --network=kong-net \
               -p 5432:5432 \
               -e "POSTGRES_USER=kong" \
               -e "POSTGRES_DB=kong" \
               -e "POSTGRES_PASSWORD=kong" \
               postgres:9.6
```

- `POSTGRES_USER`: 사용자 이름
- `POSTGRES_DB`: 데이터베이스 이름
- `POSTGRES_PASSWORD`: 사용자 비밀번호

### DB 테스트

```
docker exec -it kong-database /bin/bash

psql -U kong
```

### DB 초기화

```
docker run --rm \
		     --network=kong-net \
		     -e "KONG_DATABASE=postgres" \
		     -e "KONG_PG_HOST=kong-database" \
		     -e "KONG_PG_USER=kong" \
		     -e "KONG_PG_PASSWORD=kong" \
		     kong:latest kong migrations bootstrap
```

- `KONG_DATABASE`: 데이터베이스 지정
- `KONG_PG_HOST`: 데이터베이스 이름 지정
- `KONG_PG_USER`: 사용자 이름
- `KONG_PG_PASSWORD`: 사용자 비밀번호

## Kong 실행

```
docker run -d --name kong \
		     --network=kong-net \
		     -e "KONG_DATABASE=postgres" \
		     -e "KONG_PG_HOST=kong-database" \
		     -e "KONG_PG_USER=kong" \
		     -e "KONG_PG_PASSWORD=kong" \
		     -e "KONG_PROXY_ACCESS_LOG=/dev/stdout" \
		     -e "KONG_ADMIN_ACCESS_LOG=/dev/stdout" \
		     -e "KONG_PROXY_ERROR_LOG=/dev/stderr" \
		     -e "KONG_ADMIN_ERROR_LOG=/dev/stderr" \
		     -e "KONG_ADMIN_LISTEN=0.0.0.0:8001, 0.0.0.0:8444 ssl" \
		     -p 8000:8000 \
		     -p 8443:8443 \
		     -p 127.0.0.1:8001:8001 \
		     -p 127.0.0.1:8444:8444 \
		     kong
```

- 접속 로그와 에러 로그
	- `KONG_PROXY_ACCESS_LOG`
	- `KONG_ADMIN_ACCESS_LOG`
	- `KONG_PROXY_ERROR_LOG`
	- `KONG_ADMIN_ERROR_LOG`

## Kong 관련 port

- 8000
	- HTTP 요청을 받아 서비스로 업스트림한다.
- 8443
	- HTTPS 요청을 받아 서비스로 업스트림한다.
	- HTTPS만 받고 off를 할 수 있는 옵션 존재하다.
- 8001
	- Admin API를 위한 요청 받는다.
- 8444
	- Admin API를 HTTPS로 리슨한다.

## Konga DB 설정

### DB 초기화

```
docker run --rm \
			--network=kong-net \
			pantsel/konga:latest \
			-c prepare \
			-a 'postgres' \
			-u postgresql://kong:kong@kong-database:5432/konga
```

## Konga 실행

```
docker run -p 1337:1337 \
			--network=kong-net \
			-e "TOKEN_SECRET=TOKEN_SECRET" \
			-e "DB_ADAPTER=postgres" \
			-e "DB_URI=postgresql://kong:kong@kong-database:5432/konga" \
			-e "NODE_ENV=production" \
			--name konga \
			pantsel/konga
```

## Konga 연결 설정

![](../../assets/img/2024/08/30-1.png)
![]()

## Service 등록

![](../../assets/img/2024/08/30-2.png)

## Route 등록

![](../../assets/img/2024/08/30-3.png)

![](../../assets/img/2024/08/30-4.png)

## 연결 확인

등록한 Route Path 인 `/api/spring` 그리고 8000 Port로 요청을 보내면 Kong이 성공적으로 작용하고 있는걸 확인할 수 있다.

![](../../assets/img/2024/08/30-5.png)

## 참조

- [https://docs.konghq.com/gateway/3.7.x/install/docker/](https://docs.konghq.com/gateway/3.7.x/install/docker/)
- [https://www.sktenterprise.com/bizInsight/blogDetail/dev/2850](https://www.sktenterprise.com/bizInsight/blogDetail/dev/2850)
- [https://ibks-platform.tistory.com/379](https://ibks-platform.tistory.com/379)
