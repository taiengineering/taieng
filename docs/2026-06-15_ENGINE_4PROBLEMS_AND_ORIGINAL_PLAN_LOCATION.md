# 2026-06-15 (9부) 엔진 4대 문제 진단 + 원래 기획 문서 위치 확인

## 한 줄 요약
오늘 측정으로 엔진 4대 문제를 진단. 대표 지적: "폭주가 두 번 헤집은 엔진이라 원래 기획과 다를 수
있다." → 원래 기획 문서들을 docs/law-engine/에서 찾음(Phase 2.1~v4). v4 LAYER_REDESIGN(루트,
06-11)까지 읽음. **다음 세션: 원래 기획(law-engine/ Phase 2.x) 정독 → 현 DB 상태와 대조 →
4대 문제가 폭주 손상인지 원래 미완인지 판정.**

## 엔진 4대 문제 (오늘 측정, DB 실측)
1. **draft 계열이 의미절의 21%만 덮음**: executable_draft 10,725 part vs semantic_clause_fix
   49,997 part (연결 7,043). 79%가 IF/THEN 미분해.
2. **unresolved(13,198) > pass(12,748)**: 분해 품질 미달. IF_ACTOR에 "관한 자/대한 자" 깨진 조각.
3. **전부 CANDIDATE에서 멈춤**: executable_draft 10,725 전부 CANDIDATE. RESOLVED/CONFIRMED 0.
   확정 파이프라인 부재 또는 미실행.
4. **세계 A ↔ 세계 B 단절**:
   - 세계 A = semantic_clause_fix(50,000) + 오늘 만든 거름망. 진단에 실제 사용 중. 작동.
   - 세계 B = executable_draft/draft_slot/draft_condition_graph (IF/THEN 통과구조). CANDIDATE 멈춤.
   - 소비자 비교(IF_NUMERIC/IF_SCOPE)를 받칠 데이터가 세계 B에 있는데, 21%만 있고 멈춤 → 소비자
     비교 단계의 토대 대부분 부재. 거름(A)은 되는데 소비자 비교(B)로 가는 다리가 끊김.

## ★ 대표 지적: 폭주가 두 번 헤집은 엔진
- 지금 엔진은 폭주가 두 번 헤집어서, 원래 기획과 많이 다를 수 있음.
- 4대 문제가 "폭주로 망가진 것"인지 "원래 미완성"인지는 **원래 기획 문서를 봐야** 판정 가능.

## v4 LAYER_REDESIGN (2026-06-11, 루트) 읽음 — 핵심
- 이 문서는 **이미 위 문제를 진단하고 해결책을 설계**해둠:
  - PASS 깔때기 31%(=오늘의 21%) → B6 "탈락=보류, 소멸 금지"로 대체 설계
  - binding 7% 커버리지 → IF/THEN·binding 개념 **폐지**, 객체 필드(ApplicabilityCondition)로
  - CANDIDATE 멈춤 → 원칙 7 "Candidate 철학 유지"(버그 아니라 의도)
  - 표준 객체 2개: FacilityProfile(사업장, TriValue 결측=UNKNOWN) + ApplicabilityCondition
    (조문, actor 1급 객체) + 공통사전 Registry(EQUIP/PROC/MAT/ACT/BLDG/ACTOR/METRIC)
  - 레이어: B(법 번역, 배치) / A(사업장 번역, 런타임) / C(대조, 런타임). C2가 판단 유일 지점.
- **즉 오늘 우리가 거름망에서 한 것(actor 분류, 탈락=보류, 통과 개념)은 v4 기획과 같은 방향.**
  단 v4의 표준 객체·Registry는 아직 미구축(Phase 0/1 미착수로 보임).
- 작성자 Claude(사장님 승인, GPT 영역 포함). IF/THEN draft 계열은 v4가 "폐지" 대상으로 명시.

## 원래 기획 문서 위치 (다음 세션 정독 대상) — docs/law-engine/
- `2026-05-07_DESIGN_master_rule_v2__taiadmin.md` (23.8KB) — master_rule_v2 설계
- `Cursor_Phase_2_1_Rule_Redesign_Spec__taiadmin.md` (21.2KB) — 규칙 재설계
- `Cursor_Phase_2_2_Accuracy_Spec__taiadmin.md` (20.3KB)
- `Cursor_Phase_2_2_v3_Single_Law_Isolation_Spec__taiadmin.md` (10KB) — v3 단일법 격리
- `Cursor_Phase_2_2_v31_Reverse_Diagnose_Spec__taiadmin.md` (17.5KB) — v3.1 역진단
- `Cursor_Phase_2_2_v4_Reverse_Verification_Spec__taiadmin.md` (19.4KB) — v4 역검증
- `LEGAL_RULE_PIPELINE__taiadmin.md` (20.7KB) — 파이프라인 전체
- 분해기/추출기 코드: `extract_rule_based`, `extract_scope_from_clauses`, `parse_article_parts`,
  `rule_patterns.yaml` (전부 docs/law-engine/, GPT 전속 영역)
- 근거: `2026-06-11_PIPELINE_TRACE_FWD_REV.md` (정/역추적 정밀분석, v4의 근거)
- 폭주 관련 가능성: `2026-06-13_LEGAL_ENGINE_ROOTCAUSE_PIPELINE_SWAP.md` (15KB)

## 다음 세션 시작점 (정확히)
1. docs/law-engine/ Phase 2.1 → 2.2 → v3 → v3.1 → v4 순서로 정독 (각 1~2만자, 새 컨텍스트 필요).
2. 원래 기획의 파이프라인(LEGAL_RULE_PIPELINE)과 현 DB 상태(CANDIDATE 멈춤·21%·세계 단절) 대조.
3. 판정: 4대 문제 = 폭주 손상 vs 원래 미완. → GPT 작업지시(분해기·확정 파이프라인) 또는 v4 이행 결정.
4. 오늘 만든 거름망(2,219, executor)은 v4의 actor 분류와 같은 방향 → C1 대조의 actor 게이트로 편입 검토.

## 오늘 거름망 상태 (불변)
- legal_sieve_rule 2,219개 (BUSINESS 787/AUTHORITY 678/FRAGMENT 566/DELEGATED 98/SPECIAL 90).
- 정방향 전용. 함수 sieve_executor/run_common_sieve/diagnose_clauses_common. 라이브.
