# USER VISIBLE BRIDGE IMPL REPORT V2
# WO-USER-VISIBLE-BRIDGE-IMPL-002

**작성일**: 2026-06-19
**성격**: Track A 마지막 저장 배선 구현 + 검증 완료.
**검증 기준**: 화성 제2공장 (C28, 280명, factory_id=e9c56af6)

---

## 결론 먼저

```
USER_VISIBLE 체인의 마지막 1칸 연결 완료.

V4 → Adapter → factory_diagnosis_results → diagnosis_transform → 화면
                        ↑ 이 칸이 비어있었음 → 이제 채워짐

화성 제2공장 MUST 8건이 factory_diagnosis_results에 저장되고
transform_latest(factory_id) 경로로 전부 읽히는 것을 실측 확인.
```

---

## 구현 내용

```
1. services/obligation_adapter_service.py v1.1.0
   + build_result_data(adapter_result, v4_result)
     → 어댑터 obligations를 factory_diagnosis_results.result_data 스키마로 조립
     → 정제레이어가 읽는 키(obligations/key_obligations/sector/rule_count) 포함
   + _build_obligation에 law_article 필드 추가 (정제레이어 law_article 읽기 정합)
   기존 함수 불변

2. routers/obligation_adapter.py v1.1.1
   + POST /obligation-adapter/{factory_id}/persist
     → V4 평가 → 어댑터 변환 → factory_diagnosis_results INSERT (is_latest 토글)
   + SCHEMA_VERSION="v4adapt" (varchar(10) 한계 준수)
   기존 GET 엔드포인트 불변
```

---

## 검증 결과 (SQL 재현, 화성 제2공장)

### UV-08: factory_diagnosis_results 생성 성공 ✅
```
INSERT 성공: diagnosis_id=216fd7b0-be39-40e2-95f9-b5cc30b3c419
factory_id=e9c56af6, sector=INDUSTRIAL, rule_count=8, is_latest=true
result_data.obligations 길이=8
```

### UV-09: transform_latest 반환 성공 ✅
```
transform_latest 재현 (factory_id로 최신 결과 조회 → obligations 추출):
factory_id=e9c56af6, is_latest=true → obligations 8건 전부 반환
```

### UV-10: MUST 8건 확인 ✅
```
선임: 관리감독자 지정 / 안전관리자 선임
교육: 정기교육 / 채용교육 / 작업변경교육
점검: 일반건강진단
서류: 위험성평가 / 경보설비
= 8건
```

### UV-11: law_name 누락 0건 ✅
```
산업안전보건법(6) / 산업안전보건법 시행령(1) / 산업안전보건기준에 관한 규칙(1)
전부 채워짐
```

### UV-12: action_text 누락 0건 ✅
```
8건 전부 description=action_text 채워짐
```

---

## 검증된 전체 체인 (화성 제2공장)

```
V4 evaluate(e9c56af6)
  → MATCH 8건 (§8 검증 완료분)
      ↓
Adapter build_obligations_from_v4 + build_result_data
  → result_data.obligations 8건
      ↓
factory_diagnosis_results INSERT (is_latest=true)   ← 새로 채운 칸
  → diagnosis_id=216fd7b0...
      ↓
diagnosis_transform _fetch_latest_row + _extract_obligations
  → obligations 8건 반환 (category/title/law_name/law_article/evidence 정합)
      ↓
화면 (정제레이어 응답 그대로)
```

---

## 상태 전이 (CURRENT_PROJECT_STATE)

```
이전:
  factory_diagnosis_results 화성 결과: 0건
  Obligation Adapter: CONNECTED 부분 / USER_VISIBLE NO

현재:
  factory_diagnosis_results 화성 결과: 1건 (obligations 8건, is_latest)
  V4 → Adapter → factory_diagnosis_results → transform: CONNECTED ✅
  USER_VISIBLE: 데이터·경로 검증 완료 (실 배포 호출 확인만 남음)
```

---

## 발견·수정한 이슈 (정직 기록)

```
이슈: factory_diagnosis_results.schema_version = varchar(10)
  처음 코드값 "v4_adapter_v1"(13자) → INSERT 시 22001 에러
  → SQL 검증 중 즉시 발견
  → 코드값 "v4adapt"(7자)로 수정 (v1.1.1)
  → 추정으로 넘어가지 않고 컬럼 한계 실측 후 정정
```

---

## 원칙 준수 확인

```
V4 (applicability_api / applicability_condition_service): 수정 0줄 ✅
정제레이어 (diagnosis_transform): 수정 0줄 ✅
결과페이지 (diagnosis_result_web): 수정 0줄 ✅
익명 진단 트랙 (anonymous_diagnosis_results): 손대지 않음 ✅
새 Adapter / 새 계약 분석: 없음 ✅
Construction / Building: 손대지 않음 ✅
신규 = build_result_data 함수 + persist 엔드포인트 + 화성 결과 1건
```

---

## 남은 단계 (USER_VISIBLE 최종 확정)

```
이번 WO: 데이터·경로를 SQL로 검증 완료 (8/8, 누락 0).

최종 확정에 남은 것 (배포 의존, 코드 외):
  Railway 배포 반영 후
    POST /obligation-adapter/e9c56af6.../persist 실 호출
    GET /diagnosis/transform/latest/e9c56af6... 실 응답 확인
  → 코드·데이터는 준비됨. 실 HTTP 왕복만 남음.
```

---

## 결론

```
완료 기준 달성:
  화성 제2공장 기준 V4 결과가
  factory_diagnosis_results → diagnosis_transform까지 도달한다. ✅

UV-08 ~ UV-12 전부 PASS.

지금까지의 모든 검증
(Phase 1~4, §8 8/8, Golden Case, V4 INDUSTRIAL 100%, Adapter)이
처음으로 "사용자가 읽는 데이터 경로"까지 연결됐다.

프로젝트 상태:
  USER_VISIBLE 직전 → 실질적으로 USER_VISIBLE 검증만 남음.
  (데이터·경로 검증 완료, 실 배포 HTTP 왕복만 잔여)
```
