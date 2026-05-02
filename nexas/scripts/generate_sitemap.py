#!/usr/bin/env python3
"""
Supabase에서 ID를 조회해 섹션별 사이트맵 + sitemap_index.xml 생성.

섹션별 파일:
  sitemap_marketing.xml
  sitemap_news[_N].xml       — kosha_safety_materials
  sitemap_cases[_N].xml      — 사고 국내+건설 (한 섹션으로 합산 후 5,000건 단위 분할)
  sitemap_laws[_N].xml       — law_revision_board (공개·게시)
  sitemap_precedents[_N].xml — industrial_accident_precedents

분할: 파일당 URL이 5,000건 초과 시 *_1.xml, *_2.xml …

실행: cd nexas && python3 scripts/generate_sitemap.py

환경변수: SUPABASE_URL, SUPABASE_ANON_KEY, SITEMAP_SITE_ORIGIN, SITEMAP_LASTMOD (기본 2026-05-02)
"""

from __future__ import annotations

import glob
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

# ── 설정 ─────────────────────────────────────────────────
SITE_ORIGIN = os.environ.get("SITEMAP_SITE_ORIGIN", "https://taieng.co.kr").rstrip("/")
LASTMOD = os.environ.get("SITEMAP_LASTMOD", "2026-05-02")

DEFAULT_SB = "https://vwlahtguyggrhvslabax.supabase.co/rest/v1"
DEFAULT_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ3bGFodGd1eWdncmh2c2xhYmF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcyOTE1OTYsImV4cCI6MjA5Mjg2NzU5Nn0."
    "Yp6P7ahaCuna_gwYC8_S2KD081Ov9Fs65e9o_AenP48"
)

SB_BASE = os.environ.get("SUPABASE_URL", DEFAULT_SB).rstrip("/")
if not SB_BASE.endswith("/rest/v1"):
    SB_BASE = SB_BASE.rstrip("/") + "/rest/v1"

ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", DEFAULT_KEY)

PAGE_SIZE = 1000
# 섹션 파일당 최대 URL 수 — 초과 시 *_1.xml, *_2.xml 로 분할
MAX_URLS_PER_SECTION_FILE = 5000

NEXUS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

MARKETING_PATHS = [
    "/",
    "/index.html",
    "/free-diagnosis.html",
    "/for-business-owner.html",
    "/for-safety-manager.html",
    "/safety-news.html",
    "/accident-cases.html",
    "/law-updates.html",
    "/precedent-search.html",
]


def _headers() -> dict[str, str]:
    return {
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {ANON_KEY}",
        "Accept": "application/json",
    }


def _fetch_json(url: str) -> list[dict]:
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def fetch_ids_paged(
    table: str,
    select: str = "id",
    extra_query: str = "",
    order_by: str = "id.asc",
) -> list[str]:
    out: list[str] = []
    offset = 0
    while True:
        q = (
            f"{SB_BASE}/{table}?select={select}"
            f"&order={urllib.parse.quote(order_by, safe='.')}"
            f"&limit={PAGE_SIZE}&offset={offset}"
        )
        if extra_query:
            q += "&" + extra_query.lstrip("&")
        rows = _fetch_json(q)
        if not rows:
            break
        for row in rows:
            rid = row.get("id")
            if rid is None:
                continue
            out.append(str(rid))
        if len(rows) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return out


def loc_escape(url: str) -> str:
    return url.replace("&", "&amp;")


def write_urlset(out_path: str, urls: list[str], lastmod: str) -> None:
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fh.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u in urls:
            fh.write("  <url>\n")
            fh.write(f"    <loc>{loc_escape(u)}</loc>\n")
            fh.write(f"    <lastmod>{lastmod}</lastmod>\n")
            fh.write("    <changefreq>weekly</changefreq>\n")
            fh.write("    <priority>0.6</priority>\n")
            fh.write("  </url>\n")
        fh.write("</urlset>\n")


def write_section_chunked(basename: str, urls: list[str], lastmod: str) -> list[str]:
    """
    basename 예: sitemap_news → sitemap_news.xml 또는 sitemap_news_1.xml …
    생성된 파일명(확장자 포함) 리스트 반환.
    """
    if not urls:
        return []
    created: list[str] = []
    n = len(urls)
    if n <= MAX_URLS_PER_SECTION_FILE:
        fname = f"{basename}.xml"
        write_urlset(os.path.join(NEXUS_ROOT, fname), urls, lastmod)
        created.append(fname)
        return created
    part = 1
    for i in range(0, n, MAX_URLS_PER_SECTION_FILE):
        chunk = urls[i : i + MAX_URLS_PER_SECTION_FILE]
        fname = f"{basename}_{part}.xml"
        write_urlset(os.path.join(NEXUS_ROOT, fname), chunk, lastmod)
        created.append(fname)
        part += 1
    return created


def write_sitemap_index(entries: list[tuple[str, str]], out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fh.write('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for fname, lm in entries:
            fh.write("  <sitemap>\n")
            fh.write(f"    <loc>{SITE_ORIGIN}/{fname}</loc>\n")
            fh.write(f"    <lastmod>{lm}</lastmod>\n")
            fh.write("  </sitemap>\n")
        fh.write("</sitemapindex>\n")


def remove_obsolete_sitemaps() -> None:
    """이전 단일 대형 sitemap.xml 등 구 패턴 삭제 (인덱스·신규 섹션 파일 제외)."""
    patterns = ["sitemap-[0-9]*.xml"]
    for pat in patterns:
        for p in glob.glob(os.path.join(NEXUS_ROOT, pat)):
            try:
                os.remove(p)
                print(f"Removed obsolete {p}", file=sys.stderr)
            except OSError:
                pass


def main() -> int:
    lastmod = LASTMOD
    index_entries: list[tuple[str, str]] = []

    marketing_urls = [SITE_ORIGIN + p for p in MARKETING_PATHS]
    mpath = os.path.join(NEXUS_ROOT, "sitemap_marketing.xml")
    write_urlset(mpath, marketing_urls, lastmod)
    print(f"Wrote {mpath} ({len(marketing_urls)} urls)", file=sys.stderr)
    index_entries.append(("sitemap_marketing.xml", lastmod))

    print("Fetching kosha_safety_materials …", file=sys.stderr)
    news_urls: list[str] = []
    for rid in fetch_ids_paged("kosha_safety_materials"):
        q = urllib.parse.urlencode({"id": rid})
        news_urls.append(f"{SITE_ORIGIN}/safety-news-detail.html?{q}")
    news_files = write_section_chunked("sitemap_news", news_urls, lastmod)
    for fn in news_files:
        index_entries.append((fn, lastmod))
    print(f"  news: {len(news_urls)} URLs → {len(news_files)} file(s)", file=sys.stderr)

    print("Fetching accident cases …", file=sys.stderr)
    case_urls: list[str] = []
    for rid in fetch_ids_paged("kosha_accident_cases", extra_query="title=not.is.null"):
        q = urllib.parse.urlencode({"id": rid, "tab": "domestic"})
        case_urls.append(f"{SITE_ORIGIN}/accident-case-detail.html?{q}")
    for rid in fetch_ids_paged("kosha_construction_accidents"):
        q = urllib.parse.urlencode({"id": rid, "tab": "construction"})
        case_urls.append(f"{SITE_ORIGIN}/accident-case-detail.html?{q}")
    for fn in write_section_chunked("sitemap_cases", case_urls, lastmod):
        index_entries.append((fn, lastmod))

    print("Fetching law_revision_board …", file=sys.stderr)
    law_extra = "is_public=eq.true&status=eq.PUBLISHED"
    law_urls: list[str] = []
    for rid in fetch_ids_paged("law_revision_board", extra_query=law_extra):
        q = urllib.parse.urlencode({"id": str(rid)})
        law_urls.append(f"{SITE_ORIGIN}/law-update-detail.html?{q}")
    for fn in write_section_chunked("sitemap_laws", law_urls, lastmod):
        index_entries.append((fn, lastmod))

    print("Fetching industrial_accident_precedents …", file=sys.stderr)
    prec_urls: list[str] = []
    for rid in fetch_ids_paged("industrial_accident_precedents"):
        q = urllib.parse.urlencode({"id": rid})
        prec_urls.append(f"{SITE_ORIGIN}/precedent-detail.html?{q}")
    for fn in write_section_chunked("sitemap_precedents", prec_urls, lastmod):
        index_entries.append((fn, lastmod))

    remove_obsolete_sitemaps()

    idx_path = os.path.join(NEXUS_ROOT, "sitemap_index.xml")
    write_sitemap_index(index_entries, idx_path)
    print(f"Wrote {idx_path} ({len(index_entries)} child sitemaps)", file=sys.stderr)

    root_alias = os.path.join(NEXUS_ROOT, "sitemap.xml")
    with open(idx_path, encoding="utf-8") as r:
        idx_body = r.read()
    with open(root_alias, "w", encoding="utf-8") as fh:
        fh.write(idx_body)
    print(f"Wrote {root_alias} (alias of sitemap_index.xml)", file=sys.stderr)

    total_detail = len(news_urls) + len(case_urls) + len(law_urls) + len(prec_urls)
    print(
        f"Done. Marketing {len(marketing_urls)}, detail URLs {total_detail}.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as e:
        print(f"HTTP error: {e.code} {e.reason}", file=sys.stderr)
        raise SystemExit(1)
    except urllib.error.URLError as e:
        print(f"URL error: {e.reason}", file=sys.stderr)
        raise SystemExit(1)
