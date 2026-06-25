# WO-DATA-CONTRACT-001
# 레이어 간 데이터 계약서 (Data Contract)

**작성일:** 2026-06-25 | **상태:** 계약 동결 (API 문서 아님)
**선행:** WO-BOUNDARY-LOCK-001 (책임 경계 동결)
**목적:** 레이어 사이를 넘는 데이터 필드를 고정한다. 계약된 필드 외 누출 금지.

> 이건 API 문서가 아니라 데이터 계약서다.
> 계약된 필드만 넘어간다. 그 외는 내부 구현이며 경계를 넘지 않는다.

---

## 계약 원칙

```
1. 각 경계는 "넘어가는 필드 목록"을 고정한다.
2. 목록 외 필드는 내부 구현 — 다음 레이어가 볼 수 없다.
3. 필드를 추가하려면 별도 WO로 계약을 개정해야 한다.
4. 받는 쪽은 계약 필드만 신뢰한다. 내부 필드 의존 금지.
```

---

## 경계 1: Applicability Engine → Glue → Check Engine

```
obligation_instance 중 넘어가는 필드 (계약):

  obligation_id        (= obligation_instance.id)
  factory_id
  source_clause_id
  trigger              (= trigger_type:trigger_l2)
  reason
  confidence
  status

이외 필드는 넘기지 않는다:
  generation_batch     ✗ 내부 (배치 추적용)
  source_cmc_id        ✗ 내부 (감사용, 다음 레이어 불필요)
  detail / fired_by    ✗ 내부 (생성 근거, Glue가 trigger로 흡수)
  applicable_sectors   △ Glue 내부에서 sector 단일값으로 변환 후 소비
  created_at           ✗ 내부

Glue가 candidate로 변환 시 채우는 형식 (Check Engine 입력):
  clause_id, source_article_id, source_part_id, trigger_code,
  executor_text, condition_text, action_text, content_type,
  sector, confidence
  → 이 10필드가 Check Engine과의 실제 계약면.
  → 전부 obligation_instance + semantic_clause JOIN으로 공급.
```

---

## 경계 2: Check Engine → Check Layer

```
Check Engine이 넘기는 필드 (계약):

  verdict      (APPLICABLE / POSSIBLE / NOT_APPLICABLE / UNKNOWN)
  reason       (판정 근거 — 역추적)
  evidence     (근거 법령: law_name + article_no + article_title)
  draft        (draft_id / applicability_status)

이외는 넘기지 않는다:
  match_details (jsonb 원본)   ✗ 내부 (Check Engine 판정용)
  applicability_id             ✗ 내부 (테이블 PK)
  check_method                 △ 메타 (디버그용, 선택)

Check Layer는 위 4필드만 받아 6W를 생성한다.
verdict를 바꾸지 않는다 (BOUNDARY-LOCK ④).
```

---

## 경계 3: Check Layer → Refinement Layer

```
Check Layer가 넘기는 필드 (계약):

  obligation_id
  verdict          (변경 없이 전달)
  six_w            (누가/무엇을/언제/어디서/왜/어떻게)
  required_evidence (제출/보관 서류)
  required_data    (이행 필요 입력값)
  law_reference    (evidence 승계)

이외는 넘기지 않는다:
  Check Engine 내부 draft 원본   ✗
  계산 중간값                     ✗

Refinement는 위를 받아 표현만 가공한다.
verdict / 의무 내용 불변 (BOUNDARY-LOCK ⑤).
```

---

## 경계 4: Refinement Layer → Result

```
Refinement가 넘기는 필드 (최종 화면 계약):

  category         (선임/점검/신고/교육/서류)
  title            (의무명)
  description       (실행 가이드 문장)
  law_name / law_article
  required_evidence
  due_date         (있으면)
  status

이외는 넘기지 않는다:
  dedup 중간 키 / merge 원본    ✗ 내부

→ factory_diagnosis_results.result_data.obligations[] 형태.
→ 사용자 화면이 소비하는 최종 계약면.
```

---

## 전체 데이터 흐름 (계약 필드만)

```
facility_profiles
  (sector, ksic, numeric, has_*)
        │
        ▼
[Applicability Engine]
        │  obligation_id, factory_id, source_clause_id,
        │  trigger, reason, confidence, status
        ▼
[Glue]  → candidate 10필드 (clause_id, article_id, trigger_code, ...)
        │
        ▼
[Check Engine]
        │  verdict, reason, evidence, draft
        ▼
[Check Layer]
        │  obligation_id, verdict, six_w,
        │  required_evidence, required_data, law_reference
        ▼
[Refinement]
        │  category, title, description,
        │  law_name, law_article, required_evidence, status
        ▼
Result (factory_diagnosis_results.result_data.obligations[])
```

---

## 계약 위반 탐지

```
누출 신호 (발견 시 계약 위반):
  - 다음 레이어가 "내부 필드"를 읽음
    예: Refinement가 source_cmc_id를 참조 → 위반 (경계1 내부 필드)
  - 받는 쪽이 계약에 없는 필드에 의존
    예: Check Layer가 match_details로 분기 → 위반 (경계2 내부)
  - 필드를 몰래 추가
    예: Glue가 새 필드를 candidate에 끼움 → 계약 개정 WO 없이 금지

자가 점검:
  각 경계에서 "이 필드가 계약 목록에 있는가?"
  없으면 → 내부 구현 → 넘기지 않는다.
```

---

## 독립 발전 보장

```
이 계약이 고정되면:
  - Applicability Engine: cmc 매핑을 아무리 바꿔도
    obligation_id/trigger/reason/... 7필드만 유지하면 됨.
  - Check Engine(GPT): 내부 compiler를 고도화해도
    verdict/reason/evidence/draft만 유지하면 됨.
  - Refinement: 표현을 아무리 바꿔도
    category/title/description만 채우면 됨.

→ 서로의 내부를 모른 채 독립 발전.
→ 계약면만 지키면 루프 없음.
```

---

## 동결 선언

```
이 데이터 계약은 동결(freeze)된다.

필드 추가/변경하려면:
  - WO-DATA-CONTRACT-002 등 개정 WO를 명시적으로 작성
  - "편의상" 내부 필드를 넘기는 것 금지
  - 받는 쪽은 계약 필드만 신뢰

WO-BOUNDARY-LOCK-001(책임)과 함께
  TAI Safe 엔진 아키텍처의 두 헌법을 구성한다.
```

---

*WO-DATA-CONTRACT-001. 레이어 간 데이터 계약서.*
*4개 경계 필드 고정. 계약 외 필드는 내부 구현 — 넘기지 않는다.*
*핵심: 경계1=7필드 / 경계2=verdict·reason·evidence·draft / 경계4=화면 계약.*
*책임 경계는 WO-BOUNDARY-LOCK-001 참조. 두 문서가 아키텍처 헌법.*
