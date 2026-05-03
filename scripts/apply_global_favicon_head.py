#!/usr/bin/env python3
"""One-off batch: inject root-absolute favicon + manifest + Organization JSON-LD into nexas HTML."""
from __future__ import annotations

import re
import sys
from pathlib import Path

NEXAS = Path(__file__).resolve().parent.parent / "nexas"

MARKER = "<!-- TAI global favicon, manifest, Organization -->"

SNIPPET = """    <!-- TAI global favicon, manifest, Organization -->
    <link rel="icon" href="/favicon.ico">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="192x192" href="/android-chrome-192x192.png">
    <link rel="icon" type="image/png" sizes="512x512" href="/android-chrome-512x512.png">
    <link rel="manifest" href="/site.webmanifest">
    <meta name="theme-color" content="#0f172a">
    <script type="application/ld+json" id="tai-org-jsonld">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "TAI Engineering",
  "url": "https://taieng.co.kr",
  "logo": "https://taieng.co.kr/logo-512.png"
}
</script>
"""


def strip_previous_injection(html: str) -> str:
    return re.sub(
        r"\s*<!-- TAI global favicon, manifest, Organization -->.*?</script>\s*",
        "\n",
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )


def strip_old_head_icons(html: str) -> str:
    html = re.sub(r"<link\s+rel=[\"']shortcut\s+icon[\"'][^>]*>\s*", "", html, flags=re.I)
    html = re.sub(r"<link\s+rel=[\"']icon[\"'][^>]*>\s*", "", html, flags=re.I)
    html = re.sub(r"<link\s+rel=[\"']apple-touch-icon[\"'][^>]*>\s*", "", html, flags=re.I)
    html = re.sub(r"<link\s+rel=[\"']manifest[\"'][^>]*>\s*", "", html, flags=re.I)
    html = re.sub(r"<meta\s+name=[\"']theme-color[\"'][^>]*>\s*", "", html, flags=re.I)
    return html


def inject(html: str) -> str | None:
    """Prefer immediately after charset meta (first 1024-byte rule); else after <head>."""
    m = re.search(
        r"<meta\s+charset\s*=\s*[\"']?utf-8[\"']?\s*/?\s*>",
        html,
        flags=re.I,
    )
    if m:
        pos = m.end()
        return html[:pos] + "\n" + SNIPPET + html[pos:]
    m = re.search(r"<head[^>]*>", html, flags=re.I)
    if not m:
        return None
    pos = m.end()
    return html[:pos] + "\n" + SNIPPET + html[pos:]


def process_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8", errors="replace")
    if "<head" not in raw.lower():
        return False
    cleaned = strip_previous_injection(raw)
    cleaned = strip_old_head_icons(cleaned)
    if MARKER in cleaned:
        path.write_text(cleaned, encoding="utf-8", newline="\n")
        return True
    updated = inject(cleaned)
    if updated is None:
        return False
    path.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    if not NEXAS.is_dir():
        print("nexas not found", file=sys.stderr)
        return 1
    n = 0
    for path in sorted(NEXAS.rglob("*.html")):
        if process_file(path):
            n += 1
            print(path.relative_to(NEXAS.parent))
    print(f"updated {n} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
