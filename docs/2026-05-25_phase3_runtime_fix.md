# Phase 3 — Runtime 고정 작업지시 v1.0

> 작성일: 2026-05-25
> 전제: Phase 1 흐름분석 완료 (engine_flow_map.md)
> 목표: 사용자-facing 진단 전체를 runtime compiler로 전환
> 원칙: 엔진 아키텍처 파일 절대 수정 금지 (compiler_core, deterministic_qa 등)

---

## 발견된 문제 3건

### P1. 진단 실행이 Legacy 엔진 사용
```
free-diagnosis.html
  → POST /diagnosis/run
  → diagnosis_integrated.py
  → legal_engine_svc + master_building_legal_rules
  → engine_version: "5.7.0"  ← LEGACY!
```

### P2. 결과 조회 엔드포인트 단절
```
free-diagnosis-result.html
  → GET /diagnosis/result/{token}
  → 엔드포인트 없음 → MOCK 폴백

paid-diagnosis-result.html
  → GET /diagnosis/paid-result/{token}
  → diagnosis_result_web.py에 구현됨
  → router_registry 미등록 → 404
```

### P3. Runtime 엔진이 진단과 분리되어 있음
```
/legal-engine/apply/{factory_id} → runtime (SaaS 전용)
compiler_core → runtime (관제/내부 전용)
diagnosis_runtime_projection.py → 파일만 존재, 미등록
```

---

## 작업 순서 (4단계)

### Step 1: router_registry 등록 누락 수정

**파일: `router_registry/diagnosis.py` 또는 `router_registry/public.py`**

추가할 모듈:
```python
{"module": "routers.diagnosis_result_web"},
{"module": "routers.diagnosis_runtime_projection"},
```

확인: 배포 후 `/health` 응답에서 해당 그룹 loaded 수 증가 확인

### Step 2: /diagnosis/run 를 runtime compiler로 전환

**파일: `routers/diagnosis_integrated.py`**

현재 흐름:
```python
# LEGACY 경로
from services.legal_engine_svc import run_diagnosis  # 또는 유사
result = run_diagnosis(input_data)  # engine_version="5.7.0"
```

변경 목표:
```python
# RUNTIME 경로
# 1. 이미 존재하는 runtime compiler 함수를 찾을 것
# 2. /legal-engine/apply/{factory_id} 또는 compiler_core에서 사용하는 함수 확인
# 3. 동일한 함수를 diagnosis_integrated에서 호출
# 4. engine_version = "v3.0-runtime-compiler" 고정
```

**실행 전 확인:**
- `routers/legal_engine.py`에서 `/legal-engine/apply` 엔드포인트가 호출하는 함수 확인
- `routers/compiler_core.py`에서 `evaluate-facility` 엔드포인트가 호출하는 함수 확인
- 두 경로 중 하나를 diagnosis_integrated에서 재사용

**주의: compiler_core.py, legal_engine.py 자체는 수정하지 않음.**
**diagnosis_integrated.py의 import와 호출만 변경.**

### Step 3: 결과 조회 엔드포인트 연결

**무료진단 결과:**

`free-diagnosis-result.html`이 호출하는 URL 확인:
- `GET /diagnosis/result/{token}` 이면 → 이 엔드포인트를 `diagnosis_result_web.py`에 추가
- 또는 FE URL을 `diagnosis_result_web.py`의 기존 엔드포인트에 맞춤

**유료진단 결과:**

`paid-diagnosis-result.html`의 토큰 파라미터 에러:
- FE에서 어떤 query param으로 토큰을 전달하는지 확인
- `diagnosis_result_web.py`의 해당 엔드포인트와 매칭
- registry 등록으로 해결 가능한지 확인

### Step 4: engine_version 고정

모든 진단 응답에서:
```python
engine_version = "v3.0-runtime-compiler"
```

DB 저장 시에도 동일 버전 기록.

---

## Legacy 격리 (코드 수정 후)

다음 파일들의 legacy 경로에 주석 추가:
```python
# LEGACY - ISOLATED: 구형 엔진 경로. runtime 전환 완료 후 제거 대상.
```

대상 파일 (Phase 1에서 식별됨):
- `routers/diagnosis.py` — step1~3 legacy 경로
- `routers/anonymous_diagnosis.py` — legacy 엔진 호출 부분
- `routers/legal_engine.py` — step1~3 legacy 엔드포인트

---

## 완료 기준

- [ ] `/health` 에서 diagnosis 그룹 loaded 수 증가 확인
- [ ] `curl POST /diagnosis/run` → engine_version: "v3.0-runtime-compiler" 반환
- [ ] `taieng.co.kr/free-diagnosis.html` → 진단 실행 → 결과 페이지로 정상 이동
- [ ] `taieng.co.kr/free-diagnosis-result.html?token=xxx` → 결과 정상 표시
- [ ] `taieng.co.kr/paid-diagnosis-result.html?token=xxx` → 결과 정상 표시
- [ ] legacy 경로에 ISOLATED 주석 표시 완료

## 배포

```bash
cd ~/tai-api
git add -A && git commit -m "fix: runtime engine migration Phase 3"
git push origin main
railway up
curl -X POST https://api.taieng.co.kr/cron/reload
```

## 주의사항

- `compiler_core.py`, `deterministic_qa.py`, `runtime_activation.py` 등 엔진 아키텍처 파일 절대 수정 금지
- 수정 대상: 라우터의 import/호출 경로, router_registry 등록, FE URL 매칭
- 20KB 초과 파일 수정 시 서비스 레이어 분리 규칙 준수
- `railway up` 후 반드시 `POST /cron/reload` 실행
