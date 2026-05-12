# HANDOFF_20260503_S10 — 2단계(원문 수집·저장) 회귀 + 첨부 본체 트랙 회복 + 의무 추출 대상 분류

> 본 세션 = TAI Safe 법령엔진 정리 S10  
> 핵심: 9개 핸드오프 학습 → 산안법 시드 10건 정리 → 사용자 정정 2건 → DB 60개 테이블 학습 → 2단계 검증 → **첨부 본체 트랙 116건 회복 (139 + 319 inner)** → 의무 추출 대상 5 master 확정

---

## 0. 세션 메타

- 일시: 2026-05-03
- 시작: HANDOFF S1~S9 모두 학습
- 종료: 의무 추출 대상 분류 + 핸드오프 작성
- 진행자: 사용자(심태왕) + Claude (기획창)
- 본 세션 commit (tai-api):
  - `87e6728e` — `scripts/diagnose_orphan_rules.py` (read-only 진단)
  - `e834d00f` — `scripts/judge_orphan_rules.py` v1
  - `2b1ef80e` — `scripts/judge_orphan_rules.py` v2 (의무 패턴 16종 보강)
  - `d901fd5b` — `scripts/collect_law_attachments.py` v1
  - `3ee495b5` — `scripts/collect_law_attachments.py` v2 (ASCII-safe path)
  - `8bd2ebc3` — `scripts/expand_law_zip_attachments.py` (zip 압축 해제 + 개별 업로드)
  - `ff9c84e0` — `scripts/upload_local_attachments.py` (로컬 디렉토리 → Storage)
- 본 세션 마이그레이션 (5건):
  - `law_attachment_storage_setup`
  - `law_attachment_source_url_unique`
  - `law_attachment_status_expanded`
  - `classify_reference_attachments`

---

## 1. 사용자 정정 2건 (반드시 다음 세션도 적용)

### 정정 #1 (DELETE 절차 위반 — 결과는 운으로 맞음)

산안법 "샘플" 시드 10건 DELETE 시 **사전 본문 대조를 누락**했고, KEC 8건도 동일 패턴으로 DELETE 직전 사용자가 정지시킴.

> "패턴 같다고 지운다면 몰입과 뭐가 다른가."

검증 결과 — KEC 점번호(131/140/212/341)는 시드가 아니라 **첨부파일 본체 트랙의 실존 항목**. DELETE했다면 진짜 의무 8건 영구 손실.

**원칙(다음 세션도 유지)**: 
- DELETE/비활성화 등 비가역 작업 전에는 반드시 article_text 본문 대조
- 패턴 유사성으로 일괄 처리 금지
- 의심스러우면 사용자에게 결정 받기

### 정정 #2 (파이프라인 단계 인식)

사용자 5단계 파이프라인 명확화:

| # | 단계 | 본 세션 시작 시 상태 |
|---|---|---|
| 1 | 기본 법령 선별 (수집 대상 확정) | ✅ |
| 2 | **원문 수집·저장** | ⚠️ 검증 안 됨 (수집은 됐다고 표시만 됨) |
| 3 | 파싱 → 구조 필드 채우기 | ⚠️ 검증 안 됨 |
| 4 | 의무 추출 | ❌ 미진입 |
| 5 | 의무 고도화 → 법령엔진 가동 | ❌ 미진입 |

> "지금 어느 단계에 있나요? 2단계 검증부터 시작하죠."

본 세션은 **2단계 검증으로 회귀**. 의무 추출 정정 작업(D_MAPPED 180건 살림/죽임)은 일시 중단.

---

## 2. DB 학습 (법령엔진 60개 테이블)

본 세션에서 처음으로 DB 전수 학습. 핵심 테이블 24개 컬럼 정의 모두 확인.

### 5단계 매핑

| # | 단계 | 핵심 테이블 (실측 row) |
|---|---|---|
| 1 | 선별 | `law_external_catalog` (983), `law_collection_target` (656) |
| 2 | 수집 | **`law_master` (752)**, `law_version` (752), `law_content_raw` (752), `law_attachment` |
| 3 | 파싱 | `law_article` (30,881), `law_paragraph` (44,996), `law_item` (58,258) |
| 4 | 의무 추출 | `law_rule_drafts` (2,583), `rule_article_mapping` (2,677) |
| 5 | 법령엔진 | `master_building_legal_rules` (1,998), `master_legal_rules_pending_review` (1,468), `master_legal_rules_preserved` (321), `inspection_master` (1,246), `inspection_sets` (324) |

### 핵심 관찰

1. **단일 메인 테이블**: `master_building_legal_rules`에 building+industrial+construction 모두. `sector` / `domain_code`로 도메인 구분. 이름이 building이지만 통합 테이블.
2. **3중 분리 구조**: preserved (321) + pending_review (1,468) + main (1,998) ≈ 3,800건. 라이프사이클 관리.
3. **`law_id` NOT NULL** (article/paragraph/item) — S9에서 추가됨. version 경유 없이 master 직접 참조 가능.
4. **백업 테이블 11개** — `_old_20260423`, `_preswitch_20260423`, `_dup_backup_20260422`. 4/22~23 ATOMIC SWITCH 잔재. 운영 분리됐지만 정리 필요.
5. **pg_class.reltuples는 부정확** — 705/715로 보였는데 실측은 모두 752.

---

## 3. 2단계 검증 결과 — 카디널리티는 깔끔, 본문 누락은 광범위

### 무결성 (✅)

```
master 752 = version 752 = content_raw 752 (1:1:1)
모든 master에 current_version_id 채워짐 (NULL=0)
모든 version이 is_current=true (한 법령당 1버전 정책)
```

### 발견 #1 — target 4건 미수집

| # | 법령 | 정체 | 사용자 기준 |
|---|---|---|---|
| 1 | (한국전통문화대학교) 제3종시설물 지정 | NOTICE, article=0 | 첨부 본체 트랙 |
| 2 | 2025년 학교안전공제료 산정기준 고시 | NOTICE, article=0 | 첨부 본체 트랙 |
| 3 | **기후위기 대응을 위한 탄소중립·녹색성장 기본법 시행규칙** | 검색 결과 없음 | 🔴 **본법/시행령은 수집됨**, 시행규칙만 누락. 외부 확인 필요 |
| 4 | 한국전기설비규정 (KEC) | 첨부 본체 | (회복 완료) |

3번은 다음 세션에서 외부 확인 (시행규칙이 실재하는지). 본법+시행령으로 의무 추출 가능하니 우선순위 낮음.

### 발견 #2 — 본문 누락 116건 (수집 단계 결함)

전체 752 master 중 **116건 (15%)** 이 본문 사실상 0건. 패턴:
- `article_count <= 2` 
- `raw_xml`에 `<첨부파일링크>` 있음
- `law_attachment` 테이블에 0건

**원인**: law.go.kr DRF API가 "공고/고시" 형태로 응답. `<조문내용>` 빈 CDATA + 첨부파일 링크만. 본문이 PDF/HWP에 있음. 우리 collect_v2 파이프라인이 첨부 다운로드 안 함.

**영향 범위**:
- ELECTRIC: 88건 (KEC + KS 전기표준 77 + 기타)
- ENVIRONMENT: 7건
- BUILDING / CHEMICAL / GAS / 기타: 21건

사용자 기준: "수백 현장이 해야 할 일을 모르고 있던 정확한 케이스".

---

## 4. 첨부 본체 트랙 회복 (116건 → 458 첨부 + 2 EXPANDED)

### 4.1 인프라

- **Supabase Storage 버킷 `law-attachments`** (private, 200MB 제한)
- **`law_attachment` 메타 컬럼 추가**: `storage_bucket`, `storage_path`, `source_url`, `source_file_name`, `file_size_bytes`, `download_status`, `download_error`, `downloaded_at`, `text_extracted_at`, `file_format`, `parent_attachment_id`, `zip_inner_path`
- **`download_status` CHECK** 5종 + EXPANDED 추가 (총 6종)
- **partial unique index** `(law_version_id, source_url) WHERE source_url IS NOT NULL`

### 4.2 자동 다운로드 (`collect_law_attachments.py`)

- 후보 자동 검출: article ≤ 2 AND raw_xml 첨부링크 AND 미수집
- PDF 우선, HWP fallback
- ASCII-safe Storage path: `{master_id}/{flSeq}.{ext}` (한글 InvalidKey 회피)
- 원본 한글 파일명은 `source_file_name`에 보존
- **결과: 116 master → 138 SUCCESS + 2 FAILED (zip 50MB 초과)**
- 합계 약 281MB 다운로드

### 4.3 ZIP 처리 (`upload_local_attachments.py`)

50MB 초과 zip 2건 (Supabase 단일 PUT 한계):
- 환경유해인자공정시험기준.zip (61MB)
- 대기오염공정시험기준.Zip (72MB)

**처리**: 사용자가 Mac에서 unzip → 로컬 디렉토리 지정 → 스크립트가 재귀 탐색 + 한글 NFD→NFC 정규화 + ASCII path 변환 + 개별 업로드.

- 환경유해인자: 62 PDF (목차 61 + 1)
- 대기오염: 257 PDF (목차 257 일치)
- **합계 319 inner SUCCESS**, 원본 zip 2건 EXPANDED 마킹

> 참고: `expand_law_zip_attachments.py`도 push했으나 자동 다운로드 시 IP 차단 우려 + 로컬 unzip이 더 빠르다는 사용자 판단으로 사용 안 함. 코드는 보존.

### 4.4 최종 상태

```
SUCCESS:  ATTACHMENT_BODY  139 (281.4 MB)  -- collect 단계 자동
SUCCESS:  ZIP_INNER        319 (154.7 MB)  -- 사용자 unzip 후 업로드
EXPANDED: ZIP_PARENT         2 (126.4 MB)  -- 펼친 zip 원본 보존
FAILED:                       0
─────────────────────────────────────
합계 460 row / 약 562 MB
```

---

## 5. 의무 추출 대상 분류 (옵션 B: attachment_type_code 태그)

`master.is_active`는 그대로 유지(추후 활용 가능). 첨부의 `attachment_type_code`로만 분류.

### 분류 결과 (마이그레이션 `classify_reference_attachments` 적용)

| attachment_type_code | row | master | 사이즈 | 의무 추출 |
|---|---:|---:|---:|:---:|
| **ATTACHMENT_BODY** | 6 | **5** | 21.1 MB | ✅ |
| REFERENCE_TEST_METHOD | 339 | 14 | 428.9 MB | ❌ (시험 절차 참조용) |
| REFERENCE_PRODUCT_STANDARD | 80 | 77 | 64.7 MB | ❌ (KS 상품 규격) |
| REFERENCE_META_CATALOG | 18 | 9 | 1.7 MB | ❌ (행안부 안전기준 등록 = 메타 카탈로그) |
| REFERENCE_DESIGN_STANDARD | 8 | 5 | 45.3 MB | ❌ (국토부 설계기준 = 시공사 대상) |
| REFERENCE_ADMIN_INFO | 9 | 6 | 0.9 MB | ❌ (행정 안내) |

### 의무 추출 대상 5 master 확정

| # | 법령 | 부처 | 본문 사이즈 |
|---|---|---|---:|
| 1 | **한국전기설비규정 (KEC)** | 기후에너지환경부 | 21 MB ⭐ 메인 |
| 2 | 「고압가스/액석/도시가스」 가스기술기준 (상세) | 산업통상부 | 30 KB |
| 3 | 「액석/도시가스」 가스기술기준 | 산업통상부 | 335 KB |
| 4 | 열사용기자재 검사 및 검사면제 기준 | 산업통상부 | 100 KB |
| 5 | 전기통신사업용 무선설비 기술기준 | 국립전파연구원 | 80 KB |

KEC 외 4건은 모두 1MB 미만. 처리 부담 낮음.

---

## 6. 다음 세션 진입점 — 의무 추출 PoC (KEC)

### 결정 사항 (사용자 동의)

- **모델 조합 (옵션 B)**: Gemini 2.5 Pro 1차 추출 + Sonnet 4.6 검증
- **PoC 1건 = KEC** (21MB PDF, Gemini Pro의 200만 토큰 컨텍스트로 청크 분할 없이 단일 호출)
- **API 키**: GEMINI_API_KEY, ANTHROPIC_API_KEY 모두 Railway 환경변수에 등록됨 (사용자 확인)
- **비용 추정**: 5건 전체 약 1.1만 원 (Gemini Pro $3 + Sonnet $5)

### 작업 흐름 설계 (다음 세션 작성)

1. **`scripts/extract_obligations_poc.py`** 작성:
   - 입력: `--master-id` (기본: KEC = `64209405-1a40-4f0a-aa8a-6f3e55917001`)
   - Step 1: 첨부 PDF/HWP를 Storage에서 다운로드 (또는 사이즈 작으면 직접)
   - Step 2: PDF는 Gemini 2.5 Pro에 PDF native 입력으로 전달 (HWP는 텍스트 추출 후)
   - Step 3: 의무 후보 JSON 추출 (프롬프트: 사업장 의무 / 조건 / 주체 / 주기 등)
   - Step 4: Sonnet 4.6 검증 (누락/오추출 검사)
   - Step 5: `law_rule_drafts` 테이블에 INSERT (기존 2,583건과 별개로 `source_doc_id` = master_id 또는 attachment_id)
   - Step 6: 사용자 검토 리포트 (콘솔 + CSV)

2. **사용자 검토** → 품질 OK면 나머지 4 master 확대 + 추후 본문 article_text도 처리

### KEC HWP/PDF 처리 메모

KEC 21MB PDF는 Gemini Pro PDF native로 처리 가능 (200만 토큰). 단 출력은 청크 분할 가능 (의무 N개 → JSON 배열). 

HWP는 KEC에 없지만 다른 4건에는 있을 수 있음. `pyhwp`/`hwp5`가 한글 라이브러리 한계 있어 일부 깨짐 가능. 첫 PoC는 PDF로 시작.

---

## 7. 미해결 / 보류 이슈

### 우선순위 높음

1. **D_MAPPED 180건 정합성 작업 보류 중** — 본 세션 시작 시 진행하던 작업. 4단계 의무 추출 본 미션 완료 후 본문 기반 신규 룰로 자연 대체 예정.
2. **3단계(파싱) 검증 미진입** — article_no gap, paragraph/item 분리, 별표 누락 등. 의무 추출과 병행 또는 후속.
3. **기후위기 탄소중립 시행규칙 누락** (target 4건 미수집 중 1건) — 시행규칙이 실재하는지 외부 확인 필요.

### 우선순위 중간

4. **백업 테이블 11개 정리** — `_old_20260423`, `_preswitch_20260423`, `_dup_backup_20260422`. 운영 분리됐지만 DROP 또는 archive 스키마로 이전.
5. **`law_master` 752 vs `law_collection_target` 656** = 96 차이. catalog→target 경로 외 master 어떻게 들어왔는지 확인 (S6/S8 추정 가능).
6. **대기오염 master에 5건 ATTACHMENT_BODY 추가 row** — zip 외 별도 첨부였을 가능성. (현재는 분류 안 됨, 운영 영향 적음).

### 우선순위 낮음

7. **HWP 처리 라이브러리 검증** — 의무 추출 5 master 중 일부에 HWP 있을 가능성. `pyhwp`/`hwp5` 한국어 처리 정확도 확인.
8. **첨부 본체 회복 116건 외 추가 누락** — 첨부 링크 있는데 law_attachment에 0건인 case 386건 (이번 회복 116건의 영향 외, 별표/서식 등). 의무 추출 1차 결과 보고 결정.

---

## 8. 작업 원칙 (S9 § 4 + S10 정정 통합)

1. **핸드오프 몰입 금지** — 소스+DB가 진실
2. **검증은 row 단위 원문 대조** — 숫자 아님
3. **임의 판단 금지** — 분기마다 사용자 결정
4. **기존 파이프라인 수정 사용** — 별도 우회 금지
5. **신뢰 추락 방지** — 잘못된 1건 = 수백 업체 영향
6. **비개발자이므로 Claude가 흐름 잡되 결정 받기**
7. **패치 누적 시 멈추고 일괄 검증**
8. **(S10) 비가역 작업(DELETE/비활성화) 전 본문 대조 필수** — 패턴 유사성만으로 처리 금지
9. **(S10) 파이프라인 단계 인식** — 의무 추출 정정은 수집·파싱 검증 통과 후
10. **(S10) Python은 기계적 작업** — 검증은 Claude가 다각도 SQL 분석 + 사용자 판단

---

## 9. 사용자 핵심 판단 기준 (S9~S10 일관)

> **하나라도 놓치면 수백 현장이 해야 할 일을 안 하게 되고, 하나를 잘못 넣으면 수백 현장이 안 해도 될 일을 하게 된다.**

이번 세션에서 검증된 케이스:
- ❌ 산안법 시드 10건 DELETE — 운으로 맞음 (절차 위반)
- ✅ KEC 8건 DELETE 정지 — 본문 검증으로 첨부 본체 식별
- ✅ 중대재해법 시행령 제5조 KEEP — 자동 KILL 오판 → 사용자 검증으로 수정
- ✅ KS 77 / 환경시험 13 / 행안부 9 / 기타 12 = REFERENCE_* 분류 — 의무 추출 노이즈 차단
- ✅ 의무 추출 대상 5 master 좁힘 — 비용/노이즈 모두 최소화

---

## 10. 환경 정보 (변동 없음)

- Supabase: `vwlahtguyggrhvslabax` (서울)
- Repos: `taiengineering/tai-api` (scripts/, routers/, docs/), `taiengineering/tai-admin` (docs/)
- Railway: api.taieng.co.kr, GCP 동적 IP
- Mac 로컬 실행: `~/dev/tai-api` 에서 `railway run python3 scripts/X.py`
- LAW cron 5개 비활성화 유지

---

## 11. 다음 세션 첫 메시지 권장 흐름

```
1. 본 핸드오프 학습
2. KEC PoC 의무 추출 스크립트 (scripts/extract_obligations_poc.py) 설계 + push
3. 사용자 로컬 실행 → 결과 검토
4. 품질 OK → 나머지 4 master 확대
5. 결과 → law_rule_drafts INSERT + 검토 보고
6. 다음 분기: 3단계(파싱) 검증으로 갈지, 4단계 본 미션(의무 추출) 752 master 전체로 확대할지
```

---

**핸드오프 끝. 다음 세션은 KEC PoC부터.**
