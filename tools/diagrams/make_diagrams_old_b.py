"""2023 기존 글을 다시 쓰며 추가한 다이어그램 (그룹 B).
실행: python3 tools/diagrams/make_diagrams_old_b.py "$PWD"
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from diag import Diagram, INK, MUTED

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

G = {'gray': '#1f2937', 'muted': '#6b7280', 'blue': '#2563eb', 'green': '#059669', 'red': '#dc2626', 'amber': '#d97706', 'purple': '#7c3aed'}

# =====================================================================
# 2023/10/01-4  findBy / countBy / existsBy: what each query asks for
# =====================================================================
d = Diagram(1100, 520, '같은 질문 "이 이메일이 있나?", 세 가지 쿼리 — 가져오는 양이 다르다')
cols = [
    (40, 'findByEmail', 'red', 'SELECT 컬럼 6개 전부', ['contact_id, created_at, updated_at,', 'email, is_verified, verification_code'],
     '엔티티로 매핑', ['Optional<Contact>'], '214ms', ['쓰지 않을 값까지 전송·매핑']),
    (400, 'countByEmail', 'amber', 'SELECT count(contact_id)', ['조건에 맞는 행을 끝까지 센다'],
     '숫자 하나', ['int → 1'], '196ms', ['유니크라 1건, 비유니크면 전부 센다']),
    (760, 'existsByEmail', 'green', 'SELECT contact_id … LIMIT 1', ['첫 행을 찾으면 멈춘다'],
     '참·거짓', ['boolean → true'], '166ms', ['필요한 답만 받는다']),
]
for x, name, c, l1, s1, l2, s2, l3, s3 in cols:
    d.group(x, 86, 300, 344, name, color=c)
    d.box(x + 20, 120, 260, 84, l1, s1, color=c, label_size=14, sub_size=11)
    d.arrow([(x + 150, 204), (x + 150, 236)], color=c)
    d.box(x + 20, 236, 260, 64, l2, s2, color='gray', label_size=14, sub_size=12)
    d.arrow([(x + 150, 300), (x + 150, 332)], color=c)
    d.box(x + 20, 332, 260, 72, l3, s3, color=c, label_size=18, sub_size=11)
d.text(550, 462, '5만 건 · email 에 유니크 제약 · tester30000@nogamsung.com 을 한 번씩 조회한 쿼리 로그 기준', size=12, weight=600, color=MUTED)
d.text(550, 490, '중복 검사에 필요한 답은 "있다/없다" 하나 — 그 답만 묻는 쿼리가 existsBy 다', size=13, weight=700)
d.flow([{'path': [(190, 204), (190, 332)], 'color': 'red', 'dur': 0.8, 'hold': 0.2},
        {'path': [(550, 204), (550, 332)], 'color': 'amber', 'dur': 0.65, 'hold': 0.2},
        {'path': [(910, 204), (910, 332)], 'color': 'green', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2023/10/01-4.svg'))

# =====================================================================
# 2023/10/11-5  before/after: 22 queries -> 3 queries
# =====================================================================
d = Diagram(1100, 470, '팀 리더가 회원 20명을 조회할 때 — 반복문 안의 조회를 IN 절 하나로 꺼냈다')
d.text(60, 128, '개선 전', size=14, weight=700, color=G['red'], anchor='start')
d.box(140, 106, 180, 44, '① 회원 페이징', color='gray', label_size=13)
d.box(350, 106, 180, 44, '② 리더인 팀 조회', color='gray', label_size=13)
for i in range(8):
    d.box(560 + i * 38, 106, 32, 44, color='red')
d.text(890, 128, '…', size=16, weight=700, color=G['red'])
d.text(712, 172, '③ 회원마다 제안 SELECT × 20', size=12, weight=700, color=G['red'])
d.box(920, 100, 140, 56, '총 22번', ['0.337초'], color='red', label_size=14, sub_size=12)
for x1, x2 in ((320, 350), (530, 560)):
    d.arrow([(x1, 128), (x2, 128)], color='muted')
d.text(60, 258, '개선 후', size=14, weight=700, color=G['green'], anchor='start')
d.box(140, 236, 180, 44, '① 회원 페이징', color='gray', label_size=13)
d.box(350, 236, 180, 44, '② 리더인 팀 조회', color='gray', label_size=13)
d.box(560, 236, 330, 44, '③ offer.user.id IN (회원 id 20개)', color='blue', label_size=13)
d.box(920, 230, 140, 56, '총 3번', ['0.039초'], color='green', label_size=14, sub_size=12)
for x1, x2 in ((320, 350), (530, 560)):
    d.arrow([(x1, 258), (x2, 258)], color='muted')
d.box(60, 330, 1000, 90, color='muted')
d.text(560, 360, '개선 전은 회원 수에 비례해 쿼리가 늘고(2 + N), 개선 후는 회원 수와 상관없이 3번이다', size=13, weight=700)
d.text(560, 390, '리더가 아니면 ②에서 팀이 없으니 ③을 건너뛰고 빈 목록을 돌려준다', size=12, weight=600, color=MUTED)
d.flow([{'path': [(140, 128), (900, 128)], 'color': 'red', 'dur': 2.0, 'hold': 0.3},
        {'path': [(140, 258), (890, 258)], 'color': 'green', 'dur': 0.8, 'hold': 0.9}])
d.save(out('2023/10/11-5.svg'))

# =====================================================================
# 2023/10/11-6  IN query + groupingBy assembly
# =====================================================================
d = Diagram(1100, 470, 'IN 절로 한 번에 가져온 제안을 Map 으로 묶어 회원에게 다시 붙인다 (id 는 예시)')
d.group(40, 90, 220, 230, '① Page<User>', color='gray')
for i, u in enumerate(['User 22', 'User 23', 'User 24']):
    d.box(60, 124 + i * 58, 180, 44, u, color='gray', label_size=13)
d.arrow([(260, 205), (300, 205)], color='muted')
d.box(300, 160, 200, 90, '② userIds', ['[22, 23, 24, …]'], color='gray', label_size=14, sub_size=12)
d.arrow([(500, 205), (540, 205)], color='blue')
d.box(540, 150, 200, 110, '③ 제안 조회 1번', ['offer.user.id.in(userIds)', 'offer.team.id.eq(teamId)'], color='blue', label_size=14, sub_size=11)
d.arrow([(740, 205), (780, 205)], color='blue')
d.group(780, 90, 280, 230, '④ groupingBy(user id)', color='green')
d.box(800, 124, 240, 44, '22 → [제안 A]', color='green', label_size=13)
d.box(800, 182, 240, 44, '24 → [제안 B, 제안 C]', color='green', label_size=13)
d.box(800, 240, 240, 44, '23 → 없음', color='muted', dashed=True, label_size=13)
d.box(40, 350, 1020, 80, color='muted')
d.text(550, 376, 'users.stream().map(u -> new ProfileOfferResponse(u, oMap.getOrDefault(u.getId(), emptyList())))', size=12, weight=600, mono=True)
d.text(550, 404, '제안이 없는 회원(23)은 getOrDefault 로 빈 목록 — 회원마다 다시 조회하지 않는다', size=12, weight=700, color=MUTED)
d.flow([{'path': [(260, 205), (300, 205)], 'color': 'gray', 'dur': 0.4},
        {'path': [(500, 205), (540, 205)], 'color': 'blue', 'dur': 0.4, 'hold': 0.4},
        {'path': [(740, 205), (780, 205)], 'color': 'green', 'dur': 0.4, 'hold': 0.4},
        {'path': [(920, 320), (920, 350)], 'color': 'green', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2023/10/11-6.svg'))

# =====================================================================
# 2023/10/15-1  positionEq: null predicate is dropped
# =====================================================================
d = Diagram(1100, 470, '조건 메서드가 null 을 돌려주면 Querydsl 은 그 조건을 빼고 SQL 을 만든다')
d.box(40, 190, 240, 80, 'positionEq(position)', ['where(…) 안에서 호출'], color='purple', label_size=14, sub_size=12)
d.box(360, 110, 260, 70, 'BACKEND 일 때', ['user.position.eq(position)'], color='blue', label_size=14, sub_size=12)
d.box(360, 280, 260, 70, 'NONE 일 때', ['null 반환 → 조건에서 빠짐'], color='amber', label_size=14, sub_size=12)
d.arrow([(280, 220), (320, 220), (320, 145), (360, 145)], color='blue')
d.arrow([(280, 240), (320, 240), (320, 315), (360, 315)], color='amber')
d.box(680, 110, 380, 70, color='blue')
d.lines(870, 133, ['WHERE user_id < ?', "  AND position = 'BACKEND'"], size=13, mono=True)
d.box(680, 280, 380, 70, color='amber')
d.lines(870, 304, ['WHERE user_id < ?', '(position 조건 없음)'], size=13, mono=True)
d.arrow([(620, 145), (680, 145)], color='blue')
d.arrow([(620, 315), (680, 315)], color='amber')
d.text(550, 410, 'where(a, b, null) 은 where(a, b) 와 같다 — 메서드 하나가 정적 쿼리 두 벌을 대신한다', size=13, weight=700)
d.flow([{'path': [(280, 220), (320, 220), (320, 145), (360, 145)], 'color': 'blue', 'dur': 0.7},
        {'path': [(620, 145), (680, 145)], 'color': 'blue', 'dur': 0.4, 'hold': 0.5},
        {'path': [(280, 240), (320, 240), (320, 315), (360, 315)], 'color': 'amber', 'dur': 0.7},
        {'path': [(620, 315), (680, 315)], 'color': 'amber', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2023/10/15-1.svg'))

# =====================================================================
# 2023/10/15-2  cursor pagination: last id becomes next cursor
# =====================================================================
d = Diagram(1100, 500, '커서 기반 페이지네이션 — 이전 페이지의 마지막 id 가 다음 요청의 pageFrom 이 된다 (id 는 예시)')
rows = [(100, '1페이지 요청', 'pageFrom = Long.MAX_VALUE', 'user_id < 9223372036854775807', 'id 100 … 91'),
        (250, '2페이지 요청', 'pageFrom = 91', 'user_id < 91', 'id 90 … 81')]
for y, l, s, where, res in rows:
    d.box(40, y, 220, 70, l, [s], color='gray', label_size=14, sub_size=12)
    d.arrow([(260, y + 35), (300, y + 35)], color='blue')
    d.box(300, y, 420, 70, color='blue')
    d.lines(510, y + 24, ['WHERE ' + where, 'ORDER BY user_id DESC LIMIT 10'], size=12, mono=True, gap=20)
    d.arrow([(720, y + 35), (760, y + 35)], color='blue')
    d.box(760, y, 300, 70, res, ['10건'], color='green', label_size=14, sub_size=12)
d.arrow([(910, 170), (910, 210), (150, 210), (150, 250)], color='green', dashed=True)
d.text(530, 198, '마지막 id 91 을 다음 커서로', size=12, weight=700, color=G['green'])
d.box(40, 360, 500, 90, '커서 조건은 목록 쿼리에만', ['count 쿼리는 전체 개수를 세야 하니 user_id < ? 를 넣지 않는다', 'count 가 0 이면 목록 쿼리는 아예 보내지 않는다'], color='muted', label_size=14, sub_size=12)
d.box(560, 360, 500, 90, '커서 키 = 정렬 키', ['user_id < ? 로 자르면 user_id 로 정렬해야', '페이지 경계가 어긋나지 않는다'], color='amber', label_size=14, sub_size=12)
d.flow([{'path': [(260, 135), (300, 135)], 'color': 'blue', 'dur': 0.4},
        {'path': [(720, 135), (760, 135)], 'color': 'blue', 'dur': 0.4, 'hold': 0.3},
        {'path': [(910, 170), (910, 210), (150, 210), (150, 250)], 'color': 'green', 'dur': 1.2, 'hold': 0.2},
        {'path': [(260, 285), (300, 285)], 'color': 'blue', 'dur': 0.4},
        {'path': [(720, 285), (760, 285)], 'color': 'blue', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2023/10/15-2.svg'))
print('old_b ok')
