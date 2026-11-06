"""Build a minimal GitHub Pages index from mapa-urls.csv."""
import csv
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "docs" / "mapa-urls.csv"


def li(row: dict) -> str:
    title = html.escape(row["title"].replace("&amp;", "&"))
    url = html.escape(row["url"])
    return (
        f'        <li><a href="https://www.diformainstore.com{url}" '
        f'target="_blank" rel="noopener">{title}</a> <code>{url}</code></li>'
    )


def main() -> None:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    pages = sorted(
        [r for r in rows if r["type"] == "page" and r["status"] == "publish"],
        key=lambda r: r["url"],
    )
    posts = sorted(
        [r for r in rows if r["type"] == "post" and r["status"] == "publish"],
        key=lambda r: r["date"],
        reverse=True,
    )

    pages_html = "\n".join(li(r) for r in pages)
    posts_html = "\n".join(li(r) for r in posts[:20])

    site = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Diforma In Store — mirror preview</title>
  <meta name="description" content="Temporary public mirror preview for the new diformainstore.com. Not the live site." />
  <meta name="robots" content="noindex,nofollow" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Manrope:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <header class="hero">
    <p class="eyebrow">Mirror preview · GitHub Pages</p>
    <h1>Diforma In Store</h1>
    <p class="lede">Temporary public URL while we rebuild the site. This is not production.</p>
    <div class="actions">
      <a class="btn primary" href="https://www.diformainstore.com" target="_blank" rel="noopener">Open live site</a>
      <a class="btn" href="https://github.com/GrupoDiforma/web-diformainstore" target="_blank" rel="noopener">Repo</a>
    </div>
  </header>

  <main>
    <section>
      <h2>URL map from WordPress backup</h2>
      <p>{len(pages)} published pages · {len(posts)} published posts. Links open the current live site until each route is rebuilt here.</p>
    </section>

    <section>
      <h2>Pages ({len(pages)})</h2>
      <ul class="map">
{pages_html}
      </ul>
    </section>

    <section>
      <h2>Recent blog posts</h2>
      <ul class="map">
{posts_html}
      </ul>
      <p class="note">Showing 20 of {len(posts)} published posts. Full list in <code>docs/mapa-urls.md</code>.</p>
    </section>
  </main>

  <footer>
    <p>Grupo Diforma · mirror seed for migration off WordPress</p>
  </footer>
</body>
</html>
"""
    (ROOT / "index.html").write_text(site, encoding="utf-8")
    print("wrote", ROOT / "index.html")


if __name__ == "__main__":
    main()
