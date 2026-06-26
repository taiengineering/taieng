# WO-OPERATIONAL-VERIFY-001 — 운영 Persist 실실행 검증보고서 (Final Verification)

**일시:** 2026-06-26 | **방법:** 실호출(대표님) + DB 직독(Supabase MCP). 코드가 아닌 실행 결과로 증명.
**대상:** factory e9c56af6-5de7-487d-bd2e-0d452291a562 (INDUSTRIAL)
**PR:** #112 머지 완료 (main `85d3627b`, squash) → Railway 배포 반영 확인.

---

## TASK-001 — 머지 + 배포
```
PR #112 squash 머지 → main 85d3627b → Railway 자동배포.
배포 반영 근거: 응답에 persisted/diagnosis_id 필드 등장(구버전엔 없음).
```

## TASK-002/003 — 실호출 응답
```
POST /obligation-adapter/from-instances/e9c56af6-...?persist=true

  status            ok
  candidate_count   171
  obligation_count  171
  verdict           APPLICABLE
  persisted         true
  diagnosis_id      0b43c1e1-b25b-48f0-beb6-e7d9953e9372
  execution_time    total_ms 1456 (fetch 555 / adapter 0)
```

## TASK-004 — DB 직독 (factory_diagnosis_results)
```
id                0b43c1e1-b25b-48f0-beb6-e7d9953e9372   (신규 Row ✓)
created_at        2026-06-26 06:10:07Z
factory_id        e9c56af6-...   sector INDUSTRIAL
input_source      FROM_INSTANCES_OBLIGATION_INSTANCE     (우리 persist 배선 경유 ✓)
schema_version    v4adapt        is_latest true   rule_count 171
result_data       존재 ✓        obligations 키 ✓
obligations 개수  171 ✓
result_data.verdict APPLICABLE    source TRIGGER_BASED_ADAPTER_v1
```

## TASK-005 — Check Layer(diagnosis_transform) 읽기 검증 (데이터층)
```
transform._extract_obligations ← result_data["obligations"] (171 배열)

  total_obligations  171 ✓
  category           서류 143 / 선임 3 / 점검 25 = 171 ✓  (모두 CATEGORY_MAP 통과)
  has_description     171 (전부) ✓
  rule_type          OBLIGATION 150 / PROHIBITION 21 = 171 ✓
  verdict            APPLICABLE (불변) ✓
  ∴ transform 출력 = 171, verdict/category/description 불변.
```

---

## ★ 최종 판정: PASS
```
Applicability → obligation_instance → Glue → obligation_adapter
  → Persist(기존 재사용) → factory_diagnosis_results(신규 Row 171)
  → diagnosis_transform 읽기(result_data.obligations 171)
실행으로 증명됨. 171 → 저장 171 → 읽기 171, verdict/category/description 불변.
```

---

## 관찰 메모 (본 WO 실패 아님 — 별도 판단)
```
[1] obligations 171건 중 distinct id 169 — id 2건 중복.
    원인: 같은 조항이 NONE:UNIVERSAL 과 특정 trigger(예: MATERIAL_ACT:HAZMAT) 양쪽으로 매칭.
    성격: from-instances 어댑터 산출 자체의 속성. persist는 171을 그대로 저장(개수 보존).
    → persist/transform 결함 아님. 필요 시 트리거 중복제거는 별도 WO.
[2] 인증 HTTP transform 경로: _fetch_latest_row가 created_by == user_id 체크.
    기존 /persist·이번 persist 모두 created_by 미설정(null) → 인증 사용자 GET 시 403 가능.
    데이터층 읽힘(171)은 확정. 사용자-facing HTTP 200을 원하면 created_by 설정/서비스롤 읽기 필요(기존 속성, 별도 조치).
```

---

*WO-OPERATIONAL-VERIFY-001 — PASS. 171 → 기존 Persist → factory_diagnosis_results → diagnosis_transform 읽기, 실행 증명.*
*PDF/SaaS 연결·중복제거·created_by는 별도 WO.*
