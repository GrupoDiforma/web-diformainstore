"""
Build a static mirror of diformainstore.com for GitHub Pages.

- HTML: fetched from the live site (Elementor already rendered)
- /wp-content/* files: prefer local JetBackup copy when present
- Remaining CSS/JS/font/img: downloaded from live
- Links rewritten for project Pages base /web-diformainstore/
"""
from __future__ import annotations

import csv
import hashlib
import re
import shutil
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "docs" / "mapa-urls.csv"
SITE = ROOT / "site"
BACKUP_WEB = Path(
    r"C:\Users\Edwin_Laverde\Downloads\download_diformainstore"
    r"\backup\homedir\public_html"
)
LIVE = "https://www.diformainstore.com"
BASE_PATH = "/web-diformainstore"
SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (compatible; DiformaMirror/1.0; +local)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
)

ASSET_ATTRS = [
    ("img", "src"),
    ("img", "data-src"),
    ("img", "data-lazy-src"),
    ("source", "src"),
    ("source", "srcset"),
    ("img", "srcset"),
    ("script", "src"),
    ("link", "href"),
    ("video", "poster"),
    ("video", "src"),
    ("audio", "src"),
    ("use", "href"),
    ("image", "href"),
]


def load_routes() -> list[str]:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    routes = ["/"]
    for r in rows:
        if r["status"] != "publish" or r["type"] not in {"page", "post"}:
            continue
        u = (r["url"] or "").strip()
        if u.startswith("/") and u not in routes:
            routes.append(u)
    return routes


def is_our_host(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return host in ("", "www.diformainstore.com", "diformainstore.com")


def local_path_for_url(url: str) -> Path | None:
    """Map a site URL to a path under SITE/."""
    p = urlparse(url)
    if not is_our_host(url) and p.netloc:
        # Off-site: keep under site/_ext/<host>/...
        rel = Path("_ext") / p.netloc / unquote(p.path.lstrip("/"))
    else:
        rel = Path(unquote(p.path.lstrip("/")))
    if not rel.parts or str(rel).endswith("/"):
        rel = rel / "index.html"
    elif rel.suffix == "":
        # pretty permalink → folder/index.html
        rel = rel / "index.html"
    return SITE / rel


def backup_file_for_url(url: str) -> Path | None:
    p = urlparse(url)
    if not is_our_host(url):
        return None
    path = unquote(p.path.lstrip("/"))
    if not path:
        return None
    candidate = BACKUP_WEB / path
    if candidate.is_file():
        return candidate
    return None


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def copy_or_download(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    ensure_parent(dest)
    local = backup_file_for_url(url)
    if local:
        shutil.copy2(local, dest)
        return True
    try:
        r = SESSION.get(url, timeout=60, stream=True)
        if r.status_code != 200:
            print(f"  ! {r.status_code} {url}")
            return False
        with dest.open("wb") as f:
            for chunk in r.iter_content(65536):
                if chunk:
                    f.write(chunk)
        return True
    except requests.RequestException as e:
        print(f"  ! fail {url}: {e}")
        return False


def parse_srcset(value: str) -> list[str]:
    out = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        out.append(part.split()[0])
    return out


def collect_asset_urls(soup: BeautifulSoup, page_url: str) -> set[str]:
    urls: set[str] = set()
    for tag, attr in ASSET_ATTRS:
        for el in soup.find_all(tag):
            val = el.get(attr)
            if not val:
                continue
            if attr == "srcset":
                for u in parse_srcset(val):
                    urls.add(urljoin(page_url, u))
            else:
                urls.add(urljoin(page_url, val))
    # CSS url(...) inside style tags and inline styles (light pass)
    for style in soup.find_all("style"):
        if style.string:
            for m in re.finditer(r"url\((['\"]?)([^)'\"]+)\1\)", style.string):
                urls.add(urljoin(page_url, m.group(2)))
    for el in soup.find_all(style=True):
        for m in re.finditer(r"url\((['\"]?)([^)'\"]+)\1\)", el.get("style", "")):
            urls.add(urljoin(page_url, m.group(2)))
    # Elementor / WP often puts background in data-settings JSON — skip for v1
    skip_bits = (
        "/wp-json",
        "/feed",
        "xmlrpc.php",
        "wp-login.php",
        "wp-admin",
    )
    cleaned = set()
    for u in urls:
        if not u.startswith("http") or u.startswith("data:"):
            continue
        path = urlparse(u).path.lower()
        if any(b in path for b in skip_bits):
            continue
        cleaned.add(u)
    return cleaned


def rewrite_html(html: str, page_url: str) -> str:
    """Point same-origin absolute URLs to the Pages base path."""
    soup = BeautifulSoup(html, "lxml")
    if soup.head and not soup.head.find("base"):
        base = soup.new_tag("base", href=f"{BASE_PATH}/")
        # Prefer first child
        if soup.head.contents:
            soup.head.insert(0, base)
        else:
            soup.head.append(base)

    def rewrite_one(u: str) -> str:
        if not u or u.startswith(("data:", "mailto:", "tel:", "#", "javascript:")):
            return u
        abs_u = urljoin(page_url, u)
        p = urlparse(abs_u)
        if is_our_host(abs_u):
            path = p.path or "/"
            # Keep pretty paths; assets keep file path
            return f"{BASE_PATH}{path}" + (f"?{p.query}" if p.query else "")
        return abs_u

    for tag, attr in ASSET_ATTRS:
        for el in soup.find_all(tag):
            val = el.get(attr)
            if not val:
                continue
            if attr == "srcset":
                parts = []
                for piece in val.split(","):
                    piece = piece.strip()
                    if not piece:
                        continue
                    bits = piece.split()
                    bits[0] = rewrite_one(bits[0])
                    parts.append(" ".join(bits))
                el[attr] = ", ".join(parts)
            else:
                el[attr] = rewrite_one(val)

    for a in soup.find_all("a", href=True):
        a["href"] = rewrite_one(a["href"])

    # Replace leftover absolute origins in raw text (JSON-LD, etc.)
    out = str(soup)
    for origin in (
        "https://www.diformainstore.com",
        "http://www.diformainstore.com",
        "https://diformainstore.com",
        "http://diformainstore.com",
    ):
        out = out.replace(origin, f"https://grupodiforma.github.io{BASE_PATH}")
    return out


def fetch_page(route: str) -> Path | None:
    page_url = urljoin(LIVE, route)
    print(f"PAGE {page_url}")
    try:
        r = SESSION.get(page_url, timeout=90)
    except requests.RequestException as e:
        print(f"  ! {e}")
        return None
    if r.status_code != 200:
        print(f"  ! HTTP {r.status_code}")
        return None
    dest = local_path_for_url(page_url)
    assert dest is not None
    ensure_parent(dest)
    html = r.text
    soup = BeautifulSoup(html, "lxml")
    assets = collect_asset_urls(soup, page_url)
    print(f"  assets: {len(assets)}")
    for asset in sorted(assets):
        # Skip huge offsite trackers
        host = urlparse(asset).netloc.lower()
        if any(x in host for x in ("google-analytics", "googletagmanager", "facebook.net", "hotjar", "doubleclick")):
            continue
        dest_asset = local_path_for_url(asset)
        if dest_asset is None:
            continue
        # Only store same-origin + wp-content-ish under site; skip random CDNs for size in v1 unless CSS/JS
        if not is_our_host(asset):
            if not any(asset.lower().endswith(ext) for ext in (".css", ".js", ".woff2", ".woff", ".ttf")):
                continue
        copy_or_download(asset, dest_asset)
        time.sleep(0.05)

    dest.write_text(rewrite_html(html, page_url), encoding="utf-8")
    return dest


def copy_core_static_from_backup() -> None:
    """Copy WP theme/plugin static that pages commonly need if missing."""
    if not BACKUP_WEB.exists():
        print("Backup public_html not found; live-only assets.")
        return
    # Minimal: ensure wp-includes and active theme assets available on demand via copy_or_download
    print(f"Backup web root: {BACKUP_WEB}")


def main() -> None:
    if not CSV_PATH.exists():
        print("Missing mapa-urls.csv", file=sys.stderr)
        sys.exit(1)
    if SITE.exists():
        print("Removing previous site/ …")
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    copy_core_static_from_backup()
    routes = load_routes()
    print(f"Routes to mirror: {len(routes)}")
    ok = 0
    for route in routes:
        if fetch_page(route):
            ok += 1
        time.sleep(0.25)
    files = [p for p in SITE.rglob("*") if p.is_file()]
    size = sum(p.stat().st_size for p in files)
    print(f"Mirrored {ok}/{len(routes)} pages · {len(files)} files · {size/1e6:.1f} MB")
    print(f"Output: {SITE}")


if __name__ == "__main__":
    main()
