import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from diag import Diagram, INK, MUTED, PAL

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

RED, GREEN, BLUE, AMBER = PAL['red'][0], PAL['green'][0], PAL['blue'][0], PAL['amber'][0]

# =====================================================================
# 2026/11/09-1  deploy-time: one enum change → all 10 services
# =====================================================================
d = Diagram(1100, 560, '결재 서비스 기능 하나에 응답 코드 하나를 추가해도 core가 바뀌어 10개가 모두 다시 배포됐다')
d.box(40, 230, 220, 90, '커밋', ['결재 서비스 기능 추가', '+ 응답 코드 1개'], color='blue')
d.box(330, 215, 250, 120, 'core 모듈', ['ExceptionCode.kt · SuccessCode.kt', '응답 코드 1,350개', '모든 서비스가 의존'], color='red')
names = ['account', 'approval', 'sales', 'chat', 'mail', 'batch', 'mcp', 'etc', 'notification', 'site']
for i, n in enumerate(names):
    y = 100 + i * 38
    col = 'green' if n == 'approval' else 'amber'
    d.box(700, y, 170, 30, f'{n}-api', color=col, label_size=13)
    d.arrow([(580, 275), (640, 275), (640, y + 15), (700, y + 15)], color='muted', width=1.2)
d.arrow([(260, 275), (330, 275)], color='blue')
d.text(990, 175, '실제로 바뀐 서비스', size=13, color=GREEN)
d.text(990, 195, '1개', size=22, weight=800, color=GREEN)
d.text(990, 300, '다시 배포된 서비스', size=13, color=RED)
d.text(990, 320, '10개', size=22, weight=800, color=RED)
d.text(990, 345, '≈ 5.9 + 3.45 × 10 = 40분', size=12, color=MUTED)
d.note(40, 490, 1020, 46, '73회 중 44회(60%)가 10개 전체 배포 — 1위 원인이 이 enum 두 개, 2위가 배포 파이프라인 파일 변경(13회)', color='muted', size=14)
stages = [{'path': [(260, 275), (330, 275)], 'color': 'blue', 'dur': 0.5}]
d.flow(stages + [{'path': [(580, 275), (640, 275), (640, 100 + i * 38 + 15), (700, 100 + i * 38 + 15)],
                  'color': 'red', 'dur': 0.18, 'hold': 0.02} for i in range(10)] + [{'path': [(870, 300), (930, 310)], 'color': 'red', 'dur': 0.3, 'hold': 0.8}])
d.save(out('2026/11/09-1.svg'))

# =====================================================================
# 2026/11/09-2  deploy-time: docker layers chown -R vs COPY --chown
# =====================================================================
d = Diagram(1100, 520, 'COPY 뒤의 chown -R은 복사한 파일 전체를 새 레이어로 다시 쓴다 — 코드만 바뀌어도 145MB가 올라간다')
d.group(40, 90, 490, 330, '수정 전 — RUN chown -R app:app /app')
d.box(70, 330, 430, 60, 'dependencies 130.5MB', ['그대로면 캐시 ✓'], color='muted')
d.box(70, 260, 430, 60, 'application 14.3MB', ['코드가 바뀌면 새로'], color='amber')
d.box(70, 130, 430, 120, 'chown 레이어 144.9MB', ['의존성 + 앱을 소유자만 바꿔 통째로 다시 씀', '→ 매 빌드 새 레이어 → 매번 push', '서비스당 push 중앙 55초 (최대 117초)'], color='red')
d.group(570, 90, 490, 330, '수정 후 — COPY --chown=app:app')
d.box(600, 330, 430, 60, 'dependencies 130.5MB', ['소유자 지정해 복사 · 그대로면 캐시 ✓'], color='green')
d.box(600, 260, 430, 60, 'application 14.3MB', ['코드가 바뀌면 이것만 push'], color='amber')
d.box(600, 130, 430, 120, 'chown 레이어 없음', ['사용자를 먼저 만들고', 'WORKDIR 만 chown (빈 디렉터리)', '서비스당 push 약 4초'], color='green', dashed=True)
d.note(40, 440, 1020, 50, 'BuildKit 캐시도 mode=max → mode=min: 빌드마다 달라 재사용 안 되는 extract 단계를 내보내느라 60초 → 11초', color='muted', size=14)
d.flow([{'path': [(285, 250), (285, 215)], 'color': 'red', 'dur': 0.4},
        {'path': [(285, 130), (285, 100)], 'color': 'red', 'dur': 0.6, 'label': '145MB push', 'label_at': (390, 112)},
        {'path': [(815, 260), (815, 100)], 'color': 'green', 'dur': 0.6, 'hold': 0.8, 'label': '14MB push', 'label_at': (910, 112)}])
d.save(out('2026/11/09-2.svg'))

# =====================================================================
# 2026/11/09-3  deploy-time: serial vs pipelined deploy (gantt)
# =====================================================================
d = Diagram(1100, 560, '모든 push가 끝나길 기다리지 않고, 이미지가 나온 서비스부터 바로 배포한다')
def gantt(y0, title, pipelined):
    d.text(40, y0, title, size=15, weight=800, anchor='start')
    builds = [(0, 120), (0, 160), (0, 200), (0, 240)]
    x0, sc = 180, 1.9
    for i, (s, e) in enumerate(builds):
        y = y0 + 25 + i * 34
        d.text(170, y + 12, f'서비스 {chr(65 + i)}', size=12, color=MUTED, anchor='end')
        d.box(x0 + s * sc, y, (e - s) * sc, 24, '빌드·push', color='blue', label_size=11)
    for i, (s, e) in enumerate(builds):
        y = y0 + 25 + i * 34
        start = e if pipelined else 240 + i * 45
        d.box(x0 + start * sc, y, 45 * sc, 24, 'Kamal', color='green', label_size=11)
    end = (240 + 45) if pipelined else (240 + 4 * 45)
    d.arrow([(x0 + end * sc, y0 + 20), (x0 + end * sc, y0 + 165)], color='red' if not pipelined else 'green', head=False, dashed=True)
    d.text(x0 + end * sc + 8, y0 + 12, '끝' , size=12, color=RED if not pipelined else GREEN, anchor='start')
    return x0, sc
gantt(95, '수정 전 — publish 잡 전부 끝난 뒤 배포 잡이 직렬로', False)
gantt(300, '수정 후 — 각 publish 잡이 push 직후 그 자리에서 배포 (서버 flock이 줄 세움)', True)
d.note(40, 500, 1020, 44, 'Kamal 배포는 서비스당 30~37초 — 10개면 직렬 대기만 약 6.5분이었다', color='muted', size=14)
d.flow([{'path': [(180 + 120 * 1.9, 337), (180 + 165 * 1.9, 337)], 'color': 'green', 'dur': 0.5},
        {'path': [(180 + 160 * 1.9, 371), (180 + 205 * 1.9, 371)], 'color': 'green', 'dur': 0.5},
        {'path': [(180 + 200 * 1.9, 405), (180 + 245 * 1.9, 405)], 'color': 'green', 'dur': 0.5},
        {'path': [(180 + 240 * 1.9, 439), (180 + 285 * 1.9, 439)], 'color': 'green', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/11/09-3.svg'))

# =====================================================================
# 2026/11/09-4  deploy-time: path classification → full / canary / selected
# =====================================================================
d = Diagram(1100, 560, '바뀐 경로를 shared · pipeline · 서비스로 분류해 전체 · 카나리 · 선택 배포를 정한다')
d.box(40, 230, 200, 100, 'git diff', ['직전 성공 push 실행', '..이번 커밋'], color='blue')
d.box(310, 230, 200, 100, '경로 분류', ['paths-filter', '서비스별 경로 목록'], color='purple')
d.box(600, 100, 230, 90, 'shared가 하나라도', ['core/src/main · build.gradle', 'backend/docker'], color='red')
d.box(600, 235, 230, 90, '서비스 경로만', ['account-api/** · role/src/main/**', 'deploy.account-backend*.yml'], color='green')
d.box(600, 370, 230, 90, 'pipeline만', ['워크플로 · kamal-deploy action'], color='amber')
d.box(890, 100, 170, 90, '전체 10개', color='red')
d.box(890, 235, 170, 90, '바뀐 서비스만', color='green')
d.box(890, 370, 170, 90, '카나리 1개', ['etc-api'], color='amber')
d.arrow([(240, 280), (310, 280)], color='blue')
for y in (145, 280, 415):
    d.arrow([(510, 280), (555, 280), (555, y), (600, y)], color='muted', width=1.5)
    d.arrow([(830, y), (890, y)], color='gray')
d.note(40, 490, 1020, 50, ['core 테스트만 바뀐 커밋은 배포하지 않는다 · 수동 일부 배포는 비교 기준에서 제외 · workflow_dispatch(modules)로 언제든 전체'], color='muted', size=13)
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
d = Diagram(1100, 540, '공용 ui 패키지는 앱 11개가 쓰지만, 떼어 낸 records 패키지는 3개만 쓴다 — 패키지 경계가 곧 빌드 범위')
apps = ['영업', '결재', '메신저', '메일', '관리자', '운영', '포털', '가이드', '소개 A', '소개 B', '소개 C']
d.group(40, 85, 500, 380, '수정 전 — 레코드 UI가 @my/ui 안에')
d.box(190, 115, 200, 60, '@my/ui', ['+ 레코드 공유 UI'], color='red')
d.group(55, 215, 470, 205, '@my/ui를 쓰는 앱 11개 — 전부 검사 · 배포')
for i, a in enumerate(apps):
    x = 70 + (i % 4) * 113; y = 240 + (i // 4) * 58
    d.box(x, y, 100, 42, a, color='amber', label_size=13)
d.arrow([(290, 175), (290, 215)], color='red')
d.text(290, 445, '레코드 UI 한 줄 수정 → 앱 11개 검사·배포', size=13, color=RED)
d.group(560, 85, 500, 380, '수정 후 — @my/records로 분리')
d.box(600, 110, 180, 60, '@my/ui', ['11개가 사용'], color='muted')
d.box(840, 110, 180, 60, '@my/records', ['records → ui 단방향'], color='green')
for i, a in enumerate(['영업', '결재', '메신저']):
    x = 760 + i * 100; y = 260
    d.box(x, y, 90, 44, a, color='green', label_size=13)
    d.arrow([(930, 170), (930, 215), (x + 45, 215), (x + 45, y)], color='green', width=1.5)
d.arrow([(840, 140), (780, 140)], color='muted', dashed=True)
d.text(810, 445, '레코드 UI 수정 → 앱 3개만', size=13, color=GREEN)
d.text(810, 360, 'ui가 records를 재export하면 테스트가 실패', size=12, color=MUTED)
d.note(40, 480, 1020, 44, '영향 범위 = 바뀐 패키지 + package.json / pub deps 그래프의 전이 소비자 (이전·현재 그래프 둘 다)', color='muted', size=13)
d.flow([{'path': [(290, 175), (290, 215)], 'color': 'red', 'dur': 0.5, 'hold': 0.4},
        {'path': [(930, 170), (930, 215), (805, 215), (805, 260)], 'color': 'green', 'dur': 0.5},
        {'path': [(930, 170), (930, 215), (1005, 215), (1005, 260)], 'color': 'green', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/11/09-5.svg'))

# =====================================================================
# 2026/11/10-1  env: before / after source of truth
# =====================================================================
d = Diagram(1100, 580, '원본은 GitHub Environment 하나 — 배포 잡이 서버 파일을 다시 쓰고, Kamal은 그 파일로 컨테이너를 만든다')
d.group(40, 85, 1020, 135, '수정 전')
d.box(70, 120, 180, 76, '사람', ['서버에 SSH → vi'], color='amber')
d.box(330, 120, 240, 76, '서버 ~/app/env/*', ['원본? 로컬 사본은 9키 · 실제 43키'], color='red')
d.box(650, 120, 170, 76, 'kamal deploy', ['env-file 읽기'], color='gray')
d.box(880, 120, 150, 76, '컨테이너', color='gray')
d.arrow([(250, 158), (330, 158)], color='amber'); d.arrow([(570, 158), (650, 158)], color='gray'); d.arrow([(820, 158), (880, 158)], color='gray')
d.text(735, 207, '재배포를 빼먹으면 반영 안 됨', size=12, color=RED)
d.group(40, 250, 1020, 250, '수정 후')
d.box(70, 290, 200, 90, 'GitHub Environment', ['development / production', 'BACKEND_ENV 등 번들 Secret'], color='blue')
d.box(330, 290, 200, 90, '배포 잡', ['검증 · 마스킹', '브랜치 제한(dev / main)'], color='purple')
d.box(590, 290, 200, 90, '서버 ~/.app-env/*', ['700 / 600 · 원자 교체'], color='green')
d.box(850, 290, 180, 90, 'kamal deploy', ['env-file → 컨테이너'], color='green')
d.arrow([(270, 335), (330, 335)], color='blue'); d.arrow([(530, 335), (590, 335)], color='purple', label='SSH stdin', label_size=11)
d.arrow([(790, 335), (850, 335)], color='green')
d.box(70, 410, 200, 64, '사람', ['GitHub에서 Secret 수정'], color='amber')
d.arrow([(170, 410), (170, 380)], color='amber')
d.box(330, 410, 700, 64, color='muted')
d.text(680, 432, 'Next.js 웹은 빌드 때도 필요 → BuildKit secret mount로 빌드 단계에만 전달', size=13, weight=700)
d.text(680, 455, '이미지 레이어엔 남지 않음 · no-cache-filters: builder (secret은 캐시 키에 안 들어감)', size=12, weight=600, color=MUTED)
d.note(40, 515, 1020, 44, 'dev·prd 서버를 나눌 때는 Environment Variable KAMAL_HOST만 바꾸면 된다', color='muted', size=14)
d.flow([{'path': [(170, 410), (170, 380)], 'color': 'amber', 'dur': 0.3},
        {'path': [(270, 335), (330, 335)], 'color': 'blue', 'dur': 0.4},
        {'path': [(530, 335), (590, 335)], 'color': 'purple', 'dur': 0.4},
        {'path': [(790, 335), (850, 335)], 'color': 'green', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2026/11/10-1.svg'))

# =====================================================================
# 2026/11/10-2  env: sync pipeline detail
# =====================================================================
d = Diagram(1100, 600, '번들은 argv에도 로그에도 나오지 않고 SSH stdin으로만 서버에 간다')
d.group(40, 90, 560, 400, 'GitHub Actions 러너')
d.box(70, 125, 240, 64, '① flock 획득', ['서버 단위 · 최대 30분 대기'], color='gray')
d.box(70, 210, 240, 64, '② SSH 설정 생성', ['umask 077 임시 디렉터리 · trap 삭제'], color='gray')
d.box(70, 295, 240, 80, '③ sync.py', ['번들 파싱 · 검증', '모든 값 ::add-mask::'], color='purple')
d.box(340, 295, 230, 80, '④ ssh … python3 -', ['원격 스크립트(base64)', '+ 번들 JSON → stdin'], color='blue')
d.box(70, 400, 500, 64, '⑥ kamal deploy', ['env -u BUNDLE … — 자식 프로세스엔 번들 변수 없음'], color='green')
d.group(660, 90, 400, 400, '서버')
d.box(690, 295, 340, 80, '⑤ remote_sync.py', ['~/.app-env/ (deploy 700, 파일 600)', 'symlink 거부 · 임시 파일 → os.replace'], color='green')
d.box(690, 400, 340, 64, 'kamal-proxy · 새 컨테이너', ['env-file 읽기 → 헬스체크 → 전환'], color='green')
d.box(690, 125, 340, 140, color='red')
d.text(860, 150, '로그에 남는 것', size=14, weight=800, color=RED)
d.lines(860, 180, ['line 51: duplicate variable name …', 'category=SSH_HOST_KEY_UNKNOWN', 'Environment sync failed: LEGACY_…', '값 · 명령 원문 · SSH 출력은 버린다'], size=12, mono=False)
d.arrow([(190, 189), (190, 210)], color='gray'); d.arrow([(190, 274), (190, 295)], color='gray')
d.arrow([(310, 335), (340, 335)], color='purple')
d.arrow([(570, 335), (690, 335)], color='blue', label='stdin', label_size=12)
d.arrow([(860, 375), (860, 400)], color='green')
d.arrow([(570, 432), (690, 432)], color='green')
d.note(40, 510, 1020, 64, ['서버 스크립트는 이유를 종료 코드로만 알린다: 40 SYMLINK_REJECTED · 44 LEGACY_FILE_MISSING ·',
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
d = Diagram(1100, 600, '첫 전환 때만 옛 서버 파일과 비교하고, 다르면 컨테이너를 바꾸기 전에 멈춘 뒤 사람이 채택한다')
d.box(40, 250, 180, 80, '번들 검증 통과', color='blue')
d.box(280, 100, 220, 70, '새 경로 파일 있음', ['→ 번들이 원본'], color='green')
d.box(280, 200, 220, 70, '둘 다 없음 (새 서버)', ['→ 번들로 생성'], color='green')
d.box(280, 330, 220, 70, '옛 파일만 있음', ['첫 전환'], color='amber')
d.box(840, 110, 220, 150, '파일 쓰기', ['임시 파일 → os.replace', '→ kamal deploy'], color='green')
d.box(570, 330, 200, 70, '메모리에서 비교', ['옛 파일 키 ⊆ 번들 · 값 동일?'], color='amber')
d.box(570, 450, 200, 90, '컨테이너 교체 전 중단', ['LEGACY_VALUE_MISMATCH', '이미지 빌드는 성공 · 영향 없음'], color='red')
d.box(840, 450, 220, 90, '수동 채택 워크플로', ['main · prd · 값 차이만 허용', '진행 중 배포 있으면 중단'], color='purple')
d.arrow([(220, 290), (250, 290), (250, 135), (280, 135)], color='muted')
d.arrow([(250, 235), (280, 235)], color='muted')
d.arrow([(250, 290), (250, 365), (280, 365)], color='muted')
d.arrow([(500, 135), (840, 135)], color='green')
d.arrow([(500, 235), (840, 235)], color='green')
d.arrow([(500, 365), (570, 365)], color='amber')
d.arrow([(770, 365), (950, 365), (950, 260)], color='green', label='같음', label_size=12, label_dy=-12)
d.arrow([(670, 400), (670, 450)], color='red')
d.text(682, 425, '다름 · 키 누락', size=12, color=RED, anchor='start')
d.arrow([(770, 495), (840, 495)], color='red')
d.arrow([(1040, 450), (1040, 260)], color='purple', dashed=True)
d.text(1030, 420, '채택', size=12, color=PAL['purple'][0], anchor='end')
d.text(550, 565, '원칙: 비교를 통과시키려고 옛 파일을 지우거나 검증을 느슨하게 하지 않는다', size=14, weight=800, color=INK, anchor='middle')
d.text(550, 588, '어느 쪽이 맞는지는 사람이 정하고, 맞는 값을 Secret에 등록한 뒤 채택한다', size=13, weight=600, color=MUTED, anchor='middle')
d.flow([{'path': [(220, 290), (250, 290), (250, 365), (280, 365)], 'color': 'amber', 'dur': 0.4},
        {'path': [(500, 365), (570, 365)], 'color': 'amber', 'dur': 0.3},
        {'path': [(670, 400), (670, 450)], 'color': 'red', 'dur': 0.3},
        {'path': [(770, 495), (840, 495)], 'color': 'red', 'dur': 0.3, 'hold': 0.3},
        {'path': [(1040, 450), (1040, 260)], 'color': 'purple', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/11/10-3.svg'))

# =====================================================================
# 2026/11/10-4  env: SSHKit host key intersection
# =====================================================================
d = Diagram(1100, 520, 'SSHKit은 호스트명 · IP 양쪽에 등록된 키의 교집합을 찾는다 — 호스트명만 있는 핀은 "모르는 키"가 된다')
d.group(40, 90, 500, 300, '수정 전')
d.box(70, 125, 200, 70, 'known_hosts', ['deploy-host  ssh-ed25519 …'], color='blue')
d.box(310, 125, 200, 70, 'SSHKit 조회', ['"deploy-host,10.x.x.x"'], color='gray')
d.box(70, 230, 200, 70, 'deploy-host 키', ['{ ed25519 }'], color='green')
d.box(310, 230, 200, 70, 'IP 키', ['{ } (등록 안 함)'], color='muted')
d.box(165, 320, 250, 54, '교집합 = ∅ → SSH_HOST_KEY_UNKNOWN', color='red', label_size=13)
d.arrow([(170, 195), (170, 230)], color='blue'); d.arrow([(410, 195), (410, 230)], color='gray')
d.arrow([(170, 300), (250, 320)], color='muted'); d.arrow([(410, 300), (330, 320)], color='muted')
d.group(560, 90, 500, 300, '수정 후 — HostKeyAlias로 조회 이름 고정')
d.box(590, 125, 440, 90, 'KAMAL_SSH_CONFIG', ['Host *  HostKeyAlias deploy-host', 'StrictHostKeyChecking yes · GlobalKnownHostsFile /dev/null'], color='purple')
d.box(590, 245, 200, 60, '정상 핀', ['통과 ✓'], color='green')
d.box(830, 245, 200, 60, '다른 키', ['MISMATCH ✓'], color='red')
d.box(710, 320, 200, 54, '등록 안 된 호스트 → UNKNOWN ✓', color='amber', label_size=12)
d.arrow([(690, 215), (690, 245)], color='green'); d.arrow([(930, 215), (930, 245)], color='red'); d.arrow([(810, 215), (810, 320)], color='amber')
d.note(40, 410, 1020, 80, ['검증을 끄지 않고 조회 이름만 바꿨다 — 엄격함은 그대로인지 네 경우를 오프라인으로 재현해 확인',
                           'Kamal 2.12 · SSHKit 1.25 · Net::SSH 7.3'], color='muted', size=13)
d.flow([{'path': [(170, 195), (170, 230)], 'color': 'blue', 'dur': 0.3},
        {'path': [(410, 195), (410, 230)], 'color': 'gray', 'dur': 0.3},
        {'path': [(410, 300), (330, 320)], 'color': 'red', 'dur': 0.4, 'hold': 0.4},
        {'path': [(690, 215), (690, 245)], 'color': 'green', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2026/11/10-4.svg'))

# =====================================================================
# 2026/11/11-1  call: three paths, only one registered
# =====================================================================
d = Diagram(1100, 560, 'OS에 등록된 통화만 백그라운드에서 살아남는다 — 세 갈래 중 VoIP 푸시 착신만 CallKit을 거쳤다')
d.box(40, 110, 260, 90, '앱이 꺼져 있을 때 착신', ['VoIP 푸시 → OS 착신 화면에서 수락'], color='blue')
d.box(40, 250, 260, 90, '내가 직접 건 통화', ['CallController.start()'], color='amber')
d.box(40, 390, 260, 90, '앱 안 착신 화면에서 수락', ['앱이 앞에 떠 있을 때'], color='amber')
d.box(400, 110, 280, 90, 'OS 통화로 등록', ['iOS CallKit · Android Telecom + FGS'], color='green')
d.box(400, 310, 280, 110, '등록 안 됨', ['앱만 아는 통화', 'OS는 그냥 백그라운드 앱으로 본다'], color='red')
d.box(780, 110, 280, 90, '홈으로 나가도', ['음성 유지 · 다이나믹 아일랜드'], color='green')
d.box(780, 310, 280, 110, '홈으로 나가면', ['iOS: 음성 끊김 · 아일랜드 없음', 'Android 14+: 마이크 끊김'], color='red')
d.arrow([(300, 155), (400, 155)], color='green')
d.arrow([(300, 295), (350, 295), (350, 350), (400, 350)], color='red')
d.arrow([(300, 435), (350, 435), (350, 380), (400, 380)], color='red')
d.arrow([(680, 155), (780, 155)], color='green'); d.arrow([(680, 365), (780, 365)], color='red')
d.note(40, 495, 1020, 46, 'UIBackgroundModes에 audio · voip를 선언하는 건 "그럴 수 있는 앱"이라는 뜻일 뿐 — 지금 통화 중임은 따로 알려야 한다', color='muted', size=13)
d.flow([{'path': [(300, 155), (400, 155)], 'color': 'green', 'dur': 0.4},
        {'path': [(680, 155), (780, 155)], 'color': 'green', 'dur': 0.4},
        {'path': [(300, 295), (350, 295), (350, 350), (400, 350)], 'color': 'red', 'dur': 0.5},
        {'path': [(680, 365), (780, 365)], 'color': 'red', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2026/11/11-1.svg'))

# =====================================================================
# 2026/11/11-2  call: reporter bidirectional
# =====================================================================
d = Diagram(1100, 600, '리포터는 앱 상태를 OS로, 이벤트 핸들러는 OS에서 누른 버튼을 앱으로 — 어느 경로로 시작했든 같은 길')
d.box(40, 140, 260, 120, '통화 상태기계', ['idle → outgoing → active → ended', 'micEnabled · cameraEnabled'], color='blue')
d.box(420, 140, 260, 120, '네이티브 통화 리포터', ['ref.listen으로 상태 구독', '서버 callId ↔ OS 통화 ID', '등록 목록 기준으로 종료'], color='purple')
d.box(800, 140, 260, 120, 'OS 통화', ['iOS CallKit · 다이나믹 아일랜드', 'Android Telecom + 통화 FGS'], color='green')
d.box(420, 350, 260, 120, '이벤트 핸들러', ['ACTION_CALL_ENDED → leave()', 'TOGGLE_MUTE → setMicrophoneEnabled', 'TOGGLE_AUDIO_SESSION → 오디오 엔진'], color='amber')
d.arrow([(300, 200), (420, 200)], color='blue', label='상태 변화', label_size=12)
d.arrow([(680, 200), (800, 200)], color='purple')
d.text(740, 120, 'startCall · setCallConnected', size=11, color=PAL['purple'][0])
d.text(740, 136, 'muteCall · endCall', size=11, color=PAL['purple'][0])
d.arrow([(930, 260), (930, 410), (680, 410)], color='amber')
d.text(918, 335, '아일랜드 · 잠금 화면 · 알림에서 누른 버튼', size=12, color=AMBER, anchor='end')
d.arrow([(420, 410), (170, 410), (170, 260)], color='amber')
d.note(40, 505, 1020, 64, ['setMicrophoneEnabled는 같은 상태면 아무것도 안 한다 → 앱 ⇄ OS 음소거 핑퐁 차단',
                           '울리는 Android 착신을 앱에서 받으면 endCall(=거절) 대신 hideCallkitIncoming 후 재등록'], color='muted', size=13)
d.flow([{'path': [(300, 200), (420, 200)], 'color': 'blue', 'dur': 0.4},
        {'path': [(680, 200), (800, 200)], 'color': 'purple', 'dur': 0.4, 'hold': 0.4},
        {'path': [(930, 260), (930, 410), (680, 410)], 'color': 'amber', 'dur': 0.6},
        {'path': [(420, 410), (170, 410), (170, 260)], 'color': 'amber', 'dur': 0.6, 'hold': 0.8}])
d.save(out('2026/11/11-2.svg'))

# =====================================================================
# 2026/11/11-3  call: iOS audio session timeline
# =====================================================================
d = Diagram(1100, 560, '오디오 엔진은 CallKit이 세션을 활성화한 동안에만 돈다 — 세션의 주인은 CallKit 하나')
lanes = [('CallKit', 140), ('AVAudioSession', 230), ('LiveKit 오디오 엔진', 320)]
for name, y in lanes:
    d.text(165, y, name, size=13, anchor='end'); d.arrow([(180, y), (1070, y)], color='muted', head=False, width=1)
ev = [(270, 320, '앱 시작', ['externalCallSystem', 'engine: none'], 'muted'),
      (430, 140, 'startCall', ['통화 등록'], 'purple'),
      (590, 230, 'didActivate', ['세션 활성'], 'green'),
      (590, 320, 'engine: default', ['소리 남'], 'green'),
      (790, 230, '다른 오디오 끼어듦', ['세션 비활성 이벤트'], 'amber'),
      (790, 320, '무시', ['엔진 켠 채로'], 'amber'),
      (985, 140, 'endCall', ['didDeactivate'], 'purple'),
      (985, 320, 'engine: none', [], 'muted')]
for x, y, l, s, c in ev:
    d.box(x - 75, y - 28, 150, 56, l, s or None, color=c, label_size=13, sub_size=11)
d.arrow([(430, 168), (430, 190), (590, 190), (590, 202)], color='purple')
d.arrow([(590, 258), (590, 292)], color='green')
d.arrow([(790, 258), (790, 292)], color='amber', dashed=True)
d.arrow([(985, 168), (985, 292)], color='purple')
d.note(40, 395, 500, 140, ['3초 대체 경로', 'didActivate를 놓치면(앱이 깨어나기 전 등)', '3초 뒤 엔진을 직접 연다 — 무음 통화 방지'], color='blue', size=13)
d.note(560, 395, 500, 140, ['통화 중 비활성화는 무시', '플러그인 3.1.6은 연결된 통화의 재활성화를', 'Dart에 알리지 않는다 → 여기서 끄면 끝까지 무음'], color='amber', size=13)
d.flow([{'path': [(430, 168), (430, 190), (590, 190), (590, 202)], 'color': 'purple', 'dur': 0.5},
        {'path': [(590, 258), (590, 292)], 'color': 'green', 'dur': 0.4, 'hold': 0.4},
        {'path': [(790, 258), (790, 292)], 'color': 'amber', 'dur': 0.4, 'hold': 0.4},
        {'path': [(985, 168), (985, 292)], 'color': 'purple', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2026/11/11-3.svg'))

# =====================================================================
# 2026/11/11-4  call: web audio re-attach
# =====================================================================
d = Diagram(1100, 540, 'LiveKit room과 트랙은 살아 있는데, 오디오 엘리먼트만 옛 컨테이너와 함께 문서에서 빠졌다')
d.group(40, 85, 500, 370, '수정 전 — /chat → /download 이동')
d.box(70, 120, 200, 70, 'Room · 원격 트랙', ['모듈 레벨 · 살아 있음'], color='green')
d.box(70, 240, 200, 110, '옛 CallHost', ['숨김 컨테이너', '└ <audio> (track.attach)'], color='red', dashed=True)
d.box(310, 240, 200, 110, '새 CallHost', ['숨김 컨테이너', '└ (비어 있음)'], color='gray')
d.arrow([(170, 190), (170, 240)], color='green', label='TrackSubscribed 때 1회', label_size=11, label_dy=0)
d.text(290, 395, '옛 컨테이너가 언마운트 → <audio>도 함께 제거', size=13, color=RED)
d.text(290, 420, '통화는 연결된 채 상대 소리만 끊김', size=13, color=RED)
d.group(560, 85, 500, 370, '수정 후 — 트랙을 들고 있다가 다시 붙인다')
d.box(590, 120, 200, 70, 'remoteAudioTracks', ['Set<RemoteAudioTrack>'], color='blue')
d.box(830, 120, 200, 70, '새 CallHost 마운트', ['setLiveKitContainer(el)'], color='purple')
d.box(700, 240, 230, 110, 'setAudioContainer(el)', ['track.detach() → remove', 'el.appendChild(track.attach())'], color='green')
d.arrow([(690, 190), (690, 215), (760, 215), (760, 240)], color='blue')
d.arrow([(930, 190), (930, 215), (870, 215), (870, 240)], color='purple')
d.text(810, 395, '자동 재생이 막히면(canPlaybackAudio=false)', size=13, color=MUTED)
d.text(810, 420, '다음 pointerdown / keydown에 room.startAudio() 1회', size=13, color=MUTED)
d.note(40, 470, 1020, 46, 'track.attach()로 만든 엘리먼트를 다시 마운트되는 컴포넌트의 DOM에 두면, 컴포넌트와 수명이 묶인다', color='muted', size=13)
d.flow([{'path': [(170, 190), (170, 240)], 'color': 'green', 'dur': 0.4},
        {'path': [(170, 350), (170, 380)], 'color': 'red', 'dur': 0.4, 'hold': 0.4},
        {'path': [(930, 190), (930, 215), (870, 215), (870, 240)], 'color': 'purple', 'dur': 0.4},
        {'path': [(690, 190), (690, 215), (760, 215), (760, 240)], 'color': 'blue', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2026/11/11-4.svg'))

# =====================================================================
# 2026/11/11-5  call: video background
# =====================================================================
d = Diagram(1100, 500, 'OS가 캡처만 멈추면 상대는 정지 화면을 보고, 앱이 먼저 카메라를 끄면 상대는 아바타를 본다')
d.text(40, 110, '수정 전', size=15, weight=800, anchor='start')
d.box(40, 130, 220, 90, 'iPhone 홈으로', ['AppLifecycle: paused'], color='gray')
d.box(320, 130, 240, 90, 'iOS가 캡처 강제 정지', ['트랙은 publish 상태', 'mute 신호 없음'], color='amber')
d.box(620, 130, 200, 90, 'LiveKit SFU', ['프레임이 안 올 뿐'], color='gray')
d.box(880, 130, 180, 90, '상대 화면', ['마지막 장면 정지'], color='red')
d.arrow([(260, 175), (320, 175)], color='gray'); d.arrow([(560, 175), (620, 175)], color='amber'); d.arrow([(820, 175), (880, 175)], color='red')
d.text(40, 270, '수정 후 (iOS)', size=15, weight=800, anchor='start')
d.box(40, 290, 220, 90, 'iPhone 홈으로', ['AppLifecycleListener'], color='gray')
d.box(320, 290, 240, 90, 'setCameraEnabled(false)', ['앱이 먼저 끈다', 'cameraEnabled 선택값은 유지'], color='blue')
d.box(620, 290, 200, 90, 'LiveKit SFU', ['TrackMuted 이벤트'], color='gray')
d.box(880, 290, 180, 90, '상대 화면', ['아바타 타일'], color='green')
d.arrow([(260, 335), (320, 335)], color='gray'); d.arrow([(560, 335), (620, 335)], color='blue'); d.arrow([(820, 335), (880, 335)], color='green')
d.note(40, 410, 1020, 64, ['돌아오면(resumed) 백그라운드 때문에 끈 경우에만 다시 켠다 · 연결 중 백그라운드면 connect 직후 한 번 더 끈다',
                           'Android는 OS 통화 등록으로 FGS에 camera 타입이 붙어 백그라운드에서도 송출'], color='muted', size=13)
d.flow([{'path': [(260, 175), (320, 175)], 'color': 'gray', 'dur': 0.3},
        {'path': [(560, 175), (620, 175)], 'color': 'amber', 'dur': 0.3},
        {'path': [(820, 175), (880, 175)], 'color': 'red', 'dur': 0.3, 'hold': 0.4},
        {'path': [(260, 335), (320, 335)], 'color': 'gray', 'dur': 0.3},
        {'path': [(560, 335), (620, 335)], 'color': 'blue', 'dur': 0.3},
        {'path': [(820, 335), (880, 335)], 'color': 'green', 'dur': 0.3, 'hold': 0.8}])
d.save(out('2026/11/11-5.svg'))
print('ok')
