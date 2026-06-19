# USER VISIBLE SCOPE CLARIFICATION REPORT V1
# WO-USER-VISIBLE-SCOPE-CLARIFICATION-001

**작성일**: 2026-06-19
**성격**: 범위 분리 기록. 새 설계/탐색 없음. 권한 모델 완성 아님.

---

## 핵심 판정

```
직전까지 두 가지를 섞고 있었다:
  (1) USER_VISIBLE 체인 — V4 결과가 사용자 결과 데이터로 흐르는가
  (2) AUTHORIZATION 체인 — 그 데이터를 누가 볼 권한이 있는가

created_by=null 문제는 (1)이 아니라 (2)다.
→ 두 체인을 분리해서 본다. 이번 WO는 분리 기록만.
```

---

## 체인 1: USER_VISIBLE (데이터 흐름)

```
V4 evaluate(화성)
  → MATCH 8건                                    [PASS]
      ↓
Adapter build_obligations_from_v4
  → obligations 8건                              [PASS]
      ↓
factory_diagnosis_results 저장
  → result_data.obligations 8건, is_latest=true  [PASS]
      ↓
diagnosis_transform _extract_obligations
  → obligations 8건 추출 (컬럼 버그 수정 완료)    [PASS]
      ↓
화면 표현 스키마
  → category/title/law_name/evidence 정합        [PASS]

USER_VISIBLE 체인 = 데이터 흐름 관점에서 전부 PASS.
```

상세 검증 출처:
```
V4·Adapter:        OBLIGATION_ADAPTER_IMPL_REPORT_V1
저장:              USER_VISIBLE_BRIDGE_IMPL_REPORT_V2 (UV-08~12 PASS)
Transform 컬럼버그: TRANSFORM_COLUMN_FIX_REPORT_V1 (v1.0.2 수정)
obligations 8건:   factory_diagnosis_results 216fd7b0 실측 (law_name/action_text 누락 0)
```

---

## 체인 2: AUTHORIZATION (접근 권한) — 별도 Active Issue

```
transform_latest 권한 체크 (b2: created_by 기준)
      ↓
화성 factory_diagnosis_results.created_by = null   [BLOCK]
화성 factories.created_by = null (company_id만 존재)  [BLOCK]
      ↓
누가 조회해도 "null != user_id" → 403

= 이것은 데이터 흐름(USER_VISIBLE)이 아니라
  소유/권한 모델(AUTHORIZATION)의 문제.
```

분리 근거:
```
- obligations는 이미 존재하고 흐른다 (USER_VISIBLE PASS)
- 단지 "그 결과를 볼 권한 주체"가 데이터에 정의 안 됨 (AUTHORIZATION)
- 권한이 막혀도 데이터 체인 자체는 완성돼 있음
```

---

## Track 상태 (최종 분리)

```
[USER_VISIBLE 체인]
  V4         → PASS
  Adapter    → PASS
  Storage    → PASS
  Transform  → PASS (컬럼 버그 수정 완료)
  데이터 흐름 → 완성

[AUTHORIZATION 체인] — 별도 Active Issue
  created_by/company_id 소유 모델 → 미정
  사장님 방향: company_id 기반 (회사 소유)이 구조적으로 자연스러움
  단 이번에 설계/구현하지 않음 (루프 방지)
```

---

## Active Issue 등록: AUTH-001 (회사 소유 권한 모델)

```
ISSUE AUTH-001
  제목: factory_diagnosis_results 접근 권한 모델 (company_id 기반)
  상태: OPEN (별도 Phase)
  배경:
    - factories는 created_by 없음, company_id 있음
    - 데이터 모델이 개인 소유보다 회사 소유에 가까움
  방향(미확정, 사장님 선호):
    - transform 권한을 "사용자 company_id == factory.company_id"로
  영향 범위:
    - diagnosis_transform 권한 체크 1곳
    - persist의 created_by/company 기록 방식
  금지:
    - 이번에 설계 확장/재설계 안 함
    - USER_VISIBLE 검증과 섞지 않음
  착수 조건:
    - USER_VISIBLE 검증이 권한 외 영역에서 완료된 후
    - 사장님 명시 지시
```

---

## USER_VISIBLE 검증 완료 정의 (재정립)

```
USER_VISIBLE = "V4 결과가 사용자 결과 데이터로 흐르고,
                사용자 표현 스키마로 변환되어 화면 렌더 가능한 형태가 됨"

이 정의 기준:
  USER_VISIBLE 체인 = 완료 (데이터·변환·스키마 PASS)

권한(누가 보는가)은 이 정의에 포함되지 않음:
  = AUTHORIZATION 체인 (AUTH-001로 분리)

실 화면 최종 확인(배포 HTTP)은:
  권한 모델(AUTH-001) 확정 후 그 권한으로 호출해야 완전 종결.
  단 데이터 흐름 자체는 이미 검증됨.
```

---

## 원칙 준수

```
USER_VISIBLE과 AUTHORIZATION 분리 기록 ✅
company_id 설계 확장 안 함 ✅ (방향만 메모, 미착수)
권한 정책 재설계 안 함 ✅
Construction/Building/새 엔진 안 건드림 ✅
새 탐색/검증 없음 — 이미 확정 사실만 재정리 ✅
```

---

## 결론

```
USER_VISIBLE 체인 = 데이터 흐름 관점 완료.
  V4 → Adapter → Storage → Transform → 표현 스키마, 전부 PASS.
  obligations 8건이 사용자 결과 데이터로 흐르고 변환됨.

AUTHORIZATION 체인 = 별도 Active Issue (AUTH-001).
  created_by/company_id 소유 모델 미정.
  회사 소유(company_id) 방향이 자연스러우나 이번에 안 만듦.

두 체인을 섞지 않는다.
USER_VISIBLE의 "데이터가 흐르는가"는 답이 나왔다 = YES.
"누가 보는가"는 AUTH-001로 분리해 나중에 답한다.
```
