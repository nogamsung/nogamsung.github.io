# 글 다이어그램·썸네일 생성기

- `diag.py` — 블로그 스타일(흰 배경, 둥근 상자, SMIL 패킷 애니메이션, `prefers-reduced-motion` 시 정지)의 작은 SVG 헬퍼
- `make_diagrams.py` — 각 글의 다이어그램 정의. 실행: `python3 tools/diagrams/make_diagrams.py "$PWD"` → `assets/img/YYYY/MM/DD-N.svg`
- `make_thumbs_v2.py` — `_posts/**/*.md` front matter(title·slug·categories)로 1200x630 JPEG 썸네일 생성 (가운데 70% 안전 영역). 실행: `python3 tools/diagrams/make_thumbs_v2.py` (저장소 루트에서, Pillow 필요)

`tools/` 는 `_config.yml` 의 `exclude` 라 사이트 빌드에 포함되지 않는다.
