#!/usr/bin/env python3
"""KEC PoC cache 정밀 분석 (S12 진입 전 진단).

목적:
  - chunk 5개 + verify_batch 26개의 정확한 상태 측정
  - 누락 batch 번호 식별
  - chunk ↔ verify 정렬 일관성 검증
  - 다음 단계 (재실행 vs INSERT) 결정에 필요한 정량 데이터 산출

실행:
  cd ~/dev/tai-poc-kec
  python3 analyze_cache.py
"""
import glob
import json
import os
import re
import sys

TMP = os.path.expanduser('~/dev/tai-poc-kec/tmp_extracts')
BATCH_SIZE = 15  # PoC v2.6 SONNET_BATCH_SIZE

if not os.path.isdir(TMP):
    print(f"❌ 디렉토리 없음: {TMP}")
    sys.exit(1)

print("=" * 70)
print("KEC PoC Cache 정밀 진단 (S12 진입 전)")
print("=" * 70)

# ─────────────────────────────────────────────────────────────────
# [1] Gemini chunks (Step 4 산출물)
# ─────────────────────────────────────────────────────────────────
print("\n[1] Gemini chunks (Step 4 — 의무 추출)")
chunk_files = sorted(
    glob.glob(f'{TMP}/chunk_*_obligations.json'),
    key=lambda x: int(re.search(r'chunk_(\d+)', x).group(1))
)
chunk_total = 0
chunk_data = {}
all_obligations = []  # chunk 1..5 합친 순서대로
for f in chunk_files:
    num = int(re.search(r'chunk_(\d+)', f).group(1))
    try:
        d = json.load(open(f, encoding='utf-8'))
        if not isinstance(d, list):
            print(f"  chunk_{num}: ⚠️ list 아님 (type={type(d).__name__})")
            continue
        n = len(d)
        chunk_total += n
        chunk_data[num] = d
        all_obligations.extend(d)
        keys = list(d[0].keys()) if d and isinstance(d[0], dict) else []
        size_kb = os.path.getsize(f) / 1024
        print(f"  chunk_{num}: {n:>4}건  ({size_kb:>6.1f} KB)  keys={keys[:4]}...")
    except Exception as e:
        print(f"  chunk_{num}: ❌ {e}")
print(f"  ── chunk total: {chunk_total}건 의무")

# ─────────────────────────────────────────────────────────────────
# [2] Sonnet verify batches (Step 5 산출물)
# ─────────────────────────────────────────────────────────────────
print("\n[2] Sonnet verify batches (Step 5 — 검증)")
verify_files = sorted(
    glob.glob(f'{TMP}/verify_batch_*.json'),
    key=lambda x: int(re.search(r'verify_batch_(\d+)', x).group(1))
)
batch_total = 0
batch_pass = 0
batch_fail = 0
batch_present = []
batch_data = {}
batch_summary = []
for f in verify_files:
    num = int(re.search(r'verify_batch_(\d+)', f).group(1))
    batch_present.append(num)
    try:
        d = json.load(open(f, encoding='utf-8'))
        if not isinstance(d, list):
            batch_summary.append((num, '?', '?', '?', f'list 아님: {type(d).__name__}'))
            continue
        n = len(d)
        p = sum(1 for x in d if isinstance(x, dict) and x.get('verified') is True)
        u = sum(1 for x in d if isinstance(x, dict) and x.get('verified') is False)
        batch_total += n
        batch_pass += p
        batch_fail += u
        batch_data[num] = d
        pct = f"{p/n*100:.0f}%" if n else "0%"
        batch_summary.append((num, n, p, u, pct))
    except Exception as e:
        batch_summary.append((num, '?', '?', '?', f'ERROR: {e}'))

# 표 출력
print(f"  {'batch':>5} {'건수':>5} {'pass':>5} {'fail':>5} {'pass%':>6}")
for num, n, p, u, pct in batch_summary:
    print(f"  {num:>5} {n:>5} {p:>5} {u:>5} {pct:>6}")
print(f"  ── batch total: {batch_total}건, pass={batch_pass}, fail={batch_fail}")

# ─────────────────────────────────────────────────────────────────
# [3] 누락 batch 식별
# ─────────────────────────────────────────────────────────────────
print("\n[3] 누락 batch 식별 (broken JSON으로 캐시 안 된 것)")
expected_batch_count = (chunk_total + BATCH_SIZE - 1) // BATCH_SIZE
expected_set = set(range(1, expected_batch_count + 1))
missing = sorted(expected_set - set(batch_present))
print(f"  예상 batch 수: ⌈{chunk_total} / {BATCH_SIZE}⌉ = {expected_batch_count}")
print(f"  보유 batch: {len(batch_present)}개")
print(f"  누락 batch 번호 ({len(missing)}개): {missing}")
print(f"  누락 의무 추정: ~{len(missing) * BATCH_SIZE}건")

# ─────────────────────────────────────────────────────────────────
# [4] chunk ↔ verify 정렬 일관성 검증
# ─────────────────────────────────────────────────────────────────
print("\n[4] chunk ↔ verify 정렬 일관성")
# all_obligations[0:15] = batch 1, [15:30] = batch 2, ...
# 누락 안 된 batch에 대해 첫 의무 비교
checked = 0
mismatched = 0
for num in sorted(batch_data.keys())[:5]:  # 처음 5개만 빠르게 체크
    expected_first = all_obligations[(num - 1) * BATCH_SIZE]
    actual_first = batch_data[num][0] if batch_data[num] else None
    if not (isinstance(expected_first, dict) and isinstance(actual_first, dict)):
        continue
    e_summary = (expected_first.get('obligation_summary') or '')[:40]
    a_summary = (actual_first.get('obligation_summary') or '')[:40]
    e_article = expected_first.get('law_article', '')
    a_article = actual_first.get('law_article', '')
    match = e_summary == a_summary and e_article == a_article
    checked += 1
    if not match:
        mismatched += 1
    flag = '✅' if match else '❌'
    print(f"  batch {num:>2}: {flag}  chunk={e_article}/{e_summary}")
    if not match:
        print(f"           batch={a_article}/{a_summary}")
print(f"  체크: {checked}개, 일치: {checked - mismatched}, 불일치: {mismatched}")
if mismatched == 0:
    print("  ✅ chunk와 verify cache 정렬 일관성 OK — 재실행 시 cache 재활용 가능")
else:
    print("  ⚠️ 정렬 불일치 발생 — chunk가 verify 이후 변경됐을 가능성, 재추출 필요")

# ─────────────────────────────────────────────────────────────────
# [5] CSV 산출물 (Step 6)
# ─────────────────────────────────────────────────────────────────
print("\n[5] CSV 산출물 (Step 6)")
csv_files = glob.glob(f'{TMP}/*.csv')
for f in csv_files:
    try:
        with open(f, encoding='utf-8-sig') as fp:
            n = sum(1 for _ in fp) - 1
        size_kb = os.path.getsize(f) / 1024
        print(f"  {os.path.basename(f)}: {n}행, {size_kb:.1f} KB")
    except Exception as e:
        print(f"  {os.path.basename(f)}: ❌ {e}")
if not csv_files:
    print("  CSV 없음")

# ─────────────────────────────────────────────────────────────────
# [6] 의무 데이터 sample (첫 1건)
# ─────────────────────────────────────────────────────────────────
print("\n[6] 의무 데이터 구조 sample (chunk_1[0])")
if 1 in chunk_data and chunk_data[1]:
    sample = chunk_data[1][0]
    if isinstance(sample, dict):
        for k, v in sample.items():
            v_str = str(v) if v is not None else 'None'
            v_str = v_str if len(v_str) <= 80 else v_str[:80] + '...'
            print(f"  {k:>22}: {v_str}")

# ─────────────────────────────────────────────────────────────────
# 요약
# ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("진단 요약")
print("=" * 70)
print(f"  Step 4 Gemini 추출:  {chunk_total}건 (chunk {len(chunk_data)}/5)")
print(f"  Step 5 Sonnet 검증:  {batch_total}건 / {chunk_total}건 ({batch_total/chunk_total*100:.1f}%)")
print(f"                       └ pass={batch_pass}, fail={batch_fail}")
print(f"  Step 5 미완:        {len(missing)} batch (~{len(missing) * BATCH_SIZE}건)")
print(f"                       └ 누락 batch: {missing}")
print(f"  Step 7 DB INSERT:    0건 (PoC schema 미스매치로 미실행)")
print(f"  Cache 일관성:       {'OK' if mismatched == 0 else 'NG'}")
print("=" * 70)
print()
print("다음 단계 후보:")
print(f"  A. 누락 {len(missing)} batch만 v2.6 코드로 재실행 (~${len(missing) * 0.6:.1f}, ~30분)")
print(f"  B. 정식 코드 작성 후 575건 INSERT — 운영 schema 결정 선행")
print(f"  C. CSV로 사람 검토 후 일괄 INSERT")
