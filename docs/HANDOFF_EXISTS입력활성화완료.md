# HANDOFF — EXISTS 입력 활성화 사이클 완료 시점

**작성일:** 2026-06-25 | **목적:** 다음 작업 창이 컨텍스트 없이 이어받기 위한 핸드오프
**현재 단계:** 구조 개발 종료(헌법 동결) → 품질 개발 진행 중. EXISTS 입력 파이프 실데이터 관통 완료.

> 이 문서 하나로 현재 상태·미해결·다음 후보·주의사항을 파악할 수 있게 한다.
> 세부는 docs/ 내 각 WO 문서 참조.

---

## 0. 지금 어디까지 왔나 (한 문단)

입력(has_*) → facility_profiles 저장 → generator가 읽어 obligation_instance 생성
→ Glue → Adapter까지 **실데이터·실호출로 전 구간 관통 검증 완료**.
17회차 동안 막혀 있던 "입력 저장소 단절"이 풀렸다.
아키텍처는 헌법 3문서로 동결됨. 이후는 ① Applicability Engine 내부 품질 개발만.

---

## 1. 확정된 사실 (실측 검증됨)

```
✓ 입력단 (Cursor, CURSOR-TASK-002, 배포 7e40345):
    POST /diagnosis/exists-input/{factory_id} → facility_profiles.profile_snapshot.exists_inputs 저장
    GET  /diagnosis/exists-input/{factory_id}/trace → 입력→Builder→oi→Glue→Adapter 추적
    GET  /diagnosis/mvp-exists-fields?sector= → sector별 MVP 문항
    실호출 검증: api.taieng.co.kr 에서 POST 200 + trace 정상

✓ Generator (Claude, DB):
    exists_inputs 읽어 EXISTS obligation_instance 발동 (실데이터)
    factory e9c56af6: 96 → 171건
      UNIVERSAL 93 + THRESHOLD 3 + EXISTS 75

✓ End-to-End 실호출 (api.taieng.co.kr trace, total_ms 880):
    input(has_* 3) → builder(contract, match:true) → oi(171)
    → glue(candidate 171) → adapter(171, verdict APPLICABLE)

✓ 경계 무변경: Check Engine / cmc / Trigger / Data Contract 전부 무수정
✓ Cursor 커밋 5개(b897bbf~7e40345) 전수 확인 — 금지영역 침범 없음
```

---

## 2. 핵심 수치 (현재 baseline)

```
cmc CONFIRMED 유형별:
  EXISTS 계열 452 (WORK_ACT 187 / MATERIAL_ACT 160 / EQUIPMENT_ACT 94 / FACILITY_ACT 11)
  UNIVERSAL 94 / THRESHOLD 3

전체 엔진 Coverage (산안법 4법): 20.4% (444 / 2,174 distinct clause)
  기준규칙 30.9% / 산안법 8.3% / 시행령 4.9% / 시행규칙 2.9%

테스트 factory e9c56af6 (INDUSTRIAL, worker 280):
  obligation_instance 171 (batch 'WO-MVP-001-LIVE')
  facility_profiles profile_version 3 (실호출로 v3까지 올라감)
  exists_inputs: {has_crane, has_welding, has_chemical_substance}

EXISTS 입력 ROI (상위, input_field별 살아나는 의무):
  has_confined_space 68 / has_hazardous_material 68 / has_dust_work 37
  has_chemical_substance 32 / has_asbestos_demo 30 / has_diving 27
  has_crane 25 / has_excavation 23 / has_asbestos 23 / has_scaffold 22
  상위 10개 누적 355 (전체 EXISTS 507의 70%)
```

---

## 3. 중요한 정정 (다음 창이 반드시 알아야 함)

```
★ "Coverage 20.4% → 31%" 예측은 측정 오류였다 (Claude 자인).
   EXISTS 452는 이미 CONFIRMED → 20.4% 분자에 이미 포함됨.
   이번 작업은 "잠자던 CONFIRMED EXISTS를 실제 발동"시킨 것.
   → Coverage(엔진이 아는 의무 비율): 20.4% 그대로
   → Activation(실제 진단에 발동되는 의무): 0 → 75건  ← 이게 진짜 성과

   올바른 성공 지표:
     "단일 factory 의무 96 → 171" 또는 "EXISTS activation 0 → 75"
     NOT "Coverage %"
```

---

## 4. 미해결 / 다음 후보 (우선순위 아님, 선택지)

```
A. trace 카운터 표시 버그 (Cursor, 사소)
   trace의 "exists":0 표시 — 실제론 families_top에 EXISTS 살아있음
   (EQUIPMENT_ACT/MATERIAL_ACT/WORK_ACT를 'EXISTS' 문자열로 안 셈)
   총합 171은 정확. 표시만 수정하면 됨.

B. EXISTS 분류 차이 직독 확인 (Claude, 품질)
   Claude DB 생성: chemical 32 + crane 25 + welding 18 = 75
   Cursor trace:   CRANE 25 + HAZMAT 21 + WELDING 18 + CHEMICAL 8 + MSDS 3 = 75
   → 합 75 동일, 내부 분류만 다름. 어느 쪽이 맞는지 조문 직독 필요.
   (has_chemical_substance를 어떻게 쪼개는가의 문제)

C. Check Engine verdict 생성 검증 (별도, GPT 레이어)
   현재 Adapter까지 관통 확인. 그 다음 45CM Check Engine이
   실제 verdict/evidence 생성하는지는 미검증 (GPT 소관, 경계 주의).

D. 다른 sector factory 검증 (Claude, 가벼움)
   건설/건물 factory로 같은 흐름(UNIVERSAL+THRESHOLD+EXISTS) 작동 확인.
   CONSTRUCTION baseline 90 / BUILDING 91 이미 확보됨.

E. EXISTS 입력 확대 (상위 10개 채우기)
   현재 3개(welding/crane/chemical)만 테스트.
   has_confined_space(68)/has_hazardous_material(68)/has_dust_work(37) 등
   추가 입력 시 더 많은 의무 발동.

F. FRAGMENT 916 재파싱 (Coverage 2순위, GPT 경계 주의)
   미커버 1,730 중 53%가 주어불명/조각. semantic_clause 파싱 개선 시 회복.
   단 파싱은 GPT 엔진 인접 — Architecture Review 먼저.
```

---

## 5. 아키텍처 헌법 (절대 준수 — 3문서)

```
docs/WO-ARCHITECTURE-FREEZE-001_프로젝트헌법.md   ← 최상위: 변경 절차
docs/WO-BOUNDARY-LOCK-001_경계동결.md            ← 책임: 5레이어
docs/WO-DATA-CONTRACT-001_데이터계약.md          ← 데이터: 4경계 필드

5레이어:
  ① Applicability Engine  의무생성 (Trigger/UNIVERSAL/THRESHOLD/EXISTS)
  ② Glue Adapter          순수변환 (판단/필터 금지)
  ③ 45CM Check Engine     verdict (GPT 소관, Claude 무수정)
  ④ Check Layer           6W/증빙
  ⑤ Refinement Layer      중복/병합/표현

신규 WO는 반드시 Boundary Check 4문항으로 시작:
  Applicability 내부? / Boundary 변경? / Data Contract 변경? / Breaking Change?
  → YES 하나라도 있으면 Architecture Review 먼저.
  → 대부분의 품질작업은 "Applicability 내부 YES, 나머지 NO" = 바로 진행.
```

---

## 6. 반복 확인된 함정 (다음 창도 빠지지 말 것)

```
1. 카운트 분석 금지 — 반드시 조문 직독.
   "사업주는"으로 시작해도 뒷부분에 조건 숨음. 정규식 1차분류 신뢰불가.
   다의어 함정: "안전관리자"는 LPG법/위험물법/소방법에도 있음 → 산안법만 선별.

2. executor "해당하"/"사업장" THRESHOLD 2건은 거르면 안 됨.
   파싱 오류일 뿐 실제 사업주 의무(안전보건관리담당자/산업보건의).
   executor='사업주' 필터 추가하면 이 2건 손실.

3. obligation_count 감소 ≠ 버그.
   Glue/Adapter에 executor 필터 없음 → candidate=obligation 같아야 정상.

4. PostgREST 임베디드 조인 안 되면 2-step 폴백 (FK 없음).

5. 가정 데이터 ≠ 실데이터. 보고 전 실제 실행됐는지 DB 확인.
   "100% 완료" 선언 금지. Coverage와 activation 혼동 금지.

6. facility_profiles 다중 버전 주의.
   factory e9c56af6에 profile_version 1/2/3 존재.
   generator는 최신 버전(exists_inputs 있는 것) 읽어야 함.
```

---

## 7. 역할 분담 (절대원칙)

```
Claude 기획창:  설계·DB작업(Supabase MCP)·검증·작업지시서·docs 푸시
Cursor/Claude Code: services/ 코드·배포·HTTP 실호출 (엔진 인접 코드 직접 푸시 금지)
GPT: Deterministic Compiler/엔진 아키텍처 (Claude 수정 절대금지)

git push: kn541 계정 403 지속 → Cursor가 guri MCP push_files(TAI Engineering)로 우회
모든 docs: taiengineering/taieng repo의 docs/ 폴더에만
코드: taiengineering/tai-api (main push → Railway 자동배포, api.taieng.co.kr)
```

---

## 8. 핵심 좌표 (빠른 참조)

```
DB: Supabase Seoul, project_id vwlahtguyggrhvslabax
배포: api.taieng.co.kr (Railway 싱가포르, 프로젝트 7c3ab53b)
테스트 factory: e9c56af6-5de7-487d-bd2e-0d452291a562 (INDUSTRIAL, worker 280)
obligation batch: 'WO-MVP-001-LIVE'

핵심 테이블:
  condition_mapping_candidate (cmc)  입력→조문 매핑자산
  obligation_instance                생성된 의무 (factory_id, source_cmc_id UNIQUE)
  semantic_clause (58,495)           조문 (source_article_id → law_article → law_master)
  facility_profiles                  영구마스터 (profile_snapshot.exists_inputs ← has_* 여기)
  diagnosis_rule_results             Check Item (진단 결과 행)
  factory_diagnosis_results          진단 헤더
  appendix_condition (7건)           별표3 안전관리자 (employee_count>=50/500/1000)

EXISTS 입력 엔드포인트 (배포됨):
  POST /diagnosis/exists-input/{factory_id}
  GET  /diagnosis/exists-input/{factory_id}/trace
  GET  /diagnosis/exists-input/{factory_id}/contract
  GET  /diagnosis/mvp-exists-fields?sector=

Glue 엔드포인트 (CURSOR-TASK-001, 배포됨):
  POST /obligation-adapter/from-instances/{factory_id}
```

---

## 9. WO 문서 체인 (시간순, docs/)

```
구조 개발:
  WO-ENGINE-CODE-AUDIT-001          실제 엔진 규명 (cmc는 매핑자산)
  WO-OBLIGATION-GENERATION-ARCHITECTURE-001
  WO-OBLIGATION-GENERATOR-001
  WO-OBLIGATION-INSTANCE-IMPLEMENTATION-001
  WO-INPUT-BINDING-ARCHITECTURE/IMPLEMENTATION-001
  WO-EXISTS-INPUT-TRACE-001         has_* 저장위치 추적
  WO-DIAGNOSIS-TO-OBLIGATION-PIPELINE-001  단절 2개 규명
  WO-LIVE-DIAGNOSIS-MVP-001         첫 진단 95건
  WO-END-TO-END-CONNECTION-001      최초 관통
  WO-CHECKENGINE-API-CONTRACT-001   Contract 이미 존재 확인
  WO-OBLIGATION-ADAPTER-INTEGRATION-001  Glue 규격
  CURSOR-TASK-001_어댑터연결구현    Glue 구현 (검증완료)

헌법 (동결):
  WO-BOUNDARY-LOCK-001_경계동결
  WO-DATA-CONTRACT-001_데이터계약
  WO-ARCHITECTURE-FREEZE-001_프로젝트헌법

품질 개발:
  WO-UNIVERSAL-QUALITY-001          UNIVERSAL 94 천장 확인, 오염 89 제거
  WO-THRESHOLD-QUALITY-001          안전관리자 추가 (95→96)
  WO-COVERAGE-GAP-001               Coverage 20.4% baseline
  WO-EXISTS-ACTIVATION-SPEC-001     상위10=355의무 명세
  CURSOR-TASK-002_EXISTS입력활성화구현  입력단 구현 (검증완료)
  HANDOFF (이 문서)
```

---

## 10. 다음 창 시작 가이드

```
1. 이 문서 + 관심 영역 WO 문서를 먼저 읽는다 (추측 금지).
2. 작업 선택 시 Boundary Check 4문항부터.
3. DB 검증은 카운트가 아니라 조문 직독.
4. 새 인계장/WO를 검증보다 앞서 찍어내지 않는다 (이번 창 자성점).
5. 가정 데이터와 실데이터 결과를 혼동하지 않는다.

추천 다음 작업 (가벼운 것부터):
  - D (다른 sector factory 검증): 현재 자산 범용성 확인, 읽기 위주
  - E (EXISTS 입력 확대): 상위10 채우면 activation 大. 입력단 Cursor 동반
  - B (EXISTS 분류 직독): chemical 75건 분류 정합성, 품질
  무거운 것 (Review 필요):
  - F (FRAGMENT 재파싱): GPT 경계, Architecture Review 선행
```

---

*HANDOFF. EXISTS 입력 활성화 사이클 완료.*
*핵심: 입력→의무 실데이터·실호출 관통 (96→171, EXISTS 0→75). Coverage 20.4% 불변(activation이 성과).*
*아키텍처 동결 유지. 다음은 ① Applicability 내부 품질. 카운트 아닌 직독.*
