# HANDOFF FINAL 2026-05-07 — 통합 핸드오프

> 오늘(2026-05-07) 진행한 모든 작업의 통합 기록.
>
> **전체 진행 흐름**: sector 표준화 → 의미절 다중매핑 → master_rule_v2 5 테이블 → 의미절 v1.8 보강 시작

---

## 작업 흐름 요약

```
오전 ~ 오후
├─ A. 366 법령 sectors[] 자동 매핑 + 외부 검색 검증
├─ B. DB 운영 테이블 15개 sector 표준화 (한글/소문자/MANUFACTURING/INDUSTRY/ALL → 4 표준)
├─ C. KOSHA industry_category 분리 (sector 의미 차원 분리)
├─ D. sector 무결성 전수검사 (INVALID 0 / MISMATCH 0)
├─ E. semantic_clause.sectors[] 다중매핑 컬럼 추가 + 32,525건 다중매핑
└─ F. industrial_accident_precedents 849건 자동 분류

저녁 ~ 밤
├─ G. master_rule_v2 테이블 생성 (Phase A — 44 컬럼 + 12 인덱스 + 7 CHECK + 4 FK)
├─ H. master_rule_v2 객체화 (executor/condition/exception/relation 4 부속 테이블)
├─ I. obligation_category → action_category_code (13 표준 통일)
├─ J. sample 20건 검증 — 의미절 quality 문제 발견
├─ K. NULL executor inherit 가능성 검증 (article 단위 83.1%)
├─ L. 분해기 v1.8 patch 작업지시서 (Cursor 작업 대기)
└─ M. semantic_clause.recipient_text 컬럼 추가 (DB 사전)
```

---

## DB 변경 종합 (16가지)

### sector 표준화 (1~13)

| # | 작업 | 결과 |
|---|---|---|
| 1 | 366 법령 → sectors[] 자동 매핑 | HIGH 331 / MEDIUM 28 / INACTIVE 7 |
| 2 | 외부 검색 검증 5 그룹 | 다중이용업소·재난구호·농어촌전기 등 |
| 3 | sector 표준 통일 (system_codes) | 4 sector + 한글 라벨 (sector_label) |
| 4 | factories.sector 통일 | INDUSTRY → INDUSTRIAL (15 rows) |
| 5 | law_sector_mapping 테이블 생성 | 366 법령 INSERT |
| 6 | DB 운영 테이블 일괄 마이그레이션 (15 테이블) | 한글/소문자/MANUFACTURING/INDUSTRY/ALL → 표준 |
| 7 | KOSHA industry_category 분리 | sector → industry_category |
| 8 | sector 무결성 전수검사 | INVALID 0 / MISMATCH 0 |
| 9 | semantic_clause COMMON 17,191건 정확한 sector로 갱신 | SPECIAL_FACILITY 13,504 / INDUSTRIAL 3,402 / BUILDING 285 |
| 10 | industrial_accident_precedents 849건 자동 분류 | NULL → 100% 채움 |
| 11 | CHECK 제약 13 테이블 추가 | 미래 invalid 차단 |
| 12 | semantic_clause.sectors text[] 컬럼 추가 | **다중매핑 완료, 32,525건 공용** |
| 13 | semantic_clause_iter1 동기화 | 본 + 백업 일치 |

### master_rule_v2 + Phase B 사전 (14~16)

| # | 작업 | 결과 |
|---|---|---|
| 14 | **master_rule_v2 메인 테이블 생성** | 43 컬럼 + 12 인덱스 + 7 CHECK + 4 FK |
| 15 | **master_rule_v2 4 부속 테이블 생성** (객체화) | executor / condition / exception / relation |
| 16 | semantic_clause.recipient_text 컬럼 추가 | v1.8 분해기 사전 |

---

## 핵심 데이터 통계 (현재)

### 의미절 sectors[] 다중매핑 분포 (58,495)

| 패턴 | 건수 | 비율 |
|---|---|---|
| 단일 sector | 25,809 | 44.1% |
| 2 sectors (공용) | 21,309 | 36.4% |
| 3 sectors (공용) | 11,216 | 19.2% |
| NULL (INACTIVE) | 161 | 0.3% |

**다중 매핑 32,525건 (55.6%)**

### sector별 적용 의미절 (다중 unnest)

| sector | 적용 의미절 |
|---|---|
| BUILDING | 30,314 |
| INDUSTRIAL | 29,955 |
| CONSTRUCTION | 28,302 |
| SPECIAL_FACILITY (비활성) | 13,504 |

### 의미절 quality 현황 (v1.7.1 기준)

| 지표 | 현재 | v1.8 목표 |
|---|---|---|
| executor 채움률 | 76% | >90% |
| 가짜 executor | 3,224건 | 0건 |
| recipient 채움률 | 0% | >70% |
| Article inherit | 0건 | ~9,000건 |

---

## sector 표준 (확정)

### 4 활성 sector

| 코드 | 한글 | 의미 |
|---|---|---|
| BUILDING | 건물 | 건축법, 화재안전, 시설안전 |
| INDUSTRIAL | 공장 | 제조업, 화학물질, 위험물 |
| CONSTRUCTION | 건설 | 건설안전법, KCSC |
| SPECIAL_FACILITY | 특수시설 | 의료/학교/철도 등 (비활성) |

### 임시 표기

| 코드 | 의미 |
|---|---|
| COMMON | 단일 sector 컬럼 한계 임시 표기. sectors[] 도입 후 정리 예정 |
| NULL | 사업장 의무 아님 (INACTIVE: 자연재난구호/농어촌전기/정부조직) |

---

## master_rule_v2 5 테이블 구조

```
master_rule_v2 (메인 룰, 43 컬럼)
    │ 식별 + 출처 (source_clause_id FK)
    │ when_* / what_* / how_* / why_* / sectors[] / scope_*
    │ action_category_code (13 표준)
    │ generation_method / generation_confidence / status / needs_review
    │
    ├──→ master_rule_executor (행위자/수신자/대체, 1:N)
    │     role: EXECUTOR / RECIPIENT / ALTERNATIVE_EXECUTOR
    │
    ├──→ master_rule_condition (조건 if, 1:N)
    │
    ├──→ master_rule_exception (예외 but/다만, 1:N)
    │
    └──→ master_rule_relation (룰 간 관계, 다대다)
          relation_type: EXCEPTION / CLARIFICATION / DETAIL / ALTERNATIVE / SUPERSEDES
```

**현재 5 테이블 모두 0 rows** (Phase B 의미절 보강 후 변환 대기).

---

## 4계층 흐름 진행도

```
[Layer 1] semantic_clause (58,495)         ← 🔄 v1.8 보강 작업 중 (Cursor)
              │
              │ Phase B (의미절 → master_rule_v2 자동 변환)
              ▼
[Layer 2] master_rule_v2 (5 테이블, 0 rows) ← ✅ Phase A 완료, Phase B 대기
              │
              │ 법령엔진 v2 (Phase E, 사업장 매칭)
              ▼
[Layer 3] inspection_sets (324)            ← 🟡 Phase D 대기 (4가지 세팅 컬럼)
              │
              │ 안전관리자 4가지 세팅 후
              ▼
[Layer 4] work_schedules (0)              ← ✅ 인프라 준비됨
```

---

## 핵심 의사결정 기록

### 1. sector 표기 — 4 표준 + 임시 COMMON

배열(sectors[])이 정확. 단일 컬럼은 호환성 위해 유지.

### 2. KOSHA industry_category 분리

KOSHA의 sector(MANUFACTURING/SERVICE/COMMON)는 우리 사업장 sector와 다른 차원. 컬럼명 분리.

### 3. master_rule_v2 객체화 (배열 거부)

사용자 결정: "배열은 순서/혼동 위험 → 개별 컬럼 + 객체화" → 4 부속 테이블 분리.

### 4. obligation_category → action_category_code (13 표준)

사용자 결정: "8개는 이전 산물 → 13 표준 채택". `system_codes.action_category` (체계구축/위험성평가/교육·훈련/점검·진단/측정/보고·신고/설치·비치/기록·보존/알림·고지/조치·실시/작업방법/승인·인가/보호) 사용.

### 5. 의미절 v1.8 보강 우선

사용자 결정: "의미절이 완벽해질 때까지 의미절 작업만". master_rule_v2 자동 변환 진입 보류, 분해기 v1.8 보강 후 진행.

### 6. v1.8 옵션 B 채택

inherit + FAKE_EXECUTOR 필터 + recipient 추출 동시 보강.

### 7. Article 단위 inherit 검증

사용자 통찰: "주어 없으면 상단에 존재할 확률 높음". 검증 결과 83.1% (NULL 10,951건 중 9,095건). v1.8 핵심 보강.

---

## v1.8 보강 작업 명세 (Cursor 대기)

### 7가지 패치

1. FAKE_EXECUTOR_PATTERNS — 가짜 주어 정규식 필터
2. extract_executor_text() 정정 — 가짜 검사 추가
3. NO_INHERIT_PATTERNS — 위임/수범 조항 inherit 금지
4. paragraph 단위 inherit (1차)
5. article 단위 inherit (post-processing)
6. recipient_text 추출 (`~에게/~로`)
7. decomposition_version v1.8

### 작업 흐름

```
1. DB ALTER recipient_text 컬럼 (✅ 완료)
2. decompose_v1.py 수정 (Cursor) — ~700줄 → ~900줄
3. dry-run sample 200건 (stratified)
4. 정확도 측정 (5개 SQL 검증)
5. 정확도 90% 미만이면 v1.9 보강 (iterative)
6. 통과 시 본 적용 (iter1 truncate + 재추출)
7. iter1 → 본 동기화
8. 무결성 재검증 (사용자 지시) → 새 문제점 발견
```

---

## Phase B~F 다음 작업 (의미절 v1.8 통과 후)

### Phase B (재진입) — 의미절 → master_rule_v2 자동 변환

`docs/extraction/scripts/convert_clause_to_rule.py`:
- 7단계 알고리즘 (DESIGN_master_rule_v2_2026-05-07.md 참조)
- 예상 ~46,000건 변환 (VALIDATED ~30K, DRAFT ~16K)

### Phase C — Cursor 작업 3개 실행

| 파일 | 영향 |
|---|---|
| CURSOR_TASK_2026-05-07_kosha_industry_category.md | kosha_collect.py 1 파일 |
| CURSOR_TASK_2026-05-07_api_sector.md | tai-api 20 파일 |
| CURSOR_TASK_2026-05-07_admin_sector.md | tai-admin 15 파일 |

### Phase D — inspection_sets 4가지 세팅 컬럼

```sql
ALTER TABLE inspection_sets ADD COLUMN is_when_set/is_who_set/is_what_set/is_how_set BOOLEAN;
ALTER TABLE inspection_sets ADD COLUMN is_schedule_ready BOOLEAN GENERATED ALWAYS AS (...);
```

### Phase E — 법령엔진 API v2

`tai-api/routers/legal_engine_v2.py`:
- `/legal-engine/evaluate?factory_id=X` — 적용 룰 추출
- `/legal-engine/sync-inspection-sets?factory_id=X`

### Phase F — 점검항목관리 페이지 연동

`safe.taieng.co.kr/html/horizontal-menu-template/inspection-anchor` master_rule_v2 기반 갱신.

---

## 작업 원칙 (불변)

1. **AI/LLM 호출 0%** — 정규식/키워드 사전만
2. **검증 없는 완료 선언 금지**
3. **패턴 발견 → 룰 보강 → 재반복** (iterative refinement)
4. **정확함이 건수/비율보다 중요**
5. **ask_user_input_v0 사용 금지** (텍스트로 직접)
6. **200줄+ 파일은 GitHub MCP 직접 수정 금지** → Cursor 로컬
7. **비-OBLIGATION inherit는 needs_review로 마크** (silent failure 방지)
8. **의미절 출처 추적 가능** (FK), AI 임의판단 추적/차단

---

## 핵심 인프라 메모

- Project ID: `vwlahtguyggrhvslabax` (서울)
- Repo: `taiengineering/tai-admin`, `taiengineering/tai-api` (모두 main only)
- 의미절: `semantic_clause` (58,495 rows + sectors[] + recipient_text)
- 백업: `semantic_clause_iter1` (본 테이블과 동기화)
- sector 표준: `system_codes.sector` (4) + `system_codes.sector_label` (한글)
- 매핑: `law_sector_mapping` (366 법령)
- 분해기: `docs/extraction/scripts/decompose_v1.py` (v1.7.1, v1.8 patch 대기)
- master_rule_v2 + 4 부속 테이블: 5 테이블 생성 완료, 0 rows

---

## 오늘 push된 모든 문서 (12개)

```
docs/extraction/
├── HANDOFF_2026-05-06_evening.md           ← 어제 핸드오프
├── LAW_SECTOR_MAPPING_2026-05-07.md        ← 366 법령 sector 매핑
├── SECTOR_CODE_IMPACT_2026-05-07.md        ← 코드 영향 분석
├── CURSOR_TASK_2026-05-07_api_sector.md    ← tai-api 작업지시서
├── CURSOR_TASK_2026-05-07_admin_sector.md  ← tai-admin 작업지시서
├── CURSOR_TASK_2026-05-07_kosha_industry_category.md  ← KOSHA rename
├── SECTOR_INTEGRITY_VERIFICATION_2026-05-07.md  ← 무결성 전수검사
├── SEMANTIC_CLAUSE_SECTORS_ARRAY_2026-05-07.md  ← 의미절 sectors[] 다중매핑
├── DESIGN_master_rule_v2_2026-05-07.md     ← master_rule_v2 설계
├── PHASE_A_COMPLETE_2026-05-07.md          ← Phase A 완료
├── CURSOR_TASK_2026-05-07_decompose_v18.md ← v1.8 patch 작업지시서
├── PHASE_B_START_2026-05-07.md             ← Phase B 시작
├── HANDOFF_2026-05-07.md                   ← 1차 핸드오프
└── HANDOFF_FINAL_2026-05-07.md             ← 본 통합 핸드오프
```

---

## 다음 세션 시작 방식

새 세션에서 다음 프롬프트 사용:
- `docs/extraction/NEXT_SESSION_PROMPT_2026-05-07.md` 참조
- 또는 "어제 통합 핸드오프 보고 시작" + 현재 단계 명시

---

## 이전 핸드오프 시리즈

- `HANDOFF_2026-05-05.md` — 분해기 v1.0~v1.4, KEC 완료, Phase1/2 완료
- `HANDOFF_2026-05-06_evening.md` — 의미절 v1.7.1 본 적용 + sector 표준화 분석 시작
- `HANDOFF_2026-05-07.md` — sector 표준화 + 다중매핑 + master_rule_v2 Phase A
- `HANDOFF_FINAL_2026-05-07.md` — **본 문서** (오늘 작업 통합)
