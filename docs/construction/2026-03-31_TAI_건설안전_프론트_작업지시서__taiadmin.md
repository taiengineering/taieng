# TAI 건설안전 — 프론트엔드 작업지시서
## 작성일: 2026-03-31 | 담당: 프론트엔드 창

---

## ■ 공통 규칙 (필수 준수)

1. **1번 컬럼 = 체크박스** (`<input type="checkbox" id="checkAll" onclick="toggleAll(this)">`)
2. **2번 컬럼 = No.** (순번: `(currentPage-1)*pageSize + idx + 1`)
3. **사이드패널** — 목록 행 클릭 → 우측 슬라이드 패널로 상세/수정
4. **Vuexy Bootstrap 5** — 기존 페이지(`member-list.html`, `factory-list.html`) 스타일 동일하게 적용
5. **API 베이스** — `https://api.taieng.co.kr`
6. **역할 배지** — `role-constants.js` 공통 상수 활용
7. **전역변수** — `globals.js` → `apiCall()` 사용

---

## 1. 현장관리 (construction-site-list.html)

### 상단 필터
- 건설유형 `<select>`: 전체/건축/토목
- 공사상태 `<select>`: 전체/계획중/진행중/완료/중단
- 원청회사 `<input>`: 검색
- 기간 `<input type="date">` × 2
- [검색] [초기화] 버튼

### 목록 테이블
| No | 컬럼 | 비고 |
|----|------|------|
| 1 | 체크박스 | |
| 2 | No. | |
| 3 | 현장명 | 클릭 → 상세 패널 |
| 4 | 건설유형 | 건축/토목 배지 |
| 5 | 원청회사 | |
| 6 | 도급금액 | 억원 단위 |
| 7 | 공사기간 | YYYY.MM.DD ~ MM.DD |
| 8 | 총근로자 | |
| 9 | 상태 | 배지 |
| 10 | 안전관리자 선임 | ✅필요/➖불필요 |

### 등록 사이드패널 필드
- 현장명 * / 건설유형 * (select)
- 원청회사 * (select + 검색)
- 도급금액 / 총근로자 수
- 공사 시작일 ~ 종료일
- 현장 주소
- 공사 상태 (select)
- 메모
- [**안전관리자 의무 확인**] 버튼 → 도급금액/근로자수 입력 후 클릭 시
  - `POST /construction/engine/safety-manager` 호출
  - 결과: 「선임 의무: 1명 이상 (150억 이상 건축)」 알림 배너 표시

### API
- 목록: `GET /construction/sites?site_type=&status_code=&keyword=&page=&size=`
- 등록: `POST /construction/sites`
- 수정: `PATCH /construction/sites/{id}`
- 삭제: 선택 후 [삭제] 버튼 → 확인 팝업 → `PATCH is_active=false`

---

## 2. 공정관리 (construction-process-list.html)

### 상단 요소
- **현장 선택 드롭다운** (상단 고정) — 선택한 현장의 공정만 표시
- 공종구분 필터: 전체/건축/토목/공통
- 공정상태 필터: 전체/대기/진행중/완료
- [공정 추가] 버튼

### 목록 테이블
| No | 컬럼 | 비고 |
|----|------|------|
| 1 | 체크박스 | |
| 2 | No. | |
| 3 | 공정명 | KCSC 연동 표시 |
| 4 | 공종 | 건축/토목/공통 배지 |
| 5 | 계획기간 | |
| 6 | 진행률 | `<div class="progress">` 바 |
| 7 | 투입인원 | |
| 8 | 위험공정 | 🔴 위험/⚪ 일반 |
| 9 | 상태 | 배지 |

### 공정 추가 패널
- 현장 (고정 표시)
- KCSC 공정 검색 (autocomplete) → `GET /construction/kcsc/processes?keyword=`
  - 선택 시 공종구분, 위험공정 여부 자동 채움
- 직접입력 토글 (KCSC 없이 자유입력)
- 계획기간 (시작 ~ 종료)
- 투입인원
- 상태 select
- **위험작업 미리보기** — 공정 선택 시 `GET /construction/kcsc/works/{process_id}` 호출하여
  해당 공정의 위험작업 목록을 패널 하단에 표시 (미리보기, 선택 가능)

### 진행률 수정
- 목록 행의 진행률 바 클릭 → 인라인 슬라이더 (0~100%) 팝오버
- 저장 시 `PATCH /construction/processes/{id}` 호출

### API
- 목록: `GET /construction/sites/{site_id}/processes`
- 등록: `POST /construction/sites/{site_id}/processes`
- 수정: `PATCH /construction/processes/{id}`

---

## 3. 작업관리 (construction-work-list.html)

### 상단 요소
- 현장 선택 드롭다운 (상단 고정)
- 공정 필터 (현장 선택 후 동적 로드)
- 특별관리유형 필터: 전체/고소/밀폐/화기/전기/굴착/양중/발파/석면
- PTW 상태 필터: 전체/초안/승인/반려/종료
- 작업일 `<input type="date">`
- [작업 등록] 버튼

### 목록 테이블
| No | 컬럼 | 비고 |
|----|------|------|
| 1 | 체크박스 | |
| 2 | No. | |
| 3 | PTW 번호 | CS-2026-00001 |
| 4 | 작업명 | |
| 5 | 공정 | |
| 6 | 특별관리유형 | 빨간 배지 |
| 7 | 작업일 | |
| 8 | 관리감독자 | |
| 9 | 투입인원 | |
| 10 | PTW 상태 | 색상 배지 |

### 작업 등록 패널
- 현장 (고정), 공정 (select)
- KCSC 작업 선택 (autocomplete) → 자동으로 위험요인·PPE 채움
- 직접입력 토글
- 작업일, 시작시간 ~ 종료시간
- 작업 위치/구역
- 관리감독자 (users 검색, 013 역할)
- 하도급업체 (companies 검색)
- 특별관리작업 유형 (multi-select)
- 위험요인 코드 (chips)
- 필요 PPE (chips)
- 투입인원
- 메모

### PTW 승인 워크플로우
- DRAFT → [승인요청] 버튼 → APPROVED 또는 REJECTED
- `PATCH /construction/works/{id}/ptw` body: `{ptw_status: 'APPROVED'}`
- 승인자: 안전관리자(012) 또는 안전보건관리책임자(011) 역할만 가능
- 승인 시 녹색 배지, 반려 시 빨간 배지, 종료 시 회색 배지

### API
- 목록: `GET /construction/sites/{site_id}/works?process_id=&special_work_type=&ptw_status=&work_date=`
- 등록: `POST /construction/sites/{site_id}/works`
- PTW 변경: `PATCH /construction/works/{id}/ptw`

---

## 4. 작업자관리 (construction-worker-list.html)

### 상단 요소
- 현장 선택 드롭다운 (상단 고정)
- 소속 필터: 전체/원청/하도급
- 역할 필터: 전체 / 010~022 (role-constants.js optgroup)
- 교육 상태 필터: 전체/완료/미완료
- 출입상태 필터: 전체/현장내/퇴장/미입장
- [작업자 추가] 버튼

### 목록 테이블
| No | 컬럼 | 비고 |
|----|------|------|
| 1 | 체크박스 | |
| 2 | No. | |
| 3 | 이름 | |
| 4 | 역할 | 산안법 기반 색상 배지 |
| 5 | 소속 | 원청/하도급(업체명) |
| 6 | 투입일 | |
| 7 | 자격증 | 유/무 |
| 8 | 특수건강검진 | 완료일 또는 D-day |
| 9 | 안전교육 | ✅완료/❌미완료 |
| 10 | 출입상태 | IN=초록/OUT=회색/OFFSITE=노랑 |

### 통계 카드 (목록 상단)
- 총 작업자: N명 (원청 N / 하도급 N)
- 안전교육 완료율: N%
- 특수건강검진 만료 임박: N명 (30일 이내)

### 작업자 등록 패널
- 회원 검색 (users autocomplete) → 선택 시 자동 채움
- 직접입력 (비회원 작업자용): 이름, 연락처
- 소속: 원청/하도급 select → 하도급 선택 시 업체 select 표시
- 역할 (role-constants.js fillRoleSelect)
- 투입일 / 철수 예정일
- 보유 자격증 (chips)
- 특수건강검진일 / 결과
- 안전교육 완료일 / 시간

### 출입 변경
- 각 행의 출입상태 배지 클릭 → IN/OUT/OFFSITE 토글 팝오버
- `PATCH /construction/workers/{id}/entry` body: `{entry_status}`

### API
- 목록: `GET /construction/sites/{site_id}/workers?worker_type=&role_code=&edu_status=&entry_status=`
- 등록: `POST /construction/sites/{site_id}/workers`
- 출입: `PATCH /construction/workers/{id}/entry`

---

## 5. 점검관리 (construction-inspection-list.html)

### 상단 요소
- 현장 선택 드롭다운 (상단 고정)
- 점검유형 필터: 전체/작업 전 점검/일상점검/특별점검
- 점검결과 필터: 전체/PASS/FAIL/조건부
- 시정상태 필터: 전체/대기/진행중/완료
- 기간 필터
- [점검 등록] 버튼

### 목록 테이블
| No | 컬럼 | 비고 |
|----|------|------|
| 1 | 체크박스 | |
| 2 | No. | |
| 3 | 현장/작업명 | |
| 4 | 점검유형 | 배지 |
| 5 | 점검일시 | |
| 6 | 점검자 | |
| 7 | 전체결과 | PASS=초록/FAIL=빨강/조건부=주황 |
| 8 | 이상건수 | 0건이면 '-' |
| 9 | 시정상태 | 배지 |
| 10 | 사진 | 썸네일 (있으면) |

### 점검 등록 패널
- 현장 (고정), 작업 선택 → 공정 자동 표시
- 점검일시 (datetime-local)
- 점검자 (users 검색)
- 점검유형 select
- **체크리스트 자동 생성**:
  - 작업 선택 시 `GET /construction/kcsc/works/{process_id}` 호출
  - `safety_standard` 기반 항목 자동 생성
  - 각 항목: [양호 ✅ / 불량 ❌] 선택 + 메모 입력
- 전체 결과 (radio: PASS/FAIL/CONDITIONAL)
- 이상 항목 (불량 선택 시 자동 카운트)
- 시정조치 내용 / 기한
- 사진 첨부 (multiple)

### 시정조치 추적
- FAIL/CONDITIONAL 결과 → 시정조치 탭 활성화
- 시정완료 시 [완료 처리] 버튼 → `PATCH /construction/inspections/{id}/corrective`
- 완료 시 사진 첨부 요구 (선택적)

### API
- 목록: `GET /construction/sites/{site_id}/inspections?inspection_type=&overall_result=&corrective_status=`
- 등록: `POST /construction/sites/{site_id}/inspections`
- 시정조치: `PATCH /construction/inspections/{id}/corrective`

---

## ■ 메뉴 등록 (menu-nav.js)

`menu-nav.js`의 `건설안전` 그룹을 아래로 수정:

```javascript
{
  label: '건설안전', icon: 'tabler-crane',
  children: [
    { label: '현장관리',   href: 'construction-site-list.html' },
    { label: '공정관리',   href: 'construction-process-list.html' },
    { label: '작업관리',   href: 'construction-work-list.html' },
    { label: '작업자관리', href: 'construction-worker-list.html' },
    { label: '점검관리',   href: 'construction-inspection-list.html' },
  ]
}
```

---

## ■ 개발 순서 권장

```
1. construction-site-list.html      (가장 기본 — 다른 4개의 부모)
2. construction-process-list.html   (현장 선택 후 공정)
3. construction-work-list.html      (공정 선택 후 작업/PTW)
4. construction-worker-list.html    (현장 단위 독립)
5. construction-inspection-list.html (작업 선택 후 점검)
```
