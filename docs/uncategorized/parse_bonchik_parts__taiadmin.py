#!/usr/bin/env python3
"""
본칙 (행정고시류) 전용 parser
article_type = '본칙' — 5,444 articles 대상

대표적인 법령:
- 화학물질 시험기관 규정
- 신규화학물질의 유해성·위험성 조사 등에 관한 고시
- 작업환경측정 및 정도관리 등에 관한 고시
- 일부 NFTC도 본칙으로 분류됨 (혼재)

특징: 일반 법령 형태이지만 마커 ([①][1.][가.]) 부착 안 됨

처리 logic:
1. article_text에 마커 부착 전처리 (① → [①]①, ^N.\s → [N.]N. , ^X.\s → [X.]X.)
2. 일반 parser logic 적용 (parse_article_parts.py 동일)
3. base_code = article_code (v_law_article_code 그대로)

Usage:
    railway run python3 docs/extraction/scripts/parse_bonchik_parts.py --dry-run
    railway run python3 docs/extraction/scripts/parse_bonchik_parts.py --skip-existing

작성: 2026-05-05 (핸드오프)
"""

import argparse
import os
import re
import sys
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

try:
    import httpx
    from supabase import Client, create_client
except ImportError:
    print("[ERROR] pip install supabase httpx", file=sys.stderr)
    sys.exit(1)


SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("SUPABASE_KEY")
)
if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 없음.", file=sys.stderr)
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================
# 마커 부착 전처리 (본칙 핵심 logic)
# ============================================================
def add_markers(text: str) -> str:
    """
    본칙 article_text에 일반 parser용 마커 부착.

    원문: 제9조(의견청취 등) ① 한국산업안전보건공단(이하 "공단"이라 한다)은 ...
              1. 해당 화학물질이 ...
              2. 해당 화학물질이 ...

    부착 후: 제9조(의견청취 등) [①]① 한국산업안전보건공단(이하 "공단"이라 한다)은 ...
                  [1.]1. 해당 화학물질이 ...
                  [2.]2. 해당 화학물질이 ...
    """
    # 1. 항 마커: ① ② ... ⑮ (이미 [ ] 부착된 경우 제외)
    text = re.sub(r'(?<!\[)([①-⑮])(?!\])', r'[\1]\1', text)

    # 2. 호 마커: line 시작 + 공백 + N. + 공백
    # 자연어 "1." 잘못 부착 방지 — line 시작만 처리
    text = re.sub(r'^(\s*)(\d+)\.(\s)', r'\1[\2.]\2.\3', text, flags=re.MULTILINE)

    # 3. 목 마커: line 시작 + 공백 + X. + 공백 (한글 한 글자)
    text = re.sub(r'^(\s*)([가-힣])\.(\s)', r'\1[\2.]\2.\3', text, flags=re.MULTILINE)

    return text


# ============================================================
# 정규식 (parse_article_parts.py와 동일)
# ============================================================
PARAGRAPH_NO_MAP = {ch: i + 1 for i, ch in enumerate("①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮")}

PARAGRAPH_PATTERN = re.compile(r'\[([①-⑮])\]\s*[①-⑮]\s*')
CLAUSE_PATTERN = re.compile(r'\[(\d+)\.\]\s*\d+\.\s*')
SUBCLAUSE_PATTERN = re.compile(r'\[([가-힣])\.\]\s*[가-힣]\.\s*')
META_PATTERN = re.compile(r'<(?:개정|신설|시행)\s+([\d.,\s]+)>')

REFERENCE_PATTERN = re.compile(
    r'제\d+조(?:의\d+)?(?:제\d+항)?(?:제\d+호)?(?:[가-힣]목)?'
    r'|제\d+항(?:제\d+호)?(?:[가-힣]목)?'
    r'|제\d+호(?:[가-힣]목)?'
)

PROVISO_PATTERN = re.compile(r'(?:^|\.|\s)\s*(다만,\s*)')
ARTICLE_HEADER_PATTERN = re.compile(r'^제\d+조(?:의\d+)?\s*\([^)]+\)\s*\n?')


# ============================================================
# retry
# ============================================================
RETRY_EXCEPTIONS = (
    httpx.RemoteProtocolError, httpx.ConnectError, httpx.ReadTimeout,
    httpx.WriteTimeout, httpx.PoolTimeout, httpx.ConnectTimeout,
    httpx.NetworkError, ConnectionError,
)


def reset_supabase():
    global supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def with_retry(func, max_retries=5, initial_delay=1.0):
    for attempt in range(max_retries):
        try:
            return func()
        except RETRY_EXCEPTIONS as e:
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                print(f"  [RETRY {attempt+1}/{max_retries}] {type(e).__name__}: 대기 {delay:.1f}s + 재연결")
                time.sleep(delay)
                reset_supabase()
            else:
                raise


def fetch_all_paged(table, columns, filters=None, page_size=1000, hard_limit=None):
    all_rows = []
    offset = 0
    while True:
        def _fetch():
            q = supabase.from_(table).select(columns)
            if filters:
                for k, v in filters.items():
                    q = q.eq(k, v)
            q = q.range(offset, offset + page_size - 1)
            return q.execute().data
        batch = with_retry(_fetch)
        if not batch:
            break
        all_rows.extend(batch)
        if hard_limit and len(all_rows) >= hard_limit:
            all_rows = all_rows[:hard_limit]
            break
        if len(batch) < page_size:
            break
        offset += page_size
    return all_rows


# ============================================================
# 헬퍼 (parse_article_parts.py 동일)
# ============================================================
def split_by_pattern(text, pattern):
    result = []
    matches = list(pattern.finditer(text))
    if not matches:
        cleaned = text.strip()
        return [(None, cleaned)] if cleaned else []
    if matches[0].start() > 0:
        prefix = text[:matches[0].start()].strip()
        if prefix:
            result.append((None, prefix))
    for i, m in enumerate(matches):
        marker = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if content:
            result.append((marker, content))
    return result


def extract_meta(text):
    dates = META_PATTERN.findall(text)
    cleaned = META_PATTERN.sub('', text).strip()
    return cleaned, dates if dates else None


def has_reference(text):
    return bool(REFERENCE_PATTERN.search(text))


def find_clause_pos(text):
    m = CLAUSE_PATTERN.search(text)
    return m.start() if m else -1


def find_proviso_pos(text):
    m = PROVISO_PATTERN.search(text)
    return m.start(1) if m else -1


def split_main_and_proviso(text):
    m = PROVISO_PATTERN.search(text)
    if not m:
        return text.strip(), None
    main = text[:m.start(1)].rstrip().rstrip('.').strip()
    if main and not main.endswith('.'):
        main += '.'
    proviso = text[m.start(1):].strip()
    return main, proviso


def determine_clause_owner(text):
    cp = find_clause_pos(text)
    pp = find_proviso_pos(text)
    if cp == -1 or pp == -1:
        return 'main'
    return 'main' if cp < pp else 'proviso'


def add_part(parts, sort_ref, **fields):
    sort_ref[0] += 1
    fields['id'] = str(uuid.uuid4())
    fields['sort_order'] = sort_ref[0]
    parts.append(fields)
    return fields['id']


# ============================================================
# 호·목 처리 (parse_article_parts.py 동일)
# ============================================================
def process_clauses(parts, sort_ref, article_id, paragraph_no,
                     base_part_code, parent_id, text_with_clauses, clause_depth):
    clause_units = split_by_pattern(text_with_clauses, CLAUSE_PATTERN)
    iter_units = clause_units[1:] if clause_units and clause_units[0][0] is None else clause_units

    for cls_marker, cls_text in iter_units:
        if cls_marker is None:
            continue
        try:
            clause_no = int(cls_marker)
        except (ValueError, TypeError):
            continue

        cls_main_raw, cls_proviso_raw = split_main_and_proviso(cls_text)
        sub_units = split_by_pattern(cls_main_raw, SUBCLAUSE_PATTERN)
        if sub_units and sub_units[0][0] is None:
            cls_main_text = sub_units[0][1]
            sub_iter = sub_units[1:]
        else:
            cls_main_text = cls_main_raw
            sub_iter = sub_units if sub_units and sub_units[0][0] is not None else []

        cls_main_clean, cls_dates = extract_meta(cls_main_text)
        clause_part_code = f"{base_part_code}.{clause_no}"

        cls_id = add_part(parts, sort_ref,
            article_id=article_id, part_type='clause',
            paragraph_no=paragraph_no, clause_no=clause_no, subclause_code=None,
            depth=clause_depth, part_text=cls_main_clean,
            has_proviso=bool(cls_proviso_raw), amended_dates=cls_dates,
            has_reference=has_reference(cls_main_clean),
            part_code=clause_part_code, parent_id=parent_id,
        )

        if cls_proviso_raw:
            proviso_clean, proviso_dates = extract_meta(cls_proviso_raw)
            add_part(parts, sort_ref,
                article_id=article_id, part_type='proviso',
                paragraph_no=paragraph_no, clause_no=clause_no, subclause_code=None,
                depth=clause_depth, part_text=proviso_clean,
                has_proviso=False, amended_dates=proviso_dates,
                has_reference=has_reference(proviso_clean),
                part_code=f"{clause_part_code}.D", parent_id=cls_id,
            )

        for sub_marker, sub_text in sub_iter:
            if sub_marker is None:
                continue
            sub_main_raw, sub_proviso_raw = split_main_and_proviso(sub_text)
            sub_clean, sub_dates = extract_meta(sub_main_raw)
            sub_part_code = f"{clause_part_code}.{sub_marker}"

            sub_id = add_part(parts, sort_ref,
                article_id=article_id, part_type='subclause',
                paragraph_no=paragraph_no, clause_no=clause_no, subclause_code=sub_marker,
                depth=clause_depth + 1, part_text=sub_clean,
                has_proviso=bool(sub_proviso_raw), amended_dates=sub_dates,
                has_reference=has_reference(sub_clean),
                part_code=sub_part_code, parent_id=cls_id,
            )

            if sub_proviso_raw:
                sub_proviso_clean, sub_proviso_dates = extract_meta(sub_proviso_raw)
                add_part(parts, sort_ref,
                    article_id=article_id, part_type='proviso',
                    paragraph_no=paragraph_no, clause_no=clause_no, subclause_code=sub_marker,
                    depth=clause_depth + 1, part_text=sub_proviso_clean,
                    has_proviso=False, amended_dates=sub_proviso_dates,
                    has_reference=has_reference(sub_proviso_clean),
                    part_code=f"{sub_part_code}.D", parent_id=sub_id,
                )


# ============================================================
# 핵심 파서 (parse_article_parts.py 동일)
# ============================================================
def parse_article(article_text, article_id, base_code):
    parts = []
    sort_ref = [0]

    paragraph_units = split_by_pattern(article_text, PARAGRAPH_PATTERN)

    if not paragraph_units or all(m is None for m, _ in paragraph_units):
        full_text = article_text.strip()
        full_text = ARTICLE_HEADER_PATTERN.sub('', full_text).strip()
        if not full_text:
            return parts

        owner = determine_clause_owner(full_text)

        if owner == 'main':
            clause_units = split_by_pattern(full_text, CLAUSE_PATTERN)
            if clause_units and clause_units[0][0] is None:
                main_raw = clause_units[0][1]
            else:
                main_raw = full_text
            main_clean_raw, proviso_raw = split_main_and_proviso(main_raw)
            cleaned, dates = extract_meta(main_clean_raw)

            para_id = add_part(parts, sort_ref,
                article_id=article_id, part_type='paragraph',
                paragraph_no=None, clause_no=None, subclause_code=None,
                depth=1, part_text=cleaned,
                has_proviso=bool(proviso_raw), amended_dates=dates,
                has_reference=has_reference(cleaned),
                part_code=base_code + '.0', parent_id=None,
            )

            if proviso_raw:
                proviso_clean, proviso_dates = extract_meta(proviso_raw)
                add_part(parts, sort_ref,
                    article_id=article_id, part_type='proviso',
                    paragraph_no=None, clause_no=None, subclause_code=None,
                    depth=1, part_text=proviso_clean,
                    has_proviso=False, amended_dates=proviso_dates,
                    has_reference=has_reference(proviso_clean),
                    part_code=base_code + '.0.D', parent_id=para_id,
                )

            process_clauses(parts, sort_ref, article_id, None,
                            base_code + '.0', para_id, full_text, 2)
        else:
            pp = find_proviso_pos(full_text)
            main_raw = full_text[:pp].rstrip().rstrip('.').strip()
            if main_raw and not main_raw.endswith('.'):
                main_raw += '.'
            proviso_inner = full_text[pp:].strip()

            proviso_clause_units = split_by_pattern(proviso_inner, CLAUSE_PATTERN)
            if proviso_clause_units and proviso_clause_units[0][0] is None:
                proviso_main_raw = proviso_clause_units[0][1]
            else:
                proviso_main_raw = proviso_inner

            main_clean, dates = extract_meta(main_raw)
            para_id = add_part(parts, sort_ref,
                article_id=article_id, part_type='paragraph',
                paragraph_no=None, clause_no=None, subclause_code=None,
                depth=1, part_text=main_clean,
                has_proviso=True, amended_dates=dates,
                has_reference=has_reference(main_clean),
                part_code=base_code + '.0', parent_id=None,
            )

            proviso_clean, proviso_dates = extract_meta(proviso_main_raw)
            proviso_id = add_part(parts, sort_ref,
                article_id=article_id, part_type='proviso',
                paragraph_no=None, clause_no=None, subclause_code=None,
                depth=1, part_text=proviso_clean,
                has_proviso=False, amended_dates=proviso_dates,
                has_reference=has_reference(proviso_clean),
                part_code=base_code + '.0.D', parent_id=para_id,
            )

            process_clauses(parts, sort_ref, article_id, None,
                            base_code + '.0.D', proviso_id, proviso_inner, 2)
        return parts

    for para_marker, para_text in paragraph_units:
        if para_marker is None:
            stripped = para_text.strip()
            if not stripped or re.match(r'^제\d+조', stripped):
                continue
            continue

        para_no = PARAGRAPH_NO_MAP.get(para_marker)
        if not para_no:
            continue

        owner = determine_clause_owner(para_text)
        para_part_code = f"{base_code}.{para_no}"

        if owner == 'main':
            clause_units = split_by_pattern(para_text, CLAUSE_PATTERN)
            if clause_units and clause_units[0][0] is None:
                para_main_raw = clause_units[0][1]
            else:
                para_main_raw = para_text

            main_clean_raw, proviso_raw = split_main_and_proviso(para_main_raw)
            para_main_clean, para_dates = extract_meta(main_clean_raw)

            para_id = add_part(parts, sort_ref,
                article_id=article_id, part_type='paragraph',
                paragraph_no=para_no, clause_no=None, subclause_code=None,
                depth=1, part_text=para_main_clean,
                has_proviso=bool(proviso_raw), amended_dates=para_dates,
                has_reference=has_reference(para_main_clean),
                part_code=para_part_code, parent_id=None,
            )

            if proviso_raw:
                proviso_clean, proviso_dates = extract_meta(proviso_raw)
                add_part(parts, sort_ref,
                    article_id=article_id, part_type='proviso',
                    paragraph_no=para_no, clause_no=None, subclause_code=None,
                    depth=1, part_text=proviso_clean,
                    has_proviso=False, amended_dates=proviso_dates,
                    has_reference=has_reference(proviso_clean),
                    part_code=f"{para_part_code}.D", parent_id=para_id,
                )

            process_clauses(parts, sort_ref, article_id, para_no,
                            para_part_code, para_id, para_text, 2)
        else:
            pp = find_proviso_pos(para_text)
            main_raw = para_text[:pp].rstrip().rstrip('.').strip()
            if main_raw and not main_raw.endswith('.'):
                main_raw += '.'
            proviso_inner = para_text[pp:].strip()

            proviso_clause_units = split_by_pattern(proviso_inner, CLAUSE_PATTERN)
            if proviso_clause_units and proviso_clause_units[0][0] is None:
                proviso_main_raw = proviso_clause_units[0][1]
            else:
                proviso_main_raw = proviso_inner

            main_clean, para_dates = extract_meta(main_raw)
            para_id = add_part(parts, sort_ref,
                article_id=article_id, part_type='paragraph',
                paragraph_no=para_no, clause_no=None, subclause_code=None,
                depth=1, part_text=main_clean,
                has_proviso=True, amended_dates=para_dates,
                has_reference=has_reference(main_clean),
                part_code=para_part_code, parent_id=None,
            )

            proviso_clean, proviso_dates = extract_meta(proviso_main_raw)
            proviso_part_code = f"{para_part_code}.D"
            proviso_id = add_part(parts, sort_ref,
                article_id=article_id, part_type='proviso',
                paragraph_no=para_no, clause_no=None, subclause_code=None,
                depth=1, part_text=proviso_clean,
                has_proviso=False, amended_dates=proviso_dates,
                has_reference=has_reference(proviso_clean),
                part_code=proviso_part_code, parent_id=para_id,
            )

            process_clauses(parts, sort_ref, article_id, para_no,
                            proviso_part_code, proviso_id, proviso_inner, 2)

    return parts


# ============================================================
# DB
# ============================================================
def insert_parts(parts):
    if not parts:
        return 0
    def _insert():
        return supabase.from_('law_article_part').insert(parts).execute().data
    res = with_retry(_insert)
    return len(res) if res else 0


# ============================================================
# 메인
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="본칙 (article_type='본칙') 전용 parser — 마커 부착 전처리"
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument("--law-name", type=str)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    # 1. 본칙 articles fetch (view 사용)
    filters = {'article_type': '본칙'}
    if args.law_name:
        filters['law_name'] = args.law_name
    print(f"[INFO] 본칙 articles fetch 중...")
    articles = fetch_all_paged(
        'v_law_article_code',
        'article_id,article_code,law_name,article_type',
        filters=filters,
        hard_limit=args.limit,
    )
    # distinct
    seen = set()
    unique = []
    for a in articles:
        aid = a.get('article_id')
        if aid and aid not in seen:
            seen.add(aid)
            unique.append(a)
    if len(unique) != len(articles):
        print(f"[INFO] 중복 제거: {len(articles)} → {len(unique)}")
    articles = unique
    print(f"[INFO] 처리 대상: {len(articles)} articles")

    # 2. reset
    if args.reset and not args.dry_run:
        confirm = input("WARNING: 본칙 parts 삭제 후 재처리. 계속? [y/N] ")
        if confirm.lower() != 'y':
            print("[INFO] 취소"); return
        article_ids = [a['article_id'] for a in articles]
        for i in range(0, len(article_ids), 100):
            chunk = article_ids[i:i + 100]
            supabase.from_('law_article_part').delete().in_(
                'article_id', chunk
            ).execute()
        print(f"[INFO] 기존 parts 삭제 완료")

    # 3. skip-existing
    existing_ids = set()
    if args.skip_existing and not args.dry_run:
        all_existing = fetch_all_paged('law_article_part', 'article_id')
        existing_ids = {r['article_id'] for r in all_existing}
        target_ids = {a['article_id'] for a in articles}
        existing_ids &= target_ids
        print(f"[INFO] 기존 적재된 본칙 article_id: {len(existing_ids)}")

    # 4. 분해 + INSERT
    total_parts = 0
    skipped = 0
    errors = []
    no_marker_count = 0  # 마커 부착 후에도 분리 안 된 article (단일 paragraph)

    for i, art in enumerate(articles):
        article_id = art['article_id']
        article_code = art['article_code']

        if article_id in existing_ids:
            skipped += 1
            continue

        try:
            art_data = with_retry(lambda: supabase.from_('law_article').select(
                'article_text,article_type'
            ).eq('id', article_id).execute().data)
        except Exception as e:
            errors.append((article_code, f"fetch: {e}"))
            continue

        if not art_data or not art_data[0].get('article_text'):
            continue

        article_text = art_data[0].get('article_text', '')
        if len(article_text) < 10:
            continue

        # ⭐ 본칙 핵심: 마커 부착 전처리
        article_text_marked = add_markers(article_text)

        try:
            parts = parse_article(article_text_marked, article_id, article_code)
            if not parts:
                no_marker_count += 1
                continue
            total_parts += len(parts)

            if args.dry_run:
                if i < 5:
                    print(f"\n=== {article_code} ({len(parts)} parts) ===")
                    print(f"  원문 시작: {article_text[:80]}...")
                    print(f"  마커 부착: {article_text_marked[:120]}...")
                    for p in parts[:15]:
                        is_proviso = p['part_type'] == 'proviso'
                        indent = "  " * p['depth'] + ("  " if is_proviso else "")
                        flags = []
                        if is_proviso: flags.append("PROVISO")
                        if p['has_proviso']: flags.append("has_proviso")
                        if p['has_reference']: flags.append("ref")
                        flag_str = f" [{','.join(flags)}]" if flags else ""
                        text_preview = p['part_text'][:80].replace('\n', ' ')
                        print(f"{indent}{p['part_code']}{flag_str}: {text_preview}...")
            else:
                insert_parts(parts)
                if (i + 1) % 100 == 0:
                    print(f"[PROGRESS] {i + 1}/{len(articles)} done, parts={total_parts}, errors={len(errors)}")
        except Exception as e:
            errors.append((article_code, str(e)[:100]))
            continue

    print(f"\n[DONE] 총 분해: {total_parts} parts")
    if skipped:
        print(f"[SKIP] {skipped} articles (이미 적재)")
    if no_marker_count:
        print(f"[INFO] 마커 없는 article (paragraph 1개로 처리됨): {no_marker_count}")
    if errors:
        print(f"[ERRORS] {len(errors)} articles failed:")
        for code, err in errors[:10]:
            print(f"  {code}: {err}")


if __name__ == "__main__":
    main()
