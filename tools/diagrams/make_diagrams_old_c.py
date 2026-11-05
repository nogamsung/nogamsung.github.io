"""2024 기존 글을 다시 쓰며 추가한 다이어그램 (그룹 C).
실행: python3 tools/diagrams/make_diagrams_old_c.py "$PWD"
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from diag import Diagram, INK, MUTED

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

G = {'gray': '#1f2937', 'muted': '#6b7280', 'blue': '#2563eb', 'green': '#059669', 'red': '#dc2626', 'amber': '#d97706', 'purple': '#7c3aed'}

# =====================================================================
# 2024/06/12-1  Spring Boot upgrade path
# =====================================================================
d = Diagram(1100, 500, '한 번에 넘어가지 않고 두 단계로 — 2.x 마지막 버전에서 먼저 정리하고 3.3으로 넘어간다')
stages = [
    (40, '출발', ['Spring Boot 2.7.1', 'Java 11', 'Gradle 7.6.1', 'javax.*'], 'gray'),
    (400, '1단계: 2.x 마지막 버전', ['Spring Boot 2.7.18', 'Java 21', 'Gradle은 그대로', '의존성·deprecated 확인'], 'blue'),
    (760, '2단계: 3.x 최신 버전', ['Spring Boot 3.3.0', 'dependency-management 1.1.5', 'Gradle 8.7', 'Querydsl 5.0.0:jakarta'], 'green'),
]
for x, lab, sub, c in stages:
    d.box(x, 96, 300, 170, lab, sub, color=c, label_size=16, sub_size=13)
d.arrow([(340, 181), (400, 181)], color='blue')
d.arrow([(700, 181), (760, 181)], color='green')
d.group(40, 300, 1020, 140, '3단계: 3.3에서 컴파일과 실행을 깨는 것들 — 코드 변경', color='amber')
fixes = [('javax → jakarta', 'import 일괄 변경'), ('SecurityConfig', '람다 DSL로 재작성'),
         ('@Table', 'schema.table → catalog'), ('Querydsl', '템플릿 코드 점검'), ('buildspec.yml', 'Java 버전 변경')]
for i, (lab, sub) in enumerate(fixes):
    d.box(52 + i * 202, 338, 190, 80, lab, [sub], color='amber', label_size=14, sub_size=12)
d.arrow([(910, 266), (910, 300)], color='amber')
d.text(550, 472, '2.7.18에서 deprecated 경고를 먼저 걷어 내면, 3.x로 넘어갈 때 깨지는 곳이 "제거된 API"로 좁혀진다', size=13, weight=600, color=MUTED)
d.flow([{'path': [(190, 181), (340, 181), (400, 181), (550, 181)], 'color': 'blue', 'dur': 1.2, 'hold': 0.3},
        {'path': [(550, 181), (700, 181), (760, 181), (910, 181)], 'color': 'green', 'dur': 1.2, 'hold': 0.3},
        {'path': [(910, 266), (910, 300)], 'color': 'amber', 'dur': 0.5, 'hold': 1.0}])
d.save(out('2024/06/12-1.svg'))

# =====================================================================
# 2024/07/24-1  race condition vs distributed lock timeline
# =====================================================================
d = Diagram(1100, 560, '락이 없으면 두 서버가 같은 상태를 읽고 둘 다 처리한다 — 분산 락은 같은 key의 요청을 한 줄로 세운다')
d.group(30, 84, 1040, 210, '락 없음 — 서버마다 따로 확인한다', color='red')
d.text(80, 150, '서버 A', size=14, weight=700, anchor='middle')
d.text(80, 230, '서버 B', size=14, weight=700, anchor='middle')
d.box(140, 128, 200, 44, '① 조회: 아직 없음', color='gray', label_size=13)
d.box(300, 208, 200, 44, '② 조회: 아직 없음', color='gray', label_size=13)
d.box(500, 128, 210, 44, '③ 처리하고 저장', color='blue', label_size=13)
d.box(680, 208, 220, 44, '④ 처리하고 또 저장', color='red', label_size=13)
d.note(920, 138, 130, 104, ['같은 요청이', '두 번 처리된다'], color='red', size=13)
d.text(540, 274, 'B가 조회한 시점에는 A가 아직 저장하지 않았다 — synchronized는 JVM 하나 안에서만 막는다', size=12, weight=600, color=MUTED)
d.group(30, 314, 1040, 210, "Redisson 락 — key = 'function_' + #request.id", color='green')
d.text(80, 380, '서버 A', size=14, weight=700, anchor='middle')
d.text(80, 460, '서버 B', size=14, weight=700, anchor='middle')
d.box(140, 358, 140, 44, '락 획득', color='green', label_size=13)
d.box(300, 358, 230, 44, '조회 · 처리 · 저장', color='blue', label_size=13)
d.box(550, 358, 110, 44, 'unlock', color='green', label_size=13)
d.box(140, 438, 520, 44, 'tryLock 대기 (최대 waitTime 5초)', color='amber', dashed=True, label_size=13)
d.box(680, 438, 220, 44, '락 획득 → 조회', color='green', label_size=13)
d.note(920, 368, 130, 104, ['A가 저장한', '결과가 보인다'], color='green', size=13)
d.text(540, 504, '같은 key를 가진 요청만 기다린다 — key가 다른 요청은 서로 막지 않는다', size=12, weight=600, color=MUTED)
d.flow([{'path': [(140, 150), (710, 150)], 'color': 'blue', 'dur': 1.4},
        {'path': [(300, 230), (900, 230)], 'color': 'red', 'dur': 1.4, 'hold': 0.5},
        {'path': [(140, 380), (660, 380)], 'color': 'green', 'dur': 1.4},
        {'path': [(660, 460), (900, 460)], 'color': 'green', 'dur': 0.8, 'hold': 0.8}])
d.save(out('2024/07/24-1.svg'))

# =====================================================================
# 2024/07/24-2  RedissonLockAspect flow
# =====================================================================
d = Diagram(1100, 420, 'RedissonLockAspect가 하는 일 — key 계산, tryLock, 본 메서드 실행, finally에서 unlock')
row = [('메서드 호출', '@RedissonLock', 'gray'), ('key 계산', 'SpEL: #request.id', 'blue'),
       ('tryLock', 'waitTime 5초 · leaseTime 2초', 'amber'), ('proceed()', '본 메서드 실행', 'green'),
       ('finally', '획득했으면 unlock()', 'green')]
for i, (lab, sub, c) in enumerate(row):
    d.box(40 + i * 210, 100, 180, 76, lab, [sub], color=c, label_size=15, sub_size=11)
for i in range(4):
    x = 220 + i * 210
    d.arrow([(x, 138), (x + 30, 138)], color='muted')
d.text(655, 116, '성공', size=11, weight=700, color=G['green'])
d.box(330, 240, 340, 76, '획득 실패 → return false', ['void 메서드면 이 값은 버려진다 — 예외가 낫다'], color='red', label_size=14, sub_size=12)
d.arrow([(510, 176), (510, 240)], color='red')
d.text(520, 208, 'waitTime 초과', size=11, weight=700, color=G['red'], anchor='start')
d.box(700, 240, 360, 76, 'leaseTime 2초가 지나면', ['메서드가 안 끝나도 락이 풀린다 · unlock()이 실패한다'], color='amber', label_size=14, sub_size=12)
d.arrow([(760, 176), (760, 240)], color='amber', dashed=True)
d.text(550, 370, 'unlock()을 try/catch로 한 번 더 감싼 이유: 이미 풀린 락을 풀려고 하면 IllegalMonitorStateException이 난다', size=13, weight=600, color=MUTED)
d.flow([{'path': [(130, 138), (340, 138), (550, 138)], 'color': 'blue', 'dur': 1.0},
        {'path': [(550, 138), (760, 138), (970, 138)], 'color': 'green', 'dur': 1.0, 'hold': 0.5},
        {'path': [(510, 176), (510, 240)], 'color': 'red', 'dur': 0.6, 'hold': 0.8}])
d.save(out('2024/07/24-2.svg'))

# =====================================================================
# 2024/07/25-7  migration plan: split test accounts
# =====================================================================
d = Diagram(1100, 480, '테스트 계정 10개를 반으로 나눈다 — 1~5는 본 쿼리 전에 미리 옮겨 보고, 6~10은 본 쿼리가 옮긴 결과를 확인한다')
cols = [
    (40, '실행 전 테스트 (ID 1~5)', 'blue', ['① 대상 확인 (아직 없음)', '② IN 절로 5건만 INSERT', '③ DB에서 해시 확인', '④ 앱·웹 로그인 확인']),
    (385, '본 쿼리 (전체)', 'amber', ['① 적용 대상 COUNT', '② 6~10이 아직 없는지 확인', '③ 전체 INSERT … SELECT']),
    (730, '실행 후 확인 (ID 6~10)', 'green', ['① DB에서 해시 확인', '② 앱·웹 로그인 확인']),
]
for x, lab, c, steps in cols:
    d.group(x, 90, 330, 330, lab, color=c)
    for i, s in enumerate(steps):
        d.box(x + 15, 126 + i * 70, 300, 52, s, color=c, label_size=13)
    for i in range(len(steps) - 1):
        d.arrow([(x + 165, 178 + i * 70), (x + 165, 196 + i * 70)], color=c)
d.arrow([(370, 255), (385, 255)], color='amber')
d.arrow([(715, 255), (730, 255)], color='green')
d.text(550, 452, '1~5는 이미 옮겨졌으니 본 쿼리의 LEFT JOIN … IS NULL 조건에 걸러진다 — 같은 쿼리를 다시 돌려도 중복되지 않는다', size=12, weight=600, color=MUTED)
d.flow([{'path': [(205, 178), (205, 196), (205, 248), (205, 266), (205, 318), (205, 336)], 'color': 'blue', 'dur': 1.2, 'hold': 0.3},
        {'path': [(550, 178), (550, 196), (550, 248), (550, 266)], 'color': 'amber', 'dur': 0.9, 'hold': 0.3},
        {'path': [(895, 178), (895, 196)], 'color': 'green', 'dur': 0.5, 'hold': 1.0}])
d.save(out('2024/07/25-7.svg'))

# =====================================================================
# 2024/07/25-8  anti-join picks only rows not yet migrated
# =====================================================================
d = Diagram(1100, 500, 'LEFT JOIN … IS NULL은 아직 옮기지 않은 회원만 고른다 — 테스트로 미리 옮긴 1~5는 INSERT 대상에서 빠진다')
d.text(160, 104, 'users', size=14, weight=700, mono=True)
d.text(460, 104, 'user_password (LEFT JOIN)', size=14, weight=700, mono=True)
d.text(860, 104, 'INSERT 되는 행', size=14, weight=700)
ids = [4, 5, 6, 7, 8, 9]
for i, uid in enumerate(ids):
    y = 124 + i * 52
    d.box(60, y, 200, 40, f'user_id = {uid}', color='gray', label_size=13)
    d.arrow([(260, y + 20), (330, y + 20)], color='muted')
    if uid <= 5:
        d.box(330, y, 260, 40, f'user_id = {uid} · 해시 있음', color='blue', label_size=13)
    else:
        d.box(330, y, 260, 40, 'NULL → 대상', color='red', dashed=True, label_size=13)
        d.arrow([(590, y + 20), (700, y + 20)], color='green')
        d.box(700, y, 330, 40, f'({uid}, SHA2(password, 256))', color='green', label_size=13)
d.text(865, 170, '이미 있으니 건너뛴다', size=13, weight=600, color=MUTED)
d.text(550, 452, 'SHA2(…, 256)은 64자리 16진수 문자열을 돌려준다 · 솔트가 없어서 같은 값은 항상 같은 해시가 된다', size=12, weight=600, color=MUTED)
d.flow([{'path': [(160, 248), (260, 248), (330, 248), (590, 248), (700, 248), (865, 248)], 'color': 'green', 'dur': 1.4, 'hold': 0.3},
        {'path': [(160, 144), (260, 144), (330, 144), (460, 144)], 'color': 'blue', 'dur': 0.9, 'hold': 0.8}])
d.save(out('2024/07/25-8.svg'))
print('old_c ok')
