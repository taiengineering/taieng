# 법령엔진 Runtime 전환 작업지시 v1.0

> 작성일: 2026-05-25
> 목표: 입력→진단→결과 전체 흐름을 runtime 기반 법령엔진으로 고정, 과거 잔재 격리
> 범위: 법령엔진 결과 표시까지 (점검항목 매핑은 후속 작업)

---

## 1. 현재 문제

구형 엔진과 runtime 엔진이 혼재되어 있음:
- inspection_set_items: 5,184개 → 16개 범용 템플릿 반복 (구형 엔진이 생성)
- runtime_checklist_item: 802개 → 법령 특화 항목, APPROVED_BY_HUMAN (runtime 엔진 결과)
- runtime_inspection_item_bridge: 0건 → runtime→inspection 연결 끊김
- 프론트엔드 진단결과 페이지가 구형/신형 결과를 혼용

## 2. 대상 파일 분석 (Cursor에서 수행)

### 2.1 진단 흐름 추적 — 각 파일을 열고 아래 질문에 답할 것

**프론트엔드 입력 (taieng 레포)**
- `nexas/free-diagnosis.html` (53KB) — 어떤 API를 호출하는가?
- `nexas/free-diagnosis-result.html` (39KB) — 어떤 API에서 결과를 읽는가?
- `nexas/paid-diagnosis-result.html` (41KB) — 어떤 API에서 결과를 읽는가? (토큰 에러 원인)

**진단 API 라우터 (tai-api 레포, router_registry/diagnosis.py)**
```
routers/diagnosis.py
routers/diagnosis_engine.py       ← legacy? runtime?
routers/diagnosis_integrated.py   ← legacy? runtime?
routers/diagnosis_autofill.py
routers/diagnosis_fields.py
routers/diagnosis_report.py
routers/diagnosis_proposal.py
routers/diagnosis_roi.py
routers/diagnosis_transform.py
routers/diagnosis_plan_recommend.py
routers/saas_setup.py
```

**법령엔진 라우터 (tai-api 레포, router_registry/legal_engine.py)**
```
routers/legal_engine.py           ← 77KB! 구형+신형 혼재 가능
routers/compiler_core.py          ← runtime compiler 핵심
routers/runtime_activation.py     ← runtime 활성화
routers/runtime_evaluator_api.py  ← runtime 평가
```

**공개 API (router_registry/public.py)**
```
routers/anonymous_diagnosis.py    ← 무료/유료 진단 진입점
routers/diagnosis_result_web.py   ← 결과 웹 표시
routers/diagnosis_runtime_projection.py ← runtime projection
```

### 2.2 각 파일에서 확인할 것

1. `import` 문에서 어떤 엔진 모듈을 사용하는가?
   - `services/compiler/` → runtime 엔진
   - `services/legal_engine/` → 구형 가능성
   - `engine_version` 문자열 확인

2. DB 테이블 접근:
   - `anonymous_diagnosis_results` → 무료/유료 진단
   - `factory_diagnosis_results` → SaaS 진단
   - `diagnosis_session` → 진단 세션
   - 어떤 필드에 결과를 저장하는가? (partial_result vs full_result)

3. 엔진 호출 함수:
   - `compile()` / `run_compiler()` → runtime
   - `diagnose()` / `run_diagnosis()` → 구형 가능성
   - `v3.0-runtime-compiler` 버전 문자열 사용 여부

## 3. 작업 순서

### Phase 1: 흐름도 작성 (분석만, 수정 없음)

각 파일을 읽고 아래 형식으로 흐름도 작성:

```
[프론트엔드] free-diagnosis.html
  → POST /api/v1/anonymous-diagnosis/execute
  → [라우터] anonymous_diagnosis.py :: execute_diagnosis()
  → [엔진] services/compiler/runtime_compiler.py :: compile()
  → [DB] anonymous_diagnosis_results.full_result에 저장
  → [응답] {partial_result: ..., full_result: ...}

[프론트엔드] free-diagnosis-result.html
  → GET /api/v1/diagnosis-result-web/{token}
  → [라우터] diagnosis_result_web.py :: get_result()
  → [DB] anonymous_diagnosis_results WHERE public_token = {token}
  → [응답] partial_result (무료) 또는 full_result (유료)
```

### Phase 2: Legacy vs Runtime 분류

흐름도 완성 후 각 구간을 분류:
- ✅ RUNTIME: 이미 runtime compiler 사용 중
- ❌ LEGACY: 구형 엔진 사용 중 → 전환 필요
- ⚠️ MIXED: 조건부로 두 엔진 분기 → runtime으로 고정 필요

### Phase 3: Runtime 고정 (코드 수정)

주의: 엔진 아키텍처 파일(compiler_core, deterministic_qa 등)은 절대 수정하지 않음.
라우터의 호출 경로만 수정.

- LEGACY 구간 → runtime 호출로 교체
- MIXED 구간 → legacy 분기 제거, runtime만 남김
- `engine_version` → `v3.0-runtime-compiler` 고정

### Phase 4: Legacy 격리

- 구형 엔진을 직접 호출하는 라우터 식별
- registry에서 제거하지 않되, `# LEGACY - ISOLATED` 주석 표시
- 향후 제거 대상으로 분류

## 4. DB 현황 참조

| 테이블 | 건수 | 엔진 | 상태 |
|--------|------|------|------|
| anonymous_diagnosis_results | 2 | v3.0-runtime-compiler | ✅ runtime |
| factory_diagnosis_results | 0 | - | 비어있음 |
| runtime_checklist_item | 802 | runtime | ✅ APPROVED |
| inspection_set_items | 5,184 | 구형 | ❌ 범용 템플릿 |
| runtime_inspection_bridge | 324 | runtime | ⚠️ schema_id NULL |
| runtime_inspection_item_bridge | 0 | - | ❌ 비어있음 |
| master_rule_v2 | 58,495 | runtime | ✅ 핵심 데이터 |
| semantic_clause | 160,372 | runtime | ✅ |

## 5. 작업 원칙

- 엔진 아키텍처 파일(GPT 영역) 절대 수정 금지
- 라우터의 호출 경로, import, DB 저장 경로만 수정
- 서비스 레이어 분리 규칙 준수 (20KB+ 파일은 분리)
- 수정 전후 `/health` 200 유지 확인
- 수정 후 `railway up` + `POST /cron/reload` 필수

## 6. 완료 기준

- [ ] free-diagnosis.html → runtime 엔진 결과 정상 표시
- [ ] free-diagnosis-result.html → runtime 엔진 결과 정상 표시
- [ ] paid-diagnosis-result.html → 토큰 에러 해결, runtime 결과 표시
- [ ] 모든 진단 API가 `engine_version: v3.0-runtime-compiler` 반환
- [ ] legacy 엔진 직접 호출 경로 0건
- [ ] 흐름도 문서 작성 완료 → `taieng/docs/2026-05-25_engine_flow_map.md`
