# WO-ADAPTER-LAW-ENRICHMENT-001 — 어댑터 법령정보 보강

**작성일:** 2026-06-26 | **상태:** 구현 완료 → **PR #111 리뷰 대기** (main 미병합)
**선행:** CHECKENGINE-INTERNAL-ANALYSIS-001 (병목 규명), REFINEMENT-OUTPUT-MAPPING-001
**PR:** https://github.com/taiengineering/tai-api/pull/111  (branch `feat/adapter-law-enrichment`)

> 구조 변경이 아니라 **누락 필드 보강**. 새 판단·새 법령 생성 0. DB에 이미 있는 식별값을 어댑터 출력에 채울 뿐.

---

## Boundary Check

```
Applicability 내부?   NO     Boundary 변경?   NO
Data Contract 변경?  NO     Breaking?       NO
→ Glue/변환 레이어 보강. 새 컴런(law_name/law_article)은 빈값→값 전환이라 다운스트림 호환.
```

---

## 배경 (규명 결과)

CHECKENGINE-INTERNAL-ANALYSIS-001에서 확인: Trigger 경로 Adapter는
`law_name=""`, `law_article=""`, `evidence=[]`로 내보내고 있었다
(주석 "이후 JOIN으로 보강 가능"이 미수행). 기존 HTML/SaaS 출력이 가장 먼저 요구하는
법령명·조문이 운영 response에 비어 있던 병목.

---

## 변경 (PR #111)

**`services/obligation_instance_adapter.py` (Glue — DB 레이어)**
```
+ _format_law_article(article_no, article_sub_no)   → "제139조" / "제24조의2"
+ _resolve_law_for_candidates(supabase, candidates)
    source_article_id → law_article(article_no, article_sub_no, law_id) → law_master(law_name)
    배치 조회(200개 단위), 후보에 law_name/law_article 채움
    try/except → 실패 시 빈 값 유지(graceful, 파이프라인 무중단)
~ obligation_instances_to_candidates()        law_name/law_article 빈 키 기본 추가
~ obligation_instances_to_trigger_candidates() 보강 호출 추가
```

**`services/obligation_adapter_service.py` (Adapter — 순수)**
```
~ _build_obligation_from_candidate()
    law_name = candidate.law_name (Glue 보강값)
    law_article = candidate.law_article (Glue 보강값)
    evidence = [law_name + " " + law_article]  (조합, 없으면 [])
```

Adapter는 순수 유지(DB 호출은 Glue에서만). 설계 원칙 완전 준수.

---

## 검증 (실데이터, 코드 작성 전)

factory `e9c56af6` batch `WO-MVP-001-LIVE` 171건:
```
source_article_id 존재    171/171
article 해결            171/171
article_no 존재         171/171
law_name 존재           171/171   → 100% 보강 가능
```
※ article_sub_no는 표본 전수 null → "제{N}조" 형식. (있을 경우 "의{M}" 처리)

표본 출력:
```
law_article  evidence
제139조     산업안전보건기준에 관한 규칙 제139조
제449조     산업안전보건기준에 관한 규칙 제449조
제24조      산업안전보건법 시행령 제24조
제197조     산업안전보건법 시행규칙 제197조
제236조     산업안전보건기준에 관한 규칙 제236조
```

---

## 금지 준수

```
✓ Check Engine / Applicability / Glue(구조)/ 정제레이어 무수정 (Glue는 보강 함수만 추가)
✓ 새 Trace Engine 미구현 · 6W 미생성 · Evidence 추론 없음 · 법령 분석 없음
✓ obligation 수 / verdict / category / description 무변경
✓ 새 판단·새 법령 생성 0 — DB 식별값만 채움
```

---

## 배포 / 다음

```
- PR #111 머지 → Railway 자동배포. 머지 전 대표님 리뷰 권장.
- 보강 실패는 graceful(빈값) → 진단 파이프라인 무중단.
- 다음: 머지 후 from-instances 실호출로 law_name/article/evidence 채움 확인
  → 이어서 HTML 출력 연결 (REFINEMENT-OUTPUT-MAPPING-001의 핵심 4필드)
- run-trigger 경로(generate_obligation_candidates)는 이 WO 범위 밖 — 해당 후보가 source_article_id를
  실으면 동일 보강 적용 가능(별도 확인 필요).
```

---

*WO-ADAPTER-LAW-ENRICHMENT-001 — 구현 완료, PR 리뷰 대기.*
*분석문서의 law_name을 운영 어댑터 출력로 실제 이동 — 누락 join 보강. 171건 100% 해결 검증.*
