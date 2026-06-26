# WO-OPERATIONAL-INTEGRATION-001 — 기존 운영 Persist 재사용 (Execution)

**작성일:** 2026-06-26 | **상태:** 구현 완료 → **PR #112 리뷰 대기** (범위 a 확정)
**PR:** https://github.com/taiengineering/tai-api/pull/112  (branch `feat/from-instances-persist`)
**범위 고정:** factory_diagnosis_results → diagnosis_transform 까지. PDF/SaaS는 제외(별도 WO).

> 목표: 171을 **기존 운영 Persist**로 factory_diagnosis_results에 태워 diagnosis_transform이 읽게 한다.

---

## Boundary

```
Applicability 변경 NO  Data Contract 변경 NO  Architecture 변경 NO  Breaking NO
허용: 기존 Persist 재사용, 최소 배선 수정, 기존 함수 재사용
```

---

## 수정 파일 목록

```
routers/obligation_adapter.py  (단일 파일, PR #112)
  + _factory_sector(factory_id)            from-instances용 sector 공급(factories.sector, 폴백 INDUSTRIAL)
  + _persist_result_data(...)              기존 /persist 쓰기 블록 추출(동작 동일). /persist·/from-instances 공유
  ~ /persist                               쓰기 블록을 _persist_result_data로 교체(동작 동일)
  ~ /from-instances                        persist: bool=False 추가. true일 때만 기존 persist 재사용
```

새 persist/router/service/adapter 0. build_result_data·기존 쓰기 패턴 재사용. 기본 persist=false → 기존 동작 불변.

---

## 변경 Call Graph

```
Applicability
  ↓
obligation_instance
  ↓
Glue (obligation_instance_adapter)
  ↓
build_obligations_from_trigger_candidates  (171, 불변)
  ↓  [persist=true]
build_result_data (기존) → _persist_result_data (기존 쓰기 재사용)
  ↓
factory_diagnosis_results (is_latest=true)
  ↓
GET /diagnosis/transform/latest → diagnosis_transform → 171 읽음  ✅
```

---

## 실행 결과 / E2E 검증

```
[코드 계약 검증]
  build_result_data 출력 = {obligations, key_obligations, sector, rule_count, ...}
  diagnosis_transform._extract_obligations ← result_data["obligations"] 읽음
  ∴ persist 후 transform이 171 obligations를 읽는다(코드 근거).
[DB 검증] factories.sector(e9c56af6)=INDUSTRIAL.
[회귀] 171은 build_obligations_from_trigger_candidates 산출 불변 → 개수/verdict/reason/category/description 불변(저장만).
[live] 환경 네트워크 off → 직접 HTTP 호출 불가. 머지·배포 후 1회 호출로 런타임 확정.
```

### 머지 후 런타임 절차
```
1. PR #112 머지 → Railway 자동배포
2. POST /obligation-adapter/from-instances/{factory_id}?persist=true  → diagnosis_id 응답
3. GET /diagnosis/transform/latest/{factory_id}  → obligations 171 확인
```

---

## 제외 (별도 WO, 이번 완료조건 아님)

```
diagnosis_report PDF  → anonymous_diagnosis_results (별도 파이프)
SaaS 점검항목관리   → inspection_master (FK 0, 별도 파이프)
```

## 기존 속성 메모 (본 PR이 만든 게 아님)
```
diagnosis_transform._fetch_latest_row → created_by == user_id 권한 체크.
기존 /persist도 created_by 미설정(null) → 인증 사용자 조회 시 403 가능. 필요 시 별도 조치.
```

---

*WO-OPERATIONAL-INTEGRATION-001 — 범위 a. 171 → 기존 Persist 재사용 → factory_diagnosis_results → diagnosis_transform. PR #112 리뷰 대기.*
*PDF/SaaS 연결은 별도 WO. 하나의 WO에서 하나만 닫는다.*
