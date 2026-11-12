# English edition guide

The blog is bilingual. Korean is the default language and lives at the site root.
English lives under `/en/`. [jekyll-polyglot](https://polyglot.untra.io) builds each
language separately and pairs an original with its translation **by permalink**,
so the English post must keep the same `slug` as the Korean one.

## Where files go

| What | Korean (original) | English |
| --- | --- | --- |
| Post | `_posts/<cat>/YYYY-MM-DD-<korean-title>.md` | `_posts/en/<cat>/YYYY-MM-DD-<slug>.md` |
| Diagram (SVG) | `assets/img/YYYY/MM/DD-N.svg` | `assets/img/en/YYYY/MM/DD-N.svg` |
| Diagram source | `tools/diagrams/make_diagrams*.py` | `tools/diagrams/en/<group>.py` |
| Thumbnail | `assets/img/thumbnail/<slug>.jpg` | `assets/img/thumbnail/en/<slug>.jpg` |
| Screenshots / photos | `assets/img/YYYY/MM/DD-N.webp` | reuse the Korean file (see below) |
| UI strings | `_data/ko-KR/ui.yml` | `_data/en/ui.yml` |
| Site tagline / description | `_config.yml` | `_config.yml` → `i18n.en` |

`<cat>` is the same folder the Korean post uses (`backend`, `frontend`, `devops`, `ai`, `data`, `sql`, `etc`).

## Front matter

Copy the Korean front matter, then:

- add `lang: en`
- keep `slug`, `date`, `categories`, `tags`, `pin`, `math`, `mermaid` and similar flags **identical**
- translate `title`, `description`, `image.alt`
- set `image.path` to `/assets/img/thumbnail/en/<slug>.jpg`
- **drop** `redirect_from` (those are old Korean URLs that only the Korean post needs)
- translate `series` using the table below (every post in a series must use the same name)

| Korean series | English series |
| --- | --- |
| AI 네이티브 개발 | AI-Native Development |
| JPA N+1 문제 해결 | Fixing JPA N+1 Queries |
| JWT 세션 설계 | JWT Session Design |
| 온프레미스 무중단 배포 | Zero-Downtime Deploys on a Single Server |
| Kong API Gateway | Kong API Gateway |

## Body

- **Write it the way a native English engineering blog would.** Don't translate sentence by sentence.
  Restructure paragraphs, use idiomatic phrasing, and cut filler. Keep the first-person voice
  ("I", "we" for the team) and the author's matter-of-fact tone. Contractions are fine.
  Headings use sentence case ("Why the lock wasn't released", not "Why The Lock Wasn't Released").
- **Facts stay exactly the same.** Numbers, versions, dates, measurements, config, commands, code
  and the order of the argument don't change. Don't add claims that aren't in the original.
- **Korea-specific context.** If a reader outside Korea wouldn't know something (Naver, KakaoTalk,
  a Korean conference, the KST business day, Korean tax invoices, etc.), add a few words of context
  the first time it comes up. Drop puns or wordplay that only work in Korean.
- **Code blocks.** Keep code as is. Translate Korean comments. Translate Korean string literals
  only when they're illustrative (log lines, sample messages); if a literal is the real Korean text
  the product shows users, keep it and explain it in prose if needed.
- **Internal links** like `/posts/<slug>/` stay as they are. Replace `{% post_url <path> %}` with the
  plain `/posts/<slug>/` of the target post. The English build rewrites them to
  `/en/posts/<slug>/` automatically.
- **Links to Korean-only external pages** stay, optionally marked "(in Korean)".
- Prompts, Chirpy callouts (`{: .prompt-tip }` etc.), footnotes, tables and image attributes
  (`{: width=... }`) keep their markup.

## Images

- **Diagrams (SVG):** every diagram has Korean text, so each one gets an English copy under
  `assets/img/en/`. Generated diagrams are rebuilt from an English copy of their Python source in
  `tools/diagrams/en/` (it imports `tools/diagrams/diag.py`). Hand-made SVGs are copied and edited.
  English is wider than Korean, so widen boxes, shorten labels or wrap lines as needed, then run
  `python3 tools/diagrams/check_text_fit.py assets/img/en/...svg` and look at the rendered result.
- **Screenshots and photos** are reused from the Korean path. If one shows Korean text that matters
  to the point being made, say what it shows in the English alt text or the sentence around it.
  Don't edit raster images.
- **Thumbnails** are generated: `python3 tools/diagrams/make_thumbs_v2.py <slug>` (Pillow needed).

## Check

```bash
python3 tools/i18n/check_translations.py   # missing English editions (warning), broken image paths (error)
bundle exec jekyll b && bundle exec htmlproofer _site --disable-external
```

CI runs the same translation check before html-proofer.

Then open `/en/posts/<slug>/` and use the EN/KO button in the sidebar to compare it with the original.
