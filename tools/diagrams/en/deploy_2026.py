"""English edition of tools/diagrams/make_diagrams_batch4.py (2026/11 posts: deploy time, env bundles, call audio).
Run: python3 tools/diagrams/en/deploy_2026.py "$PWD"
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from diag import Diagram, INK, MUTED, PAL

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img/en', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

RED, GREEN, BLUE, AMBER = PAL['red'][0], PAL['green'][0], PAL['blue'][0], PAL['amber'][0]

# =====================================================================
# 2026/11/09-1  deploy-time: one enum change → all 10 services
# =====================================================================
d = Diagram(1100, 560, 'One new response code for an approval feature changed core — and all 10 services redeployed')
d.box(40, 230, 220, 90, 'Commit', ['New approval feature', '+ 1 response code'], color='blue')
d.box(330, 215, 250, 120, 'core module', ['ExceptionCode.kt · SuccessCode.kt', '1,350 response codes', 'every service depends on it'], color='red')
names = ['account', 'approval', 'sales', 'chat', 'mail', 'batch', 'mcp', 'etc', 'notification', 'site']
for i, n in enumerate(names):
    y = 100 + i * 38
    col = 'green' if n == 'approval' else 'amber'
    d.box(700, y, 170, 30, f'{n}-api', color=col, label_size=13)
    d.arrow([(580, 275), (640, 275), (640, y + 15), (700, y + 15)], color='muted', width=1.2)
d.arrow([(260, 275), (330, 275)], color='blue')
d.text(990, 175, 'Services changed', size=13, color=GREEN)
d.text(990, 195, '1', size=22, weight=800, color=GREEN)
d.text(990, 300, 'Services redeployed', size=13, color=RED)
d.text(990, 320, '10', size=22, weight=800, color=RED)
d.text(990, 345, '≈ 5.9 + 3.45 × 10 = 40 min', size=12, color=MUTED)
d.note(40, 490, 1020, 46, '44 of 73 runs (60%) deployed all 10 — top cause: these two enums; second: pipeline file changes (13 runs)', color='muted', size=14)
stages = [{'path': [(260, 275), (330, 275)], 'color': 'blue', 'dur': 0.5}]
d.flow(stages + [{'path': [(580, 275), (640, 275), (640, 100 + i * 38 + 15), (700, 100 + i * 38 + 15)],
                  'color': 'red', 'dur': 0.18, 'hold': 0.02} for i in range(10)] + [{'path': [(870, 300), (930, 310)], 'color': 'red', 'dur': 0.3, 'hold': 0.8}])
d.save(out('2026/11/09-1.svg'))

# =====================================================================
# 2026/11/09-2  deploy-time: docker layers chown -R vs COPY --chown
# =====================================================================
d = Diagram(1100, 520, 'chown -R after COPY rewrites every copied file into a new layer — a code-only change pushes 145MB')
d.group(40, 90, 490, 330, 'Before — RUN chown -R app:app /app')
d.box(70, 330, 430, 60, 'dependencies 130.5MB', ['cached if unchanged ✓'], color='muted')
d.box(70, 260, 430, 60, 'application 14.3MB', ['rebuilt when code changes'], color='amber')
d.box(70, 130, 430, 120, 'chown layer 144.9MB', ['rewrites deps + app wholesale just to change the owner', '→ new layer every build → pushed every time', 'median push per service 55s (max 117s)'], color='red')
d.group(570, 90, 490, 330, 'After — COPY --chown=app:app')
d.box(600, 330, 430, 60, 'dependencies 130.5MB', ['copied with owner set · cached if unchanged ✓'], color='green')
d.box(600, 260, 430, 60, 'application 14.3MB', ['the only layer pushed when code changes'], color='amber')
d.box(600, 130, 430, 120, 'no chown layer', ['create the user first', 'chown only the WORKDIR (empty directory)', 'about 4s push per service'], color='green', dashed=True)
d.note(40, 440, 1020, 50, 'BuildKit cache mode=max → mode=min: exporting the extract stage (different every build, never reused) 60s → 11s', color='muted', size=14)
d.flow([{'path': [(285, 250), (285, 215)], 'color': 'red', 'dur': 0.4},
        {'path': [(285, 130), (285, 100)], 'color': 'red', 'dur': 0.6, 'label': '145MB push', 'label_at': (390, 112)},
        {'path': [(815, 260), (815, 100)], 'color': 'green', 'dur': 0.6, 'hold': 0.8, 'label': '14MB push', 'label_at': (910, 112)}])
d.save(out('2026/11/09-2.svg'))

# =====================================================================
# 2026/11/09-3  deploy-time: serial vs pipelined deploy (gantt)
# =====================================================================
d = Diagram(1100, 560, "Don't wait for every push to finish — deploy each service as soon as its image is ready")
def gantt(y0, title, pipelined):
    d.text(40, y0, title, size=15, weight=800, anchor='start')
    builds = [(0, 120), (0, 160), (0, 200), (0, 240)]
    x0, sc = 180, 1.9
    for i, (s, e) in enumerate(builds):
        y = y0 + 25 + i * 34
        d.text(170, y + 12, f'Service {chr(65 + i)}', size=12, color=MUTED, anchor='end')
        d.box(x0 + s * sc, y, (e - s) * sc, 24, 'build · push', color='blue', label_size=11)
    for i, (s, e) in enumerate(builds):
        y = y0 + 25 + i * 34
        start = e if pipelined else 240 + i * 45
        d.box(x0 + start * sc, y, 45 * sc, 24, 'Kamal', color='green', label_size=11)
    end = (240 + 45) if pipelined else (240 + 4 * 45)
    d.arrow([(x0 + end * sc, y0 + 20), (x0 + end * sc, y0 + 165)], color='red' if not pipelined else 'green', head=False, dashed=True)
    d.text(x0 + end * sc + 8, y0 + 12, 'done', size=12, color=RED if not pipelined else GREEN, anchor='start')
    return x0, sc
gantt(95, 'Before — the deploy job runs serially after every publish job is done', False)
gantt(300, 'After — each publish job deploys right after its push (a server flock queues them)', True)
d.note(40, 500, 1020, 44, 'Kamal takes 30–37s per service — with 10 services, the serial wait alone was about 6.5 min', color='muted', size=14)
d.flow([{'path': [(180 + 120 * 1.9, 337), (180 + 165 * 1.9, 337)], 'color': 'green', 'dur': 0.5},
        {'path': [(180 + 160 * 1.9, 371), (180 + 205 * 1.9, 371)], 'color': 'green', 'dur': 0.5},
        {'path': [(180 + 200 * 1.9, 405), (180 + 245 * 1.9, 405)], 'color': 'green', 'dur': 0.5},
        {'path': [(180 + 240 * 1.9, 439), (180 + 285 * 1.9, 439)], 'color': 'green', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/11/09-3.svg'))

# =====================================================================
# 2026/11/09-4  deploy-time: path classification → full / canary / selected
# =====================================================================
d = Diagram(1100, 560, 'Changed paths are sorted into shared · pipeline · service → full, canary or selective deploy')
d.box(40, 230, 200, 100, 'git diff', ['last successful push run', '..this commit'], color='blue')
d.box(310, 230, 200, 100, 'Classify paths', ['paths-filter', 'per-service path lists'], color='purple')
d.box(600, 100, 230, 90, 'Any shared path', ['core/src/main · build.gradle', 'backend/docker'], color='red')
d.box(600, 235, 230, 90, 'Service paths only', ['account-api/** · role/src/main/**', 'deploy.account-backend*.yml'], color='green')
d.box(600, 370, 230, 90, 'Pipeline only', ['workflows · kamal-deploy action'], color='amber')
d.box(890, 100, 170, 90, 'All 10', color='red')
d.box(890, 235, 170, 90, 'Changed services', color='green')
d.box(890, 370, 170, 90, 'One canary', ['etc-api'], color='amber')
d.arrow([(240, 280), (310, 280)], color='blue')
for y in (145, 280, 415):
    d.arrow([(510, 280), (555, 280), (555, y), (600, y)], color='muted', width=1.5)
    d.arrow([(830, y), (890, y)], color='gray')
d.note(40, 490, 1020, 50, ["Commits that only touch core tests don't deploy · manual partial runs aren't used as the baseline",
                           'workflow_dispatch(modules) can always deploy everything'], color='muted', size=13)
d.flow([{'path': [(240, 280), (310, 280)], 'color': 'blue', 'dur': 0.4},
        {'path': [(510, 280), (555, 280), (600, 280)], 'color': 'green', 'dur': 0.4},
        {'path': [(830, 280), (890, 280)], 'color': 'green', 'dur': 0.3, 'hold': 0.5},
        {'path': [(240, 280), (310, 280)], 'color': 'blue', 'dur': 0.4},
        {'path': [(510, 280), (555, 280), (555, 415), (600, 415)], 'color': 'amber', 'dur': 0.5},
        {'path': [(830, 415), (890, 415)], 'color': 'amber', 'dur': 0.3, 'hold': 0.8}])
d.save(out('2026/11/09-4.svg'))

# =====================================================================
# 2026/11/09-5  deploy-time: ui (11 apps) vs records (3 apps)
# =====================================================================
d = Diagram(1100, 540, 'Shared ui has 11 consumer apps, the split-out records only 3 — package boundaries set build scope')
apps = ['Sales', 'Approval', 'Messenger', 'Mail', 'Admin', 'Ops', 'Portal', 'Guide', 'Site A', 'Site B', 'Site C']
d.group(40, 85, 500, 380, 'Before — record UI lives inside @my/ui')
d.box(190, 115, 200, 60, '@my/ui', ['+ record-sharing UI'], color='red')
d.group(55, 215, 470, 205, 'The 11 apps that use @my/ui — all checked and deployed')
for i, a in enumerate(apps):
    x = 70 + (i % 4) * 113; y = 240 + (i // 4) * 58
    d.box(x, y, 100, 42, a, color='amber', label_size=13)
d.arrow([(290, 175), (290, 215)], color='red')
d.text(290, 445, 'One-line record UI fix → 11 apps checked and deployed', size=13, color=RED)
d.group(560, 85, 500, 380, 'After — split out into @my/records')
d.box(600, 110, 180, 60, '@my/ui', ['used by 11'], color='muted')
d.box(840, 110, 180, 60, '@my/records', ['records → ui, one way'], color='green')
for i, a in enumerate(['Sales', 'Approval', 'Messenger']):
    x = 760 + i * 100; y = 260
    d.box(x, y, 90, 44, a, color='green', label_size=13)
    d.arrow([(930, 170), (930, 215), (x + 45, 215), (x + 45, y)], color='green', width=1.5)
d.arrow([(840, 140), (780, 140)], color='muted', dashed=True)
d.text(810, 445, 'Record UI fix → only 3 apps', size=13, color=GREEN)
d.text(810, 360, 'A test fails if ui re-exports records', size=12, color=MUTED)
d.note(40, 480, 1020, 44, 'Impact = changed packages + transitive consumers in the package.json / pub deps graph (old and new graph)', color='muted', size=13)
d.flow([{'path': [(290, 175), (290, 215)], 'color': 'red', 'dur': 0.5, 'hold': 0.4},
        {'path': [(930, 170), (930, 215), (805, 215), (805, 260)], 'color': 'green', 'dur': 0.5},
        {'path': [(930, 170), (930, 215), (1005, 215), (1005, 260)], 'color': 'green', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/11/09-5.svg'))

# =====================================================================
# 2026/11/10-1  env: before / after source of truth
# =====================================================================
d = Diagram(1100, 580, 'One source of truth in GitHub Environments — the deploy job rewrites the server file, Kamal reads it')
d.group(40, 85, 1020, 135, 'Before')
d.box(70, 120, 180, 76, 'Person', ['SSH into server → vi'], color='amber')
d.box(330, 120, 240, 76, 'server ~/app/env/*', ['which copy is the source?', 'local copy 9 keys · server 43'], color='red')
d.box(650, 120, 170, 76, 'kamal deploy', ['reads env-file'], color='gray')
d.box(880, 120, 150, 76, 'Container', color='gray')
d.arrow([(250, 158), (330, 158)], color='amber'); d.arrow([(570, 158), (650, 158)], color='gray'); d.arrow([(820, 158), (880, 158)], color='gray')
d.text(735, 207, 'Forget to redeploy and nothing changes', size=12, color=RED)
d.group(40, 250, 1020, 250, 'After')
d.box(70, 290, 200, 90, 'GitHub Environment', ['development / production', 'bundle Secrets (BACKEND_ENV…)'], color='blue')
d.box(330, 290, 200, 90, 'Deploy job', ['validate · mask', 'dev / main branches only'], color='purple')
d.box(590, 290, 200, 90, 'server ~/.app-env/*', ['700 / 600 · atomic replace'], color='green')
d.box(850, 290, 180, 90, 'kamal deploy', ['env-file → container'], color='green')
d.arrow([(270, 335), (330, 335)], color='blue'); d.arrow([(530, 335), (590, 335)], color='purple', label='SSH stdin', label_size=11)
d.arrow([(790, 335), (850, 335)], color='green')
d.box(70, 410, 200, 64, 'Person', ['edits the Secret in GitHub'], color='amber')
d.arrow([(170, 410), (170, 380)], color='amber')
d.box(330, 410, 700, 64, color='muted')
d.text(680, 432, 'Next.js also needs env at build time → BuildKit secret mount, build stage only', size=13, weight=700)
d.text(680, 455, "never in image layers · no-cache-filters: builder (secrets aren't part of the cache key)", size=12, weight=600, color=MUTED)
d.note(40, 515, 1020, 44, 'Splitting dev and prd onto two servers only means changing the Environment Variable KAMAL_HOST', color='muted', size=14)
d.flow([{'path': [(170, 410), (170, 380)], 'color': 'amber', 'dur': 0.3},
        {'path': [(270, 335), (330, 335)], 'color': 'blue', 'dur': 0.4},
        {'path': [(530, 335), (590, 335)], 'color': 'purple', 'dur': 0.4},
        {'path': [(790, 335), (850, 335)], 'color': 'green', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2026/11/10-1.svg'))

# =====================================================================
# 2026/11/10-2  env: sync pipeline detail
# =====================================================================
d = Diagram(1100, 600, 'The bundle never shows up in argv or logs — it reaches the server only through SSH stdin')
d.group(40, 90, 560, 400, 'GitHub Actions runner')
d.box(70, 125, 240, 64, '① take the flock', ['per server · waits up to 30 min'], color='gray')
d.box(70, 210, 240, 64, '② write SSH config', ['umask 077 temp dir · trap cleanup'], color='gray')
d.box(70, 295, 240, 80, '③ sync.py', ['parse · validate the bundle', 'every value → ::add-mask::'], color='purple')
d.box(340, 295, 230, 80, '④ ssh … python3 -', ['remote script (base64)', '+ bundle JSON → stdin'], color='blue')
d.box(70, 400, 500, 64, '⑥ kamal deploy', ['env -u BUNDLE … — child processes get no bundle variables'], color='green')
d.group(660, 90, 400, 400, 'Server')
d.box(690, 295, 340, 80, '⑤ remote_sync.py', ['~/.app-env/ (deploy 700, files 600)', 'rejects symlinks · temp file → os.replace'], color='green')
d.box(690, 400, 340, 64, 'kamal-proxy · new container', ['reads env-file → health check → switch'], color='green')
d.box(690, 125, 340, 140, color='red')
d.text(860, 150, 'What ends up in the logs', size=14, weight=800, color=RED)
d.lines(860, 180, ['line 51: duplicate variable name …', 'category=SSH_HOST_KEY_UNKNOWN', 'Environment sync failed: LEGACY_…', 'values · raw commands · SSH output dropped'], size=12, mono=False)
d.arrow([(190, 189), (190, 210)], color='gray'); d.arrow([(190, 274), (190, 295)], color='gray')
d.arrow([(310, 335), (340, 335)], color='purple')
d.arrow([(570, 335), (690, 335)], color='blue', label='stdin', label_size=12)
d.arrow([(860, 375), (860, 400)], color='green')
d.arrow([(570, 432), (690, 432)], color='green')
d.note(40, 510, 1020, 64, ['The server script reports why only through its exit code: 40 SYMLINK_REJECTED · 44 LEGACY_FILE_MISSING ·',
                           '46 LEGACY_KEY_MISSING_FROM_BUNDLE · 47 LEGACY_VALUE_MISMATCH · 48 REMOTE_PERMISSION_DENIED …'], color='muted', size=13)
d.flow([{'path': [(190, 189), (190, 210)], 'color': 'gray', 'dur': 0.3},
        {'path': [(190, 274), (190, 295)], 'color': 'gray', 'dur': 0.3},
        {'path': [(310, 335), (340, 335)], 'color': 'purple', 'dur': 0.3},
        {'path': [(570, 335), (690, 335)], 'color': 'blue', 'dur': 0.6},
        {'path': [(570, 432), (690, 432)], 'color': 'green', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/11/10-2.svg'))

# =====================================================================
# 2026/11/10-3  env: first cutover decision
# =====================================================================
d = Diagram(1100, 600, 'First cutover only: if the old server file differs, stop before swapping containers — a human decides')
d.box(40, 250, 180, 80, 'Bundle validated', color='blue')
d.box(280, 100, 220, 70, 'New-path file exists', ['→ the bundle is the source'], color='green')
d.box(280, 200, 220, 70, 'Neither (new server)', ['→ create from the bundle'], color='green')
d.box(280, 330, 220, 70, 'Only the old file', ['first cutover'], color='amber')
d.box(840, 110, 220, 150, 'Write the file', ['temp file → os.replace', '→ kamal deploy'], color='green')
d.box(570, 330, 200, 70, 'Compare in memory', ['old keys ⊆ bundle?', 'values equal?'], color='amber')
d.box(570, 450, 200, 90, 'Stop before swap', ['LEGACY_VALUE_MISMATCH', 'image built fine · no impact'], color='red')
d.box(840, 450, 220, 90, 'Manual adopt workflow', ['main · prd · value diffs only', 'stops if a deploy is running'], color='purple')
d.arrow([(220, 290), (250, 290), (250, 135), (280, 135)], color='muted')
d.arrow([(250, 235), (280, 235)], color='muted')
d.arrow([(250, 290), (250, 365), (280, 365)], color='muted')
d.arrow([(500, 135), (840, 135)], color='green')
d.arrow([(500, 235), (840, 235)], color='green')
d.arrow([(500, 365), (570, 365)], color='amber')
d.arrow([(770, 365), (950, 365), (950, 260)], color='green', label='equal', label_size=12, label_dy=-12)
d.arrow([(670, 400), (670, 450)], color='red')
d.text(682, 425, 'differs · key missing', size=12, color=RED, anchor='start')
d.arrow([(770, 495), (840, 495)], color='red')
d.arrow([(1040, 450), (1040, 260)], color='purple', dashed=True)
d.text(1030, 420, 'adopt', size=12, color=PAL['purple'][0], anchor='end')
d.text(550, 565, 'Rule: never delete the old file or loosen validation just to get past the comparison', size=14, weight=800, color=INK, anchor='middle')
d.text(550, 588, 'A human decides which side is right, registers the correct values as the Secret, then adopts', size=13, weight=600, color=MUTED, anchor='middle')
d.flow([{'path': [(220, 290), (250, 290), (250, 365), (280, 365)], 'color': 'amber', 'dur': 0.4},
        {'path': [(500, 365), (570, 365)], 'color': 'amber', 'dur': 0.3},
        {'path': [(670, 400), (670, 450)], 'color': 'red', 'dur': 0.3},
        {'path': [(770, 495), (840, 495)], 'color': 'red', 'dur': 0.3, 'hold': 0.3},
        {'path': [(1040, 450), (1040, 260)], 'color': 'purple', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/11/10-3.svg'))

# =====================================================================
# 2026/11/10-4  env: SSHKit host key intersection
# =====================================================================
d = Diagram(1100, 520, 'SSHKit wants the key under both hostname and IP — a hostname-only pin counts as "unknown"')
d.group(40, 90, 500, 300, 'Before')
d.box(70, 125, 200, 70, 'known_hosts', ['deploy-host  ssh-ed25519 …'], color='blue')
d.box(310, 125, 200, 70, 'SSHKit lookup', ['"deploy-host,10.x.x.x"'], color='gray')
d.box(70, 230, 200, 70, 'deploy-host keys', ['{ ed25519 }'], color='green')
d.box(310, 230, 200, 70, 'IP keys', ['{ } (not registered)'], color='muted')
d.box(130, 320, 320, 54, 'intersection = ∅ → SSH_HOST_KEY_UNKNOWN', color='red', label_size=13)
d.arrow([(170, 195), (170, 230)], color='blue'); d.arrow([(410, 195), (410, 230)], color='gray')
d.arrow([(170, 300), (250, 320)], color='muted'); d.arrow([(410, 300), (330, 320)], color='muted')
d.group(560, 90, 500, 300, 'After — HostKeyAlias pins the lookup name')
d.box(590, 125, 440, 90, 'KAMAL_SSH_CONFIG', ['Host *  HostKeyAlias deploy-host', 'StrictHostKeyChecking yes · GlobalKnownHostsFile /dev/null'], color='purple')
d.box(590, 245, 200, 60, 'Correct pin', ['passes ✓'], color='green')
d.box(830, 245, 200, 60, 'Different key', ['MISMATCH ✓'], color='red')
d.box(680, 320, 260, 54, 'Unregistered host → UNKNOWN ✓', color='amber', label_size=12)
d.arrow([(690, 215), (690, 245)], color='green'); d.arrow([(930, 215), (930, 245)], color='red'); d.arrow([(810, 215), (810, 320)], color='amber')
d.note(40, 410, 1020, 80, ["Verification stays on; only the lookup name changed — four cases reproduced offline to confirm it's still strict",
                           'Kamal 2.12 · SSHKit 1.25 · Net::SSH 7.3'], color='muted', size=13)
d.flow([{'path': [(170, 195), (170, 230)], 'color': 'blue', 'dur': 0.3},
        {'path': [(410, 195), (410, 230)], 'color': 'gray', 'dur': 0.3},
        {'path': [(410, 300), (330, 320)], 'color': 'red', 'dur': 0.4, 'hold': 0.4},
        {'path': [(690, 215), (690, 245)], 'color': 'green', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2026/11/10-4.svg'))

# =====================================================================
# 2026/11/11-1  call: three paths, only one registered
# =====================================================================
d = Diagram(1100, 560, 'Only calls registered with the OS survive in the background — of three paths, only VoIP push used CallKit')
d.box(40, 110, 260, 90, 'Incoming, app not running', ['VoIP push → accept on OS call screen'], color='blue')
d.box(40, 250, 260, 90, 'Calls I place', ['CallController.start()'], color='amber')
d.box(40, 390, 260, 90, 'Accepted on in-app screen', ['while the app is in front'], color='amber')
d.box(400, 110, 280, 90, 'Registered as an OS call', ['iOS CallKit · Android Telecom + FGS'], color='green')
d.box(400, 310, 280, 110, 'Not registered', ['a call only the app knows about', 'the OS sees a backgrounded app'], color='red')
d.box(780, 110, 280, 90, 'Even after going home', ['audio stays · Dynamic Island'], color='green')
d.box(780, 310, 280, 110, 'After going home', ['iOS: audio drops · no Island', 'Android 14+: mic drops'], color='red')
d.arrow([(300, 155), (400, 155)], color='green')
d.arrow([(300, 295), (350, 295), (350, 350), (400, 350)], color='red')
d.arrow([(300, 435), (350, 435), (350, 380), (400, 380)], color='red')
d.arrow([(680, 155), (780, 155)], color='green'); d.arrow([(680, 365), (780, 365)], color='red')
d.note(40, 495, 1020, 46, 'Declaring audio · voip in UIBackgroundModes only says "this app may" — you still have to tell the OS a call is live', color='muted', size=13)
d.flow([{'path': [(300, 155), (400, 155)], 'color': 'green', 'dur': 0.4},
        {'path': [(680, 155), (780, 155)], 'color': 'green', 'dur': 0.4},
        {'path': [(300, 295), (350, 295), (350, 350), (400, 350)], 'color': 'red', 'dur': 0.5},
        {'path': [(680, 365), (780, 365)], 'color': 'red', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2026/11/11-1.svg'))

# =====================================================================
# 2026/11/11-2  call: reporter bidirectional
# =====================================================================
d = Diagram(1100, 600, 'Reporter: app state → OS. Event handler: OS buttons → app. Same path however the call started')
d.box(40, 140, 260, 120, 'Call state machine', ['idle → outgoing → active → ended', 'micEnabled · cameraEnabled'], color='blue')
d.box(420, 140, 260, 120, 'Native call reporter', ['subscribes via ref.listen', 'server callId ↔ OS call ID', 'ends calls by registered list'], color='purple')
d.box(800, 140, 260, 120, 'OS call', ['iOS CallKit · Dynamic Island', 'Android Telecom + call FGS'], color='green')
d.box(420, 350, 260, 120, 'Event handler', ['ACTION_CALL_ENDED → leave()', 'TOGGLE_MUTE → setMicrophoneEnabled', 'TOGGLE_AUDIO_SESSION → audio engine'], color='amber')
d.arrow([(300, 200), (420, 200)], color='blue', label='state change', label_size=12)
d.arrow([(680, 200), (800, 200)], color='purple')
d.text(740, 120, 'startCall · setCallConnected', size=11, color=PAL['purple'][0])
d.text(740, 136, 'muteCall · endCall', size=11, color=PAL['purple'][0])
d.arrow([(930, 260), (930, 410), (680, 410)], color='amber')
d.text(918, 335, 'Buttons pressed on Island · lock screen · notification', size=12, color=AMBER, anchor='end')
d.arrow([(420, 410), (170, 410), (170, 260)], color='amber')
d.note(40, 505, 1020, 64, ['setMicrophoneEnabled does nothing if the state is unchanged → no app ⇄ OS mute ping-pong',
                           'Ringing Android call accepted in-app: hideCallkitIncoming and re-register instead of endCall (= decline)'], color='muted', size=13)
d.flow([{'path': [(300, 200), (420, 200)], 'color': 'blue', 'dur': 0.4},
        {'path': [(680, 200), (800, 200)], 'color': 'purple', 'dur': 0.4, 'hold': 0.4},
        {'path': [(930, 260), (930, 410), (680, 410)], 'color': 'amber', 'dur': 0.6},
        {'path': [(420, 410), (170, 410), (170, 260)], 'color': 'amber', 'dur': 0.6, 'hold': 0.8}])
d.save(out('2026/11/11-2.svg'))

# =====================================================================
# 2026/11/11-3  call: iOS audio session timeline
# =====================================================================
d = Diagram(1100, 560, 'The audio engine runs only while CallKit keeps the session active — CallKit alone owns the session')
lanes = [('CallKit', 140), ('AVAudioSession', 230), ('LiveKit audio engine', 320)]
for name, y in lanes:
    d.text(165, y, name, size=13, anchor='end'); d.arrow([(180, y), (1070, y)], color='muted', head=False, width=1)
ev = [(270, 320, 'App start', ['externalCallSystem', 'engine: none'], 'muted'),
      (430, 140, 'startCall', ['call registered'], 'purple'),
      (590, 230, 'didActivate', ['session active'], 'green'),
      (590, 320, 'engine: default', ['audio on'], 'green'),
      (790, 230, 'Other audio cuts in', ['deactivation event'], 'amber'),
      (790, 320, 'Ignored', ['engine stays on'], 'amber'),
      (985, 140, 'endCall', ['didDeactivate'], 'purple'),
      (985, 320, 'engine: none', [], 'muted')]
for x, y, l, s, c in ev:
    d.box(x - 75, y - 28, 150, 56, l, s or None, color=c, label_size=13, sub_size=11)
d.arrow([(430, 168), (430, 190), (590, 190), (590, 202)], color='purple')
d.arrow([(590, 258), (590, 292)], color='green')
d.arrow([(790, 258), (790, 292)], color='amber', dashed=True)
d.arrow([(985, 168), (985, 292)], color='purple')
d.note(40, 395, 500, 140, ['3-second fallback', 'If didActivate is missed (e.g. app still waking up),', 'open the engine ourselves after 3s — no silent calls'], color='blue', size=13)
d.note(560, 395, 500, 140, ['Ignore deactivation during a call', "Plugin 3.1.6 doesn't tell Dart when a connected", 'call is reactivated → turn off here, silent to the end'], color='amber', size=13)
d.flow([{'path': [(430, 168), (430, 190), (590, 190), (590, 202)], 'color': 'purple', 'dur': 0.5},
        {'path': [(590, 258), (590, 292)], 'color': 'green', 'dur': 0.4, 'hold': 0.4},
        {'path': [(790, 258), (790, 292)], 'color': 'amber', 'dur': 0.4, 'hold': 0.4},
        {'path': [(985, 168), (985, 292)], 'color': 'purple', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/11/11-3.svg'))

# =====================================================================
# 2026/11/11-4  call: web audio re-attach
# =====================================================================
d = Diagram(1100, 540, 'The room and tracks were still alive — only the audio element left the document with the old container')
d.group(40, 85, 500, 370, 'Before — navigating /chat → /download')
d.box(70, 120, 200, 70, 'Room · remote tracks', ['module level · still alive'], color='green')
d.box(70, 240, 200, 110, 'Old CallHost', ['hidden container', '└ <audio> (track.attach)'], color='red', dashed=True)
d.box(310, 240, 200, 110, 'New CallHost', ['hidden container', '└ (empty)'], color='gray')
d.arrow([(170, 190), (170, 240)], color='green', label='once, on TrackSubscribed', label_size=11, label_dy=0)
d.text(290, 395, 'Old container unmounts → <audio> goes with it', size=13, color=RED)
d.text(290, 420, 'Call stays connected, only remote audio drops', size=13, color=RED)
d.group(560, 85, 500, 370, 'After — keep the tracks and re-attach them')
d.box(590, 120, 200, 70, 'remoteAudioTracks', ['Set<RemoteAudioTrack>'], color='blue')
d.box(830, 120, 200, 70, 'New CallHost mounts', ['setLiveKitContainer(el)'], color='purple')
d.box(700, 240, 230, 110, 'setAudioContainer(el)', ['track.detach() → remove', 'el.appendChild(track.attach())'], color='green')
d.arrow([(690, 190), (690, 215), (760, 215), (760, 240)], color='blue')
d.arrow([(930, 190), (930, 215), (870, 215), (870, 240)], color='purple')
d.text(810, 395, 'If autoplay is blocked (canPlaybackAudio=false),', size=13, color=MUTED)
d.text(810, 420, 'room.startAudio() once on the next pointerdown / keydown', size=13, color=MUTED)
d.note(40, 470, 1020, 46, 'Put track.attach() elements in the DOM of a component that remounts, and they share its lifetime', color='muted', size=13)
d.flow([{'path': [(170, 190), (170, 240)], 'color': 'green', 'dur': 0.4},
        {'path': [(170, 350), (170, 380)], 'color': 'red', 'dur': 0.4, 'hold': 0.4},
        {'path': [(930, 190), (930, 215), (870, 215), (870, 240)], 'color': 'purple', 'dur': 0.4},
        {'path': [(690, 190), (690, 215), (760, 215), (760, 240)], 'color': 'blue', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2026/11/11-4.svg'))

# =====================================================================
# 2026/11/11-5  call: video background
# =====================================================================
d = Diagram(1100, 500, 'If the OS just stops capture, the peer sees a frozen frame; if the app mutes first, an avatar')
d.text(40, 110, 'Before', size=15, weight=800, anchor='start')
d.box(40, 130, 220, 90, 'iPhone goes home', ['AppLifecycle: paused'], color='gray')
d.box(320, 130, 240, 90, 'iOS force-stops capture', ['track stays published', 'no mute signal'], color='amber')
d.box(620, 130, 200, 90, 'LiveKit SFU', ['frames just stop'], color='gray')
d.box(880, 130, 180, 90, "Peer's screen", ['last frame frozen'], color='red')
d.arrow([(260, 175), (320, 175)], color='gray'); d.arrow([(560, 175), (620, 175)], color='amber'); d.arrow([(820, 175), (880, 175)], color='red')
d.text(40, 270, 'After (iOS)', size=15, weight=800, anchor='start')
d.box(40, 290, 220, 90, 'iPhone goes home', ['AppLifecycleListener'], color='gray')
d.box(320, 290, 240, 90, 'setCameraEnabled(false)', ['the app turns it off first', 'cameraEnabled choice kept'], color='blue')
d.box(620, 290, 200, 90, 'LiveKit SFU', ['TrackMuted event'], color='gray')
d.box(880, 290, 180, 90, "Peer's screen", ['avatar tile'], color='green')
d.arrow([(260, 335), (320, 335)], color='gray'); d.arrow([(560, 335), (620, 335)], color='blue'); d.arrow([(820, 335), (880, 335)], color='green')
d.note(40, 410, 1020, 64, ['On resume, turn it back on only if backgrounding turned it off · backgrounded while connecting → off again after connect',
                           'On Android, OS call registration gives the FGS the camera type, so video keeps sending in the background'], color='muted', size=13)
d.flow([{'path': [(260, 175), (320, 175)], 'color': 'gray', 'dur': 0.3},
        {'path': [(560, 175), (620, 175)], 'color': 'amber', 'dur': 0.3},
        {'path': [(820, 175), (880, 175)], 'color': 'red', 'dur': 0.3, 'hold': 0.4},
        {'path': [(260, 335), (320, 335)], 'color': 'gray', 'dur': 0.3},
        {'path': [(560, 335), (620, 335)], 'color': 'blue', 'dur': 0.3},
        {'path': [(820, 335), (880, 335)], 'color': 'green', 'dur': 0.3, 'hold': 0.8}])
d.save(out('2026/11/11-5.svg'))
print('ok')
