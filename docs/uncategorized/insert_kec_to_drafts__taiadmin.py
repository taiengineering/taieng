#!/usr/bin/env python3
"""insert_kec_to_drafts.py — KEC verified CSV → law_rule_drafts INSERT.

S12 (가) 의도: 원본 데이터 보존만 우선.
정규화 컬럼은 NULL로 둠 (다음 트랙: 자동 정규화 알고리즘 결정 후 채움).

특징:
- 기존 KEC drafts 있으면 confirm 후 추가 INSERT
- 575건 모두 적재 (570 PENDING + 5 NEEDS_REVIEW)
- ai_flags(jsonb)에 메타 통째 (kec_master_id, page_no, applicable_to, frequency, source_api 등)
- batch INSERT 100건씩

실행:
  cd ~/dev/tai-poc-kec && source venv/bin/activate
  python3 insert_kec_to_drafts.py --dry-run    # 먼저 미리보기
  python3 insert_kec_to_drafts.py              # 본 실행 (확인 prompt)
"""
import argparse
import csv
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ["SUPABASE_KEY"]
)

CSV_PATH = Path("./tmp_extracts/64209405-1a40-4f0a-aa8a-6f3e55917001_verified_v2_10.csv")
KEC_MASTER_ID = "64209405-1a40-4f0a-aa8a-6f3e55917001"
KEC_VERSION_ID = "4f7e2d39-6d86-4572-a776-aad6d358dfb1"
KEC_ARTICLE_ID = "e54a0408-cfb5-4276-91cd-0614a841efd6"
KEC_LAW_NAME = "한국전기설비규정"
SOURCE_API = "gemini_pro_poc_v2_10"
BATCH_SIZE = 100


def csv_to_draft_row(r):
    is_verified = str(r.get('verified', '')).lower() in ('true', '1')

    try:
        page_no = int(r.get('page_no', 0) or 0)
    except (ValueError, TypeError):
        page_no = 0

    ai_flags = {
        "kec_master_id": KEC_MASTER_ID,
        "kec_version_id": KEC_VERSION_ID,
        "page_no": page_no,
        "applicable_to": r.get('applicable_to', '') or None,
        "frequency": r.get('frequency', '') or None,
        "verified": is_verified,
        "verification_note": r.get('verification_note', '') or None,
        "source_api": SOURCE_API,
        "v2_path": "v2.6_cache→v2.7_strip→v2.8_prefix→v2.9_multi→v2.10_b1",
    }
    ai_flags = {k: v for k, v in ai_flags.items() if v is not None and v != ""}

    return {
        "law_name": KEC_LAW_NAME,
        "law_article": (r.get('law_article') or '').strip() or None,
        "article_id": KEC_ARTICLE_ID,
        "article_text": r.get('obligation_detail', '') or None,
        "obligation_summary": r.get('obligation_summary', '') or None,
        "penalty_summary": r.get('penalty_summary', '') or None,
        "ai_confidence": 95 if is_verified else 60,
        "ai_reasoning": r.get('verification_note', '') or None,
        "ai_flags": ai_flags,
        "status": "PENDING" if is_verified else "NEEDS_REVIEW",
        "review_reason": (None if is_verified else (r.get('verification_note', '') or None)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="실행 안 함, 미리보기만")
    parser.add_argument("--force", action="store_true", help="기존 데이터 있어도 진행")
    args = parser.parse_args()

    if not CSV_PATH.exists():
        print(f"CSV 없음: {CSV_PATH}")
        return 1

    print(f"CSV 읽기: {CSV_PATH}")
    with open(CSV_PATH, encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    print(f"  rows: {len(rows)}건")

    drafts = [csv_to_draft_row(r) for r in rows]
    pass_n = sum(1 for d in drafts if d["status"] == "PENDING")
    fail_n = sum(1 for d in drafts if d["status"] == "NEEDS_REVIEW")
    print(f"  변환 결과: PENDING={pass_n}, NEEDS_REVIEW={fail_n}")

    if args.dry_run:
        print("\n=== DRY-RUN: 첫 2건 미리보기 ===")
        for i, d in enumerate(drafts[:2]):
            print(f"\n[#{i+1}]")
            for k, v in d.items():
                if k == "ai_flags":
                    print(f"  {k}: {json.dumps(v, ensure_ascii=False)}")
                elif isinstance(v, str) and len(v) > 80:
                    print(f"  {k}: {v[:80]}...")
                else:
                    print(f"  {k}: {v}")
        print(f"\n=== DRY-RUN: NEEDS_REVIEW 첫 1건 ===")
        nr = [d for d in drafts if d["status"] == "NEEDS_REVIEW"]
        if nr:
            for k, v in nr[0].items():
                if k == "ai_flags":
                    print(f"  {k}: {json.dumps(v, ensure_ascii=False)}")
                elif isinstance(v, str) and len(v) > 80:
                    print(f"  {k}: {v[:80]}...")
                else:
                    print(f"  {k}: {v}")
        print("\n실제 INSERT는 --dry-run 없이 다시 실행.")
        return 0

    sb = create_client(SUPABASE_URL, SUPABASE_KEY)

    print(f"\n기존 KEC drafts 확인...")
    existing = sb.from_("law_rule_drafts").select("id", count="exact").eq("law_name", KEC_LAW_NAME).execute()
    if existing.count and existing.count > 0:
        print(f"  기존 KEC drafts: {existing.count}건 존재")
        if not args.force:
            ans = input("  계속 진행 (기존에 추가 INSERT)? [y/N]: ").strip().lower()
            if ans != 'y':
                print("중단.")
                return 0
    else:
        print(f"  기존 KEC drafts: 0건")

    print(f"\nINSERT 시작 (batch={BATCH_SIZE})...")
    inserted = 0
    for i in range(0, len(drafts), BATCH_SIZE):
        chunk = drafts[i:i+BATCH_SIZE]
        try:
            r = sb.from_("law_rule_drafts").insert(chunk).execute()
            inserted += len(chunk)
            print(f"  Batch {i//BATCH_SIZE + 1}: {len(chunk)}건 INSERT (누적 {inserted}/{len(drafts)})")
        except Exception as e:
            print(f"  Batch {i//BATCH_SIZE + 1} 실패: {str(e)[:200]}")
            print(f"  실패 batch 첫 row: {json.dumps(chunk[0], ensure_ascii=False)[:300]}")
            return 1

    print(f"\nINSERT 완료: {inserted}건")

    after = sb.from_("law_rule_drafts").select("id", count="exact").eq("law_name", KEC_LAW_NAME).execute()
    print(f"  현재 KEC drafts 총: {after.count}건")

    pending = sb.from_("law_rule_drafts").select("id", count="exact").eq("law_name", KEC_LAW_NAME).eq("status", "PENDING").execute()
    review = sb.from_("law_rule_drafts").select("id", count="exact").eq("law_name", KEC_LAW_NAME).eq("status", "NEEDS_REVIEW").execute()
    print(f"  - PENDING: {pending.count}건")
    print(f"  - NEEDS_REVIEW: {review.count}건")
    return 0


if __name__ == "__main__":
    sys.exit(main())
