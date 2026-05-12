# 공정 관리 페이지 신규 + 메뉴 수정 작업 지시서
## 담당: Claude 프론트 창
## 레포: tai-admin

---

## 전체 작업 목록

1. 모든 HTML에서 엔진설정 메뉴 수정
2. engine-process-industry.html 신규 생성
3. engine-process-construction.html 신규 생성

---

## TASK 1. 엔진설정 메뉴 수정 (모든 HTML 일괄)

### 변경 사항

**삭제:** `엔진설정` 하위 메뉴에서 `시설` 제거
```html
<!-- 제거 대상 -->
<li class="menu-item"><a class="menu-link" href="engine-factory.html"><div>시설</div></a></li>
```

**추가:** `엔진설정` 하위 메뉴에 아래 2개 추가
```html
<li class="menu-item"><a class="menu-link" href="engine-process-industry.html"><div>공정(산업)</div></a></li>
<li class="menu-item"><a class="menu-link" href="engine-process-construction.html"><div>공정(건설)</div></a></li>
```

### 최종 엔진설정 메뉴 순서 (시설 제거됨)
```
엔진설정
  ├── 전역변수       (system-codes.html)
  ├── 설비           (engine-equipment.html)
  ├── 모델           (engine-model.html)
  ├── 법규           (engine-legal.html)
  ├── 공정(산업)    (engine-process-industry.html)  ← 신규
  ├── 공정(건설)    (engine-process-construction.html)  ← 신규
  ├── 사고           (engine-accident.html)
  ├── 엔진           (engine-run.html)
  ├── TBM            (engine-tbm.html)
  ├── 교육           (engine-education.html)
  └── 크론관리       (cron-list.html)
```

### 수정 대상 HTML 파일 (메뉴가 있는 파일 전체)

`git grep -l "engine-factory.html"` 로 대상 파일 창았으면 전체 일괄 수정.
주요 파일: engine-equipment.html, engine-legal.html, engine-model.html,
cron-list.html, system-codes.html, 등 엔진설정 메뉴 있는 모든 HTML

---

## TASK 2. engine-process-industry.html 신규 생성

파일: `admin/full-version/html/horizontal-menu-template/engine-process-industry.html`

**참조:** engine-equipment.html (구조 동일, Navbar/Menu/Footer/스크립트 동일)
**메뉴 active:** 엔진설정 > 공정(산업)

### 상단 안내 배너 (필수)

```html
<div class="alert alert-info d-flex align-items-center mb-4">
  <i class="icon-base ti tabler-info-circle me-2 flex-shrink-0"></i>
  <div>
    <strong>산업공정은 KSIC + AI에 의해 자동 생성됩니다.</strong>
    수동으로 공정을 추가하면 법령 판정 오류가 발생합니다.
    이 페이지는 조회 및 이상감지만 허용됩니다.
  </div>
</div>
```

### 상단 통계 카드 (4개)

| 카드 | 색상 | 주숫자 | 부제 |
|------|------|--------|------|
| 산업공정 수 | primary | 6,957 | "501개 업종" |
| 공정설비 매핑 | info | 1,188,161 | "자동 생성" |
| 설비매핑 0개 공정 | warning | 하드코딩 0 | "이상 없음" |
| 검토필요 | danger | API연결 또는 0 | "needs_review" |

데이터: 하드코딩 (API 없으면 폴백)

### 이상 감지 보드

제목: ⚠️ 산업공정 이상 감지

| 점검항목 | 내용 | 건수 | 배지 |
|---------|------|------|------|
| 설비매핑 0개 공정 | 공정은 있는데 설비 연결 없음 | 하드코딩 0 | 초록 "정상" |
| 검토필요 공정 | needs_review=true | 하드코딩 0 | 초록 "정상" |
| 수동추가 주의 | process_equipment_map 수동 수정 시 판정오류 | - | 노란 "안내" |

### 단일 탭: 산업공정 목록

API: `GET /engine-equipment/list` (기존 활용)

필터:
- 업종코드 검색 (input)
- 공정명 검사 (input)
- 옵로리 선택: 전체 / 리븷 필터(MUST/CORE/OPTIONAL)
- 페이지당 항목수 선택하보 (10/30/50)

콌럼:
| No. | 업종코드 | 업종명 | 공정명 | 설비수 | 밴드 | 공정경로 |

행 클릭 → 사이드패널:
- 업종코드/업종명
- 공정 경로 (lv1 > lv2 > lv3 > lv4)
- 연결 설비 목록 (밴드 + 설비명)
- 연결 산업 코드 목록

---

## TASK 3. engine-process-construction.html 신규 생성

파일: `admin/full-version/html/horizontal-menu-template/engine-process-construction.html`

**산업공정과 동일한 구조, 메뉴 active만 다름:**
엔진설정 > 공정(건설)

### 상단 안내 배너

```html
<div class="alert alert-warning d-flex align-items-center mb-4">
  <i class="icon-base ti tabler-crane me-2 flex-shrink-0"></i>
  <div>
    <strong>건설공종은 KCSC API로 자동 갱신됩니다.</strong>
    신고서식 연결은 수동으로 관리할 수 있습니다.
    구조: 공종 → 작업 → 위험작업 → 신고서식
  </div>
</div>
```

### 상단 통계 카드 (4개)

| 카드 | 색상 | 주숫자 | 부제 |
|------|------|--------|------|
| 건설공종 수 | primary | 161 | "건축 75 / 토목 50 / 공통 36" |
| 건설작업 수 | info | 243 | "위험작업 88개" |
| 신고서식 미연결 | warning | 하드코딩 | "선보입력 필요" |
| KCSC 최종갱신 | secondary | 날짜 | API에서 가져오기 |

API:
- GET /byulpyo/kcsc-process (없으면 하드코딩)
- 하드코딩: 공종 161 / 작업 243 / 위험작업 88

### 택 3개

**택1: 공종 목록**

API: `GET /engine-legal/appendix` 또는 하드코딩

필터:
- 공사유형: 전체 / 건축(BUILDING) / 토목(CIVIL) / 공통(COMMON)
- 공종명 검색

콌럼:
| No. | 공종코드 | 공유형 | 레벨1 | 레벨2 | 공종명 | 작업수 |

행 클릭 → 사이드패널:
- 공종 기본정보 (코드/유형/레벨)
- 해당 작업 목록

데이터 하드코딩 (아래 10개 샘플):
```javascript
var KCSC_FALLBACK = [
  {code:'KCS 11 10 05',type:'CIVIL',lv1:'도로',lv2:'일반도로',name:'평지작업',work_count:3},
  {code:'KCS 14 20 10',type:'BUILDING',lv1:'건축공사',lv2:'철근콘크리트',name:'철근 조립 및 설치',work_count:4},
  {code:'KCS 14 20 20',type:'BUILDING',lv1:'건축공사',lv2:'철근콘크리트',name:'콘크리트 타설공사',work_count:5},
  {code:'KCS 14 31 10',type:'BUILDING',lv1:'건축공사',lv2:'도장공사',name:'내장 도장',work_count:2},
  {code:'KCS 21 10 00',type:'COMMON',lv1:'가설공사',lv2:'가설안전',name:'가설안전관리',work_count:6},
];
```

**택2: 작업 목록**

| No. | 작업코드 | 공종명 | 작업명 | 위험작업여부 | 신고서식 |

위험작업이면 작업명 옆에 `<span class="badge bg-danger">위험</span>`

행 클릭 → 사이드패널:
- 작업 상세
- 신고서식 연결 현황
- 연결 버튼: "서식 연결" (select + save)

**택3: 신고서식 연결**

API: GET /byulpyo/legal-inspection (기존)

| No. | 작업코드 | 작업명 | 연결서식코드 | 서식명 | 상태 |

미연결이면 "서식매장" 드롭다운으로 폼코드선택 및 저장

---

## 전역 규칙
- 첫 번째 콌럼: toggleAll 체크박스
- 두 번째 콌럼: No. (1부터)
- escapeHtml, doLogout 동일
- 스크립트 세트 동일

---

## 완료 기준
- [ ] 엔진설정 전체 HTML에서 시설 메뉴 제거
- [ ] 엔진설정 전체 HTML에 공정(산업)/공정(건설) 메뉴 추가
- [ ] engine-process-industry.html 생성
- [ ] engine-process-construction.html 생성 (3탭)
- [ ] git add + commit + push
- [ ] 코받: "feat: 공정관리 페이지 신규 + 엔진설정 메뉴 수정"
