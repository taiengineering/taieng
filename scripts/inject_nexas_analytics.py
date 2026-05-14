#!/usr/bin/env python3
"""Inject GA4, tai-analytics.js, and data-tai-track on CTA <a>/<button> (same-line tags only)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "nexas"

GA = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-JRP9SHHC5M"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-JRP9SHHC5M');
</script>
"""

TA_SCRIPT = '<script src="/assets/js/tai-analytics.js"></script>'


def skip_path(p: Path) -> bool:
    return "assets" in p.parts


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)


def line_infer_location(line: str) -> str:
    ll = line.lower()
    if "idx-hero" in ll or "hero-" in ll or "saas-hero" in ll or "svc-hero" in ll:
        return "hero"
    if "footer" in ll or "footer-inner" in ll:
        return "footer"
    if "pricing" in ll or "price-card" in ll or "sp-price" in ll or "diag-nudge" in ll:
        return "pricing"
    if "cta" in ll or "banner" in ll or "flow-cta" in ll:
        return "cta"
    return "content"


def classify_cta(visible: str) -> tuple[str, str | None] | None:
    t = re.sub(r"\s+", " ", visible.replace("\xa0", " ")).strip()
    if not t:
        return None
    if "모듈 둘러보기" in t:
        return "cta_click", "hero"
    if "무료 법령진단" in t or "무료 진단" in t:
        return "free_diagnosis_start", None
    if "무료" in t and ("법령진단" in t or "법령 진단" in t) and len(t) <= 120:
        return "free_diagnosis_start", None
    if "요금제 확인" in t:
        return "cta_click", None
    if "시작하기" in t and len(t) <= 50:
        return "cta_click", None
    if re.search(r"\b회원가입\b", t) or t.strip() in ("가입", "무료 가입"):
        return "cta_click", None
    if "자세히 알아보기" in t or ("자세히 보기" in t and len(t) <= 48):
        return "cta_click", None
    if "문의" in t and len(t) <= 40:
        return "consultation_click", None
    if "상담" in t and len(t) <= 45:
        return "consultation_click", None
    if "연결" in t and len(t) <= 24:
        return "consultation_click", None
    return None


def find_gt_end(s: str, start: int) -> int:
    """Index of '>' closing the opening tag that starts at start ('<')."""
    i = start + 1
    while i < len(s):
        ch = s[i]
        if ch == ">":
            return i
        if ch in "\"'":
            q = ch
            i += 1
            while i < len(s):
                if s[i] == "\\":
                    i += 2
                    continue
                if s[i] == q:
                    i += 1
                    break
                i += 1
            continue
        i += 1
    return -1


def find_tag_open(s: str, pos: int, tag: str) -> tuple[int, int] | None:
    m = re.search(rf"<{tag}\b", s[pos:], re.I)
    if not m:
        return None
    open_start = pos + m.start()
    gt = find_gt_end(s, open_start)
    if gt < 0:
        return None
    return open_start, gt


def process_line_for_tag(line: str, tag: str, close: str) -> str:
    pos = 0
    out: list[str] = []
    close_l = close.lower()
    while pos < len(line):
        hit = find_tag_open(line, pos, tag)
        if not hit:
            out.append(line[pos:])
            break
        open_start, gt = hit
        out.append(line[pos:open_start])
        open_tag = line[open_start : gt + 1]
        if "data-tai-track" in open_tag.lower():
            cend = line.lower().find(close_l, gt + 1)
            if cend == -1:
                out.append(line[open_start:])
                break
            close_actual = line[cend : cend + len(close)]
            out.append(line[open_start : cend + len(close_actual)])
            pos = cend + len(close_actual)
            continue
        cend = line.lower().find(close_l, gt + 1)
        if cend == -1:
            out.append(line[open_start:])
            break
        inner = line[gt + 1 : cend]
        close_actual = line[cend : cend + len(close)]
        visible = strip_tags(inner)
        rule = classify_cta(visible)
        if rule:
            track, loc_fixed = rule
            loc = loc_fixed or line_infer_location(line)
            ins = f' data-tai-track="{track}" data-tai-location="{loc}"'
            out.append(line[open_start:gt] + ins + ">")
            out.append(inner + close_actual)
        else:
            out.append(line[open_start : cend + len(close_actual)])
        pos = cend + len(close_actual)
    return "".join(out)


def process_line(line: str) -> str:
    line = process_line_for_tag(line, "a", "</a>")
    line = process_line_for_tag(line, "button", "</button>")
    return line


def insert_ga(raw: str) -> tuple[str, bool]:
    if "G-JRP9SHHC5M" in raw:
        return raw, False
    m = re.search(r"<head[^>]*>", raw, flags=re.I)
    if not m:
        return raw, False
    pos = m.end()
    return raw[:pos] + "\n" + GA + raw[pos:], True


def insert_tai_script(raw: str) -> tuple[str, bool]:
    if "tai-analytics.js" in raw:
        return raw, False
    ms = list(re.finditer(r"</body>", raw, flags=re.I))
    if not ms:
        return raw, False
    i = ms[-1].start()
    return raw[:i] + TA_SCRIPT + "\n" + raw[i:], True


def process_file(path: Path) -> tuple[bool, bool, int]:
    original = path.read_text(encoding="utf-8", errors="replace")
    raw, ga = insert_ga(original)
    raw, ta = insert_tai_script(raw)
    before = raw.count("data-tai-track")
    lines = raw.splitlines(keepends=True)
    new_lines = [process_line(l) for l in lines]
    raw2 = "".join(new_lines)
    after = raw2.count("data-tai-track")
    if raw2 != original:
        path.write_text(raw2, encoding="utf-8")
    return ga, ta, max(0, after - before)


def main() -> None:
    ga_n = ta_n = cta_n = 0
    for p in sorted(ROOT.rglob("*.html")):
        if skip_path(p):
            continue
        g, t, c = process_file(p)
        ga_n += int(g)
        ta_n += int(t)
        cta_n += c
    print("GA inserted:", ga_n)
    print("tai-analytics inserted:", ta_n)
    print("CTA attrs added (approx):", cta_n)


if __name__ == "__main__":
    main()
