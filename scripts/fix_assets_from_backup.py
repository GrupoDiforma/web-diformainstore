"""Copy missing icon fonts / plugin assets from JetBackup into site/."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BACKUP = Path(
    r"C:\Users\Edwin_Laverde\Downloads\download_diformainstore"
    r"\backup\homedir\public_html"
)

# Critical packs that use icon fonts (broken □ in menus)
MUST_COPY = [
    "wp-content/plugins/elementskit-lite/modules/elementskit-icon-pack/assets/fonts",
    "wp-content/plugins/elementskit-lite/modules/elementskit-icon-pack/assets/css",
    "wp-content/plugins/elementor/assets/lib/eicons/fonts",
    "wp-content/plugins/elementor/assets/lib/font-awesome/webfonts",
    "wp-content/plugins/elementor/assets/lib/font-awesome/css",
    "wp-content/themes/storefront/assets/fonts",
]


def copy_tree(rel: str) -> int:
    src = BACKUP / rel
    dst = SITE / rel
    if not src.exists():
        print("missing in backup:", rel)
        return 0
    count = 0
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return 1
    for f in src.rglob("*"):
        if not f.is_file():
            continue
        target = dst / f.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.stat().st_size != f.stat().st_size:
            shutil.copy2(f, target)
            count += 1
    print(f"copied/updated {count} from {rel}")
    return count


def scrape_font_urls_from_css() -> int:
    """Follow url(...) in local CSS under plugins/themes and ensure files exist."""
    n = 0
    for css in SITE.rglob("*.css"):
        try:
            text = css.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for raw in re.findall(r"url\(([^)]+)\)", text):
            u = raw.strip(" \t'\"")
            if not u or u.startswith(("data:", "http://", "https://", "//")):
                continue
            # strip query/hash
            u = u.split("?")[0].split("#")[0]
            dest = (css.parent / u).resolve()
            try:
                dest.relative_to(SITE.resolve())
            except ValueError:
                continue
            if dest.exists():
                continue
            # map back to backup via site-relative path
            rel = dest.relative_to(SITE.resolve())
            src = BACKUP / rel
            if src.is_file():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                n += 1
                print("font/asset", rel)
    return n


def hide_bogus_portfolio_indicator() -> None:
    """Portfolio is not a dropdown; hide broken/extra caret if font still fails."""
    # Prefer fixing fonts; also remove indicator class on Portfolio-only links.
    for html in SITE.rglob("*.html"):
        t = html.read_text(encoding="utf-8", errors="replace")
        o = t
        # Remove submenu indicator icon that sits inside Portfolio link (not a dropdown)
        t = re.sub(
            r'(href="/web-diformainstore/portfolio/"[^>]*>Portfolio)'
            r'<i[^>]*elementskit-submenu-indicator[^>]*></i>',
            r"\1",
            t,
            flags=re.I,
        )
        if t != o:
            html.write_text(t, encoding="utf-8")


def main() -> None:
    total = 0
    for rel in MUST_COPY:
        total += copy_tree(rel)
    total += scrape_font_urls_from_css()
    hide_bogus_portfolio_indicator()
    print("done, files touched:", total)


if __name__ == "__main__":
    main()
