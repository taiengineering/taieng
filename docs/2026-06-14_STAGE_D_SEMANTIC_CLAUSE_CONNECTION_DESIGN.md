# D단계 설계 — 엔진을 의미절에 직접 연결 (2026-06-14, 15차)

> 결정: **의미절 직접 읽기**(master_rule_v2 변환 경유 안 함). 대표 확정.
> 목적: executable_draft 경로의 손실(PASS 31%·binding 7%)을 우회, 보정한 의미절(9,292 executor)을
> 진단에 반영. "연결하고 전체 파이프라인을 돌려 문제를 본다."
> 함께 읽기: 2026-06-11_PIPELINE_TRACE_FWD_REV.md(병목 정밀추적), 2026-06-14_EXECUTOR_FIX_LLM_COMPLETE.md(보정).
> 성격: 설계 기록. 코드 연결은 대표 확정 후 별도 작업(evaluate_single_factory).

---

## 1. 15차까지의 맥락 (대표 구술 정리)

- **의미절 직접 읽기 = 가장 성공에 가까웠던 방식.** 실패 원인 = 사용자 입력과 대조할
  **6하원칙 기준값(수치 binding)을 의미절에서 추출 못 함.**
- 해법으로 **체크엔진** 도입 → 정밀 대조로 못 채운 부분을 **역으로 결과를 증명하는 방식**으로 메움.
- 이후 **정제 레이어**(분류·중복 제거)가 소비자 출력까지 연결됨.
- **입력**은 표준화 완료(normalize_consumer_inp / _input_to_facility_context).
- **이상상황(오염·누락)은 전체 파이프라인을 돌려가며 파악**. 그 과정에서 **의미절에 안 들어간 법령**도 발견.
- 결론: 더 분석 말고 **연결하고 전체를 돌려서 본다.**

## 2. 현재 엔진 데이터 흐름 (코드 확인: services/anonymous_factory_service.py)

```
create_temp_factory            입력표준화 → factories 임시행(is_active=false)
  ↓
evaluate_single_factory
  → _load_sector_allowed_draft_ids   executable_draft→law_article→law_sector_mapping (sector 필터)
  → _load_draft_slot_groups          draft_slot 의 IF_NUMERIC/IF_SCOPE binding 적재  ★6하원칙 값 원천
  → evaluate_draft_for_facility      factory 값 ↔ binding 대조 (체크엔진 판정, GPT 영역)
  ↓
fetch_compiler_candidates           정제 입력
  ↓
_compiler_result_to_step1_format    정제(bucket 분류·조문제목·중복제거) → 결과
```

**핵심: 현재 의무 원천은 executable_draft + draft_slot 뿐. semantic_clause는 이 경로에 안 들어옴.**
6/11 병목(draft 10,725 중 binding 748=2%만 평가)이 _load_draft_slot_groups에서 발생.

## 3. 연결고리 (DB 구조 확인 — 의미절↔draft는 같은 조문)

| 테이블 | 조문 키 |
|---|---|
| executable_draft | part_id → law_article_part.id / article_id → law_article.id |
| semantic_clause | source_part_id → law_article_part.id / source_article_id → law_article.id |

→ **둘 다 같은 법조문(part/article)에서 나온 다른 표현.** draft=binding 컴파일(2% 보유),
   의미절=육하원칙 분해(전체 보존). **part_id/article_id로 상호 매칭 가능.**
→ 의미절도 기존 sector 필터 경로(article→law→law_sector_mapping)를 그대로 재사용 가능.

## 4. 연결 설계 (evaluate_single_factory 의무 원천 전환)

### 무엇을 바꾸나
- **의무 적재원을 executable_draft/draft_slot → semantic_clause로 전환.**
  의무 원천 748개(2%) → 58,495 의미절 전체(누락 해소). executor 보정 9,292 반영(기관·업자 의무 분리).
- **무엇을 안 바꾸나(절대)**: 판정 로직 evaluate_draft_for_facility(GPT 영역), 분해기, 정제 레이어,
  입력 표준화. Claude는 **런타임 적재원 전환만**.

### 6하원칙 값 문제 (과거 실패 지점) 처리
- 의미절엔 draft_slot 같은 수치 binding(area≤500 등) 없음 — condition_text(문장)만 있음.
- 그래서 의미절 그대로는 수치 대조 불가 → **체크엔진 역증명 fallback 경로 활용**(현재도 task_count=0이면
  applicability fallback으로 동작). 정밀 수치 대조는 후속 단계에서 condition_text 구조화로 점진 강화.
- 즉 1차 연결 = **"이 사업장(sector·시설)에 해당하는 의무 목록"을 의미절에서 손실 없이 도출**까지.
  정밀 수치 게이팅은 체크엔진 + 후속 condition 파싱으로 분리.

### 연결 방식 (택1, 코드 확정 시 결정)
- (가) _load_draft_slot_groups 자리에서 의미절을 "binding 없는 의무"로 적재 → 기존 흐름 유지, 원천만 확장.
- (나) evaluate_single_factory에 의미절 직접 읽는 분기 신설(플래그로 draft경로/의미절경로 토글).
- 권고: **(나) 플래그 토글** — 운영 진단 경로라 기존 draft 경로를 살린 채 의미절 경로를 켜고 끄며 비교.

## 5. 검증 (연결 후 전체 파이프라인 가동)

- 테스트 토큰: 건설 `bce78ced-0b2c-402c-8e9e-c28ee9de92f4`(CONSTRUCTION 건축 50억 직영30·협력20,
  기존 결과 138건) / 제조 `b90d40f2`(제조업 80명, 118건).
- before(draft 경로) vs after(의미절 경로) 비교: 산안법 15~19조 선임·유해위험방지계획서·위험성평가가
  결과에 **들어오는지**(병목1·2 해소 확인). site_type 무력통과 93건·0값 매치 오염이 **줄어드는지**.
- 검증 = 카운트 아닌 결과 글읽기(어느 의무가 왜 들어오고 빠지는가).

## 6. 영역 경계 / 안전
- 판정 로직(evaluate_draft_for_facility), 분해기, master_rule_v2 = GPT 영역. 무수정.
- 원본 semantic_clause = 보호 트리거 적용됨(app.allow_semantic_clause_write). 진단은 읽기만.
- executor 보정분(semantic_clause_fix, 임시테이블)은 아직 원본 미반영 → 연결 전 **원본 반영** 선결
  (대표 승인). 또는 진단이 semantic_clause_fix를 읽도록 임시 연결 후 검증.
- 평가기 측 결함(scope 무력통과·0값 매치·주체 미검증, 6/11 문서 3·4·5)은 의미절 연결로 자동 해결 안 됨
  → facility_applicability_eval 판정계층(GPT 영역) 별도 과제로 남음.

## 7. 선결 결정 사항 (다음 세션)
1. 연결 전 executor 보정분 원본 반영할지 vs 진단이 semantic_clause_fix를 임시로 읽을지.
2. 연결 방식 (가)/(나) — 권고 (나) 플래그 토글.
3. sectors[] 복원 필요 여부(의미절 sector/sectors[] 컬럼 상태 점검).
4. 1차 범위 = 의무목록 도출까지(수치 게이팅은 체크엔진+후속) 확정.

## 관련
- 파이프라인 코드화·보호 영구화 = tai-api#110(later).
- content_type 오분류 741 = 2026-06-14_GPT_WORKORDER_CONTENT_TYPE_MISCLASSIFICATION.md(1층 GPT).
