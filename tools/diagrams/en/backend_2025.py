"""English diagrams for four 2025 backend posts (English copy of the 2025 blocks in
tools/diagrams/make_diagrams_batch2.py).

  soft-delete-status-column        2025/06/16-1, 16-2
  pdfbox-transaction-statement     2025/12/05-1, 05-2
  date-based-period-lock           2025/12/08-1, 08-2
  gradle-domain-api-module-split   2025/12/08-3, 08-4

Run: python3 tools/diagrams/en/backend_2025.py "$PWD"
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from diag import Diagram, INK, MUTED

ROOT = sys.argv[1]
def out(rel):
    p = os.path.join(ROOT, 'assets/img/en', rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

G = {'gray': '#1f2937', 'muted': '#6b7280', 'blue': '#2563eb', 'green': '#059669', 'red': '#dc2626', 'amber': '#d97706', 'purple': '#7c3aed'}

def rows(d, x, y, w, items, h=26, size=12, mono=True, colors=None):
    """Small table: one string per row."""
    for i, s in enumerate(items):
        c = (colors or {}).get(i, 'gray')
        d.box(x, y + i * h, w, h, color=c)
        d.text(x + 10, y + i * h + h / 2 + 4, s, size=size, weight=600, anchor='start', mono=mono)

# =====================================================================
# 2025/06/16-1  soft delete: three ways
# =====================================================================
d = Diagram(1100, 600, 'Three ways to forget a row: hard delete, deleted_at, a status column')
lanes = [(40, 'A. Hard delete', 'red'), (385, 'B. deleted_at timestamp', 'amber'), (730, 'C. Status enum column (chosen)', 'green')]
for x, label, c in lanes:
    d.box(x, 86, 330, 38, label, color=c)
    rows(d, x + 20, 140, 290, ['1  Steel A      ACTIVE', '2  Steel B      ACTIVE', '3  Steel C      ACTIVE'])
    d.arrow([(x + 165, 222), (x + 165, 262)], color=c)
    d.text(x + 180, 246, '"Delete" row 2', size=11, weight=700, color=G[c], anchor='start')
rows(d, 60, 270, 290, ['1  Steel A      ACTIVE', '3  Steel C      ACTIVE'])
d.box(60, 322, 290, 26, color='red', dashed=True); d.text(205, 339, '(row 2 is gone)', size=12, color=G['red'])
rows(d, 405, 270, 290, ['1  Steel A  deleted_at NULL', '2  Steel B  deleted_at 2025-06-16', '3  Steel C  deleted_at NULL'], colors={1: 'amber'})
rows(d, 750, 270, 290, ['1  Steel A      ACTIVE', '2  Steel B      DEACTIVATE', '3  Steel C      ACTIVE'], colors={1: 'green'})
d.note(40, 368, 330, 100, ['orders.company_id → 2 is orphaned.', 'FK error, or cascade wipes business records.', 'No audit trail. Ruled out from commit one.'], color='red', size=12)
d.note(385, 368, 330, 100, ['Only two states. IS NULL on every query.', 'update_* audit columns already say', '"when and who". A state like "on hold"', 'would need yet another column.'], color='amber', size=12)
d.note(730, 368, 330, 100, ['Reversible (flip back to ACTIVE).', 'update_user_id / update_datetime', 'are updated along with it. The same column', 'can hold business states later.'], color='green', size=12)
d.box(40, 490, 1020, 70, color='muted')
d.text(550, 518, 'Every repository spells out where status = \'ACTIVE\' (10 implementations, 30 places): a visible condition, not a global guard', size=13, weight=600)
d.text(550, 542, 'No UNIQUE constraints · services deactivate children explicitly (no cascade) · not a single DELETE statement in the repo', size=12, weight=600, color=MUTED)
d.flow([{'path': [(205, 222), (205, 262)], 'color': 'red', 'dur': 0.6, 'hold': 0.4},
        {'path': [(550, 222), (550, 262)], 'color': 'amber', 'dur': 0.6, 'hold': 0.4},
        {'path': [(895, 222), (895, 262)], 'color': 'green', 'dur': 0.6, 'hold': 0.8}])
d.save(out('2025/06/16-1.svg'))

# =====================================================================
# 2025/06/16-2  soft delete: request → UPDATEs, no DELETE
# =====================================================================
d = Diagram(1100, 560, 'DELETE /company turns into three groups of UPDATEs. No DELETE statement is ever sent')
cl = d.box(40, 200, 150, 70, 'Client', ['DELETE /company', '{ companyId }'], color='blue')
ct = d.box(250, 200, 200, 70, 'CompanyController', ['deactivateCompany()', 'keeps @DeleteMapping'], color='gray')
sv = d.group(510, 96, 260, 290, 'CompanyService  @Transactional')
s1 = d.box(530, 126, 220, 60, 'companyEntity', ['.deactivate(updateUser)'], color='green')
s2 = d.box(530, 206, 220, 60, 'companyManagers', ['.forEach { deactivate() }'], color='green')
s3 = d.box(530, 286, 220, 60, 'shipmentReportApprovals', ['.forEach { deactivate() }'], color='green', label_size=14)
db = d.group(830, 96, 230, 290, 'DB (dirty checking on commit)')
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
d.text(800, 140, 'no save()', size=11, color=MUTED)
d.box(40, 420, 1020, 50, color='green'); d.text(550, 450, '200  COMPANY_DEACTIVATE  "Company deactivated."   (was: COMPANY_DELETE "Company deleted.")', size=13, weight=600)
d.note(40, 486, 1020, 56, ['The HTTP verb stays DELETE: it still says "take this off the list" best, and the frontend calls didn\'t have to change.', 'The mismatch between the name (deactivate) and the verb (DELETE) is deliberate. If clients need to set a status, move to PATCH /company/{id}/status.'], color='muted', size=12)
d.flow([{'path': [(190, 235), (250, 235)], 'color': 'blue', 'dur': 0.5},
        {'path': [(450, 235), (480, 235), (480, 156), (530, 156)], 'color': 'gray', 'dur': 0.6},
        {'path': [(750, 156), (850, 156)], 'color': 'green', 'dur': 0.4},
        {'path': [(750, 236), (850, 236)], 'color': 'green', 'dur': 0.4},
        {'path': [(750, 316), (850, 316)], 'color': 'green', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2025/06/16-2.svg'))

# =====================================================================
# 2025/12/05-1  PDFBox: page anatomy with coordinates
# The miniature page keeps the Korean form title and labels, since that is the real document;
# English glosses sit beside it.
# =====================================================================
d = Diagram(1100, 640, 'Coordinates on one A4 page: the origin is bottom-left, the cursor moves top to bottom')
PX, PY, PW, PH = 150, 96, 327, 463   # A4 595.28x841.89 * 0.55
d.box(PX, PY, PW, PH, color='gray')
d.text(PX + PW / 2, PY + 40, '거 래 명 세 서', size=15, weight=700)
d.text(PX + PW / 2, PY + 58, '(transaction statement) · 2025-12-05', size=9, color=MUTED)
# header grid 10 cols, 5 rows
hx, hy, hw, hh = PX + 16, PY + 74, PW - 32, 70
d.box(hx, hy, hw, hh, color='muted')
for i in range(1, 5): d.arrow([(hx, hy + i * 14), (hx + hw, hy + i * 14)], color='muted', head=False, width=1)
for fx in (0.044, 0.12, 0.27, 0.35, 0.5, 0.544, 0.62, 0.77, 0.85): d.arrow([(hx + hw * fx, hy), (hx + hw * fx, hy + hh)], color='muted', head=False, width=1)
d.lines(hx + hw * 0.022, hy + 22, ['S', 'E', 'L', 'L', 'E', 'R'], size=6, weight=700, gap=6)
d.lines(hx + hw * 0.522, hy + 16, ['B', 'U', 'Y', 'E', 'R'], size=6, weight=700, gap=7)
# stamp (265,690) 40x40 → scaled
sx, sy = PX + 265 * 0.55, PY + (841.89 - 690 - 40) * 0.55
d.box(sx, sy, 22, 22, color='red', dashed=True); d.text(sx + 11, sy + 15, '印', size=11, weight=700, color=G['red'])
# body grid
bx, by, bw, bh = hx, hy + hh + 10, hw, 230
d.box(bx, by, bw, 16, color='amber'); d.text(bx + bw / 2, by + 11, 'Item · Spec · Unit · Qty · Unit price · Amount · Notes', size=7, weight=700)
for i in range(1, 18): d.arrow([(bx, by + 16 + i * 12), (bx + bw, by + 16 + i * 12)], color='muted', head=False, width=1)
d.box(bx, by + 16, bw, 214, color='gray')
d.text(bx + bw / 2, by + 120, '18 rows (first page) / 25 rows (after)', size=9, color=MUTED)
# footer
fy = by + bh + 8
d.box(bx, fy, bw, 42, color='muted'); d.text(bx + bw / 2, fy + 25, 'Subtotal · VAT · Total  |  Delivery site · Contact · Phone', size=7.5, weight=600)
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
AX = 540
d.box(AX, 96, 520, 72, 'Starting cursor', ['currentY = page.mediaBox.height − 50  (= 791.89)', 'each text() subtracts fontSize × 1.5 on the way down'], color='purple', sub_size=12)
d.box(AX, 184, 520, 72, 'Centering', ['textWidth = font.getStringWidth(s) / 1000 × fontSize', 'x = (pageWidth − textWidth) / 2  (glyph widths are in 1/1000 em)'], color='blue', sub_size=12)
d.box(AX, 272, 520, 72, 'Tables', ['x = 30, width = pageWidth − 60. A cell matrix handles rowSpan/colSpan', 'rects and lines are anchored at the bottom-left too: addRect(x, y − h, w, h)'], color='gray', sub_size=12)
d.box(AX, 360, 520, 72, 'Stamp', ['imageFromUrl(url, 265, 690, 40, 40): first page, FOREGROUND', 'PDImageXObject.createFromByteArray keeps PNG alpha as an SMask'], color='red', sub_size=12)
d.box(AX, 448, 520, 72, 'Pagination', ['split up front with calculatePagination(items, 18, 25)', 'header on page 1, totals on the last page, blank rows on every page'], color='amber', sub_size=12)
d.box(AX, 536, 520, 56, 'Page numbers', ['after all pages exist, reopen each stream with AppendMode.APPEND: "n / total"'], color='muted', sub_size=12)
d.flow([{'path': [(PX - 60, PY + 50), (PX - 60, PY + PH - 20)], 'color': 'purple', 'dur': 2.5, 'hold': 0.8}])
d.save(out('2025/12/05-1.svg'))

# =====================================================================
# 2025/12/05-2  PDFBox: render pipeline
# =====================================================================
d = Diagram(1100, 560, 'Exporting a transaction statement: query, draw, upload to S3, return the URL')
a = d.box(40, 120, 150, 70, 'Controller', ['POST /sales/{id}', '/transaction/export'], color='blue')
b = d.box(240, 120, 170, 70, 'Service', ['fetch-join sales items', 'company, client region'], color='gray')
c = d.box(240, 230, 170, 60, 'account service', ['company (stamp URL), region', 'WebClient .block()'], color='muted', sub_size=11)
p = d.group(460, 96, 380, 250, 'TransactionStatementPdfUtils')
p1 = d.box(480, 126, 160, 50, 'calculatePagination', ['18 / 25 rows'], color='amber', label_size=14)
p2 = d.box(660, 126, 160, 50, 'Page loop', ['p.1: title, header, stamp'], color='gray')
p3 = d.box(480, 196, 160, 50, 'Body table', ['items + blank rows'], color='gray')
p4 = d.box(660, 196, 160, 50, 'Last page: totals', ['subtotal, VAT, total'], color='gray', label_size=14)
p5 = d.box(480, 266, 340, 50, 'addPageNumbers → PDDocument.save() → ByteArray', color='purple', label_size=13)
st = d.box(880, 120, 180, 70, 'GET stamp image', ['HttpClient, 10 s timeout', 'failure → 502'], color='red')
s3 = d.box(880, 266, 180, 70, 'Upload to S3', ['sales/{companyId}/거래명세서-…', 'application/pdf'], color='green')
d.arrow([(190, 155), (240, 155)], color='blue')
d.arrow([(325, 190), (325, 230)], color='muted', dashed=True)
d.arrow([(410, 155), (480, 155)], color='gray')
d.arrow([(640, 151), (660, 151)], color='gray')
d.arrow([(740, 176), (740, 196)], color='gray')
d.arrow([(640, 221), (660, 221)], color='gray', head=False)
d.arrow([(820, 140), (880, 140)], color='red', dashed=True)
d.text(846, 110, 'sync HTTP', size=10, weight=700, color=G['red'], anchor='start')
d.arrow([(820, 291), (880, 291)], color='green')
d.box(40, 380, 1020, 54, color='green'); d.text(550, 403, '201 TRANSACTION_STATEMENT_EXPORT   { data: "https://…/sales/7/거래명세서-7-202512051030-ab12cd34" }', size=13, weight=600, mono=True)
d.text(550, 423, 'Returns an S3 URL instead of streaming bytes, so "the exact file we sent" can be opened again', size=12, weight=600, color=MUTED)
d.note(40, 452, 1020, 80, ['Request params: priceVisibleYn (hiding prices blanks the cells, keeps the columns), header/body/footer font sizes (default 9/8/9pt)', 'Known debt: PDType0Font.load per cell, wrapText can\'t wrap Korean with no spaces, hard-coded stamp position, disabled service test'], color='muted', size=12)
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
d = Diagram(1100, 560, 'Last month stays open through the 10th and locks on the 11th: isPassedRequestDate(docDate, today)')
months = [('October', 100), ('November', 420), ('December', 740)]
for label, x in months:
    d.box(x, 96, 260, 60, label, color='gray', label_size=18)
d.arrow([(740 + 260 * 10.5 / 31, 96), (740 + 260 * 10.5 / 31, 156)], color='red', dashed=True, head=False, width=2)
d.text(740 + 260 * 10.5 / 31, 172, '10th | 11th boundary', size=11, weight=700, color=G['red'])
# today = 12/8
y1 = 200
d.text(30, y1 + 22, 'Today = Dec 8', size=14, weight=700, anchor='start'); d.text(30, y1 + 42, '(dayOfMonth ≤ 10)', size=11, color=MUTED, anchor='start')
d.box(100, y1 + 56, 260, 34, color='red'); d.text(230, y1 + 78, 'Locked (two or more months ago)', size=12, weight=700, color=G['red'])
d.box(420, y1 + 56, 260, 34, color='green'); d.text(550, y1 + 78, 'Open: last month, until the 10th', size=12, weight=700, color=G['green'])
d.box(740, y1 + 56, 260, 34, color='green'); d.text(870, y1 + 78, 'Open (this month)', size=12, weight=700, color=G['green'])
d.text(740 + 260 * 7.5 / 31, y1 + 50, '▼ today (8th)', size=11, weight=700, color=G['blue'])
# today = 12/12
y2 = 310
d.text(30, y2 + 22, 'Today = Dec 12', size=14, weight=700, anchor='start'); d.text(30, y2 + 42, '(dayOfMonth > 10)', size=11, color=MUTED, anchor='start')
d.box(100, y2 + 56, 260, 34, color='red'); d.text(230, y2 + 78, 'Locked', size=12, weight=700, color=G['red'])
d.box(420, y2 + 56, 260, 34, color='red'); d.text(550, y2 + 78, 'Locked: last month, from the 11th', size=12, weight=700, color=G['red'])
d.box(740, y2 + 56, 260, 34, color='green'); d.text(870, y2 + 78, 'Open (this month)', size=12, weight=700, color=G['green'])
d.text(740 + 260 * 11.5 / 31, y2 + 50, '▼ today (12th)', size=11, weight=700, color=G['blue'])
# decision table
ty = 430
d.box(100, ty, 900, 100, color='muted')
d.text(260, ty + 24, 'Target month', size=12, weight=700); d.text(560, ty + 24, 'Today ≤ 10th', size=12, weight=700); d.text(820, ty + 24, 'Today ≥ 11th', size=12, weight=700)
for i, (m, a, b) in enumerate([('Two or more months ago', 'Locked', 'Locked'), ('Last month', 'Open', 'Locked'), ('This month · future', 'Open', 'Open')]):
    yy = ty + 48 + i * 22
    d.text(260, yy, m, size=12, weight=600)
    d.text(560, yy, a, size=12, weight=700, color=G['green'] if a == 'Open' else G['red'])
    d.text(820, yy, b, size=12, weight=700, color=G['green'] if b == 'Open' else G['red'])
d.text(550, ty + 120, 'Judged by the YearMonth of the document\'s business date (order, sale, deposit or report date). Checked on create and update. Status 409.', size=12, weight=600, color=MUTED)
d.flow([{'path': [(740 + 260 * 1 / 31, 180), (740 + 260 * 10.5 / 31, 180)], 'color': 'green', 'dur': 1.2, 'hold': 0.4},
        {'path': [(740 + 260 * 10.5 / 31, 180), (740 + 260 * 30 / 31, 180)], 'color': 'red', 'dur': 1.2, 'hold': 0.8}])
d.text(740 + 260 * 5.5 / 31, 196, 'last month open', size=10, weight=700, color=G['green']); d.text(740 + 260 * 21 / 31, 196, 'last month locked', size=10, weight=700, color=G['red'])
d.save(out('2025/12/08-1.svg'))

# =====================================================================
# 2025/12/08-2  date lock: flag vs derived rule
# =====================================================================
d = Diagram(1100, 600, 'Stored state (a flag) vs a computed rule (dates): keep one fact in two places and they drift')
d.group(40, 86, 490, 480, 'Before: flag + date rule')
d.box(60, 116, 200, 60, 'LockEntity', ['lockedYn: Boolean = false'], color='red')
d.box(300, 116, 210, 60, 'lock()', ['0 callers in production code'], color='red', dashed=True)
d.arrow([(260, 146), (300, 146)], color='red', dashed=True)
for i, n in enumerate(['Order', 'Sales', 'Deposit', 'StockReport']):
    d.box(60 + i * 115, 206, 105, 40, n, color='gray', label_size=12)
    d.arrow([(112 + i * 115, 206), (112 + i * 115 - (i - 1.5) * 40, 176)], color='muted', head=False, width=1)
d.box(60, 276, 450, 44, 'Update request', ['PUT /order (with orderId)'], color='blue', label_size=13)
d.arrow([(285, 320), (285, 346)], color='gray')
d.box(60, 346, 210, 50, '① Date check', ['isPassedRequestDate', '→ 409 DATE_PASSED'], color='amber', label_size=12, sub_size=10)
d.box(300, 346, 210, 50, '② lockedYn check', ['always false → passes'], color='red', label_size=12, sub_size=11)
d.arrow([(270, 371), (300, 371)], color='gray')
d.box(60, 426, 450, 44, '8 response DTOs', ['lockedYn: false  (an always-false value shown to the UI)'], color='red', label_size=12, sub_size=11)
d.note(60, 486, 450, 66, ['No lock button or batch, so the flag was never true in 191 days.', '① was already doing the locking. Of the two sources', 'of truth, I deleted the one nobody wrote to.'], color='red', size=11)
d.group(570, 86, 490, 480, 'After: date rule only (2025-12-08)')
d.box(590, 116, 200, 60, 'BaseEntity', ['status, audit columns'], color='gray')
d.box(830, 116, 210, 60, 'Clock (now)', ['LocalDate.now() by default,', 'injected in tests'], color='blue', dashed=True, sub_size=11)
for i, n in enumerate(['Order', 'Sales', 'Deposit', 'StockReport']):
    d.box(590 + i * 115, 206, 105, 40, n, color='gray', label_size=12)
    d.arrow([(642 + i * 115, 206), (642 + i * 115 - (i - 1.5) * 40, 176)], color='muted', head=False, width=1)
d.box(590, 276, 450, 44, 'Create / update request', ['PUT /order, /sales, /deposit, /stock/report'], color='blue', label_size=13)
d.arrow([(815, 320), (815, 346)], color='gray')
d.box(590, 346, 450, 50, 'DateUtils.isPassedRequestDate(docDate, now)', ['pure function: no stored state, no backfill, no drift'], color='green', label_size=13, sub_size=11)
d.arrow([(935, 176), (935, 346)], color='blue', dashed=True)
d.box(590, 426, 215, 44, 'Pass → save', color='green', label_size=12)
d.box(825, 426, 215, 44, '409 *_DATE_PASSED', ['"From the 11th of each month…"'], color='amber', label_size=12, sub_size=10)
d.note(590, 486, 450, 66, ['Remaining debt: reopening · rechecking the stored date ·', 'hard-coded cutoff day · time zone. If companies need their', 'own closing, add a closing-period table on top of this rule.'], color='muted', size=11)
d.flow([{'path': [(285, 320), (285, 346)], 'color': 'blue', 'dur': 0.4},
        {'path': [(270, 371), (300, 371)], 'color': 'red', 'dur': 0.4, 'hold': 0.6},
        {'path': [(815, 320), (815, 346)], 'color': 'blue', 'dur': 0.4},
        {'path': [(935, 176), (935, 346)], 'color': 'blue', 'dur': 0.5, 'hold': 0.8}])
d.save(out('2025/12/08-2.svg'))

# =====================================================================
# 2025/12/08-3  modules: dependency graph before/after
# =====================================================================
d = Diagram(1100, 620, 'Module dependency graph: from entities inside the web app to api → domain → core')
d.group(40, 86, 460, 500, 'Before (2025-06-30 to 12-07): 4 modules')
d.box(60, 120, 230, 150, color='blue')
d.text(175, 136, 'erp-api', size=14, weight=700)
d.box(75, 150, 200, 108, color='amber', dashed=True)
d.lines(175, 170, ['21 entities · repos · Q-classes', 'service DTOs · controllers · security', 'Spring Batch job + scheduler', '(batch lives in the web app)'], size=11, weight=600, gap=18)
d.box(310, 120, 170, 70, 'account-api', ['9 entities + controllers'], color='blue', label_size=14)
d.box(310, 210, 170, 60, 'batch-api', ['empty shell'], color='muted', dashed=True, label_size=14)
d.box(60, 330, 420, 60, 'core', ['enums · BaseEntity · shared DTOs · config'], color='gray', label_size=14)
d.arrow([(175, 270), (175, 330)], color='gray'); d.arrow([(395, 190), (395, 210)], color='muted', head=False, dashed=True); d.arrow([(395, 270), (395, 330)], color='gray')
d.note(60, 410, 420, 150, ['• For batch-api to use the stock entities, it would', '  have to depend on erp-api (the web app)', '• account-api can\'t read ERP data via JPA, so it', '  detours through HTTP DTOs', '• EmployeeRepositoryImpl imports a controller request DTO,', '  and inside one module the compiler says nothing'], color='red', size=12)
d.group(540, 86, 520, 500, 'After (2025-12-08): 6 modules')
d.box(560, 120, 150, 60, 'erp-api', ['bootJar'], color='blue', label_size=14)
d.box(730, 120, 150, 60, 'account-api', ['bootJar'], color='blue', label_size=14)
d.box(900, 120, 140, 60, 'batch-api', ['bootJar'], color='blue', label_size=14)
d.box(560, 240, 220, 60, 'erp-domain', ['21 entities · repos · DTOs · jar'], color='green', label_size=14)
d.box(810, 240, 230, 60, 'account-domain', ['9 entities · repos · DTOs · jar'], color='green', label_size=14)
d.box(560, 360, 480, 60, 'core', ['enums · BaseEntity · shared DTOs · config (no project deps)'], color='gray', label_size=14)
d.arrow([(635, 180), (635, 240)], color='blue')
d.arrow([(805, 180), (860, 240)], color='blue')
d.arrow([(950, 180), (720, 240)], color='purple')
d.arrow([(990, 180), (960, 240)], color='purple')
d.arrow([(670, 300), (670, 360)], color='gray'); d.arrow([(925, 300), (925, 360)], color='gray')
d.arrow([(570, 180), (550, 200), (550, 340), (570, 360)], color='muted', dashed=True); d.arrow([(1030, 180), (1050, 200), (1050, 340), (1030, 360)], color='muted', dashed=True)
d.note(560, 440, 480, 120, ['• api → domain → core. A repo importing a controller', '  now breaks the build', '• implementation only: api modules declare core', '  themselves (dashed) · batch-api uses both domains', '• domain packages added to scanBasePackages,', '  no @EntityScan needed'], color='green', size=12)
d.flow([{'path': [(950, 180), (720, 240)], 'color': 'purple', 'dur': 0.6},
        {'path': [(670, 300), (670, 360)], 'color': 'gray', 'dur': 0.4, 'hold': 0.3},
        {'path': [(990, 180), (960, 240)], 'color': 'purple', 'dur': 0.5},
        {'path': [(925, 300), (925, 360)], 'color': 'gray', 'dur': 0.4, 'hold': 0.8}])
d.save(out('2025/12/08-3.svg'))

# =====================================================================
# 2025/12/08-4  modules: what moved where
# =====================================================================
d = Diagram(1100, 560, 'What moved where: 313 files, 223 renamed · 27 added · 5 deleted · 58 modified')
d.box(40, 110, 220, 150, 'erp-api', ['142 files moved out'], color='blue', label_size=15)
d.box(40, 300, 220, 110, 'account-api', ['66 files moved out'], color='blue', label_size=15)
d.box(840, 96, 220, 160, 'erp-domain', ['domain 82 · DTOs 41', 'TestUtils · schema.sql', 'tests 30'], color='green', label_size=15)
d.box(840, 286, 220, 110, 'account-domain', ['domain 33 · DTOs 16', 'TestUtils · 2 SQL · 14 tests'], color='green', label_size=15)
d.box(840, 426, 220, 60, 'batch-api', ['StockBatchConfig · Scheduler'], color='purple', label_size=15)
bands = [([(260, 150), (840, 140)], 'blue', '21 entities · repos + impls · 41 service DTOs', (550, 135)),
         ([(260, 200), (840, 200)], 'blue', '30 repository/entity tests (moved as is)', (550, 190)),
         ([(260, 245), (700, 245), (700, 456), (840, 456)], 'purple', '2 batch job/scheduler files (88% / 92% similar)', (480, 235)),
         ([(260, 330), (840, 320)], 'green', '9 entities · repos · 16 DTOs · 14 tests', (470, 316)),
         ([(260, 380), (840, 370)], 'green', 'EmployeeQueryRequest: controller/request → domain/dto', (470, 366))]
for pts, c, lab, (lx, ly) in bands:
    d.arrow(pts, color=c, width=3)
    d.text(lx, ly, lab, size=11, weight=700, color=G[c])
d.note(40, 440, 640, 90, ['Left in api: controllers · services · security/JWT · Swagger · Excel/PDF export', 'scanBasePackages: ["…erpapi", "…core"] → ["…erpapi", "…erpdomain", "…core"]', 'kapt runs per module, so Q-classes land next to the entities (erp-domain/build/generated)'], color='muted', size=12)
d.flow([{'path': [(260, 150), (840, 140)], 'color': 'blue', 'dur': 1.0},
        {'path': [(260, 200), (840, 200)], 'color': 'blue', 'dur': 0.8},
        {'path': [(260, 245), (700, 245), (700, 456), (840, 456)], 'color': 'purple', 'dur': 1.2},
        {'path': [(260, 330), (840, 320)], 'color': 'green', 'dur': 0.8},
        {'path': [(260, 380), (840, 370)], 'color': 'green', 'dur': 0.8, 'hold': 0.8}])
d.save(out('2025/12/08-4.svg'))
