#!/usr/bin/env python3
"""
KEC (한국전기설비규정) 전용 parser.

일반 법령과 다른 마커 형식:
- 일반 법령: [①][1.][가.] (자동 부착 마커)
- KEC: 1., 가., (1) (마커 없음, 본문에 직접 표기)

KEC 본문 구조 예시:
    113.2 감전에 대한 보호      ← article header (이미 article로 분리)
    1. 기본보호                  ← 호 (clause)
    기본보호는 일반적으로...
    가. 인축의 몸을 통해...      ← 목 (subclause)
    나. 인축의 몸에 흐르는...
    
    2. 고장보호                  ← 다음 호
    다만, ...                    ← 단서 (proviso)
    가. 노출도전부에...
    (1) 인축의 몸을 통해...      ← 괄호 (본문에 그대로, 별도 분리 안 함)
    (2) 인축의 몸에 흐르는...

분리 단위:
- paragraph (depth 1): article header line + 도입부 (호 등장 전 본문)
- clause (depth 2): 1., 2., ...
- subclause (depth 3): 가., 나., ...
- 괄호 (1)(2)는 본문에 그대로 (별도 분리 안 함)
- proviso: "다만, ..."

part_code 형식:
- paragraph: ELC.O.001.113.2.0
- clause 1: ELC.O.001.113.2.0.1
- subclause 가 (clause 1 자식): ELC.O.001.113.2.0.1.가
- proviso (clause 1 단서): ELC.O.001.113.2.0.1.D

Usage:
    # dry-run
    railway run python3 docs/extraction/scripts/parse_kec_parts.py --dry-run
    
    # 실제 INSERT
    railway run python3 docs/extraction/scripts/parse_kec_parts.py --skip-existing
    
    # 기존 KEC parts 삭제 + 재처리
    railway run python3 docs/extraction/scripts/parse_kec_parts.py --reset

작성: 2026-05-05
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


KEC_LAW_ID = '64209405-1a40-4f0a-aa8a-6f3e55917001'


# ============================================================
# 정규식
# ============================================================
# article_title에서 KEC 번호 추출 (예: "[KEC 113.2.1] 기본보호" → "113.2.1")
KEC_NUMBER_PATTERN = re.compile(r'\[KEC ([\d.]+)\]')

# 호 (clause): "^N. ..." (line 시작, 숫자 + 점)
CLAUSE_PATTERN = re.compile(r'^(\d+)\.\s', re.MULTILINE)

# 목 (subclause): "^가. ..." (line 시작, 한글 한 글자 + 점)
SUBCLAUSE_PATTERN = re.compile(r'^([가-힣])\.\s', re.MULTILINE)

# 단서: "다만, ..."
PROVISO_PATTERN = re.compile(r'(?:^|\.|\s)\s*(다만,\s*)')

# 인용 (참조): KEC 번호 인용 + 일반 법령 인용
REFERENCE_PATTERN = re.compile(
    r'\b\d{3}(?:\.\d+){1,3}\b'  # KEC 번호 인용 (예: "232.4.1")
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
# 헬퍼
# ============================================================
def has_reference(text: str) -> bool:
    return bool(REFERENCE_PATTERN.search(text))


def split_main_and_proviso(text: str) -> Tuple[str, Optional[str]]:
    """단서 분리. "다만, ..." 부분을 별도로 추출."""
    m = PROVISO_PATTERN.search(text)
    if not m:
        return text.strip(), None
    main = text[:m.start(1)].rstrip().rstrip('.').strip()
    if main and not main.endswith('.'):
        main += '.'
    proviso = text[m.start(1):].strip()
    return main, proviso


def add_part(parts: List[Dict[str, Any]], sort_ref: List[int], **fields) -> str:
    """part dict 추가. uuid 미리 생성."""
    sort_ref[0] += 1
    fields['id'] = str(uuid.uuid4())
    fields['sort_order'] = sort_ref[0]
    parts.append(fields)
    return fields['id']


# ============================================================
# 핵심 분해
# ============================================================
def parse_kec_article(article_text: str, article_id: str, base_code: str) -> List[Dict[str, Any]]:
    """KEC article 본문을 paragraph/clause/subclause/proviso로 분해."""
    parts: List[Dict[str, Any]] = []
    sort_ref = [0]

    text = article_text.strip()
    if not text:
        return parts

    # 1. article header line 분리 (예: "113.2 감전에 대한 보호")
    lines = text.split('\n')
    header_line = lines[0].strip() if lines else ''
    body_text = '\n'.join(lines[1:]) if len(lines) > 1 else ''

    # 2. 호 (clause) 위치 찾기
    clause_matches = list(CLAUSE_PATTERN.finditer(body_text))

    # paragraph 본문 = header + 호 등장 전 텍스트
    if clause_matches:
        intro_text = body_text[:clause_matches[0].start()].strip()
    else:
        intro_text = body_text.strip()

    paragraph_text = header_line
    if intro_text:
        paragraph_text += '\n' + intro_text
    paragraph_text = paragraph_text.strip()

    # 3. paragraph INSERT
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

    # 4. 호 (clause) 분리
    if clause_matches:
        for i, m in enumerate(clause_matches):
            clause_no = int(m.group(1))
            start = m.end()
            end = clause_matches[i + 1].start() if i + 1 < len(clause_matches) else len(body_text)
            clause_text = body_text[start:end].strip()

            cls_main, cls_proviso = split_main_and_proviso(clause_text)

            # 목 위치 찾기
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

            # 5. 목 (subclause) 분리
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


def delete_kec_parts(kec_article_ids: List[str]):
    """KEC parts 일괄 삭제. 100개씩 나눠 삭제."""
    deleted = 0
    for i in range(0, len(kec_article_ids), 100):
        chunk = kec_article_ids[i:i + 100]

        def _delete():
            return supabase.from_('law_article_part').delete().in_(
                'article_id', chunk
            ).execute().data

        res = with_retry(_delete)
        deleted += len(res) if res else 0
    return deleted


# ============================================================
# 메인
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="KEC (한국전기설비규정) 전용 article 분해 — paragraph/clause/subclause/proviso"
    )
    parser.add_argument("--limit", type=int, help="처리 최대 개수")
    parser.add_argument("--dry-run", action="store_true", help="분해만, INSERT 안 함")
    parser.add_argument("--reset", action="store_true",
                        help="기존 KEC parts 삭제 후 재처리")
    parser.add_argument("--skip-existing", action="store_true",
                        help="이미 적재된 article_id skip")
    args = parser.parse_args()

    # 1. KEC article 가져오기
    articles = fetch_all_paged(
        'law_article',
        'id,article_no,article_sub_no,article_title,article_text,article_type',
        filters={'law_id': KEC_LAW_ID},
        hard_limit=args.limit,
    )
    print(f"[INFO] KEC article 가져옴: {len(articles)}")

    # placeholder (전문 등) 제외 — [KEC ...] 형식만 처리
    valid_articles = [
        a for a in articles
        if a.get('article_title')
        and a['article_title'].startswith('[KEC ')
        and a.get('article_text')
        and len(a['article_text']) > 5
    ]
    print(f"[INFO] 처리 대상 (placeholder 제외): {len(valid_articles)}")

    # 2. reset
    if args.reset and not args.dry_run:
        confirm = input(f"WARNING: KEC parts 모두 삭제 후 재처리. 계속? [y/N] ")
        if confirm.lower() != 'y':
            print("[INFO] 취소"); return
        kec_article_ids = [a['id'] for a in articles]
        deleted = delete_kec_parts(kec_article_ids)
        print(f"[INFO] 기존 KEC parts {deleted} row 삭제 완료")

    # 3. skip-existing
    existing_ids = set()
    if args.skip_existing and not args.dry_run:
        all_existing = fetch_all_paged('law_article_part', 'article_id')
        existing_ids = {r['article_id'] for r in all_existing}
        # KEC article_id만 필터
        kec_article_id_set = {a['id'] for a in articles}
        existing_ids &= kec_article_id_set
        print(f"[INFO] 기존 적재된 KEC article_id: {len(existing_ids)}")

    # 4. 분해 + INSERT
    total_parts = 0
    skipped = 0
    errors = []

    for i, art in enumerate(valid_articles):
        article_id = art['id']
        article_title = art['article_title']
        article_text = art['article_text']

        if article_id in existing_ids:
            skipped += 1
            continue

        # KEC 번호 추출
        m = KEC_NUMBER_PATTERN.search(article_title)
        if not m:
            errors.append((article_title[:30], "KEC 번호 추출 실패"))
            continue

        kec_number = m.group(1)
        base_code = f"ELC.O.001.{kec_number}"

        try:
            parts = parse_kec_article(article_text, article_id, base_code)
            if not parts:
                errors.append((kec_number, "분해 결과 0 parts"))
                continue
            total_parts += len(parts)

            if args.dry_run:
                if i < 3:
                    print(f"\n=== [{kec_number}] {article_title} ({len(parts)} parts) ===")
                    for p in parts[:25]:
                        is_proviso = p['part_type'] == 'proviso'
                        indent = "  " * p['depth'] + ("  " if is_proviso else "")
                        flags = []
                        if is_proviso:
                            flags.append("PROVISO")
                        if p['has_proviso']:
                            flags.append("has_proviso")
                        if p['has_reference']:
                            flags.append("ref")
                        flag_str = f" [{','.join(flags)}]" if flags else ""
                        text_preview = p['part_text'][:80].replace('\n', ' ')
                        print(f"{indent}{p['part_code']}{flag_str}: {text_preview}...")
            else:
                insert_parts(parts)
                if (i + 1) % 100 == 0:
                    print(f"[PROGRESS] {i + 1}/{len(valid_articles)} done, "
                          f"parts={total_parts}, errors={len(errors)}")
        except Exception as e:
            errors.append((kec_number, str(e)[:100]))
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
