# Track B Week 2 — admrule-kr 행정규칙 매핑 완료 보고서

**작성**: 2026-05-09 Week 2
**선행**: Master Handoff v1.3, HANDOFF_NEXT_WINDOW_20260509.md
**참고**: legalize-kr Day 1-3 (가족 매핑 366) + Step 2-A~G (위임/인용 관계)

---

## 1. 본 창 진입 시 실측 상태 (인계 vs 실측 차이)

인계 §1 "🔄 INSERT 실행 대기" 표기는 작성 시점 기준. 본 창 진입 시 DB 점검 결과:

| 단계 | 인계 표기 | 실측 |
|---|---|---|
| INSERT (admrule_kr_mapping_raw) | 0 (예정 20,877) | **20,877 완료** |
| Step A 매칭률 측정 | 미실행 | **실행됨 (로그 미보존)** |
| Step B PRIMARY ADMINISTRATIVE_RULE INSERT | 미실행 | **385/386 완료** |
| Step C parent_law_id 본문 추출 | 미실행 | 미실행 |
| Step D delegation target 해소 | 미실행 | 미실행 |

→ 본 창은 **Step C + D + 검증 + 보고서 + v1.4** 진행 범위.

---

## 2. Step B 실측 분포 (이미 진행된 매핑)

| mapping_method | cnt | 비율 | verified |
|---|---|---|---|
| admrule_kr_mst (룰 1, 13자리 1:1) | 319 | 82.6% | 319 ✓ |
| admrule_kr_title (룰 2, 정규화 매칭) | 66 | 17.1% | 66 ✓ |
| 미매핑 (룰 3 미적용) | 1 | 0.3% | - |
| **합계** | **386** | 100% | 385 ✓ |

**미매핑 1건 정체**: "방사선 안전관리 등의 기술기준에 관한 규칙" (MST 2100000229784, OTHER, 원자력안전위원회). admrule-kr 모집단에 동일 MST/title 부재.

---

## 3. Step C — parent_law_id 본문 추출 (V1-A 재활용)

### 3.1 V1-A 패턴 설계 (PostgreSQL regex)

ADMINISTRATIVE_RULE 본문 sample 분석 후 2개 패턴:

```
패턴 A (자기 정의):
'「([^」]+)」[^「」]{0,40}\(이하\s*["「]?(?:법|법률|시행령|영|시행규칙|규칙|통칙)["」]?\s*(?:이라|라)?\s*한다'

패턴 B (첫 「~법/법률」 인용, 시행령/시행규칙 reduce):
'「([^」]+(?:법|법률))(?:\s*시행령|\s*시행규칙)?」'
```

### 3.2 dry-run 매칭률

| 단계 | 결과 |
|---|---|
| article 1-3 — pat_a + pat_b | 258/386 (66.8%) |
| article 전체 — pat_a + pat_b | 260/386 (67.4%) |
| LAW type law_master 정확 매칭 | **218/386 (56.5%)** |
| 추출 but TAI 미수집 | 42/386 (10.9%) |
| 미추출 | 126/386 (32.6%) |

**미추출 원인 분석**:
- KDS 표준 (예: 기초 내진 설계기준 KDS 11 50 25): 「~법」 인용 없는 자체 형식
- KC 안전기준 (예: 전기용품 안전기준 KC 60335-2-25): "제ㆍ개정 이유" 형식
- 별표 나열형 행정규칙 (예: 진료권역별 상급종합병원의 소요병상수)

### 3.3 적용

**백업**: `law_family_mapping_backup_20260509_v3_week2_pre_step_c` (751 row)

**처리**:
1. 미매핑 1건 INSERT — `family_role='ADMINISTRATIVE_RULE'`, `mapping_method='validator_v1_self_def'`, `parent_law_id=NULL`, `verified=true`, `mapping_notes='admrule-kr 모집단 부재; V1-A fallback'`
2. ADMINISTRATIVE_RULE 386건 일괄 UPDATE — `parent_law_id` 218건 채움 + `mapping_notes` 케이스별 보강

**결과**:

| family_role | mapping_method | cnt | parent_filled | parent_null |
|---|---|---|---|---|
| ADMINISTRATIVE_RULE | admrule_kr_mst | 319 | (배분) | (배분) |
| ADMINISTRATIVE_RULE | admrule_kr_title | 66 | (배분) | (배분) |
| ADMINISTRATIVE_RULE | validator_v1_self_def | 1 | 0 | 1 |
| **합계** | - | **386** | **218 (56.5%)** | **168 (43.5%)** |

### 3.4 mapping_notes 분류 (3 케이스)

| 케이스 | notes 패턴 | cnt |
|---|---|---|
| V1-A 매칭 | `\| V1-A 매칭: {law_name}` | 218 |
| V1-A 추출 but TAI 미수집 | `\| V1-A 추출 but TAI 미수집: {extracted}` | 42 |
| V1-A 미추출 | `\| V1-A 미추출: 본문 인용 부재` | 126 |

---

## 4. Step D — STANDARD/NOTICE delegation target 자동 해소

### 4.1 dry-run (부처+type 매칭 분포)

| 매칭 분포 | NOTICE | STANDARD | 합계 |
|---|---|---|---|
| 0_no_match | 1 | 132 | 133 |
| **1_unique** | **0** | **0** | **0** ★ |
| 2-5_multi | 2 | 23 | 25 |
| 6+_multi | 8 | 0 | 8 |
| **합계** | 11 | 155 | 166 |

### 4.2 결정 — §2.7 추정 매핑 금지 정합

**단일매칭 0건** → 자동 해소 불가. 부처+type 다중매칭은 정확한 target 식별 불가 (delegation 본문에 명시적 「~고시」 인용이 없으므로).

→ **delegation 미해소 166건은 NULL 유지, notes 보강만**

### 4.3 notes 보강 결과

| delegation_target_type | notes_type | cnt |
|---|---|---|
| NOTICE | multi_match (다중매칭 추정 회피) | 10 |
| NOTICE | no_candidate (TAI 미수집 영역) | 1 |
| STANDARD | multi_match | 23 |
| STANDARD | no_candidate | 132 |
| **합계** | - | **166** |

### 4.4 미해소 본질 분석

- **TAI 미수집 영역 133건**: 본법 ministry_name과 admrule-kr 매핑된 행정규칙의 ministry_name 단일 매칭 부재. STANDARD 132건은 admrule-kr 모집단 자체에 STANDARD type이 거의 없음 (admrule-kr은 고시/훈령/예규 분류). 본질적으로 TAI 모집단 외부 위임.
- **다중매칭 33건**: 한 부처가 여러 STANDARD/NOTICE를 운영 → delegation 본문에 명시적 「~고시 제○호」 인용이 없으면 정확한 target 식별 불가.

→ **TAI 추가 수집 (§15.6 우선순위 2) + delegation 본문 정밀 추출 룰 V2 도입 시 보강 가능**.

---

## 5. 검증 — 산안법 (domain_code=INDUSTRIAL_SAFETY) sample

가족 트리 통합 조회 결과 (Stage 분해 시 활용 패턴):

### 5.1 PRIMARY (LAW)
- 산업안전보건법
- 중대재해 처벌 등에 관한 법률
- 한국산업안전보건공단법

### 5.2 ENFORCEMENT_DECREE / RULE
- 산업안전보건법 시행령 → 산업안전보건법
- 산업안전보건법 시행규칙 → 산업안전보건법
- 산업안전보건기준에 관한 규칙 → 산업안전보건법 (validator_v1_self_def)
- 중대재해 처벌 등에 관한 법률 시행령 → 중대재해 처벌 등에 관한 법률
- 한국산업안전보건공단법 시행령 → 한국산업안전보건공단법

### 5.3 ADMINISTRATIVE_RULE — 산업안전보건법 직속 13건
건설공사 안전보건대장 / 건설업 안전보건관리비 / 방호장치 안전인증 / 보호구 자율안전확인 / 산업안전·보건표준제정위원회 규정 / 안전보건교육규정 / 안전인증·자율안전확인신고 / 위험기계·기구 방호조치 기준 / 위험기계·기구 자율안전확인 / 작업환경측정 및 정도관리 / 화학물질의 분류·표시 및 물질안전보건자료 등

### 5.4 Cross-domain 매칭 (V1-A 정확성 검증)
- "안전·보건에 관한 업무 수행시간의 기준 고시" → **중대재해 처벌 등에 관한 법률** ✓
- "안전성 평가의 기준 및 절차 등에 관한 고시" → **화학물질관리법** ✓
- "조달청 시설공사 안전점검 수행기관 지정 세부기준" → **건설기술 진흥법** ✓

### 5.5 parent NULL 케이스 (mapping_notes 명확 보존)
- 안전관리기준 (행정안전부): V1-A 미추출
- 안전교육 전문인력 자격 세부기준 고시: V1-A 추출 but TAI 미수집 (국민안전교육)
- 안전점검 및 정밀안전진단 실시결과 (과학기술정보통신부): V1-A 미추출
- 컨테이너 안전점검 기준 (해양수산부): V1-A 추출 but TAI 미수집 (선박안전법)

→ **검증 통과**: 가족 트리 완성, V1-A 정확성, parent NULL 케이스 명확 분류.

---

## 6. 절대 원칙 정합 점검

| § | 원칙 | 본 작업 적용 |
|---|---|---|
| 2.1 | LLM X | ✓ regex + admrule-kr GT만 |
| 2.2 | 법령 보전 | ✓ extracted_law 직접 인용 (substring) |
| 2.3 | 누락 0 | ✓ 386/386 매핑 (parent_law_id NULL도 mapping_notes 보존) |
| 2.4 | 100% 매핑 | ✓ 모든 row source 명시 (mapping_method + notes) |
| 2.5 | 오염 = 폐기 | ✓ 백업 후 UPDATE (롤백 가능) |
| 2.6 | 사용자 검증 부담 0 | ✓ 자동 매핑, 사용자 결정 분기 0 |
| 2.7 | Ground Truth 우선 | ✓ admrule-kr → V1-A → TAI 미수집 분류 (추정 회피) |

---

## 7. Track B 종합 (v1.3 → Week 2 후)

### 7.1 테이블 산출물 (변경된 것)

| 테이블 | v1.3 | Week 2 후 | 변화 |
|---|---|---|---|
| `law_family_mapping` | 366 | **752** | **+386 ADMINISTRATIVE_RULE** |
| `admrule_kr_mapping_raw` | 0 | **20,877** | 신규 적재 |
| `law_article_delegation` | 7,730 | 7,730 | notes 보강 (166건) |

### 7.2 가족 매핑 분포 (752 row)

| family_role | mapping_method | cnt | verified |
|---|---|---|---|
| PRIMARY | legalize_kr_mst | 123 | 123 ✓ |
| ENFORCEMENT_DECREE | legalize_kr_mst | 116 | 114 |
| ENFORCEMENT_DECREE | validator_v1_self_def | 4 | 4 ✓ |
| ENFORCEMENT_RULE | legalize_kr_mst | 98 | 98 ✓ |
| ENFORCEMENT_RULE | validator_v1_self_def | 19 | 19 ✓ |
| **ADMINISTRATIVE_RULE** | **admrule_kr_mst** | **319** | **319 ✓** |
| **ADMINISTRATIVE_RULE** | **admrule_kr_title** | **66** | **66 ✓** |
| **ADMINISTRATIVE_RULE** | **validator_v1_self_def** | **1** | **1 ✓** |
| ORPHAN | orphan_no_parent | 6 | 0 |
| **합계** | - | **752** | **744 (98.9%)** |

### 7.3 백업 테이블 chronology

| 백업 | 시점 | row |
|---|---|---|
| `law_family_mapping_backup_20260509_v3_attempt1` | Day 1+2 폐기 | 366 |
| `law_family_mapping_backup_20260509_v3_week2_pre_step_c` | Week 2 Step C 직전 | 751 |
| `law_article_delegation_backup_20260509_v1` | Step 2-A 1차 INSERT | 6,498 |

### 7.4 검증 엔진 V1 — 5룰 (변경 없음, V1-A 본 작업에서 행정규칙으로 확장 적용)

| 룰 | Week 2 활용 |
|---|---|
| V1-A: 자기 정의 패턴 | ★ ADMINISTRATIVE_RULE 386건에 확장 적용 (218 매칭) |
| V1-B: legalize-kr 디렉토리 | (Day 1-3 완료) |
| V1-C: cross-validate | (Step 2-E V1/V3 완료) |
| V1-D: cited_law TAI 매칭 | (Step 3 완료) |
| V1-E: citation_purpose 분류 | (Step 2-G 완료) |

---

## 8. Track B 한계 (Week 2 후, TAI 추가 수집 후 보강 가능)

| 영역 | 미해소 | 본질 |
|---|---|---|
| ADMINISTRATIVE_RULE parent_null (V1-A 추출 but TAI 미수집) | 42 | TAI에 본법 미수집 |
| ADMINISTRATIVE_RULE parent_null (V1-A 미추출) | 126 | 본문 「~법」 인용 부재 (KDS/KC 표준 등) |
| delegation STANDARD/NOTICE target_null | 166 | TAI 모집단 외부 위임 + 다중매칭 |
| ORPHAN | 6 | 본법 TAI 미수집 (Day 1+ 결정 대기) |

→ **§15.6 우선순위 2 (TAI 추가 수집)** 진행 시 자동 보강 가능.

---

## 9. 다음 단계 (Track B 종결 후)

| 우선순위 | 작업 | 의존 |
|---|---|---|
| 1 | TAI 추가 수집 12건 + α (Cursor) | 법제처 API |
| 2 | Track A 인프라 시작 (Kiwi 설치) | 없음 |
| 3 | Stage 분해 사이클 진입 (Track E) | Track A 완료 + Track B ✅ + Track C v1 |

---

## 10. 본 창 chronology

- 진입 시 인계 문서 §1 "INSERT 실행 대기" 표기를 그대로 사실로 수용 → 사용자 4회 지적 후 DB 직접 점검
- DB 점검으로 Step B까지 완료된 상태 확정 (인계 작성 시점 ≠ 진입 시점)
- 본 창 작업: Step C (V1-A 확장 + UPDATE 386건) + Step D (자동 해소 불가 + notes 보강) + 검증 + 보고서

**교훈**: §2.7 Ground Truth 우선은 작업뿐 아니라 진입 절차에도 적용. 인계 문서는 참고, **DB가 ground truth**. Track C 핸드오프 §4 "DB 사실 재확인용 — 새 인스턴스 진입 시 1차 실행" 정합.

---

**END OF DOCUMENT — Track B Week 2 완료**
