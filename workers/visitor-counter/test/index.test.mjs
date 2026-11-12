// node --test workers/visitor-counter/test — GoatCounter·KV 를 흉내 내 Worker 동작을 확인한다
import { test } from 'node:test';
import assert from 'node:assert/strict';
import worker, { _internal } from '../src/index.js';

function setup({ totals = {}, fail = false, cached = null } = {}) {
  const calls = [];
  globalThis.fetch = async (url, init) => {
    const u = new URL(url);
    calls.push({ start: u.searchParams.get('start'), end: u.searchParams.get('end'), auth: init.headers.Authorization });
    if (fail) return new Response('rate limited', { status: 429 });
    return Response.json({ total: totals[u.searchParams.get('start')] ?? 0 });
  };
  const kv = new Map(cached ? [['stats:v1', JSON.stringify(cached)]] : []);
  const env = {
    GOATCOUNTER_CODE: 'blog', GOATCOUNTER_TOKEN: 'tok', COUNT_SINCE: '2026-11-01T00:00:00Z',
    TOTAL_OFFSET: '100', ALLOWED_ORIGINS: 'https://nogamsung.github.io',
    STATS: { get: async (k, t) => (kv.has(k) ? (t === 'json' ? JSON.parse(kv.get(k)) : kv.get(k)) : null),
             put: async (k, v) => kv.set(k, v) },
  };
  const waits = [];
  const ctx = { waitUntil: (p) => waits.push(p) };
  return { calls, env, ctx, kv, waits };
}
const req = (path = '/stats', origin = 'https://nogamsung.github.io') =>
  new Request(`https://w.example${path}`, { headers: { Origin: origin } });

test('KST 자정은 UTC 전날 15시, end 는 다음 정시로 올린다', async (t) => {
  t.mock.timers.enable({ apis: ['Date'], now: Date.parse('2026-11-12T03:20:00Z') }); // KST 12:20
  const { calls, env, ctx } = setup({ totals: { '2026-11-11T15:00:00Z': 7, '2026-11-01T00:00:00Z': 40 } });
  const res = await worker.fetch(req(), env, ctx);
  const body = await res.json();
  assert.equal(body.today, 7);
  assert.equal(body.total, 140); // 40 + TOTAL_OFFSET 100
  assert.equal(body.date, '2026-11-12');
  assert.deepEqual(calls.map((c) => c.end), ['2026-11-12T04:00:00Z', '2026-11-12T04:00:00Z']);
  assert.equal(calls[0].auth, 'Bearer tok');
  assert.equal(res.headers.get('Access-Control-Allow-Origin'), 'https://nogamsung.github.io');
});

test('KST 새벽(UTC 전날 밤)에도 오늘 시작은 KST 자정이다', async (t) => {
  t.mock.timers.enable({ apis: ['Date'], now: Date.parse('2026-11-11T16:05:00Z') }); // KST 11-12 01:05
  const { calls, env, ctx } = setup();
  const body = await (await worker.fetch(req(), env, ctx)).json();
  assert.equal(calls[0].start, '2026-11-11T15:00:00Z');
  assert.equal(body.date, '2026-11-12');
});

test('5분 안의 캐시는 GoatCounter 를 부르지 않는다', async (t) => {
  t.mock.timers.enable({ apis: ['Date'], now: Date.parse('2026-11-12T03:20:00Z') });
  const cached = { today: 3, total: 9, date: '2026-11-12', updatedAt: '2026-11-12T03:17:00Z' };
  const { calls, env, ctx } = setup({ cached });
  const body = await (await worker.fetch(req(), env, ctx)).json();
  assert.equal(calls.length, 0);
  assert.equal(body.today, 3);
});

test('GoatCounter 실패 시 지난 값을 stale 로, 날짜가 바뀌었으면 today 는 null', async (t) => {
  t.mock.timers.enable({ apis: ['Date'], now: Date.parse('2026-11-12T16:00:00Z') }); // KST 11-13 01:00
  const cached = { today: 50, total: 900, date: '2026-11-12', updatedAt: '2026-11-12T14:00:00Z' };
  const { env, ctx } = setup({ fail: true, cached });
  const body = await (await worker.fetch(req(), env, ctx)).json();
  assert.equal(body.stale, true);
  assert.equal(body.today, null);
  assert.equal(body.total, 900);
});

test('캐시도 없고 GoatCounter 도 실패하면 502', async () => {
  const { env, ctx } = setup({ fail: true });
  const res = await worker.fetch(req(), env, ctx);
  assert.equal(res.status, 502);
});

test('/stats 외 경로는 404, 허용 안 된 Origin 엔 첫 허용 Origin 을 돌려준다', async () => {
  const { env, ctx } = setup();
  const res = await worker.fetch(req('/', 'https://evil.example'), env, ctx);
  assert.equal(res.status, 404);
  assert.equal(res.headers.get('Access-Control-Allow-Origin'), 'https://nogamsung.github.io');
});

test('kstDate·isoHour', () => {
  assert.equal(_internal.kstDate(Date.parse('2026-11-11T14:59:59Z')), '2026-11-11');
  assert.equal(_internal.kstDate(Date.parse('2026-11-11T15:00:00Z')), '2026-11-12');
  assert.equal(_internal.isoHour(Date.parse('2026-11-12T04:00:00.000Z')), '2026-11-12T04:00:00Z');
});
