#!/usr/bin/env python3
"""
KEC (한국전기설비규정) 텍스트 → law_article 테이블 INSERT.

KEC는 기후에너지환경부 공고로, law.go.kr 일반 법령 API로 본문 수집 불가.
HWP에서 추출한 텍스트 파일을 leaf 단위 article로 분해하여 INSERT.

Usage:
    # dry-run (분해만, INSERT 안 함)
    railway run python3 docs/extraction/scripts/import_kec_articles.py \
        --input ~/Downloads/kec_full_text.txt --dry-run

    # 실제 INSERT (기존 placeholder 보존)
    railway run python3 docs/extraction/scripts/import_kec_articles.py \
        --input ~/Downloads/kec_full_text.txt

    # 기존 KEC article 모두 DELETE 후 새로 INSERT
    railway run python3 docs/extraction/scripts/import_kec_articles.py \
        --input ~/Downloads/kec_full_text.txt --reset

분해 단위 (leaf):
    - 5자리 (예: 142.1.1) — 자식 없는 가장 세분 단위
    - 4자리 (예: 113.2) — 5자리 자식 없는 4자리만
    - 3자리 (예: 112) — 4자리 자식 없는 3자리만 (예: "112 용어 정의")

작성: 2026-05-05
v2 (2026-05-05): law_version_id NOT NULL 처리 — 자동 fetch
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

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


# ============================================================
# KEC 상수
# ============================================================
KEC_LAW_ID = '64209405-1a40-4f0a-aa8a-6f3e55917001'  # law_master.id
BODY_START_LINE = 1105  # 1-indexed, "111 통칙" 시작 line

HEADER_RE = re.compile(r'^(\d{3}(?:\.\d+){0,2})\s+(\S.*)$')
GROUP_RE = re.compile(r'^\(\d+\s+.*\)$')


# ============================================================
# retry
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


# ============================================================
# KEC 분해
# ============================================================
def parse_kec(text: str) -> List[Dict[str, Any]]:
    """KEC 텍스트 → leaf article list."""
    body_lines = text.split('\n')[BODY_START_LINE - 1:]

    # Pass 1: 모든 header 위치 + level 수집
    headers = []
    for i, line in enumerate(body_lines):
        line_strip = line.strip()
        if not line_strip:
            continue
        if GROUP_RE.match(line_strip):
            continue  # 그룹 헤더 skip — (110 일반사항)
        m = HEADER_RE.match(line_strip)
        if m:
            number = m.group(1)
            level = number.count('.') + 3  # 3자리 → level 3
            headers.append({
                'line_idx': i,
                'number': number,
                'title': m.group(2).strip(),
                'level': level,
            })

    # Pass 2: leaf 식별
    # leaf = 다음 header가 "내 번호로 시작 + 더 깊은 level" 이 아니면 leaf
    for j, h in enumerate(headers):
        h['is_leaf'] = True
        for k in range(j + 1, len(headers)):
            next_h = headers[k]
            if next_h['level'] <= h['level']:
                break  # 동급 이상 등장 — 더 이상 자식 없음
            if next_h['number'].startswith(h['number'] + '.') and next_h['level'] > h['level']:
                h['is_leaf'] = False
                break

    # Pass 3: leaf article 추출
    articles = []
    for j, h in enumerate(headers):
        if not h['is_leaf']:
            continue
        end_idx = headers[j + 1]['line_idx'] if j + 1 < len(headers) else len(body_lines)
        article_text = '\n'.join(body_lines[h['line_idx']:end_idx]).strip()
        if len(article_text) < 5:
            continue
        articles.append({
            'number': h['number'],
            'title': h['title'],
            'level': h['level'],
            'text': article_text,
        })
    return articles


def kec_number_to_sort(num: str) -> int:
    """113.2.1 → 113002001, 113.2 → 113002000, 113 → 113000000"""
    parts = num.split('.')
    while len(parts) < 3:
        parts.append('0')
    return int(parts[0]) * 1_000_000 + int(parts[1]) * 1_000 + int(parts[2])


# ============================================================
# DB
# ============================================================
def get_kec_law_version_id() -> str:
    """KEC의 최신 law_version_id 가져오기 (NOT NULL 컬럼)."""
    def _fetch():
        return supabase.from_('law_version').select('id,announcement_date').eq(
            'law_id', KEC_LAW_ID
        ).order('announcement_date', desc=True).limit(1).execute().data

    rows = with_retry(_fetch) or []
    if not rows:
        raise RuntimeError(f'KEC law_version 없음 (law_id={KEC_LAW_ID})')
    return rows[0]['id']


def insert_chunked(rows: List[Dict[str, Any]], chunk_size: int = 100) -> int:
    """chunked INSERT with retry."""
    inserted = 0
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i:i + chunk_size]

        def _insert():
            return supabase.from_('law_article').insert(chunk).execute().data

        result = with_retry(_insert)
        inserted += len(result) if result else 0
        if (i // chunk_size + 1) % 5 == 0:
            print(f"  [PROGRESS] {inserted}/{len(rows)}")
    return inserted


def get_existing_kec_articles() -> List[Dict[str, Any]]:
    def _fetch():
        return supabase.from_('law_article').select(
            'id,article_no,article_sub_no,article_title'
        ).eq('law_id', KEC_LAW_ID).execute().data

    return with_retry(_fetch) or []


def delete_kec_articles():
    def _delete():
        return supabase.from_('law_article').delete().eq(
            'law_id', KEC_LAW_ID
        ).execute().data

    return with_retry(_delete) or []


# ============================================================
# 메인
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="KEC 텍스트 → law_article INSERT (leaf 단위 분해)"
    )
    parser.add_argument("--input", required=True, help="KEC 텍스트 파일 path")
    parser.add_argument("--dry-run", action="store_true",
                        help="분해만 하고 INSERT 안 함")
    parser.add_argument("--reset", action="store_true",
                        help="기존 KEC article 모두 DELETE 후 INSERT")
    parser.add_argument("--chunk-size", type=int, default=100)
    args = parser.parse_args()

    # 1. 파일 읽기
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"[ERROR] 파일 없음: {input_path}", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text(encoding='utf-8')
    print(f"[INFO] 입력: {input_path}")
    print(f"[INFO] 길이: {len(text):,} 자")

    # 2. KEC 분해
    articles = parse_kec(text)
    print(f"[INFO] leaf article: {len(articles)}")
    by_level = {}
    for a in articles:
        by_level[a['level']] = by_level.get(a['level'], 0) + 1
    print(f"[INFO] level 분포: {dict(sorted(by_level.items()))}")
    total_text = sum(len(a['text']) for a in articles)
    print(f"[INFO] 총 본문: {total_text:,}자, 평균: {total_text // len(articles)}자")

    # 3. dry-run sample 출력
    if args.dry_run:
        print("\n[DRY-RUN] sample 처음 3개:")
        for a in articles[:3]:
            print(f"  [{a['number']}] L{a['level']} {a['title']} ({len(a['text'])}자)")
            print(f"    text: {a['text'][:100]}...")
        print("\n[DRY-RUN] sample 마지막 3개:")
        for a in articles[-3:]:
            print(f"  [{a['number']}] L{a['level']} {a['title']} ({len(a['text'])}자)")
        print("\n[DRY-RUN] INSERT 안 함")
        return

    # 4. law_version_id fetch (NOT NULL)
    law_version_id = get_kec_law_version_id()
    print(f"\n[INFO] law_version_id: {law_version_id}")

    # 5. 기존 KEC article 체크
    existing = get_existing_kec_articles()
    if existing:
        print(f"\n[WARN] 기존 KEC article {len(existing)} row 있음:")
        for e in existing[:5]:
            print(f"  - article_no={e['article_no']} title={e.get('article_title', '')[:50]}")
        if not args.reset:
            print("\n[INFO] 기존 row 보존 + 새로 INSERT 진행 (--reset 옵션 없음)")
        else:
            confirm = input(f"\n--reset: 기존 {len(existing)} row 삭제 후 INSERT. 계속? [y/N] ")
            if confirm.lower() != 'y':
                print("[INFO] 취소")
                return
            print("[INFO] 기존 KEC article 삭제 중...")
            delete_kec_articles()
            print(f"[INFO] {len(existing)} row 삭제 완료")

    # 6. INSERT 데이터 준비
    rows = []
    for a in articles:
        num = a['number']
        article_no = int(num.split('.')[0])  # 첫 3자리 (예: 113)
        article_sub_no = kec_number_to_sort(num)  # 정렬 키
        title_full = f"[KEC {num}] {a['title']}"
        rows.append({
            'law_id': KEC_LAW_ID,
            'law_version_id': law_version_id,  # NOT NULL
            'article_no': article_no,
            'article_sub_no': article_sub_no,
            'article_title': title_full,
            'article_text': a['text'],
            'article_type': '조문',
        })

    # 7. INSERT
    print(f"\n[INFO] {len(rows)} articles INSERT 시작 (chunk_size={args.chunk_size})")
    inserted = insert_chunked(rows, args.chunk_size)
    print(f"\n[DONE] {inserted}/{len(rows)} articles INSERT 완료")

    # 8. 검증
    final = get_existing_kec_articles()
    print(f"[VERIFY] 최종 KEC article 수: {len(final)}")


if __name__ == "__main__":
    main()
