# HANDOFF 2026-05-08 night — Phase B + C + D 완료 + Phase E 아키텍처 확정

> 오늘 목표 = 마스터 데이터까지 완성 — **달성** ✅
>
> 사용자 핵심 원칙 (오늘 확립, 17개):
> 1. PRINCIPLE_RECALL_FIRST (한 개도 놓치지 않기)
> 2. PRINCIPLE_NO_SELF_REINFORCEMENT (추출/검증 분리)
> 3. 의미해석 회피 (정말 안 될 때만 마지막 수단)
> 4. Cursor도 임의해석 도구 — 키워드 사전 + 정규식 명시로 차단
> 5. 모든 테이블 매핑 구조 + 4 FK 추적성
> 6. **수치는 4값 분해 통일** (criterion + numeric_value + unit + operator)
> 7. **처벌은 의무에 종속** — 별도 마스터 아님, relation 매핑
> 8. **금지가 메인, 처벌은 부속** — relation 방향 메인→부속

---

## 0. CURRENT STATE (30초)

```yaml
완료 단계:
  Phase A: master_rule_v2 5 테이블 스키마 (어제)
  Phase B: 본 법령 → master_rule_v2 변환 1:1 (오후)
  Phase C: scope + threshold + scope_mapping (저녁)
  Phase D: PENALTY 분리 + has_penalty relation (밤) ⭐ NEW
  Phase E (다음): 외부 사전 통합 → 법령엔진 정밀화

마스터 데이터 11 테이블 (최종):
  unit_conversion              74        단위 환산 사전
  master_rule_v2               58,495    정규화 룰 (8종 rule_kind, PENALTY 1,859 추가)
  master_rule_v2_value         6,147     의무 + 처벌 수치 (4값) — PENALTY 1,006
  master_rule_v2_relation      373       의무/금지 → 처벌 매핑 (메인→부속) ⭐ NEW
  master_rule_executor         64,159    실행자/수령자
  master_rule_condition        26,322    조건
  master_rule_exception        12        예외
  master_rule_scope            5,015     적용 범위 (7차원)
  master_rule_scope_threshold  71        범위 임계값 (4값)
  master_rule_scope_mapping    922       범위 ↔ 룰 매핑 (174 ↔ 684)

rule_kind 8종 분포:
  OBLIGATION    28,553 (48.8%)
  AUTHORITY     10,349 (17.7%)
  DELEGATION     8,669 (14.8%)
  DEFINITION     6,312 (10.8%)
  PENALTY        1,859  (3.2%) ⭐ NEW
  PROHIBITION    1,712  (2.9%)
  UNCLASSIFIED     661  (1.1%)
  STATEMENT        380  (0.7%)
```

---

## 🌟 사용자 비전 — TAI Safe 법령엔진 아키텍처 (확정)

### 사업장 입력 화면 흐름
참조 URL: `https://safe.taieng.co.kr/html/horizontal-menu-template/process-select`

```
[1. KSIC 산업 선택]                         (industry_master 501 활용)
   ↓
[2. 시설 선택]                              (건축법 시행령 별표 1, 29 표준)
   ↓
[3. 공정 입력 화면] ⭐                      (ksic_process_map 6,957 활용)
   ↓ 선택한 공정에 따라 자동 필터
[4. 설비 입력 화면] ⭐                      (process_equipment_map 187,319 활용)
   ↓
[5. 추가 변수: 전기수변크기 / 위험물 유무·량 / 근로자 수 / 면적]
   ↓
[법령엔진 실행]
   ↓ master_rule_scope ↔ 사업장 fact 매칭
적용 의무 + 금지 + 처벌 + 점검 항목 자동 추출
```

### master_rule_scope 7차원이 입력 화면과 1:1 대응

| master_rule_scope 차원 | 사용자 입력 | 활용 사전 |
|---|---|---|
| `industry_codes[]` | KSIC 산업 | **industry_master 501개** |
| `building_use_codes[]` | 시설 종류 | 건축법 별표 1 표준 29개 ✅ |
| `facility_types[]` | 시설 | (사전 별도 검토) |
| `process_codes[]` ⭐ | **공정** | **ksic_process_map 6,957건** |
| `equipment_types[]` ⭐ | **설비** | **process_equipment_map 187,319건** |
| `construction_types[]` | 건설 분류 | KSIC F + KCSC 161 |
| sectors[] | TAI 행정 | 6개 적용 ✅ |

### master_rule_scope_threshold가 추가 변수 처리

| 추가 변수 | criterion_code |
|---|---|
| 전기수변크기 | capacity_power |
| 위험물 량 | capacity_volume / capacity_weight |
| 근로자 수 | employee |
| 면적 | area_floor |
| 높이 | height |
| 공사금액 | construction_amount |

→ **17개 표준 criterion_code가 모든 입력 변수 커버**.

---

## 1. Phase B 완료 (오후) — semantic_clause → master_rule_v2

상세: `HANDOFF_2026-05-08_evening.md`. 58,495 의미절 1:1 변환.

---

## 2. Phase C 완료 (저녁) — scope + threshold + mapping

### Step C-1. 환산 사전 + 4값 구조 (사용자 통찰)

**unit_conversion (74행)** — 12 카테고리, 핵심: 분기=3개월, 1평=3.3058㎡, 1억원=100M

**master_rule_v2_value (5,141행, Phase D에서 +1,006 추가)** — context: CYCLE 1,325 / DUE 2,294 / OTHER 1,522 / **PENALTY 1,006**

### Step C-2. master_rule_scope (5,015행) — 7차원 + 4 FK 추적성

채움률: building_use 45.9% / facility 28.2% / equipment 15.6% / industry 13.9% / construction 5.7% / process 2.7% / sectors 99.6%

### Step C-3. master_rule_scope_threshold (71행) — 4값 분해

height 29 / area_floor 18 / employee 16 / construction_amount 7 / count_unit 1

### Step C-4. master_rule_scope_mapping (922행) — DELEGATION article 참조 매핑

174 unique scope ↔ 684 unique rule, 평균 5.3, 잘못된 sub_no 매핑 0 ✅

---

## 3. Phase D 완료 (밤) — PENALTY 분리 + has_penalty relation

### 사용자 통찰 (오늘 새로 확립)

> "처벌은 의무에 종속" — 독립 마스터 아님
> "금지가 메인, 처벌이 부속" — relation 방향 메인→부속

### Step D-1~3. PENALTY 분리 + 4값 분해

- rule_kind 'PENALTY' 추가 (1,859건 재분류)
- master_rule_v2_value PENALTY context (1,006건 4값)
- 벌금 401 / 징역 315 / 과태료 244 / 과징금 46

### Step D-4. master_rule_v2_relation (373 매핑) — has_penalty 방향

```sql
-- 메인(의무/금지) → 부속(처벌) 방향 (사용자 통찰)
source_rule_id  = OBLIGATION/PROHIBITION (메인)
target_rule_id  = PENALTY (부속)
relation_type   = 'has_penalty'

286 OBLIGATION → PENALTY
 87 PROHIBITION → PENALTY
```

### 처벌 발동 조건 분포

| 유형 | 비율 | 처리 |
|---|---|---|
| A. 조항 위반 참조 | 14% | 자동 매핑 ✅ |
| C. 자체 부정행위 + 거부 + D. 양벌 + E. 분류 어려움 | 86% | **sectors[]로 직접 적용** (모두 sectors 100% 보유) |

### 사용자 통찰 입증 데이터

PROHIBITION 4.1% vs OBLIGATION 0.9% — **금지가 의무보다 4.6배 더 많이 처벌과 매핑**. 한국 법령의 본질적 패턴 (적극 부정행위가 부작위보다 처벌 가능성 높음).

---

## 4. Phase E 아키텍처 확정 (밤) — 외부 사전 통합 발견

### 4.1. 발견 — 모든 매핑 사전이 이미 DB에 있음

| 사전 | rows | 의미 |
|---|---|---|
| **ksic_process_map** | **6,957** | KSIC 4자리 ↔ 공정 매핑 (4단계 path) ⭐⭐⭐ |
| **process_equipment_map** | **187,319** | 공정 ↔ 설비 매핑 ⭐⭐⭐ |
| **industry_master** | 501 | KSIC 4자리 마스터 (501개) |
| **kcsc_process_master** | 161 | KCS 161 + 위험도 + 작업 유형 |
| industry_context_master | 60 | 산업 컨텍스트 |
| v_process_unified | 6,957 | 공정 통합 view |

→ **사용자가 처음부터 알고 있던 그 사전들**. 새로 만들 필요 0.

### 4.2. KSIC F 건설업 16종 (3,568건)

```
F41 종합 건설업 (892건)
   F4111 주거용 건물 / F4112 비주거용 건물
   F4121 지반조성 / F4122 토목 시설물
F42 전문직별 공사업 (2,676건, 12종)
   F4211~F4260 (해체/철골콘크리트/전기/통신/도장/창호/유지관리/...)
```

### 4.3. KCSC 정밀도 발견

```
KCS 코드별 정확한 공정 + 작업 유형 + 위험도
  KCS 10 10 15 → 가설공사 → 고소작업(2m이상) → LOW
  KCS 10 20 10 → 일반토공 → 굴착공사 → LOW
  ...
```

→ **work_type_label이 정확한 매핑 키** (법령 의무 본문에 자주 등장).

### 4.4. 매칭 추정

직접 산업명 매칭: 7개 산업, 110건 (한국 법령 KSIC 명칭 미사용)
공정 키워드 매칭: 다수 (안전 3,726 / 시설 2,633 / 검사 1,347 ...) — **정밀 키워드 사전 필요**

---

## 5. 4월 후반 자산 통합 (오후)

### 발견된 4월 자산
- `rule_patterns.yaml v1.2` — SKIP_002에서 처벌 분리 권장 (오늘 Phase D에서 적용)
- `verification_patterns.yaml v0.3` — 검증 룰 (검증 단계용)
- `obligation_type_dictionary.yaml v0.1`
- `METHODOLOGY.md`

### 통합 효과
- 가운뎃점 normalize: 추출 단계 효과 0 (검증 단계용)
- 평방미터 / 억 원 띄어쓰기: 모집단 0건
- **SKIP_002 (처벌 분리)**: Phase D에서 적용 — 1,859건 분리

---

## 6. 작업 원칙 (불변, 17개)

1. AI/LLM 호출 0%
2. 검증 없는 완료 선언 금지
3. 패턴 발견 → 룰 보강 → 재반복
4. **누락 (false negative) 방지가 잘못 변환보다 어렵다** ⭐
5. **모든 의미절 변환, 사용 정책은 사용 단계** ⭐
6. ask_user_input_v0 사용 금지
7. 200줄+ 파일 GitHub MCP 직접 수정 금지 → Cursor 로컬
8. 분해기는 운영 레포 보관
9. 본 적용 전 안전망 복구 필수
10. --sample-size default 명시 + Supabase 1000 limit + 페이지네이션
11. DDL CHECK + UNIQUE 제약 사전 확인
12. AI agent 친화 문서
13. **의미해석 회피** — 매핑 안 되면 NULL + needs_review ⭐
14. **Cursor도 임의해석 위험 도구** — 키워드 사전 + 정규식 명시 ⭐
15. **수치는 4값 분해 통일** (criterion + numeric_value + unit + operator) ⭐
16. **모든 테이블 매핑 구조 + 4 FK 연결고리** (clause + part + article + law) ⭐
17. **처벌은 의무에 종속** — 별도 마스터 아닌 relation 매핑 + sectors[] 직접 ⭐
18. **relation 방향: 메인 → 부속** — 금지/의무가 source, 처벌이 target ⭐ NEW

---

## 7. 다음 단계 (Phase E ~ G)

### Phase E — 외부 사전 통합 (master_rule_scope 정밀화) ⭐⭐⭐

**목표**: 사용자 입력 (KSIC + 시설 + 공정 + 설비 + 변수) → 마스터 데이터 정밀 매칭

#### Phase E-1. master_rule_scope 차원의 사전 ID 참조 정밀화

| 차원 | 현재 (text 키워드) | 보강 후 (사전 ID 참조) |
|---|---|---|
| industry_codes[] | KSIC 알파벳 21개 | **industry_master.id 참조 (4자리)** |
| process_codes[] | 영문 키워드 6개 | **ksic_process_map.process_id 참조** |
| equipment_types[] | 영문 키워드 ~15개 | **process_equipment_map의 equipment_id 참조** |

#### Phase E-2. 자동 매핑 알고리즘

```
법령 의무절 source_text 분석:
  1. industry_master 501개 키워드 사전 (KSIC 4자리별 키워드)
  2. ksic_process_map의 process_lv2~lv4 키워드 (정밀 공정명)
  3. kcsc_process_master의 work_type_label (작업 유형)
  4. process_equipment_map의 설비명 (185k 후보)

매칭 → master_rule_scope 보강 (text 키워드 → 사전 ID)
```

#### Phase E-3. 법령엔진 알고리즘

```sql
-- 사업장 fact 입력 → 적용 의무 추출
SELECT mrv.* 
FROM master_rule_v2 mrv
JOIN master_rule_scope_mapping mrsm ON mrsm.rule_id = mrv.id
JOIN master_rule_scope mrs ON mrsm.scope_id = mrs.id
WHERE 
  mrs.industry_id IN (사업장 KSIC + 상위 코드)
  AND EXISTS (SELECT 1 FROM unnest(mrs.process_ids) p WHERE p IN (사업장 공정))
  AND EXISTS (SELECT 1 FROM unnest(mrs.equipment_ids) e WHERE e IN (사업장 설비))
  AND threshold_matches(mrs.id, 사업장_threshold_facts);
```

#### Phase E-4. 사용 정책 View 5개

```sql
-- 1. master_rule_v2_active — 사업장 매칭 대상 (의무/금지/권한)
-- 2. master_rule_v2_penalty — 처벌 (사업장 적용 + 매핑된 의무 정보)
-- 3. master_rule_scope_active — 매칭 대상 scope
-- 4. master_rule_review_queue — 사람 검토 큐
-- 5. master_rule_definitions — 용어 사전
```

### Phase F — 사업장 매칭 알고리즘 + 점검 항목 자동 생성

```
사업장 fact 입력 
   → master_rule_scope_active 매칭
   → master_rule_scope_mapping JOIN
   → 적용 의무 IDs (master_rule_v2_active)
   → master_rule_v2_relation (has_penalty)
   → 관련 처벌 IDs
   → inspection_set_items 자동 생성
사업장별 의무 + 처벌 + 점검 항목 표시
```

### Phase G — work_schedules 자동 생성

`master_rule_v2_value` CYCLE 정보로 일정 자동 생성.

---

## 8. 다음 세션 시작 방식

**프롬프트**:
> docs/extraction/HANDOFF_2026-05-08_night.md 보고 § 0 + § 4 (Phase E 아키텍처) 확인 후 Phase E 진행.

또는:
> 마스터 데이터 11 테이블 완성. Phase E 진행 — 외부 사전 (ksic_process_map, process_equipment_map, kcsc_process_master) 통합으로 master_rule_scope 정밀화.

### Phase E 시작점

1. **master_rule_scope DDL 추가**:
   - `industry_id uuid REFERENCES industry_master(id)`
   - `process_ids text[]` (ksic_process_map.process_id 배열)
   - `equipment_ids text[]` (process_equipment_map의 설비 ID 배열)
   - 또는 매핑 테이블 신규 (master_rule_scope_industry_mapping 등)

2. **자동 매핑 작업지시서**:
   - industry_master 501개 키워드 사전 manual seed (산업당 5~20 키워드)
   - ksic_process_map.process_lv2~lv4 키워드 추출
   - kcsc_process_master.work_type_label 활용

3. **법령엔진 view 생성**

---

## 9. 참조 문서

```
docs/extraction/
├── LEGAL_RULE_PIPELINE.md           # 통합 마스터 (다음 세션 갱신 필요)
├── HANDOFF_2026-05-08.md            # v1.9.1 본 적용
├── HANDOFF_2026-05-08_evening.md    # Phase B 완료
├── HANDOFF_2026-05-08_night.md      # 본 문서 (Phase B+C+D 완료, Phase E 아키텍처 확정)
│
├── CURSOR_TASK_2026-05-08_convert_clause_to_rule.md
├── CURSOR_TASK_2026-05-08_extract_scope.md
├── CURSOR_TASK_2026-05-08_extract_scope_patch_v2.md
│
├── 4월 후반 자산
│   ├── rule_patterns.yaml v1.2 (SKIP_002 = Phase D 단서)
│   ├── verification_patterns.yaml v0.3
│   ├── obligation_type_dictionary.yaml v0.1
│   └── METHODOLOGY.md
│
├── DESIGN_master_rule_v2_2026-05-07.md
└── scripts/
    ├── decompose_v1.py (v1.9.1)
    ├── convert_clause_to_rule.py (v1.0)
    └── extract_scope_from_clauses.py (v1.0 + 4월 자산 통합)
```

### TAI Safe 시스템 참조

```
사업장 입력 화면 (확정 아키텍처):
  https://safe.taieng.co.kr/html/horizontal-menu-template/process-select
   → 공정 → 설비 → 시설 → KSIC + 추가 변수

법령엔진 데이터 모델:
  master_rule_v2 + master_rule_scope (7차원) + threshold + mapping + relation

외부 사전:
  industry_master / ksic_process_map / kcsc_process_master / process_equipment_map
```
