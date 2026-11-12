"""English diagrams for the 2026 frontend posts (cookies, WebSocket, unread badge, basePath, next start).
English copy of the 2026 blocks in tools/diagrams/make_diagrams_batch2.py.
Run: python3 tools/diagrams/en/frontend_2026.py "$PWD"
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from diag import Diagram, INK, MUTED

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img/en', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

G = {'gray': '#1f2937', 'muted': '#6b7280', 'blue': '#2563eb', 'green': '#059669', 'red': '#dc2626', 'amber': '#d97706', 'purple': '#7c3aed'}

# =====================================================================
# 2026/06/16-1  cookies: same name, two jars → 401 loop
# =====================================================================
d = Diagram(1100, 560, 'Two cookies, one name — the browser sends both, the BFF reads one, and the 401 repeats')
d.group(40, 96, 280, 170, 'Browser cookie jar')
d.box(55, 126, 250, 54, color='red'); d.lines(180, 146, ['refresh_token  (old token)', 'Domain=.example.com'], size=11, weight=600, mono=True)
d.box(55, 196, 250, 54, color='green'); d.lines(180, 216, ['refresh_token  (new token)', 'Domain=svc-a.example.com'], size=11, weight=600, mono=True)
d.group(430, 96, 300, 170, 'BFF  app/api/account/auth/token')
d.box(450, 126, 260, 50, 'RequestCookies', ['Map(name → value): one entry per name'], color='amber', label_size=13, sub_size=11)
d.box(450, 196, 260, 54, 'getRefreshToken(req)', ['→ reads the old token'], color='red', label_size=13, sub_size=11)
d.box(820, 126, 240, 124, 'Account API', ['POST /auth/token', 'old token → 401'], color='gray', label_size=14)
d.arrow([(320, 181), (430, 181)], color='gray')
d.lines(375, 138, ['Cookie:', 'refresh_token=old;', 'refresh_token=new'], size=9, weight=700, gap=13, mono=True)
d.arrow([(580, 176), (580, 196)], color='amber')
d.arrow([(710, 223), (820, 223)], color='red', label='Bearer old token', label_dy=-8, label_size=11)
d.arrow([(940, 250), (940, 300), (190, 300), (190, 266)], color='red', label='401 TOKEN_UNAUTHENTICATED — only the host cookie is cleared; the apex cookie stays → the next request takes the same path', label_dy=14, label_size=11)
d.box(40, 350, 1020, 60, color='muted')
d.text(550, 372, 'RFC 6265: a cookie is identified by (name, domain, path) — a different Domain makes it a separate cookie, so both are kept and sent', size=12, weight=600)
d.text(550, 394, 'Next.js RequestCookies: a Map keyed by name only — just one of them is read, and which one depends on the browser\'s header order', size=12, weight=600)
d.box(40, 430, 1020, 100, color='green')
d.text(550, 456, 'Fix (#374): every response that writes a token cookie also sends a Set-Cookie that expires the old apex cookie', size=13, weight=700, color=G['green'])
d.text(550, 482, 'Set-Cookie: refresh_token=; Domain=.example.com; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT', size=12, weight=600, mono=True)
d.text(550, 508, '→ after one login, refresh or logout the old cookie is gone. But "also sends" is what caused the next incident (figure 2)', size=12, weight=600, color=MUTED)
d.flow([{'path': [(320, 181), (430, 181)], 'color': 'gray', 'dur': 0.6},
        {'path': [(580, 176), (580, 196)], 'color': 'amber', 'dur': 0.3},
        {'path': [(710, 223), (820, 223)], 'color': 'red', 'dur': 0.5},
        {'path': [(940, 250), (940, 300), (190, 300), (190, 266)], 'color': 'red', 'dur': 1.2, 'hold': 0.4}], loop_pause=0.3)
d.save(out('2026/06/16-1.svg'))

# =====================================================================
# 2026/06/16-2  cookies: ResponseCookies Map overwrite
# =====================================================================
d = Diagram(1100, 640, 'ResponseCookies has one Map slot per name — the second set() overwrites the token just issued')
d.group(40, 86, 1020, 250, 'Before (#384): res.cookies.set twice')
d.box(60, 120, 300, 60, '① res.cookies.set("access_token", token,', ['{ domain: "svc-a-dev.example.com" })'], color='green', label_size=12, sub_size=11)
d.box(60, 200, 300, 60, '② res.cookies.set("access_token", "",', ['{ domain: ".example.com", expires: 0 })'], color='red', label_size=12, sub_size=11)
d.group(440, 120, 240, 140, '_parsed: Map', color='amber')
d.box(460, 160, 200, 40, color='green', dashed=True); d.text(560, 185, 'access_token → token', size=11, weight=700, color=G['green'], mono=True)
d.box(460, 210, 200, 40, color='red'); d.text(560, 235, 'access_token → ""', size=11, weight=700, color=G['red'], mono=True)
d.text(560, 150, 'key = name', size=11, color=MUTED)
d.group(760, 120, 280, 140, 'Set-Cookie headers (on the wire)', color='gray')
d.text(900, 170, 'replace(): headers.delete("set-cookie")', size=10, weight=600, color=MUTED, mono=True)
d.text(900, 190, '→ rewritten from the Map', size=10, weight=600, color=MUTED)
d.box(780, 205, 240, 40, color='red'); d.text(900, 230, 'access_token=; Domain=.example.com', size=10, weight=700, color=G['red'], mono=True)
d.arrow([(360, 150), (440, 180)], color='green'); d.arrow([(360, 230), (440, 230)], color='red')
d.arrow([(680, 190), (760, 190)], color='gray')
d.text(550, 300, 'Login is 200 and the backend issued a token, yet the only Set-Cookie that reaches the browser is the expired apex one — one slot, any Domain', size=12, weight=700, color=G['red'])
d.text(550, 322, 'A raw Set-Cookie header appended earlier is wiped out by the same delete in replace()', size=12, weight=600, color=MUTED)
d.group(40, 356, 1020, 260, 'After (#389): the second cookie never goes through the Map')
d.box(60, 390, 300, 60, '① res.cookies.set("access_token", token,', ['{ domain: "svc-a-dev.example.com" })'], color='green', label_size=12, sub_size=11)
d.box(60, 470, 300, 60, '② res.headers.append("set-cookie",', ['"access_token=; Domain=.example.com; Expires=…")'], color='blue', label_size=12, sub_size=11)
d.group(440, 384, 240, 66, '_parsed: Map', color='amber')
d.box(460, 418, 200, 26, color='green'); d.text(560, 435, 'access_token → token', size=11, weight=700, color=G['green'], mono=True)
d.group(760, 390, 280, 140, 'Set-Cookie headers (on the wire)', color='gray')
d.box(780, 430, 240, 36, color='green'); d.text(900, 453, 'access_token=token; Domain=svc-a-dev…', size=10, weight=700, color=G['green'], mono=True)
d.box(780, 476, 240, 36, color='blue'); d.text(900, 499, 'access_token=; Domain=.example.com', size=10, weight=700, color=G['blue'], mono=True)
d.arrow([(360, 420), (440, 420)], color='green'); d.arrow([(680, 420), (760, 448)], color='gray')
d.arrow([(360, 500), (720, 500), (780, 494)], color='blue', label='skips the Map: raw header, appended directly', label_dy=14, label_size=11)
d.text(550, 566, 'Order matters: append after the last cookies.set. One more cookies.set after that, and replace() deletes the raw header', size=12, weight=700, color=G['blue'])
d.text(550, 592, 'The test changed too: a jest.fn() mock of res.cookies.set can\'t imitate the Map → assert on a real NextResponse + headers.getSetCookie()', size=12, weight=600, color=MUTED)
d.flow([{'path': [(360, 150), (440, 180)], 'color': 'green', 'dur': 0.5},
        {'path': [(360, 230), (440, 230)], 'color': 'red', 'dur': 0.5},
        {'path': [(680, 190), (760, 190)], 'color': 'red', 'dur': 0.5, 'hold': 0.8},
        {'path': [(360, 420), (440, 420)], 'color': 'green', 'dur': 0.5},
        {'path': [(680, 420), (760, 448)], 'color': 'green', 'dur': 0.4},
        {'path': [(360, 500), (720, 500), (780, 494)], 'color': 'blue', 'dur': 0.8, 'hold': 0.8}])
d.pulse(780, 205, 240, 40, color='red', start=0.30, end=0.48, total=6.3)
d.save(out('2026/06/16-2.svg'))

# =====================================================================
# 2026/07/24-1  websocket: flapping loop
# =====================================================================
d = Diagram(1100, 600, 'Reconnect flapping — deactivate() calls onWebSocketClose again, and onConnect resets the count to 0')
d.group(40, 86, 300, 300, 'stompjs ActivationState')
d.box(90, 116, 200, 58, 'ACTIVE', ['after activate();', 'a socket drop doesn\'t change it'], color='green', label_size=14, sub_size=10)
d.box(90, 210, 200, 50, 'DEACTIVATING', ['right after deactivate()'], color='amber', label_size=14, sub_size=10)
d.box(90, 300, 200, 50, 'INACTIVE', ['once the socket is closed'], color='muted', label_size=14, sub_size=10)
d.arrow([(190, 174), (190, 210)], color='amber', label='deactivate()', label_dy=-2, label_size=11)
d.arrow([(190, 260), (190, 300)], color='muted')
d.arrow([(290, 325), (320, 325), (320, 145), (290, 145)], color='green')
d.text(316, 235, 'activate()', size=11, weight=700, color=G['green'], anchor='end')
d.text(190, 372, 'client.active === (state === ACTIVE)', size=11, weight=600, color=MUTED, mono=True)
# sequence on the right
d.box(400, 110, 180, 56, 'Network drop ✕', color='red', label_size=13)
d.box(640, 110, 200, 56, 'onWebSocketClose', ['attempt 0 → 1, banner ON'], color='gray', label_size=13, sub_size=11)
d.box(900, 110, 160, 56, '1 s timer', color='gray', label_size=13)
d.box(900, 230, 160, 56, 'deactivate()', ['ACTIVE → DEACTIVATING'], color='amber', label_size=13, sub_size=11)
d.box(640, 230, 200, 56, 'onWebSocketClose (again)', ['attempt 1 → 2, another timer'], color='red', label_size=13, sub_size=11)
d.box(900, 350, 160, 56, 'activate()', color='green', label_size=13)
d.box(640, 350, 200, 56, 'onConnect', ['attempt = 0  ← cap never hit'], color='green', label_size=13, sub_size=11)
d.arrow([(580, 138), (640, 138)], color='red'); d.arrow([(840, 138), (900, 138)], color='gray')
d.arrow([(980, 166), (980, 230)], color='gray')
d.arrow([(900, 258), (840, 258)], color='red', dashed=True)
d.text(860, 306, 'keeps the app callback and calls it', size=10, weight=700, color=G['red'])
d.arrow([(980, 286), (980, 350)], color='green')
d.text(986, 318, '.then(() => activate())', size=10, weight=700, color=G['green'], anchor='start')
d.arrow([(900, 378), (840, 378)], color='green')
d.arrow([(740, 406), (740, 440), (490, 440), (490, 166)], color='red', dashed=True, label='next drop → start over', label_dy=14, label_size=11)
d.box(400, 476, 660, 104, color='green')
d.text(730, 498, 'Fix (#349): if (!client.active) return; at the top of onWebSocketClose and in the timer body', size=13, weight=700, color=G['green'])
d.text(730, 520, 'Deactivating: state is DEACTIVATING → active is false → no reconnect', size=12, weight=600)
d.text(730, 540, 'Network drop: state stays ACTIVE → reconnect exactly once', size=12, weight=600)
d.text(730, 562, 'Unmount\'s deactivate() takes the same path, so the zombie sockets went away too', size=12, weight=600, color=MUTED)
d.flow([{'path': [(580, 138), (640, 138)], 'color': 'red', 'dur': 0.4},
        {'path': [(840, 138), (900, 138)], 'color': 'gray', 'dur': 0.3},
        {'path': [(980, 166), (980, 230)], 'color': 'gray', 'dur': 0.4},
        {'path': [(900, 258), (840, 258)], 'color': 'red', 'dur': 0.4, 'hold': 0.4},
        {'path': [(980, 286), (980, 350)], 'color': 'green', 'dur': 0.4},
        {'path': [(900, 378), (840, 378)], 'color': 'green', 'dur': 0.3},
        {'path': [(740, 406), (740, 440), (490, 440), (490, 166)], 'color': 'red', 'dur': 1.0, 'hold': 0.3}], loop_pause=0.4)
d.save(out('2026/07/24-1.svg'))

# =====================================================================
# 2026/07/24-2  websocket: heartbeat negotiation
# =====================================================================
d = Diagram(1100, 620, 'STOMP heartbeats are negotiated — if the server advertises 0,0, the client\'s setting is void')
cols = {'cl': 170, 'px': 500, 'sv': 830}
for key, label, sub in (('cl', 'Browser (stompjs)', 'heartbeat default 10000,10000'), ('px', 'Proxy', 'idle timeout ≈ 60 s'), ('sv', 'Spring SimpleBroker', 'no TaskScheduler')):
    d.box(cols[key] - 110, 86, 220, 50, label, [sub], color='gray', label_size=13, sub_size=11)
    d.arrow([(cols[key], 136), (cols[key], 548)], color='muted', head=False, dashed=True, width=1)
d.text(60, 170, 'Before', size=13, weight=700, color=G['red'], anchor='start')
d.arrow([(cols['cl'], 180), (cols['sv'], 180)], color='blue', label='CONNECT  heart-beat:10000,10000', label_dy=-8, label_size=11)
d.arrow([(cols['sv'], 215), (cols['cl'], 215)], color='red', label='CONNECTED  heart-beat:0,0   ← a 0 from the server turns that direction off', label_dy=-8, label_size=11)
d.box(cols['cl'] - 100, 240, 200, 40, color='muted', dashed=True); d.text(cols['cl'], 265, 'pinger ✕   ponger ✕', size=12, weight=700, color=MUTED)
d.text(cols['px'], 262, '… 0 bytes for 60 s …', size=12, weight=600, color=MUTED)
d.arrow([(cols['px'], 300), (cols['cl'], 300)], color='red', label='FIN (idle) → onWebSocketClose → banner → reconnect → idle again …', label_dy=-8, label_size=11)
d.arrow([(cols['cl'] - 110, 335), (cols['sv'] + 110, 335)], color='muted', head=False, width=1)
d.text(60, 365, 'After (#471)', size=13, weight=700, color=G['green'], anchor='start')
d.arrow([(cols['cl'], 380), (cols['sv'], 380)], color='blue', label='CONNECT  heart-beat:25000,25000', label_dy=-8, label_size=11)
d.arrow([(cols['sv'], 415), (cols['cl'], 415)], color='green', label='CONNECTED  heart-beat:25000,25000   → both ways max(25000, 25000) = 25 s', label_dy=-8, label_size=11)
for i, y in enumerate((455, 490, 525)):
    d.arrow([(cols['cl'], y), (cols['sv'], y)], color='green', head=False, dashed=True, width=1)
    d.text(cols['px'] + 150, y - 6, 'every 25 s · LF ●  (both ways) — resets the proxy timer', size=10, weight=600, color=G['green'])
d.box(40, 556, 1020, 56, color='amber')
d.text(550, 574, 'Spring needs both setHeartbeatValue(longArrayOf(25_000, 25_000)) and setTaskScheduler(ThreadPoolTaskScheduler) — one alone fails an Assert at startup', size=11, weight=700)
d.text(550, 596, 'stompjs: PING only if heartbeatOutgoing≠0 && serverIncoming≠0; PONG watch only if heartbeatIncoming≠0 && serverOutgoing≠0', size=11, weight=600, color=MUTED, mono=True)
d.flow([{'path': [(cols['cl'], 180), (cols['sv'], 180)], 'color': 'blue', 'dur': 0.7},
        {'path': [(cols['sv'], 215), (cols['cl'], 215)], 'color': 'red', 'dur': 0.7, 'hold': 0.6},
        {'path': [(cols['px'], 300), (cols['cl'], 300)], 'color': 'red', 'dur': 0.5, 'hold': 0.5},
        {'path': [(cols['cl'], 380), (cols['sv'], 380)], 'color': 'blue', 'dur': 0.7},
        {'path': [(cols['sv'], 415), (cols['cl'], 415)], 'color': 'green', 'dur': 0.7},
        {'path': [(cols['cl'], 455), (cols['sv'], 455)], 'color': 'green', 'dur': 0.5},
        {'path': [(cols['sv'], 490), (cols['cl'], 490)], 'color': 'green', 'dur': 0.5},
        {'path': [(cols['cl'], 525), (cols['sv'], 525)], 'color': 'green', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/07/24-2.svg'))

# =====================================================================
# 2026/07/24-3  websocket: first-entry race
# =====================================================================
d = Diagram(1100, 600, 'First-entry race — the direct WebSocket\'s CONNECTED beats the BFF-routed REST call and is lost')
d.text(60, 120, 'WS', size=14, weight=700, color=G['blue'], anchor='start')
d.text(60, 240, 'REST', size=14, weight=700, color=G['amber'], anchor='start')
d.arrow([(130, 130), (330, 130)], color='blue', width=6, head=False)
d.text(230, 92, 'browser → backend direct: 1 hop, JWT signature check only', size=11, weight=600, color=G['blue'])
d.box(330, 100, 150, 56, 'CONNECTED', ['setConnectionStatus()'], color='blue', label_size=13, sub_size=11)
d.box(540, 100, 230, 56, 'conversations: {}', ['no entries → nothing to update'], color='red', dashed=True, label_size=13, sub_size=11)
d.text(800, 134, '✕ lost (no-op)', size=13, weight=700, color=G['red'], anchor='start')
d.arrow([(480, 128), (540, 128)], color='blue')
d.arrow([(130, 250), (640, 250)], color='amber', width=6, head=False)
d.text(380, 236, 'browser → BFF route → backend → DB (30 rows + mentions, attachments, reactions) → BFF → browser', size=10, weight=600, color=G['amber'])
d.box(640, 220, 170, 56, 'mergeHistory()', ['creates the entry'], color='amber', label_size=13, sub_size=11)
d.box(850, 220, 210, 56, 'connectionStatus:', ['"DISCONNECTED" (default)'], color='red', label_size=13, sub_size=11)
d.arrow([(810, 248), (850, 248)], color='amber')
d.text(550, 300, 'The socket is already CONNECTED, so no status event comes again → the banner sticks and the input stays disabled.', size=12, weight=600, color=MUTED)
d.text(550, 320, 'In the next room REST is faster (warmed up) and the order flips — hence "only on first entry".', size=12, weight=600, color=MUTED)
d.group(40, 340, 500, 230, 'Before: connection status inside each conversation entry')
d.lines(290, 380, ['conversations: {', '  "dm:7": { messages, readState,', '            connectionStatus }   ← copied per resource', '}', 'setConnectionStatus: loops over existing entries only'], size=12, weight=600, gap=22, mono=True)
d.text(290, 520, 'race: entry creation vs. status event arrival', size=12, weight=700, color=G['red'])
d.group(580, 340, 480, 230, 'After (#753): a top-level store field')
d.lines(820, 380, ['conversations: { "dm:7": { messages, readState } }', 'connectionStatus: "CONNECTED"   ← per client', '', 'setConnectionStatus: (s) => set({ connectionStatus: s })', 'useMessageStore((s) => s.connectionStatus)'], size=12, weight=600, gap=22, mono=True)
d.text(820, 520, 'recorded whether or not an entry exists → no race', size=12, weight=700, color=G['green'])
d.flow([{'path': [(130, 130), (330, 130)], 'color': 'blue', 'dur': 0.6, 'hold': 0.0},
        {'path': [(480, 128), (540, 128)], 'color': 'blue', 'dur': 0.3, 'hold': 2.1}], loop_pause=1.0)
d.flow([{'path': [(130, 250), (640, 250)], 'color': 'amber', 'dur': 2.2, 'hold': 0.0},
        {'path': [(810, 248), (850, 248)], 'color': 'amber', 'dur': 0.3, 'hold': 0.5}], loop_pause=1.0)
d.save(out('2026/07/24-3.svg'))

# =====================================================================
# 2026/07/28-1  unread: three failures
# =====================================================================
d = Diagram(1100, 620, '"+1 per frame" goes wrong three ways — no initial value, two-topic fan-out, zombie sockets')
panels = [(40, '① Cold load (06-16)', 'amber'), (385, '② DM on two topics (07-24)', 'red'), (730, '③ Mail zombie sockets (07-28)', 'red')]
for x, label, c in panels:
    d.group(x, 86, 330, 440, label)
# panel 1
d.box(60, 130, 130, 70, 'Server DB', ['5 unread'], color='gray', label_size=13)
d.box(240, 130, 110, 70, 'counts', ['{}  → 0'], color='amber', label_size=13)
d.arrow([(190, 165), (240, 165)], color='muted', dashed=True)
d.text(215, 218, 'no count API ✕', size=11, weight=700, color=MUTED)
d.note(60, 240, 290, 120, ['The badge = frames received this session.', 'Refresh and it starts at 0. Reading on', 'another device doesn\'t lower it.', 'A limit we knew about.'], color='amber', size=12)
d.text(205, 400, 'What we needed: a number the server counts', size=12, weight=700, color=MUTED)
# panel 2
d.box(405, 130, 130, 50, 'Server', ['1 DM message'], color='gray', label_size=13)
d.box(585, 110, 110, 40, '/topic/dm.7', color='blue', label_size=11)
d.box(585, 170, 110, 40, '/topic/user.42', color='purple', label_size=11)
d.arrow([(535, 150), (585, 130)], color='blue'); d.arrow([(535, 160), (585, 190)], color='purple')
d.box(425, 250, 270, 60, 'increment("dm:7")  ×2', ['no message id → can\'t dedupe'], color='red', label_size=13, sub_size=11)
d.arrow([(695, 130), (712, 130), (712, 262), (695, 262)], color='blue'); d.arrow([(620, 210), (620, 250)], color='purple')
d.box(425, 330, 270, 44, 'badge 2  (bubble deduped by id: 1)', color='red', label_size=12)
d.note(405, 400, 290, 100, ['Fix: the user event counts only new DM', 'rooms not in the list yet. Existing', 'rooms are left to the dm topic.'], color='green', size=12)
# panel 3
d.box(750, 130, 130, 50, 'Broker', ['1 NEW_MAIL frame'], color='gray', label_size=13)
d.box(930, 110, 110, 36, 'Client B', color='green', label_size=11)
d.box(930, 156, 110, 36, 'A (zombie)', color='red', dashed=True, label_size=11)
d.box(930, 202, 110, 36, "A′ (zombie)", color='red', dashed=True, label_size=11)
for y in (128, 174, 220): d.arrow([(880, 155), (930, y)], color='gray')
d.box(770, 260, 270, 60, 'incrementUnread()  ×(1 + zombies)', ['prod code calling resetUnread: 0'], color='red', label_size=12, sub_size=11)
d.arrow([(985, 238), (985, 260)], color='red')
d.box(770, 340, 270, 44, '1 actual mail → badge 4', color='red', label_size=12)
d.note(750, 400, 290, 100, ['StrictMode was suspected — innocent.', 'Real duplicates: unguarded reconnect', '→ zombie sockets. Outcome: counter', 'removed, the server counts.'], color='green', size=12)
d.box(40, 546, 1020, 50, color='muted'); d.text(550, 566, 'Common root: mistaking "events received" for "unread items"', size=14, weight=700); d.text(550, 586, 'The server should count; a realtime event should only mean "ask again"', size=12, weight=600, color=MUTED)
d.flow([{'path': [(535, 150), (585, 130)], 'color': 'blue', 'dur': 0.4}, {'path': [(695, 130), (712, 130), (712, 262), (695, 262)], 'color': 'blue', 'dur': 0.5, 'hold': 0.1},
        {'path': [(535, 160), (585, 190)], 'color': 'purple', 'dur': 0.4}, {'path': [(620, 210), (620, 250)], 'color': 'purple', 'dur': 0.4, 'hold': 0.6},
        {'path': [(880, 155), (930, 128)], 'color': 'gray', 'dur': 0.3}, {'path': [(880, 155), (930, 174)], 'color': 'red', 'dur': 0.3}, {'path': [(880, 155), (930, 220)], 'color': 'red', 'dur': 0.3},
        {'path': [(985, 238), (985, 260)], 'color': 'red', 'dur': 0.3, 'hold': 0.8}])
d.save(out('2026/07/28-1.svg'))

# =====================================================================
# 2026/07/28-2  unread: zombie socket sequence
# =====================================================================
d = Diagram(1100, 660, 'Zombie socket — client A, closed by a folder switch, revives 1 s later via an unguarded close handler')
L = {'fx': 130, 'a': 400, 'b': 620, 'br': 880}
for k, label, c in (('fx', 'React effect', 'gray'), ('a', 'Client A', 'red'), ('b', 'Client B', 'green'), ('br', 'Spring broker', 'gray')):
    d.box(L[k] - 80, 86, 160, 40, label, color=c, label_size=13)
    d.arrow([(L[k], 126), (L[k], 500)], color='muted', head=False, dashed=True, width=1)
steps = [
    (150, L['fx'], L['a'], 'gray', '① folder switch → cleanup → A.deactivate()'),
    (185, L['a'], L['br'], 'gray', '② DISCONNECT receipt:close-1'),
    (220, L['br'], L['a'], 'gray', '③ RECEIPT → socket close → onWebSocketClose (no guard)'),
    (265, L['fx'], L['b'], 'green', '④ new effect → B.activate() → SUBSCRIBE /topic/mail.42'),
    (310, L['a'], L['a'] + 120, 'red', '⑤ 1 s later A.deactivate().then(A.activate())  ← zombie'),
    (350, L['a'], L['br'], 'red', '⑥ A: CONNECT → stale closure\'s subscribe(A) → SUBSCRIBE /topic/mail.42'),
    (410, L['br'], L['b'], 'green', '⑦ NEW_MAIL → B: incrementUnread()'),
    (445, L['br'], L['a'], 'red', '⑦ NEW_MAIL → A (zombie): incrementUnread()  → +2'),
]
for y, x1, x2, c, lab in steps:
    if x1 == L['a'] and x2 == L['a'] + 120:
        d.arrow([(x1, y - 14), (x2, y - 14), (x2, y + 14), (x1, y + 14)], color=c)
        d.text(x2 + 10, y + 4, lab, size=11, weight=700, color=G[c], anchor='start')
    else:
        d.arrow([(x1, y), (x2, y)], color=c)
        d.text((x1 + x2) / 2 + (6 if lab.startswith('①') else 0), y - 8, lab, size=10 if lab.startswith('①') else 11, weight=700, color=G[c])
d.text(1060, 490, 'Provider mounted in 3 layouts → every section switch adds a permanent zombie', size=11, weight=600, color=MUTED, anchor='end')
d.group(40, 520, 1020, 120, 'StrictMode was innocent (checked in the source)')
d.lines(550, 560, ['React 18.3.1 runs mount → cleanup → mount synchronously inside flushPassiveEffectsImpl — no microtask can slip in between',
                   'stompjs 7.3.0 _connect() rechecks if (!this.active) return after await beforeConnect — a sync deactivate means no socket is opened',
                   '→ StrictMode only causes a duplicate backfill() call. The real duplicate subscription came from the unguarded reconnect in ③→⑤'], size=12, weight=600, gap=22)
d.flow([{'path': [(L['fx'], 150), (L['a'], 150)], 'color': 'gray', 'dur': 0.4},
        {'path': [(L['a'], 185), (L['br'], 185)], 'color': 'gray', 'dur': 0.5},
        {'path': [(L['br'], 220), (L['a'], 220)], 'color': 'gray', 'dur': 0.5},
        {'path': [(L['fx'], 265), (L['b'], 265)], 'color': 'green', 'dur': 0.5},
        {'path': [(L['a'], 296), (L['a'] + 120, 296), (L['a'] + 120, 324), (L['a'], 324)], 'color': 'red', 'dur': 0.6},
        {'path': [(L['a'], 350), (L['br'], 350)], 'color': 'red', 'dur': 0.5},
        {'path': [(L['br'], 410), (L['b'], 410)], 'color': 'green', 'dur': 0.4},
        {'path': [(L['br'], 445), (L['a'], 445)], 'color': 'red', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/07/28-2.svg'))

# =====================================================================
# 2026/07/28-3  unread: server-authoritative
# =====================================================================
d = Diagram(1100, 560, 'The server counts, events only invalidate — countUnreadGroupedByFolder and invalidateQueries')
d.group(40, 96, 200, 180, 'Old model')
d.box(60, 130, 160, 40, 'NEW_MAIL frame', color='muted', label_size=12)
d.arrow([(140, 170), (140, 200)], color='muted', label='+1', label_dy=-2, label_size=11)
d.box(60, 200, 160, 40, 'unreadCount', color='muted', label_size=12)
d.text(140, 262, 'session counter — wrong', size=11, weight=600, color=MUTED)
d.group(290, 96, 360, 400, 'Server')
d.box(310, 130, 320, 70, 'mail_message ⟕ mail_message_flag', ['owner · ACTIVE · INBOUND · NOT EXISTS(isRead=true)'], color='gray', label_size=13, sub_size=11)
d.box(310, 230, 320, 56, 'countUnreadGroupedByFolder(owner)', ['GROUP BY folderId → Map<folderId, count>'], color='green', label_size=13, sub_size=11)
d.box(310, 316, 320, 56, 'GET /folders', ['MailFolderResponse.unreadCount'], color='green', label_size=13, sub_size=11)
d.box(310, 402, 320, 56, 'STOMP /topic/mail.{user}', ['NEW_MAIL · MAIL_STATE_CHANGED'], color='blue', label_size=13, sub_size=11)
d.arrow([(470, 200), (470, 230)], color='gray'); d.arrow([(470, 286), (470, 316)], color='green')
d.group(700, 96, 360, 400, 'Browser')
d.box(720, 130, 320, 56, 'useFolders() (react-query)', ['shows folder.unreadCount as is'], color='green', label_size=13, sub_size=11)
d.box(720, 216, 320, 56, 'UnreadBadge', ['every folder, hidden at 0, 99+'], color='green', label_size=13, sub_size=11)
d.box(720, 316, 320, 56, 'invalidateQueries(folderKeys.all)', ['on NEW_MAIL · state change · mark-read success'], color='amber', label_size=13, sub_size=11)
d.box(720, 402, 320, 56, 'useMailRealtime', ['frames never touch the number'], color='blue', label_size=13, sub_size=11)
d.arrow([(630, 344), (680, 344), (680, 158), (720, 158)], color='green', label='refetch', label_dy=-8, label_size=11)
d.arrow([(880, 186), (880, 216)], color='green')
d.arrow([(630, 430), (720, 430)], color='blue')
d.arrow([(880, 402), (880, 372)], color='amber')
d.arrow([(720, 344), (690, 344), (690, 300), (660, 300), (660, 344), (630, 344)], color='amber', head=False, width=1, dashed=True)
d.text(550, 520, 'The first fetch sets the value, reads on other devices show up at the next invalidation, and duplicate frames (even zombies) can\'t skew it', size=12, weight=700, color=G['green'])
d.text(550, 544, 'Gotcha: /folders uses the shared ListResponse wrapper, so the SpringDoc spec hides the field — unreadCount was added to the hand-written type', size=11, weight=600, color=MUTED)
d.flow([{'path': [(630, 430), (720, 430)], 'color': 'blue', 'dur': 0.5},
        {'path': [(880, 402), (880, 372)], 'color': 'amber', 'dur': 0.3},
        {'path': [(720, 344), (690, 344), (690, 300), (660, 300), (660, 344), (630, 344)], 'color': 'amber', 'dur': 0.6},
        {'path': [(470, 200), (470, 230)], 'color': 'gray', 'dur': 0.3},
        {'path': [(470, 286), (470, 316)], 'color': 'green', 'dur': 0.3},
        {'path': [(630, 344), (680, 344), (680, 158), (720, 158)], 'color': 'green', 'dur': 0.8},
        {'path': [(880, 186), (880, 216)], 'color': 'green', 'dur': 0.3, 'hold': 0.8}])
d.save(out('2026/07/28-3.svg'))

# =====================================================================
# 2026/10/04-1  basepath: four stages
# =====================================================================
d = Diagram(1100, 600, 'Four zero-downtime stages — when each one finishes, the old and the new address both work')
cols4 = [(275, '① App deploy', ['basePath + redirects(basePath:false)']), (505, '② Caddy', ['path /svc /svc/* → container', '(prefix kept)']), (735, '③ Switch links', ['add to PATH_HOSTED_SERVICES']), (965, '④ Clean up', ['remove the old host block'])]
for x, label, sub in cols4:
    d.box(x - 105, 90, 210, 56, label, sub, color='gray', label_size=14, sub_size=10)
d.text(40, 200, 'Old URL', size=13, weight=700, anchor='start'); d.text(40, 218, 'svc.example.com', size=10, color=MUTED, anchor='start', mono=True)
d.text(40, 330, 'New URL', size=13, weight=700, anchor='start'); d.text(40, 348, 'example.com/svc', size=10, color=MUTED, anchor='start', mono=True)
old = [('/x → 307 → /svc/x', 'works', 'amber'), ('unchanged', 'works', 'amber'), ('no longer linked', 'still responds', 'amber'), ('host removed', '(gone)', 'muted')]
new = [('no Caddy handle yet', '→ portal 404 / login', 'red'), ('handle @svc → container', 'works', 'green'), ('every link points here', 'works', 'green'), ('the only address', 'works', 'green')]
for i, ((a1, a2, c1), (b1, b2, c2)) in enumerate(zip(old, new)):
    x = cols4[i][0]
    d.box(x - 105, 170, 210, 80, a1, [a2], color=c1, label_size=12, sub_size=11, dashed=(c1 == 'muted'))
    d.box(x - 105, 300, 210, 80, b1, [b2], color=c2, label_size=12, sub_size=11)
for i in range(3):
    x = cols4[i][0] + 105
    d.arrow([(x, 210), (x + 20, 210)], color='muted'); d.arrow([(x, 340), (x + 20, 340)], color='muted')
d.box(40, 420, 1020, 50, color='muted')
d.text(550, 440, 'Who ships what:  ① app image   ② Caddy reload   ③ shared package → app image   ④ Caddy reload (+ DNS)', size=12, weight=600)
d.text(550, 460, 'No two stages have to happen at the same moment — the service stays up in the minutes between them', size=12, weight=600, color=MUTED)
d.note(40, 486, 1020, 90, ['Actual order: 10-02 night admin ① → 10-03 small hours admin + ops ③ → other 4 ① (push apps in one PR) → morning all 6 ③ → afternoon ④ (dev, prd)',
                           'Prerequisite: add the portal host to the messenger/mail backend CORS allowed origins (WebSocket handshake 403 → 101)',
                           'Bonus: the new address is derived from the request Host, not env vars — dev, prd and local run the same code'], color='green', size=12)
d.flow([{'path': [(170, 160), (380, 160)], 'color': 'blue', 'dur': 0.8, 'hold': 0.3}, {'path': [(400, 160), (610, 160)], 'color': 'blue', 'dur': 0.8, 'hold': 0.3},
        {'path': [(630, 160), (840, 160)], 'color': 'blue', 'dur': 0.8, 'hold': 0.3}, {'path': [(860, 160), (1070, 160)], 'color': 'blue', 'dur': 0.8, 'hold': 0.8}])
d.save(out('2026/10/04-1.svg'))

# =====================================================================
# 2026/10/04-2  basepath: where the prefix comes from
# =====================================================================
d = Diagram(1100, 640, 'Where the prefix comes from — what Next adds, what we have to add, what middleware strips')
d.group(40, 86, 300, 420, 'Browser (basePath: "/svc")')
em = [('<Link href="/x">', 'green', '✓ Next'), ('router.push("/x")', 'green', '✓ Next'), ('fetch("/api/x")', 'red', '✗ → global patch'), ('<img src="/logo.png">', 'red', '✗ → withBasePath()'), ('window.location = "/login"', 'red', '✗ → withBasePath()')]
for i, (lab, c, note) in enumerate(em):
    y = 120 + i * 72
    d.box(60, y, 260, 54, color=c); d.text(190, y + 22, lab, size=12, weight=700, mono=True); d.text(190, y + 42, note, size=11, weight=600, color=G[c])
d.box(400, 264, 200, 54, 'installBasePathFetch()', ['instrumentation-client.ts'], color='amber', label_size=12, sub_size=10)
d.box(400, 336, 200, 54, 'withBasePath()', ['"/…" only; skips //host, https:'], color='amber', label_size=12, sub_size=10)
d.arrow([(320, 291), (400, 291)], color='red'); d.arrow([(320, 363), (400, 363)], color='red'); d.arrow([(320, 435), (380, 435), (380, 376), (400, 376)], color='red')
d.box(680, 200, 160, 220, 'Caddy', ['path /svc /svc/*', 'prefix kept (handle)', '', 'else → portal'], color='gray', label_size=14, sub_size=11)
for y in (147, 219): d.arrow([(320, y), (680, y + 100)], color='green')
d.arrow([(600, 291), (680, 300)], color='amber'); d.arrow([(600, 363), (680, 340)], color='amber')
d.text(500, 170, '/svc/x', size=12, weight=700, color=G['green'], mono=True)
d.text(640, 283, '/svc/api/x', size=11, weight=700, color=G['amber'], mono=True)
d.group(900, 160, 160, 300, 'Next server', color='blue'); d.text(980, 206, 'basePath: "/svc"', size=11, weight=600, color=MUTED, mono=True)
d.box(915, 230, 130, 210, color='purple', dashed=True)
d.lines(980, 258, ['middleware', 'nextUrl.pathname', '= "/x"', '(prefix stripped)', '', 'for absolute URLs,', 'add back', 'nextUrl.basePath'], size=11, weight=600, gap=20)
d.arrow([(840, 310), (900, 310)], color='gray')
d.box(400, 460, 660, 60, color='red'); d.text(730, 484, 'Redirects hide misses: on the old subdomain, an unprefixed /api/x 307s to /svc/api/x and works', size=12, weight=700, color=G['red']); d.text(730, 506, 'On the portal host the same request hits the portal and 404s — and Jest runs without basePath', size=12, weight=600)
d.box(40, 540, 1020, 70, color='green'); d.text(550, 566, 'Check: behind a proxy that passes only /svc/* and 404s the rest, click through every screen in Chrome — zero 404s in the proxy log', size=12, weight=700, color=G['green']); d.text(550, 592, 'Regression guard: a test that greps for unprefixed "/…" literals in src= · window.open · <a href> · XHR', size=12, weight=600, color=MUTED)
d.flow([{'path': [(320, 147), (680, 247)], 'color': 'green', 'dur': 0.7},
        {'path': [(320, 291), (400, 291)], 'color': 'red', 'dur': 0.3}, {'path': [(600, 291), (680, 300)], 'color': 'amber', 'dur': 0.3},
        {'path': [(320, 435), (380, 435), (380, 376), (400, 376)], 'color': 'red', 'dur': 0.4}, {'path': [(600, 363), (680, 340)], 'color': 'amber', 'dur': 0.3},
        {'path': [(840, 310), (900, 310)], 'color': 'gray', 'dur': 0.3, 'hold': 0.8}])
d.save(out('2026/10/04-2.svg'))

# =====================================================================
# 2026/10/04-3  basepath: service worker token churn
# =====================================================================
d = Diagram(1100, 620, 'Four service workers on one origin — they keep overwriting the same appId token record')
d.group(40, 86, 1020, 240, 'Before: each app registers /<svc>/firebase-messaging-sw.js (scope /<svc>/)')
for i, s in enumerate(('svc-a', 'messenger', 'mail', 'svc-b')):
    x = 60 + i * 180
    d.box(x, 120, 160, 60, f'SW scope /{s}/', ['PushSubscription', f'endpoint #{i + 1}'], color='blue', label_size=12, sub_size=10)
    d.arrow([(x + 80, 180), (x + 80, 220), (880, 220), (880, 240)], color='blue' if i == 3 else 'muted', head=(i == 3), width=1)
d.box(780, 240, 260, 70, 'IndexedDB token record', ['key = appId (one per origin)', 'endpoint #4 ≠ stored #3 → delete, reissue'], color='red', label_size=12, sub_size=10)
d.note(60, 236, 680, 78, ['getToken(): if endpoint/auth/p256dh differ from the stored record → requestDeleteToken, then a new token.',
                          'Every app switch deletes the previous app\'s token on the server', '→ only the app opened last receives push.'], color='red', size=12)
d.group(40, 350, 1020, 250, 'After (#1635): one root service worker served by the portal (scope /)')
d.box(60, 384, 260, 60, 'SW scope /', ['/firebase-messaging-sw.js (portal)', 'one PushSubscription'], color='green', label_size=13, sub_size=10)
d.box(380, 384, 260, 60, 'IndexedDB token record', ['key = appId, one registration → stable'], color='green', label_size=13, sub_size=10)
d.arrow([(320, 414), (380, 414)], color='green')
d.box(700, 384, 340, 60, 'notificationclick', ['routes to /<svc>/… by payload.data.service'], color='amber', label_size=13, sub_size=10)
for i, s in enumerate(('svc-a', 'messenger', 'mail', 'svc-b')):
    x = 60 + i * 250
    d.box(x, 470, 220, 52, f'/{s}', ['serviceWorkerPath()', '→ root on the portal host'], color='blue', label_size=12, sub_size=10)
    d.arrow([(x + 110, 470), (x + 110, 456), (190, 456), (190, 444)], color='muted', head=False, width=1)
d.arrow([(870, 444), (870, 470)], color='amber', head=False, width=1)
d.text(550, 548, 'One source file in a shared package, synced to each app\'s public/. unregisterStale() removes our leftover registrations at other scopes', size=12, weight=600)
d.text(550, 573, 'Service workers don\'t know PATH_HOSTED_SERVICES → the 4 push apps did ① and ③ together in one PR', size=12, weight=700, color=G['amber'])
d.flow([{'path': [(140, 180), (140, 220), (880, 220), (880, 240)], 'color': 'blue', 'dur': 1.0, 'hold': 0.3},
        {'path': [(680, 180), (680, 220), (880, 220), (880, 240)], 'color': 'red', 'dur': 0.7, 'hold': 0.8},
        {'path': [(320, 414), (380, 414)], 'color': 'green', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2026/10/04-3.svg'))

# =====================================================================
# 2026/10/20-1  next start: two pipes
# =====================================================================
d = Diagram(1100, 640, 'next build sends config two ways — baked into manifests, or re-read by next start at runtime')
d.box(40, 120, 170, 70, 'next.config.ts', ['basePath, images,', 'redirects(), env …'], color='gray', label_size=14, sub_size=11)
d.box(270, 120, 150, 70, 'next build', color='blue', label_size=15)
d.arrow([(210, 155), (270, 155)], color='gray')
d.box(480, 96, 260, 110, '.next/routes-manifest.json', ['redirects · headers · rewrites', 'basePath (a copy; not used for routing)'], color='green', label_size=12, sub_size=11)
d.box(480, 220, 260, 56, 'middleware-manifest · bundles', ['matcher · env (inlined by DefinePlugin)'], color='green', label_size=12, sub_size=11)
d.box(480, 290, 260, 70, 'required-server-files.json', ['whole config serialized —', 'next start reads one experimental flag'], color='muted', label_size=12, sub_size=11)
d.arrow([(420, 140), (480, 150)], color='green'); d.arrow([(420, 160), (480, 248)], color='green'); d.arrow([(420, 180), (480, 325)], color='muted')
d.group(800, 86, 260, 290, 'Container: next start')
d.box(820, 120, 220, 50, 'routes-manifest ✓', ['always there → redirects work'], color='green', label_size=12, sub_size=10)
d.box(820, 186, 220, 50, 'next.config.* (cwd)', ['missing → defaults, no warning'], color='red', dashed=True, label_size=12, sub_size=10)
d.box(820, 252, 220, 36, 'basePath = ""', color='red', label_size=12)
d.box(820, 298, 220, 36, 'images.remotePatterns = []', color='red', label_size=12)
d.box(820, 344, 220, 24, color='muted'); d.text(930, 360, 'loadConfig: findUp → defaults', size=10, weight=600, color=MUTED, mono=True)
d.arrow([(740, 150), (820, 145)], color='green'); d.arrow([(740, 210), (820, 210)], color='red', dashed=True)
d.box(40, 400, 500, 90, '① 08-27  images 400', ['remotePatterns default → /_next/image rejects external URLs', 'the config was in required-server-files, but isn\'t read from there'], color='red', label_size=13, sub_size=11)
d.box(560, 400, 500, 90, '② 10-02  every /admin/* 404', ['redirects (manifest) live: /health → 307 → /admin/health', 'basePath (config) gone → 404. Half-working: only redirects run'], color='red', label_size=13, sub_size=11)
d.box(40, 510, 1020, 100, color='purple')
d.text(550, 536, 'Postscript (11-04): output: "standalone" — the config is serialized into server.js and passed as __NEXT_PRIVATE_STANDALONE_CONFIG', size=13, weight=700, color=G['purple'])
d.text(550, 560, 'loadConfig() uses that value without looking for a file → no config file, no pnpm, no TypeScript at runtime', size=12, weight=600)
d.text(550, 584, 'Image size 1–1.6 GB → about 300 MB (339 / 312 / 310 MB, measured locally)', size=12, weight=600, color=MUTED)
d.flow([{'path': [(210, 155), (270, 155)], 'color': 'gray', 'dur': 0.4},
        {'path': [(420, 140), (480, 150)], 'color': 'green', 'dur': 0.4}, {'path': [(740, 150), (820, 145)], 'color': 'green', 'dur': 0.5},
        {'path': [(420, 180), (480, 325)], 'color': 'muted', 'dur': 0.5, 'hold': 0.4},
        {'path': [(740, 210), (820, 210)], 'color': 'red', 'dur': 0.5, 'hold': 1.0}])
d.save(out('2026/10/20-1.svg'))

# =====================================================================
# 2026/10/20-2  next start: root built it, node runs it
# =====================================================================
d = Diagram(1100, 640, 'Root builds, node runs — the $HOME cache and directory ownership don\'t cross the USER boundary')
d.group(40, 86, 500, 290, '③-1  corepack cache miss → startup hangs')
d.box(60, 120, 220, 56, 'RUN pnpm install --prod', ['runs as root'], color='gray', label_size=12, sub_size=11)
d.box(300, 120, 220, 56, '/root/.cache/node/corepack', ['pnpm@9.15.9 stored here'], color='gray', label_size=11, sub_size=11)
d.arrow([(280, 148), (300, 148)], color='gray')
d.arrow([(60, 196), (520, 196)], color='red', head=False, dashed=True); d.text(290, 190, 'USER node', size=11, weight=700, color=G['red'])
d.box(60, 214, 220, 56, 'CMD pnpm … start', ['runs as node'], color='blue', label_size=12, sub_size=11)
d.box(300, 214, 220, 56, '/home/node/.cache/…', ['empty → goes to the network'], color='red', label_size=11, sub_size=11)
d.arrow([(280, 242), (300, 242)], color='blue')
d.box(300, 290, 220, 50, 'registry.npmjs.org  ✕', ['blocked on the dev host → waits forever'], color='red', dashed=True, label_size=12, sub_size=10)
d.arrow([(410, 270), (410, 290)], color='red')
d.text(170, 320, '"! Corepack is about to download …"', size=10, weight=600, color=MUTED, mono=True)
d.text(170, 340, 'never reaches next start', size=11, weight=700, color=G['red'])
d.group(580, 86, 480, 290, '③-2  root-owned cwd → every BFF returns HTML 500')
d.box(600, 120, 200, 56, 'COPY apps/<app>/', ['owned by root'], color='gray', label_size=12, sub_size=11)
d.box(840, 120, 200, 56, 'chown .next only', ['(#1931)'], color='amber', label_size=12, sub_size=11)
d.arrow([(600, 196), (1040, 196)], color='red', head=False, dashed=True); d.text(820, 190, 'USER node', size=11, weight=700, color=G['red'])
d.box(600, 214, 200, 56, 'utils/logger.ts', ['mkdir <cwd>/log at module load'], color='blue', label_size=12, sub_size=11)
d.box(840, 214, 200, 56, 'EACCES', ['route module fails to load'], color='red', label_size=12, sub_size=11)
d.arrow([(800, 242), (840, 242)], color='red')
d.box(600, 290, 200, 50, '/api/** → HTML 500', ['not handler JSON = module not loaded'], color='red', label_size=12, sub_size=10)
d.box(840, 290, 200, 50, '/health → 200', ['a page that skips the logger'], color='green', label_size=12, sub_size=10)
d.arrow([(940, 270), (940, 290)], color='green', head=False, width=1); d.arrow([(700, 270), (700, 290)], color='red')
d.box(40, 400, 500, 100, 'Fix (#1935)', ['ENV COREPACK_HOME=/opt/corepack   — shared path outside root\'s home', 'ENV COREPACK_ENABLE_NETWORK=0     — a cache miss fails fast, no hang', 'reproduced with a minimal node:20-slim + packageManager image'], color='green', label_size=13, sub_size=11)
d.box(580, 400, 480, 100, 'Fix (#1939)', ['RUN mkdir -p apps/<app>/log && chown -R node:node .next log', 'health check should hit real deps (logger, BFF) — not done yet'], color='green', label_size=13, sub_size=11)
d.box(40, 520, 1020, 96, color='muted')
d.text(550, 540, 'Non-root checklist', size=13, weight=700)
d.text(550, 561, '① caches tied to $HOME (corepack · npm · pnpm store): move them to a shared path, or don\'t use them at runtime', size=11, weight=600)
d.text(550, 580, '② writable dirs under cwd (.next/cache · log · temp): create them in advance and hand over ownership', size=11, weight=600)
d.text(550, 599, '③ none of the three incidents reproduced locally — pull the image from the registry and run it', size=11, weight=600, color=MUTED)
d.flow([{'path': [(280, 148), (300, 148)], 'color': 'gray', 'dur': 0.3},
        {'path': [(280, 242), (300, 242)], 'color': 'blue', 'dur': 0.3},
        {'path': [(410, 270), (410, 290)], 'color': 'red', 'dur': 0.4, 'hold': 0.8},
        {'path': [(800, 242), (840, 242)], 'color': 'red', 'dur': 0.3},
        {'path': [(700, 270), (700, 290)], 'color': 'red', 'dur': 0.3, 'hold': 0.8}])
d.save(out('2026/10/20-2.svg'))

print('ok')
