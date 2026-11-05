"""2023~2024 기존 글을 다시 쓰며 추가한 다이어그램 (그룹 A).
실행: python3 tools/diagrams/make_diagrams_old_a.py "$PWD"
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from diag import Diagram, INK, MUTED

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

G = {'gray': '#1f2937', 'muted': '#6b7280', 'blue': '#2563eb', 'green': '#059669', 'red': '#dc2626', 'amber': '#d97706', 'purple': '#7c3aed'}

# =====================================================================
# 2023/10/27-9  one-to-one: expected vs actual queries
# =====================================================================
d = Diagram(1100, 520, '기대한 쿼리 네 번, 실제로 나간 쿼리 54번 — 기술 조회 뒤에 연락처 SELECT 가 회원 수만큼 끼어든다')
d.text(60, 118, '기대', size=14, weight=700, color=G['green'], anchor='start')
exp = [('① count', 'gray'), ('② 회원 페이징', 'gray'), ('③ 기술 IN 절', 'blue'), ('⑤ 제안 IN 절', 'blue')]
for i, (lab, c) in enumerate(exp):
    x = 140 + i * 230
    d.box(x, 96, 200, 44, lab, color=c, label_size=13)
    if i: d.arrow([(x - 30, 118), (x, 118)], color='muted')
d.text(60, 238, '실제', size=14, weight=700, color=G['red'], anchor='start')
act = [('① count', 'gray', 140), ('② 회원 페이징', 'gray', 310), ('③ 기술 IN 절', 'blue', 480)]
for lab, c, x in act:
    d.box(x, 216, 150, 44, lab, color=c, label_size=12)
for i in range(6):
    d.box(650 + i * 46, 210 + (i % 2) * 6, 40, 44, color='red')
    d.text(670 + i * 46, 238 + (i % 2) * 6, 'C', size=12, weight=700, color=G['red'])
d.text(800, 290, '④ 연락처 SELECT × 회원 수 (page-size 50 → 50번)', size=12, weight=700, color=G['red'])
d.box(940, 216, 120, 44, '⑤ 제안 IN', color='blue', label_size=12)
for x1, x2 in ((290, 310), (460, 480), (630, 650), (926, 940)):
    d.arrow([(x1, 238), (x2, 238)], color='muted')
d.box(60, 330, 980, 70, color='muted')
d.text(550, 358, '코드 어디에서도 user.getContact() 를 부르지 않았다 — 회원 엔티티를 채우는 순간 Hibernate 가 연락처를 확인하러 간다', size=13, weight=600)
d.text(550, 382, 'IN 절은 "내가 부른 연관 조회"를 모아 줄 뿐, 엔티티를 만들 때 일어나는 조회는 따로 본다', size=12, weight=600, color=MUTED)
d.box(60, 420, 470, 60, '개선 전', ['쿼리 54번 · 124ms'], color='red', label_size=14, sub_size=12)
d.box(570, 420, 470, 60, 'default_batch_fetch_size: 100 적용 후', ['연락처 50번 → IN 절 1번 · 54ms'], color='green', label_size=14, sub_size=12)
d.flow([{'path': [(140, 118), (1060, 118)], 'color': 'green', 'dur': 1.4, 'hold': 0.4},
        {'path': [(140, 238), (640, 238)], 'color': 'gray', 'dur': 0.9},
        {'path': [(650, 238), (926, 238)], 'color': 'red', 'dur': 1.6, 'hold': 0.2},
        {'path': [(940, 238), (1060, 238)], 'color': 'blue', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2023/10/27-9.svg'))

# =====================================================================
# 2023/10/27-10  one-to-one: proxy vs immediate select
# =====================================================================
d = Diagram(1100, 560, '지연 로딩은 프록시가 있어야 동작한다 — 일대일에서 프록시를 못 만들면 즉시 SELECT 로 채운다')
d.group(40, 90, 490, 380, '@ManyToOne — 프록시를 만들 수 있다', color='green')
d.box(70, 130, 200, 70, 'Skill 행', ['user_id = 7'], color='gray', label_size=14, sub_size=12)
d.box(310, 130, 190, 70, 'User 프록시', ['id = 7, 아직 비어 있음'], color='green', label_size=14, sub_size=12)
d.arrow([(270, 165), (310, 165)], color='green')
d.text(180, 224, '외래 키만으로 프록시 생성', size=11, weight=700, color=G['green'])
d.box(70, 240, 430, 60, 'skill.getUser().getName() 을 부를 때', ['그때 처음 SELECT — 지연 로딩이 지켜진다'], color='green', label_size=13, sub_size=11)
d.arrow([(405, 200), (405, 240)], color='green')
d.note(70, 330, 430, 110, ['"연관 객체가 있다면 id 는 7" 이라는 사실만으로', '프록시를 넣을 수 있다. 없을 수도 있다는 가능성은', '외래 키가 NULL 인지로 이미 알 수 있다.'], color='green', size=12)
d.group(570, 90, 490, 380, '@OneToOne — 존재 여부부터 알아야 한다', color='red')
d.box(600, 130, 200, 70, 'User 행', ['연락처가 있나?'], color='gray', label_size=14, sub_size=12)
d.box(840, 130, 190, 70, 'null 인가, 프록시인가', ['결정하려면 확인이 필요'], color='amber', label_size=13, sub_size=11)
d.arrow([(800, 165), (840, 165)], color='amber')
d.box(600, 240, 430, 60, '엔티티를 채우는 순간 SELECT contact …', ['회원 한 명마다 한 번 — N+1'], color='red', label_size=13, sub_size=11)
d.arrow([(935, 200), (935, 240)], color='red')
d.note(600, 330, 430, 110, ['특히 외래 키를 갖지 않은 쪽(mappedBy)은', '테이블만 보고 연관 객체가 있는지 알 수 없다.', 'FetchType.LAZY 는 힌트일 뿐, 보장이 아니다.'], color='red', size=12)
d.text(550, 510, '해결: default_batch_fetch_size 가 이 조회들을 IN 절 하나로 묶는다 · 관계를 @ManyToOne 으로 바꾸는 방법도 있지만 도메인이 일대일이라 고르지 않았다', size=12, weight=700)
d.flow([{'path': [(270, 165), (310, 165)], 'color': 'green', 'dur': 0.5}, {'path': [(405, 200), (405, 240)], 'color': 'green', 'dur': 0.5, 'hold': 0.4},
        {'path': [(800, 165), (840, 165)], 'color': 'amber', 'dur': 0.5}, {'path': [(935, 200), (935, 240)], 'color': 'red', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2023/10/27-10.svg'))
print('old_a ok')
