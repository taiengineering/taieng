#!/usr/bin/env python3
"""diagnose_pdf_quality_v2_7.py — fail 62건 "진짜 없음"의 진짜 원인 진단.

S12 follow-up: 1차 진단에서 fail 78건 중 62건이 PDF에서 못 찾음 + page_no 16/16 부정확.
샘플들은 KEC 표준 조항(241.17 전기자동차 충전 등)이라 본문에 있을 가능성 높음.

원인 후보:
  A. pdfplumber 텍스트 추출 실패 (chunk_5=0건과 동일 현상)
  B. 점번호 표기 차이 (241.17.2.가 vs 241.17.2(가) vs 241·17·2·가)
  C. 진짜 Gemini 환각

검증:
  1. PDF 페이지별 글자 수 분포 → A 가능성
  2. fail 점번호의 prefix 검색 (3단계→2단계→1단계) → 깊이 차이 식별
  3. 점번호 표기 변형 검색 → B 가능성

실행:
  cd ~/dev/tai-poc-kec
  source venv/bin/activate
  python3 diagnose_pdf_quality_v2_7.py
"""
import csv
import pdfplumber
from collections import Counter

CSV = 'tmp_extracts/64209405-1a40-4f0a-aa8a-6f3e55917001_verified_v2_7.csv'
PDF = 'tmp_extracts/64209405-1a40-4f0a-aa8a-6f3e55917001.pdf'

print("Loading PDF text per page (1234p, ~1min)...")
pages_text = []
with pdfplumber.open(PDF) as pdf:
    for i, page in enumerate(pdf.pages, 1):
        t = page.extract_text() or ""
        pages_text.append((i, t))
        if i % 300 == 0:
            print(f"  ... {i}")

# ─────────────────────────────────────────
# A) PDF 텍스트 추출 품질
# ─────────────────────────────────────────
print("\n=== A) PDF 페이지별 텍스트 추출 품질 ===")
buckets = {'<50': [], '50~500': [], '500~1500': [], '1500~3000': [], '3000+': []}
for p, t in pages_text:
    L = len(t)
    if L < 50: buckets['<50'].append(p)
    elif L < 500: buckets['50~500'].append(p)
    elif L < 1500: buckets['500~1500'].append(p)
    elif L < 3000: buckets['1500~3000'].append(p)
    else: buckets['3000+'].append(p)

for k, v in buckets.items():
    print(f"  글자 수 {k:>10}: {len(v):>5} 페이지")

empty = buckets['<50']
print(f"\n  ★ 글자 < 50인 페이지 (추출 실패): {len(empty)}")
if empty:
    if len(empty) <= 30:
        print(f"     {empty}")
    else:
        print(f"     처음 15: {empty[:15]}")
        print(f"     마지막 15: {empty[-15:]}")

# ─────────────────────────────────────────
# B) fail 점번호 prefix 단계별 검색
# ─────────────────────────────────────────
full_text = '\n'.join(t for _, t in pages_text)

with open(CSV, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))
fails = [r for r in rows if r.get('verified', '').lower() == 'false']
print(f"\n=== B) fail {len(fails)}건 점번호 prefix 단계별 검색 ===")

depth_found = Counter()
not_found_at_all = []
for r in fails:
    art = (r.get('law_article') or '').strip()
    if not art:
        continue
    parts = art.split('.')
    found_depth = 0
    for d in range(len(parts), 0, -1):
        prefix = '.'.join(parts[:d])
        if prefix in full_text:
            found_depth = d
            break
    if found_depth == 0:
        not_found_at_all.append((art, r.get('obligation_summary', '')[:50]))
    else:
        depth_found[(len(parts), found_depth)] += 1

print(f"  (full_depth → found_depth) : 건수")
for k, v in sorted(depth_found.items()):
    full_d, found_d = k
    pct = '✅' if full_d == found_d else f'⚠️ {full_d - found_d}단계 짧게 발견'
    print(f"    {full_d}.x → {found_d}.x : {v:>3} {pct}")

print(f"\n  prefix도 전혀 없음: {len(not_found_at_all)}건")
if not_found_at_all:
    print(f"  sample (최대 8건):")
    for art, summ in not_found_at_all[:8]:
        print(f"    [{art}] {summ}")

# ─────────────────────────────────────────
# C) 점번호 표기 변형 검색
# ─────────────────────────────────────────
print(f"\n=== C) 점번호 표기 변형 시도 (fail 처음 10건) ===")
for r in fails[:10]:
    art = (r.get('law_article') or '').strip()
    if not art:
        continue
    parts = art.split('.')
    last = parts[-1]
    base = '.'.join(parts[:-1]) if len(parts) > 1 else ''
    
    variants = {
        f'{art}': art,                                     # 241.17.2.가
        f'{art}.': art + '.',                              # 241.17.2.가.
        f'중점': art.replace('.', '·'),                     # 241·17·2·가
        f'공백': ' '.join(parts),                           # 241 17 2 가
        f'괄호': f'{base}({last})' if base else art,        # 241.17.2(가)
        f'괄호공백': f'{base} ({last})' if base else art,   # 241.17.2 (가)
    }
    found = [name for name, v in variants.items() if v and v in full_text]
    print(f"  [{art}] {'✅ 변형 발견: ' + ','.join(found) if found else '❌ 어떤 변형도 없음'}")

# ─────────────────────────────────────────
# D) 결정 도구: fail 점번호의 첫 자릿수 분포 (KEC 점번호 체계 매핑)
# ─────────────────────────────────────────
print(f"\n=== D) fail 점번호 첫 1~2자리 분포 (KEC 영역 매핑) ===")
# KEC 점번호 체계:
#   1xx = 통칙
#   2xx = 저압전기설비
#     21x = 일반사항
#     22x = 안전을 위한 보호
#     23x = 전선로
#     24x = 옥내·외 배선 / 특수설비 (24x.1~17 등)
#   3xx = 고압·특고압전기설비
#   4xx = 발전용 전기설비
#   5xx = 분산형전원·재생에너지
#   6xx, 9xx 등
prefix_dist = Counter()
for r in fails:
    art = (r.get('law_article') or '').strip()
    if not art:
        continue
    head = art.split('.')[0][:3] if art else 'N/A'
    prefix_dist[head] += 1
for k, v in sorted(prefix_dist.items()):
    print(f"  {k}.xxx : {v:>3}건")

print(f"\n=== 진단 완료 ===")
