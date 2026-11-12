---
title: Docker로 Kong API Gateway와 Konga 설치하기
slug: kong-api-gateway-install
series: Kong API Gateway
redirect_from:
  - /posts/Kong-API-Gateway-설치하기/
date: 2024-08-30
description: >-
  Docker 네트워크 하나에 PostgreSQL, Kong, Konga를 띄우고 Service와 Route를 등록해 요청이 라우팅되는지 확인하기까지, 명령어마다 왜 그 단계가 필요한지와 포트·환경 변수의 의미를 함께 정리합니다.
categories: [devops, api-gateway]
tags: [kong, konga, api-gateway, docker, postgresql]
image:
  path: /assets/img/thumbnail/kong-api-gateway-install.jpg
  alt: "Docker로 Kong API Gateway와 Konga 설치하기"
---

## 들어가며

API 서버가 여러 대가 되면 서버마다 Nginx 같은 리버스 프록시를 두고 관리하기가 점점 번거로워집니다. 그래서 클라이언트 요청이 모두 **API Gateway 하나**를 거치게 하고, 라우팅·인증·로깅 같은 공통 관심사를 그곳에 모으는 구성을 많이 씁니다. MSA처럼 서비스가 잘게 나뉜 환경에서는 사실상 필수 요소입니다.

API Gateway 솔루션은 Kong, KrakenD, Spring Cloud Gateway(SCG) 등 여러 가지가 있는데, 저는 **Kong**을 써 보기로 했습니다. 이 글은 Docker로 Kong과 관리 UI인 Konga를 설치하고, 첫 라우팅이 동작하는지 확인하기까지의 과정입니다.

## 1. Kong과 Konga 🦍

Kong은 Nginx 위에서 Lua 스크립트를 실행하는 OpenResty를 기반으로 동작하는 API Gateway입니다. 라우팅 규칙과 플러그인 설정은 데이터베이스에 저장하고, 기능 대부분을 **플러그인**으로 붙였다 뗄 수 있습니다.

Konga는 Kong Admin API를 화면으로 다룰 수 있게 해 주는 오픈 소스 관리 UI입니다. 주로 [pantsel/konga](https://github.com/pantsel/konga)를 많이 씁니다.

이번 구성에 들어가는 요소는 셋입니다.

| 구성 요소 | 역할 |
|---|---|
| Database (PostgreSQL) | Service, Route, 인증 정보, 플러그인 설정을 저장한다. Konga도 자기 데이터를 여기에 둔다 |
| Kong | 클라이언트 요청을 받아 등록된 규칙에 따라 서비스로 라우팅한다 |
| Konga | Kong Admin API를 호출해 설정을 화면에서 관리한다 |

Kong은 배포판 패키지, Docker, Kubernetes Ingress Controller 등으로 설치할 수 있습니다. 이 글에서는 **Docker**로 진행합니다.

## 2. 전체 구성 🗺️

![클라이언트 요청은 8000 포트로 Kong에 들어와 Route /api/spring에 맞는 Service로 전달되고, 관리자는 1337 포트의 Konga에서 Admin API 8001을 통해 설정을 바꾸며 그 설정은 kong-database에 저장되는 구성도](/assets/img/2024/08/30-6.svg){: width="1100" height="560" }

세 컨테이너를 모두 `kong-net`이라는 Docker 네트워크 하나에 올립니다. 같은 네트워크 안에서는 컨테이너 이름(`kong-database`, `kong`)이 곧 호스트 이름이 되기 때문에, Kong은 DB를, Konga는 Kong을 이름으로 찾을 수 있습니다.

요청이 지나가는 길은 둘입니다.

- **프록시 경로**: 클라이언트 → Kong(8000) → Route 규칙 → Service(업스트림 서버)
- **관리 경로**: 관리자 → Konga(1337) → Kong Admin API(8001) → DB에 설정 저장

## 3. Docker 네트워크 만들기 🌐

Kong과 DB가 서로를 찾으려면 같은 네트워크에 있어야 합니다. 먼저 네트워크를 만듭니다.

```bash
docker network create kong-net
```

## 4. PostgreSQL 띄우고 Kong DB 초기화하기 🐘

### ① PostgreSQL 실행

```bash
docker run -d --name kong-database \
  --network=kong-net \
  -p 5432:5432 \
  -e "POSTGRES_USER=kong" \
  -e "POSTGRES_DB=kong" \
  -e "POSTGRES_PASSWORD=kong" \
  postgres:9.6
```

| 환경 변수 | 의미 |
|---|---|
| `POSTGRES_USER` | 사용자 이름 |
| `POSTGRES_DB` | 처음 만들 데이터베이스 이름 |
| `POSTGRES_PASSWORD` | 사용자 비밀번호 |

`--name kong-database`가 중요합니다. 뒤에서 Kong과 Konga가 이 이름으로 DB에 접속합니다.

### ② 접속 확인

컨테이너 안으로 들어가 `kong` 사용자로 접속해 봅니다. 프롬프트가 뜨면 DB가 정상입니다(`\q`로 나옵니다).

```bash
docker exec -it kong-database /bin/bash
```

```bash
psql -U kong
```

### ③ Kong 스키마 만들기

DB는 비어 있는 상태이므로, Kong이 쓸 테이블을 먼저 만들어야 합니다. `kong migrations bootstrap`이 그 일을 합니다. 한 번만 실행하면 되는 작업이라 `--rm`으로 띄워서 끝나면 컨테이너가 지워지게 했습니다.

```bash
docker run --rm \
  --network=kong-net \
  -e "KONG_DATABASE=postgres" \
  -e "KONG_PG_HOST=kong-database" \
  -e "KONG_PG_USER=kong" \
  -e "KONG_PG_PASSWORD=kong" \
  kong:latest kong migrations bootstrap
```

| 환경 변수 | 의미 |
|---|---|
| `KONG_DATABASE` | 사용할 데이터베이스 종류 (`postgres`) |
| `KONG_PG_HOST` | DB 호스트. 같은 네트워크이므로 컨테이너 이름 `kong-database`를 쓴다 |
| `KONG_PG_USER` | DB 사용자 이름 |
| `KONG_PG_PASSWORD` | DB 사용자 비밀번호 |

## 5. Kong 실행하기 🚀

```bash
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

DB 접속 정보는 앞 단계와 같습니다. 나머지 옵션은 이런 의미입니다.

- `KONG_PROXY_ACCESS_LOG`, `KONG_ADMIN_ACCESS_LOG`, `KONG_PROXY_ERROR_LOG`, `KONG_ADMIN_ERROR_LOG`: 프록시와 Admin API의 접속·에러 로그를 표준 출력/에러로 보낸다. 그래서 `docker logs kong`으로 바로 볼 수 있다.
- `KONG_ADMIN_LISTEN`: 컨테이너 **안에서는** Admin API를 모든 인터페이스에 연다. 같은 네트워크의 Konga가 접속해야 하기 때문이다.
- `-p 127.0.0.1:8001:8001`: 대신 **호스트에서는** Admin API를 `127.0.0.1`에만 연다. Admin API는 Kong 설정을 마음대로 바꿀 수 있으니 바깥에 노출하지 않는다.

Kong이 쓰는 포트는 네 개입니다.

| 포트 | 용도 |
|---|---|
| 8000 | HTTP 요청을 받아 업스트림 서비스로 프록시한다 |
| 8443 | HTTPS 요청을 받아 업스트림 서비스로 프록시한다 |
| 8001 | Admin API (HTTP) |
| 8444 | Admin API (HTTPS) |

프록시 포트는 설정(`KONG_PROXY_LISTEN`)으로 HTTP나 HTTPS 중 하나만 열도록 바꿀 수도 있습니다.

## 6. Konga 설치하기 🖥️

### ① Konga DB 준비

Konga도 자기 데이터를 저장할 곳이 필요합니다. 따로 DB 서버를 두지 않고 같은 PostgreSQL에 `konga` 데이터베이스를 쓰도록 했습니다. `-c prepare`는 Konga가 쓸 테이블을 준비하는 일회성 명령이라 역시 `--rm`으로 실행합니다.

```bash
docker run --rm \
  --network=kong-net \
  pantsel/konga:latest \
  -c prepare \
  -a 'postgres' \
  -u postgresql://kong:kong@kong-database:5432/konga
```

### ② Konga 실행

```bash
docker run -p 1337:1337 \
  --network=kong-net \
  -e "TOKEN_SECRET=TOKEN_SECRET" \
  -e "DB_ADAPTER=postgres" \
  -e "DB_URI=postgresql://kong:kong@kong-database:5432/konga" \
  -e "NODE_ENV=production" \
  --name konga \
  pantsel/konga
```

`TOKEN_SECRET`은 Konga가 로그인 토큰을 서명할 때 쓰는 값입니다. 예제에서는 문자열을 그대로 넣었지만, 실제로는 추측하기 어려운 값으로 바꿔야 합니다.

### ③ Konga와 Kong 연결

브라우저에서 `localhost:1337`로 접속해 Kong Admin API와 연결합니다. Konga도 `kong-net` 안에 있으므로 Admin API 주소는 컨테이너 이름으로 적을 수 있습니다(예: `http://kong:8001`).

![Konga에서 Kong Admin API 주소를 입력해 연결을 만드는 화면](/assets/img/2024/08/30-1.webp){: width="649" height="693" }

## 7. Service와 Route 등록하고 확인하기 🔀

Kong의 라우팅은 두 가지 객체로 이루어집니다.

| 객체 | 의미 |
|---|---|
| Service | 요청을 보낼 업스트림 서버 (예: Spring 서버의 주소) |
| Route | 어떤 요청을 그 Service로 보낼지 정하는 규칙 (예: 경로 `/api/spring`) |

### ① Service 등록

먼저 요청을 받을 백엔드 서버를 Service로 등록합니다.

![Konga에서 업스트림 서버 정보를 입력해 Service를 등록하는 화면](/assets/img/2024/08/30-2.webp){: width="891" height="1257" }

### ② Route 등록

등록한 Service에 Route를 붙입니다. 이번에는 경로 `/api/spring`으로 들어오는 요청을 이 Service로 보내도록 했습니다.

![Service 상세 화면에서 Route를 추가하는 화면](/assets/img/2024/08/30-3.webp){: width="889" height="1220" }

![Route에 경로 /api/spring을 설정한 화면](/assets/img/2024/08/30-4.webp){: width="890" height="657" }

### ③ 연결 확인

이제 Kong의 프록시 포트 8000으로 등록한 경로 `/api/spring`을 호출하면, Kong이 요청을 Spring 서버로 넘겨 응답이 돌아옵니다.

![8000 포트의 /api/spring으로 보낸 요청이 Kong을 거쳐 Spring 서버의 응답을 받은 화면](/assets/img/2024/08/30-5.webp){: width="709" height="489" }

![첫 라우팅에 성공해 기뻐하는 짤](/assets/img/zzal/chimchakman-3.gif){: width="362" height="446" }

## 마무리

- 세 컨테이너를 같은 Docker 네트워크에 두면 컨테이너 이름으로 서로를 찾는다. `KONG_PG_HOST`나 Konga의 연결 주소에 이름을 쓰는 이유다.
- Kong은 DB가 비어 있으면 뜨지 않는다. `kong migrations bootstrap`으로 스키마를 먼저 만든다.
- Admin API는 컨테이너 안에서는 열고, 호스트에서는 `127.0.0.1`에만 연다. 바깥에는 프록시 포트만 노출한다.
- 라우팅은 Service(어디로)와 Route(어떤 요청을)의 조합이다.

> 참고
> - [Kong Gateway: Install with Docker](https://docs.konghq.com/gateway/3.7.x/install/docker/)
> - [pantsel/konga](https://github.com/pantsel/konga)
> - [SK엔터프라이즈 비즈인사이트 블로그](https://www.sktenterprise.com/bizInsight/blogDetail/dev/2850)
> - [ibks-platform 기술 블로그](https://ibks-platform.tistory.com/379)
> - [Lua로 만든 Kong 커스텀 플러그인을 Docker 이미지로 적용하기](/posts/kong-custom-plugin/)
{: .prompt-info }
