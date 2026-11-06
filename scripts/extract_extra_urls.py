"""Extract portfolio CPT + nav menu URLs from WP SQL dump."""
from __future__ import annotations

import csv
import gzip
import re
from pathlib import Path

GZ = Path(
    r"C:\Users\Edwin_Laverde\Downloads\download_diformainstore"
    r"\backup\database\diformainstore_wp61.sql.gz"
)
OUT = Path(__file__).resolve().parents[1] / "docs"
PLUGIN = Path(
    r"C:\Users\Edwin_Laverde\Downloads\download_diformainstore"
    r"\backup\homedir\public_html\wp-content\plugins\portfolio-elementor"
)


def split_values(s: str) -> list[list]:
    items: list[list] = []
    i = 0
    n = len(s)
    while i < n:
        while i < n and s[i] in " \t\r\n,":
            i += 1
        if i >= n or s[i] != "(":
            break
        i += 1
        fields = []
        while i < n:
            while i < n and s[i] in " \t\r\n":
                i += 1
            if i >= n:
                break
            if s[i] == ")":
                i += 1
                break
            if s[i] == ",":
                i += 1
                continue
            if s.startswith("NULL", i) and (i + 4 >= n or s[i + 4] in ",)"):
                fields.append(None)
                i += 4
                continue
            if s[i] == "'":
                i += 1
                buf: list[str] = []
                while i < n:
                    c = s[i]
                    if c == "\\" and i + 1 < n:
                        buf.append(s[i + 1])
                        i += 2
                        continue
                    if c == "'":
                        if i + 1 < n and s[i + 1] == "'":
                            buf.append("'")
                            i += 2
                            continue
                        i += 1
                        break
                    buf.append(c)
                    i += 1
                fields.append("".join(buf))
                continue
            j = i
            while j < n and s[j] not in ",)":
                j += 1
            fields.append(s[i:j].strip())
            i = j
        items.append(fields)
    return items


def find_cpt() -> list[str]:
    found = []
    if PLUGIN.exists():
        for p in PLUGIN.rglob("*.php"):
            txt = p.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"register_post_type\(\s*'([^']+)'", txt):
                found.append(m.group(1))
    return sorted(set(found))


def parse_posts(data: str, col_names: list[str]) -> list[dict]:
    rows = []
    for m in re.finditer(r"INSERT INTO `wp0y_posts` VALUES\s*", data, re.I):
        start = m.end()
        end = data.find(";\n", start)
        if end < 0:
            end = data.find(";", start)
        for fields in split_values(data[start:end]):
            if len(fields) != len(col_names):
                continue
            rows.append(dict(zip(col_names, fields)))
    return rows


def main() -> None:
    cpts = find_cpt()
    print("CPT from plugin:", cpts)

    print("Reading SQL…")
    data = gzip.open(GZ, "rt", encoding="utf-8", errors="replace").read()
    mcreate = re.search(
        r"CREATE TABLE `wp0y_posts` \((.*?)\) ENGINE", data, re.S | re.I
    )
    col_names = []
    if mcreate:
        for line in mcreate.group(1).split("\n"):
            mm = re.match(r"\s*`([^`]+)`", line)
            if mm:
                col_names.append(mm.group(1))

    rows = parse_posts(data, col_names)
    type_counts: dict[str, int] = {}
    for r in rows:
        pt = (r.get("post_type") or "").strip()
        st = (r.get("post_status") or "").strip()
        if st == "publish":
            type_counts[pt] = type_counts.get(pt, 0) + 1
    print("Published post_type counts:")
    for k, v in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")

    # Likely portfolio types
    candidates = set(cpts) | {
        "portfolio",
        "elemenfolio",
        "pwrgrids_portfolio",
        "powerfolio",
        "jet-portfolio",
        "project",
    }
    # Also anything with portfolio in name
    for t in type_counts:
        if "port" in t or "folio" in t or "project" in t:
            candidates.add(t)

    extra = []
    for r in rows:
        pt = (r.get("post_type") or "").strip()
        st = (r.get("post_status") or "").strip()
        if st != "publish":
            continue
        if pt in candidates and pt not in {"page", "post", "attachment"}:
            slug = (r.get("post_name") or "").strip()
            if not slug:
                continue
            # PowerFolio often uses /portfolio/slug/
            url = f"/portfolio/{slug}/"
            extra.append(
                {
                    "ID": r.get("ID"),
                    "type": pt,
                    "status": st,
                    "title": (r.get("post_title") or "").replace("\n", " ").strip(),
                    "slug": slug,
                    "url": url,
                }
            )

    # Verify a couple against live path patterns from homepage
    print(f"Extra portfolio-like URLs: {len(extra)}")
    for e in extra[:15]:
        print(" ", e["type"], e["url"], e["title"][:50])

    out_csv = OUT / "mapa-urls-extra.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f, fieldnames=["ID", "type", "status", "title", "slug", "url"]
        )
        w.writeheader()
        for e in extra:
            w.writerow(e)
    print("Wrote", out_csv)

    # Also extract nav_menu_item titles/urls from postmeta is complex;
    # dump publish nav_menu_item posts count
    nav = [r for r in rows if r.get("post_type") == "nav_menu_item"]
    print("nav_menu_item rows:", len(nav))


if __name__ == "__main__":
    main()
