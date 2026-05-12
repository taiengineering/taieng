#!/usr/bin/env python3
"""
NFTC/KDS/기술기준 전용 parser
article_type IN ('장', '절', '조', '항', '목') — 5,331 articles 대상

대표적인 법령:
- NFTC (소방청 화재안전기술기준): 1.7.1.2 형식
- KDS (국토부 국가건설기준): 1.5 형식
- 기타 기술기준 (방사선·작업환경 등)

KEC parser와 동일 logic이지만:
- article_type IN ('장','절','조','항','목') 필터
- article_title 시작에서 [\d.]+ 추출 (KEC는 [KEC ...])
- base_code = {article_code 앞 3 부분}.{title 번호}
  예: article_code='FIR.T.002.0001-000', title='1.7.1.2 ...' → base='FIR.T.002.1.7.1.2'

Usage:
    railway run python3 docs/extraction/scripts/parse_nftc_kds_parts.py --dry-run
    railway run python3 docs/extraction/scripts/parse_nftc_kds_parts.py --skip-existing

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


# ============================================================
# 환경
# ============================================================
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


TARGET_ARTICLE_TYPES = ('장', '절', '조', '항', '목')


# ============================================================
# 정규식
# ============================================================
# article_title 시작에서 점 분리 번호 추출 (예: "1.7.1.2 \"고체에어로졸..." → "1.7.1.2")
# "1 . 일반사항" 같은 공백 포함도 처리 (split 후 첫 토큰)
NFTC_NUMBER_PATTERN = re.compile(r'^\s*(\d+(?:\.\d+)*)')

# 호: ^N. (line 시작)
CLAUSE_PATTERN = re.compile(r'^(\d+)\.\s', re.MULTILINE)

# 목: ^X. (line 시작, 한글 한 글자)
SUBCLAUSE_PATTERN = re.compile(r'^([가-힣])\.\s', re.MULTILINE)

# 단서
PROVISO_PATTERN = re.compile(r'(?:^|\.|\s)\s*(다만,\s*)')

# 인용 (참조)
REFERENCE_PATTERN = re.compile(
    r'\b\d+(?:\.\d+){1,3}\b'
    r'|제\d+조(?:의\d+)?(?:제\d+항)?(?:제\d+호)?(?:[가-힣]목)?'
)


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


def fetch_all_paged(table, columns, filters=None, in_filter=None, page_size=1000, hard_limit=None):
    """페이징 조회 + in_filter 지원."""
    all_rows = []
    offset = 0
    while True:
        def _fetch():
            q = supabase.from_(table).select(columns)
            if filters:
                for k, v in filters.items():
                    q = q.eq(k, v)
            if in_filter:
                col, vals = in_filter
                q = q.in_(col, list(vals))
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
# 헬퍼
# ============================================================
def has_reference(text: str) -> bool:
    return bool(REFERENCE_PATTERN.search(text))


def split_main_and_proviso(text: str) -> Tuple[str, Optional[str]]:
    m = PROVISO_PATTERN.search(text)
    if not m:
        return text.strip(), None
    main = text[:m.start(1)].rstrip().rstrip('.').strip()
    if main and not main.endswith('.'):
        main += '.'
    proviso = text[m.start(1):].strip()
    return main, proviso


def add_part(parts, sort_ref, **fields):
    sort_ref[0] += 1
    fields['id'] = str(uuid.uuid4())
    fields['sort_order'] = sort_ref[0]
    parts.append(fields)
    return fields['id']


def extract_number_from_title(article_title: str) -> Optional[str]:
    """article_title 시작에서 점 분리 번호 추출."""
    if not article_title:
        return None
    m = NFTC_NUMBER_PATTERN.match(article_title)
    return m.group(1) if m else None


def build_base_code(article_code: str, nftc_number: str) -> str:
    """
    article_code='FIR.T.002.0001-000', nftc_number='1.7.1.2'
    → 'FIR.T.002.1.7.1.2'
    """
    parts = article_code.split('.')
    if len(parts) < 3:
        return f"{article_code}.{nftc_number}"
    prefix = '.'.join(parts[:3])  # FIR.T.002
    return f"{prefix}.{nftc_number}"


# ============================================================
# 핵심 분해 (KEC parser와 동일 logic)
# ============================================================
def parse_nftc_article(article_text: str, article_id: str, base_code: str) -> List[Dict[str, Any]]:
    parts: List[Dict[str, Any]] = []
    sort_ref = [0]

    text = article_text.strip()
    if not text:
        return parts

    # article header line 분리 (예: "1.7.1.2 \"고체에어로졸..." 첫 line)
    lines = text.split('\n')
    header_line = lines[0].strip() if lines else ''
    body_text = '\n'.join(lines[1:]) if len(lines) > 1 else ''

    # 호 위치 찾기
    clause_matches = list(CLAUSE_PATTERN.finditer(body_text))

    if clause_matches:
        intro_text = body_text[:clause_matches[0].start()].strip()
    else:
        intro_text = body_text.strip()

    paragraph_text = header_line
    if intro_text:
        paragraph_text += '\n' + intro_text
    paragraph_text = paragraph_text.strip()

    # paragraph INSERT
    para_main, para_proviso = split_main_and_proviso(paragraph_text)
    para_part_code = f"{base_code}.0"
    para_id = add_part(parts, sort_ref,
        article_id=article_id,
        part_type='paragraph',
        paragraph_no=None, clause_no=None, subclause_code=None,
        depth=1,
        part_text=para_main,
        has_proviso=bool(para_proviso),
        amended_dates=None,
        has_reference=has_reference(para_main),
        part_code=para_part_code,
        parent_id=None,
    )

    if para_proviso:
        add_part(parts, sort_ref,
            article_id=article_id,
            part_type='proviso',
            paragraph_no=None, clause_no=None, subclause_code=None,
            depth=1,
            part_text=para_proviso,
            has_proviso=False,
            amended_dates=None,
            has_reference=has_reference(para_proviso),
            part_code=f"{para_part_code}.D",
            parent_id=para_id,
        )

    # 호 분리
    if clause_matches:
        for i, m in enumerate(clause_matches):
            clause_no = int(m.group(1))
            start = m.end()
            end = clause_matches[i + 1].start() if i + 1 < len(clause_matches) else len(body_text)
            clause_text = body_text[start:end].strip()

            cls_main, cls_proviso = split_main_and_proviso(clause_text)
            sub_matches = list(SUBCLAUSE_PATTERN.finditer(cls_main))

            if sub_matches:
                cls_main_text = cls_main[:sub_matches[0].start()].strip()
            else:
                cls_main_text = cls_main

            cls_part_code = f"{para_part_code}.{clause_no}"
            cls_id = add_part(parts, sort_ref,
                article_id=article_id,
                part_type='clause',
                paragraph_no=None, clause_no=clause_no, subclause_code=None,
                depth=2,
                part_text=cls_main_text,
                has_proviso=bool(cls_proviso),
                amended_dates=None,
                has_reference=has_reference(cls_main_text),
                part_code=cls_part_code,
                parent_id=para_id,
            )

            if cls_proviso:
                add_part(parts, sort_ref,
                    article_id=article_id,
                    part_type='proviso',
                    paragraph_no=None, clause_no=clause_no, subclause_code=None,
                    depth=2,
                    part_text=cls_proviso,
                    has_proviso=False,
                    amended_dates=None,
                    has_reference=has_reference(cls_proviso),
                    part_code=f"{cls_part_code}.D",
                    parent_id=cls_id,
                )

            # 목 분리
            for j, sub_m in enumerate(sub_matches):
                sub_marker = sub_m.group(1)
                sub_start = sub_m.end()
                sub_end = sub_matches[j + 1].start() if j + 1 < len(sub_matches) else len(cls_main)
                sub_text = cls_main[sub_start:sub_end].strip()

                sub_main, sub_proviso = split_main_and_proviso(sub_text)
                sub_part_code = f"{cls_part_code}.{sub_marker}"

                sub_id = add_part(parts, sort_ref,
                    article_id=article_id,
                    part_type='subclause',
                    paragraph_no=None, clause_no=clause_no, subclause_code=sub_marker,
                    depth=3,
                    part_text=sub_main,
                    has_proviso=bool(sub_proviso),
                    amended_dates=None,
                    has_reference=has_reference(sub_main),
                    part_code=sub_part_code,
                    parent_id=cls_id,
                )

                if sub_proviso:
                    add_part(parts, sort_ref,
                        article_id=article_id,
                        part_type='proviso',
                        paragraph_no=None, clause_no=clause_no, subclause_code=sub_marker,
                        depth=3,
                        part_text=sub_proviso,
                        has_proviso=False,
                        amended_dates=None,
                        has_reference=has_reference(sub_proviso),
                        part_code=f"{sub_part_code}.D",
                        parent_id=sub_id,
                    )

    return parts


# ============================================================
# DB
# ============================================================
def insert_parts(parts: List[Dict[str, Any]]) -> int:
    if not parts:
        return 0
    def _insert():
        return supabase.from_('law_article_part').insert(parts).execute().data
    res = with_retry(_insert)
    return len(res) if res else 0


def fetch_target_articles_via_view():
    """v_law_article_code에서 NFTC/KDS articles fetch (article_type IN target)"""
    all_rows = []
    for atype in TARGET_ARTICLE_TYPES:
        rows = fetch_all_paged(
            'v_law_article_code',
            'article_id,article_code,article_type,law_name',
            filters={'article_type': atype},
        )
        all_rows.extend(rows)
    # distinct
    seen = set()
    unique = []
    for a in all_rows:
        aid = a.get('article_id')
        if aid and aid not in seen:
            seen.add(aid)
            unique.append(a)
    return unique


# ============================================================
# 메인
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="NFTC/KDS 전용 article 분해 (article_type IN ('장','절','조','항','목'))"
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reset", action="store_true",
                        help="기존 NFTC/KDS parts 삭제 후 재처리")
    parser.add_argument("--skip-existing", action="store_true",
                        help="이미 적재된 article_id skip")
    args = parser.parse_args()

    # 1. NFTC/KDS articles fetch
    print(f"[INFO] article_type {TARGET_ARTICLE_TYPES} fetch 중...")
    articles = fetch_target_articles_via_view()
    print(f"[INFO] 가져온 articles: {len(articles)}")

    if args.limit:
        articles = articles[:args.limit]
        print(f"[INFO] limit 적용: {len(articles)}")

    # 2. reset
    if args.reset and not args.dry_run:
        confirm = input("WARNING: NFTC/KDS parts 삭제 후 재처리. 계속? [y/N] ")
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
        print(f"[INFO] 기존 적재된 NFTC/KDS article_id: {len(existing_ids)}")

    # 4. 분해 + INSERT
    total_parts = 0
    skipped = 0
    errors = []

    for i, art in enumerate(articles):
        article_id = art['article_id']
        article_code = art['article_code']
        article_type = art['article_type']

        if article_id in existing_ids:
            skipped += 1
            continue

        # article_text fetch
        try:
            art_data = with_retry(lambda: supabase.from_('law_article').select(
                'article_title,article_text,article_type'
            ).eq('id', article_id).execute().data)
        except Exception as e:
            errors.append((article_code, f"fetch: {e}"))
            continue

        if not art_data or not art_data[0].get('article_text'):
            continue

        article_title = art_data[0].get('article_title', '')
        article_text = art_data[0].get('article_text', '')
        if len(article_text) < 5:
            continue

        # NFTC 번호 추출
        nftc_number = extract_number_from_title(article_title)
        if not nftc_number:
            errors.append((article_code, f"번호 추출 실패: {article_title[:50]}"))
            continue

        base_code = build_base_code(article_code, nftc_number)

        try:
            parts = parse_nftc_article(article_text, article_id, base_code)
            if not parts:
                continue
            total_parts += len(parts)

            if args.dry_run:
                if i < 5:
                    print(f"\n=== [{nftc_number}] ({article_type}) {article_title[:60]} ({len(parts)} parts) ===")
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
    if errors:
        print(f"[ERRORS] {len(errors)} articles failed:")
        for code, err in errors[:10]:
            print(f"  {code}: {err}")


if __name__ == "__main__":
    main()
