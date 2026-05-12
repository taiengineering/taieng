# TAI 건설안전 5개 페이지 기획서
## 작성일: 2026-03-31

---

## 0. 건설안전 구조 개요

```
현장관리 (construction-site-list.html)        ← 건설현장 등록/관리
    └── 공정관리 (construction-process-list.html) ← KCSC 공정 매핑
            └── 작업관리 (construction-work-list.html) ← 위험작업 등록
                    └── 작업자관리 (construction-worker-list.html) ← 배치/자격
                            └── 점검관리 (construction-inspection-list.html) ← 안전점검
```

### 핵심 엔티티 관계
- **현장** → 하나의 건설 프로젝트 (산안법 시행령 제16조 기준 적용)
- **공정** → KCSC 표준 공정 (건축 75 / 토목 50 / 공통 36 = 총 161개)
- **작업** → 위험작업 88개 (KCSC), 공정별 세부 작업 155개
- **작업자** → 원청/하도급 구분, 자격증/특수건강검진 관리
- **점검** → 위험작업별 작업 전 안전점검

---

## 1. 현장관리 (construction-site-list.html)

### 목적
건설 현장을 등록·관리하고 산안법 의무(안전관리자 선임, 안전관리비 계상 등)를 자동 판정한다.

### 핵심 필드
| 필드 | 설명 | 비고 |
|------|------|------|
| site_name | 현장명 | 필수 |
| company_id | 원청회사 | FK → companies |
| site_type | 건설유형 | BUILDING/CIVIL (건축/토목) |
| contract_amount | 도급금액(억원) | 산안법 선임 기준 |
| total_workers | 총 근로자 수 | 하도급 포함 |
| start_date / end_date | 공사 기간 | |
| site_address | 현장 주소 | |
| safety_manager_required | 안전관리자 선임 여부 | 엔진 자동 판정 |
| status_code | 공사상태 | PLANNED/ONGOING/COMPLETED/SUSPENDED |

### 자동 판정 로직
- 건축: 도급금액 ≥ 150억 → 안전관리자 1인 이상 선임 의무
- 토목: 도급금액 ≥ 120억 → 안전관리자 1인 이상 선임 의무
- 근로자 ≥ 50명(하도급 포함): 안전보건관리책임자 지정 의무

### 목록 컬럼 (global rule 적용)
1. 체크박스 (toggleAll)
2. No. (순번)
3. 현장명
4. 건설유형 (건축/토목)
5. 원청회사
6. 도급금액
7. 공사기간
8. 총근로자
9. 상태 배지
10. 안전관리자 선임 여부 (자동)

---

## 2. 공정관리 (construction-process-list.html)

### 목적
현장별로 KCSC 표준 공정을 매핑하고 공정별 진행상황을 관리한다.

### 핵심 필드
| 필드 | 설명 | 비고 |
|------|------|------|
| site_id | 현장 FK | |
| process_id | KCSC 공정 FK | kcsc_process_master |
| process_name | 공정명 | |
| planned_start / planned_end | 계획 기간 | |
| actual_start / actual_end | 실제 기간 | |
| progress_rate | 진행률(%) | 0~100 |
| status_code | 공정상태 | PENDING/IN_PROGRESS/DONE |
| is_high_risk | 위험공정 여부 | KCSC 기준 자동 |
| worker_count | 해당 공정 투입 인원 | |

### KCSC 연동
- `kcsc_process_master` (161개) 기반
- `construction_type`: BUILDING/CIVIL/COMMON
- 공정 선택 시 `kcsc_work_master`의 위험작업 자동 표시

### 목록 컬럼
1. 체크박스
2. No.
3. 공정명 (KCSC 연동)
4. 공종구분 (건축/토목/공통)
5. 계획기간
6. 진행률 프로그레스바
7. 투입인원
8. 위험공정 여부
9. 상태

---

## 3. 작업관리 (construction-work-list.html)

### 목적
위험작업을 등록하고 작업허가서(PTW)를 발행·관리한다.

### 핵심 필드
| 필드 | 설명 | 비고 |
|------|------|------|
| site_id | 현장 FK | |
| process_id | 공정 FK | |
| work_id | KCSC 작업 FK | kcsc_work_master |
| work_date | 작업일자 | |
| work_time_start / end | 작업시간 | |
| work_location | 작업위치/구역 | |
| assigned_manager | 관리감독자 | FK → users |
| ptw_number | 작업허가서 번호 | 자동채번 |
| ptw_status | PTW 상태 | DRAFT/APPROVED/REJECTED/CLOSED |
| hazard_codes | 위험요인 코드 | 쉼표 구분 |
| ppe_required | 필요 PPE | |
| special_work_type | 특별관리작업 유형 | 고소/밀폐/화기/전기 등 |
| worker_count | 작업 인원 | |
| subcontractor_id | 하도급업체 | |

### 특별관리작업 분류 (system_codes)
- 고소작업 (2m 이상)
- 밀폐공간작업
- 화기작업 (용접/절단)
- 전기작업 (활선)
- 굴착작업
- 양중작업 (크레인)
- 발파작업
- 석면해체

### 목록 컬럼
1. 체크박스
2. No.
3. 작업허가서 번호
4. 현장/공정
5. 작업명 (KCSC)
6. 특별관리유형 (배지)
7. 작업일자
8. 관리감독자
9. 투입인원
10. PTW 상태

---

## 4. 작업자관리 (construction-worker-list.html)

### 목적
현장 투입 작업자(원청/하도급)를 등록하고 자격증·특수건강검진·안전교육 이력을 관리한다.

### 핵심 필드
| 필드 | 설명 | 비고 |
|------|------|------|
| site_id | 현장 FK | |
| user_id | 작업자 FK | users |
| worker_type | 원청/하도급 | DIRECT/SUBCON |
| subcontractor_id | 하도급업체 | FK → companies |
| role_code | 역할 | 010~022 (산안법 기반) |
| join_date / leave_date | 투입/철수 일자 | |
| certification_codes | 보유 자격증 코드 | |
| health_check_date | 특수건강검진일 | |
| safety_edu_date | 안전교육 완료일 | |
| safety_edu_hours | 교육시간 | |
| entry_status | 출입상태 | IN/OUT/OFFSITE |

### 하도급 인원 포함 원칙 (산안법 시행령 제16조③)
- 안전관리자 선임 시 하도급 근로자 수를 **포함**하여 계산
- 작업자 목록에서 원청/하도급 구분 필터 제공

### 목록 컬럼
1. 체크박스
2. No.
3. 이름
4. 역할 (산안법 기반 배지)
5. 소속 (원청/하도급업체)
6. 투입일
7. 자격증 (유/무)
8. 특수건강검진 (D-day 또는 완료)
9. 안전교육 (완료/미완료)
10. 출입상태

---

## 5. 점검관리 (construction-inspection-list.html)

### 목적
위험작업 전 안전점검(작업 전 점검)을 실시하고 결과를 기록한다. 이상 발견 시 시정조치까지 연결한다.

### 핵심 필드
| 필드 | 설명 | 비고 |
|------|------|------|
| site_id | 현장 FK | |
| work_id | 작업 FK | construction_works |
| inspection_date | 점검일시 | |
| inspector_id | 점검자 | FK → users |
| inspection_type | 점검유형 | BEFORE_WORK/DAILY/SPECIAL |
| checklist_items | 점검항목 JSON | KCSC 기준 항목 |
| overall_result | 전체 결과 | PASS/FAIL/CONDITIONAL |
| defect_count | 이상 건수 | |
| corrective_action | 시정조치 내용 | |
| corrective_deadline | 시정 기한 | |
| corrective_status | 시정 상태 | PENDING/IN_PROGRESS/DONE |
| photo_urls | 점검 사진 | |

### 점검 체크리스트 자동 생성
- 작업 선택 → `kcsc_work_master`의 `safety_standard` 기반 체크리스트 자동 생성
- 위험작업(is_hazardous=true) 88개에 대한 항목 자동 로드

### 목록 컬럼
1. 체크박스
2. No.
3. 현장/작업명
4. 점검유형
5. 점검일시
6. 점검자
7. 전체결과 (PASS/FAIL/CONDITIONAL 배지)
8. 이상건수
9. 시정상태
10. 사진 (썸네일)
