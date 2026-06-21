# FACT PROMOTION — 5개 레지스터 정제
# WO-FACT-PROMOTION-001

**작성일**: 2026-06-21
**목적**: FACT/CANDIDATE/UNKNOWN/VALID 재검토 + NOT_ERROR 신설 = 5레지스터 운영 승격.
**원칙**: 수정 0. 읽기/분류만. 반례 검증으로 승격·강등.
**핵심**: 수정 전 "확실한 것만 승격". law_sector_mapping 수정은 아직 진입 금지.

---

## STEP-1: FACT 전수 재검토 (원인소스 + 재현 + 반례없음)

```
F-01 Sector 오염 (소방 NFPC)
  원인소스: _load_sector_allowed_draft_ids, secs=None → allowed.add ✓
  재현: 건설 92% / 산업 82% 소방, verify unmapped 30 재현 ✓
  반례검증: 소방 법령 108개 중 미매핑 100개(93%) — 읽기 검증으로 확인 ✓
    (소방이 전부 정상매핑인데 다른 이유로 통과 = 반례 없음)
  → FACT 유지 (단 "어느 소방법이 어느 섹터" 판단은 별개 = GPT)

F-02 Penalty 0원
  원인소스: _task_to_rule_row penalty_summary="" 고정 ✓
  재현: 결과 전 행 penalty_summary="" ✓
  반례검증: penalty_summary 필드는 스키마에 정식 존재(자리 있음, 값만 빔).
    → "Step1 설계상 제외"인지 "미구현 오류"인지 미확정 = 반례 배제 실패.
  → CANDIDATE 강등 (UNKNOWN 성격 — Step2/penalty 코드 확인 필요)

F-03 Form 0
  원인소스: form_linked=0 고정 ✓
  재현: summary.form_linked=0 ✓
  반례검증: F-02와 동일 — Step1 설계상 form 미연결인지 미확정.
  → CANDIDATE 강등
```

---

## STEP-2: VALID 전수 재검토 (4단계: 결과→역추적→소스→재현) → VALID_LOCK

```
V-01 compiler_core 경로
  결과(engine_version=v3.0-compiler-core-anonymous)→역추적(WO-003)
  →소스(run_anonymous_diagnosis)→재현(스모크 동일) ✓✓✓✓ → VALID_LOCK
V-02 결과 계보 (remarks←law_article.article_title)
  →소스(_load_draft_fallback_context)→재현(211건 human) ✓✓✓✓ → VALID_LOCK
V-03 rule_type 변환 (draft_slot→_ACTION_TO_TASK)
  →소스 확정→재현(분포 정상) ✓✓✓✓ → VALID_LOCK
V-04 표현 정제 (_refine_rules_table)
  →소스→재현(토큰 0건) ✓✓✓✓ → VALID_LOCK
V-05 산업 고유 의무 (작업환경측정/산안법)
  →문장 읽기(주기/시료채취/보존 정상)→재현 ✓✓✓✓ → VALID_LOCK
V-06 sector filter mismatch=0
  →verify 재현(mismatch 0 양섹터) ✓✓✓✓ → VALID_LOCK

★ 6건 전부 VALID_LOCK 승격 = 재조사 금지 목록 등록.
```

---

## STEP-3: UNKNOWN 세분화

```
U-01 건물(BUILDING) 결과       → [환경 부족] engine-test에 건물 프로브 없음
U-02 138 vs rules_table 114    → [정보 부족] dedupe 차이인지 누락인지 미확인
U-03 INSTALL 45 양섹터 동일 이유 → [데이터 부족] draft_slot 레벨 미확인
U-04 penalty/form 설계 의도     → [정보 부족] Step2/penalty 코드 미확인 (F-02/F-03서 강등)
```

---

## STEP-4: CANDIDATE 위험도 평가 (수정영향도/의존성/검증비용)

```
후보              수정영향도  의존성              검증비용
C-01 건설의무누락  높음        draft_slot/binding  높음(GPT, 재실행 필요)
                              (GPT 전담)
C-02 category불일치 중간       compiler_core       중간(_bucket↔category Reading)
C-03 측정기관TRAINING 낮음      조문 주체 판단       낮음(본문 1건 읽기)
C-04 COMMON과다    낮음        presentation        높음(구조)
F-02 penalty(강등) 중간        compiler_core       낮음(코드 1곳 확인)
F-03 form(강등)    중간        compiler_core       낮음
```

---

## STEP-5/6: 5개 레지스터 (최종)

### FACT REGISTER (확정 오류, 단 수정소관 분리)
```
F-01 Sector 오염 (소방 NFPC 미매핑 93%)
   = 유일하게 살아남은 FACT. 단 수정 = law_sector_mapping(데이터) + 법령해석(GPT).
   compiler_core 무관 = 독립.
```

### VALID_LOCK REGISTER (재조사 금지)
```
V-01 compiler_core 경로
V-02 결과 계보 (article_title)
V-03 rule_type 변환
V-04 표현 정제
V-05 산업 고유 의무
V-06 mismatch=0 (섹터 누수 차단)
→ 이 6건은 다시 조사하지 않는다.
```

### NOT_ERROR REGISTER (오류처럼 보였으나 설계상 정상)
```
N-01 compiler_core가 4세대 중 하나만 쓰는 것
   = 곁가지(V4/legal_runtime/v510/legacy) 미사용은 설계상 정상(Canonical 고정 완료).
N-02 result_data를 JSONB 통째 저장
   = 정규화 테이블 아닌 full_result JSONB는 설계 의도(정제레이어가 읽음).
N-03 remarks가 법조문 제목인 것
   = "보고하여야"가 아니라 article_title 노출은 의도된 표현(토큰 회피).
N-04 temp-factory 생성 후 삭제
   = create_temp_factory→cleanup은 anonymous 진단의 설계된 lifecycle.
N-05 mismatch=0 / unmapped만 경고
   = sector filter가 "잘못된 섹터 차단(mismatch)"과 "미매핑 통과(unmapped)"를
     구분하는 것은 설계 의도(누락 방지 우선).
```

### CANDIDATE REGISTER (검증 후 수정)
```
C-01 건설 의무 누락 (GPT binding)
C-02 category 분류 불일치
C-03 측정기관 TRAINING 분류
C-04 COMMON 과다
F-02 penalty 미연결 (강등, 설계의도 확인 필요)
F-03 form 미연결 (강등)
```

### UNKNOWN REGISTER
```
U-01 건물 섹터 (환경부족)
U-02 138 vs 114 (정보부족)
U-03 INSTALL 동일 이유 (데이터부족)
U-04 penalty/form 설계의도 (정보부족)
```

---

## 다음 작업 진입 조건 (FACT 중 수정 가능 항목)

```
조건: 의존성 없음 + 영향범위 명확 + 수정 후 검증 가능

충족 항목: F-01 (Sector 오염)
  - 의존성: compiler_core 무관 (law_sector_mapping 데이터만) ✓
  - 영향범위: 명확 (소방 100개 미매핑 → 섹터 등록) ✓
  - 검증: verify unmapped 30 → 감소 확인 가능 ✓
  단 "어느 소방법이 어느 섹터" = 법령해석 = GPT 선행 필요.

→ 수정 대상이 사장님 예측대로 단 1건(F-01)으로 좁혀짐.
  F-02/F-03는 설계의도 확인(UNKNOWN U-04) 후에야 FACT 재승격 가능.
```

---

## 성공 기준

```
- FACT 재검토 (F-01 유지, F-02/F-03 강등)        → ✅
- VALID 4단계 검증 → 6건 VALID_LOCK              → ✅
- UNKNOWN 세분화 (정보/환경/데이터 부족)          → ✅
- CANDIDATE 위험도 평가                          → ✅
- NOT_ERROR 신설 (5건)                           → ✅
- 5개 레지스터 작성                              → ✅
- 수정 0건                                       → ✅
```

---

## 완료 문장

```
4개 레지스터를 재검토하여 5개(FACT/VALID_LOCK/NOT_ERROR/CANDIDATE/UNKNOWN)로
정제하였다. 반례 검증으로 F-02(penalty)·F-03(form)을 CANDIDATE로 강등하고,
VALID 6건을 4단계 검증 완료로 VALID_LOCK 승격(재조사 금지)하였다.
설계상 정상인 5건을 NOT_ERROR로 분리하였다.
수정 가능한 확정 오류는 F-01(Sector 오염) 단 1건으로 좁혀졌으며,
이마저 "어느 소방법이 어느 섹터"라는 법령해석(GPT) 선행이 필요하다.
수정은 수행하지 않았다.
```
