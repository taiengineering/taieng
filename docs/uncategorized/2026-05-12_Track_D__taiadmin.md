# [Track D] 2026-05-09 — Day 1 + Day 2 + Phase 1 (1·1.1·1.5·1.6) 종결 + Phase 2 진단

> **본 보고서**: Day 1 (재정의) + Day 2 sample 변환 + Phase 1 본 적용 (마이그레이션 2 + 변환 1,322건) + Phase 1.1 (PUA 보전) + Phase 1.5 (zip 압축 해제 + child INSERT + 변환) + Phase 1.6 (IMAGE_PDF 재분류) + Phase 2 진단 (가설 무효 발견). 동일 파일명 유지 (`Track_D_20260512.md`), push history 보존.
> **마스터 §2 정합**: ① LLM 0% / ② 법령 보전 / ③ 누락 0 / ④ 100% 매핑 (로스리스) / ⑤ 오염=폐기 / ⑥ 검증 부담 0 / ⑦ ground truth

---

## ⚠️ 직전 산출물 (commit `54522efb`) 폐기

직전 본 보고서는 **외부 법제처 PDF 다운로드 + kordoc 시범 변환** 내용이었으나, 잘못된 출발점에서 작성됨:
- KEC/NFTC/KDS/본칙은 v2에서 이미 `law_article`/`law_article_part`에 텍스트 통합 완료된 영역 (5/5 핸드오프 명시)
- TAI는 별표 원본 파일을 Storage `law-attachments` 버킷에 보유 (458 파일) — 외부 다운로드 불요
- 사용자 지적: "kec등 이작업은 v2에서 완료한 작업" + "원문은 조문에 가지고 있을테니 먼저 확인 바람"

본 창의 사전 점검 누락 = 사용자 지적 패턴 (임의 판단·끼워넣기) 재발. 본 commit으로 교체.

---

## Track D 작업 범위 (재정의, 사용자 OK)

### 작업 정체성
- Track ID: D (별표·서식 처리, 완전 독립 트랙)
- 기간: Week 1~3 (Day 1 진단 결과로 재조정 가능)
- 시작: 2026-05-09 Day 1

### 입력 (확정)
- `law_attachment` 460건 — Storage `law-attachments` 버킷 458 파일 보유
- 변환 텍스트 0건 / `text_extracted_at` NULL / `download_status='success'` 0건

### 처리 (확정)
- kordoc 결정적 변환 (마스터 §2 ① LLM 0%)
- 출력: Markdown + IRBlock[] + metadata

### 출력
- `law_attachment.attachment_text` UPDATE (+ `text_extracted_at`, `text_hash`, `download_status`)
- 신규 verdict 컬럼 1개 추가 (Phase 1)
- zip 압축 해제 child row INSERT (Phase 1.5)
- 다른 트랙 영향 0

### 회피 영역 (작업 X)
- **KEC** 7,518 parts → `law_article` + `law_article_part` 통합 완료
- **NFTC/KDS** 5,387 parts → 동일 통합 완료
- **본칙** 21,216 parts → 동일 통합 완료
- 일반 법령 조문 본문 → `law_article` 33,862건 통합 완료

---

## Day 1 (재정의) 완료 결과

### Task 1 — `law_attachment` 460건 분포 ✅

| file_format | cnt | has_storage | has_article_link | avg_size | max_size |
|---|---|---|---|---|---|
| pdf | 418 | 418 | 0 | 575.5 KB | 21.0 MB |
| hwp | 30 | 30 | 0 | 399.8 KB | 5.6 MB |
| other | 12 | 10 | 0 | 26,960.3 KB | 69.8 MB |
| **합계** | **460** | **458** | **0** | — | — |

**핵심 발견**:
- ⚠️ `parent_article_id` **0건** — 모든 행이 article 매핑 없음. 사용자 말씀 "아티클과 구조가 맞지 않아 별도 테이블"의 정확한 의미.
- other 12건 평균 26.9 MB — 비정상적 크기. 압축 파일 가능성.
- Storage 미보유 2건 (other 12 중) → Phase 1에서 `NO_STORAGE` verdict 분류.

### Task 2 — `law_attachment_old_20260423` 4,907건 본질 진단 ✅

`attachment_text = attachment_title` **100%** (4,907건). 200자 hard cap = title의 truncate. v2 텍스트 추출 결과 아님 — Track D 작업 시 무시.

### Task 3 — Storage 1 파일 시범 변환 ✅

PDF 102 KB 단일 파일 → kordoc 변환 OK (388자), 한글 깨짐 1건 발견 (`제ž개정` ← `제·개정`) → Day 2 sample 검증 트리거.

---

## Day 2 — sample 변환 12건 + 폐기 룰 정의

### sample 12건 결과

| 분류 | 결과 |
|---|---|
| HWP 3건 (small/mid/big) | **100% OK** (kordoc HWP 안정) |
| PDF in_zip 3건 | **100% OK** |
| xlsx 1건 | OK |
| **PDF standalone L (KEC 21MB)** | **garbled 23,347** ← PUA 영역 사용자 폰트 매핑 한계 |
| zip 2건 | FAIL (kordoc HWPX 오인 — `Contents/` prefix 없는 zip) |
| 기타 | mixed |

### 사용자 정정 — POLLUTED_LATIN false positive

본 창의 1차 sniff 룰에 `'×', '·', '±', '°', '÷', '²', '³'` 등이 polluted 패턴으로 들어가 있었으나, 사용자 정정: **이는 정상 기호** (수식·각도·단위 표기). 본 창의 임의 판단 패턴 재발.

### sniff 룰 v2 (사용자 정정 코드)

```python
def sniff(md: str) -> dict:
    if not md:
        return {'verdict': 'EMPTY'}
    chars = len(md)
    pua = sum(1 for c in md if 0xE000 <= ord(c) <= 0xF8FF)
    pr = pua / chars if chars else 0
    if pua >= 100 or pr >= 0.01:
        return {'verdict': 'POLLUTED_PUA', 'pua': pua, 'pua_ratio': round(pr, 4), 'chars': chars}
    return {'verdict': 'CLEAN', 'chars': chars}
```

**룰 본질**: PUA (Private Use Area, U+E000~U+F8FF) 영역이 100자 이상 또는 1% 이상이면 폐기 후보. 정상 한글/한자/Latin/특수기호는 통과.

---

## Phase 1 — 본 적용 (마이그레이션 + 460 변환)

### 마이그레이션 1 — `track_d_add_extraction_verdict_column`

**사전 누락 (마스터 §2 학습 #11 위배)**: 본 창이 임의로 9개 소문자 verdict 값을 `download_status`에 넣으려다 460건 모두 `law_attachment_download_status_check` (대문자 6 값 PENDING/DOWNLOADING/SUCCESS/FAILED/SKIPPED/EXPANDED) CHECK 위반. **사용자 지적 후 정정**.

**해결**: 기존 `download_status` 6값 그대로 + 신규 `extraction_verdict` 컬럼 추가 (마스터 §2.4 로스리스 변환 정합 — 신규 컬럼으로 9 verdict 정밀 보전, 다른 트랙·코드 호환성 0 영향).

```sql
ALTER TABLE law_attachment ADD COLUMN IF NOT EXISTS extraction_verdict TEXT;
ALTER TABLE law_attachment ADD CONSTRAINT law_attachment_extraction_verdict_check 
  CHECK (extraction_verdict IS NULL OR extraction_verdict IN (
    'CLEAN','POLLUTED_PUA','UNSUPPORTED_FORMAT','CONVERSION_FAILED',
    'NO_STORAGE','TIMEOUT','EXCEPTION','EMPTY','DOWNLOAD_FAILED'
  ));
CREATE INDEX IF NOT EXISTS idx_law_attachment_verdict ON law_attachment(extraction_verdict);
```

### STATUS_MAP — 단일 진실 매핑

| verdict (스크립트) | download_status | extraction_verdict | attachment_text |
|---|---|---|---|
| CLEAN | SUCCESS | CLEAN | 보전 (md) |
| POLLUTED_PUA | FAILED | POLLUTED_PUA | NULL → Phase 1.1 보전 |
| UNSUPPORTED_FORMAT | SKIPPED | UNSUPPORTED_FORMAT | NULL → Phase 1.5 child 처리 |
| CONVERSION_FAILED | FAILED | CONVERSION_FAILED | NULL → Phase 1.6 IMAGE_PDF 재분류 |
| NO_STORAGE | SKIPPED | NO_STORAGE | NULL (보전 불가) |
| TIMEOUT/EXCEPTION/EMPTY/DOWNLOAD_FAILED | FAILED | 동일 | NULL |

### Phase 1 본 적용 결과 (460 row, 627초)

| extraction_verdict | download_status | cnt | with_text | avg_text_len |
|---|---|---|---|---|
| CLEAN | SUCCESS | 404 | 404 ✅ | 14,179자 |
| POLLUTED_PUA | FAILED | 40 | 0 → Phase 1.1 보전 |
| UNSUPPORTED_FORMAT | SKIPPED | 9 (zip) | 0 → Phase 1.5 처리 |
| CONVERSION_FAILED | FAILED | 5 | 0 → Phase 1.6 재분류 |
| NO_STORAGE | SKIPPED | 2 | 0 (Storage 부재) |

---

## Phase 1.1 + 1.6 — PUA 보전 + IMAGE_PDF 재분류

### 사용자 지적 — 마스터 §2.3 (보전) 누락

본 창의 직전 처리: POLLUTED_PUA 40건의 `attachment_text` NULL → 사용자 지적: "실패한것도 법령일건데. 그냥 에러로??". 마스터 §2.3 "분해 안 하더라도 보전" 위배.

**해결 균형 (§2.3 + §2.5)**:
- 저장 단계 (Track D): 변환 결과 모두 보전 (`attachment_text`)
- 사용 단계 (분해엔진 / Track E): `extraction_verdict='CLEAN'` 필터로 오염 폐기

### 마이그레이션 2 — `track_d_extend_verdict_image_pdf`

CHECK 확장: `IMAGE_PDF` verdict 추가 (10 verdict). kordoc stderr `IMAGE_BASED_PDF` 패턴 식별 → CONVERSION_FAILED 5건 재분류.

### 부분 재처리 (45 target, 83초)

| ACTION | cnt | 비고 |
|---|---|---|
| PUA_PRESERVED | 40 | raw md 보전 (avg 63,231자, hash + extracted_at) |
| CONV_FAIL_TO_IMAGE_PDF | 5 | kordoc stderr `IMAGE_BASED_PDF` 패턴 5건 모두 재분류, download_status FAILED → SKIPPED |
| FAIL | 0 | UPDATE_FAIL 없음 |

### Phase 1.1 + 1.6 후 DB 상태

| extraction_verdict | download_status | cnt | with_text |
|---|---|---|---|
| CLEAN | SUCCESS | 404 | 404 ✅ |
| POLLUTED_PUA | FAILED | 40 | 40 ✅ avg 63,231자 |
| UNSUPPORTED_FORMAT | SKIPPED | 9 | 0 → Phase 1.5 |
| IMAGE_PDF | SKIPPED | 5 | 0 (OCR 후속) |
| NO_STORAGE | SKIPPED | 2 | 0 |

**Phase 1.1+1.6 후 텍스트 보전율**: 444/460 = **96.5%**

---

## Phase 1.5 — zip 처리 (9 zip → 862 child INSERT + 변환)

### Step A — 시범 1 zip (162.6KB, 안 HWP 2개)

**1단계 검증** (`track_d_phase15_pilot.py`):
- zip download 166,483 bytes ✅
- zip 안 = HWP 2개 (OLE magic `d0cf11e0...`, kordoc 안정)
- 한글 파일명 cp437 → cp949 디코딩 정상
- Storage write 권한 검증 (test upload + remove) ✅

**2단계 INSERT** (`track_d_phase15_extract.py`):
- 1차 시도 — 실패 (UNIQUE 제약 `uniq_law_attachment_version_source` 위반, source_url 동일)
- **사용자 지적 — 본 창의 사전 점검 누락 (CHECK + 이번 UNIQUE 반복)**
- 정정: 기존 in_zip 319건 패턴 발견 — `source_url = parent.url + '#inner={seq:03d}'` + `storage_path = {uuid}/zip_{id}/{seq:03d}.{ext}` (3자리 zero-padded)
- 2차 시도 — INSERT 2건 OK (잔여 `01.hwp`/`02.hwp` 정리 + `001.hwp`/`002.hwp` upload + INSERT)

**시범 변환** (`track_d_phase15_convert.py`, 1초):
- 시범 2 row 모두 CLEAN (text_len 57,164 + 938)

### Step B — 8 zip 일괄 압축 해제 + INSERT (`track_d_phase15_batch.py`, 530초)

| zip | size | child entries | inserted |
|---|---|---|---|
| 4. 배출가스 연속자동 | 3.5MB | 14 | 14 ✅ |
| 실내공기질 | 5.7MB | 20 | 20 ✅ |
| 1. 총칙 시료채취 | 9.2MB | 20 | 20 ✅ |
| 먹는물수질 | 23.6MB | 155 | 155 ✅ |
| 3. 환경대기 | 23.6MB | 82 | 82 ✅ |
| 2. 배출가스 | 32.1MB | 141 | **140** (1 누락) |
| 교량설계 | 44.3MB | 71 | **70** (1 누락) |
| 수질오염 | 47.2MB | 357 | **355** (2 누락) |
| **합계** | — | **860** | **856** (-4 timeout) |

dry-run 860 PLAN vs apply 856 inserted — **diff 4건** (read/write timeout + HTTP/2 StreamReset, 큰 zip).

### Step B' — 누락 4건 재시도 (`track_d_phase15_retry.py`, 13초)

zip 별 `expected_seqs` (zipfile.namelist) vs `actual_seqs` (DB storage_path 추출) 비교로 정확 식별. exponential backoff (2-4-8s):

| zip | missing seq | retry 결과 |
|---|---|---|
| 2. 배출가스 | [48] | OK ✅ |
| 교량설계 | [63] | OK ✅ |
| 수질오염 | [289, 295] | OK ✅ |
| **합계** | **4** | **retried_ok 4** |

### Step C — 860 PENDING 변환 (`track_d_phase15_convert.py` 재실행)

| ACTION | cnt | 비고 |
|---|---|---|
| CLEAN | 818 + 1 retry | 정상 변환 |
| POLLUTED_PUA | 41 | raw md 보전 |
| DOWNLOAD_FAILED | 1 | read timeout — verdict reset 후 재실행 1건 → CLEAN |
| UPDATE_FAIL | 0 | — |

### Phase 1.5 후 DB 상태 (zip + child)

| 분류 | cnt |
|---|---|
| 9 zip parent (UNSUPPORTED_FORMAT) | 9 (보전 불가, child 보유) |
| zip-extracted child (CLEAN) | 821 |
| zip-extracted child (POLLUTED_PUA, 보전) | 41 |
| **child total** | **862** |

---

## Phase 1 종결 — 최종 통계 (1,322 row)

| extraction_verdict | download_status | cnt | with_text | is_child | avg_len |
|---|---|---|---|---|---|
| **CLEAN** | SUCCESS | **1,225** | 1,225 ✅ | 1,106 | 9,504자 |
| **POLLUTED_PUA** | FAILED | **81** | 81 ✅ | 75 | 37,636자 |
| UNSUPPORTED_FORMAT | SKIPPED | 9 (parent zip) | 0 | 0 | — |
| IMAGE_PDF | SKIPPED | 5 (OCR 후속) | 0 | 0 | — |
| NO_STORAGE | SKIPPED | 2 (보전 불가) | 0 | 0 | — |
| **합계** | — | **1,322** | **1,306 (98.8%)** | **1,181** | — |

**텍스트 보전율: 1,306 / 1,322 = 98.8%**

영구 보전 불가 (16건, 1.2%):
- UNSUPPORTED_FORMAT 9 — parent zip (child 862 보유로 실질 보전)
- IMAGE_PDF 5 — OCR 후속 트랙 위임
- NO_STORAGE 2 — 파일 자체 부재

---

## 마스터 §2 절대 원칙 종결 점검 (Phase 1)

| 원칙 | 적용 |
|---|---|
| ① LLM 0% | ✅ kordoc 결정적 변환 + 룰베이스 sniff (PUA 비율) |
| ② 법령 보전 | ✅ Storage 458 원본 + child 862 + attachment_text 1,306 |
| ③ 누락 0 | ✅ 1,322 row 모두 verdict 분류, 16건 (1.2%)만 보전 불가 (각 사유 기록) |
| ④ 100% 매핑 (로스리스) | ✅ extraction_verdict 10 verdict + parent_attachment_id 트레이스 + zip_inner_path 보전 |
| ⑤ 오염 = 폐기 | ✅ POLLUTED_PUA 81건 분해엔진 입력 차단 (CLEAN 필터), 원본 보전 |
| ⑥ 사용자 검증 부담 0 | ✅ 결정적 룰베이스 |
| ⑦ ground truth 우선 | ✅ Storage 원본 파일 |

---

## ⚠️ Phase 2 진단 — 가설 무효 발견 (사용자 지시 후 진행 보류)

### 본 창의 직전 announce (가설)

> "Phase 2: CLEAN 1,225건 → `law_article` INSERT (article_type='별표') + `law_article_part` 분해 + `parent_article_id` 추론"

### 진단 결과

**attachment_title 패턴**: 1,302건 (99.7%) "파일명만" (xxx.hwp/pdf), 별표 N/별지 N/서식 N 패턴 0건.

**attachment_no**: 1,306건 모두 NULL (별표 번호 식별자 부재).

**attachment_type_code 분포**:

| attachment_type_code | cnt | % | sample |
|---|---|---|---|
| REFERENCE_TEST_METHOD | 1,117 | 85.5% | "ES 02302.1d 실내 공기 중 미세먼지 측정방법 - 중량법" (공정시험기준 ES) |
| REFERENCE_PRODUCT_STANDARD | 81 | 6.2% | "KC 60598-2-8" (KC 안전기준) |
| REFERENCE_DESIGN_STANDARD | 78 | 6.0% | "KCS 24 20 15", "KDS 24 17 11" (설계 기준 / 시방서) |
| REFERENCE_META_CATALOG | 17 | 1.3% | "안전기준등록(관보, 고시)" |
| REFERENCE_ADMIN_INFO | 7 | 0.5% | "제3종시설물의 지정고시" |
| **ATTACHMENT_BODY** | **6** | **0.5%** | "조문별제개정이유서", "KGS Code 항목별 개정사유" (개정이유서/관보) |

### 결론 — 본 창 가설 100% 무효

1. **REFERENCE_* 1,300건 (99.5%)** = 외부 참조 표준 (KS/KC/KDS/KCS/공정시험기준 ES 등) — **법령 별표가 아닌 외부 표준 문서**. `law_article`로 변환하면 의미 왜곡 (마스터 §2.2 위배 위험).
2. **ATTACHMENT_BODY 6건 (0.5%)** = 개정이유서/관보 메타 — **별표·서식 본문 X**, 행정 메타 자료.
3. **별표·서식 본문은 1,322건 안에 사실상 부재**. 마스터 §7 Track D 정의 ("별표 PDF/HWP")와 실제 데이터 불일치 — **별표 본문은 v2에서 이미 `law_article`/`law_article_part`에 통합된 영역 (KEC/NFTC/KDS/본칙 등)이며, 본 1,322건은 외부 참조 표준 + 행정 메타로 구성**.

→ **Track D Phase 2 작업 범위 재정의 필요**.

### Phase 2 작업 방향 후보 (사용자 결정 사항)

| 옵션 | 작업 |
|---|---|
| A. 외부 참조 표준 별도 처리 | KS/KC/KDS/KCS/공정시험기준 → 별도 테이블 (예: `external_standard`) 또는 분해엔진 입력 외 보전 |
| B. law_article 통합 | 외부 참조 표준 본문도 `law_article` INSERT (article_type='참조표준') — 분해엔진 입력 |
| C. Track E 영역 위임 | 외부 참조 표준은 Track D 범위 외, Track E (분해엔진) 시작 시점 별도 결정 |
| D. Track D Phase 1 종결 + 다른 트랙 진행 | Phase 1 산출물 (CLEAN 1,225건) 보전 상태로 두고, 후속 Phase는 사용자 트리거 시 진입 |

---

## 다른 트랙 영향
- Track A/B/C: 영향 0 (별도 데이터 도메인)
- Track E: 분해엔진 입력 = `law_article` 본문 (v2 통합 완료) + dict_legal_terms (Track C). Track D Phase 1 산출물은 추가 입력 후보 (분해엔진 적용 여부는 Phase 2 결정 후)

---

## Pending 사항

1. **Phase 2 작업 범위 재정의** — 사용자 결정 (옵션 A/B/C/D)
2. **OCR 후속 트랙** — IMAGE_PDF 5건 위임 대상 (별도 트랙 또는 후속 작업)
3. **TAI 별표 본문 별도 수집 검토** — 마스터 §7 정의 "별표 PDF/HWP"가 본 1,322건과 매칭 안 됨. 진짜 별표가 어디 있는지 (외부 수집 필요한지) 별도 진단 필요할 수 있음

---

## 산출물 인덱스

### 마이그레이션 (Supabase apply_migration)

| 마이그레이션 | 단계 | 내용 |
|---|---|---|
| `track_d_add_extraction_verdict_column` | Phase 1 | `extraction_verdict` TEXT 컬럼 + CHECK 9 verdict + 인덱스 |
| `track_d_extend_verdict_image_pdf` | Phase 1.6 | CHECK 확장 — `IMAGE_PDF` verdict 추가 (10 verdict) |

### Cursor 스크립트 (`/tmp/`)

| 스크립트 | 단계 | 내용 |
|---|---|---|
| `track_d_apply.py` | Phase 1 본 변환 | 460 row 변환 (sniff + STATUS_MAP + DB UPDATE) |
| `track_d_phase1_extend.py` | Phase 1.1 + 1.6 | POLLUTED_PUA 보전 + CONVERSION_FAILED → IMAGE_PDF 재분류 (45 target) |
| `track_d_phase15_pilot.py` | Phase 1.5 시범 1 | zip 1건 압축 해제 + Storage write 권한 검증 |
| `track_d_phase15_extract.py` | Phase 1.5 시범 2 | 시범 zip의 안 파일 INSERT + Storage upload (2건) |
| `track_d_phase15_convert.py` | Phase 1.5 변환 | PENDING (extraction_verdict NULL) row 자동 변환 (fetch_pending) |
| `track_d_phase15_batch.py` | Phase 1.5 일괄 | 8 zip 압축 해제 + INSERT (860 PLAN, 856 inserted) |
| `track_d_phase15_retry.py` | Phase 1.5 재시도 | 누락 seq 식별 + INSERT (4 missing → 4 retried_ok) |

### 보고서 chronology

| 시점 | commit | 내용 |
|---|---|---|
| Day 1 외부 시범 | `54522efb` | **DEPRECATED** |
| Day 1 (재정의) | `a849f403` | 작업 범위 재정의 + 진단 ①②③ |
| Day 2 + Phase 1 종결 | (본 commit) | Day 2 sample + Phase 1·1.1·1.5·1.6 + Phase 2 진단 |

---

**END OF PHASE 1 — Phase 2 작업 범위 재정의 결정 대기.**
