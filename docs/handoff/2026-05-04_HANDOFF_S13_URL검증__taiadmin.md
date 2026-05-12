# S13 — 4 master 다이렉트 URL 검증 결과 + 가스 작업 범위 재정의

**작성일**: 2026-05-04
**선행 문서**: `HANDOFF_20260504_S12.md` (§ 4.1, § 4.2, § 8.1)
**목적**: web_search/web_fetch로 검증한 본문 수집 경로 확정 + 핸드오프 § 4.2 / § 8.1 보강

---

## 1. S12 핸드오프 § 4.2 (외부 PDF 후보 URL) — 검증 결과

### 1.1 결론 표

| Master | 본문 형식 | 검증된 직접 URL | 상태 |
|---|---|---|---|
| **무선설비** (2023-22) | HTML (law.go.kr 본문 페이지) | `https://law.go.kr/admRulLsInfoP.do?admRulId=42701` | ✅ **HTML 페이지 검색 결과로 확정**. 단 PDF 아님 |
| **무선설비** (rra.go.kr 첨부) | PDF/HWP 추정 | `https://www.rra.go.kr/FileDownSvl?file_type=LAWKR&file_parentseq=31&file_seq=N` | ⚠️ **file_seq 미확인** (file_seq=16은 2002 버전 확인됨, 최신 file_seq 모름) |
| **무선설비** (hctinsight PDF) | PDF | `http://hctinsight.com/webzine/webzine/202312/file/kc/kc1.pdf` | ❌ **2023-22호 개정 부분만**, 전체 본문 아님 |
| **열사용기자재** (2024-184) | **HWPX 12.36MB** | `https://motie.go.kr/kor/article/ATCL0c554f816/64712/view` (페이지에서 다운로드) | ✅ 본문 존재 확정. 단 **PDF 아님 → HWPX 처리 필요** |
| **가스 #1** (2020-271) | KGS Code 코드별 PDF | KGS Code 사이트: `https://cyber.kgs.or.kr/kgscode...` | ⚠️ **단일 PDF 없음, 코드 묶음** |
| **가스 #2** (2020-168) | 동일 | 동일 | ⚠️ **단일 PDF 없음, 코드 묶음** |

### 1.2 핵심 발견 — KEC와 다른 점

| 항목 | KEC | 4 master |
|---|---|---|
| 본문 형식 | PDF (21.6MB / 1234p) | HTML / HWPX / 코드별 PDF 묶음 |
| 단일 파일? | ✅ 단일 PDF | ❌ 단일 파일 없음 |
| 추출 도구 | pdfplumber 충분 | **master별 다른 도구 필요** (HTML 파서 / HWPX 변환 / 다중 PDF 통합) |
| 페이지 마커 | `[PAGE N]` | **무선/열사용은 페이지 개념 없음**. 가스는 코드 단위 |

→ **PoC v2.7~v2.10 (PDF 전제)를 그대로 적용 불가**. master별 추출 단계 분기 필수.

---

## 2. master별 본문 수집 전략 (확정)

### 2.1 무선설비 (2023-22) — HTML 기반

**1순위**: law.go.kr HTML 본문 페이지 직접 파싱
- URL: `https://law.go.kr/admRulLsInfoP.do?admRulId=42701`
- 방법: requests + BeautifulSoup (또는 pdfkit/wkhtmltopdf로 PDF 변환 후 처리)
- 장점: 최신 통합 본문 자동 (개정 누적 적용된 "현재 시행 본문")
- 단점: 페이지 개념 없음 → ctx 추출 시 chunk_id 또는 article 단위로 마킹 필요

**2순위**: rra.go.kr 자료실 첨부파일
- URL 패턴: `https://www.rra.go.kr/FileDownSvl?file_type=LAWKR&file_parentseq=31&file_seq=N`
- 작업: rra.go.kr `lw_seq=31` 페이지 직접 접속 → 최신 file_seq 확인 (수동) → 다운로드
- file_seq 자동 확인 불가 (web_fetch robots.txt 차단)

**3순위 (불가)**: hctinsight PDF — 개정 부분만이라 전체 본문 아님

### 2.2 열사용기자재 (2024-184) — HWPX 기반

**확정 URL**: `https://motie.go.kr/kor/article/ATCL0c554f816/64712/view`
- 첨부 파일명: `(개정전문) 열사용기자재의 검사 및 검사면제에 관한 기준(산업통상자원부 고시 제2024-184호).hwpx`
- 크기: 12,360.4 KB (12.36 MB)
- 설명: "(개정전문)" → **전부개정 본문 통째**. KEC PDF에 상응하는 단일 본문 파일

**HWPX 처리 옵션**:
- A) **pyhwpx** (Python 라이브러리) — 텍스트 추출 가능, 표 추출 한계 있음
- B) **LibreOffice headless 변환** — `libreoffice --headless --convert-to pdf input.hwpx` → PDF로 변환 후 pdfplumber (KEC 파이프라인 재사용)
- C) **hwp5txt** (hwp5 라이브러리) — HWPX는 미지원, HWP만 처리

→ **권장: B) LibreOffice → PDF → pdfplumber**. KEC 파이프라인 100% 재사용.

### 2.3 가스 #1, #2 — 작업 범위 재정의 (3가지 옵션)

KGS Code = FU(고압가스) / FP(액화석유가스) / FS(고압가스 사용) / FC(고압가스 충전) / FD / FE / FT 등 수십 개 코드 묶음.
산자부 고시 2020-271호와 2020-168호는 그 중 **여러 코드의 통합 개정 공고**.
**단일 본문 파일이 없음** — KGS Code 사이트에서 코드별 PDF 별도 제공.

#### 옵션 A: 통합 처리 (보류 권장)
- 2020-271호 / 2020-168호 개정안에 포함된 코드 목록 추출 → 각 코드 PDF를 KGS Code 사이트에서 일괄 다운로드 → 모두 합쳐서 1 master 처리
- 단점: 코드별 PDF 다수 + master_id가 1개라서 article 매칭 어려움
- 장점: 기존 4 master 메타 그대로 유지 가능

#### 옵션 B: master 분리 (DB 스키마 변경)
- 가스 #1, #2 master 각각을 코드별 sub-master로 분리
- 예: 가스 #1 → FU211, FU212, FP111, FP112, ...
- 단점: DB 마이그레이션 필요 (현재 4 master 메타 폐기 + 신규 master 다수 INSERT)
- 장점: KGS Code 본래 구조와 1:1 매핑

#### 옵션 C: 보류 (권장)
- 4 master 트랙에서 가스 #1, #2 **제외** → 무선 + 열사용 2건만 처리
- 745 master 트랙 (article_text 기반) 끝난 후 KGS Code 별도 트랙으로 재진입
- 장점: 4 master 트랙 빠르게 종결 → 745 master 본 미션 진입 빠름
- 단점: 가스 master active 적재가 더 늦어짐

→ **권장: 옵션 C (보류)**. 가스는 745 master 트랙 후 별도 KGS Code 트랙으로 진행.

---

## 3. S12 핸드오프 § 8.1 결정 답

| 항목 | 답 |
|---|---|
| **시작 master** | **무선설비 (2023-22)** — 가장 분량 작음, HTML 본문 직접 파싱 가능 |
| **외부 본문 다운로드 방식** | **1차: law.go.kr HTML 페이지 직접 파싱** (수동 OK, 자동 시 robots.txt 검토 필요) |
| **추출 코드 방식** | **(b) Cursor 정식 단일 파일** (PoC v2.7~v2.10 학습 통합) |
| **master별 적용 차이** | 무선=HTML 파서, 열사용=HWPX→PDF 변환, 가스=보류 |
| **이번 트랙 목표** | **무선 + 열사용 2 master** (가스 2건 보류) |

---

## 4. 무선설비 작업 절차 (이번 세션 시작)

### 4.1 단계
1. **본문 확보**:
   - law.go.kr HTML 페이지 (`admRulId=42701`) 수동 접속 → 본문 영역 텍스트 복사 → 파일 저장
   - 또는 rra.go.kr 자료실 (`lw_seq=31`) 수동 접속 → 최신 file_seq 첨부파일 다운로드
2. **Supabase storage 업로드**: `law-attachments` 버킷 → `{master_id}/body_무선설비_2023-22.{형식}`
3. **law_attachment INSERT**: `attachment_type_code='ATTACHMENT_BODY'`, `storage_path`, `file_size_bytes`, `attachment_title='전기통신사업용 무선설비의 기술기준 본문'`
4. **본문 텍스트 추출**:
   - HTML이면 BeautifulSoup
   - PDF면 pdfplumber (KEC 파이프라인)
   - HWP/HWPX면 LibreOffice 변환 후 pdfplumber
5. **PoC 파이프라인 적용** (Cursor 단일 파일 — `extract_master.py`):
   - Gemini chunk 추출 (master별 점번호 형식 system prompt: `제3조 제2항`, `제5조의2`)
   - Sonnet 검증 (v2.7 4가지 보강 + v2.8 ctx prefix + v2.9 멀티 위치 + v2.10 batch=1)
6. **drafts INSERT**: `insert_kec_to_drafts.py` 응용 (상수 5개 변경)
   - `MASTER_ID = "a7b2021e-e211-423d-90ec-c1dfd633f5f6"`
   - `LAW_NAME = "전기통신사업용 무선설비의 기술기준"`
   - `SOURCE_API = "gemini_pro_v2_10_4master"`
   - `external_source = "law.go.kr"` (또는 `rra.go.kr`)

### 4.2 master별 점번호 형식 (system prompt)
- 무선: `제N조`, `제N조제N항`, `제N조의N`, 항목 표기 `① ② ③ ...`, 호 `1. 2. 3. ...`, 목 `가. 나. 다. ...`
- 열사용: `[별표 N]`, `제N조 ②`, `1. 가. 1)`
- (가스: 보류)

### 4.3 quality 보장 (KEC 동일)
- broken JSON 0%
- false negative 5% 이하
- prefix 발견율 100%
- 비용 ≤ $3 / master

---

## 5. 다음 단계 (대표님 결정 필요)

이 문서 검토 후 다음 중 선택:

1. **A**: 무선설비 본문 직접 가져오기 시작 (Cursor에서 `extract_master.py` 신규 작성)
   - 본문은 law.go.kr HTML 또는 rra.go.kr 자료실에서 대표님이 수동 다운로드 후 Supabase 업로드
   - 이후 PoC 파이프라인 적용
2. **B**: 가스 master 보류 결정 먼저 확인 (이 핸드오프 § 2.3 옵션 C 채택?)
3. **C**: 745 master 트랙으로 직행 (4 master 모두 후순위) — article_text 기반이라 PDF 불필요, 본 미션 빠른 진입

---

## 6. 검증 못한 항목 (한계 보고)

- rra.go.kr `FileDownSvl` 최신 file_seq 확인 — robots.txt 차단으로 web_fetch 불가
- law.go.kr 본문 페이지 실제 fetch — search 결과로만 URL 존재 확인, 직접 fetch 시 PERMISSIONS_ERROR
- 가스 #1, #2 산자부 고시 본문 hwp가 실제로 존재하는지 — motie.go.kr 검색에 안 뜸 (KGS Code 사이트로 분산됐을 가능성)
- KGS Code 사이트의 코드별 PDF 다운로드 URL 패턴 — 추가 검색 필요 (대표님 결정 후 진행)

이 항목들은 추측 금지 — 대표님이 수동 확인 또는 다음 세션에서 추가 검색.
