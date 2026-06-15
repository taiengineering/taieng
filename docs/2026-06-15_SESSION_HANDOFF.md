# 2026-06-15 세션 핸드오프 — 법령엔진 D단계 (거름망 완성 + 엔진 진단 + 원래 기획 위치)

## 이 세션 한 일 (요약)
법령엔진 D단계. 거름망을 값 단위로 완성·보정하고, "통과" 개념 정립, 전체 파이프라인 확정,
엔진 4대 문제 진단, 원래 기획 문서 위치 확인까지. 핵심은 **다음 세션이 "원래 기획 정독"부터
깨끗이 시작하도록 준비**한 것.

---

## 1. 거름망 (legal_sieve_rule) — 완성, 라이브
- **최종 2,219개**: BUSINESS(KEEP) 787 / AUTHORITY(DROP) 678 / FRAGMENT(DROP) 566 /
  DELEGATED_ORG(DROP) 98 / SPECIAL_FACILITY(DROP) 90.
- 전부 stage=common_value / field_kind=executor / rule_kind=word / order_sensitive=false.
- 함수: `sieve_executor(text)` / `run_common_sieve()` / `diagnose_clauses_common()` (전부 STABLE, 라이브).
- 실제 진단: clauses 13,971 (KEEP 6,475 + 보류 7,496), DROP은 DB에서 제외.
- **잘못 걸러낼 확률 2.6% → ~0 보정**: DROP 1,443개 글읽기 → 사업장 주체 신호/예외 든 42개 중
  명백 오분류 11개(id 1432·1122·1094·140·1132·546·1286·615·484·398·1083) DELETE → 미매치=보류 복귀.
- 복합 수범자("또는/및") 309개는 섹터 단계에서 재검토 (미착수).

## 2. 확정된 개념·원칙 (이 세션 산물)
- **거름 데이터는 정방향 전용. 체크엔진 검증룰 아님.** 체크엔진은 원본(법조문)까지 추적하므로,
  파생 판정(거름)을 검증 기준으로 쓰면 순환. 단 검증 대상 축소 전처리로는 활용 여지.
- **"통과(pass)" 개념**: 거름망을 "남기기(음의 논리)"→"통과(양의 논리)"로. 거름·추출·소비자비교가
  "통과하는가" 한 형식으로 통일=N:N. **탈락 관문(명백한 비대상 제거)+선별 관문(맞는 것 통과)** 분리.
  현 거름망=탈락 관문(DROP), KEEP+보류=1차 통과.
- **LLM 한계**: 비교(N:N)는 결정적 SQL이라 한계 없음. 한계는 "추출" 한 곳(비결정성·환각).
  → 추출=LLM 1회→사장님 글읽기 검수→데이터로 굳힘→런타임은 데이터끼리 비교(LLM 안 부름).
- **비교 4축**(대표): 사용자 입력값 / 법령·의미절 / 거름망 / 추출.
- **검증 기준은 원본**: dict_legal_terms(14,942, kiwi 추출 97%)는 우리 법령 파생물이라 검증 기준 아님.
  원본 = law_article_part(143,549). 격리분 = *_legacy_contaminated 4테이블(~4,246, 검증 못 씀).

## 3. ★ 대표의 전체 파이프라인 그림 (확정)
```
법령 전체(비교 불가)
  → 공용 거름(빼기, executor)         ← 이 세션 완성
  → 섹터별 거름(건설/건물/산업)        ← 미설계
  적용 가능 남은 데이터
  → 소비자 데이터 비교 (규모·면적·공사금액)
  KSIC 뽑기 → 소비자 비교
  → 두 개 합집합 + 중복 제거
  = 의무조항(소비자 최종 의무)
```

## 4. 노가다 축소 발견 (대표가 옳았음)
- `draft_slot`(50,133, LLM IF/THEN 슬롯분해)의 **IF_ACTOR 7,513**을 조사 떼고 정제 →
  **distinct 주체 164개**(executor_text 5,197의 1/30). 이미 거름망 23 / 미분류 141.
- **단 IF_ACTOR가 "~한 자/하는 자" 행위구·깨진 조각(관한 자/대한 자) 섞임** (추출 품질 문제,
  family_name 전부 UNKNOWN/status UNRESOLVED). 141개 분류는 보류 — 묶으면 "못 찾는다" 위반 위험.
  진짜 주체 명사(근로자/감리자/소방본부장/시장군수구청장 등)만 추리는 게 맞다는 결론, 미실행.

## 5. ★ 엔진 4대 문제 (이 세션 측정, DB 실측)
1. **draft 계열이 의미절의 21%만 덮음**: executable_draft 10,725 part vs semantic_clause_fix
   49,997 part (연결 7,043). 79% IF/THEN 미분해.
2. **unresolved(13,198) > pass(12,748)**: 분해 품질 미달, IF_ACTOR 깨진 조각.
3. **전부 CANDIDATE에서 멈춤**: RESOLVED/CONFIRMED 0. 확정 파이프라인 부재/미실행.
4. **세계 A(semantic_clause_fix+거름망, 진단에 작동) ↔ 세계 B(draft IF/THEN 통과구조, CANDIDATE
   멈춤) 단절**: 소비자 비교(IF_NUMERIC/IF_SCOPE)를 받칠 데이터가 세계 B에 21%만 있고 멈춤.
- 이는 분해기 산출물(GPT 전속 영역)일 가능성.

## 6. ★ 폭주 두 번 + 원래 기획 (대표 지적)
- 지금 엔진은 폭주가 두 번 헤집어서 원래 기획과 다를 수 있음.
- **v4 LAYER_REDESIGN** (`docs/2026-06-11_LEGAL_ENGINE_V4_LAYER_REDESIGN.md`, 읽음): 이미 4대 문제를
  진단하고 객체화 해결책 설계 — IF/THEN·binding **폐지**, FacilityProfile + ApplicabilityCondition
  (actor 1급) + 공통사전 Registry, B/A/C 레이어, "탈락=보류", Candidate 철학 유지. Phase 0/1 미착수로 보임.
  → **오늘 거름망(actor 분류·탈락=보류·통과)은 v4와 같은 방향.**
- **원래 기획 문서들은 `docs/law-engine/`에 있음** (루트 아님):
  · `2026-05-07_DESIGN_master_rule_v2__taiadmin.md` (23.8KB)
  · `Cursor_Phase_2_1_Rule_Redesign_Spec__taiadmin.md` (21.2KB)
  · `Cursor_Phase_2_2_Accuracy_Spec__taiadmin.md` (20.3KB)
  · `Cursor_Phase_2_2_v3_Single_Law_Isolation_Spec__taiadmin.md` (10KB)
  · `Cursor_Phase_2_2_v31_Reverse_Diagnose_Spec__taiadmin.md` (17.5KB)
  · `Cursor_Phase_2_2_v4_Reverse_Verification_Spec__taiadmin.md` (19.4KB)
  · `LEGAL_RULE_PIPELINE__taiadmin.md` (20.7KB)
  · 분해기/추출기 코드: extract_rule_based, extract_scope_from_clauses, parse_article_parts,
    rule_patterns.yaml (전부 GPT 전속 영역)
  · 근거: `2026-06-11_PIPELINE_TRACE_FWD_REV.md` / 폭주: `2026-06-13_LEGAL_ENGINE_ROOTCAUSE_PIPELINE_SWAP.md`

---

## ★ 다음 세션 시작점 (정확히)
1. **[최우선] `docs/law-engine/` Phase 2.1 → 2.2 → v3 → v3.1 → v4 정독** (각 1~2만자, 새 컨텍스트로).
   LEGAL_RULE_PIPELINE 포함.
2. 원래 기획 파이프라인 ↔ 현 DB 상태(CANDIDATE 멈춤·21%·세계 단절) 대조.
3. **판정**: 4대 문제 = 폭주 손상 vs 원래 미완. → GPT 작업지시(분해기·확정 파이프라인 = GPT 전속)
   또는 v4 이행 결정.
4. 거름망(2,219, executor)을 v4의 C1 대조 actor 게이트로 편입 검토.
5. 그 후: 섹터 거름 설계(IF_family 체계, 통째거름 아님) / KSIC 뽑기 C구조 / 보류 7,496 축소.

## 이 세션 docs 커밋
- eccdcc16 (7부: 거름 데이터 정방향 전용)
- fef3e87 (8부: 전체 파이프라인 + 통과 개념 + IF/THEN 겹 발견)
- aae212c (9부: 엔진 4대 문제 + 원래 기획 위치)
- 본 핸드오프 (이 커밋)

## 불변 원칙 (유지)
- 검증=글읽기(카운트 금지). 1룰=1값(섞으면 추적 불가). 빼기는 명백한 것만(애매=보류).
- 추출=LLM+검수, 런타임 판정=값 룰, 검증=원본. 표준은 문제마다 바꾸지 않음.
- 엔진코어/분해기/판정로직 = GPT 전속. Claude는 버그 증거 있을 때만 직접수정.
- ⚠️ 보안 미결: Railway 환경변수 전체 노출됨 — 키 rotate 권고(앞으론 변수명만 확인).
