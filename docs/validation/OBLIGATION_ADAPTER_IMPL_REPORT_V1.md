# OBLIGATION ADAPTER IMPL REPORT V1
# WO-OBLIGATION-ADAPTER-IMPL-001

**작성일**: 2026-06-18
**성격**: B안 어댑터 구현 완료 보고.
**검증 기준**: 화성 제2공장 (C28, 280명)

---

## 구현 결과 (B안: Adapter 분리)

```
V4 (불변)
  ↓ evaluate() — verdict + evaluation_details
Adapter (신규)  ← V4 MATCH + 조건 레코드 조인 → obligations 변환
  ↓ result_data.obligations 호환 JSON
정제레이어 (불변) — diagnosis_transform.py
  ↓
결과페이지 (불변)
```

생성 파일 3종:
```
1. services/obligation_adapter_service.py  (변환 로직, FastAPI import 없음)
   - ACTION_TYPE_TO_CATEGORY 매핑 (정제레이어 CATEGORY_MAP 정합)
   - build_obligations_from_v4(v4_result, conditions_by_id)
   - 새 판단 없음: evaluation_result=='MATCH'만 통과

2. routers/obligation_adapter.py  (HTTP only)
   - GET /obligation-adapter/{factory_id}
   - V4 evaluate() 재사용 → 조건 조회 → 서비스 변환 → JSON

3. router_registry/diagnosis.py  (등록)
   - {"module": "routers.obligation_adapter"} 추가
```

---

## 불변 보존 확인

```
V4 (applicability_api.py / applicability_condition_service.py): 수정 0줄
정제레이어 (diagnosis_transform.py): 수정 0줄
Track A: 무영향
새 테이블: 생성 안 함
→ §8 검증 자산 100% 보존
```

---

## 검증 결과 (화성 제2공장, SQL 재현)

어댑터의 _build_obligation 로직을 SQL로 재현, MUST 8건 변환 확인:

| category | title | law_name | evidence | rule_type |
|---|---|---|---|---|
| 선임 | 관리감독자 지정 | 산업안전보건법 | 제16조 | DESIGNATION |
| 선임 | 안전관리자 (50~999명 1명) | 산업안전보건법 시행령 | 별표 3 | APPOINTMENT |
| 교육 | 정기 안전보건교육 실시 | 산업안전보건법 | 제29조 | EDUCATION |
| 교육 | 채용 시 안전보건교육 실시 | 산업안전보건법 | 제29조 | EDUCATION |
| 교육 | 작업내용 변경 시 교육 실시 | 산업안전보건법 | 제29조 | EDUCATION |
| 점검 | 일반건강진단 실시 | 산업안전보건법 | 제129조 | HEALTH_CHECK |
| 서류 | 위험성평가 실시 | 산업안전보건법 | 제36조 | RISK_ASSESSMENT |
| 서류 | 경보용 설비 설치 | 산업안전보건기준에 관한 규칙 | 제19조 | INSTALLATION |

```
8/8 변환 성공.
category 분류가 정제레이어 5종(선임/점검/신고/교육/서류)과 정합.
법령명/조문/조치문 누락 0건.
```

---

## 성공 기준

```
AD-01 MUST 8건 obligations 변환     → ✅ 8/8
AD-02 category 정제레이어 정합       → ✅ (선임2/교육3/점검1/서류2)
AD-03 V4 수정 0줄                   → ✅
AD-04 정제레이어 수정 0줄            → ✅
AD-05 새 테이블 0개                  → ✅
AD-06 evidence(법령근거) 누락 0건    → ✅
```

---

## 상태 전이 (CURRENT_PROJECT_STATE)

```
이전:
  Obligation Metadata: CONNECTED = NO
  V4: USER_VISIBLE = NO

현재 (이 WO 이후):
  Obligation Adapter: BUILT = YES / VERIFIED = YES(SQL재현)
                      / CONNECTED = YES(코드경로 존재)
                      / USER_VISIBLE = 미확인(배포+화면 연결 후)

남은 단계 (USER_VISIBLE 도달 위해):
  - Railway 배포 반영 후 실 API 호출 검증
  - 정제레이어/결과페이지가 /obligation-adapter 결과를
    result_data로 받아 렌더링하는 배선 (별도 WO)
```

---

## 미해결 (다음 판단, 차단 아님)

```
risk_level: 현재 MEDIUM 고정 (V4 미보유, 정제레이어 폴백과 동일)
  → 향후 법령별 위험도 부여 시 보강 (이번 범위 아님)

headline / warnings / roi / inspection_schedule:
  정제레이어가 자체 폴백 생성 (어댑터 책임 아님)

실 배포 호출 검증:
  이 WO는 변환 로직까지. Railway 배포 후 GET 호출은 다음 확인.
```

---

## 결론

```
B안 어댑터 구현 완료.

V4 검증 결과(MUST 8건)가 처음으로
정제레이어 호환 obligation 스키마로 변환되는
실제 코드 경로가 생겼다.

Layer 2(V4) → Layer 3(Obligation) 단절이
코드 레벨에서 연결됨 (CONNECTED 도달).

남은 것은 배포 반영 + 화면 배선 (USER_VISIBLE).
V4 불변 / 정제레이어 불변 / Track A 무영향으로 달성.
```
