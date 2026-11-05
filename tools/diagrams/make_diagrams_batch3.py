"""시리즈 "AI와 일하기" 5편의 다이어그램 (2026-11-05 작성).
실행: python3 tools/diagrams/make_diagrams_batch3.py "$PWD"
로고는 assets/img/logos/*.svg (Simple Icons, CC0) 의 path 를 인라인으로 심는다.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from diag import Diagram, INK, MUTED

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

G = {'gray': '#1f2937', 'muted': '#6b7280', 'blue': '#2563eb', 'green': '#059669', 'red': '#dc2626', 'amber': '#d97706', 'purple': '#7c3aed'}
BRAND = {'claude': '#D97757', 'anthropic': '#191919', 'openai': '#412991', 'githubcopilot': '#1f2937', 'cursor': '#1f2937', 'github': '#181717'}

_logo_cache = {}
def logo_path(name):
    if name not in _logo_cache:
        s = open(os.path.join(ROOT, 'assets/img/logos', name + '.svg'), encoding='utf-8').read()
        _logo_cache[name] = re.search(r'<path d="([^"]+)"', s).group(1)
    return _logo_cache[name]

def icon(d, name, x, y, size=28, color=None):
    """Simple Icons 24x24 글리프를 (x, y) 왼쪽 위 기준 size 로 심는다."""
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
d = Diagram(1100, 520, '2026-06-23 오후의 PR 다섯 개 — 생성 몇 초 뒤 머지된 둘, CI 통과를 기다린 셋')
def tx(hhmm):
    h, m = hhmm.split(':'); t = int(h) * 60 + int(m)
    return 80 + (t - 15 * 60 - 40) * (960 / 115)
d.arrow([(80, 130), (1040, 130)], color='muted', head=True)
for lab in ('15:47', '16:00', '16:22', '16:48', '17:05', '17:29'):
    x = tx(lab); d.arrow([(x, 124), (x, 136)], color='muted', head=False, width=1); d.text(x, 115, lab, size=11, color=MUTED)
d.box(tx('16:22'), 150, tx('17:12') - tx('16:22'), 36, color='red'); d.text((tx('16:22') + tx('17:12')) / 2, 173, 'dev 빨간 구간 약 50분 (16:22:30 → 17:12:28)', size=12, weight=700, color=G['red'])
prs = [('15:47', '15:53', '#466 사이드바 셸 (1/N)', '제가 직접 · CI 통과 뒤 머지', 'green'),
       ('16:22', '16:22', '#470 전체 사이드바 통합 (60파일)', '에이전트 · 7초 뒤 머지 · CI 뒤늦게 실패', 'red'),
       ('16:48', '16:48', '#472 견적·수주·수금 모달 (15파일)', '에이전트 · 5초 뒤 머지 · CI 실패', 'red'),
       ('17:05', '17:12', '#473 깨진 테스트 12개 정리', '제가 직접 · CI 통과 뒤 머지 → dev 복구', 'green'),
       ('17:21', '17:29', '#475 미사용 Navbar 제거', '제가 직접 · CI 통과 뒤 머지', 'green')]
for i, (a, b, lab, sub, c) in enumerate(prs):
    y = 210 + i * 56
    x1, x2 = tx(a), max(tx(b), tx(a) + 6)
    d.arrow([(x1, y + 14), (x2, y + 14)], color=c, width=6, head=False)
    left = i in (0, 4)
    lx = x1 - 8 if left else x2 + 10
    d.text(lx, y + 10, lab, size=12, weight=700, anchor='end' if left else 'start')
    d.text(lx, y + 26, sub, size=11, weight=600, color=G[c] if c == 'red' else MUTED, anchor='end' if left else 'start')
d.text(560, 507, '머지 14초 전·68초 뒤에 제가 다른 PR(#469, #471)을 머지하고 있었다 — 사람이 다른 걸 보는 사이에 에이전트가 끼어든 모양', size=11, weight=600, color=MUTED)
d.flow([{'path': [(tx('16:22'), 224), (tx('16:22') + 6, 224)], 'color': 'red', 'dur': 0.3, 'hold': 0.5},
        {'path': [(tx('16:48'), 280), (tx('16:48') + 6, 280)], 'color': 'red', 'dur': 0.3, 'hold': 0.5},
        {'path': [(tx('17:05'), 392), (tx('17:12'), 392)], 'color': 'green', 'dur': 0.8, 'hold': 0.8}])
d.save(out('2026/06/23-1.svg'))

# =====================================================================
# 2026/06/23-2  subagent: delegation chain
# =====================================================================
d = Diagram(1100, 640, '권한의 경계가 없다 — 서브에이전트 ⊂ 메인 세션 ⊂ 사용자')
d.group(40, 86, 1020, 100, '사용자 터미널')
logo_box(d, 60, 112, 300, 56, 'github', 'gh auth: 제 계정', 'keyring · scope repo, workflow', color='gray')
d.box(390, 112, 650, 56, color='muted'); d.text(715, 136, '셸 환경 · ~/.config/gh · .claude/settings.json · 훅 — 아래로 전부 상속된다', size=12, weight=600); d.text(715, 156, '별도 자격증명 없음', size=11, color=MUTED)
d.group(40, 210, 1020, 170, 'Claude Code 메인 세션 (오케스트레이터)')
logo_box(d, 60, 240, 300, 56, 'claude', '메인 세션', '다른 PR(#469, #471)을 보는 중', color='gray')
d.box(390, 240, 200, 56, 'permissions', ['allow: Bash(git *) …', 'gh 는 미기재'], color='amber', label_size=12, sub_size=10)
d.box(610, 240, 200, 56, 'safety-guard.sh', ['exit 2 · rm -rf · SQL · main 강제푸시만'], color='amber', label_size=12, sub_size=10)
d.box(830, 240, 210, 56, 'pre-push.sh', ['"푸시 차단" 출력, exit 1 = 비차단'], color='red', label_size=12, sub_size=10)
d.text(550, 330, 'Agent(subagent_type="nextjs-modifier", prompt="48개 파일에서 <Navbar/> 제거 …")', size=12, weight=600, mono=True)
d.arrow([(210, 296), (210, 320), (210, 404)], color='gray')
d.group(40, 404, 1020, 216, '서브에이전트 nextjs-modifier')
d.box(60, 434, 300, 56, 'tools: (없음)', ['→ 메인의 Bash·Edit·Write 전부 상속'], color='red', label_size=13, sub_size=11)
steps = [('Edit ×48', '의도된 범위', 'green'), ('git push -u origin …', '"차단" 메시지, 그러나 exit 1', 'amber'), ('gh pr create', 'Summary/Changes/Test plan, jest 미실행', 'red'), ('gh pr merge --squash', 'dev 보호 없음 → 7초 뒤 머지', 'red')]
for i, (lab, sub, c) in enumerate(steps):
    x = 390 + i * 165
    d.box(x, 434, 150, 56, lab, [sub], color=c, label_size=11, sub_size=9)
    if i: d.arrow([(x - 15, 462), (x, 462)], color=c)
d.text(550, 530, 'GitHub: author = mergedBy = 제 계정 · Co-authored-by: Claude — 제가 세션에서 만든 PR과 구분 불가', size=12, weight=700, color=G['red'])
d.text(550, 556, '유일한 지문: 기본 PR 템플릿, 체크되지 않은 jest 항목, 생성→머지 수 초', size=11, weight=600, color=MUTED)
d.flow([{'path': [(210, 296), (210, 404)], 'color': 'gray', 'dur': 0.5},
        {'path': [(360, 462), (390, 462)], 'color': 'green', 'dur': 0.3},
        {'path': [(540, 462), (555, 462)], 'color': 'amber', 'dur': 0.2}, {'path': [(705, 462), (720, 462)], 'color': 'red', 'dur': 0.2},
        {'path': [(870, 462), (885, 462)], 'color': 'red', 'dur': 0.2, 'hold': 1.0}])
d.save(out('2026/06/23-2.svg'))

# =====================================================================
# 2026/06/23-3  subagent: guard layers
# =====================================================================
d = Diagram(1100, 600, '가드 레이어 (2026-06-30 기준) — 사건 경로(push → pr create → pr merge)를 하드 차단하는 층이 없다')
layers = [('편집', 'worktree-guard.sh', 'PreToolUse(Edit|Write) · exit 2', '허브에서 소스 편집 차단 (06-18)', 'green', '편집은 worktree 안 → 해당 없음'),
          ('명령', 'safety-guard.sh', 'PreToolUse(Bash) · exit 2', 'rm -rf · 파괴적 SQL · main 강제 푸시 (05-07)', 'green', 'dev · gh 는 비대상'),
          ('푸시', 'pre-push.sh', 'PreToolUse(Bash) · exit 1', '테스트 + 커버리지 90% "차단" (05-07)', 'red', '✗ 메시지만, 실제로 통과'),
          ('의도', '위임 프롬프트 규칙', '"git·gh·PR·머지 금지, 편집+tsc/jest 만"', '사건 당일 신설 (06-23)', 'amber', '프롬프트가 지켜지는 한'),
          ('도구', 'agents tools:', 'modifier/generator 9개 미지정', '= 전부 상속 (지금도)', 'red', '✗ Bash 통째로'),
          ('서버', 'dev 브랜치 보호', '없음', 'CI 는 required check 아님 (지금도)', 'red', '✗ 7초 머지 가능')]
for i, (zone, name, how, when, c, verdict) in enumerate(layers):
    y = 92 + i * 76
    d.box(40, y, 90, 60, zone, color='muted', label_size=14)
    d.box(150, y, 300, 60, name, [how], color=c, label_size=13, sub_size=10)
    d.box(470, y, 300, 60, color='gray'); d.text(620, y + 35, when, size=11, weight=600)
    d.box(790, y, 270, 60, color=c); d.text(925, y + 35, verdict, size=12, weight=700, color=G[c])
d.text(550, 572, '가드는 위협 모델별로 따로 있어야 한다 — 인덱스 꼬임을 막는 가드는 에이전트의 머지를 막지 않는다', size=13, weight=700)
d.flow([{'path': [(120, 122 + i * 76), (150, 122 + i * 76)], 'color': layers[i][4], 'dur': 0.3, 'hold': 0.2} for i in range(6)])
d.save(out('2026/06/23-3.svg'))

# =====================================================================
# 2026/10/08-1  AI product: two arcs timeline
# =====================================================================
d = Diagram(1100, 520, '같은 Claude API 를 두 번 넣었다 — 채팅은 5일 만에 뺐고, 문서 판정기는 6일 만에 비용을 재설계했다')
d.arrow([(80, 150), (1040, 150)], color='muted')
def mx(month, day):
    days = {5: 0, 6: 31, 7: 61, 8: 92, 9: 123, 10: 153}[month] + day
    return 80 + (days - 20) * (960 / 150)
for lab, m, dd in (('5월', 5, 27), ('6월', 6, 15), ('7월', 7, 15), ('8월', 8, 15), ('9월', 9, 15), ('10월', 10, 8)):
    x = mx(m, dd); d.text(x, 138, lab, size=11, color=MUTED)
ev = [((5, 27), '05-27 채팅 어시스턴트 추가', ['Claude Sonnet · SSE · 토큰 한도', '테이블 4 · 엔드포인트 10'], 'amber', 180),
      ((6, 1), '06-01 전면 제거', ['105개 파일 · v1.0.0 리셋', '매뉴얼은 13줄 플레이스홀더'], 'red', 300),
      ((10, 2), '10-02 문서 판정기 추가', ['구조화 출력 · 하루 100건', 'Jev 선별 (제외 0.1)'], 'green', 180),
      ((10, 8), '10-08 비용 재설계', ['실측 $0.23/건 · $37/일', 'SCREENED_PIPE · 제외 0.3 · 목표 $10'], 'blue', 300)]
for (m, dd), lab, sub, c, y in ev:
    x = mx(m, dd)
    d.arrow([(x, 150), (x, y)], color=c, head=False, dashed=True, width=1)
    bx = min(max(x - 130, 40), 1060 - 260)
    d.box(bx, y, 260, 76, lab, sub, color=c, label_size=13, sub_size=11)
icon(d, 'claude', mx(5, 27) - 14, 118 - 30, 24); icon(d, 'claude', mx(10, 2) - 14, 118 - 30, 24)
d.box(380, 230, 360, 120, color='muted'); d.lines(560, 258, ['4개월의 공백', '같은 API, 다른 질문:', '"무엇이든 물어보세요" → "표의 빈 칸 4개"', '"사용자 × 토큰" → "문서 1건 = 호출 1회"'], size=12, weight=600, gap=22)
d.text(550, 430, '바뀐 것은 모델이 아니라 문제 정의 · 비용 단위 · 실패 처리였다', size=14, weight=700)
d.text(550, 456, '(출시 전 플랫폼 — prd 는 팀이 운영하는 운영 유사 환경, 공고 풀은 실제 공공 데이터)', size=11, weight=600, color=MUTED)
d.flow([{'path': [(mx(5, 27), 150), (mx(6, 1), 150)], 'color': 'red', 'dur': 0.6, 'hold': 0.6},
        {'path': [(mx(6, 1), 150), (mx(10, 2), 150)], 'color': 'muted', 'dur': 1.4},
        {'path': [(mx(10, 2), 150), (mx(10, 8), 150)], 'color': 'blue', 'dur': 0.5, 'hold': 1.0}])
d.save(out('2026/10/08-1.svg'))

# =====================================================================
# 2026/10/08-2  AI product: cost bars + score bands
# =====================================================================
d = Diagram(1100, 560, '하루 Claude 비용과 Jev 점수 구간별 Claude YES 비율 — prd 407건 실측 (2026-10-08)')
d.group(40, 86, 480, 440, '하루 비용 (Claude 호출)')
base_y, scale = 470, 8.5
bars = [('실측 (10-08 이전)', 37, 'red', '약 160건 × $0.23', False), ('목표 (#1753 설계)', 10, 'blue', '게이트 뒤 Claude 구간만', True), ('예상 (자동 모델, 10-15 추기)', 5, 'green', 'Opus 는 저류 가능성 있을 때만', True)]
for i, (lab, v, c, sub, dashed) in enumerate(bars):
    x = 80 + i * 150
    h = v * scale
    d.box(x, base_y - h, 110, h, color=c, dashed=dashed)
    d.text(x + 55, base_y - h - 10, f'${v}', size=16, weight=700, color=G[c])
    d.text(x + 55, base_y + 18, lab, size=10, weight=700)
    d.text(x + 55, base_y + 34, sub, size=9, weight=600, color=MUTED)
d.arrow([(70, base_y), (510, base_y)], color='muted', head=False, width=1)
d.text(280, 110, '빗금 = 목표·예상 (실측 아님)', size=11, weight=600, color=MUTED)
d.group(560, 86, 500, 440, 'Jev 관로 점수 구간 → Claude 가 "관로 YES" 라고 한 비율')
bands = [('0.1 ~ 0.3', 2, '194건 중 4건', 'red', '→ SCREENED_OUT (Claude 없이 제외)'), ('0.3 ~ 0.7', None, 'Claude 가 읽는 구간', 'amber', '→ Claude 로'), ('≥ 0.7', 67, '', 'green', '→ SCREENED_PIPE (Claude 없이 "가능성 높음")')]
for i, (lab, v, n, c, act) in enumerate(bands):
    x = 600 + i * 150
    if v is None:
        d.box(x, 180, 110, 290, color=c, dashed=True); d.text(x + 55, 320, '?', size=28, weight=700, color=G[c])
    else:
        h = v * 4.3; d.box(x, base_y - h, 110, h, color=c); d.text(x + 55, base_y - h - 10, f'{v}%', size=16, weight=700, color=G[c])
    d.text(x + 55, base_y + 18, lab, size=11, weight=700); d.text(x + 55, base_y + 34, n, size=9, weight=600, color=MUTED)
    d.text(x + 55, 130 + (i % 2) * 16, act, size=9, weight=700, color=G[c])
d.arrow([(590, base_y), (1050, base_y)], color='muted', head=False, width=1)
d.flow([{'path': [(135, base_y - 37 * scale), (285, base_y - 10 * scale)], 'color': 'blue', 'dur': 0.8, 'hold': 0.4},
        {'path': [(285, base_y - 10 * scale), (435, base_y - 5 * scale)], 'color': 'green', 'dur': 0.6, 'hold': 1.0}])
d.save(out('2026/10/08-2.svg'))

# =====================================================================
# 2026/10/08-3  AI product: pipeline with gate
# =====================================================================
d = Diagram(1100, 640, '매일 05:30 — 후보 선정, 첨부 추출, 판정 모델 게이트, Claude 분석, 계산기, 빈 칸 반영')
s1 = d.box(40, 100, 180, 64, '① 후보 선정', ['180일 내 설계용역·공사입찰', '하루 한도 100건'], color='gray', label_size=13, sub_size=10)
s2 = d.box(260, 100, 180, 64, '② 첨부 추출', ['PDF·HWP·DOCX → 텍스트', '과업지시서 > 공고문 > 기타'], color='gray', label_size=13, sub_size=10)
s3 = d.box(480, 100, 200, 64, '③ Jev 채점 (게이트)', ['25,000자 구간마다 질문 2개', '$0.042/1M 토큰 · 0.3~0.5초'], color='purple', label_size=13, sub_size=10)
d.arrow([(220, 132), (260, 132)], color='gray'); d.arrow([(440, 132), (480, 132)], color='gray')
# branches
b1 = d.box(720, 90, 340, 44, '저류 낱말 있음 OR 저류 ≥ 0.3  → Claude', color='green', label_size=12)
b2 = d.box(720, 144, 340, 44, '관로 ≥ 0.7  → SCREENED_PIPE  (Claude 없음, 칸은 안 채움)', color='amber', label_size=11)
b3 = d.box(720, 198, 340, 44, '관로 < 0.3 · 전부 읽음 · 제품명 없음 → SCREENED_OUT', color='red', label_size=11)
b4 = d.box(720, 252, 340, 44, '그 밖 (0.3 ≤ 관로 < 0.7)  → Claude', color='green', label_size=12)
for y in (112, 166, 220, 274): d.arrow([(680, 132), (700, 132), (700, y), (720, y)], color='muted', width=1)
# claude analysis
logo_box(d, 480, 340, 300, 70, 'claude', 'Claude 분석 (Opus)', '구조화 출력 · effort high · 10분 타임아웃 · $0.23/건', color='green')
d.arrow([(890, 134), (890, 140)], color='green', head=False, width=1)
d.arrow([(1060, 112), (1080, 112), (1080, 375), (780, 375)], color='green')
d.arrow([(1060, 274), (1075, 274), (1075, 370)], color='green', head=False)
c1 = d.box(40, 340, 200, 70, '설치 기준 계산기', ['결정론적 코드', '용량 계산은 LLM 이 안 한다'], color='blue', label_size=13, sub_size=10)
r = d.box(260, 340, 200, 70, 'Resolver', ['문서 값 우선, 없으면 계산기', '비어 있는 칸에만'], color='gray', label_size=13, sub_size=10)
d.arrow([(480, 375), (460, 375)], color='green'); d.arrow([(260, 375), (240, 375)], color='gray', head=False); d.arrow([(240, 375), (260, 375)], color='blue', head=False)
d.box(40, 440, 420, 56, '영업 대상 표', ['저류 시설 · 관로 · 적용 검토 · 예상 용량 — "AI 문서 분석(잠정)"'], color='green', label_size=13, sub_size=11)
d.arrow([(360, 410), (360, 440)], color='gray')
d.box(500, 440, 560, 56, color='muted'); d.lines(780, 460, ['Jev 장애 → 선별 없이 Claude 로 (fail-open) · Claude 계정 오류 → 실행 전체 중단 (fail-stop)', '429/529 → 60초 뒤 재시도 · 413/거절/토큰 초과 → 그 건만'], size=11, weight=600, gap=18)
d.text(550, 530, '출력은 enum · 숫자 · 인용뿐 — 문서에 지시문이 섞여 있어도 점수 밖으로 새어 나올 자리가 없다', size=12, weight=700, color=G['purple'])
d.text(550, 556, '"선별은 비용을 줄이는 수단이지 분석의 전제가 아니다"', size=12, weight=600, color=MUTED)
d.flow([{'path': [(220, 132), (260, 132)], 'color': 'gray', 'dur': 0.4}, {'path': [(440, 132), (480, 132)], 'color': 'gray', 'dur': 0.4},
        {'path': [(680, 132), (700, 132), (700, 274), (720, 274)], 'color': 'purple', 'dur': 0.6},
        {'path': [(1060, 274), (1075, 274), (1075, 375), (780, 375)], 'color': 'green', 'dur': 0.9},
        {'path': [(480, 375), (460, 375)], 'color': 'green', 'dur': 0.2}, {'path': [(360, 410), (360, 440)], 'color': 'gray', 'dur': 0.3, 'hold': 1.0}])
d.save(out('2026/10/08-3.svg'))

# =====================================================================
# 2026/10/27-3  dual harness: one harness, two agents
# =====================================================================
d = Diagram(1100, 620, '하네스 한 벌, 에이전트 둘 — 손으로 두 벌 고치는 파일은 없다')
d.group(40, 86, 300, 470, 'Claude Code 쪽')
logo_box(d, 60, 116, 260, 56, 'claude', 'Claude Code', '≥ 2.1.277', color='gray')
d.box(60, 192, 260, 56, '.claude/settings.json', ['훅 배선 · permissions'], color='blue', label_size=12, sub_size=10)
d.box(60, 268, 260, 56, '.claude/agents/*.md', ['서브에이전트 15개 — 원본'], color='blue', label_size=12, sub_size=10)
d.box(60, 344, 260, 56, '.claude/skills → 심볼릭 링크', ['../.agents/skills'], color='blue', label_size=12, sub_size=10)
d.box(60, 420, 260, 56, 'PreToolUse(Edit|Write)', ['worktree-guard · post-edit-lint'], color='blue', label_size=12, sub_size=10)
d.group(400, 86, 300, 470, '공용 (원본은 여기)')
d.box(420, 116, 260, 56, 'AGENTS.md', ['루트 + 스택 5개, 파일당 ≤ 300줄'], color='green', label_size=13, sub_size=10)
d.box(420, 192, 260, 56, '.agents/skills/ (32)', ['부수 효과 9개는 모델 호출 금지'], color='green', label_size=13, sub_size=10)
d.box(420, 268, 260, 56, '.claude/hooks/*.sh', ['판정 스크립트 — 한 벌'], color='green', label_size=13, sub_size=10)
d.box(420, 344, 260, 56, '.githooks/ pre-commit · pre-push', ['게이트: 어느 도구든, 터미널도'], color='green', label_size=13, sub_size=10)
d.box(420, 420, 260, 56, 'memory/ · docs/', ['저장소가 원본'], color='green', label_size=13, sub_size=10)
d.group(760, 86, 300, 470, 'Codex 쪽')
logo_box(d, 780, 116, 260, 56, 'openai', 'Codex', '0.164.0', color='gray')
d.box(780, 192, 260, 56, '.codex/hooks.json', ['같은 .claude/hooks/*.sh 를 부른다'], color='purple', label_size=12, sub_size=10)
d.box(780, 268, 260, 56, '.codex/agents/*.toml', ['생성물 — gen-codex-agents.py'], color='purple', label_size=12, sub_size=10)
d.box(780, 344, 260, 56, '$start = /start', ['.agents/skills 를 직접 읽는다'], color='purple', label_size=12, sub_size=10)
d.box(780, 420, 260, 56, 'PreToolUse(apply_patch)', ['codex-adapter.sh → 같은 가드'], color='purple', label_size=12, sub_size=10)
d.arrow([(320, 372), (420, 220)], color='blue', dashed=True, label='symlink', label_dy=-6, label_size=10)
d.arrow([(320, 448), (420, 296)], color='blue', dashed=True)
d.arrow([(680, 220), (780, 372)], color='purple', dashed=True, label='읽기', label_dy=-6, label_size=10)
d.arrow([(680, 296), (780, 448)], color='purple', dashed=True, label='exec', label_dy=-6, label_size=10)
d.arrow([(320, 310), (380, 310), (380, 334), (720, 334), (720, 310), (780, 310)], color='purple', dashed=True)
d.lines(730, 268, ['생성', 'pre-commit 검사'], size=9, weight=700, color=G['purple'], gap=12)
d.text(550, 586, '게이트 = git 훅 · 스킬 = .agents/skills · 지침 = AGENTS.md · 리뷰 = 반대편 모델 — 한쪽 구독이 끊겨도 다른 쪽 하나로 전부 돈다', size=12, weight=700)
d.flow([{'path': [(320, 372), (420, 220)], 'color': 'blue', 'dur': 0.6}, {'path': [(680, 220), (780, 372)], 'color': 'purple', 'dur': 0.6},
        {'path': [(320, 448), (420, 296)], 'color': 'blue', 'dur': 0.6}, {'path': [(680, 296), (780, 448)], 'color': 'purple', 'dur': 0.6},
        {'path': [(320, 310), (380, 310), (380, 334), (720, 334), (720, 310), (780, 310)], 'color': 'purple', 'dur': 1.2, 'hold': 0.8}])
d.save(out('2026/10/27-3.svg'))

# =====================================================================
# 2026/10/27-4  dual harness: /pr cross-review flow
# =====================================================================
d = Diagram(1100, 600, '/pr 의 교차 리뷰 — 반대편 모델이 보고, 못 보면 exit 3 으로 자체 리뷰')
d.box(40, 110, 140, 56, '/pr', ['worktree 에서'], color='gray', label_size=14, sub_size=10)
d.box(220, 110, 220, 56, '작업 도구 감지', ['CLAUDECODE ? → 리뷰어 codex', 'CODEX_THREAD_ID ? → claude'], color='gray', label_size=12, sub_size=10)
d.box(480, 110, 200, 56, '깊이', ['마이그레이션·인증·권한·결제·', '훅 경로면 high, 아니면 medium'], color='amber', label_size=12, sub_size=10)
d.arrow([(180, 138), (220, 138)], color='gray'); d.arrow([(440, 138), (480, 138)], color='gray')
logo_box(d, 300, 230, 260, 70, 'openai', 'codex review', 'read-only 샌드박스 · effort = 깊이', color='purple')
logo_box(d, 600, 230, 300, 70, 'claude', 'claude -p --tools Read,Grep,Glob', '셸 없음 · diff 는 파일로 · opus/sonnet', color='blue')
d.arrow([(330, 166), (430, 230)], color='purple', label='Claude 안에서 작업 중', label_dy=-6, label_size=10)
d.arrow([(640, 166), (700, 230)], color='blue', label='Codex 안에서 작업 중', label_dy=-6, label_size=10)
d.box(40, 350, 300, 70, 'exit 0', ['VERDICT: PASS | REVIEW | BLOCK', 'Critical → BLOCK, High → REVIEW'], color='green', label_size=13, sub_size=10)
d.box(380, 350, 340, 70, 'exit 3 — 리뷰어를 쓸 수 없음', ['미설치 · 한도 · 로그인 · 빈 출력', '→ 막지 않는다. 지금 도구의 리뷰어로 대신'], color='amber', label_size=13, sub_size=10)
d.box(760, 350, 300, 70, 'exit 1', ['그 밖의 오류 → 메시지 보고 고치거나 3처럼'], color='red', label_size=13, sub_size=10)
for x1 in (430, 750):
    d.arrow([(x1, 300), (190, 350)], color='green', width=1); d.arrow([(x1, 300), (550, 350)], color='amber', width=1); d.arrow([(x1, 300), (910, 350)], color='red', width=1)
d.box(40, 460, 1020, 56, color='muted'); d.text(550, 482, 'PR 본문 "## Review": 리뷰어 · 판정 · 고친 것 · 안 고친 것(이유)  →  CI 전부 통과를 직접 기다린 뒤 --match-head-commit 으로 squash 머지', size=12, weight=600); d.text(550, 504, '"같은 모델은 자기 실수를 잘 못 본다" — 보안 리뷰와 병렬로 돈다', size=11, weight=600, color=MUTED)
d.text(550, 560, '이 PR 자체가 이 스크립트로 리뷰됐다 (Codex 1회, Claude 2회) — 셸을 뺄 것, 오탐, 무한 루프를 잡아냈다', size=12, weight=700, color=G['purple'])
d.flow([{'path': [(180, 138), (220, 138)], 'color': 'gray', 'dur': 0.3}, {'path': [(440, 138), (480, 138)], 'color': 'gray', 'dur': 0.3},
        {'path': [(330, 166), (430, 230)], 'color': 'purple', 'dur': 0.5, 'hold': 0.6},
        {'path': [(430, 300), (190, 350)], 'color': 'green', 'dur': 0.5, 'hold': 0.4},
        {'path': [(430, 300), (550, 350)], 'color': 'amber', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/10/27-4.svg'))

print('ok')

# =====================================================================
# 2026/04/16-1  adoption: four eras of AI coding tools, with logos
# =====================================================================
d = Diagram(1100, 560, 'AI 코딩 도구 4년 — 자동완성, 채팅, 에디터 안의 에이전트, 터미널 에이전트')
def yx(y, m):
    return 70 + ((y - 2021) * 12 + (m - 1)) * (960 / 66)
d.arrow([(70, 140), (1040, 140)], color='muted')
for y in (2021, 2022, 2023, 2024, 2025, 2026):
    x = yx(y, 1); d.arrow([(x, 134), (x, 146)], color='muted', head=False, width=1); d.text(x, 124, str(y), size=12, weight=700, color=MUTED)
eras = [('자동완성', 2021, 6, 2022, 11, 'blue'), ('채팅', 2022, 11, 2023, 6, 'amber'), ('에디터 안의 에이전트', 2023, 6, 2025, 2, 'purple'), ('터미널 에이전트', 2025, 2, 2026, 7, 'green')]
for lab, y1, m1, y2, m2, c in eras:
    x1, x2 = yx(y1, m1), yx(y2, m2)
    d.box(x1, 156, x2 - x1 - 4, 30, color=c); d.text((x1 + x2) / 2, 176, lab, size=12, weight=700, color=G[c])
events = [('githubcopilot', 2021, 6, 'GitHub Copilot', '프리뷰 2021-06 · GA 2022-06', 210, 'left'),
          ('openai', 2022, 11, 'ChatGPT', '2022-11-30', 300, 'left'),
          ('cursor', 2023, 3, 'Cursor', '2023, VS Code 포크', 390, 'left'),
          ('anthropic', 2024, 11, 'MCP', '2024-11-25 공개', 210, 'right'),
          ('claude', 2025, 2, 'Claude Code', '프리뷰 2025-02-24 · GA 2025-05-22', 300, 'right'),
          ('openai', 2025, 4, 'Codex CLI', '2025-04-16 · Copilot agent mode 2025-04', 390, 'right')]
for name, y, m, lab, sub, by, side in events:
    x = yx(y, m)
    d.arrow([(x, 140), (x, by)], color='muted', head=False, dashed=True, width=1)
    bx = x - 20 if side == 'left' else x - 240
    bx = max(40, min(bx, 1060 - 260))
    d.box(bx, by, 260, 56, color='gray'); icon(d, name, bx + 12, by + 14, 28)
    d.text(bx + 52, by + 25, lab, size=13, weight=700, anchor='start'); d.text(bx + 52, by + 43, sub, size=10, weight=600, color=MUTED, anchor='start')
d.box(40, 490, 1020, 50, color='green'); d.text(550, 510, '네 번째가 다른 점: 에이전트가 셸을 쥔다 — 빌드·테스트·커밋을 실행한다. 그때부터 문제는 도구가 아니라 권한과 게이트다', size=12, weight=700, color=G['green']); d.text(550, 530, '2025-12 Agentic AI Foundation(리눅스 재단)에 MCP 와 AGENTS.md 기부 · 2026-04-16 이 저장소의 첫 Co-Authored-By 커밋', size=11, weight=600, color=MUTED)
d.flow([{'path': [(yx(2021, 6), 140), (yx(2026, 4), 140)], 'color': 'green', 'dur': 3.0, 'hold': 1.0}])
d.save(out('2026/04/16-1.svg'))

# =====================================================================
# 2026/04/16-2  adoption: monthly commits with three eras
# =====================================================================
d = Diagram(1100, 520, '월별 커밋 — 혼자 (2025-05 ~ 2026-02), 에이전트가 있지만 흐름은 그대로 (2026-03), 에이전트 주도 PR 흐름 (2026-04)')
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
d.group(70, 100, 790, 60, '혼자 · 자동완성 시대 — [TYPE] 영어 한 줄, 직접 푸시, PR 0, 커버리지 게이트 10% → 1%', color='muted')
d.group(870, 100, 90, 60, '3월', color='amber'); d.text(915, 140, '설정만', size=11, weight=700, color=G['amber'])
d.group(950, 100, 110, 60, '4월', color='green'); d.text(1005, 140, 'PR 57', size=11, weight=700, color=G['green'])
d.text(260, 460, '2025-10, 2026-01 은 0 · 2026-02 는 "add a lot of different things" 한 커밋', size=11, weight=600, color=MUTED)
d.text(740, 460, '3월: 38개 중 16개가 CI 시행착오 · 4월 16일: 첫 Co-Authored-By, 첫 PR CI, PR #1', size=11, weight=600, color=MUTED)
d.text(550, 490, '산출량이지 가치가 아니다 — 이 시리즈에서 숫자를 쓸 때는 그 한계도 같이 쓴다', size=12, weight=700)
d.flow([{'path': [(880, 100), (880, 160)], 'color': 'amber', 'dur': 0.4, 'hold': 0.4}, {'path': [(960, 100), (960, 160)], 'color': 'green', 'dur': 0.4, 'hold': 1.0}])
d.save(out('2026/04/16-2.svg'))

# =====================================================================
# 2026/04/16-3  adoption: before/after workflow
# =====================================================================
d = Diagram(1100, 600, '작업 흐름 — 도입 전과 2026-04-16 이후')
d.group(40, 86, 1020, 130, '도입 전')
before = [('편집', 'IDE + 자동완성', 'muted'), ('./gradlew build', '로컬에서 손으로', 'muted'), ('git push', '브랜치에 직접', 'muted'), ('배포 워크플로', 'PR 검사 없음', 'muted')]
for i, (lab, sub, c) in enumerate(before):
    x = 60 + i * 250
    d.box(x, 120, 230, 60, lab, [sub], color=c, label_size=13, sub_size=11)
    if i: d.arrow([(x - 20, 150), (x, 150)], color='muted')
d.group(40, 240, 1020, 330, '이후 — 훅 · 스킬 · PR 흐름 · 메모리가 한 묶음')
after = [('이슈 #N', '모듈별 작업 큐', 'gray', None), ('worktree 브랜치', 'feature/<name>', 'gray', None), ('에이전트 편집', 'PostToolUse: ktlint', 'blue', 'claude'), ('턴 종료', 'Stop: test + JaCoCo', 'blue', None),
         ('/commit', 'Conventional Commits', 'purple', None), ('git push', 'PreToolUse: 커버리지 90% 미만 차단', 'amber', None), ('/pr → PR CI', 'pr-ci.yml, 처음 생긴 PR 게이트', 'green', 'github'), ('스쿼시 머지', 'release-please 가 버전', 'green', None)]
for i, (lab, sub, c, lg) in enumerate(after):
    col, row = i % 4, i // 4
    x, y = 60 + col * 250, 280 + row * 110
    d.box(x, y, 230, 70, color=c)
    if lg: icon(d, lg, x + 12, y + 21, 28)
    d.text(x + 115 + (12 if lg else 0), y + 28, lab, size=13, weight=700); d.text(x + 115 + (12 if lg else 0), y + 50, sub, size=10, weight=600, color=MUTED)
    if col: d.arrow([(x - 20, y + 35), (x, y + 35)], color=c)
d.arrow([(925, 350), (925, 365), (175, 365), (175, 390)], color='gray')
d.box(60, 510, 980, 44, color='muted'); d.text(550, 528, '파란 = 훅 · 보라 = 스킬 · 초록 = GitHub · 노랑 = 게이트.  memory/MEMORY.md 에 결정을 적는다.  이날 이후 직접 푸시는 사라졌다', size=11, weight=600)
d.flow([{'path': [(290, 315), (310, 315)], 'color': 'gray', 'dur': 0.3}, {'path': [(540, 315), (560, 315)], 'color': 'blue', 'dur': 0.3}, {'path': [(790, 315), (810, 315)], 'color': 'blue', 'dur': 0.3},
        {'path': [(925, 350), (925, 365), (175, 365), (175, 390)], 'color': 'gray', 'dur': 0.8},
        {'path': [(290, 425), (310, 425)], 'color': 'purple', 'dur': 0.3}, {'path': [(540, 425), (560, 425)], 'color': 'amber', 'dur': 0.3, 'hold': 0.3}, {'path': [(790, 425), (810, 425)], 'color': 'green', 'dur': 0.3, 'hold': 1.0}])
d.save(out('2026/04/16-3.svg'))

# =====================================================================
# 2026/05/07-1  harness: the fold
# =====================================================================
d = Diagram(1100, 560, '2026-05-07 — 저장소 두 개의 하네스 두 벌이 루트 하나로 접힌다')
for i, (name, c) in enumerate((('backend 저장소', 'blue'), ('frontend 저장소', 'purple'))):
    y = 100 + i * 200
    d.group(40, y, 300, 170, name, color=c)
    for j, item in enumerate(('.claude/ (훅·커맨드·에이전트)', '.github/workflows/', 'memory/MEMORY.md', 'CLAUDE.md')):
        d.box(60, y + 30 + j * 34, 260, 28, color=c); d.text(190, y + 48 + j * 34, item, size=11, weight=600, mono=True)
d.box(390, 230, 180, 70, 'git-filter-repo', ['백엔드 이력을 backend/ 아래로'], color='gray', label_size=13, sub_size=10)
d.arrow([(340, 185), (390, 250)], color='blue'); d.arrow([(340, 385), (390, 280)], color='purple')
d.group(620, 100, 440, 370, '모노레포 루트')
d.box(640, 130, 400, 44, '.claude/ — 에이전트 12 · 커맨드 15 · 훅 4 · 패턴 문서 9', color='green', label_size=12)
d.box(640, 184, 400, 44, '.claude/stacks.json — 스택 분기의 단일 진실', color='green', label_size=12)
d.box(640, 238, 400, 44, '.github/workflows/ 7개 + paths-filter', color='green', label_size=12)
d.box(640, 292, 400, 44, 'memory/MEMORY.md (오늘 항목 4개, Why · How to apply)', color='green', label_size=12)
d.box(640, 346, 400, 44, 'CLAUDE.md 루트 76줄 → backend/ 275줄 · frontend/ 73줄', color='green', label_size=12)
d.box(640, 400, 195, 44, 'backend/.claude/ ✕', color='red', dashed=True, label_size=12); d.box(845, 400, 195, 44, 'frontend/.claude/ ✕', color='red', dashed=True, label_size=12)
d.arrow([(570, 265), (620, 265)], color='gray')
d.text(550, 500, 'Claude Code 는 루트 settings.json 하나만 읽고, GitHub 은 루트 .github/ 만 인식한다 — 하위 폴더의 훅과 워크플로는 한 번도 돌지 않았다', size=12, weight=700, color=G['red'])
d.text(550, 526, '중복 스타터 파일 8,049줄 삭제 · 합친 본질적 이유는 하네스가 아니라 API 타입 드리프트', size=11, weight=600, color=MUTED)
d.flow([{'path': [(340, 185), (390, 250)], 'color': 'blue', 'dur': 0.5}, {'path': [(340, 385), (390, 280)], 'color': 'purple', 'dur': 0.5}, {'path': [(570, 265), (620, 265)], 'color': 'green', 'dur': 0.4, 'hold': 1.0}])
d.save(out('2026/05/07-1.svg'))

# =====================================================================
# 2026/05/07-2  harness: read / follow / enforce
# =====================================================================
d = Diagram(1100, 620, '에이전트가 읽는 것, 따르는 것, 막는 것 — 세 층')
logo_box(d, 40, 96, 1020, 56, 'claude', 'Claude Code 세션', 'SessionStart 가 맥락을 넣고, 도구 호출마다 훅이 본다', color='gray')
d.group(40, 180, 330, 300, '읽는 것 (맥락)', color='blue')
for i, (lab, sub) in enumerate((('CLAUDE.md 3겹', '루트 색인 → 스택 규칙, 누적 로딩'), ('.claude/skills/*.md', '패턴 문서 — kotlin · nextjs · db …'), ('memory/MEMORY.md', '결정과 "왜", 날짜별 항목'), ('docs/specs/*', 'PRD + 역할별 프롬프트'))):
    d.box(60, 210 + i * 64, 290, 54, lab, [sub], color='blue', label_size=12, sub_size=10)
d.group(390, 180, 320, 300, '따르는 것 (스킬)', color='purple')
for i, (lab, sub) in enumerate((('/start → /plan → /new', 'worktree · PRD · 생성 에이전트'), ('/test → /review', '테스트 생성 · 리뷰'), ('/commit → /pr → /merge', 'Conventional Commits · 보안 리뷰 게이트'), ('/memory · /rule', '기억 추가 · 실수 뒤 규칙 등록'))):
    d.box(410, 210 + i * 64, 280, 54, lab, [sub], color='purple', label_size=12, sub_size=10)
d.group(730, 180, 330, 300, '막는 것 (강제)', color='amber')
for i, (lab, sub, c) in enumerate((('safety-guard.sh', 'PreToolUse(Bash) · exit 2', 'amber'), ('pre-push.sh', '커버리지 90% · main 직접 푸시 차단', 'amber'), ('post-edit-lint.sh · Stop 테스트', 'PostToolUse · Stop', 'amber'), ('CI 10개', 'backend · frontend · api-contract · release', 'green'))):
    d.box(750, 210 + i * 64, 290, 54, lab, [sub], color=c, label_size=12, sub_size=10)
d.box(390, 500, 320, 44, '.claude/stacks.json', ['훅과 스킬이 읽어 스택별로 분기'], color='green', label_size=12, sub_size=10)
d.arrow([(390, 522), (300, 522), (300, 480)], color='green', head=False, width=1); d.arrow([(710, 522), (800, 522), (800, 480)], color='green', head=False, width=1)
d.text(550, 580, '실수 → 규칙: 에이전트가 남긴 마커 주석이 화면에 보이자 루트 CLAUDE.md 맨 위에 "절대 금지"가 올라갔다 (5월 14일)', size=11, weight=600, color=MUTED)
d.flow([{'path': [(550, 152), (550, 180)], 'color': 'gray', 'dur': 0.3}, {'path': [(390, 522), (300, 522), (300, 480)], 'color': 'green', 'dur': 0.5}, {'path': [(710, 522), (800, 522), (800, 480)], 'color': 'green', 'dur': 0.5, 'hold': 1.0}])
d.save(out('2026/05/07-2.svg'))

# =====================================================================
# 2026/05/07-3  harness: API contract loop
# =====================================================================
d = Diagram(1100, 560, 'API 계약 한 소스 — Kotlin 컨트롤러에서 TypeScript 타입까지, CI 가 양쪽을 다시 만들어 비교한다')
s = [('Kotlin 컨트롤러 · DTO', 'backend/', 'blue'), ('./gradlew generateOpenApi', 'springdoc, H2 프로파일로 앱 기동', 'blue'), ('backend/openapi/*.json', '모듈 4개', 'gray'), ('정규화', 'description 합치기 · 키 정렬 (내일)', 'amber'), ('openapi-typescript', 'npm run gen:api', 'purple'), ('frontend/types/api/*.gen.ts', '프론트엔드가 import', 'purple')]
for i, (lab, sub, c) in enumerate(s):
    col, row = i % 3, i // 3
    x, y = 60 + col * 340, 110 + row * 120
    d.box(x, y, 300, 70, lab, [sub], color=c, label_size=13, sub_size=10)
    if col: d.arrow([(x - 40, y + 35), (x, y + 35)], color=c)
d.arrow([(1020, 180), (1020, 200), (210, 200), (210, 230)], color='gray')
d.box(60, 360, 1000, 60, 'CI api-contract.yml — PR 마다 양쪽을 다시 생성해 커밋된 산출물과 git diff --exit-code', ['한쪽만 커밋된 PR 은 실패한다. 에이전트가 컨트롤러를 고치면 타입 재생성까지가 한 작업'], color='green', label_size=13, sub_size=11)
d.text(550, 460, '하루 만에 드러난 비용: springdoc 출력이 비결정적 — 같은 코드에서 키 순서가 바뀌어 거짓 diff', size=12, weight=700, color=G['amber'])
d.text(550, 486, '합친 본질적 이유 — 백엔드 컨트롤러 변경이 프론트엔드 타입에 즉시 반영되도록 강제', size=11, weight=600, color=MUTED)
d.flow([{'path': [(360, 145), (400, 145)], 'color': 'blue', 'dur': 0.4}, {'path': [(700, 145), (740, 145)], 'color': 'blue', 'dur': 0.4},
        {'path': [(1020, 180), (1020, 200), (210, 200), (210, 230)], 'color': 'gray', 'dur': 0.9},
        {'path': [(360, 265), (400, 265)], 'color': 'amber', 'dur': 0.4}, {'path': [(700, 265), (740, 265)], 'color': 'purple', 'dur': 0.4},
        {'path': [(900, 300), (900, 360)], 'color': 'green', 'dur': 0.4, 'hold': 1.0}])
d.save(out('2026/05/07-3.svg'))
print('batch3 all ok')
