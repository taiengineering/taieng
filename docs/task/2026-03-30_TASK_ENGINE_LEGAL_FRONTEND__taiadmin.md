# engine-legal 프론트엔드 작업 지시서
## 담당: Claude 프론트 창
## 레포: tai-admin
## 참조: admin/full-version/html/horizontal-menu-template/engine-equipment.html (구조 동일)

---

## 작업 1: engine-legal.html 신규 생성

파일: `admin/full-version/html/horizontal-menu-template/engine-legal.html`

**engine-equipment.html에서 Navbar/Menu/Footer/스크립트 세트 그대로 복사.**
메뉴에서 active는 엔진설정 > 법규

### [1] 상단 신호등 카드 (4개)

`GET /engine-legal/stats` 호출

| 카드 | 아이콘 | 색상 | 주숫자 | 다른행 |
|------|------|------|--------|--------|
| 전체 법령 | tabler-books | primary | total_laws | "조문 {total_articles}개" |
| 판정룰 | tabler-rule | warning | total_rules | "미매핑 {unmapped_rules}개" |
| 별표 데이터 | tabler-table | info | byulpyo.total | "안전인증 {safety_cert}/위험물 {dangerous_goods}" |
| 종합 품질 | tabler-shield-check | success | 직접 계산 | "정상" or "문제있음" |

카드 왜쪽 테두리 상태 색상:
- unmapped_rules = 0 → #28c76f (녹)
- unmapped_rules > 0 → #ea5455 (빨간)

---

### [2] 자동 점검 리포트 카드

**제목**: ⚠️ 자동 점검 리포트 (문제 있는 항목만)

아래 데이터 **하드코딩** 표시:

| 점검항목 | 문제내용 | 건수 | 상태배지 |
|---------|---------|------|--------|
| 섹터 편중 감지 | 산안기준규칙·시행규칙·근로기준법 등 전 산업 적용 법령이 BUILDING에만 매핑 | 11개 법령 | 파란 badge bg-danger "조치필요" |
| 서식 미연결 | 신고의무 룰 중 form_code 없는 룰 | 80개 | badge bg-warning "보완필요" |
| Summary 공백 | 판정룰 중 의무요약 문구 없음 | 379개 | badge bg-warning "보완필요" |
| 판정룰 없는 법령 | 수집됨으나 판정룰 0개 | 13개 | badge bg-warning "검토필요" |
| 별표 미완성 | 고압가스 종류·기준 데이터 미수집 | 1개 | badge bg-warning "수집필요" |

---

### [3] 탭 3개

**탭1: 법령 품질 스코어**

API: `GET /engine-legal/laws`

필터:
- 법령유형: ALL / LAW(법률) / ENFORCEMENT_DECREE(시행령) / ENFORCEMENT_RULE(시행규칙)
- 이름 검색
- 품질등급: ALL / 양호(80+) / 보통(50-79) / 미흡(0-49)

콤럼:
| No. | 법령명 | 유형 | 조문 | 항 | 룰수 | 스코어 | 등급 |

**스코어 계산** (합계 100점):
- 조문수 > 0: +20
- 항수 > 0: +20 (항=0이면 "파싱누락" 빨간 badge)
- 룰수 > 0: +20
- 룰 섹터 2개이상: +20
- summary완성: +10
- 서식연결: +10

등급:
- 80~100 → bg-success "양호"
- 50~79  → bg-warning "보통"
- 0~49   → bg-danger "미흡"

기본정렬: 스코어 오름차순

행 클릭 → 사이드패널 오픈:
- 법령 기본정보 (이름/유형/정부부체)
- 조문 목록 (article_no + article_title, 최대 20개)
- 연결 판정룰 목이 (sector + obligation_type 배지)
API: `GET /engine-legal/laws/{id}`

---

**탭2: 판정룰 현황**

API: `GET /engine-legal/rules`

필터:
- 섹터: ALL / BUILDING / MANUFACTURING / CONSTRUCTION / SPECIAL_FACILITY
- 의무유형: ALL / APPOINT / INSPECT / REPORT / NOTIFY / ACTION / OTHER
- 키워드 검색

켄럼:
| No. | 법령명 | 조문 | 섹터 | 의무유형 | 의무요약 |

**obligation_type 배지 색상**:
```javascript
function getObTypeBadge(type) {
  const map = {
    'APPOINT': ['bg-label-primary',   '선임'],
    'INSPECT': ['bg-label-info',       '점검'],
    'REPORT':  ['bg-label-warning',    '신고'],   // 주황 #ff9f43
    'NOTIFY':  ['bg-label-secondary',  '보고'],   // 파랑 #1a5fd4 (bg-label-primary로 대체)
    'ACTION':  ['bg-label-success',    '조치'],
    'OTHER':   ['bg-label-secondary',  '기타'],
  };
  const m = map[type] || map['OTHER'];
  return `<span class="badge ${m[0]}">${m[1]}</span>`;
}
```

REPORT(신고): 주황 / NOTIFY(보고): 파랑으로 명확히 구분

행 클릭 → 사이드패널:
- 룰 상세 (법령명/조문/지정조건/의무요약/벌칙요약/서식코드)
API: `GET /engine-legal/rules/row/{id}`

---

**탭3: 별표 현황**

API: `GET /engine-legal/appendix`

소카드 5개 (클릭 햨 할성):
| 카드 | 도메인 | 건수 |
|------|--------|------|
| 안전인증 대상 | SAFETY_CERT | 30개 |
| 자율안전확인 | SELF_CERT | 20개 |
| 위험물 품명·지정수량 | HAZMAT | 49개 |
| 선임기준 | APPOINTMENT | 19개 |
| 법정 안전검사 | STATUTORY_INSPECTION | 13개 |

카드 클릭 → 아래 테이블에 해당 데이터 표시

안전인증 테이블: 코드 | 구분(MACHINE/DEVICE/PROTECTIVE) | 품목명 | 세부사항 | cert_type
위험물 테이블: 코드 | 유별 | 품명 | 지정수량 | 단위

행 클릭 → 사이드패널 상세:
API: `GET /engine-legal/appendix/{id}?table=master_safety_certification`

---

### 전역 규칙
- 첫 번째 켄럼 = toggleAll 체크박스
- 두 번째 켄럼 = No. (1부터)
- escapeHtml 함수 필수
- 인증 코드 (engine-equipment.html과 동일)
- doLogout 함수 동일

---

## 작업 2: quote-list.html 수정

파일: `admin/full-version/html/horizontal-menu-template/quote-list.html`

진단 결과 요약에서 `report_required` 를 `obligation_type`으로 나눠서 신고/보고 각각 표시:

```javascript
// 기존: report_required=true → 여러 개
// 수정: obligation_type 값으로 신고(REPORT) vs 보고(NOTIFY) 구분
function renderObligationBadges(rules) {
  const report = rules.filter(r => r.obligation_type === 'REPORT').length;
  const notify  = rules.filter(r => r.obligation_type === 'NOTIFY').length;
  let html = '';
  if (report > 0)
    html += `<span class="badge" style="background:#ff9f43;color:#fff">신고 ${report}건</span> `;
  if (notify > 0)
    html += `<span class="badge" style="background:#1a5fd4;color:#fff">보고 ${notify}건</span>`;
  return html;
}
```

요약 카드 배지:
- REPORT(신고) → 주황 `#ff9f43`
- NOTIFY(보고) → 파랑 `#1a5fd4`

---

## 작업 3: diagnosis-step1.html (보게: tadmin)

파일: `html/horizontal-menu-template/diagnosis-step1.html`

판정룰 테이블에 `구분` 켄럼 추가:
```html
<th>구분</th>  <!-- 신고/보고 구분 켄럼 -->
```

데이터 렌더링:
```javascript
function renderObType(type) {
  if (!type) return '<span class="badge bg-secondary">기타</span>';
  if (type === 'REPORT')
    return '<span class="badge" style="background:#ff9f43;color:#fff">신고</span>';
  if (type === 'NOTIFY' || type === 'NOTIFICATION')
    return '<span class="badge" style="background:#1a5fd4;color:#fff">보고</span>';
  const m = {
    'APPOINT': ['bg-label-primary', '선임'],
    'INSPECT': ['bg-label-info',    '점검'],
    'ACTION':  ['bg-label-success', '조치'],
  };
  const b = m[type];
  return b ? `<span class="badge ${b[0]}">${b[1]}</span>` : `<span class="badge bg-secondary">${type}</span>`;
}
```

`rules_table` API 응답이 있으면 우선 사용, 없으면 기존 `obligations` 별도 사용.

---

## 완료 기준
- [ ] engine-legal.html 구현 (3탭 정상 동작)
- [ ] 탭1 스코어 계산 및 등급 표시
- [ ] 탭2 판정룰 REPORT(주황)/NOTIFY(파랑) 구분
- [ ] 탭3 별표 5종 데이터 조회
- [ ] quote-list.html 신고/보고 배지 구분
- [ ] diagnosis-step1.html 구분 켄럼 추가
- [ ] git add + commit + push
- [ ] 코받메시지: "feat: engine-legal.html 법령품질관리 + 신고/보고 구분 적용"
