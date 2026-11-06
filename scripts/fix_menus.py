"""Fix broken menu anchors in already-mirrored HTML (hash loss + Portfolio #)."""
from __future__ import annotations

import re
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"
BASE = "/web-diformainstore"

REPLACEMENTS = [
    # Portfolio top-level was href="#" on live too; point to portfolio page
    (
        re.compile(
            r'(<a[^>]*class="[^"]*ekit-menu-nav-link[^"]*"[^>]*href=")#"([^>]*>\s*Portfolio\s*</a>)',
            re.I,
        ),
        rf'\1{BASE}/portfolio/\2',
    ),
    (
        re.compile(
            r'(<a[^>]*href=")#"([^>]*class="[^"]*ekit-menu-nav-link[^"]*"[^>]*>\s*Portfolio\s*</a>)',
            re.I,
        ),
        rf'\1{BASE}/portfolio/\2',
    ),
    # Restore section anchors that rewrite dropped
    (re.compile(rf'href="{re.escape(BASE)}/"([^>]*?>\s*About Us\s*<)'), rf'href="{BASE}/#about-us"\1'),
    (re.compile(rf'href="{re.escape(BASE)}/"([^>]*?>\s*Our Clients\s*<)'), rf'href="{BASE}/#our-clients"\1'),
    # Also plain dropdown-item without relying on text order in attributes
]


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    original = text
    for pat, repl in REPLACEMENTS:
        text = pat.sub(repl, text)

    # Broader: any About Us / Our Clients links that point only to base home
    text = re.sub(
        rf'(<a([^>]*class="[^"]*dropdown-item[^"]*"[^>]*)href="{re.escape(BASE)}/"([^>]*)>)(\s*About Us\s*)(</a>)',
        rf'<a\2href="{BASE}/#about-us"\3>\4\5',
        text,
        flags=re.I,
    )
    text = re.sub(
        rf'(<a([^>]*class="[^"]*dropdown-item[^"]*"[^>]*)href="{re.escape(BASE)}/"([^>]*)>)(\s*Our Clients\s*)(</a>)',
        rf'<a\2href="{BASE}/#our-clients"\3>\4\5',
        text,
        flags=re.I,
    )
    # Portfolio may include an <i> icon before </a>
    text = text.replace('href="#">Portfolio', f'href="{BASE}/portfolio/">Portfolio')
    text = text.replace("href='#'>Portfolio", f"href='{BASE}/portfolio/'>Portfolio")

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    files = list(SITE.rglob("*.html"))
    for p in files:
        if fix_file(p):
            changed += 1
    print(f"Fixed menus in {changed}/{len(files)} HTML files")


if __name__ == "__main__":
    main()
