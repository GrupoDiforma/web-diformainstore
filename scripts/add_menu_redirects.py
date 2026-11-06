from pathlib import Path

BASE = "/web-diformainstore"
SITE = Path(__file__).resolve().parents[1] / "site"
ALIASES = {
    "floor-display": "floor-displays",
    "counter-display": "counter-displays-and-glorifiers",
    "siderack-display": "sided-display-rack",
    "3d-poster": "3d-posters-and-premium-signs",
    "sampling-stand": "sampling-stands-and-trays",
}

for src, dst in ALIASES.items():
    d = SITE / src
    d.mkdir(parents=True, exist_ok=True)
    target = f"{BASE}/{dst}/"
    (d / "index.html").write_text(
        "<!DOCTYPE html>\n"
        "<html lang=\"en\"><head>\n"
        "<meta charset=\"utf-8\">\n"
        f"<meta http-equiv=\"refresh\" content=\"0;url={target}\">\n"
        f"<link rel=\"canonical\" href=\"{target}\">\n"
        "<title>Redirecting…</title>\n"
        f"<script>location.replace('{target}');</script>\n"
        "</head><body>"
        f"<p><a href=\"{target}\">Continue</a></p>"
        "</body></html>\n",
        encoding="utf-8",
    )
    print("alias", src, "->", dst)
