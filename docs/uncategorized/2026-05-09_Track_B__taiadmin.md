# [Track B] 2026-05-09 진행 — Day 1 (UPDATED)

**트랙**: B (조문 가족 매핑)  
**작업창**: TAI 회의실 (Claude 기획창)  
**작업자**: 사용자 + Claude  
**업데이트**: Plan B 사전 작업으로 자체 매핑 가능률 측정 → 99%+ 결론

---

## Done

### Task 1-6 (이전 보고)
- TAI law_master 752건 + law_mst_no 100% 채움 검증
- legalize-kr 저장소 구조 + 메타데이터 형식 확인 (법령MST 매핑 핵심)
- INDUSTRIAL_SAFETY 도메인 29건 검증 (본법 3 + 시행령 3 + 시행규칙 2 + NOTICE 20 + OTHER 1)

### Task 7-11 (Plan B 사전 작업)

#### Task 7: TAI 자체 이름 패턴 자동 매핑 가능률 측정
- ENFORCEMENT_DECREE: 116/121 (95.9%) 자동 매핑
- ENFORCEMENT_RULE: 98/122 (80.3%) 자동 매핑

#### Task 8: 미매칭 29건 list 추출 → 3개 카테고리 분류
| 카테고리 | 건수 | 처리 방식 |
|---|---|---|
| **A. 독립 대통령령** | 5 | family_role=INDEPENDENT_DECREE, parent X |
| **B. 본법명 다른 시행규칙** | 22 | 본법 search 매핑 (자기 본문 정의 패턴 또는 사용자 검증) |
| **C. 정규화 변형** | 0 (실제 0건) | - |

#### Task 9: 정규화 강화 룰 시도
- 띄어쓰기 + 가운뎃점 통일 → 추가 매칭 0건
- 결론: 미매칭은 정규화 문제 X, 본법명 자체가 다른 케이스

#### Task 10-11: 미매칭 시행규칙 22건의 본법 후보 search
**TAI에 본법 존재 (21건) — 법령MST 1:1 매핑 가능**:
| 시행규칙 | 본법 후보 (TAI) |
|---|---|
| 산업안전보건기준에 관한 규칙 (273603) | **산업안전보건법 (276853)** ★ 핵심 |
| 건설기계 안전기준에 관한 규칙 | 건설기계관리법 (283763) |
| 건축물대장의 기재 및 관리 등에 관한 규칙 | 건축법 (273437) |
| 건축물의 구조기준 등에 관한 규칙 | 건축법 (273437) |
| 건축물의 설비기준 등에 관한 규칙 | 건축법 (273437) |
| 건축물의 피난·방화구조 등의 기준에 관한 규칙 | 건축법 (273437) |
| 건축물착공통계조사시행규칙 | 건축법 (273437) |
| 공동주택 분양가격의 산정 등에 관한 규칙 | 주택법 (283191) |
| 공동주택 층간소음의 범위와 기준에 관한 규칙 | 공동주택관리법 (280069) (또는 소음·진동관리법) |
| 녹색건축 인증에 관한 규칙 | 녹색건축물 조성 지원법 (268779) |
| 도시·군계획시설의 결정·구조 및 설치기준에 관한 규칙 | 국토의 계획 및 이용에 관한 법률 (276959) |
| 사회복지법인 및 사회복지시설 재무·회계 규칙 | 사회복지사업법 (270405) |
| 수도용 자재와 제품의 위생안전기준 인증 등에 관한 규칙 | 수도법 (276757) |
| 어린이·노인 및 장애인 보호구역의 지정 및 관리에 관한 규칙 | (도로교통법 추정, TAI에 미수집) |
| 의료기기 유통 및 판매질서 유지에 관한 규칙 | 의료기기법 (268885) |
| 자연재난 구호 및 복구 비용 부담기준 등에 관한 규칙 | 재난 및 안전관리 기본법 (268803) |
| 전기사업회계규칙 | 전기사업법 (283981) |
| 제로에너지건축물 인증에 관한 규칙 | 녹색건축물 조성 지원법 (268779) |
| 중·저준위방사성폐기물 처분시설의 유치지역지원에 관한 특별법 시행규칙 | 중·저준위 방사성폐기물 처분시설의 유치지역지원에 관한 특별법 (276605) (띄어쓰기 1자 차이) |
| 지능형건축물의 인증에 관한 규칙 | 녹색건축물 조성 지원법 (268779) |
| 혁신의료기기 지원 및 관리 등에 관한 규칙 | 의료기기산업 육성 및 혁신의료기기 지원법 (276677) |

**TAI에 본법 미수집 (3건)**:
| 시행규칙 | 본법 추정 (TAI 미수집) |
|---|---|
| 보건복지부 소관 비상대비에 관한 법률 시행규칙 | 비상대비자원 관리법 |
| 국립장애인도서관 이용규칙 | 도서관법 |
| 기후에너지환경부장관의 소속청장에 대한 지휘에 관한 규칙 | 정부조직법 |

---

## Found (핵심 발견 — UPDATED)

### 종합 매핑 가능률 (법령 366건)
| 카테고리 | 건수 | 자동 매핑 (이름 패턴) | 추가 매핑 (본법 search) | 사용자 수동 |
|---|---|---|---|---|
| LAW (본법) | 123 | parent X (PRIMARY) | - | - |
| ENFORCEMENT_DECREE | 121 | 116 (95.9%) | - | 5 (독립 대통령령) |
| ENFORCEMENT_RULE | 122 | 98 (80.3%) | +21 (총 119) | 3 (본법 미수집) |
| **합계** | **366** | **214 (58.5%)** | **+21 (235, 64.2%)** | **8 (2.2%)** |

→ **TAI 자체 매핑만으로 99%+ 가능. legalize-kr 없이도 거의 완성.**  
→ **legalize-kr는 cross-validation 용으로만 활용**

### 행정규칙 386건 (NOTICE 340 + STANDARD 42 + OTHER 4)
- legalize-kr/admrule-kr 활용 필요 (Week 2 작업)

---

## 결정 변경

### Issue B-1 → 사용자 결정 사실상 불필요
- legalize-kr 산안법 sample fetch 검증의 의미 약화
- 이유: TAI 자체 매핑 가능률 99%+ 확인됨
- **legalize-kr 활용은 cross-validation 단계에서 (Week 2)**

### 새로운 진행 방향
**Day 2 — TAI 자체 가족 매핑 자동화 진행**:
1. `law_family_mapping` 테이블 DDL 작성 (Track A 의뢰)
2. ENFORCEMENT_DECREE 116건 + ENFORCEMENT_RULE 98건 자동 INSERT (이름 패턴 룰)
3. ENFORCEMENT_RULE 21건 본법 search 매핑 INSERT (사용자 5분 검증 후)
4. 독립 대통령령 5건 INSERT (parent_law_id=NULL, family_role=INDEPENDENT_DECREE)
5. 본법 미수집 3건 → 사용자 결정 (수집 vs ORPHAN)
6. LAW 123건 INSERT (family_role=PRIMARY)

### 사용자 결정 요청 (3건만)

**Decision B-2: 본법 미수집 3건 처리**
- (α) 법제처 API에서 비상대비자원관리법 / 도서관법 / 정부조직법 추가 수집
- (β) ORPHAN으로 보전 (parent_law_id=NULL, family_role=ORPHAN, 후속 작업 시 처리)

**Decision B-3: ENFORCEMENT_RULE 21건 본법 search 매핑 검증**
- 위 표의 본법 후보 21쌍을 사용자가 검토 후 OK 받으면 INSERT
- 모호한 케이스 (예: 공동주택 층간소음 → 공동주택관리법 vs 소음·진동관리법) 사용자 판단

**Decision B-4: legalize-kr 활용 시점**
- (α) Day 2에 사용자 git clone (cross-validation 즉시 시작)
- (β) Week 2로 미루기 (행정규칙 매핑 시 admrule-kr과 함께)
- 추천: **(β)** Week 2 — Day 2는 TAI 자체 매핑만으로 진행 가능

---

## Tomorrow (Day 2)

### Day 2 Task List
1. **law_family_mapping 테이블 DDL** — Track A에 의뢰 (DDL 충돌 방지)
   ```sql
   CREATE TABLE law_family_mapping (
     id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
     law_master_id uuid REFERENCES law_master(id) UNIQUE,
     parent_law_id uuid REFERENCES law_master(id),
     family_role text NOT NULL CHECK (family_role IN (
       'PRIMARY','ENFORCEMENT_DECREE','ENFORCEMENT_RULE',
       'INDEPENDENT_DECREE','ORPHAN','ADMINISTRATIVE_RULE'
     )),
     mapping_method text NOT NULL CHECK (mapping_method IN (
       'name_pattern','parent_search','manual','legalize_kr_mst','admrule_kr_mst'
     )),
     verified boolean DEFAULT false,
     created_at timestamptz DEFAULT now()
   );
   ```

2. LAW 123건 INSERT (family_role=PRIMARY)
3. ENFORCEMENT_DECREE 116건 + ENFORCEMENT_RULE 98건 자동 INSERT (mapping_method='name_pattern')
4. 독립 대통령령 5건 INSERT (mapping_method='manual', verified=true)
5. ENFORCEMENT_RULE 21건 사용자 검증 후 INSERT (mapping_method='parent_search')
6. 본법 미수집 3건 — 사용자 결정 대기

### Day 2 마일스톤
- 법령 366건 중 363건 (99.2%) 매핑 완료 예상
- 미해결 3건 = 사용자 결정 후 Day 3

---

## Track A 의뢰사항

Track A 창에서 작업 중인 분에게 — Day 2 진행 시 다음 DDL 필요합니다:

```sql
-- law_family_mapping 테이블 (위 DDL)
-- 우선순위: Day 2 시작 전 적용 필요
-- DDL 작업 시 다른 트랙 SQL 정지 통보 부탁
```

Track A 진행 상황에 따라 Day 2 시작 시점 조정.

---

**END OF DAY 1 (UPDATED)**
