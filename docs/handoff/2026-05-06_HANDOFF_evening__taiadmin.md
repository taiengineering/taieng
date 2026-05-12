# HANDOFF 2026-05-06 (저녁)

> 의미절 분해 본 적용 완료 → master_rule_v2 설계 진입 → sector 표준화 이슈 분석

## 오늘 작업 종합

### 1. 의미절 본 적용 58,495 ✓ 완료

| 지표 | 결과 |
|---|---|
| Version | v1.7.1 (truncate-first 정상 작동) |
| Total clauses | **58,495** |
| Distinct laws / articles / parts | 366 / 19,265 / 49,997 |
| 미분류 | 702 (1.20%, 모두 needs_review) |
| executor 채움률 | 68.8% |
| condition 채움률 | 38.0% |
| **if 셋 채움률** | **80.0%** ✓ 사용자 핵심 우려 충족 |
| cycle 채움률 | 11.4% |
| exception 추출 | 12건 (모집단 "다만" 자체 19건만 있음, 정규식 정상 작동) |
| Silent failure | **0** |

본 테이블 `semantic_clause` 마이그레이션 완료 (decomposition_version='v1.7.1', UNIQUE/CHECK/FK 제약 활성).

### 2. master_rule_v2 설계 시작 (PENDING)

#### 사용자 결정 사항

1. ✓ **기존 mblr 자산 archive 결정**
   - 이유: 80%(1,601건)가 AI_GENERATED, 검증 시도해도 추적 오류 위험 큼
   - 사용자 표현: "이전에 너무 고생해서 만든 데이터들이라 아까워서 재사용하다 AI 임의판단 개입해서 이 모양이 됐음"
   - 결정: drop 안 하고 rename(`_archive_ai_generated_20260506`)으로 보존

2. ✓ **새 시스템 4 테이블 (사용자 검증 후 push 예정)**
   - `master_rule` (마스터 룰, 의미절 기반, 6하원칙 + 범위)
   - `master_rule_application` (사업장별 적용 결과)
   - `inspection_item_v2` (점검항목, 4가지 세팅 boolean)
   - `master_rule_extraction_log` (변환 추적)

3. ✓ **의미절 → master_rule 자동 변환 알고리즘 원칙**
   - AI 호출 0회 (정규식/키워드 사전만)
   - DEFINITION/DELEGATION/STATEMENT 의미절은 skip (룰 아님)
   - generation_confidence 자동 계산
   - 신뢰도 < 0.7 OR scope 비어있으면 needs_review=true

### 3. sector 표준화 — 핵심 이슈 발견

#### 사용자 핵심 통찰

- "공용/건물/공장/건설/특수시설 5가지 구분이 최상위에 있어야 함"
- 단 **"공용"은 별도 카테고리가 아니라 "중복"(다중 적용) 의미**
- → master_rule_v2.sectors는 **`text[]` 배열** (단일 enum 아님)

#### 사용자 동의 사항

1. ✓ sectors text[] 다중 배열 동의
2. ✓ 법령명 → sectors 매핑 동의 + **단** 전역변수 사용처 코드 수정 작업 동반
3. **분석 필요**: 법령 단위 매핑 vs 조문 단위 매핑
4. ✓ sector 4개 표준 동의: BUILDING / INDUSTRIAL / CONSTRUCTION / SPECIAL_FACILITY (특수시설은 비활성, 향후 고도화)

#### 현재 sector 데이터 불일치 (정리 필요)

4 테이블에서 sector 값 모두 다름:

| 테이블 | 값 | 행수 |
|---|---|---|
| `factories` | INDUSTRY / BUILDING / CONSTRUCTION (3개, COMMON 없음) | 30 |
| `master_building_legal_rules` | COMMON / **MANUFACTURING** / BUILDING / CONSTRUCTION | 2,002 |
| `semantic_clause` | COMMON / BUILDING / CONSTRUCTION / **INDUSTRIAL** | 58,495 |
| `system_codes.sector` | BUILDING / **INDUSTRY** / CONSTRUCTION / **SPECIAL** (COMMON 없음, code/code_name 거꾸로) | 4 |

→ 공장 코드만도 3가지 (INDUSTRY/MANUFACTURING/INDUSTRIAL), COMMON 누락.

#### Cross-applicability 검증 결과

sector × 키워드 매트릭스 분석 결과:

| 방향 | 비율 | 평가 |
|---|---|---|
| **CONSTRUCTION → BUILDING** | **0.2% (10건)** | sample 10건 모두 가짜 매칭. 건설 조문이 건물에 적용되는 경우 거의 없음 |
| BUILDING → CONSTRUCTION | 2.6% (119건) | 일부 진짜 (건축법의 "건축공사" 조문) |
| **INDUSTRIAL → CONSTRUCTION** | **2.7% (84건)** | **매우 강함** — 산업안전보건법은 명시적으로 건설업 적용 ("건설업 공사금액 N억원" 조문) |
| BUILDING → INDUSTRIAL | 0.9% (41건) | 거의 없음 |

**결정적 발견**: 한 법령 안에서 sector 다양성 = 0 (366 법령 모두 단일 sector). 즉 의미절 분해 시 sector는 **법령 단위**로만 부여됨. 조문 단위 cross-applicability 분석은 현재 데이터로 불가능.

→ **법령 단위 다중 매핑이 충분** (예외: 산업안전보건기준 9장 같은 명백한 경우만 조문 단위 override).

#### COMMON 47K (80%)는 "공통"이 아니라 "분류 안 됨"

TOP 20 법령 분석 결과:

| 법령 | 건수 | 진짜 sector |
|---|---|---|
| 전기통신사업법 | 718 | SPECIAL_FACILITY (비활성) |
| 재난 및 안전관리 기본법 (시행령 포함) | 1,356 | 모든 sector |
| 국토의 계획 및 이용에 관한 법률 (시행령) | 1,206 | BUILDING + CONSTRUCTION |
| 주택법 | 605 | BUILDING + CONSTRUCTION |
| 의료법 | 595 | SPECIAL_FACILITY (비활성) |
| 대기환경보전법 (시행규칙 포함) | 1,106 | INDUSTRIAL + CONSTRUCTION (건물 X) |
| 물환경보전법 | 535 | INDUSTRIAL + CONSTRUCTION |
| 산업집적활성화법 (시행령) | 960 | INDUSTRIAL만 |
| 장애인복지법 | 504 | SPECIAL_FACILITY |
| 산업재해보상보험법 | 502 | 모든 sector |
| 공동주택관리법 (시행령) | 880 | BUILDING만 |
| 폐기물관리법 | 447 | 모든 sector |

→ COMMON은 "다양한 sector 매핑이 필요한데 안 된 상태"였음. 사람이 법령명만 보면 정확히 매핑 가능.

---

## 핵심 이슈

### 이슈 1: sector 표준 깨짐 (4 테이블 불일치) — **내일 1순위**

- `system_codes.sector`에 COMMON 누락, INDUSTRY/SPECIAL 명칭 통일 필요
- `factories.sector` INDUSTRY → INDUSTRIAL 통일 필요 (15 rows)
- 코드 사이드 영향: 백엔드/프론트의 sector 사용처 검색 필요 (전역변수)

### 이슈 2: 산업안전보건법 분류 오류

- 현재 `semantic_clause`에서 INDUSTRIAL로만 분류
- 실제로는 BUILDING + INDUSTRIAL + CONSTRUCTION 3 sector 모두 적용
- → 법령 단위 다중 매핑으로 해결 (`law_sector_mapping`)

### 이슈 3: 코드 영향 미파악

- 사용자 명시: "전역변수를 사용하고 있는 곳들이 있으므로 해당 프로그램이나 API 등을 수정해야 하는 작업 동반"
- 백엔드 (`tai-api`) Python 코드의 sector 사용처
- 프론트엔드 (`tai-admin`) HTML/JS의 sector 사용처
- → grep 검색 필요

### 이슈 4: 86개 테이블 RLS 비활성

- `semantic_clause`, `master_building_legal_rules`, `law_article` 등 핵심 테이블 포함
- anon 키로 누구나 read/modify 가능
- 메모리상 RLS 활성화 시 정책 없으면 anon 차단 → 신중히
- 별도 작업 (이번 흐름과 무관, 우선순위 낮음)

---

## 내일 작업 (5월 7일 우선순위)

### A. 법령명 → sectors 자동 매핑 (1차) — 1순위

**목표**: 366 법령 → sectors[] 다중 매핑 사전 작성

```python
# 자동 매핑 룰 후보 (사용자 검증 가능)
LAW_SECTOR_RULES = [
    # 명확한 단일 sector
    (r'^건축법', ['BUILDING']),
    (r'^공동주택관리법', ['BUILDING']),
    (r'^주택법', ['BUILDING', 'CONSTRUCTION']),
    (r'^건설(공사|기술|산업|사업|폐기물|기계)', ['CONSTRUCTION']),
    (r'^산업집적활성화', ['INDUSTRIAL']),
    
    # 명확한 다중 sector
    (r'^산업안전보건', ['BUILDING', 'INDUSTRIAL', 'CONSTRUCTION']),
    (r'^재난 및 안전관리 기본', ['BUILDING', 'INDUSTRIAL', 'CONSTRUCTION']),
    (r'^산업재해보상보험', ['BUILDING', 'INDUSTRIAL', 'CONSTRUCTION']),
    (r'^대기환경보전|^물환경보전', ['INDUSTRIAL', 'CONSTRUCTION']),
    (r'^폐기물관리', ['BUILDING', 'INDUSTRIAL', 'CONSTRUCTION']),
    (r'^국토의 계획 및 이용', ['BUILDING', 'CONSTRUCTION']),
    
    # SPECIAL_FACILITY (비활성)
    (r'^전기통신사업|^의료법|^장애인복지|^영유아보육|^학교', ['SPECIAL_FACILITY']),
]
```

**산출물**:
1. `docs/extraction/scripts/law_sector_mapping.py` — 자동 매핑 스크립트
2. `docs/extraction/LAW_SECTOR_AUTO_MAPPING_2026-05-07.md` — 366 법령 자동 매핑 결과 (HIGH/MEDIUM/LOW 신뢰도)
3. `law_sector_mapping` 테이블 생성 (Supabase migration)

**작업 순서**:
1. 법령명 자동 매핑 룰 작성 (30분)
2. 366 법령 자동 매핑 실행 + 결과 표 출력
3. 사용자 LOW 신뢰도 review (50~80건 추정)
4. `law_sector_mapping` 테이블 INSERT

### B. system_codes.sector + factories.sector 정비 — 2순위

**목표**: 4 테이블 sector 코드 통일

**작업**:
1. `system_codes.sector` migration:
   - COMMON 추가 (정확히는 사용 안 됨, 표준만)
   - INDUSTRY → INDUSTRIAL
   - SPECIAL → SPECIAL_FACILITY
   - code/code_name 거꾸로 들어간 부분 수정
2. `factories.sector` 일괄 UPDATE:
   - INDUSTRY → INDUSTRIAL (15 rows)
3. `factories.sector` CHECK 제약 추가 (4개 enum 강제)

### C. 코드 영향 검색 — 3순위

**목표**: 백엔드/프론트의 sector 사용처 grep으로 검색

**검색 대상**:
- `tai-api`: `sector ==`, `'INDUSTRY'`, `'MANUFACTURING'`, `'BUILDING'`, `'CONSTRUCTION'`, `'COMMON'`, `'SPECIAL'`
- `tai-admin`: 같은 패턴
- 결과를 `docs/extraction/SECTOR_CODE_IMPACT_2026-05-07.md`로 정리

**판단**: 영향 범위 작으면 그날 수정, 크면 별도 작업지시서 작성 후 Cursor.

### D. master_rule_v2 스키마 doc 작성 — 4순위

**목표**: A/B/C 완료 후 4 테이블 정확한 DDL + 인덱스 + 제약

**산출물**:
- `docs/extraction/DESIGN_pipeline_5_master_rule_schema.md` — 스키마 정확한 명세
- 의미절 → master_rule 변환 알고리즘 doc
- 사용자 검토 후 Supabase migration

---

## 핵심 자료 (오늘 분석 결과)

### sector × 키워드 cross-applicability 매트릭스

```
| sector       | total  | 건축물 키워드 | 공장 키워드 | 건설 키워드 |
|--------------|--------|---------------|-------------|-------------|
| COMMON       | 46,726 | 0.9% (421)    | 3.2% (1506) | 0.9% (435)  |
| BUILDING     | 4,539  | 29.7% (자기)  | 0.9% (41)   | 2.6% (119)  |
| INDUSTRIAL   | 3,151  | 1.3% (40)     | 5.6% (자기) | 2.7% (84)   |
| CONSTRUCTION | 4,079  | 0.2% (10)     | 0.9% (35)   | 18.6% (자기)|
```

### 5요소 채움률 (본 적용)

```
Total            : 58,495
executor         : 68.8%
condition        : 38.0%
exception        :  0.02% (12건, 모집단 자체 적음)
cycle            : 11.4%
form             :  7.1%
if 셋 (조건+주어+행위) : 80.0%
미분류           :  1.20% (review 마크)
```

### content_type 분포

```
OBLIGATION   : 33,628
AUTHORITY    : 10,916
DEFINITION   :  6,473
DELEGATION   :  4,643
PROHIBITION  :  1,742
STATEMENT    :    391
미분류        :    702 (review 마크)
```

---

## 작업 원칙 (불변)

1. AI/LLM 호출 0% (정규식/키워드 사전 기반만)
2. 검증 없는 완료 선언 금지
3. 패턴 발견 → 룰 보강 → 재반복 (iterative refinement)
4. 정확함이 건수/비율보다 중요
5. ask_user_input_v0 사용 금지 (텍스트로 직접)
6. 200줄+ 파일은 GitHub MCP 직접 수정 금지 → Cursor 로컬
7. 비-OBLIGATION inherit는 needs_review로 마크 (silent failure 방지)
8. 의미절 출처 추적 가능 (FK), AI 임의판단 추적/차단

---

## 핵심 인프라 메모

- Project ID: `vwlahtguyggrhvslabax` (서울)
- Repo: `taiengineering/tai-admin`, branch main only
- 분해기 코드: `docs/extraction/scripts/decompose_v1.py` (v1.7.1, ~700줄)
- 본 적용 로그: `/tmp/decompose_full_v171_apply.log`
- 본 테이블: `semantic_clause` (58,495 rows, production ready)
- 백업 테이블: `semantic_clause_iter1` (1~2주 후 DROP 예정)

## 이전 핸드오프 문서

- `docs/extraction/HANDOFF_2026-05-05.md` — 5월 5일 작업 (분해기 v1.0~v1.4, KEC 완료, Phase1/2 완료)
- `docs/extraction/HANDOFF_2026-05-06_evening.md` — **본 문서** (의미절 v1.7.1 본 적용 + sector 표준화 분석)
