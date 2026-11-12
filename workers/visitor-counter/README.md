# 블로그 방문자 수 Worker

사이드바의 `오늘 N · 전체 M`을 채우는 Cloudflare Worker입니다.

- **수집**: GoatCounter의 `count.js`가 합니다. Chirpy가 `analytics.goatcounter.id`를 보고 production 빌드에만 넣습니다.
- **조회**: 이 Worker가 GoatCounter API(`/api/v0/stats/total`)를 API 키로 불러서 `GET /stats` → `{ today, total, date, updatedAt }`으로 돌려줍니다.
- **"오늘"의 기준**: KST(Asia/Seoul) 자정부터 지금까지입니다. GoatCounter는 UTC 1시간 단위로 저장하고 KST는 UTC+9로 정시 차이라서, `start=전날 15:00Z`처럼 정시로 자르면 KST 하루가 정확히 나옵니다.
- **방문자 정의**: GoatCounter를 그대로 따릅니다.
  - `사이트 + User-Agent + IP`로 세션을 만들고 8시간 동안 기억합니다. 쿠키는 쓰지 않고 IP는 저장하지 않습니다.
  - 같은 세션이 처음 보는 경로를 열 때 1회로 셉니다. 새로고침은 세지 않고, 다른 글은 따로 셉니다.
  - 스스로 봇이라고 밝히는 크롤러는 제외됩니다.
- **캐시**: workers.dev에서는 Cache API가 동작하지 않아서 KV에 5분 동안 캐시합니다(쓰기는 하루 최대 288번). GoatCounter가 실패하면 마지막 값을 `stale: true`로 돌려줍니다.

## 배포와 비밀값

**배포는 GitHub Actions가 합니다**(`.github/workflows/visitor-counter-deploy.yml`). main에 `workers/visitor-counter/**`가 바뀌어 push되거나 수동 실행(workflow_dispatch)하면, 테스트 → `wrangler deploy` → `/stats` 스모크 테스트 순서로 진행합니다.

비밀값은 **GitHub Secrets에만** 둡니다. 저장소와 로컬에는 남기지 않습니다.

| Secret | 용도 | 만든 곳 |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | Worker 배포 | Cloudflare → Manage account → Account API tokens (`github-actions-blog-visitor-counter`, Workers 계정 권한) |
| `CLOUDFLARE_ACCOUNT_ID` | 배포 대상 계정 | Cloudflare 계정 ID |
| `GOATCOUNTER_TOKEN` | Worker가 GoatCounter 통계를 읽음. 배포할 때마다 Worker secret으로 다시 넣습니다 | GoatCounter → 사용자 메뉴 → API (`blog-visitor-counter-worker`, Read statistics만) |

공개 값은 그대로 커밋합니다. 브라우저에 노출되거나 식별자일 뿐이라 비밀이 아닙니다.
- `wrangler.toml`: GoatCounter 사이트 코드, KV namespace id
- `_config.yml`: Worker 주소

키를 바꿀 때는 새 키를 만들어 `gh secret set <이름>`으로 등록한 뒤 이 워크플로를 수동 실행하고, 옛 키는 삭제합니다.

로컬에서 직접 배포해야 한다면 `npx wrangler login` → `npx wrangler deploy` 후 `npx wrangler logout`으로 로그인 토큰을 지웁니다. 비밀값 파일은 `.secret-*`, `.dev.vars` 패턴으로 git에서 제외되어 있습니다.

## 그 밖에

- 테스트: `npm test`. GoatCounter와 KV를 흉내 내서 KST 경계, 캐시, 실패 처리를 확인합니다.
- `TOTAL_OFFSET`: GoatCounter를 붙이기 전 방문자 수(예: GA 누적값)를 전체 수에 더하고 싶을 때 씁니다.
- `ALLOWED_ORIGINS`: CORS로 허용할 Origin 목록입니다. 로컬 `jekyll serve`(4000번 포트)도 들어 있습니다.
- 무료 한도: Workers는 요청 하루 10만 건, KV는 쓰기 하루 1,000번입니다. GoatCounter API는 초당 4번까지 받습니다.
