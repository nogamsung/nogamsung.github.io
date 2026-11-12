"""English diagrams for five 2026 backend posts (English copy of the matching blocks in
tools/diagrams/make_diagrams.py).

  livekit-call-settlement-race        2026/09/03-1, 03-2, 03-3
  refresh-token-rotation-rollback     2026/09/04-1, 04-2
  spring-boot-4-kotlin-lazy-loading   2026/10/27-1, 27-2
  circuit-breaker-fail-closed         2026/11/02-1, 02-2
  jwt-permission-version              2026/11/03-3, 03-4, 03-5

Run: python3 tools/diagrams/en/backend_2026.py "$PWD"
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from diag import Diagram, INK, MUTED

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img/en', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

# =====================================================================
# 2026/11/03-3  pv post: roles are issue-time values
# =====================================================================
d = Diagram(1100, 520, "A token's roles are frozen at issue time: old permissions keep working until it expires")
d.text(80, 110, '09:00', size=13, color=MUTED, anchor='start'); d.text(1020, 110, '09:30', size=13, color=MUTED, anchor='end')
d.arrow([(80, 130), (1020, 130)], color='muted', head=True)
d.text(550, 150, '← access token lifetime: 30 min →', size=13, weight=600, color=MUTED)
d.box(60, 180, 300, 90, '09:00 Sign in', ['access token issued', 'roles = [A, B, C]  (issue-time value)'], color='blue')
d.box(400, 180, 300, 90, '09:10 Admin changes roles', ['DB: roles = [A]', '(B, C revoked)'], color='amber')
d.box(740, 180, 300, 90, '09:10 – 09:30 Requests', ["service filter only reads the token's roles", 'roles = [A, B, C] → allowed ❌'], color='red')
d.arrow([(360, 225), (400, 225)], color='gray'); d.arrow([(700, 225), (740, 225)], color='gray')
d.box(60, 320, 980, 60, color='muted')
d.lines(550, 341, ["The 9 service APIs only verify the signature and never ask account (stateless).",
                   "Fast and unaffected by account outages, but the roles inside a token never get refreshed."], size=13, weight=600)
d.box(60, 410, 470, 70, 'Delay ① API', ['revoked roles still pass for 30 min,', 'newly granted ones get 403 for 30 min'], color='red')
d.box(570, 410, 470, 70, 'Delay ② UI', ['the sidebar reads the session_claims cookie', 'only once, when it mounts'], color='red')
d.flow([{'path': [(360, 225), (400, 225)], 'color': 'amber', 'dur': 0.5},
        {'path': [(700, 225), (740, 225)], 'color': 'red', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/11/03-3.svg'))

# =====================================================================
# 2026/11/03-4  pv post: request flow with 401 → refresh → retry
# =====================================================================
d = Diagram(1100, 640, "If roles changed after the token's pv, the request gets a 401 and the client refreshes and retries once")
cl = d.box(40, 120, 180, 70, 'Browser', ['global fetch wrapper'], color='blue')
sv = d.box(320, 120, 240, 70, 'Service API filter', ['verify signature → read pv'], color='gray')
gt = d.box(320, 240, 240, 70, 'PermissionFreshnessGate', ['Caffeine 5s cache'], color='purple')
ac = d.box(660, 240, 200, 70, 'account service', ['/permission-changed-at'], color='gray')
rd = d.box(920, 240, 150, 70, 'Redis', ['MGET user:, tenant:'], color='amber')
ctl = d.box(660, 120, 200, 70, 'Controller', ['200 OK'], color='green')
tk = d.box(660, 400, 200, 70, 'account reissue', ['recompute roles, new pv'], color='blue')
adm = d.box(920, 400, 150, 70, 'Admin console', ['change roles'], color='amber')
d.arrow([(220, 155), (320, 155)], color='blue', label='① request', label_size=12)
d.arrow([(440, 190), (440, 240)], color='gray'); d.text(452, 215, '② isStale?', size=11, anchor='start')
d.arrow([(560, 275), (660, 275)], color='purple', label='③ fetch on miss', dashed=True, label_size=11)
d.arrow([(860, 275), (920, 275)], color='amber', label='④', dashed=True)
d.arrow([(560, 155), (660, 155)], color='green', label='⑤a pass', label_size=12)
d.arrow([(320, 300), (250, 300), (250, 175), (220, 175)], color='red')
d.text(240, 330, '⑤b 401 TOKEN_PERMISSION_CHANGED', size=11, weight=700, color='#dc2626', anchor='start')
d.arrow([(130, 190), (130, 435), (660, 435)], color='blue')
d.text(142, 415, '⑥ refresh once (many concurrent 401s → 1 refresh)', size=11, weight=700, color='#2563eb', anchor='start')
d.arrow([(920, 435), (860, 435)], color='amber', head=True)
d.arrow([(995, 400), (995, 310)], color='amber')
d.text(985, 385, 'afterCommit: evict cache → Lua SET max', size=11, weight=700, color='#d97706', anchor='end')
d.note(40, 520, 1020, 80, ['⑦ Retry the original request exactly once with the new token (new pv) → 200. Concurrent 401s share one refresh.',
                           "Lookup failed (account blip, circuit OPEN)? Let it through (fail-open): that's just how things worked before this gate."], color='muted', size=13)
d.flow([
    {'path': [(220, 155), (320, 155)], 'color': 'blue', 'dur': 0.5},
    {'path': [(440, 190), (440, 240)], 'color': 'gray', 'dur': 0.3},
    {'path': [(560, 275), (660, 275)], 'color': 'purple', 'dur': 0.4},
    {'path': [(860, 275), (920, 275)], 'color': 'amber', 'dur': 0.3},
    {'path': [(920, 290), (860, 290)], 'color': 'amber', 'dur': 0.3},
    {'path': [(660, 290), (560, 290)], 'color': 'purple', 'dur': 0.4, 'label': 'changed-at > pv', 'label_at': (610, 320)},
    {'path': [(320, 300), (250, 300), (250, 175), (220, 175)], 'color': 'red', 'dur': 0.7, 'hold': 0.4},
    {'path': [(130, 190), (130, 435), (660, 435)], 'color': 'blue', 'dur': 0.8},
    {'path': [(660, 450), (130, 450), (130, 190)], 'color': 'blue', 'dur': 0.8},
    {'path': [(220, 170), (320, 170)], 'color': 'blue', 'dur': 0.4},
    {'path': [(560, 170), (660, 170)], 'color': 'green', 'dur': 0.4, 'hold': 1.0},
])
d.save(out('2026/11/03-4.svg'))

# =====================================================================
# 2026/11/03-5  pv post: race timeline
# =====================================================================
d = Diagram(1100, 620, 'Evict before commit, and another request refills the cache with the old DB values',
            'Tokens issued after that carry the old roles under a new pv')
lanes = [('Admin A txn', 120), ('Policy cache', 200), ('B, C reissue', 280), ('Redis changed-at', 360)]
for name, y in lanes:
    d.text(150, y, name, size=13, anchor='end'); d.arrow([(170, y), (1060, y)], color='muted', head=False, width=1)
xs = [250, 400, 550, 700, 880]
for x, t in zip(xs, ['T0', 'T1', 'T2', 'T3', 'T4']):
    d.text(x, 92, t, size=12, color=MUTED)
d.box(200, 100, 100, 40, 'BEGIN · write', color='gray', label_size=12)
d.box(350, 100, 100, 40, 'evictAll', color='amber', label_size=12)
d.box(650, 100, 100, 40, 'COMMIT', color='green', label_size=12)
d.box(350, 180, 100, 40, '(empty)', color='muted', label_size=12)
d.box(500, 180, 130, 40, 'old policy reloaded', color='red', label_size=12)
d.text(640, 200, 'TTL 30s', size=11, color=MUTED, anchor='start')
d.box(500, 260, 100, 40, 'B: pv=T2', color='blue', label_size=12)
d.box(830, 260, 110, 40, 'C: pv=T4', color='blue', label_size=12)
d.box(650, 340, 100, 40, 'tenant=T3', color='amber', label_size=12)
d.arrow([(550, 260), (550, 220)], color='red', head=True)
d.text(560, 240, 'cache miss → DB (uncommitted = old values)', size=11, weight=700, color='#dc2626', anchor='start')
d.arrow([(885, 260), (640, 200)], color='red', head=True, dashed=True, label='cache hit (old policy)', label_dy=-10, label_size=11)
d.note(170, 420, 890, 50, "Gate: T3 > T4?  No → pass.  C's token = { roles = old, pv = T4 }: old roles wear a new pv for 30 min", color='red', size=13)
d.note(170, 500, 890, 90, ["Fixed order:  COMMIT → afterCommit ① evict cache → ② record changed-at (T3')",
                           "Every load after ① reads the committed policy. Tokens with pv < T3' (B's too)",
                           "are all stale, and their reissue reads the fresh cache."], color='green', size=13)
d.flow([
    {'path': [(300, 120), (350, 120)], 'color': 'gray', 'dur': 0.4},
    {'path': [(400, 140), (400, 180)], 'color': 'amber', 'dur': 0.3},
    {'path': [(550, 260), (550, 220)], 'color': 'red', 'dur': 0.5},
    {'path': [(450, 120), (650, 120)], 'color': 'gray', 'dur': 0.5},
    {'path': [(700, 140), (700, 340)], 'color': 'amber', 'dur': 0.5},
    {'path': [(885, 260), (640, 200)], 'color': 'red', 'dur': 0.6, 'hold': 1.2},
])
d.save(out('2026/11/03-5.svg'))

# =====================================================================
# 2026/09/04-1  refresh post: 6 copies
# =====================================================================
d = Diagram(1100, 560, 'One sign-in on the shell, one refresh token, six copies: five web app cookies plus the shell store')
acc = d.box(60, 110, 200, 80, 'account service', ['sign in → access 30 min', 'refresh jti=A (in ledger)'], color='gray')
sh = d.box(360, 110, 220, 80, 'Electron shell', ['SessionManager', 'reissues on a 5-min timer'], color='blue')
d.arrow([(260, 150), (360, 150)], color='gray', label='token pair')
store = d.box(360, 240, 220, 60, '⑥ Shell store', ['safeStorage-encrypted file'], color='blue')
d.arrow([(470, 190), (470, 240)], color='blue', label='save', label_dy=0, label_size=11, label_color=INK)
apps = ['① Web app A cookie', '② Web app B cookie', '③ Web app C cookie', '④ Web app D cookie', '⑤ Web app E cookie']
ys = [95, 175, 255, 335, 415]
for name, y in zip(apps, ys):
    d.box(700, y, 180, 56, name, ['refresh_token = A'], color='amber', label_size=13, sub_size=11)
    d.arrow([(580, 150), (640, 150), (640, y + 28), (700, y + 28)], color='blue', head=True, width=1.5)
    d.arrow([(880, y + 28), (960, y + 28)], color='red', head=True, dashed=True, width=1.5)
d.text(1025, 253, 'Middleware', size=12, weight=700, color='#dc2626'); d.text(1025, 271, 'reissues', size=12, weight=700, color='#dc2626')
d.text(1025, 289, 'on its own', size=12, weight=700, color='#dc2626')
d.text(1025, 307, '(shell unaware)', size=11, weight=600, color=MUTED)
d.arrow([(360, 270), (200, 270), (200, 190)], color='red', head=True, dashed=True, width=1.5, label='shell reissues too', label_dy=14, label_size=11)
d.note(60, 490, 1020, 50, 'Six holders each call /auth/token with the same jti=A: a setup that only worked because tokens never rotated', color='red', size=14)
d.flow([{'path': [(260, 150), (360, 150)], 'color': 'gray', 'dur': 0.5},
        {'path': [(470, 190), (470, 240)], 'color': 'blue', 'dur': 0.3}] +
       [{'path': [(580, 150), (640, 150), (640, y + 28), (700, y + 28)], 'color': 'blue', 'dur': 0.35, 'hold': 0.05} for y in ys] +
       [{'path': [(880, y + 28), (960, y + 28)], 'color': 'red', 'dur': 0.3, 'hold': 0.1} for y in ys] +
       [{'path': [(360, 270), (200, 270), (200, 190)], 'color': 'red', 'dur': 0.5, 'hold': 1.0}])
d.save(out('2026/09/04-1.svg'))

# =====================================================================
# 2026/09/04-2  refresh post: misjudged rotation sequence
# =====================================================================
d = Diagram(1100, 640, 'Another holder shows up with the old token 61s after rotation: flagged as theft, every session revoked')
cols = [('Web app D middleware', 160, 'amber'), ('Web app B middleware', 420, 'amber'), ('account service', 700, 'gray'), ('Redis ledger', 960, 'purple')]
for name, x, c in cols:
    d.box(x - 95, 80, 190, 44, name, color=c, label_size=13)
    d.arrow([(x, 124), (x, 560)], color='muted', head=False, width=1, dashed=True)
d.arrow([(160, 170), (700, 170)], color='amber', label='① 30 min later: /auth/token (A)', label_dy=-10)
d.arrow([(700, 200), (960, 200)], color='purple', label='DEL active:A = 1 (winner)', label_dy=-10, label_size=11)
d.arrow([(960, 230), (700, 230)], color='purple', label='register new jti B, rotated:A = DONE(B)  TTL 60s', label_dy=12, label_size=11)
d.arrow([(700, 260), (160, 260)], color='green', label="② new pair (refresh = B): only web app D's cookie has B", label_dy=12)
d.note(80, 300, 940, 36, '… 61 seconds later, the user finally opens the web app B tab. Its refresh cookie still holds A …', color='muted', size=13)
d.arrow([(420, 370), (700, 370)], color='amber', label='③ /auth/token (A)', label_dy=-10)
d.arrow([(700, 400), (960, 400)], color='purple', label='DEL active:A = 0, GET rotated:A = nil (TTL expired)', label_dy=-10, label_size=11)
d.arrow([(960, 440), (700, 440)], color='red', label='④ "reuse = theft" → revokeAll: delete active:B, rotated:A = REVOKED', label_dy=17, label_size=11)
d.arrow([(700, 480), (420, 480)], color='red', label='401', label_dy=-10)
d.arrow([(700, 520), (160, 520)], color='red', label='⑤ the next reissue (B) also gets 401: all six are signed out', label_dy=12)
d.note(80, 575, 940, 50, ["The \"theft\" was a copy I had planted myself. Concurrent tabs (60s grace) were handled,",
                          "but independent holders with no upper bound on timing were never considered."], color='red', size=13)
d.flow([
    {'path': [(160, 170), (700, 170)], 'color': 'amber', 'dur': 0.6},
    {'path': [(700, 200), (960, 200)], 'color': 'purple', 'dur': 0.4},
    {'path': [(960, 230), (700, 230)], 'color': 'purple', 'dur': 0.4},
    {'path': [(700, 260), (160, 260)], 'color': 'green', 'dur': 0.6, 'hold': 0.8},
    {'path': [(420, 370), (700, 370)], 'color': 'amber', 'dur': 0.5},
    {'path': [(700, 400), (960, 400)], 'color': 'purple', 'dur': 0.4},
    {'path': [(960, 440), (700, 440)], 'color': 'red', 'dur': 0.5},
    {'path': [(700, 480), (420, 480)], 'color': 'red', 'dur': 0.4},
    {'path': [(700, 520), (160, 520)], 'color': 'red', 'dur': 0.6, 'hold': 1.2},
])
d.save(out('2026/09/04-2.svg'))

# =====================================================================
# 2026/11/02-1  circuit breaker: topology
# =====================================================================
d = Diagram(1100, 560, "Each service API's access gate calls account; on a cache miss, the request thread waits for the reply")
d.group(40, 90, 560, 330, 'Service API (×9, all built the same way)')
d.box(70, 130, 150, 60, 'Auth filter', ['JWT signature check'], color='gray')
d.box(70, 220, 150, 60, 'Access gate', ['Caffeine 60s / 10s'], color='purple')
d.box(70, 310, 150, 60, 'Business logic', color='gray')
d.arrow([(145, 190), (145, 220)], color='gray'); d.arrow([(145, 280), (145, 310)], color='gray')
d.box(300, 125, 270, 60, 'WebClient (.block())', ['connect 3s · response 10s'], color='amber')
d.arrow([(220, 250), (260, 250), (260, 155), (300, 155)], color='purple'); d.text(268, 215, 'cache miss', size=11, weight=700, color='#7c3aed', anchor='start')
d.box(300, 290, 270, 60, 'Notification · mail calls', ['fire-and-forget / sync'], color='amber')
d.arrow([(220, 340), (260, 340), (260, 320), (300, 320)], color='gray')
acc = d.box(700, 120, 220, 70, 'account service', ['source of truth for roles'], color='gray')
noti = d.box(700, 240, 220, 60, 'Notification service', color='gray')
mail = d.box(700, 340, 220, 60, 'Mail service', color='gray')
d.arrow([(570, 142), (700, 142)], color='blue', label='[account-access]', label_dy=-10, label_size=11)
d.arrow([(570, 170), (700, 170)], color='blue', label='[account-read]', label_dy=12, label_size=11)
d.arrow([(570, 310), (640, 310), (640, 270), (700, 270)], color='green'); d.text(652, 250, '[notification]', size=11, weight=700, color='#059669', anchor='start')
d.arrow([(570, 330), (640, 330), (640, 370), (700, 370)], color='green'); d.text(632, 384, '[mail-send]', size=11, weight=700, color='#059669', anchor='end')
d.note(40, 450, 1020, 80, ['Before: timeouts and caches, but nothing to stop follow-up calls during repeated failures; a failed check meant allow (fail-open).',
                           "After: 4 circuits (target × meaning of failure). account gets two, so slow list queries can't open the access-check circuit."], color='muted', size=13)
d.flow([
    {'path': [(145, 190), (145, 220)], 'color': 'gray', 'dur': 0.3},
    {'path': [(220, 250), (260, 250), (260, 155), (300, 155)], 'color': 'purple', 'dur': 0.5},
    {'path': [(570, 142), (700, 142)], 'color': 'blue', 'dur': 0.4, 'hold': 0.6},
    {'path': [(700, 160), (570, 160)], 'color': 'blue', 'dur': 0.4},
    {'path': [(145, 280), (145, 310)], 'color': 'gray', 'dur': 0.3},
    {'path': [(220, 340), (260, 340), (260, 320), (300, 320)], 'color': 'gray', 'dur': 0.4},
    {'path': [(570, 310), (640, 310), (640, 270), (700, 270)], 'color': 'green', 'dur': 0.5, 'hold': 1.0},
])
d.save(out('2026/11/02-1.svg'))

# =====================================================================
# 2026/11/02-2  circuit breaker: request flow with OPEN branch
# =====================================================================
d = Diagram(1100, 640, 'On a cache miss, if the account call fails or the circuit is open, we now return 503 instead of allowing')
d.box(40, 90, 170, 56, 'Request', ['(authenticated)'], color='blue')
d.box(280, 90, 220, 56, 'Allow cache 60s?', color='purple')
d.box(280, 175, 220, 56, 'Deny cache 10s?', color='purple')
d.box(280, 260, 220, 56, 'Circuit state', ['account-access'], color='amber', label_size=13)
d.box(280, 345, 220, 56, 'HTTP GET has-service-role', ['timeout 10s'], color='gray', label_size=13)
d.box(760, 90, 300, 56, 'Pass → controller', color='green')
d.box(760, 175, 300, 56, '403 access denied', ['SERVICE_ACCESS_DENIED'], color='red')
d.box(760, 260, 300, 56, "503 can't decide, no HTTP call", ['OPEN → CallNotPermittedException at once'], color='red', label_size=13)
d.arrow([(210, 118), (280, 118)], color='blue')
d.arrow([(500, 118), (760, 118)], color='green', label='hit', label_dy=-10, label_size=12)
d.arrow([(390, 146), (390, 175)], color='gray'); d.text(400, 160, 'miss', size=11, anchor='start')
d.arrow([(500, 203), (760, 203)], color='red', label='hit', label_dy=-10, label_size=12)
d.arrow([(390, 231), (390, 260)], color='gray'); d.text(400, 245, 'miss', size=11, anchor='start')
d.arrow([(500, 288), (760, 288)], color='red', label='OPEN', label_dy=-10, label_size=12)
d.arrow([(390, 316), (390, 345)], color='gray'); d.text(400, 330, 'CLOSED / HALF_OPEN', size=11, anchor='start')
rows = [('true → cache allow for 60s → pass', 'green'), ('false → cache deny for 10s → 403', 'red'),
        ('connection error · timeout · 5xx → recorded as failure → 503', 'red'), ('4xx (401·403·429) → not counted (ignored) → 503 + ERROR log (status only)', 'red')]
for i, (t, c) in enumerate(rows):
    y = 330 + i * 42
    d.box(600, y, 460, 34, t, color=c, label_size=12)
    d.arrow([(500, 373), (550, 373), (550, y + 17), (600, y + 17)], color=c, width=1.5)
d.note(40, 520, 490, 56, ['Before (fail-open): every failure → return true', 'every 15s of outage opened access to all services'], color='red', size=13)
d.note(570, 520, 490, 56, ['Circuit: 30s window · min 10 calls · failure ≥ 50% → OPEN 15s', '→ HALF_OPEN, 3 trial calls → CLOSED / OPEN'], color='amber', size=13)
d.note(40, 590, 1020, 40, "Failures aren't cached · an OPEN circuit isn't tied to liveness · turning the circuit off doesn't bring back \"failed check = allow\"", color='muted', size=13)
d.flow([
    {'path': [(210, 118), (280, 118)], 'color': 'blue', 'dur': 0.4},
    {'path': [(390, 146), (390, 175)], 'color': 'gray', 'dur': 0.25},
    {'path': [(390, 231), (390, 260)], 'color': 'gray', 'dur': 0.25},
    {'path': [(390, 316), (390, 345)], 'color': 'gray', 'dur': 0.25},
    {'path': [(500, 373), (550, 373), (550, 431), (600, 431)], 'color': 'red', 'dur': 0.5, 'hold': 0.8},
    {'path': [(210, 130), (280, 130)], 'color': 'blue', 'dur': 0.4},
    {'path': [(390, 146), (390, 175)], 'color': 'gray', 'dur': 0.25},
    {'path': [(390, 231), (390, 260)], 'color': 'gray', 'dur': 0.25},
    {'path': [(500, 288), (760, 288)], 'color': 'red', 'dur': 0.5, 'hold': 1.0},
])
d.save(out('2026/11/02-2.svg'))

# =====================================================================
# 2026/09/03-1  LiveKit: architecture
# =====================================================================
d = Diagram(1100, 600, 'The backend only manages the call lifecycle',
            'Media: LiveKit · Signaling: STOMP and push · Settlement: webhooks')
web = d.box(40, 120, 150, 60, 'Clients', ['web · app · desktop'], color='blue')
api = d.box(380, 110, 260, 80, 'Messenger API (CallService)', ['create · accept · decline · leave', 'state machine · settlement'], color='gray')
lk = d.box(380, 300, 260, 80, 'LiveKit SFU (self-hosted)', ['WebRTC · built-in TURN', 'rooms · participants'], color='purple')
redis = d.box(800, 110, 240, 60, 'Redis pub/sub', ['STOMP fan-out (multi-instance)'], color='amber')
push = d.box(800, 210, 240, 60, 'Push (FCM / APNs VoIP)', ['incoming calls in background'], color='amber')
db = d.box(800, 310, 240, 60, 'MySQL', ['call_session · call_participant'], color='muted')
d.arrow([(190, 140), (380, 140)], color='blue', label='① REST POST /calls, /join, /leave', label_dy=-10, label_size=12)
d.arrow([(380, 165), (190, 165)], color='green', label='② STOMP /topic/user.{id} CALL_*', label_dy=12, label_size=12)
d.arrow([(640, 140), (800, 140)], color='amber', width=1.5)
d.arrow([(640, 160), (800, 240)], color='amber', width=1.5, label='③', label_dy=-10)
d.arrow([(640, 180), (680, 180), (680, 340), (800, 340)], color='muted', width=1.5)
d.arrow([(510, 190), (510, 300)], color='purple')
d.text(498, 245, 'token signing · createRoom / deleteRoom', size=11, weight=700, color=INK, anchor='end')
d.arrow([(540, 300), (540, 190)], color='red')
d.text(700, 286, 'webhook (JWT signed by LiveKit)', size=11, weight=700, color='#dc2626', anchor='start')
d.text(700, 302, 'participant_joined / left · room_finished', size=11, weight=700, color='#dc2626', anchor='start')
d.arrow([(190, 180), (115, 180), (115, 340), (380, 340)], color='purple', label='④ WebRTC media (UDP/TCP)', label_dy=-10, label_size=12)
d.note(40, 430, 1020, 60, ['Only the server signs tokens (identity = userId, fixed room, TTL 1h). CALL_* types are added to the existing user topic.',
                           'Webhooks are the source of truth for settlement: REST leave may never arrive (tab killed, app crash).'], color='muted', size=13)
d.note(40, 510, 1020, 50, 'RINGING ─(join)→ ACTIVE ─(leave, ≤ 1 left)→ ENDED   |   (decline, 1:1)→ DECLINED   |   (no answer for 45s)→ MISSED', color='green', size=13)
d.flow([
    {'path': [(190, 140), (380, 140)], 'color': 'blue', 'dur': 0.5},
    {'path': [(640, 140), (800, 140)], 'color': 'amber', 'dur': 0.4},
    {'path': [(640, 160), (800, 240)], 'color': 'amber', 'dur': 0.4},
    {'path': [(380, 165), (190, 165)], 'color': 'green', 'dur': 0.5, 'hold': 0.4},
    {'path': [(190, 180), (115, 180), (115, 340), (380, 340)], 'color': 'purple', 'dur': 0.8, 'hold': 0.4},
    {'path': [(540, 300), (540, 190)], 'color': 'red', 'dur': 0.5, 'hold': 1.0},
])
d.save(out('2026/09/03-1.svg'))

# =====================================================================
# 2026/09/03-2  LiveKit: settlement race sequence (before / after)
# =====================================================================
d = Diagram(1100, 640, 'If the webhook marks B as LEFT first, the REST leave that follows returns early',
            '"Already LEFT" skips the end-of-call check and the CALL_ENDED broadcast')
cols = [('Callee B (browser)', 150, 'blue'), ('LiveKit', 400, 'purple'), ('Messenger API', 650, 'gray'), ('Caller A', 950, 'blue')]
for name, x, c in cols:
    d.box(x - 85, 80, 170, 44, name, color=c, label_size=13)
    d.arrow([(x, 124), (x, 600)], color='muted', head=False, width=1, dashed=True)
d.text(60, 150, 'Before', size=13, weight=700, color='#dc2626', anchor='start')
d.arrow([(150, 170), (400, 170)], color='blue', label='① LiveKit disconnect', label_dy=-10, label_size=12)
d.arrow([(400, 205), (650, 205)], color='purple', label='② webhook participant_left(B)', label_dy=-10, label_size=12)
d.text(700, 225, 'B.state = LEFT  (no end-of-call check)', size=11, weight=600, color=MUTED, anchor='start')
d.arrow([(150, 250), (650, 250)], color='blue', label='③ POST /calls/{id}/leave', label_dy=-10, label_size=12)
d.text(700, 270, 'state == LEFT → return  (1ms)', size=11, weight=700, color='#dc2626', anchor='start')
d.arrow([(650, 300), (950, 300)], color='red', dashed=True, label='no CALL_ENDED', label_dy=-10, label_size=12)
d.note(760, 320, 280, 36, 'A stuck in call · ghost banner · 409', color='red', size=12)
d.text(60, 390, 'After', size=13, weight=700, color='#059669', anchor='start')
d.arrow([(150, 410), (400, 410)], color='blue', label='① disconnect', label_dy=-10, label_size=12)
d.arrow([(400, 445), (650, 445)], color='purple', label='② participant_left(B)', label_dy=-10, label_size=12)
d.text(668, 465, '→ LEFT → settleIfNoLongerViable → joined ≤ 1 → ENDED', size=11, weight=600, color=INK, anchor='start')
d.arrow([(650, 495), (950, 495)], color='green', label='CALL_ENDED', label_dy=-10, label_size=12)
d.arrow([(150, 540), (650, 540)], color='blue', label='③ POST /leave', label_dy=-10, label_size=12)
d.text(668, 560, 'settleIfNoLongerViable → isFinished() → return  (idempotent)', size=11, weight=600, color='#059669', anchor='start')
d.flow([
    {'path': [(150, 170), (400, 170)], 'color': 'blue', 'dur': 0.4},
    {'path': [(400, 205), (650, 205)], 'color': 'purple', 'dur': 0.4},
    {'path': [(150, 250), (650, 250)], 'color': 'blue', 'dur': 0.6, 'hold': 0.3},
    {'path': [(650, 300), (950, 300)], 'color': 'red', 'dur': 0.5, 'hold': 0.8},
    {'path': [(150, 410), (400, 410)], 'color': 'blue', 'dur': 0.4},
    {'path': [(400, 445), (650, 445)], 'color': 'purple', 'dur': 0.4},
    {'path': [(650, 495), (950, 495)], 'color': 'green', 'dur': 0.5},
    {'path': [(150, 540), (650, 540)], 'color': 'blue', 'dur': 0.6, 'hold': 1.2},
])
d.save(out('2026/09/03-2.svg'))

# =====================================================================
# 2026/09/03-3  LiveKit: multi-device bell
# =====================================================================
d = Diagram(1100, 560, "STOMP topics are per user, so excludeUserId can't leave out just one of the responder's devices",
            'Send to everyone and let each client recognize its own echo')
d.text(60, 110, 'Before', size=13, weight=700, color='#dc2626', anchor='start')
d.box(60, 130, 160, 56, "B's device A (web)", ['Accept button'], color='blue', label_size=13, sub_size=11)
d.box(330, 130, 200, 56, 'Messenger API', ['CALL_ACCEPTED', 'excludeUserId = B'], color='gray', label_size=13, sub_size=11)
d.box(640, 130, 180, 56, '/topic/user.{B}', ["all of B's devices subscribe"], color='amber', label_size=13, sub_size=11)
d.box(880, 100, 190, 50, "B's device A (web)", color='blue', label_size=12)
d.box(880, 170, 190, 50, "B's device B (phone) 🔔", color='red', label_size=12)
d.arrow([(220, 158), (330, 158)], color='blue', label='POST /join', label_dy=-10, label_size=11)
d.arrow([(530, 158), (640, 158)], color='red', dashed=True, label='B excluded', label_dy=-10, label_size=11)
d.text(585, 172, 'not sent', size=11, weight=700, color='#dc2626')
d.arrow([(820, 150), (880, 125)], color='muted', width=1); d.arrow([(820, 165), (880, 195)], color='muted', width=1)
d.text(560, 240, "The server has no way to say \"all of B's devices except A\" → the phone keeps ringing", size=12, weight=700, color='#dc2626')
d.text(60, 280, 'After', size=13, weight=700, color='#059669', anchor='start')
d.box(60, 300, 160, 56, "B's device A (web)", ['_acceptingCallId = id'], color='blue', label_size=13, sub_size=11)
d.box(330, 300, 200, 56, 'Messenger API', ['CALL_ACCEPTED', 'excludeUserId = null (all)'], color='gray', label_size=13, sub_size=11)
d.box(640, 300, 180, 56, '/topic/user.{B}', color='amber', label_size=13)
d.box(880, 270, 190, 50, 'Device A: own echo → ignore', color='green', label_size=11)
d.box(880, 340, 190, 50, 'Device B: my userId JOINED', ['→ dismiss ringing 🔕'], color='green', label_size=11, sub_size=10)
d.arrow([(220, 328), (330, 328)], color='blue', label='POST /join', label_dy=-10, label_size=11)
d.arrow([(530, 328), (640, 328)], color='green', label='published', label_dy=-10, label_size=11)
d.arrow([(820, 320), (880, 295)], color='green', width=1.5); d.arrow([(820, 335), (880, 365)], color='green', width=1.5)
d.note(60, 410, 1020, 56, ['+ CALL_CANCELLED push to every participant → clears CallKit / service worker ringing.',
                           '(Two months later: iOS VoIP push was narrowed back to CALL_RINGING only)'], color='muted', size=13)
d.note(60, 480, 1020, 56, ['The server can\'t tell "this device" from "my other device" (same userId).',
                           "Only the client's in-progress flag can."], color='green', size=13)
d.flow([
    {'path': [(220, 158), (330, 158)], 'color': 'blue', 'dur': 0.4},
    {'path': [(530, 158), (640, 158)], 'color': 'red', 'dur': 0.4, 'hold': 0.8},
    {'path': [(220, 328), (330, 328)], 'color': 'blue', 'dur': 0.4},
    {'path': [(530, 328), (640, 328)], 'color': 'green', 'dur': 0.4},
    {'path': [(820, 320), (880, 295)], 'color': 'green', 'dur': 0.3},
    {'path': [(820, 335), (880, 365)], 'color': 'green', 'dur': 0.3, 'hold': 1.2},
])
d.save(out('2026/09/03-3.svg'))

# =====================================================================
# 2026/10/27-1  Boot4: final vs open LAZY flow
# =====================================================================
d = Diagram(1100, 620, "A final entity can't be proxied, so its associations load right away",
            'Once it is open, a proxy goes in instead, and touching it outside the transaction throws')
d.box(40, 110, 240, 60, 'repo.findById(purchase)', ['inside a transaction'], color='blue')
d.box(340, 110, 300, 60, 'SELECT * FROM stock_purchase', ['WHERE id = ?'], color='gray')
d.box(700, 110, 360, 60, 'Is clientEntity final?', ['@ManyToOne(fetch = LAZY): the code is identical'], color='amber')
d.arrow([(280, 140), (340, 140)], color='blue'); d.arrow([(640, 140), (700, 140)], color='gray')
d.text(60, 215, 'final (Kotlin 1.9 plugin.jpa)', size=13, weight=700, color='#dc2626', anchor='start')
d.box(40, 235, 480, 60, "No proxy possible → secondary select runs now", ['SELECT * FROM client WHERE id = ?'], color='red')
d.box(40, 325, 480, 50, 'purchase.clientEntity = real object', color='muted', label_size=13)
d.box(40, 405, 480, 50, 'Transaction ends (S3 upload etc., no persistence context)', color='muted', label_size=13)
d.box(40, 485, 480, 60, 'purchase.clientEntity.name → works', ['effectively EAGER'], color='red')
d.text(600, 215, 'open (Kotlin 2.x plugin.jpa / allOpen)', size=13, weight=700, color='#059669', anchor='start')
d.box(580, 235, 480, 60, 'ByteBuddy subclass proxy created', ['holds only the id, no select'], color='green')
d.box(580, 325, 480, 50, 'purchase.clientEntity = Proxy(id = …)', color='muted', label_size=13)
d.box(580, 405, 480, 50, 'Transaction ends', color='muted', label_size=13)
d.box(580, 485, 480, 60, 'purchase.clientEntity.name → LazyInitializationException', ['no session'], color='green')
for x in (280, 820):
    d.arrow([(x, 295), (x, 325)], color='gray'); d.arrow([(x, 375), (x, 405)], color='gray'); d.arrow([(x, 455), (x, 485)], color='gray')
d.arrow([(880, 170), (880, 200), (280, 200), (280, 235)], color='red', width=1.5, label='yes', label_dy=-10, label_size=11)
d.arrow([(880, 170), (880, 235)], color='green', width=1.5); d.text(892, 215, 'no', size=11, weight=700, color='#059669', anchor='start')
d.note(40, 565, 1020, 40, 'All 67 @ManyToOne said LAZY, but because all 232 entities were final, every one of the 67 was loading eagerly', color='amber', size=13)
d.flow([
    {'path': [(280, 140), (340, 140)], 'color': 'blue', 'dur': 0.3}, {'path': [(640, 140), (700, 140)], 'color': 'gray', 'dur': 0.3},
    {'path': [(880, 170), (880, 200), (280, 200), (280, 235)], 'color': 'red', 'dur': 0.7},
    {'path': [(280, 295), (280, 325)], 'color': 'red', 'dur': 0.2}, {'path': [(280, 375), (280, 405)], 'color': 'red', 'dur': 0.2}, {'path': [(280, 455), (280, 485)], 'color': 'red', 'dur': 0.2, 'hold': 0.6},
    {'path': [(880, 170), (880, 235)], 'color': 'green', 'dur': 0.4},
    {'path': [(820, 295), (820, 325)], 'color': 'green', 'dur': 0.2}, {'path': [(820, 375), (820, 405)], 'color': 'green', 'dur': 0.2}, {'path': [(820, 455), (820, 485)], 'color': 'green', 'dur': 0.2, 'hold': 1.0},
])
d.save(out('2026/10/27-1.svg'))

# =====================================================================
# 2026/10/27-2  Boot4: fake vs real fetch join
# =====================================================================
d = Diagram(1100, 560, 'The SQL looks the same, but the HQL join is a different kind',
            "An entity join doesn't populate the association; only an association-path join does")
d.text(60, 100, 'Fake fetch join (179 places)', size=14, weight=700, color='#dc2626', anchor='start')
d.box(40, 120, 500, 70, '.innerJoin(QClient).on(QClient.id.eq(p.client.id)).fetchJoin()', color='red', label_size=12)
d.box(40, 215, 500, 56, 'HQL: join ClientEntity c on c.id = p.client.id', ["entity join: Hibernate doesn't know it relates to p.client"], color='muted', label_size=12, sub_size=11)
d.box(40, 296, 500, 56, 'SQL: ... INNER JOIN client c ON c.id = p.client_id', color='muted', label_size=12)
d.box(40, 377, 500, 70, 'Result mapping: p.client = proxy (uninitialized)', ['hidden by the secondary select while final → exception / N+1 once open'], color='red', label_size=12, sub_size=11)
d.text(580, 100, 'Real fetch join', size=14, weight=700, color='#059669', anchor='start')
d.box(560, 120, 500, 70, '.innerJoin(p.client, client).fetchJoin()', ['filter conditions from on move to where'], color='green', label_size=12, sub_size=11)
d.box(560, 215, 500, 56, 'HQL: join fetch p.client c', ['association-path join'], color='muted', label_size=12, sub_size=11)
d.box(560, 296, 500, 56, 'SQL: ... INNER JOIN client c ON c.id = p.client_id  (same)', color='muted', label_size=12)
d.box(560, 377, 500, 70, 'Result mapping: p.client filled from the same ResultSet row', ['safe outside a transaction, one query'], color='green', label_size=12, sub_size=11)
for x in (290, 810):
    d.arrow([(x, 190), (x, 215)], color='gray'); d.arrow([(x, 271), (x, 296)], color='gray'); d.arrow([(x, 352), (x, 377)], color='gray')
d.note(40, 475, 1020, 60, ['With an inner join, moving the on filters (reportDate · companyId) to where is equivalent. Via an intermediate entity, fetch the parent too.',
                           "@Transactional tests can't catch this. The only test that did was one that ran without a transaction."], color='amber', size=12)
d.flow([
    {'path': [(290, 190), (290, 215)], 'color': 'red', 'dur': 0.3}, {'path': [(290, 271), (290, 296)], 'color': 'red', 'dur': 0.3}, {'path': [(290, 352), (290, 377)], 'color': 'red', 'dur': 0.3, 'hold': 0.8},
    {'path': [(810, 190), (810, 215)], 'color': 'green', 'dur': 0.3}, {'path': [(810, 271), (810, 296)], 'color': 'green', 'dur': 0.3}, {'path': [(810, 352), (810, 377)], 'color': 'green', 'dur': 0.3, 'hold': 1.0},
])
d.save(out('2026/10/27-2.svg'))
print('12 English diagrams written')
