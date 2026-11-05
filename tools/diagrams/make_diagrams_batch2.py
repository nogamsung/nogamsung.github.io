"""2025년 백엔드 4편 + 2026년 프론트엔드 5편의 다이어그램 (2026-11-05 작성).
실행: python3 tools/diagrams/make_diagrams_batch2.py "$PWD"
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from diag import Diagram, INK, MUTED

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

G = {'gray': '#1f2937', 'muted': '#6b7280', 'blue': '#2563eb', 'green': '#059669', 'red': '#dc2626', 'amber': '#d97706', 'purple': '#7c3aed'}

def rows(d, x, y, w, items, h=26, size=12, mono=True, colors=None):
    """작은 표: items 는 문자열 목록, 한 줄에 하나."""
    for i, s in enumerate(items):
        c = (colors or {}).get(i, 'gray')
        d.box(x, y + i * h, w, h, color=c)
        d.text(x + 10, y + i * h + h / 2 + 4, s, size=size, weight=600, anchor='start', mono=mono)

# =====================================================================
# 2025/06/16-1  soft delete: three ways
# =====================================================================
d = Diagram(1100, 600, '행을 잊는 세 가지 방법 — 물리 삭제, deleted_at, 상태 컬럼')
lanes = [(40, 'A. 물리 삭제', 'red'), (385, 'B. deleted_at 타임스탬프', 'amber'), (730, 'C. 상태 enum 컬럼 (선택)', 'green')]
for x, label, c in lanes:
    d.box(x, 86, 330, 38, label, color=c)
    rows(d, x + 20, 140, 290, ['1  철강A        ACTIVE', '2  철강B        ACTIVE', '3  철강C        ACTIVE'])
    d.arrow([(x + 165, 222), (x + 165, 262)], color=c)
    d.text(x + 180, 246, '2번 행을 "삭제"', size=11, weight=700, color=G[c], anchor='start')
rows(d, 60, 270, 290, ['1  철강A        ACTIVE', '3  철강C        ACTIVE'])
d.box(60, 322, 290, 26, color='red', dashed=True); d.text(205, 339, '(2번 행 사라짐)', size=12, color=G['red'])
rows(d, 405, 270, 290, ['1  철강A   deleted_at NULL', '2  철강B   deleted_at 2025-06-16', '3  철강C   deleted_at NULL'], colors={1: 'amber'})
rows(d, 750, 270, 290, ['1  철강A        ACTIVE', '2  철강B        DEACTIVATE', '3  철강C        ACTIVE'], colors={1: 'green'})
d.note(40, 368, 330, 92, ['orders.company_id → 2 가 고아가 된다.', 'FK 오류 또는 cascade 로 업무 기록까지 삭제.', '감사 추적 없음. 첫 커밋부터 선택지 밖.'], color='red', size=12)
d.note(385, 368, 330, 92, ['상태가 둘뿐(있음/없음). 모든 조회에 IS NULL.', '"언제·누가"는 이미 update_* 감사 컬럼이 기록.', '보류 같은 업무 상태가 생기면 컬럼이 또 필요.'], color='amber', size=12)
d.note(730, 368, 330, 92, ['되돌릴 수 있다(ACTIVE 로 복귀).', 'update_user_id·update_datetime 도 함께 갱신.', '같은 컬럼이 나중에 업무 상태까지 담는다.'], color='green', size=12)
d.box(40, 490, 1020, 70, color='muted')
d.text(550, 518, '조회는 리포지토리마다 where status = \'ACTIVE\' 를 명시한다 (구현 10개, 30곳) — 전역 가드 대신 쿼리에 보이는 조건', size=14, weight=600)
d.text(550, 542, 'UNIQUE 제약 없음 · 자식은 서비스가 명시적으로 내림(cascade 없음) · DELETE 문은 저장소 어디에도 없음', size=12, weight=600, color=MUTED)
d.flow([{'path': [(205, 222), (205, 262)], 'color': 'red', 'dur': 0.6, 'hold': 0.4},
        {'path': [(550, 222), (550, 262)], 'color': 'amber', 'dur': 0.6, 'hold': 0.4},
        {'path': [(895, 222), (895, 262)], 'color': 'green', 'dur': 0.6, 'hold': 0.8}])
d.save(out('2025/06/16-1.svg'))

# =====================================================================
# 2025/06/16-2  soft delete: request → UPDATEs, no DELETE
# =====================================================================
d = Diagram(1100, 560, 'DELETE /company 요청은 UPDATE 세 묶음이 된다 — DELETE 문은 한 번도 나가지 않는다')
cl = d.box(40, 200, 150, 70, '클라이언트', ['DELETE /company', '{ companyId }'], color='blue')
ct = d.box(250, 200, 200, 70, 'CompanyController', ['deactivateCompany()', '@DeleteMapping 유지'], color='gray')
sv = d.group(510, 96, 260, 290, 'CompanyService  @Transactional')
s1 = d.box(530, 126, 220, 60, 'companyEntity', ['.deactivate(updateUser)'], color='green')
s2 = d.box(530, 206, 220, 60, 'companyManager 들', ['.forEach { deactivate() }'], color='green')
s3 = d.box(530, 286, 220, 60, 'shipmentReportApproval 들', ['.forEach { deactivate() }'], color='green')
db = d.group(830, 96, 230, 290, 'DB (커밋 시 더티 체킹)')
d.box(850, 126, 190, 60, color='green'); d.lines(945, 150, ['UPDATE company SET', 'status=\'DEACTIVATE\', update_user_id=?'], size=9, mono=True)
d.box(850, 206, 190, 60, color='green'); d.lines(945, 230, ['UPDATE company_manager', 'SET status=\'DEACTIVATE\''], size=10, mono=True)
d.box(850, 286, 190, 60, color='green'); d.lines(945, 310, ['UPDATE shipment_report_approval', 'SET status=\'DEACTIVATE\''], size=10, mono=True)
d.box(850, 356, 190, 24, color='red', dashed=True); d.text(945, 372, 'DELETE FROM company  ✕', size=11, weight=700, color=G['red'], mono=True)
d.arrow([(190, 235), (250, 235)], color='blue')
d.arrow([(450, 235), (480, 235), (480, 156), (530, 156)], color='gray')
d.arrow([(450, 235), (480, 235), (530, 235)], color='gray')
d.arrow([(450, 235), (480, 235), (480, 316), (530, 316)], color='gray')
for y in (156, 236, 316):
    d.arrow([(750, y), (850, y)], color='green', dashed=True)
d.text(800, 140, 'save() 없음', size=11, color=MUTED)
d.box(40, 420, 1020, 50, color='green'); d.text(550, 450, '응답 200  COMPANY_DEACTIVATE  "회사 비활성화를 완료했습니다."   (전: COMPANY_DELETE "회사 삭제를 완료했습니다.")', size=13, weight=600)
d.note(40, 486, 1020, 56, ['HTTP 동사는 DELETE 를 유지했다 — "목록에서 없애 달라"는 의도 전달에 가장 맞고, 프론트 호출부를 같이 바꾸지 않기 위해.', '이름(비활성화)과 동사(DELETE)의 불일치는 알고 남긴 것. 상태를 직접 지정하는 요구가 오면 PATCH /company/{id}/status 로.'], color='muted', size=12)
d.flow([{'path': [(190, 235), (250, 235)], 'color': 'blue', 'dur': 0.5},
        {'path': [(450, 235), (480, 235), (480, 156), (530, 156)], 'color': 'gray', 'dur': 0.6},
        {'path': [(750, 156), (850, 156)], 'color': 'green', 'dur': 0.4},
        {'path': [(750, 236), (850, 236)], 'color': 'green', 'dur': 0.4},
        {'path': [(750, 316), (850, 316)], 'color': 'green', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2025/06/16-2.svg'))

# =====================================================================
# 2025/12/05-1  PDFBox: page anatomy with coordinates
# =====================================================================
d = Diagram(1100, 640, 'A4 한 장의 좌표 — 원점은 왼쪽 아래, 커서는 위에서 아래로 내려간다')
PX, PY, PW, PH = 150, 96, 327, 463   # A4 595.28x841.89 * 0.55
d.box(PX, PY, PW, PH, color='gray')
d.text(PX + PW / 2, PY + 40, '거 래 명 세 서', size=15, weight=700)
d.text(PX + PW / 2, PY + 58, '2025년 12월 05일', size=9, color=MUTED)
# header grid 10 cols, 5 rows
hx, hy, hw, hh = PX + 16, PY + 74, PW - 32, 70
d.box(hx, hy, hw, hh, color='muted')
for i in range(1, 5): d.arrow([(hx, hy + i * 14), (hx + hw, hy + i * 14)], color='muted', head=False, width=1)
for fx in (0.044, 0.12, 0.27, 0.35, 0.5, 0.544, 0.62, 0.77, 0.85): d.arrow([(hx + hw * fx, hy), (hx + hw * fx, hy + hh)], color='muted', head=False, width=1)
d.text(hx + 7, hy + 38, '공급자', size=7, weight=700)
d.text(hx + hw * 0.522, hy + 38, '공급받는자', size=7, weight=700)
# stamp (265,690) 40x40 → scaled
sx, sy = PX + 265 * 0.55, PY + (841.89 - 690 - 40) * 0.55
d.box(sx, sy, 22, 22, color='red', dashed=True); d.text(sx + 11, sy + 15, '印', size=11, weight=700, color=G['red'])
# body grid
bx, by, bw, bh = hx, hy + hh + 10, hw, 230
d.box(bx, by, bw, 16, color='amber'); d.text(bx + bw / 2, by + 11, '제품명 · 규격 · 단위 · 수량 · 단가 · 공급가액 · 비고', size=7, weight=700)
for i in range(1, 18): d.arrow([(bx, by + 16 + i * 12), (bx + bw, by + 16 + i * 12)], color='muted', head=False, width=1)
d.box(bx, by + 16, bw, 214, color='gray')
d.text(bx + bw / 2, by + 120, '18 행 (첫 페이지) / 25 행 (이후)', size=9, color=MUTED)
# footer
fy = by + bh + 8
d.box(bx, fy, bw, 42, color='muted'); d.text(bx + bw / 2, fy + 25, '소계 · 부가세 · 합계  |  납품장소 · 담당자 · 연락처', size=8, weight=600)
d.text(PX + PW / 2, PY + PH - 10, '1 / 2', size=8, color=MUTED)
# axes
d.arrow([(PX - 24, PY + PH + 14), (PX + 80, PY + PH + 14)], color='blue'); d.text(PX + 92, PY + PH + 18, 'x', size=12, weight=700, color=G['blue'], anchor='start')
d.arrow([(PX - 24, PY + PH + 14), (PX - 24, PY + PH - 90)], color='blue'); d.text(PX - 24, PY + PH - 100, 'y', size=12, weight=700, color=G['blue'])
d.text(PX - 30, PY + PH + 34, '(0, 0)', size=11, weight=700, color=G['blue'], anchor='start')
d.text(PX + PW + 8, PY - 4, '(595.28, 841.89)', size=11, weight=700, color=G['blue'], anchor='start')
# cursor animation
d.arrow([(PX - 60, PY + 50), (PX - 60, PY + PH - 20)], color='purple', dashed=True)
d.text(PX - 60, PY + 38, 'currentY', size=11, weight=700, color=G['purple'])
# right annotations
AX = 560
d.box(AX, 96, 500, 72, '시작 커서', ['currentY = page.mediaBox.height − 50  (= 791.89)', 'text() 한 번에 fontSize × 1.5 만큼 빼면서 내려간다'], color='purple', sub_size=12)
d.box(AX, 184, 500, 72, '가운데 정렬', ['textWidth = font.getStringWidth(s) / 1000 × fontSize', 'x = (pageWidth − textWidth) / 2  — 글리프 폭은 1/1000 em'], color='blue', sub_size=12)
d.box(AX, 272, 500, 72, '표', ['x = 30, 너비 = pageWidth − 60. 셀 행렬로 rowSpan/colSpan 처리', '사각형·선도 모두 왼쪽 아래 모서리 기준 (addRect(x, y − h, w, h))'], color='gray', sub_size=12)
d.box(AX, 360, 500, 72, '도장', ['imageFromUrl(url, 265, 690, 40, 40) — 첫 페이지, 전경(FOREGROUND)', 'PDImageXObject.createFromByteArray: PNG 알파는 SMask 로 유지'], color='red', sub_size=12)
d.box(AX, 448, 500, 72, '페이지 나눔', ['calculatePagination(items, 18, 25) 로 미리 쪼갠다', '머리표는 1쪽만, 합계표는 마지막 쪽만, 빈 행은 매 쪽 채움'], color='amber', sub_size=12)
d.box(AX, 536, 500, 56, '페이지 번호', ['모든 쪽을 만든 뒤 AppendMode.APPEND 로 스트림을 다시 열어 "n / 전체"'], color='muted', sub_size=12)
d.flow([{'path': [(PX - 60, PY + 50), (PX - 60, PY + PH - 20)], 'color': 'purple', 'dur': 2.5, 'hold': 0.8}])
d.save(out('2025/12/05-1.svg'))

# =====================================================================
# 2025/12/05-2  PDFBox: render pipeline
# =====================================================================
d = Diagram(1100, 560, '거래명세서 내보내기 — 조회, 그리기, S3 업로드, URL 응답')
a = d.box(40, 120, 150, 70, '컨트롤러', ['POST /sales/{id}', '/transaction/export'], color='blue')
b = d.box(240, 120, 170, 70, '서비스', ['판매 품목 fetch join', '회사·거래처 지역 조회'], color='gray')
c = d.box(240, 230, 170, 60, 'account 서비스', ['회사(도장 URL), 지역', 'WebClient .block()'], color='muted')
p = d.group(460, 96, 380, 250, 'TransactionStatementPdfUtils')
p1 = d.box(480, 126, 160, 50, 'calculatePagination', ['18 / 25 행'], color='amber')
p2 = d.box(660, 126, 160, 50, '페이지 루프', ['1쪽: 제목·머리표·도장'], color='gray')
p3 = d.box(480, 196, 160, 50, '본문 표', ['품목 + 빈 행 채움'], color='gray')
p4 = d.box(660, 196, 160, 50, '마지막 쪽: 합계표', ['소계·부가세·합계'], color='gray')
p5 = d.box(480, 266, 340, 50, 'addPageNumbers → PDDocument.save() → ByteArray', color='purple', label_size=13)
st = d.box(880, 120, 180, 70, '도장 이미지 GET', ['HttpClient, 10초 타임아웃', '실패 → 502'], color='red')
s3 = d.box(880, 266, 180, 70, 'S3 업로드', ['sales/{companyId}/거래명세서-…', 'application/pdf'], color='green')
d.arrow([(190, 155), (240, 155)], color='blue')
d.arrow([(325, 190), (325, 230)], color='muted', dashed=True)
d.arrow([(410, 155), (480, 155)], color='gray')
d.arrow([(640, 151), (660, 151)], color='gray')
d.arrow([(740, 176), (740, 196)], color='gray')
d.arrow([(640, 221), (660, 221)], color='gray', head=False)
d.arrow([(820, 140), (880, 140)], color='red', dashed=True)
d.text(850, 110, '동기 HTTP', size=10, weight=700, color=G['red'])
d.arrow([(820, 291), (880, 291)], color='green')
d.box(40, 380, 1020, 54, color='green'); d.text(550, 403, '201 TRANSACTION_STATEMENT_EXPORT   { data: "https://…/sales/7/거래명세서-7-202512051030-ab12cd34" }', size=13, weight=600, mono=True)
d.text(550, 423, '응답으로 바이트를 흘리지 않고 S3 URL 을 돌려준다 — "그때 보낸 그 파일"을 다시 열 수 있다', size=12, weight=600, color=MUTED)
d.note(40, 452, 1020, 80, ['요청 파라미터: priceVisibleYn(가격 숨김은 열을 빼지 않고 셀만 비움), header/body/footer 글자 크기 (기본 9/8/9pt)', '알고 남긴 빚: 셀마다 PDType0Font.load 반복, 공백 없는 한글은 wrapText 가 못 감쌈, 도장 좌표 상수, 막아 둔 서비스 테스트'], color='muted', size=12)
d.flow([{'path': [(190, 155), (240, 155)], 'color': 'blue', 'dur': 0.4},
        {'path': [(325, 190), (325, 230)], 'color': 'muted', 'dur': 0.4},
        {'path': [(410, 155), (480, 155)], 'color': 'gray', 'dur': 0.4},
        {'path': [(640, 151), (660, 151)], 'color': 'gray', 'dur': 0.2},
        {'path': [(820, 140), (880, 140)], 'color': 'red', 'dur': 0.5},
        {'path': [(740, 176), (740, 196)], 'color': 'gray', 'dur': 0.3},
        {'path': [(650, 246), (650, 266)], 'color': 'purple', 'dur': 0.3},
        {'path': [(820, 291), (880, 291)], 'color': 'green', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2025/12/05-2.svg'))

# =====================================================================
# 2025/12/08-1  date lock: calendar
# =====================================================================
d = Diagram(1100, 560, '매달 10일까지는 지난 달이 열려 있고, 11일부터 잠긴다 — isPassedRequestDate(문서 날짜, 오늘)')
months = [('10월', 100), ('11월', 420), ('12월', 740)]
for label, x in months:
    d.box(x, 96, 260, 60, label, color='gray', label_size=18)
d.arrow([(740 + 260 * 10.5 / 31, 96), (740 + 260 * 10.5 / 31, 156)], color='red', dashed=True, head=False, width=2)
d.text(740 + 260 * 10.5 / 31, 172, '10일 | 11일 경계', size=11, weight=700, color=G['red'])
# today = 12/8
y1 = 200
d.text(60, y1 + 22, '오늘 = 12월 8일', size=14, weight=700, anchor='start'); d.text(60, y1 + 42, '(dayOfMonth ≤ 10)', size=11, color=MUTED, anchor='start')
d.box(100, y1 + 56, 260, 34, color='red'); d.text(230, y1 + 78, '잠김 (지지난 달 이전)', size=12, weight=700, color=G['red'])
d.box(420, y1 + 56, 260, 34, color='green'); d.text(550, y1 + 78, '열림 — 지난 달, 10일까지', size=12, weight=700, color=G['green'])
d.box(740, y1 + 56, 260, 34, color='green'); d.text(870, y1 + 78, '열림 (이번 달)', size=12, weight=700, color=G['green'])
d.text(740 + 260 * 7.5 / 31, y1 + 50, '▼ 오늘 (8일)', size=11, weight=700, color=G['blue'])
# today = 12/12
y2 = 310
d.text(60, y2 + 22, '오늘 = 12월 12일', size=14, weight=700, anchor='start'); d.text(60, y2 + 42, '(dayOfMonth > 10)', size=11, color=MUTED, anchor='start')
d.box(100, y2 + 56, 260, 34, color='red'); d.text(230, y2 + 78, '잠김', size=12, weight=700, color=G['red'])
d.box(420, y2 + 56, 260, 34, color='red'); d.text(550, y2 + 78, '잠김 — 지난 달, 11일부터', size=12, weight=700, color=G['red'])
d.box(740, y2 + 56, 260, 34, color='green'); d.text(870, y2 + 78, '열림 (이번 달)', size=12, weight=700, color=G['green'])
d.text(740 + 260 * 11.5 / 31, y2 + 50, '▼ 오늘 (12일)', size=11, weight=700, color=G['blue'])
# decision table
ty = 430
d.box(100, ty, 900, 100, color='muted')
d.text(260, ty + 24, '대상 월', size=12, weight=700); d.text(560, ty + 24, '오늘 ≤ 10일', size=12, weight=700); d.text(820, ty + 24, '오늘 ≥ 11일', size=12, weight=700)
for i, (m, a, b) in enumerate([('지지난 달 이전', '잠김', '잠김'), ('지난 달', '열림', '잠김'), ('이번 달 · 미래', '열림', '열림')]):
    yy = ty + 48 + i * 22
    d.text(260, yy, m, size=12, weight=600)
    d.text(560, yy, a, size=12, weight=700, color=G['green'] if a == '열림' else G['red'])
    d.text(820, yy, b, size=12, weight=700, color=G['green'] if b == '열림' else G['red'])
d.text(550, ty + 120, '판정 기준은 문서의 업무 날짜(수주일·판매일·입금일·보고일)의 YearMonth. 생성과 수정 모두 검사. 상태 코드 409.', size=12, weight=600, color=MUTED)
d.flow([{'path': [(740 + 260 * 1 / 31, 180), (740 + 260 * 10.5 / 31, 180)], 'color': 'green', 'dur': 1.2, 'hold': 0.4},
        {'path': [(740 + 260 * 10.5 / 31, 180), (740 + 260 * 30 / 31, 180)], 'color': 'red', 'dur': 1.2, 'hold': 0.8}])
d.text(740 + 260 * 5.5 / 31, 196, '지난 달 열림', size=10, weight=700, color=G['green']); d.text(740 + 260 * 21 / 31, 196, '지난 달 잠김', size=10, weight=700, color=G['red'])
d.save(out('2025/12/08-1.svg'))

# =====================================================================
# 2025/12/08-2  date lock: flag vs derived rule
# =====================================================================
d = Diagram(1100, 600, '저장하는 상태(플래그) vs 계산하는 규칙(날짜) — 같은 사실을 두 곳에 두면 어긋난다')
d.group(40, 86, 490, 480, '분리 전: 플래그 + 날짜 규칙')
d.box(60, 116, 200, 60, 'LockEntity', ['lockedYn: Boolean = false'], color='red')
d.box(300, 116, 210, 60, 'lock()', ['운영 코드에서 호출 0건'], color='red', dashed=True)
d.arrow([(260, 146), (300, 146)], color='red', dashed=True)
for i, n in enumerate(['Order', 'Sales', 'Deposit', 'StockReport']):
    d.box(60 + i * 115, 206, 105, 40, n, color='gray', label_size=12)
    d.arrow([(112 + i * 115, 206), (112 + i * 115 - (i - 1.5) * 40, 176)], color='muted', head=False, width=1)
d.box(60, 276, 450, 44, '수정 요청', ['PUT /order (orderId 있음)'], color='blue', label_size=13)
d.arrow([(285, 320), (285, 346)], color='gray')
d.box(60, 346, 210, 50, '① 날짜 검사', ['isPassedRequestDate → 409 DATE_PASSED'], color='amber', label_size=12, sub_size=11)
d.box(300, 346, 210, 50, '② lockedYn 검사', ['항상 false → 통과'], color='red', label_size=12, sub_size=11)
d.arrow([(270, 371), (300, 371)], color='gray')
d.box(60, 426, 450, 44, '응답 DTO 8개', ['lockedYn: false  (항상 false 인 값을 UI 에 노출)'], color='red', label_size=12, sub_size=11)
d.note(60, 486, 450, 66, ['마감 버튼·배치가 없어 플래그는 191일 동안 한 번도 true 가 되지 않았다.', '마감은 ① 이 이미 하고 있었다. 두 진실 중 쓰는 사람 없는 쪽을 지웠다.'], color='red', size=12)
d.group(570, 86, 490, 480, '분리 후: 날짜 규칙만 (2025-12-08)')
d.box(590, 116, 200, 60, 'BaseEntity', ['status, 감사 컬럼'], color='gray')
d.box(830, 116, 210, 60, '시계 (now)', ['기본 LocalDate.now(), 테스트는 주입'], color='blue', dashed=True)
for i, n in enumerate(['Order', 'Sales', 'Deposit', 'StockReport']):
    d.box(590 + i * 115, 206, 105, 40, n, color='gray', label_size=12)
    d.arrow([(642 + i * 115, 206), (642 + i * 115 - (i - 1.5) * 40, 176)], color='muted', head=False, width=1)
d.box(590, 276, 450, 44, '생성·수정 요청', ['PUT /order, /sales, /deposit, /stock/report'], color='blue', label_size=13)
d.arrow([(815, 320), (815, 346)], color='gray')
d.box(590, 346, 450, 50, 'DateUtils.isPassedRequestDate(문서 날짜, now)', ['순수 함수 — 저장 상태 없음, 백필 없음, 드리프트 없음'], color='green', label_size=13, sub_size=11)
d.arrow([(935, 176), (935, 346)], color='blue', dashed=True)
d.box(590, 426, 215, 44, '통과 → 저장', color='green', label_size=12)
d.box(825, 426, 215, 44, '409 *_DATE_PASSED', ['"매달 11일부터는 전달…"'], color='amber', label_size=12, sub_size=11)
d.note(590, 486, 450, 66, ['남은 빚: 다시 열기 · 저장된 옛 날짜 재검사 · 기준일 하드코딩 · 타임존.', '회사별 마감이 필요해지면 마감 기간 테이블을 이 규칙 위에 얹는다.'], color='muted', size=12)
d.flow([{'path': [(285, 320), (285, 346)], 'color': 'blue', 'dur': 0.4},
        {'path': [(270, 371), (300, 371)], 'color': 'red', 'dur': 0.4, 'hold': 0.6},
        {'path': [(815, 320), (815, 346)], 'color': 'blue', 'dur': 0.4},
        {'path': [(935, 176), (935, 346)], 'color': 'blue', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2025/12/08-2.svg'))

# =====================================================================
# 2025/12/08-3  modules: dependency graph before/after
# =====================================================================
d = Diagram(1100, 620, '모듈 의존 그래프 — 엔티티가 웹 앱 안에 있던 구조에서 api → domain → core 로')
d.group(40, 86, 460, 500, '분리 전 (2025-06-30 ~ 12-07): 모듈 4개')
d.box(60, 120, 230, 150, 'erp-api', color='blue', label_size=14)
d.box(75, 150, 200, 108, color='amber', dashed=True)
d.lines(175, 170, ['엔티티 21 · 리포지토리 · Q클래스', '서비스 DTO · 컨트롤러 · 보안', 'Spring Batch 작업 + 스케줄러', '(배치가 웹 앱 안에 산다)'], size=11, weight=600, gap=18)
d.box(310, 120, 170, 70, 'account-api', ['엔티티 9 + 컨트롤러'], color='blue', label_size=14)
d.box(310, 210, 170, 60, 'batch-api', ['빈 껍데기'], color='muted', dashed=True, label_size=14)
d.box(60, 330, 420, 60, 'core', ['enum · BaseEntity · 공통 DTO · 설정'], color='gray', label_size=14)
d.arrow([(175, 270), (175, 330)], color='gray'); d.arrow([(395, 190), (395, 210)], color='muted', head=False, dashed=True); d.arrow([(395, 270), (395, 330)], color='gray')
d.note(60, 410, 420, 150, ['• batch-api 가 재고 엔티티를 쓰려면 erp-api(웹 앱)를 의존해야 한다', '• account-api 는 ERP 데이터를 JPA 로 못 읽어 HTTP DTO 로 우회', '• EmployeeRepositoryImpl 이 controller 의 요청 DTO 를 import', '  — 같은 모듈 안에서는 컴파일러가 아무 말도 하지 않는다'], color='red', size=12)
d.group(540, 86, 520, 500, '분리 후 (2025-12-08): 모듈 6개')
d.box(560, 120, 150, 60, 'erp-api', ['bootJar'], color='blue', label_size=14)
d.box(730, 120, 150, 60, 'account-api', ['bootJar'], color='blue', label_size=14)
d.box(900, 120, 140, 60, 'batch-api', ['bootJar'], color='blue', label_size=14)
d.box(560, 240, 220, 60, 'erp-domain', ['엔티티 21 · 리포지토리 · DTO · jar'], color='green', label_size=14)
d.box(810, 240, 230, 60, 'account-domain', ['엔티티 9 · 리포지토리 · DTO · jar'], color='green', label_size=14)
d.box(560, 360, 480, 60, 'core', ['enum · BaseEntity · 공통 DTO · 설정 (project deps 없음)'], color='gray', label_size=14)
d.arrow([(635, 180), (635, 240)], color='blue')
d.arrow([(805, 180), (860, 240)], color='blue')
d.arrow([(950, 180), (720, 240)], color='purple')
d.arrow([(990, 180), (960, 240)], color='purple')
d.arrow([(670, 300), (670, 360)], color='gray'); d.arrow([(925, 300), (925, 360)], color='gray')
d.arrow([(570, 180), (550, 200), (550, 340), (570, 360)], color='muted', dashed=True); d.arrow([(1030, 180), (1050, 200), (1050, 340), (1030, 360)], color='muted', dashed=True)
d.note(560, 440, 480, 120, ['• 의존 방향 api → domain → core. 리포지토리가 컨트롤러를 import 하면 빌드가 깨진다', '• implementation 만 사용 — core 를 api 모듈이 따로 선언 (점선)', '• batch-api 는 두 도메인을 모두, api 는 자기 도메인 하나만', '• scanBasePackages 에 도메인 패키지 추가 — @EntityScan 불필요'], color='green', size=12)
d.flow([{'path': [(950, 180), (720, 240)], 'color': 'purple', 'dur': 0.6},
        {'path': [(670, 300), (670, 360)], 'color': 'gray', 'dur': 0.4, 'hold': 0.3},
        {'path': [(990, 180), (960, 240)], 'color': 'purple', 'dur': 0.5},
        {'path': [(925, 300), (925, 360)], 'color': 'gray', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2025/12/08-3.svg'))

# =====================================================================
# 2025/12/08-4  modules: what moved where
# =====================================================================
d = Diagram(1100, 560, '무엇이 어디로 갔나 — 313개 파일, 이름 변경 223 · 추가 27 · 삭제 5 · 수정 58')
d.box(40, 110, 220, 150, 'erp-api', ['142개 파일 나감'], color='blue', label_size=15)
d.box(40, 300, 220, 110, 'account-api', ['66개 파일 나감'], color='blue', label_size=15)
d.box(840, 96, 220, 160, 'erp-domain', ['도메인 82 · DTO 41', 'TestUtils · schema.sql', '테스트 30'], color='green', label_size=15)
d.box(840, 286, 220, 110, 'account-domain', ['도메인 33 · DTO 16', 'TestUtils · sql 2 · 테스트 14'], color='green', label_size=15)
d.box(840, 426, 220, 60, 'batch-api', ['StockBatchConfig · Scheduler'], color='purple', label_size=15)
bands = [([(260, 150), (840, 140)], 'blue', '엔티티 21 · 리포지토리 + 구현 · 서비스 DTO 41', (550, 135)),
         ([(260, 200), (840, 200)], 'blue', '리포지토리·엔티티 테스트 30 (그대로 이동)', (550, 190)),
         ([(260, 245), (700, 245), (700, 456), (840, 456)], 'purple', '배치 작업·스케줄러 2 (유사도 88% / 92%)', (480, 235)),
         ([(260, 330), (840, 320)], 'green', '엔티티 9 · 리포지토리 · DTO 16 · 테스트 14', (470, 316)),
         ([(260, 380), (840, 370)], 'green', 'EmployeeQueryRequest: controller/request → domain/dto', (470, 366))]
for pts, c, lab, (lx, ly) in bands:
    d.arrow(pts, color=c, width=3)
    d.text(lx, ly, lab, size=11, weight=700, color=G[c])
d.note(40, 440, 640, 90, ['api 에 남은 것: 컨트롤러 · 서비스 · 보안/JWT · Swagger · Excel/PDF 출력', 'scanBasePackages: ["…erpapi", "…core"] → ["…erpapi", "…erpdomain", "…core"]', 'Q클래스는 kapt 가 모듈별로 돌아 엔티티 옆(erp-domain/build/generated) 에 생긴다'], color='muted', size=12)
d.flow([{'path': [(260, 150), (840, 140)], 'color': 'blue', 'dur': 1.0},
        {'path': [(260, 200), (840, 200)], 'color': 'blue', 'dur': 0.8},
        {'path': [(260, 245), (700, 245), (700, 456), (840, 456)], 'color': 'purple', 'dur': 1.2},
        {'path': [(260, 330), (840, 320)], 'color': 'green', 'dur': 0.8},
        {'path': [(260, 380), (840, 370)], 'color': 'green', 'dur': 0.8, 'hold': 0.8}])
d.save(out('2025/12/08-4.svg'))

# =====================================================================
# 2026/06/16-1  cookies: same name, two jars → 401 loop
# =====================================================================
d = Diagram(1100, 560, '같은 이름의 쿠키 둘 — 브라우저는 둘 다 보내고, BFF 는 하나만 읽고, 401 이 반복된다')
d.group(40, 96, 280, 170, '브라우저 쿠키 저장소')
d.box(55, 126, 250, 54, color='red'); d.lines(180, 146, ['refresh_token  (옛 토큰)', 'Domain=.example.com'], size=11, weight=600, mono=True)
d.box(55, 196, 250, 54, color='green'); d.lines(180, 216, ['refresh_token  (새 토큰)', 'Domain=svc-a.example.com'], size=11, weight=600, mono=True)
bff = d.group(430, 96, 300, 170, 'BFF  app/api/account/auth/token')
d.box(450, 126, 260, 50, 'RequestCookies', ['Map(name → value): 같은 이름은 하나만'], color='amber', label_size=13, sub_size=11)
d.box(450, 196, 260, 54, 'getRefreshToken(req)', ['→ 옛 토큰이 읽힘'], color='red', label_size=13, sub_size=11)
api = d.box(820, 126, 240, 124, 'Account API', ['POST /auth/token', '옛 토큰 → 401'], color='gray', label_size=14)
d.arrow([(320, 181), (430, 181)], color='gray')
d.lines(375, 138, ['Cookie:', 'refresh_token=옛;', 'refresh_token=새'], size=10, weight=700, gap=13, mono=True)
d.arrow([(580, 176), (580, 196)], color='amber')
d.arrow([(710, 223), (820, 223)], color='red', label='Bearer 옛 토큰', label_dy=-8, label_size=11)
d.arrow([(940, 250), (940, 300), (190, 300), (190, 266)], color='red', label='401 TOKEN_UNAUTHENTICATED — 호스트 쿠키만 지움, apex 쿠키는 남음 → 다음 요청이 같은 길', label_dy=14, label_size=11)
d.text(565, 320, '', size=1)
d.box(40, 350, 1020, 60, color='muted'); d.text(550, 372, 'RFC 6265: 쿠키의 식별자는 (이름, 도메인, 경로) — Domain 이 다르면 다른 쿠키라 공존하고 둘 다 전송된다', size=13, weight=600); d.text(550, 394, 'Next.js RequestCookies: 이름으로만 키잉된 Map — 둘 중 하나만 읽힌다. 어느 쪽인지는 브라우저의 헤더 순서에 달렸다', size=13, weight=600)
d.box(40, 430, 1020, 100, color='green')
d.text(550, 456, '수정(#374): 토큰 쿠키를 쓰는 모든 응답에 옛 apex 쿠키를 만료시키는 Set-Cookie 를 함께 보낸다', size=13, weight=700, color=G['green'])
d.text(550, 482, 'Set-Cookie: refresh_token=; Domain=.example.com; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT', size=12, weight=600, mono=True)
d.text(550, 508, '→ 한 번의 로그인·재발급·로그아웃 뒤 옛 쿠키가 사라진다. 그런데 이 "함께 보낸다"가 다음 사고를 불렀다 (그림 2)', size=12, weight=600, color=MUTED)
d.flow([{'path': [(320, 181), (430, 181)], 'color': 'gray', 'dur': 0.6},
        {'path': [(580, 176), (580, 196)], 'color': 'amber', 'dur': 0.3},
        {'path': [(710, 223), (820, 223)], 'color': 'red', 'dur': 0.5},
        {'path': [(940, 250), (940, 300), (190, 300), (190, 266)], 'color': 'red', 'dur': 1.2, 'hold': 0.4}], loop_pause=0.3)
d.save(out('2026/06/16-1.svg'))

# =====================================================================
# 2026/06/16-2  cookies: ResponseCookies Map overwrite
# =====================================================================
d = Diagram(1100, 640, 'ResponseCookies 의 Map 은 이름 하나에 슬롯 하나 — 두 번째 set 이 방금 발급한 토큰을 덮어쓴다')
d.group(40, 86, 1020, 250, '수정 전 (#384): res.cookies.set 두 번')
d.box(60, 120, 300, 60, '① res.cookies.set("access_token", 토큰,', ['{ domain: "svc-a-dev.example.com" })'], color='green', label_size=12, sub_size=11)
d.box(60, 200, 300, 60, '② res.cookies.set("access_token", "",', ['{ domain: ".example.com", expires: 0 })'], color='red', label_size=12, sub_size=11)
d.group(440, 120, 240, 140, '_parsed: Map', color='amber')
d.box(460, 160, 200, 40, color='green', dashed=True); d.text(560, 185, 'access_token → 토큰', size=11, weight=700, color=G['green'], mono=True)
d.box(460, 210, 200, 40, color='red'); d.text(560, 235, 'access_token → ""', size=11, weight=700, color=G['red'], mono=True)
d.text(560, 150, '키 = 이름', size=11, color=MUTED)
d.group(760, 120, 280, 140, 'Set-Cookie 헤더 (전선)', color='gray')
d.text(900, 170, 'replace(): headers.delete("set-cookie")', size=10, weight=600, color=MUTED, mono=True)
d.text(900, 190, '→ Map 에서 다시 쓴다', size=10, weight=600, color=MUTED)
d.box(780, 205, 240, 40, color='red'); d.text(900, 230, 'access_token=; Domain=.example.com', size=10, weight=700, color=G['red'], mono=True)
d.arrow([(360, 150), (440, 180)], color='green'); d.arrow([(360, 230), (440, 230)], color='red')
d.arrow([(680, 190), (760, 190)], color='gray')
d.text(560, 300, '로그인 200, 백엔드는 토큰을 발급했지만 브라우저에 닿은 Set-Cookie 는 만료된 apex 쿠키 하나 — Domain 이 달라도 슬롯은 하나다', size=12, weight=700, color=G['red'])
d.text(560, 322, '먼저 붙여 둔 원시 Set-Cookie 헤더도 replace() 의 delete 에 함께 지워진다', size=12, weight=600, color=MUTED)
d.group(40, 356, 1020, 260, '수정 후 (#389): 두 번째 쿠키는 Map 을 거치지 않는다')
d.box(60, 390, 300, 60, '① res.cookies.set("access_token", 토큰,', ['{ domain: "svc-a-dev.example.com" })'], color='green', label_size=12, sub_size=11)
d.box(60, 470, 300, 60, '② res.headers.append("set-cookie",', ['"access_token=; Domain=.example.com; Expires=…")'], color='blue', label_size=12, sub_size=11)
d.group(440, 384, 240, 66, '_parsed: Map', color='amber')
d.box(460, 418, 200, 26, color='green'); d.text(560, 435, 'access_token → 토큰', size=11, weight=700, color=G['green'], mono=True)
d.group(760, 390, 280, 140, 'Set-Cookie 헤더 (전선)', color='gray')
d.box(780, 430, 240, 36, color='green'); d.text(900, 453, 'access_token=토큰; Domain=svc-a-dev…', size=10, weight=700, color=G['green'], mono=True)
d.box(780, 476, 240, 36, color='blue'); d.text(900, 499, 'access_token=; Domain=.example.com', size=10, weight=700, color=G['blue'], mono=True)
d.arrow([(360, 420), (440, 420)], color='green'); d.arrow([(680, 420), (760, 448)], color='gray')
d.arrow([(360, 500), (720, 500), (780, 494)], color='blue', label='Map 우회, 원시 헤더로 직접', label_dy=14, label_size=11)
d.text(550, 566, '순서가 중요하다: append 는 마지막 cookies.set 뒤에. 그 뒤에 cookies.set 이 한 번이라도 더 오면 replace() 가 원시 헤더를 지운다', size=12, weight=700, color=G['blue'])
d.text(550, 592, '테스트도 바꿨다: res.cookies.set 을 jest.fn() 으로 모킹하면 Map 을 흉내 내지 못한다 → 실제 NextResponse + headers.getSetCookie() 로 검증', size=12, weight=600, color=MUTED)
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
d = Diagram(1100, 600, '재연결 플래핑 — deactivate() 가 onWebSocketClose 를 다시 부르고, onConnect 가 횟수를 0 으로 되돌린다')
d.group(40, 86, 300, 300, 'stompjs ActivationState')
d.box(90, 120, 200, 50, 'ACTIVE', ['activate() 뒤. 소켓 끊김으로는 안 바뀜'], color='green', label_size=14, sub_size=10)
d.box(90, 210, 200, 50, 'DEACTIVATING', ['deactivate() 호출 직후'], color='amber', label_size=14, sub_size=10)
d.box(90, 300, 200, 50, 'INACTIVE', ['소켓 닫힘 확인 뒤'], color='muted', label_size=14, sub_size=10)
d.arrow([(190, 170), (190, 210)], color='amber', label='deactivate()', label_dy=-4, label_size=11)
d.arrow([(190, 260), (190, 300)], color='muted')
d.arrow([(290, 325), (320, 325), (320, 145), (290, 145)], color='green', label='activate()', label_dy=-4, label_size=11)
d.text(190, 372, 'client.active === (state === ACTIVE)', size=11, weight=600, color=MUTED, mono=True)
# sequence on the right
d.box(400, 110, 180, 56, '네트워크 끊김 ✕', color='red', label_size=13)
d.box(640, 110, 200, 56, 'onWebSocketClose', ['attempt 0 → 1, 배너 ON'], color='gray', label_size=13, sub_size=11)
d.box(900, 110, 160, 56, '1초 타이머', color='gray', label_size=13)
d.box(900, 230, 160, 56, 'deactivate()', ['ACTIVE → DEACTIVATING'], color='amber', label_size=13, sub_size=11)
d.box(640, 230, 200, 56, 'onWebSocketClose (다시)', ['attempt 1 → 2, 타이머 또'], color='red', label_size=13, sub_size=11)
d.box(900, 350, 160, 56, 'activate()', color='green', label_size=13)
d.box(640, 350, 200, 56, 'onConnect', ['attempt = 0  ← 상한이 영원히 안 찬다'], color='green', label_size=13, sub_size=11)
d.arrow([(580, 138), (640, 138)], color='red'); d.arrow([(840, 138), (900, 138)], color='gray')
d.arrow([(980, 166), (980, 230)], color='gray')
d.arrow([(900, 258), (840, 258)], color='red', dashed=True)
d.text(870, 306, '앱 콜백을 보존해 그대로 호출', size=10, weight=700, color=G['red'])
d.arrow([(980, 286), (980, 350)], color='green', label='.then(() => activate())', label_dy=-4, label_size=10)
d.arrow([(900, 378), (840, 378)], color='green')
d.arrow([(740, 406), (740, 440), (490, 440), (490, 166)], color='red', dashed=True, label='다음 끊김 → 처음부터', label_dy=14, label_size=11)
d.box(400, 480, 660, 90, color='green')
d.text(730, 506, '수정(#349): onWebSocketClose 입구와 타이머 본문에  if (!client.active) return;', size=13, weight=700, color=G['green'])
d.text(730, 530, 'deactivate 중이면 state 가 DEACTIVATING → active=false → 재연결 안 함. 네트워크 끊김이면 ACTIVE 유지 → 한 번만 재연결', size=12, weight=600)
d.text(730, 554, '언마운트의 deactivate 도 같은 길이라 좀비 소켓까지 함께 사라졌다', size=12, weight=600, color=MUTED)
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
d = Diagram(1100, 620, 'STOMP 하트비트는 협상제 — 서버가 0,0 을 광고하면 클라이언트 설정은 무효가 된다')
cols = {'cl': 170, 'px': 500, 'sv': 830}
for key, label, sub in (('cl', '브라우저 (stompjs)', 'heartbeat 기본 10000,10000'), ('px', '프록시', 'idle 타임아웃 ≈ 60초'), ('sv', 'Spring SimpleBroker', 'TaskScheduler 없음')):
    d.box(cols[key] - 110, 86, 220, 50, label, [sub], color='gray', label_size=13, sub_size=11)
    d.arrow([(cols[key], 136), (cols[key], 570)], color='muted', head=False, dashed=True, width=1)
d.text(60, 170, '수정 전', size=13, weight=700, color=G['red'], anchor='start')
d.arrow([(cols['cl'], 180), (cols['sv'], 180)], color='blue', label='CONNECT  heart-beat:10000,10000', label_dy=-8, label_size=11)
d.arrow([(cols['sv'], 215), (cols['cl'], 215)], color='red', label='CONNECTED  heart-beat:0,0   ← 서버값이 0 이면 그 방향은 없음', label_dy=-8, label_size=11)
d.box(cols['cl'] - 100, 240, 200, 40, color='muted', dashed=True); d.text(cols['cl'], 265, 'pinger ✕   ponger ✕', size=12, weight=700, color=MUTED)
d.text(cols['px'], 262, '… 60초 동안 바이트 0 …', size=12, weight=600, color=MUTED)
d.arrow([(cols['px'], 300), (cols['cl'], 300)], color='red', label='FIN (idle) → onWebSocketClose → 배너 → 재연결 → 다시 idle …', label_dy=-8, label_size=11)
d.arrow([(cols['cl'] - 110, 335), (cols['sv'] + 110, 335)], color='muted', head=False, width=1)
d.text(60, 365, '수정 후 (#471)', size=13, weight=700, color=G['green'], anchor='start')
d.arrow([(cols['cl'], 380), (cols['sv'], 380)], color='blue', label='CONNECT  heart-beat:25000,25000', label_dy=-8, label_size=11)
d.arrow([(cols['sv'], 415), (cols['cl'], 415)], color='green', label='CONNECTED  heart-beat:25000,25000   → 양방향 max(25000, 25000) = 25초', label_dy=-8, label_size=11)
for i, y in enumerate((455, 490, 525)):
    d.arrow([(cols['cl'], y), (cols['sv'], y)], color='green', head=False, dashed=True, width=1)
    d.text(cols['px'] + 150, y - 6, f'25초 · LF ●  (양방향)  — 프록시 타이머 리셋', size=10, weight=600, color=G['green'])
d.box(40, 560, 1020, 50, color='amber')
d.text(550, 580, 'Spring: setHeartbeatValue(longArrayOf(25_000, 25_000)) 와 setTaskScheduler(ThreadPoolTaskScheduler) 둘 다 필요 — 하나만 넣으면 기동 시 Assert', size=12, weight=700)
d.text(550, 600, 'stompjs: heartbeatOutgoing≠0 && serverIncoming≠0 일 때만 PING, heartbeatIncoming≠0 && serverOutgoing≠0 일 때만 PONG 감시', size=11, weight=600, color=MUTED, mono=True)
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
d = Diagram(1100, 600, '첫 입장 레이스 — 직결 WebSocket 의 CONNECTED 가 BFF 경유 REST 보다 먼저 와서 빈 스토어에 쓰이고 사라진다')
d.text(60, 120, 'WS', size=14, weight=700, color=G['blue'], anchor='start')
d.text(60, 240, 'REST', size=14, weight=700, color=G['amber'], anchor='start')
d.arrow([(130, 130), (330, 130)], color='blue', width=6, head=False)
d.text(230, 92, '브라우저 → 백엔드 직결 1홉, JWT 서명만 검증', size=11, weight=600, color=G['blue'])
d.box(330, 100, 150, 56, 'CONNECTED', ['setConnectionStatus()'], color='blue', label_size=13, sub_size=11)
d.box(540, 100, 230, 56, 'conversations: {}', ['엔트리 없음 → 순회할 게 없음'], color='red', dashed=True, label_size=13, sub_size=11)
d.text(800, 134, '✕ 유실 (no-op)', size=13, weight=700, color=G['red'], anchor='start')
d.arrow([(480, 128), (540, 128)], color='blue')
d.arrow([(130, 250), (640, 250)], color='amber', width=6, head=False)
d.text(385, 238, '브라우저 → BFF 라우트 → 백엔드 → DB (30건 + 멘션·첨부·반응 조립) → BFF → 브라우저', size=11, weight=600, color=G['amber'])
d.box(640, 220, 170, 56, 'mergeHistory()', ['엔트리 생성'], color='amber', label_size=13, sub_size=11)
d.box(850, 220, 210, 56, 'connectionStatus:', ['"DISCONNECTED" (기본값)'], color='red', label_size=13, sub_size=11)
d.arrow([(810, 248), (850, 248)], color='amber')
d.text(550, 310, '연결은 이미 CONNECTED 라 상태 이벤트는 다시 오지 않는다 → 배너 고착 + 입력창 disabled. 방을 옮기면 REST 가 빨라져(워밍) 순서가 뒤집히므로 "처음 들어왔을 때만"', size=12, weight=600, color=MUTED)
d.group(40, 340, 500, 230, '수정 전: 연결 상태가 대화별 엔트리 안에')
d.lines(290, 380, ['conversations: {', '  "dm:7": { messages, readState,', '            connectionStatus }   ← 리소스별 복제', '}', 'setConnectionStatus: 기존 엔트리만 순회'], size=12, weight=600, gap=22, mono=True)
d.text(290, 520, '엔트리 생성 vs 상태 이벤트 도착의 순서 레이스', size=12, weight=700, color=G['red'])
d.group(580, 340, 480, 230, '수정 후 (#753): 스토어 최상위 필드')
d.lines(820, 380, ['conversations: { "dm:7": { messages, readState } }', 'connectionStatus: "CONNECTED"   ← 클라이언트 단위', '', 'setConnectionStatus: (s) => set({ connectionStatus: s })', 'useMessageStore((s) => s.connectionStatus)'], size=12, weight=600, gap=22, mono=True)
d.text(820, 520, '엔트리가 있든 없든 기록된다 → 레이스 소멸', size=12, weight=700, color=G['green'])
d.flow([{'path': [(130, 130), (330, 130)], 'color': 'blue', 'dur': 0.6, 'hold': 0.0},
        {'path': [(480, 128), (540, 128)], 'color': 'blue', 'dur': 0.3, 'hold': 2.1}], loop_pause=1.0)
d.flow([{'path': [(130, 250), (640, 250)], 'color': 'amber', 'dur': 2.2, 'hold': 0.0},
        {'path': [(810, 248), (850, 248)], 'color': 'amber', 'dur': 0.3, 'hold': 0.5}], loop_pause=1.0)
d.save(out('2026/07/24-3.svg'))

# =====================================================================
# 2026/07/28-1  unread: three failures
# =====================================================================
d = Diagram(1100, 620, '"프레임이 오면 +1" 이 틀리는 세 가지 방식 — 초깃값 없음, 두 토픽 팬아웃, 좀비 소켓')
panels = [(40, '① 콜드 로드 (06-16)', 'amber'), (385, '② DM 두 토픽 (07-24)', 'red'), (730, '③ 메일 좀비 소켓 (07-28)', 'red')]
for x, label, c in panels:
    d.group(x, 86, 330, 440, label)
# panel 1
d.box(60, 130, 130, 70, '서버 DB', ['안읽음 5'], color='gray', label_size=13)
d.box(240, 130, 110, 70, 'counts', ['{}  → 0'], color='amber', label_size=13)
d.arrow([(190, 165), (240, 165)], color='muted', dashed=True, label='집계 API 없음 ✕', label_dy=-8, label_size=11)
d.note(60, 230, 290, 120, ['배지는 "이 세션에서 받은 프레임 수".', '새로고침하면 0. 다른 기기에서 읽어도', '줄지 않는다. 알고 넘어간 한계.'], color='amber', size=12)
d.text(205, 400, '필요한 것: 서버가 세는 숫자', size=12, weight=700, color=MUTED)
# panel 2
d.box(405, 130, 130, 50, '서버', ['DM 메시지 1건'], color='gray', label_size=13)
d.box(585, 110, 110, 40, '/topic/dm.7', color='blue', label_size=11)
d.box(585, 170, 110, 40, '/topic/user.42', color='purple', label_size=11)
d.arrow([(535, 150), (585, 130)], color='blue'); d.arrow([(535, 160), (585, 190)], color='purple')
d.box(425, 250, 270, 60, 'increment("dm:7")  ×2', ['메시지 id 를 모른다 → dedup 불가'], color='red', label_size=13, sub_size=11)
d.arrow([(695, 130), (712, 130), (712, 262), (695, 262)], color='blue'); d.arrow([(620, 210), (620, 250)], color='purple')
d.box(425, 330, 270, 44, '배지 2  (말풍선은 id dedup 으로 1개)', color='red', label_size=12)
d.note(405, 400, 290, 100, ['수정: user 이벤트는 "아직 목록에 없는 신규', 'DM 방"만 센다. 기존 방은 dm 토픽에 맡긴다.'], color='green', size=12)
# panel 3
d.box(750, 130, 130, 50, '브로커', ['NEW_MAIL 1프레임'], color='gray', label_size=13)
d.box(930, 110, 110, 36, '클라이언트 B', color='green', label_size=11)
d.box(930, 156, 110, 36, 'A (좀비)', color='red', dashed=True, label_size=11)
d.box(930, 202, 110, 36, "A′ (좀비)", color='red', dashed=True, label_size=11)
for y in (128, 174, 220): d.arrow([(880, 155), (930, y)], color='gray')
d.box(770, 260, 270, 60, 'incrementUnread()  ×(1 + 좀비 수)', ['resetUnread 호출 운영 코드 0건'], color='red', label_size=12, sub_size=11)
d.arrow([(985, 238), (985, 260)], color='red')
d.box(770, 340, 270, 44, '실제 1통 → 배지 4', color='red', label_size=12)
d.note(750, 400, 290, 100, ['StrictMode 를 의심했지만 결백.', '진짜 중복: 가드 없는 재연결 → 좀비 소켓.', '결론: 카운터 삭제, 서버 집계로.'], color='green', size=12)
d.box(40, 546, 1020, 50, color='muted'); d.text(550, 566, '공통 뿌리: "이벤트 도착 횟수"를 "읽지 않은 개수"로 착각했다', size=14, weight=700); d.text(550, 586, '숫자는 서버가 세고, 실시간 이벤트는 "다시 물어보라"는 신호일 뿐이어야 한다', size=12, weight=600, color=MUTED)
d.flow([{'path': [(535, 150), (585, 130)], 'color': 'blue', 'dur': 0.4}, {'path': [(695, 130), (712, 130), (712, 262), (695, 262)], 'color': 'blue', 'dur': 0.5, 'hold': 0.1},
        {'path': [(535, 160), (585, 190)], 'color': 'purple', 'dur': 0.4}, {'path': [(620, 210), (620, 250)], 'color': 'purple', 'dur': 0.4, 'hold': 0.6},
        {'path': [(880, 155), (930, 128)], 'color': 'gray', 'dur': 0.3}, {'path': [(880, 155), (930, 174)], 'color': 'red', 'dur': 0.3}, {'path': [(880, 155), (930, 220)], 'color': 'red', 'dur': 0.3},
        {'path': [(985, 238), (985, 260)], 'color': 'red', 'dur': 0.3, 'hold': 0.8}])
d.save(out('2026/07/28-1.svg'))

# =====================================================================
# 2026/07/28-2  unread: zombie socket sequence
# =====================================================================
d = Diagram(1100, 660, '좀비 소켓 — 폴더 이동으로 닫힌 클라이언트 A 가 가드 없는 close 핸들러 때문에 1초 뒤 되살아난다')
L = {'fx': 130, 'a': 400, 'b': 620, 'br': 880}
for k, label, c in (('fx', 'React effect', 'gray'), ('a', '클라이언트 A', 'red'), ('b', '클라이언트 B', 'green'), ('br', 'Spring 브로커', 'gray')):
    d.box(L[k] - 80, 86, 160, 40, label, color=c, label_size=13)
    d.arrow([(L[k], 126), (L[k], 500)], color='muted', head=False, dashed=True, width=1)
steps = [
    (150, L['fx'], L['a'], 'gray', '① 폴더 이동 → cleanup → A.deactivate()'),
    (185, L['a'], L['br'], 'gray', '② DISCONNECT receipt:close-1'),
    (220, L['br'], L['a'], 'gray', '③ RECEIPT → 소켓 close → onWebSocketClose (가드 없음)'),
    (265, L['fx'], L['b'], 'green', '④ 새 effect → B.activate() → SUBSCRIBE /topic/mail.42'),
    (310, L['a'], L['a'] + 120, 'red', '⑤ 1초 뒤 A.deactivate().then(A.activate())  ← 좀비'),
    (350, L['a'], L['br'], 'red', '⑥ A: CONNECT → 옛 클로저의 subscribe(A) → SUBSCRIBE /topic/mail.42'),
    (410, L['br'], L['b'], 'green', '⑦ NEW_MAIL → B: incrementUnread()'),
    (445, L['br'], L['a'], 'red', '⑦ NEW_MAIL → A(좀비): incrementUnread()  → +2'),
]
for y, x1, x2, c, lab in steps:
    if x1 == L['a'] and x2 == L['a'] + 120:
        d.arrow([(x1, y - 14), (x2, y - 14), (x2, y + 14), (x1, y + 14)], color=c)
        d.text(x2 + 10, y + 4, lab, size=11, weight=700, color=G[c], anchor='start')
    else:
        d.arrow([(x1, y), (x2, y)], color=c)
        d.text((x1 + x2) / 2, y - 8, lab, size=11, weight=700, color=G[c])
d.text(880, 490, 'Provider 가 3개 레이아웃에 각각 마운트 → 섹션 이동마다 영구 좀비 +1', size=11, weight=600, color=MUTED)
d.group(40, 520, 1020, 120, 'StrictMode 는 결백했다 (소스 확인)')
d.lines(550, 560, ['React 18.3.1: mount → cleanup → mount 를 flushPassiveEffectsImpl 안에서 동기 실행 — 사이에 마이크로태스크가 끼지 않는다',
                   'stompjs 7.3.0 _connect(): await beforeConnect 뒤 if (!this.active) return — activate 직후 동기 deactivate 면 첫 클라이언트는 소켓을 열지 않는다',
                   '→ StrictMode 로 생기는 건 backfill() 중복 호출뿐. 중복 구독의 진짜 경로는 ③→⑤ 의 가드 없는 재연결이었다'], size=12, weight=600, gap=22)
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
d = Diagram(1100, 560, '숫자는 서버가 센다, 이벤트는 무효화만 — countUnreadGroupedByFolder 와 invalidateQueries')
d.group(40, 96, 200, 180, '옛 모델')
d.box(60, 130, 160, 40, 'NEW_MAIL 프레임', color='muted', label_size=12)
d.arrow([(140, 170), (140, 200)], color='muted', label='+1', label_dy=-2, label_size=11)
d.box(60, 200, 160, 40, 'unreadCount', color='muted', label_size=12)
d.text(140, 262, '세션 카운터 — 틀린다', size=11, weight=600, color=MUTED)
d.group(290, 96, 360, 400, '서버')
d.box(310, 130, 320, 70, 'mail_message ⟕ mail_message_flag', ['owner · ACTIVE · INBOUND · NOT EXISTS(isRead=true)'], color='gray', label_size=13, sub_size=11)
d.box(310, 230, 320, 56, 'countUnreadGroupedByFolder(owner)', ['GROUP BY folderId → Map<folderId, count>'], color='green', label_size=13, sub_size=11)
d.box(310, 316, 320, 56, 'GET /folders', ['MailFolderResponse.unreadCount'], color='green', label_size=13, sub_size=11)
d.box(310, 402, 320, 56, 'STOMP /topic/mail.{user}', ['NEW_MAIL · MAIL_STATE_CHANGED'], color='blue', label_size=13, sub_size=11)
d.arrow([(470, 200), (470, 230)], color='gray'); d.arrow([(470, 286), (470, 316)], color='green')
d.group(700, 96, 360, 400, '브라우저')
d.box(720, 130, 320, 56, 'useFolders() (react-query)', ['folder.unreadCount 를 그대로 표시'], color='green', label_size=13, sub_size=11)
d.box(720, 216, 320, 56, 'UnreadBadge', ['모든 폴더, 0 이면 숨김, 99+'], color='green', label_size=13, sub_size=11)
d.box(720, 316, 320, 56, 'invalidateQueries(folderKeys.all)', ['NEW_MAIL · 상태 변경 · 읽음 처리 성공 시'], color='amber', label_size=13, sub_size=11)
d.box(720, 402, 320, 56, 'useMailRealtime', ['프레임을 받아도 숫자는 안 건드린다'], color='blue', label_size=13, sub_size=11)
d.arrow([(630, 344), (680, 344), (680, 158), (720, 158)], color='green', label='refetch', label_dy=-8, label_size=11)
d.arrow([(880, 186), (880, 216)], color='green')
d.arrow([(630, 430), (720, 430)], color='blue')
d.arrow([(880, 402), (880, 372)], color='amber')
d.arrow([(720, 344), (690, 344), (690, 300), (660, 300), (660, 344), (630, 344)], color='amber', head=False, width=1, dashed=True)
d.text(550, 520, '초깃값은 첫 조회가 채우고, 다른 기기에서 읽으면 다음 무효화 때 줄고, 프레임이 몇 번 오든(좀비 소켓이 있어도) 숫자는 서버 집계 하나다', size=12, weight=700, color=G['green'])
d.text(550, 544, '함정: /folders 는 공용 ListResponse 래퍼라 SpringDoc 스펙에 필드가 안 떠서 수기 타입에 unreadCount 를 직접 추가', size=11, weight=600, color=MUTED)
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
d = Diagram(1100, 600, '무중단 4단계 — 각 단계가 끝난 상태에서 옛 주소와 새 주소가 모두 동작한다')
cols4 = [(275, '① 앱 배포', 'basePath + redirects(basePath:false)'), (505, '② Caddy', 'path /svc /svc/* → 컨테이너 (접두 유지)'), (735, '③ 링크 전환', 'PATH_HOSTED_SERVICES 에 추가'), (965, '④ 정리', '옛 호스트 블록 제거')]
for x, label, sub in cols4:
    d.box(x - 105, 90, 210, 56, label, [sub], color='gray', label_size=14, sub_size=10)
d.text(40, 200, '옛 주소', size=13, weight=700, anchor='start'); d.text(40, 218, 'svc.example.com', size=10, color=MUTED, anchor='start', mono=True)
d.text(40, 330, '새 주소', size=13, weight=700, anchor='start'); d.text(40, 348, 'example.com/svc', size=10, color=MUTED, anchor='start', mono=True)
old = [('/x → 307 → /svc/x', '동작', 'amber'), ('그대로', '동작', 'amber'), ('링크는 안 나가지만', '응답은 계속', 'amber'), ('호스트 삭제', '(사라짐)', 'muted')]
new = [('Caddy 핸들 없음', '→ 포털 404/로그인', 'red'), ('handle @svc → 컨테이너', '동작', 'green'), ('모든 링크가 여기로', '동작', 'green'), ('유일한 주소', '동작', 'green')]
for i, ((a1, a2, c1), (b1, b2, c2)) in enumerate(zip(old, new)):
    x = cols4[i][0]
    d.box(x - 105, 170, 210, 80, a1, [a2], color=c1, label_size=12, sub_size=11, dashed=(c1 == 'muted'))
    d.box(x - 105, 300, 210, 80, b1, [b2], color=c2, label_size=12, sub_size=11)
for i in range(3):
    x = cols4[i][0] + 105
    d.arrow([(x, 210), (x + 20, 210)], color='muted'); d.arrow([(x, 340), (x + 20, 340)], color='muted')
d.box(40, 420, 1020, 50, color='muted')
d.text(550, 440, '누가 무엇을 배포하나:  ① 앱 이미지   ② Caddy 리로드   ③ 공유 패키지 → 앱 이미지   ④ Caddy 리로드 (+ DNS)', size=12, weight=600)
d.text(550, 460, '어떤 두 단계도 같은 순간에 일어날 필요가 없다 — 그 사이의 몇 분 동안도 서비스는 열려 있다', size=12, weight=600, color=MUTED)
d.note(40, 486, 1020, 90, ['실제 순서: 10-02 밤 관리자 앱 ① → 10-03 새벽 관리자·운영 ③ → 나머지 4개 ① (푸시 앱은 한 PR 로) → 오전 6개 전부 ③ → 오후 ④ (dev, prd)',
                           '선행 조건: 메신저·메일 백엔드 CORS 허용 출처에 포털 호스트 추가 (WebSocket 핸드셰이크 403 → 101)', '덤: 새 주소는 환경 변수가 아니라 요청 Host 에서 유도한다 — dev/prd/로컬이 같은 코드'], color='green', size=12)
d.flow([{'path': [(170, 160), (380, 160)], 'color': 'blue', 'dur': 0.8, 'hold': 0.3}, {'path': [(400, 160), (610, 160)], 'color': 'blue', 'dur': 0.8, 'hold': 0.3},
        {'path': [(630, 160), (840, 160)], 'color': 'blue', 'dur': 0.8, 'hold': 0.3}, {'path': [(860, 160), (1070, 160)], 'color': 'blue', 'dur': 0.8, 'hold': 0.8}])
d.save(out('2026/10/04-1.svg'))

# =====================================================================
# 2026/10/04-2  basepath: where the prefix comes from
# =====================================================================
d = Diagram(1100, 640, '접두는 어디서 붙나 — Next 가 붙여 주는 것, 우리가 붙여야 하는 것, 미들웨어에서 벗겨지는 것')
d.group(40, 86, 300, 420, '브라우저 (basePath: "/svc")')
em = [('<Link href="/x">', 'green', '✓ Next'), ('router.push("/x")', 'green', '✓ Next'), ('fetch("/api/x")', 'red', '✗ → 전역 패치'), ('<img src="/logo.png">', 'red', '✗ → withBasePath()'), ('window.location = "/login"', 'red', '✗ → withBasePath()')]
for i, (lab, c, note) in enumerate(em):
    y = 120 + i * 72
    d.box(60, y, 260, 54, color=c); d.text(190, y + 22, lab, size=12, weight=700, mono=True); d.text(190, y + 42, note, size=11, weight=600, color=G[c])
d.box(400, 264, 200, 54, 'installBasePathFetch()', ['instrumentation-client.ts'], color='amber', label_size=12, sub_size=10)
d.box(400, 336, 200, 54, 'withBasePath()', ['"/…" 만, //host·https: 제외'], color='amber', label_size=12, sub_size=10)
d.arrow([(320, 291), (400, 291)], color='red'); d.arrow([(320, 363), (400, 363)], color='red'); d.arrow([(320, 435), (380, 435), (380, 376), (400, 376)], color='red')
d.box(680, 200, 160, 220, 'Caddy', ['path /svc /svc/*', '접두 유지 (handle)', '', '그 외 → 포털'], color='gray', label_size=14, sub_size=11)
for y in (147, 219): d.arrow([(320, y), (680, y + 100)], color='green')
d.arrow([(600, 291), (680, 300)], color='amber'); d.arrow([(600, 363), (680, 340)], color='amber')
d.text(500, 170, '/svc/x', size=12, weight=700, color=G['green'], mono=True)
d.text(640, 283, '/svc/api/x', size=11, weight=700, color=G['amber'], mono=True)
d.group(900, 160, 160, 300, 'Next 서버', color='blue'); d.text(980, 206, 'basePath: "/svc"', size=11, weight=600, color=MUTED, mono=True)
d.box(915, 230, 130, 210, color='purple', dashed=True)
d.lines(980, 258, ['미들웨어', 'nextUrl.pathname', '= "/x"', '(접두 벗겨짐)', '', '절대 URL 만들 때', 'nextUrl.basePath', '다시 붙이기'], size=11, weight=600, gap=20)
d.arrow([(840, 310), (900, 310)], color='gray')
d.box(400, 460, 660, 60, color='red'); d.text(730, 484, '리다이렉트가 누락을 가린다: 옛 서브도메인에서는 접두 없는 /api/x 가 307 로 /svc/api/x 에 가서 멀쩡히 동작', size=12, weight=700, color=G['red']); d.text(730, 506, '포털 호스트에서는 같은 요청이 포털에 가 404 — Jest 는 basePath 없이 돈다', size=12, weight=600)
d.box(40, 540, 1020, 70, color='green'); d.text(550, 566, '검증: `/svc/*` 만 넘기고 나머지는 404 인 프록시 뒤에서 Chrome 으로 화면을 전부 돌고 프록시 로그의 404 를 본다 (접두 밖 요청 0건 확인)', size=12, weight=700, color=G['green']); d.text(550, 592, '재발 방지: src= · window.open · <a href> · XHR 의 접두 없는 "/…" 리터럴을 grep 하는 테스트', size=12, weight=600, color=MUTED)
d.flow([{'path': [(320, 147), (680, 247)], 'color': 'green', 'dur': 0.7},
        {'path': [(320, 291), (400, 291)], 'color': 'red', 'dur': 0.3}, {'path': [(600, 291), (680, 300)], 'color': 'amber', 'dur': 0.3},
        {'path': [(320, 435), (380, 435), (380, 376), (400, 376)], 'color': 'red', 'dur': 0.4}, {'path': [(600, 363), (680, 340)], 'color': 'amber', 'dur': 0.3},
        {'path': [(840, 310), (900, 310)], 'color': 'gray', 'dur': 0.3, 'hold': 0.8}])
d.save(out('2026/10/04-2.svg'))

# =====================================================================
# 2026/10/04-3  basepath: service worker token churn
# =====================================================================
d = Diagram(1100, 620, '한 출처에 서비스워커 4개 — 같은 appId 의 토큰 레코드 하나를 서로 덮어쓴다')
d.group(40, 86, 1020, 240, '수정 전: 앱마다 /<svc>/firebase-messaging-sw.js 등록 (scope /<svc>/)')
for i, s in enumerate(('svc-a', 'messenger', 'mail', 'svc-b')):
    x = 60 + i * 180
    d.box(x, 120, 160, 60, f'SW scope /{s}/', ['PushSubscription', f'endpoint #{i + 1}'], color='blue', label_size=12, sub_size=10)
    d.arrow([(x + 80, 180), (x + 80, 220), (880, 220), (880, 240)], color='blue' if i == 3 else 'muted', head=(i == 3), width=1)
d.box(780, 240, 260, 70, 'IndexedDB 토큰 레코드', ['키 = appId (출처당 하나)', 'endpoint #4 ≠ 저장된 #3 → 삭제 후 재발급'], color='red', label_size=12, sub_size=10)
d.note(60, 240, 680, 70, ['getToken(): 현재 등록의 endpoint/auth/p256dh 가 저장된 것과 다르면 requestDeleteToken 뒤 새 토큰.', '사용자가 앱을 옮길 때마다 직전 앱의 토큰이 서버에서 지워진다 → 마지막에 연 앱만 푸시를 받는다.'], color='red', size=12)
d.group(40, 350, 1020, 250, '수정 후 (#1635): 포털이 서빙하는 루트 서비스워커 하나 (scope /)')
d.box(60, 384, 260, 60, 'SW scope /', ['/firebase-messaging-sw.js (포털)', 'PushSubscription 하나'], color='green', label_size=13, sub_size=10)
d.box(380, 384, 260, 60, 'IndexedDB 토큰 레코드', ['키 = appId, 등록 하나 → 안정'], color='green', label_size=13, sub_size=10)
d.arrow([(320, 414), (380, 414)], color='green')
d.box(700, 384, 340, 60, 'notificationclick', ['payload.data.service 로 /<svc>/… 라우팅'], color='amber', label_size=13, sub_size=10)
for i, s in enumerate(('svc-a', 'messenger', 'mail', 'svc-b')):
    x = 60 + i * 250
    d.box(x, 470, 220, 44, f'/{s}', ['serviceWorkerPath() → 포털 호스트면 루트'], color='blue', label_size=12, sub_size=10)
    d.arrow([(x + 110, 470), (x + 110, 456), (190, 456), (190, 444)], color='muted', head=False, width=1)
d.arrow([(870, 444), (870, 470)], color='amber', head=False, width=1)
d.text(550, 545, '소스는 공유 패키지에 하나, 각 앱 public/ 으로 동기화. 자기 출처의 다른 scope 에 남은 우리 워커 등록은 unregisterStale() 로 해제', size=12, weight=600)
d.text(550, 570, '서비스워커는 PATH_HOSTED_SERVICES 를 모른다 → 푸시를 쓰는 4개 앱은 ①과 ③을 한 PR 로 함께 옮겼다', size=12, weight=700, color=G['amber'])
d.flow([{'path': [(140, 180), (140, 220), (880, 220), (880, 240)], 'color': 'blue', 'dur': 1.0, 'hold': 0.3},
        {'path': [(680, 180), (680, 220), (880, 220), (880, 240)], 'color': 'red', 'dur': 0.7, 'hold': 0.8},
        {'path': [(320, 414), (380, 414)], 'color': 'green', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2026/10/04-3.svg'))

# =====================================================================
# 2026/10/20-1  next start: two pipes
# =====================================================================
d = Diagram(1100, 640, 'next build 는 설정을 두 갈래로 내보낸다 — 매니페스트에 구워지는 것과 next start 가 런타임에 다시 읽는 것')
d.box(40, 120, 170, 70, 'next.config.ts', ['basePath, images,', 'redirects(), env …'], color='gray', label_size=14, sub_size=11)
d.box(270, 120, 150, 70, 'next build', color='blue', label_size=15)
d.arrow([(210, 155), (270, 155)], color='gray')
d.box(480, 96, 260, 110, '.next/routes-manifest.json', ['redirects · headers · rewrites', 'basePath (복사본, 라우팅엔 안 씀)'], color='green', label_size=12, sub_size=11)
d.box(480, 220, 260, 56, 'middleware-manifest · 번들', ['matcher · env (DefinePlugin 인라인)'], color='green', label_size=12, sub_size=11)
d.box(480, 290, 260, 70, 'required-server-files.json', ['설정 전체 직렬화 —', 'next start 는 실험 플래그 1개만 읽음'], color='muted', label_size=12, sub_size=11)
d.arrow([(420, 140), (480, 150)], color='green'); d.arrow([(420, 160), (480, 248)], color='green'); d.arrow([(420, 180), (480, 325)], color='muted')
d.group(800, 86, 260, 290, '컨테이너: next start')
d.box(820, 120, 220, 50, 'routes-manifest ✓', ['항상 있음 → 리다이렉트 동작'], color='green', label_size=12, sub_size=10)
d.box(820, 186, 220, 50, 'next.config.* (cwd)', ['없음 → 경고 없이 기본값'], color='red', dashed=True, label_size=12, sub_size=10)
d.box(820, 252, 220, 36, 'basePath = ""', color='red', label_size=12)
d.box(820, 298, 220, 36, 'images.remotePatterns = []', color='red', label_size=12)
d.box(820, 344, 220, 24, color='muted'); d.text(930, 360, 'loadConfig: findUp → 기본값', size=10, weight=600, color=MUTED, mono=True)
d.arrow([(740, 150), (820, 145)], color='green'); d.arrow([(740, 210), (820, 210)], color='red', dashed=True)
d.box(40, 400, 500, 90, '① 08-27  이미지 400', ['remotePatterns 기본값 → /_next/image 가 외부 URL 거부', '설정은 required-server-files 에 있었지만 거기서 읽지 않는다'], color='red', label_size=13, sub_size=11)
d.box(560, 400, 500, 90, '② 10-02  /admin/* 전부 404', ['redirects(매니페스트)는 살아 /health → 307 → /admin/health', 'basePath(설정) 는 없어 404. 리다이렉트만 동작하는 반쪽 상태'], color='red', label_size=13, sub_size=11)
d.box(40, 510, 1020, 100, color='purple')
d.text(550, 536, '추기 (11-04): output: "standalone" — 설정이 server.js 안에 직렬화되어 __NEXT_PRIVATE_STANDALONE_CONFIG 로 들어간다', size=13, weight=700, color=G['purple'])
d.text(550, 560, 'loadConfig() 는 파일을 찾지 않고 그 값을 쓴다 → 런타임에 설정 파일도, pnpm 도, TypeScript 도 필요 없음', size=12, weight=600)
d.text(550, 584, '이미지 1~1.6GB → 약 300MB (339 / 312 / 310MB 로컬 측정)', size=12, weight=600, color=MUTED)
d.flow([{'path': [(210, 155), (270, 155)], 'color': 'gray', 'dur': 0.4},
        {'path': [(420, 140), (480, 150)], 'color': 'green', 'dur': 0.4}, {'path': [(740, 150), (820, 145)], 'color': 'green', 'dur': 0.5},
        {'path': [(420, 180), (480, 325)], 'color': 'muted', 'dur': 0.5, 'hold': 0.4},
        {'path': [(740, 210), (820, 210)], 'color': 'red', 'dur': 0.5, 'hold': 1.0}])
d.save(out('2026/10/20-1.svg'))

# =====================================================================
# 2026/10/20-2  next start: root built it, node runs it
# =====================================================================
d = Diagram(1100, 640, '루트가 빌드하고 node 가 실행한다 — $HOME 캐시와 디렉터리 소유권이 USER 경계를 넘지 못한다')
d.group(40, 86, 500, 290, '③-1  corepack 캐시 미스 → 기동 멈춤')
d.box(60, 120, 220, 56, 'RUN pnpm install --prod', ['root 로 실행'], color='gray', label_size=12, sub_size=11)
d.box(300, 120, 220, 56, '/root/.cache/node/corepack', ['pnpm@9.15.9 저장'], color='gray', label_size=11, sub_size=11)
d.arrow([(280, 148), (300, 148)], color='gray')
d.arrow([(60, 196), (520, 196)], color='red', head=False, dashed=True); d.text(290, 190, 'USER node', size=11, weight=700, color=G['red'])
d.box(60, 214, 220, 56, 'CMD pnpm … start', ['node 로 실행'], color='blue', label_size=12, sub_size=11)
d.box(300, 214, 220, 56, '/home/node/.cache/…', ['비어 있음 → 네트워크로'], color='red', label_size=11, sub_size=11)
d.arrow([(280, 242), (300, 242)], color='blue')
d.box(300, 290, 220, 50, 'registry.npmjs.org  ✕', ['dev 호스트에서 차단 → 영원히 대기'], color='red', dashed=True, label_size=12, sub_size=10)
d.arrow([(410, 270), (410, 290)], color='red')
d.text(170, 320, '"! Corepack is about to download …"', size=10, weight=600, color=MUTED, mono=True)
d.text(170, 340, 'next start 에 도달하지 못함', size=11, weight=700, color=G['red'])
d.group(580, 86, 480, 290, '③-2  루트 소유 cwd → 모든 BFF 가 HTML 500')
d.box(600, 120, 200, 56, 'COPY apps/<app>/', ['root 소유'], color='gray', label_size=12, sub_size=11)
d.box(840, 120, 200, 56, 'chown .next 만', ['(#1931)'], color='amber', label_size=12, sub_size=11)
d.arrow([(600, 196), (1040, 196)], color='red', head=False, dashed=True); d.text(820, 190, 'USER node', size=11, weight=700, color=G['red'])
d.box(600, 214, 200, 56, 'utils/logger.ts', ['모듈 로드 시 mkdir <cwd>/log'], color='blue', label_size=12, sub_size=11)
d.box(840, 214, 200, 56, 'EACCES', ['라우트 모듈 로드 실패'], color='red', label_size=12, sub_size=11)
d.arrow([(800, 242), (840, 242)], color='red')
d.box(600, 290, 200, 50, '/api/** → HTML 500', ['핸들러 JSON 이 아니다 = 모듈이 안 올라옴'], color='red', label_size=12, sub_size=10)
d.box(840, 290, 200, 50, '/health → 200', ['로거를 import 하지 않는 페이지'], color='green', label_size=12, sub_size=10)
d.arrow([(940, 270), (940, 290)], color='green', head=False, width=1); d.arrow([(700, 270), (700, 290)], color='red')
d.box(40, 400, 500, 100, '수정 (#1935)', ['ENV COREPACK_HOME=/opt/corepack   — root 홈 밖, 공유 경로', 'ENV COREPACK_ENABLE_NETWORK=0     — 캐시 미스를 "멈춤"이 아니라 "즉시 실패"로', '최소 node:20-slim + packageManager 이미지로 재현'], color='green', label_size=13, sub_size=11)
d.box(580, 400, 480, 100, '수정 (#1939)', ['RUN mkdir -p apps/<app>/log && chown -R node:node .next log', '헬스체크는 실제 의존성(로거·BFF)을 지나는 경로여야 한다 — 아직 못 함'], color='green', label_size=13, sub_size=11)
d.box(40, 520, 1020, 90, color='muted')
d.text(550, 546, '비루트 전환 점검 목록', size=13, weight=700)
d.text(550, 570, '① $HOME 에 의존하는 캐시(corepack · npm · pnpm store)는 공유 경로로 빼거나 런타임에 쓰지 않는다   ② cwd 아래 쓰기 디렉터리(.next/cache · log · 임시)는 미리 만들고 소유권을 준다', size=11, weight=600)
d.text(550, 592, '③ 세 사고 모두 로컬 재현 불가 — 레지스트리의 이미지를 받아 띄워 본다', size=11, weight=600, color=MUTED)
d.flow([{'path': [(280, 148), (300, 148)], 'color': 'gray', 'dur': 0.3},
        {'path': [(280, 242), (300, 242)], 'color': 'blue', 'dur': 0.3},
        {'path': [(410, 270), (410, 290)], 'color': 'red', 'dur': 0.4, 'hold': 0.8},
        {'path': [(800, 242), (840, 242)], 'color': 'red', 'dur': 0.3},
        {'path': [(700, 270), (700, 290)], 'color': 'red', 'dur': 0.3, 'hold': 0.8}])
d.save(out('2026/10/20-2.svg'))

print('ok')
