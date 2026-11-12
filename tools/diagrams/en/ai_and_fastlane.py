"""English edition of tools/diagrams/make_diagrams_batch3.py
("AI-Native Development" series + the fastlane post).
Run: python3 tools/diagrams/en/ai_and_fastlane.py "$PWD"
Logos are inlined from assets/img/logos/*.svg (Simple Icons, CC0).
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from diag import Diagram, INK, MUTED

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img/en', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

G = {'gray': '#1f2937', 'muted': '#6b7280', 'blue': '#2563eb', 'green': '#059669', 'red': '#dc2626', 'amber': '#d97706', 'purple': '#7c3aed'}
BRAND = {'claude': '#D97757', 'anthropic': '#191919', 'openai': '#412991', 'githubcopilot': '#1f2937', 'cursor': '#1f2937', 'github': '#181717'}

_logo_cache = {}
def logo_path(name):
    if name not in _logo_cache:
        s = open(os.path.join(ROOT, 'assets/img/logos', name + '.svg'), encoding='utf-8').read()
        _logo_cache[name] = re.search(r'<path d="([^"]+)"', s).group(1)
    return _logo_cache[name]

def icon(d, name, x, y, size=28, color=None):
    """Embed a 24x24 Simple Icons glyph at top-left (x, y), scaled to size."""
    d.parts.append(f'<g transform="translate({x},{y}) scale({size / 24:.4f})"><path d="{logo_path(name)}" fill="{color or BRAND.get(name, INK)}"/></g>')

def logo_box(d, x, y, w, h, name, label, sub=None, color='gray', size=26):
    d.box(x, y, w, h, color=color)
    icon(d, name, x + 14, y + h / 2 - size / 2, size)
    d.text(x + 14 + size + 10, y + h / 2 + (0 if sub else 5), label, size=14, weight=700, anchor='start')
    if sub:
        d.text(x + 14 + size + 10, y + h / 2 + 18, sub, size=11, weight=600, color=MUTED, anchor='start')

# =====================================================================
# 2026/06/23-1  subagent: PR timeline
# =====================================================================
d = Diagram(1100, 520, 'Five PRs on the afternoon of 2026-06-23 — two merged seconds after creation, three waited for CI')
def tx(hhmm):
    h, m = hhmm.split(':'); t = int(h) * 60 + int(m)
    return 80 + (t - 15 * 60 - 40) * (960 / 115)
d.arrow([(80, 130), (1040, 130)], color='muted', head=True)
for lab in ('15:47', '16:00', '16:22', '16:48', '17:05', '17:29'):
    x = tx(lab); d.arrow([(x, 124), (x, 136)], color='muted', head=False, width=1); d.text(x, 115, lab, size=11, color=MUTED)
d.box(tx('16:22'), 150, tx('17:12') - tx('16:22'), 36, color='red'); d.text((tx('16:22') + tx('17:12')) / 2, 173, 'dev red for about 50 min (16:22:30 → 17:12:28)', size=12, weight=700, color=G['red'])
prs = [('15:47', '15:53', '#466 Sidebar shell (1/N)', 'By me · merged after CI passed', 'green'),
       ('16:22', '16:22', '#470 Sidebar on every screen (60 files)', 'Agent · merged 7 s later · CI failed afterward', 'red'),
       ('16:48', '16:48', '#472 Quote/order/payment modals (15 files)', 'Agent · merged 5 s later · CI failed', 'red'),
       ('17:05', '17:12', '#473 Clean up 12 broken tests', 'By me · merged after CI passed → dev recovered', 'green'),
       ('17:21', '17:29', '#475 Remove unused Navbar', 'By me · merged after CI passed', 'green')]
for i, (a, b, lab, sub, c) in enumerate(prs):
    y = 210 + i * 56
    x1, x2 = tx(a), max(tx(b), tx(a) + 6)
    d.arrow([(x1, y + 14), (x2, y + 14)], color=c, width=6, head=False)
    left = i in (3, 4)
    lx = x1 - 8 if left else x2 + 10
    d.text(lx, y + 10, lab, size=12, weight=700, anchor='end' if left else 'start')
    d.text(lx, y + 26, sub, size=11, weight=600, color=G[c] if c == 'red' else MUTED, anchor='end' if left else 'start')
d.text(560, 507, 'I merged other PRs (#469, #471) 14 s before and 68 s after these merges — the agent slipped in while I was looking elsewhere', size=11, weight=600, color=MUTED)
d.flow([{'path': [(tx('16:22'), 224), (tx('16:22') + 6, 224)], 'color': 'red', 'dur': 0.3, 'hold': 0.5},
        {'path': [(tx('16:48'), 280), (tx('16:48') + 6, 280)], 'color': 'red', 'dur': 0.3, 'hold': 0.5},
        {'path': [(tx('17:05'), 392), (tx('17:12'), 392)], 'color': 'green', 'dur': 0.8, 'hold': 0.8}])
d.save(out('2026/06/23-1.svg'))

# =====================================================================
# 2026/06/23-2  subagent: delegation chain
# =====================================================================
d = Diagram(1100, 640, 'No permission boundary — subagent ⊂ main session ⊂ user')
d.group(40, 86, 1020, 100, 'User terminal')
logo_box(d, 60, 112, 300, 56, 'github', 'gh auth: my account', 'keyring · scope repo, workflow', color='gray')
d.box(390, 112, 650, 56, color='muted'); d.text(715, 136, 'Shell env · ~/.config/gh · .claude/settings.json · hooks — all inherited downward', size=12, weight=600); d.text(715, 156, 'No separate credentials', size=11, color=MUTED)
d.group(40, 210, 1020, 170, 'Claude Code main session (orchestrator)')
logo_box(d, 60, 240, 300, 56, 'claude', 'Main session', 'Looking at other PRs (#469, #471)', color='gray')
d.box(390, 240, 200, 56, 'permissions', ['allow: Bash(git *) …', 'gh not listed'], color='amber', label_size=12, sub_size=10)
d.box(610, 240, 200, 56, 'safety-guard.sh', ['exit 2 · only rm -rf · SQL ·', 'force push to main'], color='amber', label_size=12, sub_size=10)
d.box(830, 240, 210, 56, 'pre-push.sh', ['prints "push blocked",', 'but exit 1 = non-blocking'], color='red', label_size=12, sub_size=10)
d.text(550, 330, 'Agent(subagent_type="nextjs-modifier", prompt="Remove <Navbar/> from 48 files …")', size=12, weight=600, mono=True)
d.arrow([(210, 296), (210, 320), (210, 404)], color='gray')
d.group(40, 404, 1020, 216, 'Subagent nextjs-modifier')
d.box(60, 434, 300, 56, 'tools: (none)', ['→ inherits all of main\'s Bash · Edit · Write'], color='red', label_size=13, sub_size=11)
steps = [('Edit ×48', ['intended scope'], 'green'), ('git push -u origin …', ['"blocked" message,', 'but exit 1'], 'amber'),
         ('gh pr create', ['default template,', 'jest never run'], 'red'), ('gh pr merge --squash', ['dev unprotected →', 'merged 7 s later'], 'red')]
for i, (lab, sub, c) in enumerate(steps):
    x = 390 + i * 165
    d.box(x, 434, 150, 56, lab, sub, color=c, label_size=11, sub_size=9)
    if i: d.arrow([(x - 15, 462), (x, 462)], color=c)
d.text(550, 530, 'GitHub: author = mergedBy = my account · Co-authored-by: Claude — indistinguishable from PRs I made in a session', size=12, weight=700, color=G['red'])
d.text(550, 556, 'The only fingerprints: the default PR template, an unchecked jest item, seconds from creation to merge', size=11, weight=600, color=MUTED)
d.flow([{'path': [(210, 296), (210, 404)], 'color': 'gray', 'dur': 0.5},
        {'path': [(360, 462), (390, 462)], 'color': 'green', 'dur': 0.3},
        {'path': [(540, 462), (555, 462)], 'color': 'amber', 'dur': 0.2}, {'path': [(705, 462), (720, 462)], 'color': 'red', 'dur': 0.2},
        {'path': [(870, 462), (885, 462)], 'color': 'red', 'dur': 0.2, 'hold': 1.0}])
d.save(out('2026/06/23-2.svg'))

# =====================================================================
# 2026/06/23-3  subagent: guard layers
# =====================================================================
d = Diagram(1100, 600, 'Guard layers as of 2026-06-30 — none hard-blocks the incident path (push → pr create → pr merge)')
layers = [('Edit', 'worktree-guard.sh', 'PreToolUse(Edit|Write) · exit 2', 'Blocks source edits in the hub (06-18)', 'green', 'Edits were in a worktree → n/a'),
          ('Command', 'safety-guard.sh', 'PreToolUse(Bash) · exit 2', 'rm -rf · destructive SQL · force push to main (05-07)', 'green', 'dev and gh not covered'),
          ('Push', 'pre-push.sh', 'PreToolUse(Bash) · exit 1', 'Tests + 90% coverage "block" (05-07)', 'red', '✗ message only, push goes out'),
          ('Intent', 'Delegation prompt rule', '"No git · gh · PR · merge; edit + tsc/jest only"', 'Added the day of the incident (06-23)', 'amber', 'Only as long as it\'s obeyed'),
          ('Tools', 'agents tools:', 'unset on 9 modifiers/generators', '= inherits everything (still)', 'red', '✗ all of Bash'),
          ('Server', 'dev branch protection', 'none', 'CI is not a required check (still)', 'red', '✗ a 7-second merge is possible')]
for i, (zone, name, how, when, c, verdict) in enumerate(layers):
    y = 92 + i * 76
    d.box(40, y, 90, 60, zone, color='muted', label_size=14)
    d.box(150, y, 300, 60, name, [how], color=c, label_size=13, sub_size=10)
    d.box(470, y, 300, 60, color='gray'); d.text(620, y + 35, when, size=11, weight=600)
    d.box(790, y, 270, 60, color=c); d.text(925, y + 35, verdict, size=12, weight=700, color=G[c])
d.text(550, 572, 'You need a guard per threat model — the guard against index tangles doesn\'t stop an agent from merging', size=13, weight=700)
d.flow([{'path': [(120, 122 + i * 76), (150, 122 + i * 76)], 'color': layers[i][4], 'dur': 0.3, 'hold': 0.2} for i in range(6)])
d.save(out('2026/06/23-3.svg'))

# =====================================================================
# 2026/10/08-1  AI product: two arcs timeline
# =====================================================================
d = Diagram(1100, 520, 'The same Claude API, added twice — chat pulled after 5 days, the document judge\'s cost redesigned after 6')
d.arrow([(80, 150), (1040, 150)], color='muted')
def mx(month, day):
    days = {5: 0, 6: 31, 7: 61, 8: 92, 9: 123, 10: 153}[month] + day
    return 80 + (days - 20) * (960 / 150)
for lab, m, dd in (('May', 5, 27), ('Jun', 6, 15), ('Jul', 7, 15), ('Aug', 8, 15), ('Sep', 9, 15), ('Oct', 10, 8)):
    x = mx(m, dd); d.text(x, 138, lab, size=11, color=MUTED)
ev = [((5, 27), '05-27 Chat assistant added', ['Claude Sonnet · SSE · token limits', '4 tables · 10 endpoints'], 'amber', 180),
      ((6, 1), '06-01 Removed entirely', ['105 files · reset to v1.0.0', 'manual: 13-line placeholders'], 'red', 300),
      ((10, 2), '10-02 Document judge added', ['Structured output · 100 a day', 'Jev screening (exclude 0.1)'], 'green', 180),
      ((10, 8), '10-08 Cost redesign', ['Measured $0.23/doc · $37/day', 'SCREENED_PIPE · exclude 0.3 · $10 goal'], 'blue', 300)]
for (m, dd), lab, sub, c, y in ev:
    x = mx(m, dd)
    d.arrow([(x, 150), (x, y)], color=c, head=False, dashed=True, width=1)
    bx = min(max(x - 130, 40), 1060 - 260)
    d.box(bx, y, 260, 76, lab, sub, color=c, label_size=13, sub_size=11)
icon(d, 'claude', mx(5, 27) - 14, 118 - 30, 24); icon(d, 'claude', mx(10, 2) - 14, 118 - 30, 24)
d.box(360, 230, 400, 120, color='muted'); d.lines(560, 258, ['A 4-month gap', 'Same API, different question:', '"Ask me anything" → "4 blank cells in a table"', '"users × tokens" → "1 document = 1 call"'], size=12, weight=600, gap=22)
d.text(550, 430, 'What changed wasn\'t the model but the problem definition, the unit of cost and the failure handling', size=14, weight=700)
d.text(550, 456, '(Pre-launch platform — prd is a production-like environment the team runs; the pool of notices is real public data)', size=11, weight=600, color=MUTED)
d.flow([{'path': [(mx(5, 27), 150), (mx(6, 1), 150)], 'color': 'red', 'dur': 0.6, 'hold': 0.6},
        {'path': [(mx(6, 1), 150), (mx(10, 2), 150)], 'color': 'muted', 'dur': 1.4},
        {'path': [(mx(10, 2), 150), (mx(10, 8), 150)], 'color': 'blue', 'dur': 0.5, 'hold': 1.0}])
d.save(out('2026/10/08-1.svg'))

# =====================================================================
# 2026/10/08-2  AI product: cost bars + score bands
# =====================================================================
d = Diagram(1100, 560, 'Daily Claude cost, and Claude YES rate by Jev score band — measured on 407 docs in prd (2026-10-08)')
d.group(40, 86, 480, 440, 'Daily cost (Claude calls)')
base_y, scale = 470, 8.5
bars = [('Measured (pre 10-08)', 37, 'red', '~160 docs × $0.23', False), ('Target (#1753 design)', 10, 'blue', 'only the gated Claude band', True), ('Expected (auto, 10-15)', 5, 'green', 'Opus only if retention likely', True)]
for i, (lab, v, c, sub, dashed) in enumerate(bars):
    x = 80 + i * 150
    h = v * scale
    d.box(x, base_y - h, 110, h, color=c, dashed=dashed)
    d.text(x + 55, base_y - h - 10, f'${v}', size=16, weight=700, color=G[c])
    d.text(x + 55, base_y + 18, lab, size=10, weight=700)
    d.text(x + 55, base_y + 34, sub, size=9, weight=600, color=MUTED)
d.arrow([(70, base_y), (510, base_y)], color='muted', head=False, width=1)
d.text(505, 110, 'Dashed = target / expected (not measured)', size=11, weight=600, color=MUTED, anchor='end')
d.group(560, 86, 500, 440, 'Jev pipe score band → share Claude called "pipes: YES"')
bands = [('0.1 – 0.3', 2, '4 of 194', 'red', '→ SCREENED_OUT (excluded, no Claude)'), ('0.3 – 0.7', None, 'the band Claude reads', 'amber', '→ to Claude'), ('≥ 0.7', 67, '', 'green', '→ SCREENED_PIPE ("likely", no Claude)')]
for i, (lab, v, n, c, act) in enumerate(bands):
    x = 600 + i * 150
    if v is None:
        d.box(x, 180, 110, 290, color=c, dashed=True); d.text(x + 55, 320, '?', size=28, weight=700, color=G[c])
    else:
        h = v * 4.3; d.box(x, base_y - h, 110, h, color=c); d.text(x + 55, base_y - h - 10, f'{v}%', size=16, weight=700, color=G[c])
    d.text(x + 55, base_y + 18, lab, size=11, weight=700); d.text(x + 55, base_y + 34, n, size=9, weight=600, color=MUTED)
    d.text(x + 55 + (12 if i == 0 else 0), 130 + (i % 2) * 16, act, size=9, weight=700, color=G[c])
d.arrow([(590, base_y), (1050, base_y)], color='muted', head=False, width=1)
d.flow([{'path': [(135, base_y - 37 * scale), (285, base_y - 10 * scale)], 'color': 'blue', 'dur': 0.8, 'hold': 0.4},
        {'path': [(285, base_y - 10 * scale), (435, base_y - 5 * scale)], 'color': 'green', 'dur': 0.6, 'hold': 1.0}])
d.save(out('2026/10/08-2.svg'))

# =====================================================================
# 2026/10/08-3  AI product: pipeline with gate
# =====================================================================
d = Diagram(1100, 640, 'Every day at 05:30 — candidates, extraction, judge-model gate, Claude, calculator, blank cells')
s1 = d.box(40, 100, 180, 64, '① Pick candidates', ['Design/construction bids', '≤ 180 days · 100 a day'], color='gray', label_size=13, sub_size=10)
s2 = d.box(260, 100, 180, 64, '② Extract attachments', ['PDF · HWP · DOCX → text', 'SOW > notice > other'], color='gray', label_size=13, sub_size=10)
s3 = d.box(480, 100, 200, 64, '③ Jev scoring (gate)', ['2 questions per 25,000 chars', '$0.042/1M tokens · 0.3–0.5 s'], color='purple', label_size=13, sub_size=10)
d.arrow([(220, 132), (260, 132)], color='gray'); d.arrow([(440, 132), (480, 132)], color='gray')
# branches
b1 = d.box(720, 90, 340, 44, 'Retention keyword OR retention ≥ 0.3  → Claude', color='green', label_size=12)
b2 = d.box(720, 144, 340, 44, 'pipe ≥ 0.7 → SCREENED_PIPE (no Claude, cells left blank)', color='amber', label_size=11)
b3 = d.box(720, 198, 340, 44, 'pipe < 0.3 · all read · no product name → SCREENED_OUT', color='red', label_size=11)
b4 = d.box(720, 252, 340, 44, 'Everything else (0.3 ≤ pipe < 0.7)  → Claude', color='green', label_size=12)
for y in (112, 166, 220, 274): d.arrow([(680, 132), (700, 132), (700, y), (720, y)], color='muted', width=1)
# claude analysis
logo_box(d, 480, 340, 340, 70, 'claude', 'Claude analysis (Opus)', 'JSON schema · effort high · 10-min timeout · $0.23/doc', color='green')
d.arrow([(890, 134), (890, 140)], color='green', head=False, width=1)
d.arrow([(1060, 112), (1080, 112), (1080, 375), (820, 375)], color='green')
d.arrow([(1060, 274), (1075, 274), (1075, 370)], color='green', head=False)
c1 = d.box(40, 340, 200, 70, 'Capacity calculator', ['Deterministic code —', 'the LLM never sizes capacity'], color='blue', label_size=13, sub_size=10)
r = d.box(260, 340, 200, 70, 'Resolver', ['Document value, else calculator', 'blank cells only'], color='gray', label_size=13, sub_size=10)
d.arrow([(480, 375), (460, 375)], color='green'); d.arrow([(260, 375), (240, 375)], color='gray', head=False); d.arrow([(240, 375), (260, 375)], color='blue', head=False)
d.box(40, 440, 420, 66, 'Sales-prospect table', ['Retention · pipes · applicability · est. capacity', 'labeled "AI document analysis (provisional)"'], color='green', label_size=13, sub_size=11)
d.arrow([(360, 410), (360, 440)], color='gray')
d.box(500, 440, 560, 66, color='muted'); d.lines(780, 455, ['Jev down → to Claude without screening (fail-open)', 'Claude account error → stop the whole run (fail-stop)', '429/529 → retry after 60 s · 413 / refusal / too many tokens → that doc only'], size=11, weight=600, gap=18)
d.text(550, 540, 'Output is only enums, numbers and quotes — even if a document contains instructions, nothing can leak past the scores', size=12, weight=700, color=G['purple'])
d.text(550, 566, '"Screening is a way to cut cost, not a precondition for analysis"', size=12, weight=600, color=MUTED)
d.flow([{'path': [(220, 132), (260, 132)], 'color': 'gray', 'dur': 0.4}, {'path': [(440, 132), (480, 132)], 'color': 'gray', 'dur': 0.4},
        {'path': [(680, 132), (700, 132), (700, 274), (720, 274)], 'color': 'purple', 'dur': 0.6},
        {'path': [(1060, 274), (1075, 274), (1075, 375), (820, 375)], 'color': 'green', 'dur': 0.9},
        {'path': [(480, 375), (460, 375)], 'color': 'green', 'dur': 0.2}, {'path': [(360, 410), (360, 440)], 'color': 'gray', 'dur': 0.3, 'hold': 1.0}])
d.save(out('2026/10/08-3.svg'))

# =====================================================================
# 2026/10/27-3  dual harness: one harness, two agents
# =====================================================================
d = Diagram(1100, 620, 'One harness, two agents — no file is maintained twice by hand')
d.group(40, 86, 300, 470, 'Claude Code side')
logo_box(d, 60, 116, 260, 56, 'claude', 'Claude Code', '≥ 2.1.277', color='gray')
d.box(60, 192, 260, 56, '.claude/settings.json', ['hook wiring · permissions'], color='blue', label_size=12, sub_size=10)
d.box(60, 268, 260, 56, '.claude/agents/*.md', ['15 subagents — the source'], color='blue', label_size=12, sub_size=10)
d.box(60, 344, 260, 56, '.claude/skills → symlink', ['../.agents/skills'], color='blue', label_size=12, sub_size=10)
d.box(60, 420, 260, 56, 'PreToolUse(Edit|Write)', ['worktree-guard · post-edit-lint'], color='blue', label_size=12, sub_size=10)
d.group(400, 86, 300, 470, 'Shared (sources live here)')
d.box(420, 116, 260, 56, 'AGENTS.md', ['root + 5 stacks, ≤ 300 lines per file'], color='green', label_size=13, sub_size=10)
d.box(420, 192, 260, 56, '.agents/skills/ (32)', ['9 with side effects: no model invocation'], color='green', label_size=13, sub_size=10)
d.box(420, 268, 260, 56, '.claude/hooks/*.sh', ['decision scripts — one copy'], color='green', label_size=13, sub_size=10)
d.box(420, 344, 260, 56, '.githooks/ pre-commit · pre-push', ['gates: any tool, terminal too'], color='green', label_size=13, sub_size=10)
d.box(420, 420, 260, 56, 'memory/ · docs/', ['the repo is the source of truth'], color='green', label_size=13, sub_size=10)
d.group(760, 86, 300, 470, 'Codex side')
logo_box(d, 780, 116, 260, 56, 'openai', 'Codex', '0.164.0', color='gray')
d.box(780, 192, 260, 56, '.codex/hooks.json', ['calls the same .claude/hooks/*.sh'], color='purple', label_size=12, sub_size=10)
d.box(780, 268, 260, 56, '.codex/agents/*.toml', ['generated — gen-codex-agents.py'], color='purple', label_size=12, sub_size=10)
d.box(780, 344, 260, 56, '$start = /start', ['reads .agents/skills directly'], color='purple', label_size=12, sub_size=10)
d.box(780, 420, 260, 56, 'PreToolUse(apply_patch)', ['codex-adapter.sh → same guards'], color='purple', label_size=12, sub_size=10)
d.arrow([(320, 372), (420, 220)], color='blue', dashed=True, label='symlink', label_dy=-6, label_size=10)
d.arrow([(320, 448), (420, 296)], color='blue', dashed=True)
d.arrow([(680, 220), (780, 372)], color='purple', dashed=True, label='reads', label_dy=-6, label_size=10)
d.arrow([(680, 296), (780, 448)], color='purple', dashed=True, label='exec', label_dy=-6, label_size=10)
d.arrow([(320, 310), (380, 310), (380, 334), (720, 334), (720, 310), (780, 310)], color='purple', dashed=True)
d.lines(730, 248, ['generated,', 'pre-commit', 'checks'], size=9, weight=700, color=G['purple'], gap=11)
d.text(550, 586, 'Gates = git hooks · skills = .agents/skills · instructions = AGENTS.md · review = the other model — either one alone runs it all', size=12, weight=700)
d.flow([{'path': [(320, 372), (420, 220)], 'color': 'blue', 'dur': 0.6}, {'path': [(680, 220), (780, 372)], 'color': 'purple', 'dur': 0.6},
        {'path': [(320, 448), (420, 296)], 'color': 'blue', 'dur': 0.6}, {'path': [(680, 296), (780, 448)], 'color': 'purple', 'dur': 0.6},
        {'path': [(320, 310), (380, 310), (380, 334), (720, 334), (720, 310), (780, 310)], 'color': 'purple', 'dur': 1.2, 'hold': 0.8}])
d.save(out('2026/10/27-3.svg'))

# =====================================================================
# 2026/10/27-4  dual harness: /pr cross-review flow
# =====================================================================
d = Diagram(1100, 600, '/pr cross review — the opposite model reviews; if it can\'t, exit 3 and self-review')
d.box(40, 110, 140, 56, '/pr', ['in a worktree'], color='gray', label_size=14, sub_size=10)
d.box(220, 110, 220, 56, 'Detect working tool', ['CLAUDECODE ? → reviewer codex', 'CODEX_THREAD_ID ? → claude'], color='gray', label_size=12, sub_size=10)
d.box(480, 110, 220, 56, 'Depth', ['migration · auth · permission ·', 'payment · hooks → high, else medium'], color='amber', label_size=12, sub_size=10)
d.arrow([(180, 138), (220, 138)], color='gray'); d.arrow([(440, 138), (480, 138)], color='gray')
logo_box(d, 300, 230, 260, 70, 'openai', 'codex review', 'read-only sandbox · effort = depth', color='purple')
logo_box(d, 600, 230, 300, 70, 'claude', 'claude -p --tools Read,Grep,Glob', 'no shell · diff in a file · opus/sonnet', color='blue')
d.arrow([(330, 166), (430, 230)], color='purple', label='working in Claude', label_dy=-6, label_size=10)
d.arrow([(640, 166), (700, 230)], color='blue', label='working in Codex', label_dy=-6, label_size=10)
d.box(40, 350, 300, 70, 'exit 0', ['VERDICT: PASS | REVIEW | BLOCK', 'Critical → BLOCK, High → REVIEW'], color='green', label_size=13, sub_size=10)
d.box(380, 350, 340, 70, 'exit 3 — reviewer unavailable', ['not installed · limit · login · empty output', '→ don\'t block; use the current tool\'s reviewer'], color='amber', label_size=13, sub_size=10)
d.box(760, 350, 300, 70, 'exit 1', ['other errors → read the message and fix,', 'or handle it like 3'], color='red', label_size=13, sub_size=10)
for x1 in (430, 750):
    d.arrow([(x1, 300), (190, 350)], color='green', width=1); d.arrow([(x1, 300), (550, 350)], color='amber', width=1); d.arrow([(x1, 300), (910, 350)], color='red', width=1)
d.box(40, 460, 1020, 56, color='muted'); d.text(550, 482, 'PR body "## Review": reviewer · verdict · fixed · not fixed (why)  →  wait for all CI to pass, then squash-merge with --match-head-commit', size=12, weight=600); d.text(550, 504, '"The same model is bad at spotting its own mistakes" — runs in parallel with the security review', size=11, weight=600, color=MUTED)
d.text(550, 560, 'This PR was itself reviewed by the script (Codex once, Claude twice) — it caught the shell access, false positives and an infinite loop', size=12, weight=700, color=G['purple'])
d.flow([{'path': [(180, 138), (220, 138)], 'color': 'gray', 'dur': 0.3}, {'path': [(440, 138), (480, 138)], 'color': 'gray', 'dur': 0.3},
        {'path': [(330, 166), (430, 230)], 'color': 'purple', 'dur': 0.5, 'hold': 0.6},
        {'path': [(430, 300), (190, 350)], 'color': 'green', 'dur': 0.5, 'hold': 0.4},
        {'path': [(430, 300), (550, 350)], 'color': 'amber', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/10/27-4.svg'))

print('ok')

# =====================================================================
# 2026/04/16-1  adoption: four eras of AI coding tools, with logos
# =====================================================================
d = Diagram(1100, 560, 'Four years of AI coding tools — autocomplete, chat, agents in the editor, terminal agents')
def yx(y, m):
    return 70 + ((y - 2021) * 12 + (m - 1)) * (960 / 66)
d.arrow([(70, 140), (1040, 140)], color='muted')
for y in (2021, 2022, 2023, 2024, 2025, 2026):
    x = yx(y, 1); d.arrow([(x, 134), (x, 146)], color='muted', head=False, width=1); d.text(x, 124, str(y), size=12, weight=700, color=MUTED)
eras = [('Autocomplete', 2021, 6, 2022, 11, 'blue'), ('Chat', 2022, 11, 2023, 6, 'amber'), ('Agents in the editor', 2023, 6, 2025, 2, 'purple'), ('Terminal agents', 2025, 2, 2026, 7, 'green')]
for lab, y1, m1, y2, m2, c in eras:
    x1, x2 = yx(y1, m1), yx(y2, m2)
    d.box(x1, 156, x2 - x1 - 4, 30, color=c); d.text((x1 + x2) / 2, 176, lab, size=12, weight=700, color=G[c])
# (logo, year, month, label, sub lines, box y, box x offset from the event line)
events = [('githubcopilot', 2021, 6, 'GitHub Copilot', ['Preview 2021-06 · GA 2022-06'], 210, -20),
          ('openai', 2022, 11, 'ChatGPT', ['2022-11-30'], 300, -20),
          ('cursor', 2023, 3, 'Cursor', ['2023, a VS Code fork'], 390, -20),
          ('anthropic', 2024, 11, 'MCP', ['Released 2024-11-25'], 210, -200),
          ('claude', 2025, 2, 'Claude Code', ['Preview 2025-02-24', 'GA 2025-05-22'], 300, -173),
          ('openai', 2025, 4, 'Codex CLI', ['2025-04-16', 'Copilot agent mode 2025-04'], 390, -142)]
BW = 220
for name, y, m, lab, sub, by, off in events:
    x = yx(y, m)
    d.arrow([(x, 140), (x, by)], color='muted', head=False, dashed=True, width=1)
    bx = max(40, min(x + off, 1060 - BW))
    bh = 56 if len(sub) == 1 else 66
    d.box(bx, by, BW, bh, color='gray'); icon(d, name, bx + 12, by + bh / 2 - 14, 28)
    ty = by + bh / 2 - (len(sub) * 15) / 2
    d.text(bx + 52, ty, lab, size=13, weight=700, anchor='start')
    for i, s in enumerate(sub):
        d.text(bx + 52, ty + 18 + i * 14, s, size=10, weight=600, color=MUTED, anchor='start')
d.box(40, 490, 1020, 50, color='green'); d.text(550, 510, 'What\'s different about the fourth: the agent holds the shell — it runs builds, tests and commits. From then on, the problem is permissions and gates, not tools', size=12, weight=700, color=G['green']); d.text(550, 530, '2025-12: MCP and AGENTS.md donated to the Agentic AI Foundation (Linux Foundation) · 2026-04-16: this repo\'s first Co-Authored-By commit', size=11, weight=600, color=MUTED)
d.flow([{'path': [(yx(2021, 6), 140), (yx(2026, 4), 140)], 'color': 'green', 'dur': 3.0, 'hold': 1.0}])
d.save(out('2026/04/16-1.svg'))

# =====================================================================
# 2026/04/16-2  adoption: monthly commits with three eras
# =====================================================================
d = Diagram(1100, 520, 'Monthly commits — solo (2025-05 to 2026-02), agent but same workflow (2026-03), agent-driven PRs (2026-04)')
months = [('25-05', 3), ('06', 17), ('07', 22), ('08', 12), ('09', 8), ('10', 0), ('11', 15), ('12', 10), ('26-01', 0), ('02', 1), ('03', 38), ('04', 81)]
base, scale, bw = 420, 2.8, 60
for i, (lab, v) in enumerate(months):
    x = 80 + i * 80
    c = 'muted' if i < 10 else ('amber' if i == 10 else 'green')
    h = max(v * scale, 2)
    d.box(x, base - h, bw, h, color=c)
    d.text(x + bw / 2, base - h - 8, str(v), size=12, weight=700, color=G[c] if c != 'muted' else MUTED)
    d.text(x + bw / 2, base + 18, lab, size=11, weight=600, color=MUTED)
d.arrow([(70, base), (1050, base)], color='muted', head=False, width=1)
d.group(70, 100, 790, 60, 'Solo, autocomplete era — one-line English [TYPE] titles, direct pushes, 0 PRs, coverage gate 10% → 1%', color='muted')
d.group(870, 100, 90, 60, 'March', color='amber'); d.text(915, 140, 'setup only', size=11, weight=700, color=G['amber'])
d.group(950, 100, 110, 60, 'April', color='green'); d.text(1005, 140, '57 PRs', size=11, weight=700, color=G['green'])
d.text(550, 457, '2025-10 and 2026-01 had 0 commits · 2026-02 was a single commit, "add a lot of different things"', size=11, weight=600, color=MUTED)
d.text(550, 475, 'March: 16 of 38 were CI trial and error · April 16: first Co-Authored-By, first PR CI, PR #1', size=11, weight=600, color=MUTED)
d.text(550, 501, 'This is output, not value — whenever this series uses numbers, it states that limit too', size=12, weight=700)
d.flow([{'path': [(880, 100), (880, 160)], 'color': 'amber', 'dur': 0.4, 'hold': 0.4}, {'path': [(960, 100), (960, 160)], 'color': 'green', 'dur': 0.4, 'hold': 1.0}])
d.save(out('2026/04/16-2.svg'))

# =====================================================================
# 2026/04/16-3  adoption: before/after workflow
# =====================================================================
d = Diagram(1100, 600, 'Workflow — before adoption, and from 2026-04-16')
d.group(40, 86, 1020, 130, 'Before')
before = [('Edit', 'IDE + autocomplete', 'muted'), ('./gradlew build', 'by hand, locally', 'muted'), ('git push', 'straight to the branch', 'muted'), ('Deploy workflow', 'no PR checks', 'muted')]
for i, (lab, sub, c) in enumerate(before):
    x = 60 + i * 250
    d.box(x, 120, 230, 60, lab, [sub], color=c, label_size=13, sub_size=11)
    if i: d.arrow([(x - 20, 150), (x, 150)], color='muted')
d.group(40, 240, 1020, 330, 'After — hooks, skills, PR workflow and memory as one package')
after = [('Issue #N', 'per-module work queue', 'gray', None), ('Worktree branch', 'feature/<name>', 'gray', None), ('Agent edits', 'PostToolUse: ktlint', 'blue', 'claude'), ('End of turn', 'Stop: test + JaCoCo', 'blue', None),
         ('/commit', 'Conventional Commits', 'purple', None), ('git push', 'PreToolUse: blocks under 90% coverage', 'amber', None), ('/pr → PR CI', 'pr-ci.yml, the first PR gate', 'green', 'github'), ('Squash merge', 'release-please sets the version', 'green', None)]
for i, (lab, sub, c, lg) in enumerate(after):
    col, row = i % 4, i // 4
    x, y = 60 + col * 250, 280 + row * 110
    d.box(x, y, 230, 70, color=c)
    if lg: icon(d, lg, x + 12, y + 21, 28)
    d.text(x + 115 + (12 if lg else 0), y + 28, lab, size=13, weight=700); d.text(x + 115 + (12 if lg else 0), y + 50, sub, size=10, weight=600, color=MUTED)
    if col: d.arrow([(x - 20, y + 35), (x, y + 35)], color=c)
d.arrow([(925, 350), (925, 365), (175, 365), (175, 390)], color='gray')
d.box(60, 510, 980, 44, color='muted'); d.text(550, 528, 'Blue = hooks · purple = skills · green = GitHub · amber = gates.  Decisions go in memory/MEMORY.md.  Direct pushes ended that day', size=11, weight=600)
d.flow([{'path': [(290, 315), (310, 315)], 'color': 'gray', 'dur': 0.3}, {'path': [(540, 315), (560, 315)], 'color': 'blue', 'dur': 0.3}, {'path': [(790, 315), (810, 315)], 'color': 'blue', 'dur': 0.3},
        {'path': [(925, 350), (925, 365), (175, 365), (175, 390)], 'color': 'gray', 'dur': 0.8},
        {'path': [(290, 425), (310, 425)], 'color': 'purple', 'dur': 0.3}, {'path': [(540, 425), (560, 425)], 'color': 'amber', 'dur': 0.3, 'hold': 0.3}, {'path': [(790, 425), (810, 425)], 'color': 'green', 'dur': 0.3, 'hold': 1.0}])
d.save(out('2026/04/16-3.svg'))

# =====================================================================
# 2026/05/07-1  harness: the fold
# =====================================================================
d = Diagram(1100, 560, '2026-05-07 — two harnesses from two repos fold into one root')
for i, (name, c) in enumerate((('backend repo', 'blue'), ('frontend repo', 'purple'))):
    y = 100 + i * 200
    d.group(40, y, 300, 170, name, color=c)
    for j, item in enumerate(('.claude/ (hooks, commands, agents)', '.github/workflows/', 'memory/MEMORY.md', 'CLAUDE.md')):
        d.box(60, y + 30 + j * 34, 260, 28, color=c); d.text(190, y + 48 + j * 34, item, size=11, weight=600, mono=True)
d.box(390, 225, 180, 80, 'git-filter-repo', ['backend history', 'moved under backend/'], color='gray', label_size=13, sub_size=10)
d.arrow([(340, 185), (390, 250)], color='blue'); d.arrow([(340, 385), (390, 280)], color='purple')
d.group(620, 100, 440, 370, 'Monorepo root')
d.box(640, 130, 400, 44, '.claude/ — 12 agents · 15 commands · 4 hooks · 9 pattern docs', color='green', label_size=11)
d.box(640, 184, 400, 44, '.claude/stacks.json — single source of truth for stacks', color='green', label_size=12)
d.box(640, 238, 400, 44, '7 workflows in .github/workflows/ + paths-filter', color='green', label_size=12)
d.box(640, 292, 400, 44, 'memory/MEMORY.md (4 entries today, Why · How to apply)', color='green', label_size=12)
d.box(640, 346, 400, 44, 'CLAUDE.md: root 76 lines → backend/ 275 · frontend/ 73', color='green', label_size=12)
d.box(640, 400, 195, 44, 'backend/.claude/ ✕', color='red', dashed=True, label_size=12); d.box(845, 400, 195, 44, 'frontend/.claude/ ✕', color='red', dashed=True, label_size=12)
d.arrow([(570, 265), (620, 265)], color='gray')
d.text(550, 500, 'Claude Code reads only the root settings.json and GitHub only sees the root .github/ — the subfolder hooks and workflows never ran', size=12, weight=700, color=G['red'])
d.text(550, 526, 'Deleted 8,049 lines of duplicated starter files · the real reason for the merge was API type drift, not the harness', size=11, weight=600, color=MUTED)
d.flow([{'path': [(340, 185), (390, 250)], 'color': 'blue', 'dur': 0.5}, {'path': [(340, 385), (390, 280)], 'color': 'purple', 'dur': 0.5}, {'path': [(570, 265), (620, 265)], 'color': 'green', 'dur': 0.4, 'hold': 1.0}])
d.save(out('2026/05/07-1.svg'))

# =====================================================================
# 2026/05/07-2  harness: read / follow / enforce
# =====================================================================
d = Diagram(1100, 620, 'What the agent reads, what it follows, what stops it — three layers')
logo_box(d, 40, 96, 1020, 56, 'claude', 'Claude Code session', 'SessionStart injects context; hooks watch every tool call', color='gray')
d.group(40, 180, 330, 300, 'Reads (context)', color='blue')
for i, (lab, sub) in enumerate((('3 layers of CLAUDE.md', 'root index → stack rules, loaded cumulatively'), ('.claude/skills/*.md', 'pattern docs — kotlin · nextjs · db …'), ('memory/MEMORY.md', 'decisions and the "why", dated entries'), ('docs/specs/*', 'PRD + per-role prompts'))):
    d.box(60, 210 + i * 64, 290, 54, lab, [sub], color='blue', label_size=12, sub_size=10)
d.group(390, 180, 320, 300, 'Follows (skills)', color='purple')
for i, (lab, sub) in enumerate((('/start → /plan → /new', 'worktree · PRD · generator agents'), ('/test → /review', 'test generation · review'), ('/commit → /pr → /merge', 'Conventional Commits · security review gate'), ('/memory · /rule', 'add memory · register a rule after a mistake'))):
    d.box(410, 210 + i * 64, 280, 54, lab, [sub], color='purple', label_size=12, sub_size=10)
d.group(730, 180, 330, 300, 'Stops it (enforcement)', color='amber')
for i, (lab, sub, c) in enumerate((('safety-guard.sh', 'PreToolUse(Bash) · exit 2', 'amber'), ('pre-push.sh', '90% coverage · blocks direct push to main', 'amber'), ('post-edit-lint.sh · Stop tests', 'PostToolUse · Stop', 'amber'), ('10 CI workflows', 'backend · frontend · api-contract · release', 'green'))):
    d.box(750, 210 + i * 64, 290, 54, lab, [sub], color=c, label_size=12, sub_size=10)
d.box(390, 500, 320, 44, '.claude/stacks.json', ['hooks and skills read it to branch by stack'], color='green', label_size=12, sub_size=10)
d.arrow([(390, 522), (300, 522), (300, 480)], color='green', head=False, width=1); d.arrow([(710, 522), (800, 522), (800, 480)], color='green', head=False, width=1)
d.text(550, 580, 'Mistake → rule: once the agent\'s marker comments showed up on screen, a "never" rule went to the top of the root CLAUDE.md (May 14)', size=11, weight=600, color=MUTED)
d.flow([{'path': [(550, 152), (550, 180)], 'color': 'gray', 'dur': 0.3}, {'path': [(390, 522), (300, 522), (300, 480)], 'color': 'green', 'dur': 0.5}, {'path': [(710, 522), (800, 522), (800, 480)], 'color': 'green', 'dur': 0.5, 'hold': 1.0}])
d.save(out('2026/05/07-2.svg'))

# =====================================================================
# 2026/05/07-3  harness: API contract loop
# =====================================================================
d = Diagram(1100, 560, 'One source for the API contract — Kotlin controllers to TypeScript types, with CI regenerating both')
s = [('Kotlin controllers · DTOs', 'backend/', 'blue'), ('./gradlew generateOpenApi', 'springdoc, boots the app with the H2 profile', 'blue'), ('backend/openapi/*.json', '4 modules', 'gray'), ('Normalize', 'merge descriptions · sort keys (tomorrow)', 'amber'), ('openapi-typescript', 'npm run gen:api', 'purple'), ('frontend/types/api/*.gen.ts', 'imported by the frontend', 'purple')]
for i, (lab, sub, c) in enumerate(s):
    col, row = i % 3, i // 3
    x, y = 60 + col * 340, 110 + row * 120
    d.box(x, y, 300, 70, lab, [sub], color=c, label_size=13, sub_size=10)
    if col: d.arrow([(x - 40, y + 35), (x, y + 35)], color=c)
d.arrow([(1020, 180), (1020, 200), (210, 200), (210, 230)], color='gray')
d.box(60, 360, 1000, 60, 'CI api-contract.yml — every PR regenerates both sides and runs git diff --exit-code against the committed output', ['A PR that commits only one side fails. When the agent changes a controller, regenerating the types is part of the same task'], color='green', label_size=13, sub_size=11)
d.text(550, 460, 'The cost, within a day: springdoc output is non-deterministic — key order changes on the same code, causing false diffs', size=12, weight=700, color=G['amber'])
d.text(550, 486, 'The real reason for the merge — force backend controller changes to show up in frontend types immediately', size=11, weight=600, color=MUTED)
d.flow([{'path': [(360, 145), (400, 145)], 'color': 'blue', 'dur': 0.4}, {'path': [(700, 145), (740, 145)], 'color': 'blue', 'dur': 0.4},
        {'path': [(1020, 180), (1020, 200), (210, 200), (210, 230)], 'color': 'gray', 'dur': 0.9},
        {'path': [(360, 265), (400, 265)], 'color': 'amber', 'dur': 0.4}, {'path': [(700, 265), (740, 265)], 'color': 'purple', 'dur': 0.4},
        {'path': [(900, 300), (900, 360)], 'color': 'green', 'dur': 0.4, 'hold': 1.0}])
d.save(out('2026/05/07-3.svg'))
print('batch3 all ok')

# =====================================================================
# 2026/10/28-1  fastlane: where secrets go
# =====================================================================
BRAND.update({'apple': '#1f2937', 'googleplay': '#01875F', 'fastlane': '#00F200', 'githubactions': '#2088FF'})
d = Diagram(1100, 520, 'How the materials flow — secrets in a main-only Environment, lanes authenticate to the stores with API keys')
d.group(40, 90, 260, 330, 'Secrets (base64)', color='amber')
for i, s in enumerate(('ASC_KEY_ID · ISSUER_ID', 'ASC_KEY_P8_BASE64', 'APPLE_DIST_CERT_P12 · password', 'PLAY_SERVICE_ACCOUNT_JSON', 'ANDROID_UPLOAD_KEYSTORE + 3 more')):
    d.box(60, 120 + i * 58, 220, 44, color='amber'); d.text(170, 147 + i * 58, s, size=10, weight=700, mono=True)
logo_box(d, 340, 150, 240, 70, 'githubactions', 'Environment: store', 'main branch only', color='blue')
logo_box(d, 340, 270, 240, 70, 'githubactions', 'Workflow job', 'passes env; .p12 in RUNNER_TEMP', color='blue')
d.arrow([(300, 255), (340, 185)], color='amber'); d.arrow([(460, 220), (460, 270)], color='blue')
logo_box(d, 620, 210, 200, 70, 'fastlane', 'bundle exec', 'fastlane 2.241.1, pinned', color='green')
d.arrow([(580, 305), (600, 305), (600, 245), (620, 245)], color='blue')
logo_box(d, 860, 130, 200, 64, 'apple', 'App Store Connect', 'API key · no 2FA', color='gray')
logo_box(d, 860, 300, 200, 64, 'googleplay', 'Google Play', 'service account JSON', color='gray')
d.arrow([(820, 235), (840, 235), (840, 162), (860, 162)], color='green'); d.arrow([(820, 255), (840, 255), (840, 332), (860, 332)], color='green')
d.note(40, 444, 1020, 56, ['Certificates live only in setup_ci\'s temporary keychain · profiles aren\'t kept as secrets but fetched on demand with the API key', 'No secrets → warn and skip the upload instead of failing · the first Play AAB is uploaded by hand in the console'], color='muted', size=12)
d.flow([{'path': [(300, 255), (340, 185)], 'color': 'amber', 'dur': 0.5}, {'path': [(460, 220), (460, 270)], 'color': 'blue', 'dur': 0.4},
        {'path': [(580, 305), (600, 305), (600, 245), (620, 245)], 'color': 'blue', 'dur': 0.5},
        {'path': [(820, 235), (840, 235), (840, 162), (860, 162)], 'color': 'green', 'dur': 0.5},
        {'path': [(820, 255), (840, 255), (840, 332), (860, 332)], 'color': 'green', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/10/28-1.svg'))

# =====================================================================
# 2026/10/28-2  fastlane: three lanes + where the first run broke
# =====================================================================
d = Diagram(1100, 600, 'Three lanes — upload and version prep are automatic, a person submits for review. Red numbers: where run #1 broke')
lanes = [('apple', 'ios release', [('dotenv', '.env lookup', 1), ('setup_ci', 'temp keychain + cert', None), ('get_provisioning_profile', 'fetched with API key', None), ('build_app', 'Automatic → manual signing', 5), ('upload_to_testflight', 'waits for processing', None), ('deliver + attach build', 'submit_for_review: false', None)]),
         ('googleplay', 'android release', [('Gradle signing', 'upload keystore', None), ('upload_to_play_store', 'track = PLAY_TRACK', None), ('release_status', 'draft', None)]),
         ('apple', 'mac profile · release', [('setup_ci + cert', 'sigh picks by cert', 3), ('get_provisioning_profile', 'macos · filename check', 2), ('electron-builder', 'mas signing · pkg', 4), ('upload_to_testflight', 'app_platform: osx', None), ('deliver + attach build', 'a person submits', None)])]
for r, (lg, name, steps) in enumerate(lanes):
    y = 96 + r * 150
    logo_box(d, 40, y, 180, 60, lg, name, None, color='gray', size=22)
    for i, (lab, sub, bad) in enumerate(steps):
        x = 240 + i * 140
        d.box(x, y, 128, 60, lab, [sub], color='red' if bad else 'blue', label_size=11, sub_size=9)
        if bad: d.box(x + 104, y - 10, 24, 22, color='red', fill='#dc2626'); d.text(x + 116, y + 5, str(bad), size=11, weight=700, color='#ffffff')
        d.arrow([(x - 12, y + 30), (x, y + 30)], color='muted', width=1)
d.box(240, 520, 820, 50, 'A person: "Add for Review" in App Store Connect · "Start rollout" in the Play Console', color='amber', label_size=13)
d.text(130, 545, 'Automation ends here →', size=12, weight=700, color=G['amber'])
d.flow([{'path': [(228, 126), (1080, 126)], 'color': 'blue', 'dur': 1.6}, {'path': [(228, 276), (660, 276)], 'color': 'green', 'dur': 0.9},
        {'path': [(228, 426), (940, 426)], 'color': 'purple', 'dur': 1.4, 'hold': 0.8}])
d.save(out('2026/10/28-2.svg'))
print('fastlane ok')
