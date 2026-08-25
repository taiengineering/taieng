# WP-PERSISTENCE-02B STEP-0 — ARCHITECTURE REBASE

- 작성일: 2026-08-25
- 모드: ARCHITECTURE REBASE / NO MUTATION
- DB MUTATION = 0 / CODE MUTATION = 0 / DEPLOY = 0 / BRIDGE UPDATE = 0
- 선행: WP-PERSISTENCE-02A STEP-4D = PASS / COMPLETE / SEALED
- GENERAL schema UUID: `dc79ac3c-388c-42dc-b029-3dd9bda54a47`

---

## 0. 목적

기존 "document persistence" 후속 계획을
**"source persistence + Web View lazy compose + on-demand PDF export"** 구조로 정정한다.

02A 전체 성과(GENERAL schema materialization / human approval / runtime eligibility)는
**유효하며 되돌리지 않는다.** GENERAL schema 는 이제 "document 생성 틀"이 아니라
**Web View / export renderer 가 사용할 presentation schema** 로 목적만 재조준된다.

BREAK-1 / BREAK-2 를 기존 의미의 "반드시 고쳐야 하는 persistence 결함"으로
후속 작업의 목표로 사용하지 않는다.

---

## 1. 정본 아키텍처 (정정 후)

```
inspection / result source data
        ↓
inspection_set → GENERAL schema explicit mapping
        ↓
Web View lazy compose (View Model)
        ↓
화면 표시

사용자가 PDF 다운로드 요청
        ↓
동일 View Model 로 PDF on-demand 생성
        ↓
다운로드
```

**기본 흐름에서 제거되는 것 (전부 없음):**
```
runtime_document_data 자동 생성       = 없음
source_anchor writer                  = 없음 (source_inspection_id writer 기본흐름 제거)
inspection completion hook            = 없음
PDF 사전 생성                          = 없음
PDF Storage 영구 저장                  = 없음
runtime_data_json 자동 복제            = 없음
```

---

## 2. GENERAL schema 목적 재정의

| 구분 | 기존 (폐기) | 정정 (정본) |
|---|---|---|
| mapping 목적 | inspection_set → runtime schema → runtime_document 생성용 | inspection_set → APPROVED runtime schema → renderer 가 사용할 presentation schema resolution |
| schema 역할 | document auto-create 틀 | Web View / export render schema |
| 산출물 | runtime_document_data row 생성 | View Model (lazy compose, 저장 안 함) |
| PDF | 완료 시 사전 생성 + Storage 저장 | user download 요청 시 on-demand export |

GEN-INSPECT-RESULT-001 = **Web View / render schema 로 계속 사용** (STEP-4D 승인 유효).

---

## 3. 확정 사항 (9건)

```
1. GEN-INSPECT-RESULT-001 = Web View/render schema 로 계속 사용
   → STEP-4D APPROVED_FOR_RUNTIME_USE 유효, 재작업 없음.

2. runtime_inspection_bridge = explicit schema resolution SoT 유지
   → mapping 의 SoT 는 계속 runtime_inspection_bridge (새 테이블 만들지 않음).
   → 현재 324 rows 존재, runtime_form_schema_id 채워진 것 0 (아직 미연결).
   → 의미 고정:
     runtime_inspection_bridge = inspection_set → presentation schema explicit resolution SoT
     NOT: inspection_set → document auto-create bridge
   → B1 이후 붙일 invariant:
     (a) inspection_set 당 active presentation schema = 0..1
     (b) 연결 대상 schema 는 APPROVED_FOR_RUNTIME_USE 만 허용
     (c) fallback / latest / name match / family inference / LLM inference 금지
     (d) bridge mapping 자체는 runtime_document_data 생성 / payload write / PDF 생성 /
         completion hook 을 절대 trigger 하지 않음 (순수 resolution, side effect 0)

3. mapping 목적 = document auto-create 가 아니라 renderer schema 선택
   → mapping 은 "이 inspection_set 을 화면/PDF 로 그릴 때 어떤 presentation schema 를
     쓸지" 를 정하는 것. document row 를 만들지 않는다.

4. inspection completion → runtime_document_data 자동생성 금지
   → 점검 완료가 document row 를 만들지 않는다. completion hook 없음.

5. runtime_data_json 자동복제 금지
   → source data 를 document payload 로 복제/스냅샷하지 않는다. source 가 SoT.

6. source_inspection_id writer 를 기본 점검흐름에서 제거
   → WP-01 BREAK-1 (anchor writer 부재)은 이제 "결함"이 아니다.
     기본 흐름은 source 를 직접 참조(lazy)하므로 anchor writer 자체가 불필요.

7. generated_document / PDF / Storage persistence 를 완료 Gate 에서 제거
   → 폐기되는 것은 "모든 점검 결과 PDF 를 사전 생성·영구 저장해야 한다는 완료조건".
   → WP-01 BREAK-2 (storage_path/download_url/pdf_hash NULL)는 기본 Web View 흐름에서
     NOT A DEFECT (사전 생성/저장 안 하므로 비어있는 것이 정상). 완료가 PDF 사전 생성/저장 안 함.
   → generated_document 기존 1544 rows 자체 = UNCLASSIFIED / OUT OF SCOPE (§4). 처리 별도 승인.

8. PDF = user download 요청 시 on-demand export
   → View Model → PDF 를 요청 시점에만 생성. 저장 안 함(기본).

9. 기존 explicit CREATE/EDIT/SUBMIT/CONFIRM 문서 lifecycle 은 별도 scope 로 분리
   → 사용자가 명시적으로 만드는 문서(작성/수정/제출/승인 흐름)는 이 source-persistence
     흐름과 다른 별도 트랙. 이번 재베이스 범위 밖.
```

---

## 4. BREAK-1 / BREAK-2 재분류

```
WP-01 원판정:
  BREAK-1 = source-anchor writer 부재 (runtime_document_data.source_inspection_id writer 없음)
  BREAK-2 = generated_document 1544 rows 전부 storage_path/download_url/pdf_hash NULL

02B 재분류:
  BREAK-1 → NOT A DEFECT FOR DEFAULT INSPECTION WEB VIEW FLOW.
    기본 흐름이 source 직접 참조(lazy compose)이므로 anchor writer 자체가 불필요.
    "자동 document 생성 + anchor" 는 폐기된 설계. writer 를 만들지 않는 것이 정본.

  BREAK-2 → NOT A DEFECT FOR DEFAULT INSPECTION WEB VIEW FLOW.
    WP-01 에서 관측한 storage_path / download_url / pdf_hash NULL 상태는
    기본 inspection Web View 흐름에서는 결함이 아니다
    (사전 PDF 생성/저장을 하지 않으므로 이 컬럼들이 비어있는 것이 정상).

    generated_document 기존 1544 rows 자체의 provenance / 용도는
    이번 STEP-0 에서 판정하지 않는다.
    기존 rows = UNCLASSIFIED / OUT OF SCOPE FOR THIS REBASE.
    방치 / 아카이브 / 삭제 / 재사용 여부 = 별도 조사 및 별도 승인 전까지 NO MUTATION.
```

**폐기된 것의 정확한 범위**: 폐기된 것은 **"모든 점검 결과 PDF 를 사전 생성·영구 저장해야
한다는 완료조건"** 이지, `generated_document` 테이블이나 기존 1544 rows 전체가 아니다.
특히 이 문서가 explicit CREATE/EDIT/SUBMIT/CONFIRM lifecycle 을 별도 scope 로 보존하므로,
1544 rows 중 일부가 그 별도 문서 흐름의 정상 데이터일 가능성을 배제하지 않는다.

**중요**: BREAK-1/BREAK-2 를 후속 작업의 "고칠 목표"로 삼지 않는다. WP-01 감사 결과 자체는
그 시점의 정확한 관찰이었으나, 제품 결정이 "source persistence" 로 바뀌면서 기본 Web View
흐름 기준으로는 결함이 아니게 된다. 기존 rows 의 분류/처리는 별도 트랙.

---

## 5. 현재 production 실측 (read-only 근거, mutation 0)

```
general_schema_status       = APPROVED_FOR_RUNTIME_USE   (4D 결과 유효)
runtime_inspection_bridge   = 324 rows
  bridge_with_schema        = 0   (runtime_form_schema_id 채워진 것 0 = 아직 미연결)
  bridge_to_general         = 0   (GENERAL schema 연결된 것 0)
inspection_sets_total       = 327
runtime_document_data_total = 1
  → existing row provenance 는 STEP-0 범위에서 판정하지 않음.
  → 금지 대상은 inspection completion 에 의한 신규 자동생성.
  → 기존 row UPDATE/DELETE 없음 (explicit CREATE/EDIT lifecycle 의 정상 row 가능성 배제 안 함).
generated_document_total    = 1544
  → 기존 rows = UNCLASSIFIED / OUT OF SCOPE (§4). 방치/아카이브/삭제/재사용 = 별도 승인 전 NO MUTATION.
```

→ bridge 324 행이 존재하나 schema resolution 은 0. **아직 아무 매핑도 없음.**
   이것이 B1 (explicit mapping) 의 출발점. bridge 를 SoT 로 유지하되, mutation 은
   B1 HUMAN REVIEW 를 거친 뒤 승인된 대상만.

---

## 6. 재조정된 후속 로드맵

```
02A STEP-4D = SEALED
    ↓
02B STEP-0  ARCHITECTURE REBASE (본 문서, NO MUTATION)
    ↓
B1          explicit mapping (HUMAN REVIEW → inspection_set ↔ GENERAL schema 명시 연결)
    ↓
Web View    composer (lazy compose, View Model)
    ↓
Web View    renderer (화면 표시)
    ↓
On-demand   PDF export (요청 시 View Model → PDF)
```

**폐기된 경로 (더 이상 정본 아님):**
```
B1 DATA POPULATION → BREAK-1 source-anchor writer → runtime_document_data 생성
```

---

## 7. 범위 밖 (이번 STEP-0 에서 하지 않음)

```
B1 mapping DB mutation                (대상 수 미확정 — 아래 참조)
runtime_inspection_bridge UPDATE
GENERAL schema 재작업 (이미 SEALED)
runtime_document_data 생성/UPDATE/DELETE (기존 row 포함)
generated_document 처리 (방치/아카이브/삭제/재사용 — 전부 별도 승인 전 NO MUTATION)
source_anchor writer 구현
Web View composer / renderer 구현
PDF export 구현
explicit CREATE/EDIT/SUBMIT/CONFIRM lifecycle (별도 scope)
CODE / DEPLOY / BRIDGE 변경
```

**B1 mapping 대상 수 = 미확정.** 이 STEP-0 문서 안에 316 같은 특정 수의 근거가 없다
(production snapshot: bridge 324 / inspection_sets 327 / bridge_with_schema 0).
B1 HUMAN REVIEW 결과에서 eligible / non-eligible / exception 수를 확정한 후 승인된 대상만
mutation 한다. 과거 02A artifact 에 특정 수가 있더라도 B1 시작 시 다시 증거를 연결하여
확정한다. 아키텍처 재베이스 문서에 mutation 수를 미리 고정하지 않는다.

---

## 8. 판정

```
WP-PERSISTENCE-02B STEP-0 = ARCHITECTURE REBASE COMPLETE

ARCHITECTURE = source persistence + Web View lazy compose + on-demand PDF export
02A 성과 = 유효 (되돌리지 않음)
GENERAL schema = Web View/render schema 로 목적 재정의
runtime_inspection_bridge = presentation schema resolution SoT (새 테이블 없음, invariant §3-2)

BREAK-1 = NOT A DEFECT FOR DEFAULT WEB VIEW FLOW
BREAK-2 = NOT A DEFECT FOR DEFAULT WEB VIEW FLOW
generated_document existing rows = UNCLASSIFIED / OUT OF SCOPE (NO DELETE/ARCHIVE/UPDATE)
runtime_document_data existing row = UNCLASSIFIED / OUT OF SCOPE (NO MUTATION)

B1 mapping 대상 수 = 미확정 (HUMAN REVIEW 후 확정)

DB MUTATION = 0
CODE MUTATION = 0
DEPLOY = 0
BRIDGE UPDATE = 0

NEXT = B1 explicit mapping — 먼저 어떤 inspection_set 이 GENERAL presentation schema 의
       적용 대상인지 HUMAN REVIEW 로 확정하는 단계부터 시작
```

제출 후 STOP. B1 은 별도 착수 지시 시 시작.
