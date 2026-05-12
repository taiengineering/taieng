#!/usr/bin/env python3
"""diagnose_fails_v2_7.py — fail 78건이 진짜 환각인지 false negative인지 판별.

S12: v2.7 검증 후 fail 78건이 모두 "본문 근거 없음" 사유로 reject됨.
진단 목적: 점번호가 PDF에 실제 존재하는지 grep해서 false negative 비율 측정.

판단 기준:
- PDF에 실제 존재 70%+ → false negative (ctx 부족 문제, ctx 확장 후 재검증)
- PDF에 진짜 없음 50%+ → Gemini 환각 (fail 유지하고 본 작업 진행)
- PDF에 존재 + page_no 정확 90%+ → system prompt 과엄격 (조정 후 재검증)

실행:
  cd ~/dev/tai-poc-kec
  source venv/bin/activate
  python3 diagnose_fails_v2_7.py
"""
import csv
import pdfplumber

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

print(f"\nLoading fails from CSV...")
with open(CSV, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))
fails = [r for r in rows if r.get('verified', '').lower() == 'false']
print(f"Total fails: {len(fails)}")

exists_in_pdf = 0
not_found = 0
page_correct = 0
page_wrong = 0
samples_not_found = []
samples_page_wrong = []

for r in fails:
    art = (r.get('law_article') or '').strip()
    gemini_page = int(r.get('page_no', 0) or 0)
    if not art:
        not_found += 1
        continue
    found_pages = [pg for pg, t in pages_text if art in t]
    if not found_pages:
        not_found += 1
        if len(samples_not_found) < 5:
            samples_not_found.append((art, gemini_page, r.get('obligation_summary', '')[:50]))
        continue
    exists_in_pdf += 1
    if gemini_page in found_pages:
        page_correct += 1
    else:
        page_wrong += 1
        if len(samples_page_wrong) < 8:
            samples_page_wrong.append((art, gemini_page, found_pages[:3], r.get('obligation_summary', '')[:50]))

total = len(fails)
print(f"\n=== fail {total}건의 점번호가 KEC PDF에 실제 존재하는가 ===")
print(f"  PDF에 존재:        {exists_in_pdf}/{total} ({exists_in_pdf/total*100:.0f}%)")
print(f"  PDF에 진짜 없음:   {not_found}/{total} ({not_found/total*100:.0f}%)")
print(f"\n=== Gemini page_no 정확도 (존재하는 {exists_in_pdf}건 중) ===")
print(f"  정확:              {page_correct}/{exists_in_pdf}")
print(f"  page_no 틀림:      {page_wrong}/{exists_in_pdf}")

if samples_not_found:
    print(f"\n=== 진짜 본문에 없는 sample (최대 5건) ===")
    for art, p, summ in samples_not_found:
        print(f"  [{art}] (Gemini said p{p}) {summ}")

if samples_page_wrong:
    print(f"\n=== 본문에는 있지만 page_no 틀린 sample (최대 8건) ===")
    for art, gp, real_pages, summ in samples_page_wrong:
        print(f"  [{art}] Gemini said p{gp}, 실제 p{real_pages}")
        print(f"      {summ}")
