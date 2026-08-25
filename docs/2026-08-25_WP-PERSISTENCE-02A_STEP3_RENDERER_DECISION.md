# WP-PERSISTENCE-02A STEP-3 — RENDERER DECISION

- 작성일: 2026-08-25
- 성격: 지시서 §16. renderer 요구 수준 결정. **renderer code 수정 금지.**

---

## 1. 구분 (지시서 §16)

```
STORAGE LOSSLESS  ≠  HUMAN-READABLE TABLE
```
- 저장 무결성: runtime_data_json 이 list/dict 를 lossless 보존 → inspection_results
  배열은 손실 없이 저장/재조회 가능(STEP-2·이번 STEP 실측 확인).
- 사람이 읽는 표: 저장된 배열을 PDF 등에서 **행 테이블로 그려주는** 것은 별개 기능.

---

## 2. 두 선택지 평가

**A. canonical JSON rendering 만으로 충분한가?**
- 초기 목적이 "점검 사실의 canonical evidence 보존"이라면, 저장·재조회가 lossless 이면
  evidence 요구의 핵심(무손실 보존·감사 추적)은 충족된다.
- 단, 사람이 문서를 열었을 때 inspection_results 가 raw JSON 으로 보이면 가독성이 낮다.

**B. inspection_results 를 사람이 읽는 row table 로 렌더할 enhancement 필요한가?**
- multi_row 필드를 PDF 표(항목/결과/비고/시각 열)로 렌더하려면 renderer 가 multi_row
  배열을 표로 전개하는 지원이 필요.
- 현재 renderer 가 multi_row 를 표로 전개하는지는 이번 STEP 에서 코드 수정 없이 단정하지
  않는다(READ-ONLY). STD-FIRE-001 에 multi_row 필드가 존재하나 실제 렌더 산출물이
  DB 에 없어(generated_document 파일 0, WP-01) 렌더 실증 불가.

---

## 3. 결정

```
초기 evidence 보존 요구 = STORAGE LOSSLESS 로 충족 (A 성립)
사람이 읽는 점검 결과표(PDF 행 테이블) = RENDERER_ENHANCEMENT_REQUIRED (후속)
```

- **이번 GENERAL schema 는 저장 계약으로 완결**한다(A). 저장·재조회·감사 무결성 확보.
- inspection_results 의 **human-readable 표 렌더**는 **RENDERER_ENHANCEMENT_REQUIRED**
  로 분리한다(B). 이는 WP-PERSISTENCE-03(generated file/렌더) 범위와 겹치므로 그쪽에서
  다룬다.
- 이번 STEP 에서 renderer code 수정 = 0.

→ **RENDERER = ENHANCEMENT REQUIRED (표 렌더는 후속, 저장은 현재 충분)**

## 4. 후속 분리 기록

```
RENDERER_ENHANCEMENT_REQUIRED
- 대상: inspection_results(multi_row) → PDF/HTML 행 테이블 렌더
- 위치: 기존 document renderer (watch_engine/document 또는 Gotenberg 템플릿)
- 원칙: raw_code → display_label 매핑은 renderer 소유(payload truth 아님, §9)
- 시점: WP-PERSISTENCE-03 또는 별도 렌더 WP. 이번 STEP 아님.
```

## 5. G10 관련 (§17 approval gate 연계)

- approval gate G10 = "renderer 에서 값 silent-drop 없음".
- 저장 계약상 값은 전부 payload 에 보존되므로 **저장 레벨 silent-drop 은 0**.
- 렌더 레벨에서 표에 일부 열이 안 그려지는 것은 "표시 누락"이지 "데이터 손실"이 아니다.
  단 G10 충족을 위해 renderer enhancement 시 모든 result item 을 표에 출력하도록 요구
  (후속 WP 검증 항목).
