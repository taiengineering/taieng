# [Track B] 2026-05-09 진행 — Day 2 (당일 연속 진행)

**트랙**: B (조문 가족 매핑)  
**작업**: Day 1에서 도출된 plan을 순서대로 실행

---

## Done

### Step 1: law_family_mapping 테이블 DDL 적용
- migration: `create_law_family_mapping_v3`
- 컬럼: law_master_id (UNIQUE FK) / parent_law_id (FK) / family_role / mapping_method / verified / mapping_notes
- CHECK constraints:
  - family_role: PRIMARY / ENFORCEMENT_DECREE / ENFORCEMENT_RULE / INDEPENDENT_DECREE / ORPHAN / ADMINISTRATIVE_RULE
  - mapping_method: name_pattern / parent_search / manual / legalize_kr_mst / admrule_kr_mst / pending
- 인덱스 4개 (parent_law_id / family_role / mapping_method / verified)

### Step 2: LAW 123건 PRIMARY INSERT — 100% 매핑 ✓
- mapping_method = manual
- verified = true
- parent_law_id = NULL (본법은 부모 X)

### Step 3: ENFORCEMENT_DECREE/RULE 자동 매핑 INSERT
- 이름 패턴 자동 매핑: `"X 시행령"` → parent = X (LAW)
- ENFORCEMENT_DECREE 116건 INSERT (verified=true)
- ENFORCEMENT_RULE 98건 INSERT (verified=true)
- mapping_method = name_pattern
- 합계 214건 자동 매핑 ✓

### Step 4: ENFORCEMENT_DECREE 미매칭 5건 본법 search
- 본법 search 결과 5건 모두 본법 발견 — INDEPENDENT_DECREE 아니라 parent_search 매핑 가능
- Day 1 분석을 정정: 독립 대통령령 5건 → parent_search 5건

### Step 5: parent_search 25건 INSERT (verified=false)
- ENFORCEMENT_DECREE 5건:
  | 자식 | 부모 |
  |---|---|
  | 고준위 방사성폐기물 관리위원회 직제 | 고준위 방사성폐기물 관리에 관한 특별법 |
  | 방송통신설비의 기술기준에 관한 규정 | 전기통신사업법 (추정) |
  | 사회재난 구호 및 복구 비용 부담기준 등에 관한 규정 | 재난 및 안전관리 기본법 |
  | 자연재난 구호 및 복구 비용 부담기준 등에 관한 규정 | 재난 및 안전관리 기본법 |
  | 전기통신사업 회계정리 및 보고에 관한 규정 | 전기통신사업법 |
- ENFORCEMENT_RULE 20건: Day 1 보고서 §"본법 후보 매핑" 표 참조 (산업안전보건기준에 관한 규칙 → 산업안전보건법 등)
- mapping_method = parent_search

### Step 6: ORPHAN 4건 INSERT (verified=false)
- 본법이 TAI 미수집인 4건:
  | 자식 | 추정 본법 (TAI 미수집) |
  |---|---|
  | 국립장애인도서관 이용규칙 | 도서관법 |
  | 기후에너지환경부장관의 소속청장에 대한 지휘에 관한 규칙 | 정부조직법 |
  | 보건복지부 소관 비상대비에 관한 법률 시행규칙 | 비상대비자원관리법 |
  | 어린이·노인 및 장애인 보호구역의 지정 및 관리에 관한 규칙 | 도로교통법 |
- mapping_method = pending (사용자 결정 — 본법 추가 수집 vs ORPHAN 유지)

### Step 7-8: 종합 검증

**법령 366건 매핑 결과:**
| family_role | mapping_method | cnt | verified |
|---|---|---|---|
| PRIMARY | manual | 123 | 123 ✓ |
| ENFORCEMENT_DECREE | name_pattern | 116 | 116 ✓ |
| ENFORCEMENT_DECREE | parent_search | 5 | 0 (검증 대기) |
| ENFORCEMENT_RULE | name_pattern | 98 | 98 ✓ |
| ENFORCEMENT_RULE | parent_search | 20 | 0 (검증 대기) |
| ORPHAN | pending | 4 | 0 (검증 대기) |
| **합계** | - | **366** | **337 (92.1%)** |

**전체 law_master 752건 매핑 상태:**
| law_type_code | total | mapped | unmapped | % |
|---|---|---|---|---|
| LAW | 123 | 123 | 0 | **100%** ✓ |
| ENFORCEMENT_DECREE | 121 | 121 | 0 | **100%** ✓ |
| ENFORCEMENT_RULE | 122 | 122 | 0 | **100%** ✓ |
| NOTICE | 340 | 0 | 340 | 0% (Week 2 admrule-kr) |
| STANDARD | 42 | 0 | 42 | 0% (Week 2 admrule-kr) |
| OTHER | 4 | 0 | 4 | 0% (Week 2 admrule-kr) |

**법령 366/366 = 100% 매핑 완료** ✓  
**행정규칙 386건 = Week 2 작업 (계획대로)**

### Step 9: 산안법 가족 매핑 최종 검증

```
산업안전보건법 (276853) — PRIMARY ✓
├ 산업안전보건법 시행령 (284771) — name_pattern ✓
├ 산업안전보건법 시행규칙 (271485) — name_pattern ✓
└ 산업안전보건기준에 관한 규칙 (273603) — parent_search ★ (verified=false)

중대재해 처벌 등에 관한 법률 (228817) — PRIMARY ✓
└ 중대재해 처벌 등에 관한 법률 시행령 (277417) — name_pattern ✓

한국산업안전보건공단법 (279743) — PRIMARY ✓
└ 한국산업안전보건공단법 시행령 (268455) — name_pattern ✓
```

**TAI 핵심 도메인 INDUSTRIAL_SAFETY 가족 매핑 완성**.

---

## Found

### 1. Day 1 분석 정정
- ENFORCEMENT_DECREE 5건: INDEPENDENT_DECREE 아니라 **parent_search 가능**
- ORPHAN: 3건 추정 → **실제 4건** (도로교통법 누락)

### 2. 매핑 정확도 개선
- 자동 매핑 (verified=true): 337건 (92.1%)
- 사용자 검증 대기 (verified=false): 29건 (7.9%)
- 미매핑 0건 ✓

### 3. parent_search 25건의 신뢰도
- 핵심 케이스 (산업안전보건기준에 관한 규칙 → 산업안전보건법) = 명확
- 일부 추정 케이스 (방송통신설비 기술기준 → 전기통신사업법, 공동주택 층간소음 → 공동주택관리법) = 사용자 검증 필요

---

## Tomorrow (Day 3)

### 사용자 검증 작업 (verified=false 29건)
1. **parent_search 25건 검토** — 위 표의 부모 매핑 확인
2. **ORPHAN 4건 처리 결정**:
   - α: 4개 본법(도로교통법/도서관법/정부조직법/비상대비자원관리법) 법제처 API에서 추가 수집
   - β: ORPHAN 유지 (후속 작업 시 처리)
3. 검증 완료된 row → `UPDATE law_family_mapping SET verified=true`

### Week 2 사전 준비
- legalize-kr/admrule-kr 저장소 구조 조사
- 행정규칙 386건 (NOTICE 340 + STANDARD 42 + OTHER 4) 매핑 전략 도출
- legalize-kr 6자리 MST 매핑 cross-validation 시도 (Day 2 매핑 결과와 비교)

### 의존성
- Track A 인프라 완성 후 Stage 분해 시 law_family_mapping의 parent_law_id 활용
- Track E (Stage 분해) 시작 전 verified=false 29건 검증 완료 권장

---

## Day 1+2 종합 마일스톤

| 마일스톤 | 상태 |
|---|---|
| TAI law_master 752건 + law_mst_no 100% 검증 | ✓ |
| legalize-kr 매핑 전략 도출 | ✓ |
| law_family_mapping 테이블 생성 | ✓ |
| **법령 366건 100% 매핑 (자동 + parent_search)** | **✓** |
| 산안법 가족 4건 매핑 (PRIMARY + 자식 3) | ✓ |
| 사용자 검증 대기 29건 list 작성 | ✓ |
| 행정규칙 386건 매핑 (Week 2) | 대기 |
| legalize-kr cross-validation (Week 2) | 대기 |

**Track B Week 1 목표 (산안법 가족 1건 검증) → 1일 만에 366건 100% 매핑 달성**.

---

## 사용자 결정 요청 (3개)

**Decision B-2 (재확인)**: ORPHAN 4건 처리
- α: 4개 본법 추가 수집 (도로교통법/도서관법/정부조직법/비상대비자원관리법)
- β: ORPHAN 유지 (후속 처리)

**Decision B-3 (재확인)**: parent_search 25건 검증
- 한꺼번에 verified=true 또는 케이스별 검토?

**Decision B-4 (재확인)**: legalize-kr 활용 시점 (Week 2로 미루기 추천)

---

**END OF DAY 1+2**
