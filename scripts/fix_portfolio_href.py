from pathlib import Path
import re
from bs4 import BeautifulSoup

SITE = Path(__file__).resolve().parents[1] / "site"
BASE = "/web-diformainstore"

changed = 0
for p in SITE.rglob("*.html"):
    t = p.read_text(encoding="utf-8", errors="replace")
    o = t
    t = t.replace('href="#">Portfolio', f'href="{BASE}/portfolio/">Portfolio')
    t = t.replace("href='#'>Portfolio", f"href='{BASE}/portfolio/'>Portfolio")
    if t != o:
        p.write_text(t, encoding="utf-8")
        changed += 1
print("changed", changed)

soup = BeautifulSoup((SITE / "index.html").read_text(encoding="utf-8"), "lxml")
for a in soup.select(".ekit-menu-nav-link"):
    print(a.get("href"), "|", a.get_text(" ", strip=True)[:40])
