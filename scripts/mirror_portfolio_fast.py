"""Fast incremental mirror of elemenfolio portfolio pages (concurrent asset fetch)."""
from __future__ import annotations

import csv
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin

# reuse helpers
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mirror_site import (  # noqa: E402
    EXTRA_CSV,
    LIVE,
    SITE,
    SESSION,
    collect_asset_urls,
    copy_or_download,
    is_our_host,
    local_path_for_url,
    rewrite_html,
    ensure_parent,
)
from bs4 import BeautifulSoup
from urllib.parse import urlparse

WORKERS = 12


def routes_pending() -> list[str]:
    routes = []
    for r in csv.DictReader(EXTRA_CSV.open(encoding="utf-8")):
        u = (r.get("url") or "").strip()
        if u.startswith("/") and u not in routes:
            routes.append(u)
    pending = []
    for route in routes:
        dest = local_path_for_url(urljoin(LIVE, route))
        if dest and dest.exists() and dest.stat().st_size > 1000:
            continue
        pending.append(route)
    return pending


def fetch_one(route: str) -> tuple[str, bool, int]:
    page_url = urljoin(LIVE, route)
    try:
        r = SESSION.get(page_url, timeout=90)
    except Exception as e:
        print("!", route, e)
        return route, False, 0
    if r.status_code != 200:
        print("!", route, r.status_code)
        return route, False, 0
    soup = BeautifulSoup(r.text, "lxml")
    assets = collect_asset_urls(soup, page_url)
    todo = []
    for asset in assets:
        host = urlparse(asset).netloc.lower()
        if any(
            x in host
            for x in (
                "google-analytics",
                "googletagmanager",
                "facebook.net",
                "hotjar",
                "doubleclick",
            )
        ):
            continue
        dest = local_path_for_url(asset)
        if dest is None:
            continue
        if not is_our_host(asset):
            if not any(
                asset.lower().endswith(ext)
                for ext in (".css", ".js", ".woff2", ".woff", ".ttf", ".eot")
            ):
                continue
        if dest.exists() and dest.stat().st_size > 0:
            continue
        todo.append((asset, dest))

    ok_assets = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = [pool.submit(copy_or_download, a, d) for a, d in todo]
        for fut in as_completed(futs):
            if fut.result():
                ok_assets += 1

    dest = local_path_for_url(page_url)
    assert dest is not None
    ensure_parent(dest)
    dest.write_text(rewrite_html(r.text, page_url), encoding="utf-8")
    # strip portfolio caret
    html = dest.read_text(encoding="utf-8", errors="replace")
    html = html.replace(
        'href="/web-diformainstore/portfolio/">Portfolio'
        '<i aria-hidden="true" class="icon icon-down-arrow1 elementskit-submenu-indicator"></i>',
        'href="/web-diformainstore/portfolio/">Portfolio',
    )
    dest.write_text(html, encoding="utf-8")
    print(f"OK {route} (+{ok_assets} assets)")
    return route, True, ok_assets


def main() -> None:
    pending = routes_pending()
    print(f"Pending portfolio pages: {len(pending)}")
    ok = 0
    # page-level concurrency moderate to avoid hammering host
    with ThreadPoolExecutor(max_workers=4) as pool:
        futs = [pool.submit(fetch_one, route) for route in pending]
        for fut in as_completed(futs):
            _, success, _ = fut.result()
            if success:
                ok += 1
    print(f"Done {ok}/{len(pending)}")
    files = [p for p in SITE.rglob("*") if p.is_file()]
    print(f"site files={len(files)} size={sum(p.stat().st_size for p in files)/1e6:.1f}MB")


if __name__ == "__main__":
    main()
