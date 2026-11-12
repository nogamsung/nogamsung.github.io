"""English edition of tools/diagrams/make_diagrams_old_d.py (2024 posts: Kong x3, Airflow x1).
Run: python3 tools/diagrams/en/infra_2024.py "$PWD"
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from diag import Diagram, INK, MUTED

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img/en', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

G = {'gray': '#1f2937', 'muted': '#6b7280', 'blue': '#2563eb', 'green': '#059669', 'red': '#dc2626', 'amber': '#d97706', 'purple': '#7c3aed'}

# =====================================================================
# 2024/08/30-6  Kong install: containers on kong-net, proxy path vs admin path
# =====================================================================
d = Diagram(1100, 560, 'Three containers on one kong-net: requests go to :8000, config goes Konga → Admin API')
d.group(200, 90, 700, 350, 'Docker network: kong-net', color='muted')
d.box(20, 130, 150, 80, 'Client', ['HTTP :8000'], color='gray', label_size=14, sub_size=12)
d.box(20, 325, 150, 80, 'Admin', ['browser → :1337'], color='gray', label_size=14, sub_size=12)
d.box(240, 120, 380, 120, 'kong', ['Proxy :8000 (HTTP) · :8443 (HTTPS)', 'Admin API :8001 · :8444 (HTTPS)'], color='blue', label_size=16, sub_size=12)
d.box(240, 325, 220, 90, 'konga', [':1337 · Kong admin UI'], color='purple', label_size=15, sub_size=12)
d.box(560, 325, 310, 90, 'kong-database', ['PostgreSQL :5432', 'DBs: kong · konga'], color='green', label_size=15, sub_size=12)
d.box(930, 130, 150, 80, 'Spring server', ['upstream'], color='gray', label_size=14, sub_size=12)
d.arrow([(170, 170), (240, 170)], color='blue')
d.arrow([(620, 170), (930, 170)], color='blue', label='Route /api/spring → Service', label_dy=-12)
d.arrow([(170, 365), (240, 365)], color='purple')
d.arrow([(365, 325), (365, 240)], color='purple')
d.text(377, 283, 'Admin API :8001', size=12, weight=700, color=G['purple'], anchor='start')
d.arrow([(580, 240), (580, 280), (715, 280), (715, 325)], color='green')
d.text(727, 300, 'saves Service · Route · Plugin', size=12, weight=700, color=G['green'], anchor='start')
d.arrow([(460, 385), (560, 385)], color='green', label='konga DB', label_dy=-10, label_size=11)
d.box(40, 465, 1020, 70, color='muted')
d.text(550, 490, 'Admin ports (8001 · 8444) are bound to 127.0.0.1 on the host; from outside, only proxy ports 8000 · 8443 are visible', size=13, weight=600)
d.text(550, 514, 'Containers on the same network find each other by name (kong-database, kong)', size=12, weight=600, color=MUTED)
d.flow([{'path': [(170, 170), (240, 170)], 'color': 'blue', 'dur': 0.5},
        {'path': [(620, 170), (930, 170)], 'color': 'blue', 'dur': 0.9, 'hold': 0.4},
        {'path': [(170, 365), (240, 365)], 'color': 'purple', 'dur': 0.5},
        {'path': [(365, 325), (365, 240)], 'color': 'purple', 'dur': 0.6},
        {'path': [(580, 240), (580, 280), (715, 280), (715, 325)], 'color': 'green', 'dur': 0.8, 'hold': 0.6}])
d.save(out('2024/08/30-6.svg'))

# =====================================================================
# 2024/09/04-17  Kong request phases: where a plugin runs
# =====================================================================
d = Diagram(1100, 560, 'The phases one request passes through inside Kong: jwt-custom checks the token in access')
d.box(30, 110, 120, 250, 'Client', color='gray', label_size=14)
d.box(190, 110, 150, 70, 'certificate', ['HTTPS only'], color='muted', label_size=14, sub_size=11)
d.box(370, 110, 150, 70, 'rewrite', ['before route match'], color='muted', label_size=14, sub_size=11)
d.box(550, 110, 170, 70, 'access', ['auth plugins · jwt-custom'], color='red', label_size=15, sub_size=11)
d.box(930, 110, 150, 70, 'Spring server', ['upstream'], color='gray', label_size=14, sub_size=11)
d.box(750, 290, 170, 70, 'header_filter', ['response headers'], color='muted', label_size=14, sub_size=11)
d.box(560, 290, 170, 70, 'body_filter', ['response body'], color='muted', label_size=14, sub_size=11)
d.box(560, 400, 170, 56, 'log', ['after the response'], color='muted', label_size=14, sub_size=11)
for x1, x2 in ((150, 190), (340, 370), (520, 550)):
    d.arrow([(x1, 145), (x2, 145)], color='muted')
d.arrow([(720, 145), (930, 145)], color='blue', label='proxied if it passes', label_dy=-12)
d.arrow([(1005, 180), (1005, 325), (920, 325)], color='muted')
d.text(1015, 250, 'response', size=12, weight=700, color=MUTED, anchor='start')
d.arrow([(750, 325), (730, 325)], color='muted')
d.arrow([(560, 325), (150, 325)], color='muted', label='response', label_dy=-10)
d.arrow([(645, 360), (645, 400)], color='muted', dashed=True)
d.arrow([(635, 110), (635, 90), (90, 90), (90, 110)], color='red', dashed=True)
d.text(362, 76, 'Bad token: 401 right here; the request never reaches the upstream', size=12, weight=700, color=G['red'])
d.box(40, 476, 1020, 64, color='muted')
d.text(550, 498, 'Implement a function named after a phase (access, etc.) in handler.lua and Kong calls it in that phase', size=13, weight=600)
d.text(550, 521, 'Plugins attach to Global · Service · Route · Consumer; in this post it goes on a Route', size=12, weight=600, color=MUTED)
d.flow([{'path': [(150, 145), (720, 145)], 'color': 'blue', 'dur': 1.4},
        {'path': [(720, 145), (930, 145)], 'color': 'blue', 'dur': 0.6, 'hold': 0.3},
        {'path': [(1005, 180), (1005, 325), (150, 325)], 'color': 'green', 'dur': 1.6, 'hold': 0.3},
        {'path': [(635, 110), (635, 90), (90, 90), (90, 110)], 'color': 'red', 'dur': 0.9, 'hold': 0.6}])
d.save(out('2024/09/04-17.svg'))

# =====================================================================
# 2024/09/04-18  JWT credential setup: bundled jwt is only the entry point
# =====================================================================
d = Diagram(1100, 460, 'The bundled JWT plugin is only a way in for the credential, then it gets switched off')
steps = [('① Create Consumer', ['Kong Manager :8002']),
         ('② Install bundled JWT', ['needed to open Credentials']),
         ('③ Save as Disabled', ['jwt-custom does the checks']),
         ('④ Add JWT credential', ['issuer · secret · algorithm'])]
for i, (lab, sub) in enumerate(steps):
    x = 40 + i * 260
    d.box(x, 100, 230, 80, lab, sub, color='purple' if i < 3 else 'green', label_size=14, sub_size=12)
    if i: d.arrow([(x - 30, 140), (x, 140)], color='muted')
d.box(820, 250, 230, 80, 'PostgreSQL', ["Consumer's JWT credential"], color='green', label_size=14, sub_size=12)
d.arrow([(935, 180), (935, 250)], color='green')
d.box(40, 250, 200, 80, 'Request', ['Authorization: Bearer …'], color='gray', label_size=14, sub_size=12)
d.box(300, 250, 260, 80, 'jwt-custom (Route)', ['finds the credential by issuer', 'and verifies the signature'], color='red', label_size=14, sub_size=11)
d.arrow([(240, 290), (300, 290)], color='blue')
d.arrow([(560, 290), (820, 290)], color='blue', label='credential lookup', label_dy=-10)
d.box(40, 370, 1020, 64, color='muted')
d.text(550, 392, 'Only jwt-custom verifies tokens on the Route; the bundled JWT plugin just gets the values into the DB', size=13, weight=600)
d.text(550, 415, "alg and secret can't be changed in Konga, so I set them in Kong Manager", size=12, weight=600, color=MUTED)
d.flow([{'path': [(40, 140), (1040, 140)], 'color': 'purple', 'dur': 1.6},
        {'path': [(935, 180), (935, 250)], 'color': 'green', 'dur': 0.5, 'hold': 0.4},
        {'path': [(240, 290), (300, 290)], 'color': 'blue', 'dur': 0.4},
        {'path': [(560, 290), (820, 290)], 'color': 'blue', 'dur': 0.8, 'hold': 0.6}])
d.save(out('2024/09/04-18.svg'))

# =====================================================================
# 2024/09/11-4  bundled JWT vs jwt-custom per case
# =====================================================================
d = Diagram(1100, 510, 'The split is on missing tokens: bundled JWT returns 401, jwt-custom routes as usual')
cases = [('No token', ['guest-accessible API']), ('Invalid token', ['expired · bad signature']), ('Valid token', ['member request'])]
left = [('401 Unauthorized', ['blocks guest APIs too'], 'red'),
        ('401', ['fixed response format'], 'red'),
        ('Pass', ['Consumer info in headers'], 'green')]
right = [('Pass', ['routed without auth'], 'green'),
         ('Error response', ['in the format we want'], 'amber'),
         ('Pass', ['member info in headers'], 'green')]
d.group(40, 90, 500, 320, 'Bundled JWT plugin', color='red')
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
d.text(550, 452, "The bundled plugin returns 401 when there's no token, which breaks the existing APIs that guests can call", size=13, weight=600)
d.text(550, 475, "I took the open-source JWT plugin, changed it to verify only when a token is present, and put it in the Gateway", size=12, weight=600, color=MUTED)
d.flow(stages)
d.save(out('2024/09/11-4.svg'))

# =====================================================================
# 2024/09/24-1  Airflow: what the install puts where
# =====================================================================
d = Diagram(1100, 540, 'How it runs after the install: webserver, scheduler and AIRFLOW_HOME')
d.group(200, 90, 520, 330, 'conda env airflow_env · Python 3.8', color='blue')
d.group(760, 90, 310, 330, 'AIRFLOW_HOME = ~/airflow', color='amber')
d.box(20, 130, 150, 80, 'Browser', ['admin → :8080'], color='gray', label_size=14, sub_size=12)
d.box(230, 130, 210, 80, 'airflow webserver', [':8080 · web UI'], color='blue', label_size=14, sub_size=12)
d.box(480, 130, 210, 80, 'airflow scheduler', ['reads DAGs, runs tasks'], color='blue', label_size=14, sub_size=12)
d.box(230, 300, 330, 80, 'providers (optional)', ['apache-airflow-providers-mysql · -amazon', 'let tasks work with MySQL · AWS'], color='purple', label_size=14, sub_size=11)
d.box(785, 115, 260, 50, 'airflow.cfg', ['load_examples = False'], color='amber', label_size=13, sub_size=11)
d.box(785, 180, 260, 60, 'dags/', ['DAG files (.py)'], color='amber', label_size=14, sub_size=11)
d.box(785, 300, 260, 90, 'Metadata DB', ['created by airflow db migrate', 'SQLite file by default'], color='green', label_size=14, sub_size=11)
d.box(230, 450, 150, 56, 'MySQL', color='gray', label_size=14)
d.box(410, 450, 150, 56, 'AWS services', color='gray', label_size=14)
d.arrow([(170, 170), (230, 170)], color='blue')
d.arrow([(690, 200), (785, 200)], color='amber', label='parse', label_dy=-10, label_size=11)
d.arrow([(335, 210), (335, 255), (600, 255), (600, 330), (785, 330)], color='green')
d.arrow([(640, 210), (640, 365), (785, 365)], color='green')
d.text(682, 318, 'read', size=11, weight=700, color=G['green'])
d.text(688, 380, 'write state', size=11, weight=700, color=G['green'])
d.arrow([(305, 380), (305, 450)], color='purple')
d.arrow([(485, 380), (485, 450)], color='purple')
d.note(600, 440, 470, 76, ['Run webserver and scheduler in separate terminals,', 'both in the same conda env and AIRFLOW_HOME'], color='muted', size=13)
d.flow([{'path': [(170, 170), (230, 170)], 'color': 'blue', 'dur': 0.4},
        {'path': [(335, 210), (335, 255), (600, 255), (600, 330), (785, 330)], 'color': 'blue', 'dur': 1.2, 'hold': 0.3},
        {'path': [(690, 200), (785, 200)], 'color': 'amber', 'dur': 0.5},
        {'path': [(640, 210), (640, 365), (785, 365)], 'color': 'green', 'dur': 0.9, 'hold': 0.3},
        {'path': [(305, 380), (305, 450)], 'color': 'purple', 'dur': 0.5, 'hold': 0.6}])
d.save(out('2024/09/24-1.svg'))
print('infra_2024 en ok')
