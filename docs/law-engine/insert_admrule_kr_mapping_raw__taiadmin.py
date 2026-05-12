"""
admrule_kr_mapping.csv → admrule_kr_mapping_raw 테이블 INSERT
실행: railway run python3 insert_admrule_kr_mapping_raw.py
"""
import os
import csv
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 환경변수 필요")
    exit(1)

print(f"Using Supabase URL: {SUPABASE_URL}")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# CSV 위치 (현재 디렉토리 또는 absolute path)
CSV_PATH = "/Users/taiwangsim/Desktop/tai-engineering/admrule-kr/admrule_kr_mapping.csv"
BATCH_SIZE = 100

with open(CSV_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"CSV rows: {len(rows)}")

inserted_total = 0
batch_idx = 0

for i in range(0, len(rows), BATCH_SIZE):
    batch_idx += 1
    batch = rows[i:i + BATCH_SIZE]
    
    # legal_mst 검증 (13자리 숫자만)
    valid_batch = [
        {
            "directory_path": r["directory_path"],
            "directory_name": r["directory_name"],
            "filename": r["filename"],
            "fm_title": r["fm_title"],
            "rule_type": r["rule_type"],
            "ministry_name": r["ministry_name"],
            "legal_mst": r["legal_mst"],
            "issue_number": None,  # 행정규칙ID는 별도 컬럼 안 둠 (필요 시 추가)
            "source_file": r["source_file"],
        }
        for r in batch
        if r.get("legal_mst") and len(r["legal_mst"]) == 13 and r["legal_mst"].isdigit()
    ]
    
    if not valid_batch:
        print(f"Batch {batch_idx}: 0 valid rows (skip)")
        continue
    
    try:
        result = supabase.table("admrule_kr_mapping_raw").insert(valid_batch).execute()
        inserted_count = len(result.data) if result.data else 0
        inserted_total += inserted_count
        print(f"Batch {batch_idx} ({i + 1}-{i + len(batch)}): ok ({inserted_count} rows)")
    except Exception as e:
        print(f"Batch {batch_idx} ERROR: {e}")
        # 첫 실패 row만 출력
        if valid_batch:
            print(f"  First row: {valid_batch[0]}")
        break

print(f"\nInserted rows: {inserted_total}")

# COUNT 확인
count_result = supabase.table("admrule_kr_mapping_raw").select("id", count="exact").limit(1).execute()
print(f"admrule_kr_mapping_raw COUNT(*): {count_result.count}")
