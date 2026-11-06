"""Extract pages/posts URL map from WordPress SQL dump."""
import csv
import gzip
import re
from pathlib import Path

GZ = Path(
    r"C:\Users\Edwin_Laverde\Downloads\download_diformainstore"
    r"\backup\database\diformainstore_wp61.sql.gz"
)
OUT_DIR = Path(__file__).resolve().parents[1] / "docs"


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


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Reading", GZ)
    with gzip.open(GZ, "rt", encoding="utf-8", errors="replace") as f:
        data = f.read()
    print("SQL chars:", len(data))

    mcreate = re.search(
        r"CREATE TABLE `wp0y_posts` \((.*?)\) ENGINE", data, re.S | re.I
    )
    col_names: list[str] = []
    if mcreate:
        for line in mcreate.group(1).split("\n"):
            mm = re.match(r"\s*`([^`]+)`", line)
            if mm:
                col_names.append(mm.group(1))
    print("columns", len(col_names))

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
    print("rows parsed", len(rows))

    content = []
    for r in rows:
        pt = (r.get("post_type") or "").strip()
        if pt not in {"page", "post"}:
            continue
        status = (r.get("post_status") or "").strip()
        if status in {"auto-draft", "inherit", "trash"}:
            continue
        content.append(
            {
                "ID": r.get("ID"),
                "type": pt,
                "status": status,
                "title": (r.get("post_title") or "").replace("\n", " ").strip(),
                "slug": (r.get("post_name") or "").strip(),
                "parent": r.get("post_parent"),
                "date": (r.get("post_date") or "")[:19],
                "modified": (r.get("post_modified") or "")[:19],
            }
        )

    by_id = {c["ID"]: c for c in content}

    def page_path(c: dict) -> str:
        parts: list[str] = []
        cur: dict | None = c
        seen: set = set()
        while cur:
            if cur["ID"] in seen:
                break
            seen.add(cur["ID"])
            if cur["slug"]:
                parts.append(cur["slug"])
            pid = cur.get("parent")
            if not pid or pid in ("0", 0, None):
                break
            cur = by_id.get(str(pid)) or by_id.get(pid)
            if not cur or cur["type"] != "page":
                break
        return "/" + "/".join(reversed(parts)) + "/" if parts else "/"

    for c in content:
        if c["type"] == "page":
            c["url"] = page_path(c)
        else:
            c["url"] = f"/{c['slug']}/" if c["slug"] else ""

    pages = sorted([c for c in content if c["type"] == "page"], key=lambda x: x["url"])
    posts = sorted(
        [c for c in content if c["type"] == "post"],
        key=lambda x: x["date"],
        reverse=True,
    )

    csv_path = OUT_DIR / "mapa-urls.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "ID",
                "type",
                "status",
                "title",
                "slug",
                "url",
                "parent",
                "date",
                "modified",
            ],
        )
        w.writeheader()
        for c in pages + posts:
            w.writerow({k: c.get(k, "") for k in w.fieldnames})

    md = OUT_DIR / "mapa-urls.md"
    lines = [
        "# Mapa de URLs — diformainstore.com",
        "",
        "Fuente: `diformainstore_wp61.sql.gz` · Permalinks `/%postname%/`",
        f"Extraído: páginas **{len(pages)}** · posts **{len(posts)}** (sin trash/auto-draft)",
        "",
        "## Páginas",
        "",
        "| ID | Estado | Título | URL |",
        "|---|---|---|---|",
    ]
    for c in pages:
        title = c["title"].replace("|", "\\|")
        lines.append(f"| {c['ID']} | {c['status']} | {title} | `{c['url']}` |")
    lines += [
        "",
        "## Posts (blog)",
        "",
        "| ID | Fecha | Estado | Título | URL |",
        "|---|---|---|---|---|",
    ]
    for c in posts:
        title = c["title"].replace("|", "\\|")
        lines.append(
            f"| {c['ID']} | {c['date'][:10]} | {c['status']} | {title} | `{c['url']}` |"
        )
    lines += ["", "CSV completo: [`mapa-urls.csv`](mapa-urls.csv)", ""]
    md.write_text("\n".join(lines), encoding="utf-8")

    print("Wrote", csv_path)
    print("Wrote", md)
    print("Pages", len(pages), "Posts", len(posts))
    print("Sample pages:")
    for p in pages[:20]:
        print(" ", p["status"], p["url"], "-", p["title"][:60])
    print("Sample posts:")
    for p in posts[:10]:
        print(" ", p["status"], p["url"], "-", p["title"][:60])


if __name__ == "__main__":
    main()
