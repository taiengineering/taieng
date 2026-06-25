# WO-THRESHOLD-QUALITY-001
# THRESHOLD 별표 확장 (숫자 입력 기반 의무)

**작성일:** 2026-06-25 | **상태:** 완료 (품질 개발 — ① Applicability 내부)
**헌법:** WO-ARCHITECTURE-FREEZE-001 준수

## Boundary Check (헌법 TASK-007)

```
Applicability 내부 작업인가?    YES  (① THRESHOLD 확장)
Boundary 변경 필요한가?         NO
Data Contract 변경 필요한가?    NO
Breaking Change인가?            NO
→ 전부 통과. Architecture Review 불필요.
```

---

## 결론 먼저

```
has_* 없이 worker_count만으로 obligation_instance 증가 달성.

factory e9c56af6 (worker 280):
  기존 95건 → 96건 (+1, 안전관리자 선임)
    UNIVERSAL 93 + THRESHOLD 3

THRESHOLD CONFIRMED: 2 → 3건
  worker≥20 안전보건관리담당자 (기존)
  worker≥50 산업보건의 (기존)
  worker≥50 안전관리자 선임 (신규 — 별표3 위임 본조 연결) ★

→ 숫자 입력만으로 실제 의무 증가. 성공 기준 달성.
→ 근거 확실한 것만 보수적 적재 (보건관리자/500/1000 보류).
```

---

## TASK-001: 기존 THRESHOLD 재확인

```
worker_count >= 20 → 안전보건관리담당자 (시행령 제24조, 본조 명시)
worker_count >= 50 → 산업보건의 (시행령 제29조, 본조 명시)
둘 다 sector=공통, CONFIRMED.
```

---

## TASK-002: appendix_condition 7건 전수 직독

```
7건 전부 단일 별표(appendix_id 0be28b96 = 별표 3 안전관리자):

  threshold_field: employee_count (= worker_count) ✅ 운영입력 존재
  threshold_operator: >= ✅
  sector: INDUSTRIAL (전부)
  ksic_code: NULL (업종 매칭 불가)

내용:
  employee_count≥50  → 안전관리자 1명  (업종별 4건: 운수창고/식료품제조/토사석광업/그외)
  employee_count≥500 → 안전관리자 2명  (2건)
  employee_count≥1000→ 안전관리자 2명  (1건, 그외 업종)

핵심 직독 판단:
  - 하한 50명(안전관리자 최소 1명 선임 의무 발생)은
    모든 INDUSTRIAL 업종 공통 → ksic 매칭 없이 적용 가능.
  - 500/1000명(2명) 및 업종별 상한은 ksic_code 필요 → 보류.
  - semantic_clause 연결: 별표3 위임 본조 발견 (아래).
```

---

## TASK-003: 안전관리자 별표 기준 — 근거 조문 연결

```
별표3 위임 본조 발견 (직독):
  clause 04f98e27 (source_article_id 6fb01548):
    "법 제17조제1항에 따라 안전관리자를 두어야 하는 사업의 종류와
     사업장의 상시근로자 수, 안전관리자의 수 및 선임방법은 별표 3과 같다."

  → 이 본조가 appendix_condition 7건(별표3)의 모조문.
  → 연결 확정: clause 04f98e27 ← appendix employee_count≥50.

직독으로 걸러낸 함정:
  "안전관리자 선임" 검색 시 대부분 산안법 아님:
    - 액화석유가스(LPG법) / 위험물안전관리법 / 소방법
  → 카운트로 넣었으면 타법 오염. 글 읽기로 산안법 본조만 선별.

보건관리자(별표5):
  OBLIGATION 성격 모조문 부재 (준용 DELEGATION만 존재).
  → "근거 불명확 → 생성 금지" 원칙 → 보류.
```

---

## TASK-004: THRESHOLD 매핑 생성

```
적재 (CONFIRMED, 근거 확실만):
  THRESHOLD:WORKER:SAFETYMGR50:04f9
    input_field: worker_count
    operator: >=  value: 50
    sector: INDUSTRIAL
    clause: 04f98e27 (별표3 위임 본조)
    confidence: 0.90

보류 (근거/업종 부족):
  - 보건관리자 별표5: OBLIGATION 모조문 부재 → 보류
  - 안전관리자 500/1000명(2명): ksic 업종 매칭 필요 → 보류
  - 업종별 상한(499/999): 업종 식별 불가 → 보류

→ "범위 넓히지 말고 숫자로 살아나는 것만" 원칙 준수.
→ 1건만 추가 (보수적).
```

---

## TASK-005: obligation_instance 재생성

```
factory e9c56af6 (INDUSTRIAL, worker 280):

  기존: UNIVERSAL 93 + THRESHOLD 2 = 95
  신규: + 안전관리자 선임 1 (worker 280 ≥ 50)
  ─────────────────────────────
  합계: UNIVERSAL 93 + THRESHOLD 3 = 96

신규 의무 reason (직독 확인):
  "상시근로자 280명 ≥50 → 법 제17조제1항에 따라 안전관리자를
   두어야 한다 (별표 3 — 상시근로자 50명 이상 안전관리자 1명 이상 선임)"
```

---

## TASK-006: Adapter 통과 확인

```
96건 정합성:
  total 96 / article_id 보유 96 / action_text 누출 0
  → candidate 변환 100% 가능.

Adapter 경로 (무변경):
  obligation_instance 96
    → Glue → candidate 96
    → build_obligations_from_trigger_candidates
    → obligations 96

건수 증가 확인: 95 → 96 ✅
Boundary/Data Contract 무변경 ✅
```

---

## 핵심 발견

### 발견 1: 숫자 입력만으로 의무가 늘었다

```
has_* 0개인 factory에서 worker_count=280만으로
안전관리자 선임 의무 추가 생성.
→ EXISTS 입력 수집 없이 진단 증가.
→ THRESHOLD가 "지금 당장 살아나는" 트랙임을 실증.
```

### 발견 2: 별표 위임 본조가 연결 고리

```
appendix_condition(별표 내용) ↔ semantic_clause(위임 본조)는
"법 제17조1항...별표 3과 같다" 모조문으로 연결.
→ 별표 THRESHOLD는 본조-별표 쌍으로 적재해야 근거 완결.
→ clause 04f98e27이 그 본조.
```

### 발견 3: "안전관리자" 다의어 함정 (직독으로만 회피)

```
"안전관리자 선임" 조문 대부분이 산안법 아님:
  LPG법 / 위험물안전관리법 / 소방법.
→ 카운트 기반이면 타법 오염 유입.
→ 별표3 위임 본조(산안법)만 직독 선별.
→ UNIVERSAL 정제와 동일 교훈 재확인.
```

### 발견 4: 보수적 적재가 품질을 지킨다

```
appendix 7건 중 1건(하한 50명)만 적재.
500/1000명·업종별·보건관리자는 보류.
→ ksic 업종 매칭, 보건관리자 모조문은 후속 과제.
→ 근거 불명확분을 넣지 않음 (헌법 원칙).
```

---

## 성공 기준 답변

```
has_* 없이 worker_count/floor_area 등 숫자 입력만으로
실제 obligation_instance가 증가하는가?

✅ 달성.
  worker_count=280 → 안전관리자 선임 의무 추가.
  obligation_instance 95 → 96.
  Adapter 통과 96. Boundary/Contract 무변경.
```

---

## 남은 THRESHOLD 확장 여지

```
1. 안전관리자 500/1000명 (2명 선임)
   - ksic_code 업종 매칭 필요 (현재 NULL)
   - 업종 식별 입력 갖춰지면 적재

2. 보건관리자 (별표5)
   - OBLIGATION 모조문 확보 후 적재
   - 현재 준용 DELEGATION만 존재

3. floor_area / electrical_kw / gas_capacity 기반
   - appendix_condition에 해당 threshold_field 없음
   - 별표 추가 수확 시 확장 (안전검사/위험물 등)

4. PENDING 21건 (UNIVERSAL 정제분)
   - 일부 THRESHOLD 성격 → 재평가 시 편입 가능
```

---

## 다음 단계 (헌법 ① 내부)

```
THRESHOLD: worker_count 축은 본조 명시분 거의 소진.
  더 늘리려면 ksic 업종 매칭 OR 별표 추가 수확.

다음 품질 후보:
  - EXISTS 입력 수집 (가장 큰 미연결, 입력단 동반 — 효과 최대)
  - floor_area/electrical_kw 별표 수확 (안전검사 대상 등)
  - 다른 sector factory 검증 (건설/건물)

→ worker 기반은 천장 근접. 다음은 EXISTS 또는 다축 THRESHOLD.
```

---

*WO-THRESHOLD-QUALITY-001 완료. 품질 개발 — ① Applicability 내부.*
*핵심: worker_count=280만으로 안전관리자 의무 추가 (95→96). 별표3 위임 본조 연결.*
*"안전관리자" 다의어 직독 회피 (LPG/위험물/소방법 오염 차단). 보수적 1건 적재.*
*Boundary/Data Contract 무변경. has_* 없이 숫자로 의무 증가 실증.*
