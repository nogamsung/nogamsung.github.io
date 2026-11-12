"""English edition of tools/diagrams/make_diagrams_old_a.py, make_diagrams_old_b.py and make_diagrams_old_c.py
(2023-2024 posts: JPA duplicate check, N+1 x2, Querydsl pagination, Spring Boot 3 upgrade, Redisson lock, SHA-256 migration).
Run: python3 tools/diagrams/en/backend_2023_2024.py "$PWD"
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from diag import Diagram, INK, MUTED

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img/en', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

G = {'gray': '#1f2937', 'muted': '#6b7280', 'blue': '#2563eb', 'green': '#059669', 'red': '#dc2626', 'amber': '#d97706', 'purple': '#7c3aed'}

# =====================================================================
# 2023/10/01-4  findBy / countBy / existsBy: what each query asks for
# =====================================================================
d = Diagram(1100, 520, 'One question, "does this email exist?", three queries — each fetches a different amount')
cols = [
    (40, 'findByEmail', 'red', 'SELECT all 6 columns', ['contact_id, created_at, updated_at,', 'email, is_verified, verification_code'],
     'Mapped to an entity', ['Optional<Contact>'], '214ms', ['Sends and maps values it never uses']),
    (400, 'countByEmail', 'amber', 'SELECT count(contact_id)', ['Counts every matching row'],
     'A single number', ['int → 1'], '196ms', ['Unique: 1 row. Non-unique: counts them all']),
    (760, 'existsByEmail', 'green', 'SELECT contact_id … LIMIT 1', ['Stops at the first match'],
     'True or false', ['boolean → true'], '166ms', ['Gets only the answer it needs']),
]
for x, name, c, l1, s1, l2, s2, l3, s3 in cols:
    d.group(x, 86, 300, 344, name, color=c)
    d.box(x + 20, 120, 260, 84, l1, s1, color=c, label_size=14, sub_size=11)
    d.arrow([(x + 150, 204), (x + 150, 236)], color=c)
    d.box(x + 20, 236, 260, 64, l2, s2, color='gray', label_size=14, sub_size=12)
    d.arrow([(x + 150, 300), (x + 150, 332)], color=c)
    d.box(x + 20, 332, 260, 72, l3, s3, color=c, label_size=18, sub_size=11)
d.text(550, 462, '50,000 rows · unique constraint on email · from the query logs of one lookup of tester30000@nogamsung.com each', size=12, weight=600, color=MUTED)
d.text(550, 490, 'A duplicate check needs one answer, yes or no — existsBy is the query that asks only that', size=13, weight=700)
d.flow([{'path': [(190, 204), (190, 332)], 'color': 'red', 'dur': 0.8, 'hold': 0.2},
        {'path': [(550, 204), (550, 332)], 'color': 'amber', 'dur': 0.65, 'hold': 0.2},
        {'path': [(910, 204), (910, 332)], 'color': 'green', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2023/10/01-4.svg'))

# =====================================================================
# 2023/10/11-5  before/after: 22 queries -> 3 queries
# =====================================================================
d = Diagram(1100, 470, 'A team leader lists 20 users — the lookup inside the loop became a single IN query')
d.text(60, 128, 'Before', size=14, weight=700, color=G['red'], anchor='start')
d.box(140, 106, 180, 44, '① Users page', color='gray', label_size=13)
d.box(350, 106, 180, 44, "② Leader's team", color='gray', label_size=13)
for i in range(8):
    d.box(560 + i * 38, 106, 32, 44, color='red')
d.text(890, 128, '…', size=16, weight=700, color=G['red'])
d.text(712, 172, '③ Offer SELECT per user × 20', size=12, weight=700, color=G['red'])
d.box(920, 100, 140, 56, '22 queries', ['0.337s'], color='red', label_size=14, sub_size=12)
for x1, x2 in ((320, 350), (530, 560)):
    d.arrow([(x1, 128), (x2, 128)], color='muted')
d.text(60, 258, 'After', size=14, weight=700, color=G['green'], anchor='start')
d.box(140, 236, 180, 44, '① Users page', color='gray', label_size=13)
d.box(350, 236, 180, 44, "② Leader's team", color='gray', label_size=13)
d.box(560, 236, 330, 44, '③ offer.user.id IN (20 user ids)', color='blue', label_size=13)
d.box(920, 230, 140, 56, '3 queries', ['0.039s'], color='green', label_size=14, sub_size=12)
for x1, x2 in ((320, 350), (530, 560)):
    d.arrow([(x1, 258), (x2, 258)], color='muted')
d.box(60, 330, 1000, 90, color='muted')
d.text(560, 360, 'Before, the query count grows with the number of users (2 + N). After, it is 3 no matter how many', size=13, weight=700)
d.text(560, 390, 'If the caller leads no team, ② finds nothing, ③ is skipped and an empty list comes back', size=12, weight=600, color=MUTED)
d.flow([{'path': [(140, 128), (900, 128)], 'color': 'red', 'dur': 2.0, 'hold': 0.3},
        {'path': [(140, 258), (890, 258)], 'color': 'green', 'dur': 0.8, 'hold': 0.9}])
d.save(out('2023/10/11-5.svg'))

# =====================================================================
# 2023/10/11-6  IN query + groupingBy assembly
# =====================================================================
d = Diagram(1100, 470, 'Fetch offers with one IN query, group them into a Map, attach them back to users (example ids)')
d.group(40, 90, 220, 230, '① Page<User>', color='gray')
for i, u in enumerate(['User 22', 'User 23', 'User 24']):
    d.box(60, 124 + i * 58, 180, 44, u, color='gray', label_size=13)
d.arrow([(260, 205), (300, 205)], color='muted')
d.box(300, 160, 200, 90, '② userIds', ['[22, 23, 24, …]'], color='gray', label_size=14, sub_size=12)
d.arrow([(500, 205), (540, 205)], color='blue')
d.box(540, 150, 200, 110, '③ One offer query', ['offer.user.id.in(userIds)', 'offer.team.id.eq(teamId)'], color='blue', label_size=14, sub_size=11)
d.arrow([(740, 205), (780, 205)], color='blue')
d.group(780, 90, 280, 230, '④ groupingBy(user id)', color='green')
d.box(800, 124, 240, 44, '22 → [Offer A]', color='green', label_size=13)
d.box(800, 182, 240, 44, '24 → [Offer B, Offer C]', color='green', label_size=13)
d.box(800, 240, 240, 44, '23 → none', color='muted', dashed=True, label_size=13)
d.box(40, 350, 1020, 80, color='muted')
d.text(550, 376, 'users.stream().map(u -> new ProfileOfferResponse(u, oMap.getOrDefault(u.getId(), emptyList())))', size=12, weight=600, mono=True)
d.text(550, 404, 'User 23 has no offers, so getOrDefault hands it an empty list — no extra query per user', size=12, weight=700, color=MUTED)
d.flow([{'path': [(260, 205), (300, 205)], 'color': 'gray', 'dur': 0.4},
        {'path': [(500, 205), (540, 205)], 'color': 'blue', 'dur': 0.4, 'hold': 0.4},
        {'path': [(740, 205), (780, 205)], 'color': 'green', 'dur': 0.4, 'hold': 0.4},
        {'path': [(920, 320), (920, 350)], 'color': 'green', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2023/10/11-6.svg'))

# =====================================================================
# 2023/10/15-1  positionEq: null predicate is dropped
# =====================================================================
d = Diagram(1100, 470, 'When a condition method returns null, Querydsl leaves that condition out of the SQL')
d.box(40, 190, 240, 80, 'positionEq(position)', ['called inside where(…)'], color='purple', label_size=14, sub_size=12)
d.box(360, 110, 260, 70, 'If BACKEND', ['user.position.eq(position)'], color='blue', label_size=14, sub_size=12)
d.box(360, 280, 260, 70, 'If NONE', ['returns null → condition dropped'], color='amber', label_size=14, sub_size=12)
d.arrow([(280, 220), (320, 220), (320, 145), (360, 145)], color='blue')
d.arrow([(280, 240), (320, 240), (320, 315), (360, 315)], color='amber')
d.box(680, 110, 380, 70, color='blue')
d.lines(870, 133, ['WHERE user_id < ?', "  AND position = 'BACKEND'"], size=13, mono=True)
d.box(680, 280, 380, 70, color='amber')
d.lines(870, 304, ['WHERE user_id < ?', '(no position condition)'], size=13, mono=True)
d.arrow([(620, 145), (680, 145)], color='blue')
d.arrow([(620, 315), (680, 315)], color='amber')
d.text(550, 410, 'where(a, b, null) is the same as where(a, b) — one method replaces two static queries', size=13, weight=700)
d.flow([{'path': [(280, 220), (320, 220), (320, 145), (360, 145)], 'color': 'blue', 'dur': 0.7},
        {'path': [(620, 145), (680, 145)], 'color': 'blue', 'dur': 0.4, 'hold': 0.5},
        {'path': [(280, 240), (320, 240), (320, 315), (360, 315)], 'color': 'amber', 'dur': 0.7},
        {'path': [(620, 315), (680, 315)], 'color': 'amber', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2023/10/15-1.svg'))

# =====================================================================
# 2023/10/15-2  cursor pagination: last id becomes next cursor
# =====================================================================
d = Diagram(1100, 500, "Cursor pagination — the last id on one page is the next request's pageFrom (example ids)")
rows = [(100, 'Page 1 request', 'pageFrom = Long.MAX_VALUE', 'user_id < 9223372036854775807', 'id 100 … 91'),
        (250, 'Page 2 request', 'pageFrom = 91', 'user_id < 91', 'id 90 … 81')]
for y, l, s, where, res in rows:
    d.box(40, y, 220, 70, l, [s], color='gray', label_size=14, sub_size=12)
    d.arrow([(260, y + 35), (300, y + 35)], color='blue')
    d.box(300, y, 420, 70, color='blue')
    d.lines(510, y + 24, ['WHERE ' + where, 'ORDER BY user_id DESC LIMIT 10'], size=12, mono=True, gap=20)
    d.arrow([(720, y + 35), (760, y + 35)], color='blue')
    d.box(760, y, 300, 70, res, ['10 rows'], color='green', label_size=14, sub_size=12)
d.arrow([(910, 170), (910, 210), (150, 210), (150, 250)], color='green', dashed=True)
d.text(530, 198, 'The last id, 91, becomes the next cursor', size=12, weight=700, color=G['green'])
d.box(40, 360, 500, 90, 'Cursor condition on the list query only', ['The count query counts everything, so no user_id < ?', "If the count is 0, the list query isn't sent at all"], color='muted', label_size=14, sub_size=12)
d.box(560, 360, 500, 90, 'Cursor key = sort key', ['If you cut on user_id < ?, sort by user_id too,', "or page boundaries won't line up"], color='amber', label_size=14, sub_size=12)
d.flow([{'path': [(260, 135), (300, 135)], 'color': 'blue', 'dur': 0.4},
        {'path': [(720, 135), (760, 135)], 'color': 'blue', 'dur': 0.4, 'hold': 0.3},
        {'path': [(910, 170), (910, 210), (150, 210), (150, 250)], 'color': 'green', 'dur': 1.2, 'hold': 0.2},
        {'path': [(260, 285), (300, 285)], 'color': 'blue', 'dur': 0.4},
        {'path': [(720, 285), (760, 285)], 'color': 'blue', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2023/10/15-2.svg'))

# =====================================================================
# 2023/10/27-9  one-to-one: expected vs actual queries
# =====================================================================
d = Diagram(1100, 520, 'Expected 4 queries, got 54 — a contact SELECT per user slips in after the skills query')
d.text(60, 118, 'Expected', size=14, weight=700, color=G['green'], anchor='start')
exp = [('① count', 'gray'), ('② Users page', 'gray'), ('③ Skills IN', 'blue'), ('⑤ Offers IN', 'blue')]
for i, (lab, c) in enumerate(exp):
    x = 140 + i * 230
    d.box(x, 96, 200, 44, lab, color=c, label_size=13)
    if i: d.arrow([(x - 30, 118), (x, 118)], color='muted')
d.text(60, 238, 'Actual', size=14, weight=700, color=G['red'], anchor='start')
act = [('① count', 'gray', 140), ('② Users page', 'gray', 310), ('③ Skills IN', 'blue', 480)]
for lab, c, x in act:
    d.box(x, 216, 150, 44, lab, color=c, label_size=12)
for i in range(6):
    d.box(650 + i * 46, 210 + (i % 2) * 6, 40, 44, color='red')
    d.text(670 + i * 46, 238 + (i % 2) * 6, 'C', size=12, weight=700, color=G['red'])
d.text(800, 290, '④ Contact SELECT × users (page-size 50 → 50 queries)', size=12, weight=700, color=G['red'])
d.box(940, 216, 120, 44, '⑤ Offers IN', color='blue', label_size=12)
for x1, x2 in ((290, 310), (460, 480), (630, 650), (926, 940)):
    d.arrow([(x1, 238), (x2, 238)], color='muted')
d.box(60, 330, 980, 70, color='muted')
d.text(550, 358, 'No code ever called user.getContact() — Hibernate checks the contact the moment it builds each User', size=13, weight=600)
d.text(550, 382, 'IN clauses batch the lookups you write yourself; lookups fired while building entities are a separate problem', size=12, weight=600, color=MUTED)
d.box(60, 420, 470, 60, 'Before', ['54 queries · 124ms'], color='red', label_size=14, sub_size=12)
d.box(570, 420, 470, 60, 'With default_batch_fetch_size: 100', ['50 contact queries → 1 IN query · 54ms'], color='green', label_size=14, sub_size=12)
d.flow([{'path': [(140, 118), (1060, 118)], 'color': 'green', 'dur': 1.4, 'hold': 0.4},
        {'path': [(140, 238), (640, 238)], 'color': 'gray', 'dur': 0.9},
        {'path': [(650, 238), (926, 238)], 'color': 'red', 'dur': 1.6, 'hold': 0.2},
        {'path': [(940, 238), (1060, 238)], 'color': 'blue', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2023/10/27-9.svg'))

# =====================================================================
# 2023/10/27-10  one-to-one: proxy vs immediate select
# =====================================================================
d = Diagram(1100, 560, "Lazy loading needs a proxy — when a one-to-one can't get one, Hibernate SELECTs right away")
d.group(40, 90, 490, 380, '@ManyToOne — a proxy can be created', color='green')
d.box(70, 130, 200, 70, 'Skill row', ['user_id = 7'], color='gray', label_size=14, sub_size=12)
d.box(310, 130, 190, 70, 'User proxy', ['id = 7, not loaded yet'], color='green', label_size=14, sub_size=12)
d.arrow([(270, 165), (310, 165)], color='green')
d.text(180, 224, 'Proxy built from the FK alone', size=11, weight=700, color=G['green'])
d.box(70, 240, 430, 60, 'When skill.getUser().getName() is called', ['the first SELECT runs — lazy loading holds'], color='green', label_size=13, sub_size=11)
d.arrow([(405, 200), (405, 240)], color='green')
d.note(70, 330, 430, 110, ['"If there is a related user, its id is 7" is', 'enough to plug in a proxy. Whether it might be', 'missing is already known from a NULL FK.'], color='green', size=12)
d.group(570, 90, 490, 380, '@OneToOne — it must know if the row exists', color='red')
d.box(600, 130, 200, 70, 'User row', ['Is there a contact?'], color='gray', label_size=14, sub_size=12)
d.box(840, 130, 190, 70, 'null or a proxy?', ['Must check to decide'], color='amber', label_size=13, sub_size=11)
d.arrow([(800, 165), (840, 165)], color='amber')
d.box(600, 240, 430, 60, 'SELECT contact … as each User is built', ['once per user — N+1'], color='red', label_size=13, sub_size=11)
d.arrow([(935, 200), (935, 240)], color='red')
d.note(600, 330, 430, 110, ['The side without the FK (mappedBy) in particular', "can't tell from its table whether a match exists.", 'FetchType.LAZY is a hint, not a guarantee.'], color='red', size=12)
d.text(550, 500, 'Fix: default_batch_fetch_size folds these lookups into one IN query', size=12, weight=700)
d.text(550, 522, "Switching to @ManyToOne would also work, but the domain really is one-to-one, so I didn't", size=12, weight=700)
d.flow([{'path': [(270, 165), (310, 165)], 'color': 'green', 'dur': 0.5}, {'path': [(405, 200), (405, 240)], 'color': 'green', 'dur': 0.5, 'hold': 0.4},
        {'path': [(800, 165), (840, 165)], 'color': 'amber', 'dur': 0.5}, {'path': [(935, 200), (935, 240)], 'color': 'red', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2023/10/27-10.svg'))

# =====================================================================
# 2024/06/12-1  Spring Boot upgrade path
# =====================================================================
d = Diagram(1100, 500, 'Two steps, not one jump — clean up on the last 2.x release first, then move to 3.3')
stages = [
    (40, 'Starting point', ['Spring Boot 2.7.1', 'Java 11', 'Gradle 7.6.1', 'javax.*'], 'gray'),
    (400, 'Step 1: last 2.x release', ['Spring Boot 2.7.18', 'Java 21', 'Gradle unchanged', 'Check deps and deprecations'], 'blue'),
    (760, 'Step 2: latest 3.x', ['Spring Boot 3.3.0', 'dependency-management 1.1.5', 'Gradle 8.7', 'Querydsl 5.0.0:jakarta'], 'green'),
]
for x, lab, sub, c in stages:
    d.box(x, 96, 300, 170, lab, sub, color=c, label_size=16, sub_size=13)
d.arrow([(340, 181), (400, 181)], color='blue')
d.arrow([(700, 181), (760, 181)], color='green')
d.group(40, 300, 1020, 140, 'Step 3: what breaks compiling and running on 3.3 — code changes', color='amber')
fixes = [('javax → jakarta', 'Bulk import change'), ('SecurityConfig', 'Rewrite in lambda DSL'),
         ('@Table', 'schema.table → catalog'), ('Querydsl', 'Review template code'), ('buildspec.yml', 'Bump Java version')]
for i, (lab, sub) in enumerate(fixes):
    d.box(52 + i * 202, 338, 190, 80, lab, [sub], color='amber', label_size=14, sub_size=12)
d.arrow([(910, 266), (910, 300)], color='amber')
d.text(550, 472, 'Clear the deprecation warnings on 2.7.18 first, and what breaks on 3.x narrows down to "removed APIs"', size=13, weight=600, color=MUTED)
d.flow([{'path': [(190, 181), (340, 181), (400, 181), (550, 181)], 'color': 'blue', 'dur': 1.2, 'hold': 0.3},
        {'path': [(550, 181), (700, 181), (760, 181), (910, 181)], 'color': 'green', 'dur': 1.2, 'hold': 0.3},
        {'path': [(910, 266), (910, 300)], 'color': 'amber', 'dur': 0.5, 'hold': 1.0}])
d.save(out('2024/06/12-1.svg'))

# =====================================================================
# 2024/07/24-1  race condition vs distributed lock timeline
# =====================================================================
d = Diagram(1100, 560, 'Without a lock, both servers act on the same state — a distributed lock lines up same-key requests')
d.group(30, 84, 1040, 210, 'No lock — each server checks on its own', color='red')
d.text(80, 150, 'Server A', size=14, weight=700, anchor='middle')
d.text(80, 230, 'Server B', size=14, weight=700, anchor='middle')
d.box(140, 128, 200, 44, '① Read: not there yet', color='gray', label_size=13)
d.box(300, 208, 200, 44, '② Read: not there yet', color='gray', label_size=13)
d.box(500, 128, 210, 44, '③ Process and save', color='blue', label_size=13)
d.box(680, 208, 220, 44, '④ Process and save again', color='red', label_size=13)
d.note(920, 138, 130, 104, ['Same request', 'handled twice'], color='red', size=13)
d.text(540, 274, "When B read, A hadn't saved yet — synchronized only guards a single JVM", size=12, weight=600, color=MUTED)
d.group(30, 314, 1040, 210, "Redisson lock — key = 'function_' + #request.id", color='green')
d.text(80, 380, 'Server A', size=14, weight=700, anchor='middle')
d.text(80, 460, 'Server B', size=14, weight=700, anchor='middle')
d.box(140, 358, 140, 44, 'Acquire lock', color='green', label_size=13)
d.box(300, 358, 230, 44, 'Read · process · save', color='blue', label_size=13)
d.box(550, 358, 110, 44, 'unlock', color='green', label_size=13)
d.box(140, 438, 520, 44, 'Waiting in tryLock (up to waitTime, 5s)', color='amber', dashed=True, label_size=13)
d.box(680, 438, 220, 44, 'Acquire lock → read', color='green', label_size=13)
d.note(920, 368, 130, 104, ['Sees what', 'A saved'], color='green', size=13)
d.text(540, 504, 'Only requests with the same key wait — different keys never block each other', size=12, weight=600, color=MUTED)
d.flow([{'path': [(140, 150), (710, 150)], 'color': 'blue', 'dur': 1.4},
        {'path': [(300, 230), (900, 230)], 'color': 'red', 'dur': 1.4, 'hold': 0.5},
        {'path': [(140, 380), (660, 380)], 'color': 'green', 'dur': 1.4},
        {'path': [(660, 460), (900, 460)], 'color': 'green', 'dur': 0.8, 'hold': 0.8}])
d.save(out('2024/07/24-1.svg'))

# =====================================================================
# 2024/07/24-2  RedissonLockAspect flow
# =====================================================================
d = Diagram(1100, 420, 'What RedissonLockAspect does — compute the key, tryLock, run the method, unlock in finally')
row = [('Method call', '@RedissonLock', 'gray'), ('Compute key', 'SpEL: #request.id', 'blue'),
       ('tryLock', 'waitTime 5s · leaseTime 2s', 'amber'), ('proceed()', 'Run the method', 'green'),
       ('finally', 'unlock() if acquired', 'green')]
for i, (lab, sub, c) in enumerate(row):
    d.box(40 + i * 210, 100, 180, 76, lab, [sub], color=c, label_size=15, sub_size=11)
for i in range(4):
    x = 220 + i * 210
    d.arrow([(x, 138), (x + 30, 138)], color='muted')
d.text(655, 116, 'OK', size=11, weight=700, color=G['green'])
d.box(300, 240, 380, 76, 'Not acquired → return false', ['A void method drops this value — throw instead'], color='red', label_size=14, sub_size=12)
d.arrow([(510, 176), (510, 240)], color='red')
d.text(520, 208, 'waitTime exceeded', size=11, weight=700, color=G['red'], anchor='start')
d.box(700, 240, 360, 76, 'Once leaseTime (2s) passes', ['the lock is released mid-method · unlock() fails'], color='amber', label_size=14, sub_size=12)
d.arrow([(760, 176), (760, 240)], color='amber', dashed=True)
d.text(550, 370, 'Why unlock() gets its own try/catch: unlocking an already released lock throws IllegalMonitorStateException', size=13, weight=600, color=MUTED)
d.flow([{'path': [(130, 138), (340, 138), (550, 138)], 'color': 'blue', 'dur': 1.0},
        {'path': [(550, 138), (760, 138), (970, 138)], 'color': 'green', 'dur': 1.0, 'hold': 0.5},
        {'path': [(510, 176), (510, 240)], 'color': 'red', 'dur': 0.6, 'hold': 0.8}])
d.save(out('2024/07/24-2.svg'))

# =====================================================================
# 2024/07/25-7  migration plan: split test accounts
# =====================================================================
d = Diagram(1100, 480, 'Split 10 test accounts in half — migrate 1–5 before the main query, verify 6–10 after it runs')
cols = [
    (40, 'Pre-run test (IDs 1–5)', 'blue', ['① Confirm targets (not there yet)', '② INSERT just these 5 via IN', '③ Check the hashes in the DB', '④ Log in on the app and web']),
    (385, 'Main query (everyone)', 'amber', ['① COUNT the rows to migrate', '② Confirm 6–10 are not there yet', '③ Full INSERT … SELECT']),
    (730, 'Post-run check (IDs 6–10)', 'green', ['① Check the hashes in the DB', '② Log in on the app and web']),
]
for x, lab, c, steps in cols:
    d.group(x, 90, 330, 330, lab, color=c)
    for i, s in enumerate(steps):
        d.box(x + 15, 126 + i * 70, 300, 52, s, color=c, label_size=13)
    for i in range(len(steps) - 1):
        d.arrow([(x + 165, 178 + i * 70), (x + 165, 196 + i * 70)], color=c)
d.arrow([(370, 255), (385, 255)], color='amber')
d.arrow([(715, 255), (730, 255)], color='green')
d.text(550, 452, "1–5 are already migrated, so the main query's LEFT JOIN … IS NULL skips them — rerunning it adds no duplicates", size=12, weight=600, color=MUTED)
d.flow([{'path': [(205, 178), (205, 196), (205, 248), (205, 266), (205, 318), (205, 336)], 'color': 'blue', 'dur': 1.2, 'hold': 0.3},
        {'path': [(550, 178), (550, 196), (550, 248), (550, 266)], 'color': 'amber', 'dur': 0.9, 'hold': 0.3},
        {'path': [(895, 178), (895, 196)], 'color': 'green', 'dur': 0.5, 'hold': 1.0}])
d.save(out('2024/07/25-7.svg'))

# =====================================================================
# 2024/07/25-8  anti-join picks only rows not yet migrated
# =====================================================================
d = Diagram(1100, 500, 'LEFT JOIN … IS NULL picks only users not yet migrated — 1–5, moved during testing, are skipped')
d.text(160, 104, 'users', size=14, weight=700, mono=True)
d.text(460, 104, 'user_password (LEFT JOIN)', size=14, weight=700, mono=True)
d.text(860, 104, 'Rows inserted', size=14, weight=700)
ids = [4, 5, 6, 7, 8, 9]
for i, uid in enumerate(ids):
    y = 124 + i * 52
    d.box(60, y, 200, 40, f'user_id = {uid}', color='gray', label_size=13)
    d.arrow([(260, y + 20), (330, y + 20)], color='muted')
    if uid <= 5:
        d.box(330, y, 260, 40, f'user_id = {uid} · has a hash', color='blue', label_size=13)
    else:
        d.box(330, y, 260, 40, 'NULL → migrate', color='red', dashed=True, label_size=13)
        d.arrow([(590, y + 20), (700, y + 20)], color='green')
        d.box(700, y, 330, 40, f'({uid}, SHA2(password, 256))', color='green', label_size=13)
d.text(865, 170, 'Already there, skipped', size=13, weight=600, color=MUTED)
d.text(550, 452, 'SHA2(…, 256) returns a 64-character hex string · with no salt, the same input always gives the same hash', size=12, weight=600, color=MUTED)
d.flow([{'path': [(160, 248), (260, 248), (330, 248), (590, 248), (700, 248), (865, 248)], 'color': 'green', 'dur': 1.4, 'hold': 0.3},
        {'path': [(160, 144), (260, 144), (330, 144), (460, 144)], 'color': 'blue', 'dur': 0.9, 'hold': 0.8}])
d.save(out('2024/07/25-8.svg'))
print('backend_2023_2024 ok')
