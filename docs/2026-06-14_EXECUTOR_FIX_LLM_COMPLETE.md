# 2026-06-14 executor 보정 완료 — 규칙+LLM 전체 (다음 세션 이어받기)

> 함께 읽기: _EXECUTOR_FIX_STRATEGY.md(완벽2조건·BLOCKLIST), _LEGAL_PIPELINE_3LAYER.md(3층),
> _LLM_EXECUTOR_RULES_VALIDATION.md(LLM 규정·그물). 모두 taiengineering/taieng/docs/.
> 이 문서 = executor 보정 1차 최종 진척. 이전: _EXECUTOR_FIX_ALL_DONE.md(규칙 단계까지).

---

## 최종 결과 (오류 12,358건 전수 처리, 임시테이블 semantic_clause_fix)

| 구분 | 건수 | 비율 |
|---|---|---|
| 보정 완료 (규칙 5,342 + LLM 3,950) | 9,292 | 75% |
| 의무아님·주어없음 (제외) | 1,956 | 16% |
| 보류 (규칙·LLM 미해결) | 1,110 | 9% |
- executor 변경 9,287 / **source_text 변경 0**(원문 완전 무손상). executor_original 박제.
- 원본 semantic_clause·운영 **미반영**. 모두 임시테이블 안에서만.

## 보정 회차별 (APPLIED status)
| status | 내용 | 건수 |
|---|---|---|
| APPLIED_LLM | **GPT API + 6중그물 (조건절/수식절 깊은 주어)** | 3,950 |
| APPLIED_G2A | 갈래2 수식절 뒤 주어명사 | 2,425 |
| APPLIED | 갈래1 주격직결 사전등재 | 1,280 |
| APPLIED_JANG | "~의 장" | 443 |
| APPLIED_HEAD | 맨앞 사전등재 실행주체(일괄) | 366 |
| APPLIED_B | 금지문(누구든지+맨앞주체) | 209 |
| APPLIED_ENUM | 나열 복합주어 | 204 |
| APPLIED_DICT | 사전미등재 정당주체 | 168 |
| APPLIED_DEEP | 잔여 맨앞 주격직결 | 139 |
| APPLIED_POSS | 소유격 "A의 B" | 60 |
| APPLIED_LLM_C | 갈래2 C부사구(LLM 직접) | 48 |
| **합계** | | **9,292** |

## 제외/보류 분류
- 의무아님·주어없음 1,956: LLM_NO_SUBJECT 1,214(주어생략) + EXCLUDE_PENALTY 411(벌칙) +
  EXCLUDE_NONOBLIG 328(위임/준용/효력) + LLM_NONOBLIG 1 + BLOCKED 2.
- 보류 1,110(NEEDS_REVIEW_FINAL): 규칙·LLM 모두 미해결. 성격 = 나열 복합주어(맨앞에 진짜 주어
  있으나 괄호중첩·길어서 잘림, 예 산림재난방지기관의 장 및 공원사무소의 장 / 식품의약품안전처장…),
  주어생략(사무국을 둔다·도면에는), 부사격 장소(콘크리트피니셔에), 긴문장 뒤 동사조각.
  현재 executor에 동사조각("정하/통하/적용하") 남음 = 미보정 표시일 뿐, source_text는 멀쩡.

## ★ LLM 3층 (GPT API) — 이번 세션 핵심
- **방식**: tai-api 임시 라우터 routers/admin_executor_llm_fix.py. gpt-4o-mini(OPENAI_API_KEY,
  Railway). DEFER_REVIEW를 배치로 GPT 판정 → 6중그물 → 통과+high만 executor_fixed에 LLM_CANDIDATE.
- **6중 그물**: ①Kiwi 명사끝 ②원문 발췌존재(환각차단) ③BLOCKLIST(법령형식어·사물) ④role_check
  (실행주체만, 수령대상/객체/장소 배제) ⑤벌칙/효력/준용 종결(의무아님) ⑥부사격 차단(에/에는/에 대해서).
- **검증방식 유효성 증명(대표 핵심 관심사)**: 표본 글읽기로 누수 발견할 때마다 그물 보강 →
  1차 벌칙·불완전주어 누수→그물5, 2차 장소·사물 누수→그물6, 3차 누수0. 최종 표본 30건 전수
  정확(통지를 받은 자/수입허가를 받은 자 등 규칙으로 못 깎던 깊은 주어를 GPT가 정확히 잡음).
  = GPT를 믿은 게 아니라 그물이 통과시킨 것만 채택. 3,950 반영.
- **실행 모드**: /start(백그라운드 202즉시응답, 배치마다 Supabase 재접속) + /status + /stop.
  긴 동기 HTTP는 502(게이트웨이 타임아웃) → 백그라운드 필수.

## ★ 무한반복 사고 & 대응 (교훈)
- 초기 라우터 결함: rejected(그물탈락)·비주어(주어없음/의무아님)가 fix_status를 안 바꿔
  DEFER_REVIEW로 남음 → 매 배치 재조회→GPT 재호출→또 탈락 무한반복(processed 9329인데 실제 6233).
- 대응: stop → SQL로 비주어 분리 → 라우터 수정(채택=LLM_CANDIDATE / 주어없음=LLM_NO_SUBJECT /
  의무아님=LLM_NONOBLIG / 그물탈락=LLM_REJECTED, 모두 DEFER서 빠져 재조회 차단) push(54b8035).
- **데이터 오염 0**: 반복은 GPT 호출 낭비였을 뿐, 채택분은 그물 통과한 것만 1회 기록(중복 아님).
- 재시작 시 "남은 건 채택0·전부 탈락" 실시간 확인 → 보류 확정이 정답임을 검증.

## 임시 라우터 (작업 후 처리 필요)
- routers/admin_executor_llm_fix.py + router_registry/external.py 등록 줄. **작업 끝났으니 제거 대상.**
- INTERNAL_API_SECRET 헤더 보호. gpt-4o-mini. 코드화 시 이 로직(6중그물)을 파이프라인 스크립트로 이관.

## 다음 (D단계로 가는 길)
1. **보류 1,110 코드화 단계 처리**: 나열 복합주어 규칙·괄호중첩 처리 보강 시 일부 추가 보정.
   진짜 주어생략·부사격 장소는 "주어없음" 확정.
2. **content_type 오분류 741 → 1층 GPT** (작업지시서 2026-06-14_GPT_WORKORDER_CONTENT_TYPE_*.md).
   단 LLM 작업서 벌칙·효력·준용은 이미 EXCLUDE/NO_SUBJECT로 걸러져 진단엔 안 섞임.
3. **2·3층 코드화**: 규칙(맨앞 주격직결/소유격/의장/나열/수식절뒤주어/금지문/BLOCKLIST) +
   LLM 6중그물 라우터 → 분해기 뒤 보정 파이프라인 스크립트 = 새 법 자동적용 소스.
4. **임시 라우터 제거** + 코드화 완료 후 → 원본 semantic_clause 복사(대표 승인) →
   **D단계: 엔진이 의미절 읽도록 경로전환**. 선결: sectors[] 복원, 의미절 직접읽기 vs master_rule_v2.

## 원칙 (불변, 재확인됨)
- 맨앞 주격직결만 안전, 문장중간 주격 위험. 분해기·Kiwi사전 무변경.
- LLM은 발췌·분석만(생성 배제). LLM 답도 그물+표본 통과해야 채택(믿지 않고 검증).
- 매 단계 표본 글읽기로 검증(카운트 금지). 틀린 보정보다 보류.
- 긴 작업은 백그라운드 + 배치마다 DB 재접속. 상태 전이 없으면 무한반복(이번 교훈).
- 원본·운영은 보정 안정 후 한 번만 반영(대표 승인).

## 미결 (대표 처리)
- 환경변수 노출 → 키 rotate 권고(OPENAI·ANTHROPIC·결제·Supabase service role·세션).
