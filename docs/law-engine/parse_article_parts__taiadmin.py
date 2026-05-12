#!/usr/bin/env python3
"""
TAI 법령 article 위계 분해 스크립트 (조 → 항/단서 → 호 → 목)

article_text를 항·호·목·단서 단위로 분해하여 law_article_part 테이블에 적재.
이미 부착된 마커 활용:
- 항: [①][②]...[⑮]
- 호: [1.][2.]...
- 목: [가.][나.][다.]...
- 단서: "다만, ..." (예외조항, 별도 part로 분리)

part_code 형식:
  IND.L.002.0005-000        = 산안법 제5조
  IND.L.002.0005-000.1      = 제5조 제1항 본문 (의무)
  IND.L.002.0005-000.1.D    = 제5조 제1항 단서 (예외)
  IND.L.002.0005-000.1.2    = 제5조 제1항 제2호 (호가 본문 자식)
  IND.L.002.0005-000.1.D.2  = 제5조 제1항 단서 안 제2호 (호가 단서 자식)
  IND.L.002.0005-000.4.2.가 = 제5조 제4항 제2호 가목

작성: 2026-05-05 (S14, v5: retry + UUID 미리생성 + INSERT 최적화)
v6 (2026-05-05): KEC 제외 — 한국전기설비규정은 마커 형식 다름, 별도 parse_kec_parts.py 사용
v7 (2026-05-05): article_type='조문' filter 추가 + distinct 보장
v7.1 (2026-05-05): proviso part_text typo fix
v8 (2026-05-05): --unprocessed-only 옵션 추가 — RPC로 미처리만 직접 fetch
   - fetch_all_paged 의 페이징 누락/중복 문제 우회
   - get_unprocessed_articles_for_parser RPC 함수 사용
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


# 별도 parser 사용 법령 (마커 형식이 일반 법령과 다름)
EXCLUDED_LAW_NAMES = {
    '한국전기설비규정',  # KEC — parse_kec_parts.py 사용
}


# ============================================================
# 정규식 패턴
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
# v5: retry + connection refresh
# ============================================================
RETRY_EXCEPTIONS = (
    httpx.RemoteProtocolError,
    httpx.ConnectError,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
    httpx.ConnectTimeout,
    httpx.NetworkError,
    ConnectionError,
)


def reset_supabase():
    """connection 끊긴 경우 새 client 생성."""
    global supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def with_retry(func, max_retries=5, initial_delay=1.0):
    """supabase 호출 retry. HTTP/2 끊김 등 자동 재시도 + 재연결."""
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


# ============================================================
# 헬퍼
# ============================================================
def split_by_pattern(text: str, pattern: re.Pattern) -> List[Tuple[Optional[str], str]]:
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


def extract_meta(text: str) -> Tuple[str, Optional[List[str]]]:
    dates = META_PATTERN.findall(text)
    cleaned = META_PATTERN.sub('', text).strip()
    return cleaned, dates if dates else None


def has_reference(text: str) -> bool:
    return bool(REFERENCE_PATTERN.search(text))


def find_clause_pos(text: str) -> int:
    m = CLAUSE_PATTERN.search(text)
    return m.start() if m else -1


def find_proviso_pos(text: str) -> int:
    m = PROVISO_PATTERN.search(text)
    return m.start(1) if m else -1


def split_main_and_proviso(text: str) -> Tuple[str, Optional[str]]:
    m = PROVISO_PATTERN.search(text)
    if not m:
        return text.strip(), None
    main = text[:m.start(1)].rstrip().rstrip('.').strip()
    if main and not main.endswith('.'):
        main += '.'
    proviso = text[m.start(1):].strip()
    return main, proviso


def determine_clause_owner(text: str) -> str:
    cp = find_clause_pos(text)
    pp = find_proviso_pos(text)
    if cp == -1 or pp == -1:
        return 'main'
    return 'main' if cp < pp else 'proviso'


def fetch_all_paged(table_or_view: str, columns: str, filters: Dict[str, Any] = None,
                     page_size: int = 1000, hard_limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """페이징 조회. retry 적용."""
    all_rows = []
    offset = 0
    while True:
        def _fetch():
            q = supabase.from_(table_or_view).select(columns)
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


def fetch_unprocessed_via_rpc() -> List[Dict[str, Any]]:
    """v8: 미처리 article만 RPC로 직접 fetch (페이징 누락/중복 우회)"""
    excluded = list(EXCLUDED_LAW_NAMES)

    def _rpc():
        return supabase.rpc(
            'get_unprocessed_articles_for_parser',
            {'excluded_law_names': excluded}
        ).execute().data

    return with_retry(_rpc) or []


# ============================================================
# part 추가 헬퍼 (v5: id 미리 생성)
# ============================================================
def add_part(parts: List[Dict[str, Any]], sort_ref: List[int], **fields) -> str:
    """part dict 추가. id 미리 생성. 반환: 생성된 uuid str"""
    sort_ref[0] += 1
    fields['id'] = str(uuid.uuid4())
    fields['sort_order'] = sort_ref[0]
    parts.append(fields)
    return fields['id']


# ============================================================
# 호·목 처리
# ============================================================
def process_clauses(parts: List[Dict[str, Any]], sort_ref: List[int],
                     article_id: str, paragraph_no: Optional[int],
                     base_part_code: str, parent_id: str,
                     text_with_clauses: str, clause_depth: int):
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
            article_id=article_id,
            part_type='clause',
            paragraph_no=paragraph_no,
            clause_no=clause_no,
            subclause_code=None,
            depth=clause_depth,
            part_text=cls_main_clean,
            has_proviso=bool(cls_proviso_raw),
            amended_dates=cls_dates,
            has_reference=has_reference(cls_main_clean),
            part_code=clause_part_code,
            parent_id=parent_id,
        )

        if cls_proviso_raw:
            proviso_clean, proviso_dates = extract_meta(cls_proviso_raw)
            add_part(parts, sort_ref,
                article_id=article_id,
                part_type='proviso',
                paragraph_no=paragraph_no,
                clause_no=clause_no,
                subclause_code=None,
                depth=clause_depth,
                part_text=proviso_clean,
                has_proviso=False,
                amended_dates=proviso_dates,
                has_reference=has_reference(proviso_clean),
                part_code=f"{clause_part_code}.D",
                parent_id=cls_id,
            )

        for sub_marker, sub_text in sub_iter:
            if sub_marker is None:
                continue
            sub_main_raw, sub_proviso_raw = split_main_and_proviso(sub_text)
            sub_clean, sub_dates = extract_meta(sub_main_raw)
            sub_part_code = f"{clause_part_code}.{sub_marker}"

            sub_id = add_part(parts, sort_ref,
                article_id=article_id,
                part_type='subclause',
                paragraph_no=paragraph_no,
                clause_no=clause_no,
                subclause_code=sub_marker,
                depth=clause_depth + 1,
                part_text=sub_clean,
                has_proviso=bool(sub_proviso_raw),
                amended_dates=sub_dates,
                has_reference=has_reference(sub_clean),
                part_code=sub_part_code,
                parent_id=cls_id,
            )

            if sub_proviso_raw:
                sub_proviso_clean, sub_proviso_dates = extract_meta(sub_proviso_raw)
                add_part(parts, sort_ref,
                    article_id=article_id,
                    part_type='proviso',
                    paragraph_no=paragraph_no,
                    clause_no=clause_no,
                    subclause_code=sub_marker,
                    depth=clause_depth + 1,
                    part_text=sub_proviso_clean,
                    has_proviso=False,
                    amended_dates=sub_proviso_dates,
                    has_reference=has_reference(sub_proviso_clean),
                    part_code=f"{sub_part_code}.D",
                    parent_id=sub_id,
                )


# ============================================================
# 핵심 파서
# ============================================================
def parse_article(article_text: str, article_id: str, base_code: str) -> List[Dict[str, Any]]:
    parts: List[Dict[str, Any]] = []
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
                article_id=article_id,
                part_type='paragraph',
                paragraph_no=None, clause_no=None, subclause_code=None,
                depth=1,
                part_text=cleaned,
                has_proviso=bool(proviso_raw),
                amended_dates=dates,
                has_reference=has_reference(cleaned),
                part_code=base_code + '.0',
                parent_id=None,
            )

            if proviso_raw:
                proviso_clean, proviso_dates = extract_meta(proviso_raw)
                add_part(parts, sort_ref,
                    article_id=article_id,
                    part_type='proviso',
                    paragraph_no=None, clause_no=None, subclause_code=None,
                    depth=1,
                    part_text=proviso_clean,
                    has_proviso=False,
                    amended_dates=proviso_dates,
                    has_reference=has_reference(proviso_clean),
                    part_code=base_code + '.0.D',
                    parent_id=para_id,
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
                article_id=article_id,
                part_type='paragraph',
                paragraph_no=None, clause_no=None, subclause_code=None,
                depth=1,
                part_text=main_clean,
                has_proviso=True,
                amended_dates=dates,
                has_reference=has_reference(main_clean),
                part_code=base_code + '.0',
                parent_id=None,
            )

            proviso_clean, proviso_dates = extract_meta(proviso_main_raw)
            proviso_id = add_part(parts, sort_ref,
                article_id=article_id,
                part_type='proviso',
                paragraph_no=None, clause_no=None, subclause_code=None,
                depth=1,
                part_text=proviso_clean,
                has_proviso=False,
                amended_dates=proviso_dates,
                has_reference=has_reference(proviso_clean),
                part_code=base_code + '.0.D',
                parent_id=para_id,
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
                article_id=article_id,
                part_type='paragraph',
                paragraph_no=para_no, clause_no=None, subclause_code=None,
                depth=1,
                part_text=para_main_clean,
                has_proviso=bool(proviso_raw),
                amended_dates=para_dates,
                has_reference=has_reference(para_main_clean),
                part_code=para_part_code,
                parent_id=None,
            )

            if proviso_raw:
                proviso_clean, proviso_dates = extract_meta(proviso_raw)
                add_part(parts, sort_ref,
                    article_id=article_id,
                    part_type='proviso',
                    paragraph_no=para_no, clause_no=None, subclause_code=None,
                    depth=1,
                    part_text=proviso_clean,
                    has_proviso=False,
                    amended_dates=proviso_dates,
                    has_reference=has_reference(proviso_clean),
                    part_code=f"{para_part_code}.D",
                    parent_id=para_id,
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
                article_id=article_id,
                part_type='paragraph',
                paragraph_no=para_no, clause_no=None, subclause_code=None,
                depth=1,
                part_text=main_clean,
                has_proviso=True,
                amended_dates=para_dates,
                has_reference=has_reference(main_clean),
                part_code=para_part_code,
                parent_id=None,
            )

            proviso_clean, proviso_dates = extract_meta(proviso_main_raw)
            proviso_part_code = f"{para_part_code}.D"
            proviso_id = add_part(parts, sort_ref,
                article_id=article_id,
                part_type='proviso',
                paragraph_no=para_no, clause_no=None, subclause_code=None,
                depth=1,
                part_text=proviso_clean,
                has_proviso=False,
                amended_dates=proviso_dates,
                has_reference=has_reference(proviso_clean),
                part_code=proviso_part_code,
                parent_id=para_id,
            )

            process_clauses(parts, sort_ref, article_id, para_no,
                            proviso_part_code, proviso_id, proviso_inner, 2)

    return parts


# ============================================================
# DB 적재 (v5: parent_id 미리 채워서 INSERT 한 번만)
# ============================================================
def insert_parts(parts: List[Dict[str, Any]]) -> int:
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
    parser = argparse.ArgumentParser(description="TAI 법령 article 항·호·목·단서 분해")
    parser.add_argument("--article-id", type=str)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--law-name", type=str)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--unprocessed-only", action="store_true",
                        help="v8: 미처리 article만 RPC로 직접 fetch (페이징 누락 우회)")
    args = parser.parse_args()

    if args.reset and not args.dry_run:
        confirm = input("WARNING: law_article_part 전체 삭제. 계속? [y/N] ")
        if confirm.lower() != 'y':
            print("[INFO] 취소"); return
        supabase.from_('law_article_part').delete().neq(
            'id', '00000000-0000-0000-0000-000000000000'
        ).execute()
        print("[INFO] 삭제 완료")

    # v8: 미처리만 RPC fetch
    if args.unprocessed_only:
        print("[INFO] --unprocessed-only: RPC로 미처리 article 직접 fetch")
        articles = fetch_unprocessed_via_rpc()
        print(f"[INFO] 미처리 article: {len(articles)}")
        if args.limit:
            articles = articles[:args.limit]
            print(f"[INFO] limit 적용: {len(articles)}")
        # skip-existing 자동 활성화 (RPC가 이미 미처리만 가져옴)
        existing_ids = set()
    elif args.article_id:
        articles = with_retry(lambda: supabase.from_('v_law_article_code').select(
            'article_id,article_code,law_name,article_type'
        ).eq('article_id', args.article_id).execute().data)
        existing_ids = set()
    else:
        # v7: article_type='조문' filter 추가 (view에 부칙·별표 등 12,000+ 비조문 article 포함)
        filters = {'article_type': '조문'}
        if args.law_name:
            filters['law_name'] = args.law_name
        articles = fetch_all_paged(
            'v_law_article_code',
            'article_id,article_code,law_name,article_type',
            filters=filters,
            hard_limit=args.limit,
        )

        # v7: distinct 보장 (fetch_all_paged retry 시 중복 가능성)
        seen_ids = set()
        unique_articles = []
        for a in articles:
            aid = a.get('article_id')
            if aid and aid not in seen_ids:
                seen_ids.add(aid)
                unique_articles.append(a)
        if len(unique_articles) != len(articles):
            print(f"[INFO] 중복 제거: {len(articles)} → {len(unique_articles)}")
        articles = unique_articles

        # KEC 등 별도 parser 사용 법령 제외
        excluded_count = sum(1 for a in articles if a.get('law_name') in EXCLUDED_LAW_NAMES)
        if excluded_count > 0:
            articles = [a for a in articles if a.get('law_name') not in EXCLUDED_LAW_NAMES]
            print(f"[INFO] 별도 parser 사용 법령 제외: {excluded_count} articles ({', '.join(EXCLUDED_LAW_NAMES)})")

        existing_ids = set()
        if args.skip_existing and not args.dry_run:
            existing_rows = fetch_all_paged('law_article_part', 'article_id')
            existing_ids = {r['article_id'] for r in existing_rows}
            print(f"[INFO] 기존 적재된: {len(existing_ids)}")

    print(f"[INFO] 파싱 대상: {len(articles)} articles")

    total_parts = 0
    skipped = 0
    errors = []

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

        if not art_data:
            continue
        if art_data[0].get('article_type') != '조문':
            continue

        article_text = art_data[0].get('article_text', '')
        if not article_text or len(article_text) < 10:
            continue

        try:
            parts = parse_article(article_text, article_id, article_code)
            if not parts:
                continue
            total_parts += len(parts)

            if args.dry_run:
                if i < 3:
                    print(f"\n=== {article_code} ({len(parts)} parts) ===")
                    for p in parts[:20]:
                        is_proviso = p['part_type'] == 'proviso'
                        indent = "  " * p['depth'] + ("  " if is_proviso else "")
                        flags = []
                        if is_proviso:
                            flags.append("PROVISO")
                        if p['has_proviso']:
                            flags.append("has_proviso")
                        if p['has_reference']:
                            flags.append("ref")
                        if p.get('amended_dates'):
                            flags.append(f"amended={p['amended_dates']}")
                        flag_str = f" [{','.join(flags)}]" if flags else ""
                        text_preview = p['part_text'][:80].replace('\n', ' ')
                        print(f"{indent}{p['part_code']}{flag_str}: {text_preview}...")
            else:
                insert_parts(parts)
                if (i + 1) % 50 == 0:
                    print(f"[PROGRESS] {i + 1}/{len(articles)} done, parts={total_parts}, errors={len(errors)}")
        except Exception as e:
            errors.append((article_code, str(e)))
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
