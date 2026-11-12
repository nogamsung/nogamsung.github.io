// 블로그 사이드바용 방문자 수 API — GET /stats → { today, total, date, updatedAt }
//
// - 수집은 GoatCounter(count.js)가 하고, 이 Worker는 GoatCounter API를 읽기만 한다.
// - API 키(GOATCOUNTER_TOKEN)를 브라우저에 노출하지 않으려고 Worker를 거친다.
// - "오늘"은 KST(UTC+9) 자정부터 지금까지. GoatCounter는 UTC 1시간 단위로 저장하고
//   KST는 정시 차이라서, 정시로 자른 UTC 범위로 정확히 KST 하루를 구할 수 있다.
// - workers.dev 에서는 Cache API가 동작하지 않으므로 KV를 5분 캐시로 쓴다
//   (갱신은 5분에 한 번 → 하루 최대 288번 쓰기, 무료 한도 1,000번 안).

const HOUR = 3_600_000;
const DAY = 24 * HOUR;
const KST_OFFSET = 9 * HOUR;
const CACHE_KEY = 'stats:v1';
const FRESH_MS = 5 * 60_000;

export default {
  async fetch(request, env, ctx) {
    const cors = corsHeaders(request, env);
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: { ...cors, 'Access-Control-Allow-Methods': 'GET', 'Access-Control-Max-Age': '86400' },
      });
    }

    const { pathname } = new URL(request.url);
    if (request.method !== 'GET' || pathname !== '/stats') {
      return json({ error: 'not_found' }, 404, cors);
    }

    const cached = await env.STATS.get(CACHE_KEY, 'json');
    if (cached && Date.now() - Date.parse(cached.updatedAt) < FRESH_MS) {
      return json(cached, 200, cors);
    }

    try {
      const fresh = await computeStats(env);
      ctx.waitUntil(env.STATS.put(CACHE_KEY, JSON.stringify(fresh)));
      return json(fresh, 200, cors);
    } catch (err) {
      console.error('goatcounter fetch failed', err instanceof Error ? err.message : err);
      // GoatCounter 장애·한도 초과 때는 마지막 값을 그대로 돌려준다 (날짜가 바뀌었으면 today 는 버린다)
      if (cached) {
        const sameDay = cached.date === kstDate(Date.now());
        return json({ ...cached, today: sameDay ? cached.today : null, stale: true }, 200, cors);
      }
      return json({ error: 'upstream_unavailable' }, 502, cors);
    }
  },
};

async function computeStats(env) {
  const now = Date.now();
  const todayStart = Math.floor((now + KST_OFFSET) / DAY) * DAY - KST_OFFSET; // KST 자정(UTC 시각)
  const end = Math.ceil(now / HOUR) * HOUR; // API 가 정시 단위를 요구한다

  const [today, total] = await Promise.all([
    countVisitors(env, todayStart, end),
    countVisitors(env, Date.parse(env.COUNT_SINCE), end),
  ]);

  return {
    today,
    total: total + Number(env.TOTAL_OFFSET || 0),
    date: kstDate(now),
    updatedAt: new Date(now).toISOString(),
  };
}

async function countVisitors(env, start, end) {
  const url = new URL(`https://${env.GOATCOUNTER_CODE}.goatcounter.com/api/v0/stats/total`);
  url.searchParams.set('start', isoHour(start));
  url.searchParams.set('end', isoHour(end));

  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${env.GOATCOUNTER_TOKEN}`, Accept: 'application/json' },
  });
  if (!res.ok) throw new Error(`GoatCounter ${res.status}`);

  const body = await res.json();
  if (typeof body.total !== 'number') throw new Error('GoatCounter: unexpected response');
  return body.total;
}

function corsHeaders(request, env) {
  const allowed = (env.ALLOWED_ORIGINS || '').split(',').map((s) => s.trim()).filter(Boolean);
  const origin = request.headers.get('Origin');
  return {
    'Access-Control-Allow-Origin': allowed.includes(origin) ? origin : allowed[0] || '*',
    Vary: 'Origin',
  };
}

function json(body, status, headers) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...headers, 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=60' },
  });
}

const isoHour = (t) => new Date(t).toISOString().replace(/\.\d{3}Z$/, 'Z');
const kstDate = (t) => new Date(t + KST_OFFSET).toISOString().slice(0, 10);

export const _internal = { computeStats, kstDate, isoHour };
