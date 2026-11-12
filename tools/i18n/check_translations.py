"""한국어 글마다 같은 slug 의 영어판(_posts/en/**)이 있는지, 영어판이 가리키는 이미지가 실제로 있는지 확인한다.

- 영어판이 없는 글: 경고만 낸다 (영어 빌드에서는 한국어 원문이 대신 보이므로 배포는 막지 않는다)
- 영어판의 이미지 경로가 없는 파일을 가리킴: 실패 (종료 코드 1)
GitHub Actions 에서는 ::warning:: / ::error:: 주석으로 PR 화면에 표시된다.

사용: python3 tools/i18n/check_translations.py   (저장소 루트에서)
"""
import glob, os, re, sys

GHA = bool(os.environ.get('GITHUB_ACTIONS'))


def note(level, path, msg):
    print(f'::{level} file={path}::{msg}' if GHA else f'{level}: {path}: {msg}')


def front(path):
    text = open(path, encoding='utf-8').read()
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    return (m.group(1) if m else ''), text


def slug(fm):
    m = re.search(r'^slug:\s*(\S+)', fm, re.M)
    return m.group(1) if m else None


en = {}
for f in glob.glob('_posts/en/**/*.md', recursive=True):
    fm, text = front(f)
    if not re.search(r'^lang:\s*en\s*$', fm, re.M):
        note('error', f, 'English post is missing `lang: en` in front matter')
    en[slug(fm)] = (f, text)

missing = broken = 0
for f in sorted(glob.glob('_posts/**/*.md', recursive=True)):
    if f.startswith('_posts/en/') or f.endswith('2023-01-01-title.md'):
        continue
    s = slug(front(f)[0])
    if s and s not in en:
        note('warning', f, f'English edition missing (expected _posts/en/**/*-{s}.md with slug: {s})')
        missing += 1

for s, (f, text) in sorted(en.items()):
    for img in sorted(set(re.findall(r'/assets/img/[^\s)"\']+\.(?:svg|webp|png|jpe?g|gif)', text))):
        if not os.path.isfile('.' + img):
            note('error', f, f'image not found: {img}')
            broken += 1

print(f'English editions: {len(en)}, missing: {missing}, broken image links: {broken}')
sys.exit(1 if broken else 0)
