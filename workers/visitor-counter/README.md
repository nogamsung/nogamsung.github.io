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

## 처음 설정

1. **GoatCounter**
   1. https://www.goatcounter.com 에서 사이트를 만듭니다. 사이트 코드가 `<code>`이면 주소는 `https://<code>.goatcounter.com`입니다.
   2. Settings에서 **"Allow adding visitor counts on your website"**를 켭니다. 글별 조회수가 공개 카운터를 쓰기 때문입니다.
   3. 오른쪽 위 사용자 메뉴 → **API**에서 키를 만듭니다. 권한은 통계 읽기만 줍니다.
2. **Worker 배포** (이 디렉터리에서)
   ```bash
   npm install
   npx wrangler login
   npx wrangler kv namespace create STATS      # 출력된 id 를 wrangler.toml 의 kv_namespaces.id 에
   # wrangler.toml 의 GOATCOUNTER_CODE 를 <code> 로
   npx wrangler secret put GOATCOUNTER_TOKEN   # 3번에서 만든 API 키
   npx wrangler deploy                          # https://blog-visitor-counter.<계정>.workers.dev
   curl https://blog-visitor-counter.<계정>.workers.dev/stats
   ```
3. **블로그** (`_config.yml`)
   ```yaml
   analytics:
     goatcounter:
       id: <code>
   visitor_counter:
     endpoint: https://blog-visitor-counter.<계정>.workers.dev
   ```

## 그 밖에

- 테스트: `npm test`. GoatCounter와 KV를 흉내 내서 KST 경계, 캐시, 실패 처리를 확인합니다.
- `TOTAL_OFFSET`: GoatCounter를 붙이기 전 방문자 수(예: GA 누적값)를 전체 수에 더하고 싶을 때 씁니다.
- `ALLOWED_ORIGINS`: CORS로 허용할 Origin 목록입니다. 로컬 `jekyll serve`(4000번 포트)도 들어 있습니다.
- 무료 한도: Workers는 요청 하루 10만 건, KV는 쓰기 하루 1,000번입니다. GoatCounter API는 초당 4번까지 받습니다.
