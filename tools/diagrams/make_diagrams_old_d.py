"""2024년 기존 글(Kong 3편, Airflow 1편)을 다시 쓰며 추가한 다이어그램 (그룹 D).
실행: python3 tools/diagrams/make_diagrams_old_d.py "$PWD"
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from diag import Diagram, INK, MUTED

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

G = {'gray': '#1f2937', 'muted': '#6b7280', 'blue': '#2563eb', 'green': '#059669', 'red': '#dc2626', 'amber': '#d97706', 'purple': '#7c3aed'}

# =====================================================================
# 2024/08/30-6  Kong install: containers on kong-net, proxy path vs admin path
# =====================================================================
d = Diagram(1100, 560, '컨테이너 세 개를 kong-net 하나에 — 요청은 8000 으로, 설정은 Konga → Admin API 로')
d.group(200, 90, 700, 350, 'Docker network: kong-net', color='muted')
d.box(20, 130, 150, 80, '클라이언트', ['HTTP :8000'], color='gray', label_size=14, sub_size=12)
d.box(20, 325, 150, 80, '관리자', ['브라우저 → :1337'], color='gray', label_size=14, sub_size=12)
d.box(240, 120, 380, 120, 'kong', ['프록시 :8000 (HTTP) · :8443 (HTTPS)', 'Admin API :8001 · :8444 (HTTPS)'], color='blue', label_size=16, sub_size=12)
d.box(240, 325, 220, 90, 'konga', [':1337 · Kong 관리 UI'], color='purple', label_size=15, sub_size=12)
d.box(560, 325, 310, 90, 'kong-database', ['PostgreSQL :5432', 'DB: kong · konga'], color='green', label_size=15, sub_size=12)
d.box(930, 130, 150, 80, 'Spring 서버', ['업스트림'], color='gray', label_size=14, sub_size=12)
d.arrow([(170, 170), (240, 170)], color='blue')
d.arrow([(620, 170), (930, 170)], color='blue', label='Route /api/spring → Service', label_dy=-12)
d.arrow([(170, 365), (240, 365)], color='purple')
d.arrow([(365, 325), (365, 240)], color='purple')
d.text(377, 283, 'Admin API :8001', size=12, weight=700, color=G['purple'], anchor='start')
d.arrow([(580, 240), (580, 280), (715, 280), (715, 325)], color='green')
d.text(727, 300, 'Service · Route · Plugin 저장', size=12, weight=700, color=G['green'], anchor='start')
d.arrow([(460, 385), (560, 385)], color='green', label='konga DB', label_dy=-10, label_size=11)
d.box(40, 465, 1020, 70, color='muted')
d.text(550, 490, 'Admin 포트(8001 · 8444)는 호스트의 127.0.0.1 에만 열었다 — 바깥에서는 프록시 포트 8000 · 8443 만 보인다', size=13, weight=600)
d.text(550, 514, '같은 네트워크 안의 컨테이너는 이름(kong-database, kong)으로 서로를 찾는다', size=12, weight=600, color=MUTED)
d.flow([{'path': [(170, 170), (240, 170)], 'color': 'blue', 'dur': 0.5},
        {'path': [(620, 170), (930, 170)], 'color': 'blue', 'dur': 0.9, 'hold': 0.4},
        {'path': [(170, 365), (240, 365)], 'color': 'purple', 'dur': 0.5},
        {'path': [(365, 325), (365, 240)], 'color': 'purple', 'dur': 0.6},
        {'path': [(580, 240), (580, 280), (715, 280), (715, 325)], 'color': 'green', 'dur': 0.8, 'hold': 0.6}])
d.save(out('2024/08/30-6.svg'))

# =====================================================================
# 2024/09/04-17  Kong request phases: where a plugin runs
# =====================================================================
d = Diagram(1100, 560, '요청 하나가 Kong 안에서 지나가는 단계 — jwt-custom 은 access 에서 토큰을 본다')
d.box(30, 110, 120, 250, '클라이언트', color='gray', label_size=14)
d.box(190, 110, 150, 70, 'certificate', ['HTTPS 일 때'], color='muted', label_size=14, sub_size=11)
d.box(370, 110, 150, 70, 'rewrite', ['라우트 매칭 전'], color='muted', label_size=14, sub_size=11)
d.box(550, 110, 170, 70, 'access', ['인증 플러그인 · jwt-custom'], color='red', label_size=15, sub_size=11)
d.box(930, 110, 150, 70, 'Spring 서버', ['업스트림'], color='gray', label_size=14, sub_size=11)
d.box(750, 290, 170, 70, 'header_filter', ['응답 헤더'], color='muted', label_size=14, sub_size=11)
d.box(560, 290, 170, 70, 'body_filter', ['응답 본문'], color='muted', label_size=14, sub_size=11)
d.box(560, 400, 170, 56, 'log', ['응답을 보낸 뒤'], color='muted', label_size=14, sub_size=11)
for x1, x2 in ((150, 190), (340, 370), (520, 550)):
    d.arrow([(x1, 145), (x2, 145)], color='muted')
d.arrow([(720, 145), (930, 145)], color='blue', label='통과하면 프록시', label_dy=-12)
d.arrow([(1005, 180), (1005, 325), (920, 325)], color='muted')
d.text(1015, 250, '응답', size=12, weight=700, color=MUTED, anchor='start')
d.arrow([(750, 325), (730, 325)], color='muted')
d.arrow([(560, 325), (150, 325)], color='muted', label='응답', label_dy=-10)
d.arrow([(645, 360), (645, 400)], color='muted', dashed=True)
d.arrow([(635, 110), (635, 90), (90, 90), (90, 110)], color='red', dashed=True)
d.text(362, 80, '토큰이 잘못되면 여기서 바로 401 — 업스트림까지 가지 않는다', size=12, weight=700, color=G['red'])
d.box(40, 476, 1020, 64, color='muted')
d.text(550, 498, 'handler.lua 에 단계 이름의 함수(access 등)를 구현하면 Kong 이 그 단계에서 호출한다', size=13, weight=600)
d.text(550, 521, '플러그인은 Global · Service · Route · Consumer 단위로 붙인다 — 이 글에서는 Route 에 붙였다', size=12, weight=600, color=MUTED)
d.flow([{'path': [(150, 145), (720, 145)], 'color': 'blue', 'dur': 1.4},
        {'path': [(720, 145), (930, 145)], 'color': 'blue', 'dur': 0.6, 'hold': 0.3},
        {'path': [(1005, 180), (1005, 325), (150, 325)], 'color': 'green', 'dur': 1.6, 'hold': 0.3},
        {'path': [(635, 110), (635, 90), (90, 90), (90, 110)], 'color': 'red', 'dur': 0.9, 'hold': 0.6}])
d.save(out('2024/09/04-17.svg'))

# =====================================================================
# 2024/09/04-18  JWT credential setup: bundled jwt is only the entry point
# =====================================================================
d = Diagram(1100, 460, '기본 JWT 플러그인은 credential 을 넣는 입구로만 쓰고 끈다')
steps = [('① Consumer 생성', ['Kong Manager :8002']),
         ('② 기본 JWT 설치', ['Credentials 탭을 열려면 필요']),
         ('③ Disabled 로 저장', ['검증은 jwt-custom 몫']),
         ('④ JWT credential 등록', ['issuer · secret · algorithm'])]
for i, (lab, sub) in enumerate(steps):
    x = 40 + i * 260
    d.box(x, 100, 230, 80, lab, sub, color='purple' if i < 3 else 'green', label_size=14, sub_size=12)
    if i: d.arrow([(x - 30, 140), (x, 140)], color='muted')
d.box(820, 250, 230, 80, 'PostgreSQL', ['Consumer 의 JWT credential'], color='green', label_size=14, sub_size=12)
d.arrow([(935, 180), (935, 250)], color='green')
d.box(40, 250, 200, 80, '요청', ['Authorization: Bearer …'], color='gray', label_size=14, sub_size=12)
d.box(300, 250, 260, 80, 'jwt-custom (Route)', ['issuer 로 credential 을 찾아', '서명을 검증한다'], color='red', label_size=14, sub_size=11)
d.arrow([(240, 290), (300, 290)], color='blue')
d.arrow([(560, 290), (820, 290)], color='blue', label='credential 조회', label_dy=-10)
d.box(40, 370, 1020, 64, color='muted')
d.text(550, 392, 'Route 에서 토큰을 검증하는 건 jwt-custom 하나다 — 기본 JWT 는 값을 DB 에 넣는 데만 쓴다', size=13, weight=600)
d.text(550, 415, 'alg · secret 은 Konga 에서 바꿀 수 없어서 Kong Manager 에서 설정했다', size=12, weight=600, color=MUTED)
d.flow([{'path': [(40, 140), (1040, 140)], 'color': 'purple', 'dur': 1.6},
        {'path': [(935, 180), (935, 250)], 'color': 'green', 'dur': 0.5, 'hold': 0.4},
        {'path': [(240, 290), (300, 290)], 'color': 'blue', 'dur': 0.4},
        {'path': [(560, 290), (820, 290)], 'color': 'blue', 'dur': 0.8, 'hold': 0.6}])
d.save(out('2024/09/04-18.svg'))

# =====================================================================
# 2024/09/11-4  bundled JWT vs jwt-custom per case
# =====================================================================
d = Diagram(1100, 510, '토큰이 없을 때 갈린다 — 기본 JWT 플러그인은 401, jwt-custom 은 그대로 라우팅')
cases = [('토큰 없음', ['비회원도 쓰는 API']), ('잘못된 토큰', ['만료 · 서명 불일치']), ('올바른 토큰', ['회원 요청'])]
left = [('401 Unauthorized', ['비회원 API 도 막힌다'], 'red'),
        ('401', ['응답 형식은 고정'], 'red'),
        ('통과', ['Consumer 정보를 헤더로'], 'green')]
right = [('통과', ['인증 없이 라우팅'], 'green'),
         ('에러 응답', ['원하는 형식으로'], 'amber'),
         ('통과', ['회원 정보를 헤더로'], 'green')]
d.group(40, 90, 500, 320, '기본 JWT 플러그인', color='red')
d.group(560, 90, 500, 320, 'jwt-custom', color='green')
stages = []
for i, (c, sub) in enumerate(cases):
    y = 125 + i * 92
    for ox, res in ((0, left[i]), (520, right[i])):
        d.box(60 + ox, y, 180, 64, c, sub, color='gray', label_size=14, sub_size=11)
        d.box(300 + ox, y, 220, 64, res[0], res[1], color=res[2], label_size=14, sub_size=11)
        d.arrow([(240 + ox, y + 32), (300 + ox, y + 32)], color='muted')
    stages.append({'path': [(240, y + 32), (300, y + 32)], 'color': left[i][2], 'dur': 0.5, 'hold': 0.15})
    stages.append({'path': [(760, y + 32), (820, y + 32)], 'color': right[i][2], 'dur': 0.5, 'hold': 0.35})
d.box(40, 430, 1020, 64, color='muted')
d.text(550, 452, "기본 플러그인은 토큰이 없으면 401 — 이미 서비스 중인 '비회원도 응답받는 API' 와 맞지 않았다", size=13, weight=600)
d.text(550, 475, "오픈 소스인 JWT 플러그인을 바탕으로 '토큰이 있을 때만 검증' 하도록 고쳐 Gateway 에 넣었다", size=12, weight=600, color=MUTED)
d.flow(stages)
d.save(out('2024/09/11-4.svg'))

# =====================================================================
# 2024/09/24-1  Airflow: what the install puts where
# =====================================================================
d = Diagram(1100, 540, '설치가 끝나면 이렇게 돈다 — 웹서버와 스케줄러, 그리고 AIRFLOW_HOME')
d.group(200, 90, 520, 330, 'conda 환경 airflow_env · Python 3.8', color='blue')
d.group(760, 90, 310, 330, 'AIRFLOW_HOME = ~/airflow', color='amber')
d.box(20, 130, 150, 80, '브라우저', ['관리자 → :8080'], color='gray', label_size=14, sub_size=12)
d.box(230, 130, 210, 80, 'airflow webserver', [':8080 · 웹 UI'], color='blue', label_size=14, sub_size=12)
d.box(480, 130, 210, 80, 'airflow scheduler', ['DAG 를 읽고 태스크 실행'], color='blue', label_size=14, sub_size=12)
d.box(230, 300, 330, 80, 'providers (옵션)', ['apache-airflow-providers-mysql · -amazon', '태스크에서 MySQL · AWS 를 다룬다'], color='purple', label_size=14, sub_size=11)
d.box(785, 115, 260, 50, 'airflow.cfg', ['load_examples = False'], color='amber', label_size=13, sub_size=11)
d.box(785, 180, 260, 60, 'dags/', ['DAG 파일(.py)'], color='amber', label_size=14, sub_size=11)
d.box(785, 300, 260, 90, '메타데이터 DB', ['airflow db migrate 로 만든다', '기본값은 SQLite 파일'], color='green', label_size=14, sub_size=11)
d.box(230, 450, 150, 56, 'MySQL', color='gray', label_size=14)
d.box(410, 450, 150, 56, 'AWS 서비스', color='gray', label_size=14)
d.arrow([(170, 170), (230, 170)], color='blue')
d.arrow([(690, 200), (785, 200)], color='amber', label='파싱', label_dy=-10, label_size=11)
d.arrow([(335, 210), (335, 255), (600, 255), (600, 330), (785, 330)], color='green')
d.arrow([(640, 210), (640, 365), (785, 365)], color='green')
d.text(680, 318, '조회', size=11, weight=700, color=G['green'])
d.text(684, 380, '상태 기록', size=11, weight=700, color=G['green'])
d.arrow([(305, 380), (305, 450)], color='purple')
d.arrow([(485, 380), (485, 450)], color='purple')
d.note(600, 440, 470, 76, ['웹서버와 스케줄러는 터미널을 나눠 따로 띄운다', '둘 다 같은 conda 환경 · 같은 AIRFLOW_HOME 에서'], color='muted', size=13)
d.flow([{'path': [(170, 170), (230, 170)], 'color': 'blue', 'dur': 0.4},
        {'path': [(335, 210), (335, 255), (600, 255), (600, 330), (785, 330)], 'color': 'blue', 'dur': 1.2, 'hold': 0.3},
        {'path': [(690, 200), (785, 200)], 'color': 'amber', 'dur': 0.5},
        {'path': [(640, 210), (640, 365), (785, 365)], 'color': 'green', 'dur': 0.9, 'hold': 0.3},
        {'path': [(305, 380), (305, 450)], 'color': 'purple', 'dur': 0.5, 'hold': 0.6}])
d.save(out('2024/09/24-1.svg'))
print('old_d ok')
