# D단계 관찰 파이프라인 작업계획서

작성일: 2026-06-16  
근거 문서: `docs/2026-06-11_LEGAL_ENGINE_V4_LAYER_REDESIGN.md` (v2.1)  
구현 WO: `docs/2026-06-16_WO_D_PIPELINE_IMPL.md`

---

## ⚠️ 이 계획서의 목적

```
D-001~007은 진단엔진 완성이 아니다.
소비자 입력 → 결과까지 전 구간을 관찰 가능하게 만드는 것이다.

정확도 개선 ❌   새 엔진 제작 ❌   기존 엔진 교체 ❌
관찰 가능성 확보 ✅   trace 생성 ✅   Track A 병행 ✅
```

---

## 현재 DB 상태 (2026-06-16 실측)

| 테이블 | 건수 | 비고 |
|---|---|---|
| semantic_clause_fix (executor 있는 것) | 53,053 | D-001 입력 |
| legal_sieve_rule | 2,219 | D-002 입력 |
| law_sector_mapping | 366 | D-003 입력 |
| facility_applicability | 29,096+ | D-004A 입력 |

---

## 전체 순서 한눈에

```
[착수 전]
  0. 사전 체크 (이 문서 §1)

[구현]
  1. WO-D-001  SemanticClause Pipeline
  2. WO-D-002  Common Sieve Engine
  3. WO-D-003  Section Sieve
  4. WO-D-004A Track A Check Adapter
  5. WO-D-005  KSIC Signal Engine
  6. WO-D-006  Reverse Check Engine
  7. WO-D-007  Refinery

[완료 후]
  8. 전체 통합 체크 (이 문서 §9)
  9. Track A ↔ 파이프라인 diff
```

각 단계: 구현 → 단계 체크 → 통과 확인 → 다음 단계
단계 체크 미통과 시 다음 단계 진행 금지.

---

## §0. 착수 전 사전 체크

**시점**: Cursor에게 첫 지시 내리기 전
**담당**: 사장님 또는 Claude

### 0-1. Railway 배포 상태 확인
```
GET https://api.taieng.co.kr/health → 200 OK 확인
```
확인 안 되면 진행 금지. Railway 먼저 복구.

### 0-2. 기존 함수 존재 확인
Cursor에게 아래 4개 함수가 코드베이스에 존재하는지 확인 지시:
```
services/anonymous_factory_service.py 안에:
  - evaluate_single_factory
  - run_anonymous_diagnosis

services/facility_applicability_eval.py 안에:
  - evaluate_draft_for_facility

services/compiler_core_svc.py 안에:
  - fetch_compiler_candidates
```
4개 전부 존재 확인 후 착수. 하나라도 없으면 위치 확인 후 WO 수정.

### 0-3. schemas/ 디렉토리 존재 확인
```
tai-api/schemas/ 디렉토리가 있는지 확인
없으면 mkdir schemas/ 먼저
```

### 0-4. 체크 완료 선언
```
0-1 ✅ / 0-2 ✅ / 0-3 ✅ 확인 후 D-001 착수
```

---

## §1. WO-D-001: SemanticClause Pipeline

### 작업 내용
`semantic_clause_fix` + `law_article_part` + `law_article` + `law_master` JOIN →  
`SemanticClause` Pydantic 객체 + 조회 서비스 + API 엔드포인트

### Cursor 지시 핵심
```
생성 파일:
  schemas/semantic_clause_schema.py
  services/semantic_clause_service.py
  routers/semantic_pipeline_api.py

등록:
  router_registry/legal_engine.py 에
  {"module": "routers.semantic_pipeline_api"} 추가

금지:
  anonymous_diagnosis.py 수정 금지
  semantic_clause_fix 테이블 수정 금지
```

### D-001 완료 체크
**시점**: Cursor 구현 완료 후, D-002 착수 전

**체크 1 — API 응답 (기계)**
```bash
curl https://api.taieng.co.kr/semantic-pipeline/clauses?limit=5
```
기대값: `{"items": [...], "total": N}` (N > 50,000)

**체크 2 — 건수 확인 (기계)**
```bash
curl https://api.taieng.co.kr/semantic-pipeline/clauses/count
```
기대값: `{"total": 53053}` (±100 허용)

**체크 3 — 글읽기 (사람)**
응답 items 중 아무거나 3개 골라서:
- `executor_text` 값이 사람이 읽을 수 있는 주체 텍스트인가?
- `law_name`, `article_no`, `clause_text`가 의미 있게 채워졌는가?
- null/빈값이 executor_text에 없는가?

**체크 4 — 기존 엔진 무결성**
```bash
curl -X POST https://api.taieng.co.kr/anonymous-diagnosis \
  -d '{"site_kind":"manufacturing","scale":"small","workers":10,"region":""}'
```
기대값: 기존과 동일한 진단 결과 반환 (D-001 전후 동일해야 함)

**판정**: 체크 1~4 전부 통과 → D-002 착수

---

## §2. WO-D-002: Common Sieve Engine

### 작업 내용
`legal_sieve_rule` 2,219개를 SemanticClause에 적용 →  
`CandidateClause` (KEEP / DROP / PENDING) 생성

### Cursor 지시 핵심
```
생성 파일:
  schemas/candidate_clause_schema.py
  services/common_sieve_service.py
  routers/common_sieve_api.py

등록: router_registry/legal_engine.py

거름 로직 원칙:
  DROP = executor_text가 legal_sieve_rule의 DROP 값과 완전 일치
  KEEP = KEEP 값과 완전 일치
  PENDING = 어느 쪽도 아님 (소멸 금지)

금지:
  법 해석 기반 DROP 금지
  (예: "산안법이면 DROP", "소방법이면 KEEP" 같은 로직 절대 금지)
  admin_executor_llm_fix.py 수정 금지
```

### D-002 완료 체크
**시점**: Cursor 구현 완료 후, D-003 착수 전

**체크 1 — 배치 실행 (기계)**
```bash
curl -X POST https://api.taieng.co.kr/common-sieve/run
```
기대값: `{"keep": K, "drop": D, "pending": P}` (K+D+P = 53,053)

**체크 2 — 비율 확인 (기계)**
- DROP 비율이 90% 이상이면 이상 — 거름이 과도한 것
- PENDING 이 0이면 이상 — 미매칭이 없을 수 없음
- 이전 세션 기준: KEEP ≈ 6,475 / PENDING ≈ 7,496 / DROP = 나머지

**체크 3 — DROP 글읽기 (사람) ★ 핵심**
DROP된 결과 10개 샘플:
```bash
curl "https://api.taieng.co.kr/common-sieve/candidates?sieve_result=DROP&limit=10"
```
각 항목의 `executor_text`를 읽는다.
→ 기관명(고용노동부장관, 공단, 위원회 등)이거나 행위 조각(관한 자, 대한 자)이어야 함
→ "사업주" "건축주" "시행자" 같은 사업장 주체가 DROP되었다면 즉시 중단

**체크 4 — KEEP 글읽기 (사람) ★ 핵심**
KEEP된 결과 10개 샘플:
```bash
curl "https://api.taieng.co.kr/common-sieve/candidates?sieve_result=KEEP&limit=10"
```
각 항목의 `executor_text`가 사업주 계열 주체인지 확인.

**체크 5 — trace 확인 (기계)**
DROP 항목에 `sieve_rule_id`와 `sieve_reason`이 채워졌는지 확인.

**체크 6 — 기존 엔진 무결성** (§1과 동일 curl)

**판정**: 체크 3에서 사업주 계열이 DROP되면 즉시 중단 후 원인 분석.
전부 통과 → D-003 착수

---

## §3. WO-D-003: Section Sieve

### 작업 내용
CandidateClause(KEEP) → `law_sector_mapping` 대조 →  
산업/건설/건물 섹터 배정 → `SectionCandidateClause`

### Cursor 지시 핵심
```
생성 파일:
  schemas/section_candidate_schema.py
  services/section_sieve_service.py
  routers/section_sieve_api.py

등록: router_registry/legal_engine.py

원칙:
  law_sector_mapping에 없는 법령 = universal (전 섹터 통과, "가지고 감")
  SPECIAL_FACILITY 배정 절대 금지
  sector_source 필드 반드시 기록
```

### D-003 완료 체크
**시점**: Cursor 구현 완료 후, D-004A 착수 전

**체크 1 — 산업 섹터 필터 (기계)**
```bash
curl -X POST https://api.taieng.co.kr/section-sieve/run \
  -d '{"facility_sector": "INDUSTRIAL"}'
```
기대값: `{"total": N, "sector_source": {...}}` (N > 0)

**체크 2 — SPECIAL_FACILITY 0건 (기계)**
응답에 `SPECIAL_FACILITY` 배정 건수 = 0 확인.

**체크 3 — universal 법령 포함 확인 (기계)**
law_sector_mapping에 없는 법령의 절도 INDUSTRIAL 결과에 포함되는지 확인.
`sector_source = "universal"` 건수 > 0 이어야 함.

**체크 4 — 글읽기 (사람)**
INDUSTRIAL 결과 5개의 `law_name` 확인.
소방법, 산안법 계열이 섞여 나오는 것은 정상.
의료법, 특수교육법 등 명백히 다른 섹터 법령이 있다면 기록 (즉시 중단 아님, 관찰).

**판정**: 체크 1~3 통과 → D-004A 착수

---

## §4. WO-D-004A: Track A Check Adapter

### 작업 내용
`facility_applicability` 테이블 결과를 읽어서  
`CheckResult` 표준 객체로 변환하는 어댑터

### Cursor 지시 핵심
```
생성 파일:
  schemas/check_input_schema.py
  services/check_engine_adapter.py
  routers/check_adapter_api.py

등록: router_registry/legal_engine.py

★ 절대 금지:
  evaluate_single_factory 수정 금지
  evaluate_draft_for_facility 수정 금지
  SemanticClause → facility_applicability_eval 연결 시도 금지
  (binding_field 없어서 결과 0건 — 가짜 연결)

D-004A가 하는 일:
  facility_applicability 테이블에서 facility_id 기준으로 rows 읽기
  각 row를 CheckResult로 변환
  check_method = "track_a_facility_applicability" 기록
```

### D-004A 완료 체크
**시점**: Cursor 구현 완료 후, D-005 착수 전

**체크 1 — Track A 결과 읽기 (기계)**
테스트용 factory_id 하나로:
```bash
curl -X POST https://api.taieng.co.kr/check-adapter/run-track-a \
  -d '{"facility_id": "[테스트 factory_id]"}'
```
기대값: CheckResult 목록 반환

**체크 2 — 필드 확인 (기계)**
각 CheckResult에:
- `draft_id` 있음
- `applicability_status` = MATCH_CANDIDATE 또는 POSSIBLE_CANDIDATE
- `check_method` = "track_a_facility_applicability"
- `reason` 채워짐

**체크 3 — 글읽기 (사람) ★ 핵심**
CheckResult 5개의 `reason` 필드를 읽는다.
→ "binding_field XXX 조건 매칭" 같은 의미 있는 이유여야 함
→ "unknown" "None" ""이면 어댑터 로직 수정 필요

**체크 4 — evaluate_single_factory 미수정 확인 (기계)**
```bash
git diff HEAD~1 -- services/anonymous_factory_service.py
```
변경 없어야 함. 변경 있으면 즉시 revert.

**판정**: 전부 통과 → D-005 착수

---

## §5. WO-D-005: KSIC Signal Engine

### 작업 내용
`process_noun_match_stats`를 활용해 업종(KSIC) 기반 의무 신호 생성.  
기존 CheckResult에 보강 신호 추가 (제거 금지)

### Cursor 지시 핵심
```
생성 파일:
  schemas/ksic_signal_schema.py
  services/ksic_signal_service.py
  routers/ksic_signal_api.py

등록: router_registry/legal_engine.py

원칙:
  KSICSignal = 의무 추가용 신호 (제거 근거 사용 금지)
  KSICSignal 없어도 기존 CheckResult 유지
  signal_source 필드 반드시 기록
```

### D-005 완료 체크
**시점**: Cursor 구현 완료 후, D-006 착수 전

**체크 1 — 신호 생성 (기계)**
```bash
curl -X POST https://api.taieng.co.kr/ksic-signal/run \
  -d '{"facility_id": "[테스트 factory_id]", "clause_id": "[임의 clause_id]"}'
```
기대값: KSICSignal 또는 null

**체크 2 — 의무 감소 없음 (기계) ★ 핵심**
D-004A에서 나온 CheckResult 건수와 D-005 처리 후 건수 비교.
KSIC 처리 전후 의무 건수가 줄어서는 안 됨.

**체크 3 — signal_source 확인 (기계)**
KSICSignal 있는 경우 `signal_source` 필드 채워짐 확인.

**판정**: 체크 2 통과 (건수 감소 없음) → D-006 착수

---

## §6. WO-D-006: Reverse Check Engine

### 작업 내용
ObligationCandidate를 입력받아 "왜 포함됐는가" 경로를 역으로 재구성.  
순수 함수 — 네트워크 호출 없음.

### Cursor 지시 핵심
```
생성 파일:
  schemas/reverse_check_schema.py
  services/reverse_check_service.py
  routers/reverse_check_api.py

등록: router_registry/legal_engine.py

원칙:
  build_reverse_trace = 순수 함수 (DB 조회 없음)
  full_trace 필드에 경로 전체 JSON 직렬화
  law_article_url 형식: https://www.law.go.kr/법령/{law_name}/{article_no}
```

### D-006 완료 체크
**시점**: Cursor 구현 완료 후, D-007 착수 전

**체크 1 — 역추적 실행 (기계)**
D-004A 결과 중 하나를 ObligationCandidate로 조립해서:
```bash
curl -X POST https://api.taieng.co.kr/reverse-check/trace \
  -d '{...ObligationCandidate...}'
```
기대값: ReverseCheckResult 반환

**체크 2 — 필드 완전성 (기계)**
- `sieve_rule_matched` 있음
- `sector_assigned` 리스트 있음
- `check_reason` 채워짐
- `full_trace` JSON 직렬화됨
- `law_article_url` 형식 올바름

**체크 3 — 글읽기 (사람) ★ 핵심**
ReverseCheckResult 3개의 경로를 읽는다:
1. 어떤 거름룰로 KEEP됐는가 (`sieve_rule_matched`)
2. 어떤 섹터로 배정됐는가 (`sector_assigned`)
3. Track A에서 어떤 이유로 APPLICABLE이 됐는가 (`check_reason`)

→ 이 세 단계가 말이 되는 흐름인가? (논리적으로 일관되면 통과)

**판정**: 체크 3 글읽기 통과 → D-007 착수

---

## §7. WO-D-007: Refinery

### 작업 내용
ObligationCandidate + ReverseCheckResult →  
중복 제거 + 의무 문장 생성 → `StoredDiagnosisResult`

### Cursor 지시 핵심
```
생성 파일:
  schemas/stored_diagnosis_schema.py
  services/refinery_service.py
  routers/refinery_api.py

등록: router_registry/legal_engine.py

원칙:
  기존 emit_stored_diagnosis_result 수정 금지 (래핑 또는 병행만)
  기존 assemble_refinery_result 수정 금지
  obligations[].trace에 ReverseCheckResult 전체 포함
  pipeline_version = "WO-D-007-v1" 기록
  before_dedup / after_dedup 로그 출력
```

### D-007 완료 체크
**시점**: Cursor 구현 완료 후

**체크 1 — Refinery 실행 (기계)**
```bash
curl -X POST https://api.taieng.co.kr/refinery/run \
  -d '{"facility_id": "[테스트 factory_id]"}'
```
기대값: StoredDiagnosisResult 반환

**체크 2 — 필드 완전성 (기계)**
- `pipeline_version` = "WO-D-007-v1"
- `obligations` 리스트 있음
- 각 obligation에 `trace` 있음
- `total_count` > 0

**체크 3 — 중복 제거 로그 (기계)**
서버 로그에서 `before_dedup`, `after_dedup` 출력 확인.
before ≥ after 이어야 함.

**체크 4 — 전체 글읽기 (사람) ★ 핵심**
StoredDiagnosisResult의 `obligations` 전체를 읽는다:
- 의무 문장이 한국어로 의미 있게 생성됐는가?
- trace의 경로가 논리적으로 일관되는가?
- 명백히 이상한 의무(의료장소 접지 등)가 포함됐는가?
  → 포함됐다면 D-003 섹터 필터 문제 — 기록만 (즉시 중단 아님)

**체크 5 — 기존 엔진 무결성 최종 확인**
```bash
curl -X POST https://api.taieng.co.kr/anonymous-diagnosis \
  -d '{"site_kind":"manufacturing","scale":"small","workers":10,"region":""}'
```
기존과 동일한 결과 반환 확인.

**판정**: 전부 통과 → §8 전체 통합 체크

---

## §8. 파이프라인 상태 관찰 엔드포인트

D-007 완료 후 아래 엔드포인트도 구현 (별도 지시):

```bash
# 전체 단계별 건수 현황
GET /pipeline/status
기대값:
{
  "semantic": 53053,
  "common_sieve": {"keep": K, "drop": D, "pending": P},
  "section": {"INDUSTRIAL": N, "BUILDING": N, "CONSTRUCTION": N},
  "check_track_a": {"applicable": N, "unknown": N},
  "refinery": {"total_obligations": N}
}

# 특정 clause 전체 경로 추적
GET /pipeline/trace/{clause_id}

# 특정 사업장 전체 파이프라인 실행 (개발·검증용)
POST /pipeline/run/{facility_id}
```

---

## §9. 전체 통합 체크 (D-007 완료 후)

**시점**: D-007 단계 체크 통과 후

### 9-1. 파이프라인 상태 확인 (기계)
```bash
curl https://api.taieng.co.kr/pipeline/status
```
모든 단계 건수가 0이 아닌지 확인.

### 9-2. Track A ↔ 파이프라인 diff (기계 + 사람)

**테스트 사업장**: 제조업 50명 (선임 경계)

1. 기존 Track A 결과 얻기:
```bash
POST /anonymous-diagnosis
{"site_kind":"manufacturing","scale":"medium","workers":50,"region":""}
```

2. 새 파이프라인 결과 얻기:
```bash
POST /pipeline/run/{facility_id}
```

3. 두 결과의 의무 목록 비교:
- Track A에 있는데 파이프라인에 없는 것 → 누락 목록
- 파이프라인에 있는데 Track A에 없는 것 → 신규 감지 목록

4. 누락/신규 목록 글읽기 (사람):
→ 누락: 왜 빠졌는지 /pipeline/trace로 추적
→ 신규: 맞는 의무인지 원문 확인

### 9-3. 빈 입력 테스트 (기계)
입력값 없이 실행했을 때 시스템이 0으로 채우지 않고 UNKNOWN 처리하는지 확인.

### 9-4. 기존 엔진 최종 무결성 (기계)
```bash
POST /anonymous-diagnosis
{"site_kind":"construction","scale":"large","workers":100,"region":""}
```
D-001 착수 전과 동일한 결과 반환 확인.

### 9-5. Health 체크
```bash
GET /health → 200 OK
```

---

## §10. 체크 요약표

| WO | 기계 체크 | 글읽기 체크 | 핵심 판단 기준 |
|---|---|---|---|
| D-001 | API 응답 + 건수 | executor_text 3개 | 기존 anonymous-diagnosis 무결성 |
| D-002 | 건수 비율 + trace | DROP 10개 + KEEP 10개 ★ | 사업주 계열이 DROP되면 즉시 중단 |
| D-003 | SPECIAL_FACILITY=0 + universal>0 | law_name 5개 | 이상 법령 기록 (중단 아님) |
| D-004A | CheckResult 필드 + git diff | reason 5개 ★ | evaluate_single_factory 미수정 |
| D-005 | 의무 건수 감소 없음 ★ | — | KSIC 후 의무 줄면 즉시 중단 |
| D-006 | 필드 완전성 | 경로 3개 ★ | 3단계 흐름이 논리적인가 |
| D-007 | pipeline_version + dedup 로그 | obligations 전체 ★ | 기존 엔진 최종 무결성 |
| 통합 | pipeline/status + diff | 누락/신규 목록 ★★ | Track A와 파이프라인 gap 가시화 |

★ = 사람이 직접 읽어야 하는 체크  
★★ = 가장 중요한 최종 체크

---

## §11. 중단 조건

아래 중 하나라도 발생하면 즉시 중단하고 원인 분석:

```
1. /health 200 실패
2. 기존 anonymous-diagnosis 결과가 달라짐
3. D-002: 사업주 계열(사업주, 건축주, 시행자 등)이 DROP됨
4. D-004A: evaluate_single_factory 코드 변경됨
5. D-005: KSIC 처리 후 의무 건수 감소
6. 어떤 단계에서도 SemanticClause → facility_applicability_eval 연결 시도 발견
```

---

## §12. 다음 단계 (D-001~007 완료 후)

```
1. 통합 체크 §9 완료 리포트 작성
2. Track A ↔ 파이프라인 gap 분석 문서
3. WO-APPENDIX-COLLECT-001 착수 (별표 수집)
4. WO-LEG-Compiler-003 GPT 발행 (Actor Resolution)
5. WO-D-004B 별도 설계 승인 요청
```

---

## 참고: 테스트용 factory_id 얻는 법

```bash
# Supabase에서 테스트용 ANON_TEMP factory_id 조회
SELECT id, sector, employee_count
FROM factories
WHERE status_code = 'ANON_TEMP'
ORDER BY created_at DESC
LIMIT 5;
```
단, ANON_TEMP는 cleanup 후 삭제됨 — 테스트용 고정 factory row를 별도 생성해서 사용 권장.
