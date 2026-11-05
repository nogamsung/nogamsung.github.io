import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from diag import Diagram, INK, MUTED

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

# =====================================================================
# 2026/11/03-3  pv post: roles are issue-time values
# =====================================================================
d = Diagram(1100, 520, '토큰의 roles는 발급 시점 값이다 — 권한을 바꿔도 토큰이 만료될 때까지는 옛 권한이 통한다')
# timeline bar
d.text(80, 110, '09:00', size=13, color=MUTED, anchor='start'); d.text(1020, 110, '09:30', size=13, color=MUTED, anchor='end')
d.arrow([(80, 130), (1020, 130)], color='muted', head=True)
d.text(550, 150, '← access 토큰 수명 30분 →', size=13, weight=600, color=MUTED)
d.box(60, 180, 300, 90, '09:00 로그인', ['access 토큰 발급', 'roles = [A, B, C]  (발급 시점 값)'], color='blue')
d.box(400, 180, 300, 90, '09:10 관리자가 권한 변경', ['DB: roles = [A]', '(B, C 회수)'], color='amber')
d.box(740, 180, 300, 90, '09:10 ~ 09:30 요청', ['서비스 필터는 토큰의 roles만 본다', 'roles = [A, B, C] → 통과 ❌'], color='red')
d.arrow([(360, 225), (400, 225)], color='gray'); d.arrow([(700, 225), (740, 225)], color='gray')
d.box(60, 320, 980, 60, color='muted')
d.text(550, 350, '서비스 API 9개는 account에 묻지 않고 서명만 검증한다 (stateless) — 빠르고 account 장애에 강하지만, 토큰 안의 권한은 갱신되지 않는다', size=14, weight=600)
d.box(60, 410, 470, 70, '지연 ① API', ['회수한 권한이 30분간 통과, 부여한 권한이 30분간 403'], color='red')
d.box(570, 410, 470, 70, '지연 ② 화면', ['사이드바가 session_claims 쿠키를 마운트 때 한 번만 읽는다'], color='red')
d.flow([{'path': [(360, 225), (400, 225)], 'color': 'amber', 'dur': 0.5},
        {'path': [(700, 225), (740, 225)], 'color': 'red', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/11/03-3.svg'))

# =====================================================================
# 2026/11/03-4  pv post: request flow with 401 → refresh → retry
# =====================================================================
d = Diagram(1100, 640, '권한 변경 시각이 토큰의 pv보다 늦으면 401로 끊고, 클라이언트가 재발급 후 한 번 더 시도한다')
cl = d.box(40, 120, 180, 70, '브라우저', ['전역 fetch 래퍼'], color='blue')
sv = d.box(320, 120, 240, 70, '서비스 API 필터', ['서명 검증 → pv 추출'], color='gray')
gt = d.box(320, 240, 240, 70, 'PermissionFreshnessGate', ['Caffeine 5초 캐시'], color='purple')
ac = d.box(660, 240, 200, 70, 'account 서비스', ['/permission-changed-at'], color='gray')
rd = d.box(920, 240, 150, 70, 'Redis', ['MGET user:, tenant:'], color='amber')
ctl = d.box(660, 120, 200, 70, '컨트롤러', ['200 OK'], color='green')
tk = d.box(660, 400, 200, 70, 'account 재발급', ['roles 재계산, 새 pv'], color='blue')
adm = d.box(920, 400, 150, 70, '관리자 콘솔', ['권한 변경'], color='amber')
# static arrows
d.arrow([(220, 155), (320, 155)], color='blue', label='① 요청', label_size=12)
d.arrow([(440, 190), (440, 240)], color='gray'); d.text(452, 215, '② isStale?', size=11, anchor='start')
d.arrow([(560, 275), (660, 275)], color='purple', label='③ 미스면 조회', dashed=True, label_size=11)
d.arrow([(860, 275), (920, 275)], color='amber', label='④', dashed=True)
d.arrow([(560, 155), (660, 155)], color='green', label='⑤a 통과', label_size=12)
d.arrow([(320, 300), (250, 300), (250, 175), (220, 175)], color='red')
d.text(240, 330, '⑤b 401 TOKEN_PERMISSION_CHANGED', size=11, weight=700, color='#dc2626', anchor='start')
d.arrow([(130, 190), (130, 435), (660, 435)], color='blue')
d.text(142, 415, '⑥ refresh 1회 (동시 401 여러 개 → 1회)', size=11, weight=700, color='#2563eb', anchor='start')
d.arrow([(920, 435), (860, 435)], color='amber', head=True)
d.arrow([(995, 400), (995, 310)], color='amber')
d.text(985, 385, 'afterCommit: 캐시 비우기 → Lua SET max', size=11, weight=700, color='#d97706', anchor='end')
d.note(40, 520, 1020, 80, ['⑦ 새 토큰(새 pv)으로 원요청을 정확히 1회 재시도 → 200.  동시에 401이 여러 개 와도 refresh는 한 번만.',
                           '조회 실패(account 순단·회로 OPEN)면 통과(fail-open): 이 게이트가 없던 시절의 동작으로 돌아갈 뿐이다.'], color='muted', size=13)
d.flow([
    {'path': [(220, 155), (320, 155)], 'color': 'blue', 'dur': 0.5},
    {'path': [(440, 190), (440, 240)], 'color': 'gray', 'dur': 0.3},
    {'path': [(560, 275), (660, 275)], 'color': 'purple', 'dur': 0.4},
    {'path': [(860, 275), (920, 275)], 'color': 'amber', 'dur': 0.3},
    {'path': [(920, 290), (860, 290)], 'color': 'amber', 'dur': 0.3},
    {'path': [(660, 290), (560, 290)], 'color': 'purple', 'dur': 0.4, 'label': '변경 시각 > pv', 'label_at': (610, 320)},
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
d = Diagram(1100, 620, '커밋 전에 캐시를 비우면 다른 요청이 옛 DB 값으로 캐시를 다시 채우고, 그 뒤 발급된 토큰은 옛 권한에 새 pv를 단다')
lanes = [('관리자 A 트랜잭션', 120), ('정책 캐시', 200), ('사용자 B·C 재발급', 280), ('Redis 변경 시각', 360)]
for name, y in lanes:
    d.text(150, y, name, size=13, anchor='end'); d.arrow([(170, y), (1060, y)], color='muted', head=False, width=1)
xs = [250, 400, 550, 700, 880]
for x, t in zip(xs, ['T0', 'T1', 'T2', 'T3', 'T4']):
    d.text(x, 92, t, size=12, color=MUTED)
d.box(200, 100, 100, 40, 'BEGIN · 수정', color='gray', label_size=12)
d.box(350, 100, 100, 40, 'evictAll', color='amber', label_size=12)
d.box(650, 100, 100, 40, 'COMMIT', color='green', label_size=12)
d.box(350, 180, 100, 40, '(빈 캐시)', color='muted', label_size=12)
d.box(500, 180, 130, 40, '옛 정책 재적재', color='red', label_size=12)
d.text(640, 200, 'TTL 30초', size=11, color=MUTED, anchor='start')
d.box(500, 260, 100, 40, 'B: pv=T2', color='blue', label_size=12)
d.box(830, 260, 110, 40, 'C: pv=T4', color='blue', label_size=12)
d.box(650, 340, 100, 40, 'tenant=T3', color='amber', label_size=12)
d.arrow([(550, 260), (550, 220)], color='red', head=True)
d.text(560, 240, '캐시 미스 → DB (미커밋 = 옛 값)', size=11, weight=700, color='#dc2626', anchor='start')
d.arrow([(885, 260), (640, 200)], color='red', head=True, dashed=True, label='캐시 히트 (옛 정책)', label_dy=-10, label_size=11)
d.note(170, 420, 890, 50, '게이트: T3 > T4 ?  아니오 → 통과.  C의 토큰 = { roles = 옛 권한, pv = T4 }  — 옛 권한이 새 pv를 달고 30분 굳는다', color='red', size=13)
d.note(170, 500, 890, 90, ['수정 후 순서:  COMMIT → afterCommit ① 캐시 비우기 → ② 시각 기록 (T3\')',
                           '① 뒤의 캐시 적재는 전부 커밋된 새 정책.  pv < T3\' 인 토큰(B 포함)은 전부 낡음 → 재발급 때는 새 캐시.'], color='green', size=13)
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
d = Diagram(1100, 560, '셸이 로그인 한 번으로 받은 refresh 토큰을 웹앱 5개 쿠키와 자기 저장소, 여섯 곳에 복제한다')
acc = d.box(60, 110, 200, 80, 'account 서비스', ['로그인 → access 30분', 'refresh jti=A (원장 등록)'], color='gray')
sh = d.box(360, 110, 220, 80, 'Electron 셸', ['SessionManager', '5분 타이머로 재발급'], color='blue')
d.arrow([(260, 150), (360, 150)], color='gray', label='토큰 쌍')
store = d.box(360, 240, 220, 60, '⑥ 셸 저장소', ['safeStorage 암호화 파일'], color='blue')
d.arrow([(470, 190), (470, 240)], color='blue', label='save', label_dy=0, label_size=11, label_color=INK)
apps = ['① 웹앱 A 쿠키', '② 웹앱 B 쿠키', '③ 웹앱 C 쿠키', '④ 웹앱 D 쿠키', '⑤ 웹앱 E 쿠키']
ys = [95, 175, 255, 335, 415]
for name, y in zip(apps, ys):
    d.box(700, y, 180, 56, name, ['refresh_token = A'], color='amber', label_size=13, sub_size=11)
    d.arrow([(580, 150), (640, 150), (640, y + 28), (700, y + 28)], color='blue', head=True, width=1.5)
    d.arrow([(880, y + 28), (960, y + 28)], color='red', head=True, dashed=True, width=1.5)
d.text(1000, 262, '미들웨어가', size=12, weight=700, color='#dc2626'); d.text(1000, 280, '각자 재발급', size=12, weight=700, color='#dc2626')
d.text(1000, 298, '(셸은 모른다)', size=11, weight=600, color=MUTED)
d.arrow([(360, 270), (200, 270), (200, 190)], color='red', head=True, dashed=True, width=1.5, label='셸도 재발급', label_dy=14, label_size=11)
d.note(60, 490, 1020, 50, '여섯 보유자가 같은 jti=A를 들고 각자 /auth/token 을 부른다 — "회전되지 않는다"는 전제 위에 성립하던 구조', color='red', size=14)
d.flow([{'path': [(260, 150), (360, 150)], 'color': 'gray', 'dur': 0.5},
        {'path': [(470, 190), (470, 240)], 'color': 'blue', 'dur': 0.3}] +
       [{'path': [(580, 150), (640, 150), (640, y + 28), (700, y + 28)], 'color': 'blue', 'dur': 0.35, 'hold': 0.05} for y in ys] +
       [{'path': [(880, y + 28), (960, y + 28)], 'color': 'red', 'dur': 0.3, 'hold': 0.1} for y in ys] +
       [{'path': [(360, 270), (200, 270), (200, 190)], 'color': 'red', 'dur': 0.5, 'hold': 1.0}])
d.save(out('2026/09/04-1.svg'))

# =====================================================================
# 2026/09/04-2  refresh post: misjudged rotation sequence
# =====================================================================
d = Diagram(1100, 640, '회전 뒤 60초가 지나 옛 토큰을 든 다른 보유자가 재발급을 요청하면 "탈취"로 판정되어 전 세션이 폐기된다')
cols = [('웹앱 D 미들웨어', 160, 'amber'), ('웹앱 B 미들웨어', 420, 'amber'), ('account 서비스', 700, 'gray'), ('Redis 원장', 960, 'purple')]
for name, x, c in cols:
    d.box(x - 80, 80, 160, 44, name, color=c, label_size=13)
    d.arrow([(x, 124), (x, 560)], color='muted', head=False, width=1, dashed=True)
# step 1
d.arrow([(160, 170), (700, 170)], color='amber', label='① 30분 뒤 /auth/token (A)', label_dy=-10)
d.arrow([(700, 200), (960, 200)], color='purple', label='DEL active:A = 1 (승자)', label_dy=-10, label_size=11)
d.arrow([(960, 230), (700, 230)], color='purple', label='새 jti B 등록, rotated:A = DONE(B)  TTL 60s', label_dy=12, label_size=11)
d.arrow([(700, 260), (160, 260)], color='green', label='② 새 쌍 (refresh = B) — 웹앱 D 쿠키만 B', label_dy=12)
# time gap
d.note(80, 300, 940, 36, '… 61초 뒤. 사용자가 이제야 웹앱 B 탭을 연다. 쿠키의 refresh 는 여전히 A …', color='muted', size=13)
d.arrow([(420, 370), (700, 370)], color='amber', label='③ /auth/token (A)', label_dy=-10)
d.arrow([(700, 400), (960, 400)], color='purple', label='DEL active:A = 0, GET rotated:A = nil (TTL 만료)', label_dy=-10, label_size=11)
d.arrow([(960, 440), (700, 440)], color='red', label='④ "재사용 = 탈취" → revokeAll: active:B 삭제, rotated:A = REVOKED', label_dy=17, label_size=11)
d.arrow([(700, 480), (420, 480)], color='red', label='401', label_dy=-10)
d.arrow([(700, 520), (160, 520)], color='red', label='⑤ 다음 재발급(B)도 401 — 여섯 곳 모두 로그아웃', label_dy=12)
d.note(80, 575, 940, 50, '탈취로 보이는 것은 사실 내가 심어 둔 사본이었다 — 동시 탭 경합(60초 유예)은 잘 처리했지만, 시차가 상한 없는 독립 보유자는 상정 밖이었다', color='red', size=13)
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
d = Diagram(1100, 560, '서비스 API마다 인증 요청이 지나는 게이트가 account 서비스를 부른다 — 캐시가 비면 스레드가 응답을 기다린다')
d.group(40, 90, 560, 330, '서비스 API (×9, 각각 같은 구조)')
d.box(70, 130, 150, 60, '인증 필터', ['JWT 서명 검증'], color='gray')
d.box(70, 220, 150, 60, '접근 판정 게이트', ['Caffeine 60s / 10s'], color='purple')
d.box(70, 310, 150, 60, '업무 서비스', color='gray')
d.arrow([(145, 190), (145, 220)], color='gray'); d.arrow([(145, 280), (145, 310)], color='gray')
d.box(300, 125, 270, 60, 'WebClient (.block())', ['connect 3s · response 10s'], color='amber')
d.arrow([(220, 250), (260, 250), (260, 155), (300, 155)], color='purple'); d.text(268, 215, '캐시 미스', size=11, weight=700, color='#7c3aed', anchor='start')
d.box(300, 290, 270, 60, '알림 · 메일 호출', ['fire-and-forget / 동기'], color='amber')
d.arrow([(220, 340), (260, 340), (260, 320), (300, 320)], color='gray')
acc = d.box(700, 120, 220, 70, 'account 서비스', ['권한의 단일 진실'], color='gray')
noti = d.box(700, 240, 220, 60, '알림 서비스', color='gray')
mail = d.box(700, 340, 220, 60, '메일 서비스', color='gray')
d.arrow([(570, 142), (700, 142)], color='blue', label='[account-access]', label_dy=-10, label_size=11)
d.arrow([(570, 170), (700, 170)], color='blue', label='[account-read]', label_dy=12, label_size=11)
d.arrow([(570, 310), (640, 310), (640, 270), (700, 270)], color='green'); d.text(652, 250, '[notification]', size=11, weight=700, color='#059669', anchor='start')
d.arrow([(570, 330), (640, 330), (640, 370), (700, 370)], color='green'); d.text(652, 392, '[mail-send]', size=11, weight=700, color='#059669', anchor='start')
d.note(40, 450, 1020, 80, ['이전: 타임아웃·캐시는 있었지만 "반복 장애 중 후속 호출 차단"이 없었고, 판정 실패는 허용(fail-open)이었다.',
                           '이후: 회로 4개 (대상 서비스 × 실패의 의미). account 는 둘로 — 목록 조회가 느려 회로가 열려도 권한 판정은 살린다.'], color='muted', size=13)
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
d = Diagram(1100, 640, '캐시 미스에 account 호출이 실패하거나 회로가 열려 있으면, 이제 허용이 아니라 503을 돌려준다')
d.box(40, 90, 170, 56, '인증된 요청', color='blue')
d.box(280, 90, 220, 56, '허용 캐시 60s?', color='purple')
d.box(280, 175, 220, 56, '거부 캐시 10s?', color='purple')
d.box(280, 260, 220, 56, '회로 상태 (account-access)', color='amber', label_size=13)
d.box(280, 345, 220, 56, 'HTTP GET has-service-role', ['timeout 10s'], color='gray', label_size=13)
d.box(760, 90, 300, 56, '통과 → 컨트롤러', color='green')
d.box(760, 175, 300, 56, '403 접근 거부', ['SERVICE_ACCESS_DENIED'], color='red')
d.box(760, 260, 300, 56, '503 판정 불가 — HTTP 안 나감', ['OPEN → CallNotPermittedException 즉시'], color='red', label_size=13)
d.arrow([(210, 118), (280, 118)], color='blue')
d.arrow([(500, 118), (760, 118)], color='green', label='히트', label_dy=-10, label_size=12)
d.arrow([(390, 146), (390, 175)], color='gray'); d.text(400, 160, '미스', size=11, anchor='start')
d.arrow([(500, 203), (760, 203)], color='red', label='히트', label_dy=-10, label_size=12)
d.arrow([(390, 231), (390, 260)], color='gray'); d.text(400, 245, '미스', size=11, anchor='start')
d.arrow([(500, 288), (760, 288)], color='red', label='OPEN', label_dy=-10, label_size=12)
d.arrow([(390, 316), (390, 345)], color='gray'); d.text(400, 330, 'CLOSED / HALF_OPEN', size=11, anchor='start')
# HTTP outcomes
rows = [('true → 허용 60s 캐시 → 통과', 'green'), ('false → 거부 10s 캐시 → 403', 'red'),
        ('연결 오류 · timeout · 5xx → 회로에 실패 기록 → 503', 'red'), ('4xx(401·403·429) → 집계 제외(ignore) → 503 + ERROR 로그(status만)', 'red')]
for i, (t, c) in enumerate(rows):
    y = 330 + i * 42
    d.box(600, y, 460, 34, t, color=c, label_size=12)
    d.arrow([(500, 373), (550, 373), (550, y + 17), (600, y + 17)], color=c, width=1.5)
d.note(40, 520, 490, 56, ['이전 (fail-open): 모든 실패 → return true', '장애 15초마다 전 서비스 권한이 열리는 셈'], color='red', size=13)
d.note(570, 520, 490, 56, ['회로: 30s 창 · 최소 10회 · 실패율 ≥ 50% → OPEN 15s', '→ HALF_OPEN 3회 시험 → CLOSED / OPEN'], color='amber', size=13)
d.note(40, 590, 1020, 40, '실패 결과는 캐시하지 않는다 · 회로 OPEN 은 liveness 에 연결하지 않는다 · 회로를 꺼도 "판정 실패 = 허용" 으로는 돌아가지 않는다', color='muted', size=13)
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
d = Diagram(1100, 600, '백엔드는 통화 수명주기만 관리한다 — 미디어는 LiveKit, 신호는 STOMP와 푸시, 정산은 webhook')
web = d.box(40, 120, 150, 60, '웹 · 앱 · 데스크톱', ['클라이언트'], color='blue')
api = d.box(380, 110, 260, 80, '메신저 API (CallService)', ['통화 생성·수락·거절·leave', '상태기계 · 정산'], color='gray')
lk = d.box(380, 300, 260, 80, 'LiveKit SFU (자체 호스팅)', ['WebRTC · TURN 내장', '방·참가자 관리'], color='purple')
redis = d.box(800, 110, 240, 60, 'Redis pub/sub', ['STOMP 팬아웃 (다중 인스턴스)'], color='amber')
push = d.box(800, 210, 240, 60, '푸시 (FCM / APNs VoIP)', ['백그라운드 착신'], color='amber')
db = d.box(800, 310, 240, 60, 'MySQL', ['call_session · call_participant'], color='muted')
d.arrow([(190, 140), (380, 140)], color='blue', label='① REST POST /calls, /join, /leave', label_dy=-10, label_size=12)
d.arrow([(380, 165), (190, 165)], color='green', label='② STOMP /topic/user.{id} CALL_*', label_dy=12, label_size=12)
d.arrow([(640, 140), (800, 140)], color='amber', width=1.5)
d.arrow([(640, 160), (800, 240)], color='amber', width=1.5, label='③', label_dy=-10)
d.arrow([(640, 180), (680, 180), (680, 340), (800, 340)], color='muted', width=1.5)
d.arrow([(510, 190), (510, 300)], color='purple')
d.text(498, 245, '토큰 서명 · createRoom / deleteRoom', size=11, weight=700, color=INK, anchor='end')
d.arrow([(540, 300), (540, 190)], color='red')
d.text(700, 286, 'webhook (LiveKit 서명 JWT)', size=11, weight=700, color='#dc2626', anchor='start')
d.text(700, 302, 'participant_joined / left · room_finished', size=11, weight=700, color='#dc2626', anchor='start')
d.arrow([(190, 180), (115, 180), (115, 340), (380, 340)], color='purple', label='④ WebRTC 미디어 (UDP/TCP)', label_dy=-10, label_size=12)
d.note(40, 430, 1020, 60, ['토큰은 서버만 서명 (identity = userId, 방 고정, TTL 1h).  신호는 기존 유저 토픽에 CALL_* 타입을 additive 로 추가.',
                           '정산의 진실은 webhook — REST leave 는 안 올 수도 있다 (탭 강제 종료·앱 크래시).'], color='muted', size=13)
d.note(40, 510, 1020, 50, 'RINGING ─(join)→ ACTIVE ─(leave, 남은 참가자 ≤ 1)→ ENDED   |   (decline 1:1)→ DECLINED   |   (45초 무응답)→ MISSED', color='green', size=13)
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
d = Diagram(1100, 640, 'webhook이 먼저 참가자를 LEFT로 바꾸면, 뒤이어 온 REST leave가 "이미 LEFT"라며 조기 반환해 종료 판정과 CALL_ENDED 방송을 건너뛴다')
cols = [('수신자 B 브라우저', 150, 'blue'), ('LiveKit', 400, 'purple'), ('메신저 API', 650, 'gray'), ('발신자 A', 950, 'blue')]
for name, x, c in cols:
    d.box(x - 85, 80, 170, 44, name, color=c, label_size=13)
    d.arrow([(x, 124), (x, 600)], color='muted', head=False, width=1, dashed=True)
d.text(60, 150, '수정 전', size=13, weight=700, color='#dc2626', anchor='start')
d.arrow([(150, 170), (400, 170)], color='blue', label='① LiveKit disconnect', label_dy=-10, label_size=12)
d.arrow([(400, 205), (650, 205)], color='purple', label='② webhook participant_left(B)', label_dy=-10, label_size=12)
d.text(760, 225, 'B.state = LEFT  (종료 판정 없음)', size=11, weight=600, color=MUTED, anchor='start')
d.arrow([(150, 250), (650, 250)], color='blue', label='③ POST /calls/{id}/leave', label_dy=-10, label_size=12)
d.text(760, 270, 'state == LEFT → return  (1ms)', size=11, weight=700, color='#dc2626', anchor='start')
d.arrow([(650, 300), (950, 300)], color='red', dashed=True, label='CALL_ENDED 없음', label_dy=-10, label_size=12)
d.note(760, 320, 280, 36, 'A 화면 통화 중 · 유령 배너 · 409', color='red', size=12)
d.text(60, 390, '수정 후', size=13, weight=700, color='#059669', anchor='start')
d.arrow([(150, 410), (400, 410)], color='blue', label='① disconnect', label_dy=-10, label_size=12)
d.arrow([(400, 445), (650, 445)], color='purple', label='② participant_left(B)', label_dy=-10, label_size=12)
d.text(760, 465, 'LEFT 전이 → settleIfNoLongerViable → joined ≤ 1 → ENDED', size=11, weight=600, color=INK, anchor='start')
d.arrow([(650, 495), (950, 495)], color='green', label='CALL_ENDED', label_dy=-10, label_size=12)
d.arrow([(150, 540), (650, 540)], color='blue', label='③ POST /leave', label_dy=-10, label_size=12)
d.text(760, 560, 'settleIfNoLongerViable → isFinished() → return  (멱등)', size=11, weight=600, color='#059669', anchor='start')
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
d = Diagram(1100, 560, 'STOMP 토픽은 유저 단위라 excludeUserId로는 응답자의 다른 기기를 가릴 수 없다 — 전원에게 보내고 클라이언트가 자기 echo를 구분한다')
d.text(60, 110, '수정 전', size=13, weight=700, color='#dc2626', anchor='start')
d.box(60, 130, 160, 56, 'B 기기 A (웹)', ['수락 버튼'], color='blue', label_size=13, sub_size=11)
d.box(330, 130, 200, 56, '메신저 API', ['CALL_ACCEPTED', 'excludeUserId = B'], color='gray', label_size=13, sub_size=11)
d.box(640, 130, 180, 56, '/topic/user.{B}', ['B의 모든 기기가 구독'], color='amber', label_size=13, sub_size=11)
d.box(900, 100, 160, 50, 'B 기기 A (웹)', color='blue', label_size=12)
d.box(900, 170, 160, 50, 'B 기기 B (폰) 🔔', color='red', label_size=12)
d.arrow([(220, 158), (330, 158)], color='blue', label='POST /join', label_dy=-10, label_size=11)
d.arrow([(530, 158), (640, 158)], color='red', dashed=True, label='B 제외 → 발행 안 됨', label_dy=-10, label_size=11)
d.arrow([(820, 150), (900, 125)], color='muted', width=1); d.arrow([(820, 165), (900, 195)], color='muted', width=1)
d.text(560, 215, '서버에는 "B의 기기 A만 빼고"를 표현할 수단이 없다 → 폰의 벨이 계속 울린다', size=12, weight=700, color='#dc2626')
d.text(60, 280, '수정 후', size=13, weight=700, color='#059669', anchor='start')
d.box(60, 300, 160, 56, 'B 기기 A (웹)', ['_acceptingCallId = id'], color='blue', label_size=13, sub_size=11)
d.box(330, 300, 200, 56, '메신저 API', ['CALL_ACCEPTED', 'excludeUserId = null (전원)'], color='gray', label_size=13, sub_size=11)
d.box(640, 300, 180, 56, '/topic/user.{B}', color='amber', label_size=13)
d.box(900, 270, 160, 50, '기기 A: 자기 echo → 무시', color='green', label_size=11)
d.box(900, 340, 160, 50, '기기 B: 내 userId JOINED', ['→ 착신 닫기 🔕'], color='green', label_size=11, sub_size=10)
d.arrow([(220, 328), (330, 328)], color='blue', label='POST /join', label_dy=-10, label_size=11)
d.arrow([(530, 328), (640, 328)], color='green', label='발행', label_dy=-10, label_size=11)
d.arrow([(820, 320), (900, 295)], color='green', width=1.5); d.arrow([(820, 335), (900, 365)], color='green', width=1.5)
d.note(60, 420, 1020, 50, '+ CALL_CANCELLED 푸시를 참가자 전원에게 → CallKit / 서비스워커 벨 정리.  (두 달 뒤: iOS VoIP 는 CALL_RINGING 전용으로 다시 좁힘)', color='muted', size=13)
d.note(60, 485, 1020, 50, '서버는 "내 기기"와 "내 다른 기기"를 구분할 수 없다 (둘 다 같은 userId) — 클라이언트의 진행 플래그만이 구분할 수 있다', color='green', size=13)
d.flow([
    {'path': [(220, 158), (330, 158)], 'color': 'blue', 'dur': 0.4},
    {'path': [(530, 158), (640, 158)], 'color': 'red', 'dur': 0.4, 'hold': 0.8},
    {'path': [(220, 328), (330, 328)], 'color': 'blue', 'dur': 0.4},
    {'path': [(530, 328), (640, 328)], 'color': 'green', 'dur': 0.4},
    {'path': [(820, 320), (900, 295)], 'color': 'green', 'dur': 0.3},
    {'path': [(820, 335), (900, 365)], 'color': 'green', 'dur': 0.3, 'hold': 1.2},
])
d.save(out('2026/09/03-3.svg'))

# =====================================================================
# 2026/10/27-1  Boot4: final vs open LAZY flow
# =====================================================================
d = Diagram(1100, 620, 'final 엔티티는 프록시를 만들 수 없어 연관을 즉시 로드한다 — open이 되면 프록시가 들어가고, 트랜잭션 밖 접근이 예외가 된다')
d.box(40, 110, 240, 60, 'repo.findById(purchase)', ['트랜잭션 안'], color='blue')
d.box(340, 110, 300, 60, 'SELECT * FROM stock_purchase', ['WHERE id = ?'], color='gray')
d.box(700, 110, 360, 60, 'clientEntity 가 final 인가?', ['@ManyToOne(fetch = LAZY) — 코드는 둘 다 같다'], color='amber')
d.arrow([(280, 140), (340, 140)], color='blue'); d.arrow([(640, 140), (700, 140)], color='gray')
# final branch (left)
d.text(60, 215, 'final (Kotlin 1.9 plugin.jpa)', size=13, weight=700, color='#dc2626', anchor='start')
d.box(40, 235, 480, 60, '프록시 생성 불가 → 보조 select 즉시 실행', ['SELECT * FROM client WHERE id = ?'], color='red')
d.box(40, 325, 480, 50, 'purchase.clientEntity = 실제 객체', color='muted', label_size=13)
d.box(40, 405, 480, 50, '트랜잭션 종료 (S3 업로드 등 영속성 컨텍스트 없음)', color='muted', label_size=13)
d.box(40, 485, 480, 60, 'purchase.clientEntity.name → 정상 반환', ['사실상 EAGER'], color='red')
# open branch (right)
d.text(600, 215, 'open (Kotlin 2.x plugin.jpa / allOpen)', size=13, weight=700, color='#059669', anchor='start')
d.box(580, 235, 480, 60, 'ByteBuddy 서브클래스 프록시 생성', ['id 만 보유, select 없음'], color='green')
d.box(580, 325, 480, 50, 'purchase.clientEntity = Proxy(id = …)', color='muted', label_size=13)
d.box(580, 405, 480, 50, '트랜잭션 종료', color='muted', label_size=13)
d.box(580, 485, 480, 60, 'purchase.clientEntity.name → LazyInitializationException', ['세션 없음'], color='green')
for x in (280, 820):
    d.arrow([(x, 295), (x, 325)], color='gray'); d.arrow([(x, 375), (x, 405)], color='gray'); d.arrow([(x, 455), (x, 485)], color='gray')
d.arrow([(880, 170), (880, 200), (280, 200), (280, 235)], color='red', width=1.5, label='예', label_dy=-10, label_size=11)
d.arrow([(880, 170), (880, 235)], color='green', width=1.5); d.text(892, 215, '아니오', size=11, weight=700, color='#059669', anchor='start')
d.note(40, 565, 1020, 40, '@ManyToOne 67곳 전부 LAZY 라고 적혀 있었지만, 232개 엔티티가 final 이라 67곳 전부 즉시 로딩으로 돌고 있었다', color='amber', size=13)
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
d = Diagram(1100, 560, 'SQL은 같아 보여도 HQL의 조인 종류가 다르다 — 엔티티 조인은 연관을 채우지 않고, 연관 경로 조인만 채운다')
d.text(60, 100, '가짜 fetch join (179곳)', size=14, weight=700, color='#dc2626', anchor='start')
d.box(40, 120, 500, 70, '.innerJoin(QClient).on(QClient.id.eq(p.client.id)).fetchJoin()', color='red', label_size=12)
d.box(40, 215, 500, 56, 'HQL: join ClientEntity c on c.id = p.client.id', ['엔티티 조인 — Hibernate 는 p.client 와의 관계를 모른다'], color='muted', label_size=12, sub_size=11)
d.box(40, 296, 500, 56, 'SQL: ... INNER JOIN client c ON c.id = p.client_id', color='muted', label_size=12)
d.box(40, 377, 500, 70, '결과 매핑: p.client = 프록시 (미초기화)', ['final 시절엔 보조 select 가 채워 가려짐 → open 이 되자 예외 / N+1'], color='red', label_size=12, sub_size=11)
d.text(580, 100, '진짜 fetch join', size=14, weight=700, color='#059669', anchor='start')
d.box(560, 120, 500, 70, '.innerJoin(p.client, client).fetchJoin()', ['on 의 필터 조건은 where 로'], color='green', label_size=12, sub_size=11)
d.box(560, 215, 500, 56, 'HQL: join fetch p.client c', ['연관 경로 조인'], color='muted', label_size=12, sub_size=11)
d.box(560, 296, 500, 56, 'SQL: ... INNER JOIN client c ON c.id = p.client_id  (동일)', color='muted', label_size=12)
d.box(560, 377, 500, 70, '결과 매핑: p.client 를 같은 ResultSet 행에서 채움', ['트랜잭션 밖에서도 안전, 쿼리 1개'], color='green', label_size=12, sub_size=11)
for x in (290, 810):
    d.arrow([(x, 190), (x, 215)], color='gray'); d.arrow([(x, 271), (x, 296)], color='gray'); d.arrow([(x, 352), (x, 377)], color='gray')
d.note(40, 475, 1020, 60, ['inner join 이면 on 의 필터(reportDate·companyId)를 where 로 옮겨도 동치.  중간 엔티티를 거치면 상위 연관도 fetch 해야 한다.',
                           '@Transactional 테스트는 이 결함을 못 잡는다 — 트랜잭션 없이 돌리는 테스트 하나가 유일하게 잡았다.'], color='amber', size=12)
d.flow([
    {'path': [(290, 190), (290, 215)], 'color': 'red', 'dur': 0.3}, {'path': [(290, 271), (290, 296)], 'color': 'red', 'dur': 0.3}, {'path': [(290, 352), (290, 377)], 'color': 'red', 'dur': 0.3, 'hold': 0.8},
    {'path': [(810, 190), (810, 215)], 'color': 'green', 'dur': 0.3}, {'path': [(810, 271), (810, 296)], 'color': 'green', 'dur': 0.3}, {'path': [(810, 352), (810, 377)], 'color': 'green', 'dur': 0.3, 'hold': 1.0},
])
d.save(out('2026/10/27-2.svg'))
print('12 diagrams written')
