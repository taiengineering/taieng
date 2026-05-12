# TAI Safe 가격설정 작업지시서

> **작성**: 2026-03-29  
> **대상**: 백엔드(Cursor) + 프론트엔드(Cursor)  
> **우선순위**: 플랜실팔 화면 구현 후 프론트 작업

---

## 개요

**목적**: admin(tadmin) 설정 메뉴 하위에 "가격설정" 승계 페이지를 만들다.  
대표님이 플랜별 가격, 초과 인원당 단가, 단건 진단 요금을 UI에서 직접 수정하면 서비스 전체에 즐시 반영되는 구조

---

## 1. DB 현황 (현재 완료됨)

### 테이블: `price_saas_plan`

| 콼럼 | 타입 | 설명 |
|------|------|------|
| id | uuid | PK |
| plan_code | text | BASIC / PRO / ENTERPRISE |
| plan_name | text | 플랜명 |
| display_name | text | 화면표시명 (스타터/비즈니스/엔터프라이즈) |
| description | text | 대상 설명 (5~30인 등) |
| monthly_base_fee | numeric | 월 기본료 |
| annual_base_fee | numeric | 연간 기본료 |
| annual_discount_rate | numeric | 연간 할인율(%) |
| annual_free_months | integer | 연간 무료 제공 개월 |
| included_users | integer | 포함 인원 (10/30/-1) |
| extra_user_fee_v2 | numeric | 초과 1인당 월요금 |
| max_facilities | integer | 최대 시설 수 (-1=무제한) |
| max_sites | integer | 최대 시설 수 (v2 기준) |
| storage_history_month | integer | 실행이력 보관 개월 (-1=무제한) |
| include_task_assign | boolean | 업무 할당·분산 포함 |
| include_group_mgmt | boolean | 그룹 관리 포함 |
| include_miss_alert | boolean | 누락 알림 포함 |
| include_api_v2 | boolean | API 연동 포함 |
| include_safety_content | text | 안전인식 콘텐츠 (basic/advanced/custom) |
| include_dashboard | text | 대시보드 등급 (basic/advanced/custom) |
| badge_color | text | 배지 색상 (secondary/primary/dark) |
| sort_order | integer | 정렬 순서 |
| is_active | boolean | 활성화 여부 |

### 테이블: `price_diagnosis_report`

| 콼럼 | 타입 | 설명 |
|------|------|------|
| id | uuid | PK |
| facility_type_code | text | BUILDING/FACTORY/CONSTRUCTION/HAZARD_LOW/HAZARD_MID/HAZARD_HIGH |
| facility_type_name | text | 시설 유형 한글명 |
| basic_fee | numeric | 기초진단 요금 |
| process_fee | numeric | 공정/공종 진단 요금 |
| equipment_fee | numeric | 설비/기계 진단 요금 |
| total_report_fee | numeric | 종합 리포트 요금 |
| is_active | boolean | 활성화 여부 |
| sort_order | integer | 정렬 순서 |

### 테이블: `price_change_log`
- 가격 변경 시 자동 기록 (record_id, field_name, old_value, new_value, changed_at)

---

## 2. 백엔드 작업지시 (tai-api / Cursor)

### 파일: `app/routers/price_setting.py` 샨로 생성

#### API 목록

```
GET    /price-setting/saas-plans
           전체 SaaS 플랜 목록 조회 (sort_order 오름차순)

GET    /price-setting/saas-plans/{plan_id}
           특정 플랜 상세 조회

PATCH  /price-setting/saas-plans/{plan_id}
           플랜 가격/옵션 수정
           수정 시 price_change_log 에 이력 저장

GET    /price-setting/diagnosis-reports
           시설 유형별 단건 진단 요금 목록

PATCH  /price-setting/diagnosis-reports/{report_id}
           단건 진단 요금 수정
           수정 시 price_change_log 에 이력 저장

GET    /price-setting/change-logs
           가격 변경 이력 조회
           Query params: table_name, limit(default 50)
```

#### Request Body 예시 (PATCH saas-plans)

```json
{
  "monthly_base_fee": 49000,
  "included_users": 10,
  "extra_user_fee_v2": 3000,
  "annual_free_months": 2,
  "max_sites": 1,
  "storage_history_month": 6,
  "include_api_v2": false,
  "badge_color": "secondary",
  "is_active": true
}
```

#### 구현 주의사항

```
- 모든 수정은 변경된 필드만 PATCH (None 필드 제외)
- 수정 전 old_value vs new_value 비교 후 변경된 것만 price_change_log 저장
- updated_at 자동 갱신
- 목종 app/main.py에 router include 필수
  from app.routers import price_setting
  app.include_router(price_setting.router)
```

---

## 3. 프론트엔드 작업지시 (tai-admin / Cursor)

### 파일 생성 목록

```
tadmin/full-version/html/horizontal-menu-template/price-setting.html
tadmin/full-version/assets/js/tai/pages/price-setting.page.js
```

---

### 3-1. 메뉴 연결 수정 (하위페이지 전체 동일 적용)

**대상**: tadmin 수평메뉴 `<aside id="layout-menu">` 내부  
**시설관리** 메뉴 하위엔 추가:

```html
<!-- 시설관리 메뉴 하위 마지막 항목으로 추가 -->
<li class="menu-item">
  <a class="menu-link" href="price-setting.html">
    <div>가격설정</div>
  </a>
</li>
```

> 또는 **설정** 메뉴를 별도로 만들고 하위에 가격설정 넣는 것도 가능.  
> 최종 메뉴 위치는 대표님 확인 후 결정.

---

### 3-2. `price-setting.html` 페이지 구조

#### 기본 템플릿
- `education-setting.html` 복사 후 수정 (내비바, 헤더, 스타일 동일)
- `<title>TAI - 가격설정</title>`
- 헤더: `<h4>가격설정</h4>` / 설명: `SaaS 플랜 및 단건 진단 요금을 설정합니다.`
- 오른쪽 버튼: `<button class="btn btn-primary" id="btnSaveAll">💾 전체 저장</button>`
- 스크립트: `price-setting.page.js` 로드

#### 탭 구성 (내비게이션 탭)

```html
<ul class="nav nav-tabs mb-4">
  <li class="nav-item">
    <button class="nav-link active" data-bs-target="#tabSaas">SaaS 플랜</button>
  </li>
  <li class="nav-item">
    <button class="nav-link" data-bs-target="#tabDiagnosis">단건 진단 요금</button>
  </li>
  <li class="nav-item">
    <button class="nav-link" data-bs-target="#tabChangelog">변경 이력</button>
  </li>
</ul>
```

---

#### 탭 1: SaaS 플랜

**화면 구성**:
- 플랜 3개(BASIC/PRO/ENTERPRISE)를 카드형식으로 렬더
- 각 카드 내 수정 가능한 입력 필드 직접 노출

**각 소플랜 카드 내부 필드**:

```
[기본 정보]
- 한글 플랜명 (display_name)     입력
- 대상 설명 (description)         입력
- 배지 색상 (badge_color)         select (secondary/primary/dark/success)
- 활성화 (is_active)               토글 스위치

[월정액 과금]
- 월 기본료 (monthly_base_fee)     숫자 입력 (KRW)
- 포함 인원 (included_users)       숫자 입력 (-1 = 무제한)
- 초과 1인당 (extra_user_fee_v2)   숫자 입력 (KRW)
- 최대 시설 수 (max_sites)          숫자 입력 (-1 = 무제한)

[연간 결제]
- 연간 기본료 (annual_base_fee)     숫자 입력 (KRW)
- 연간 할인율 (annual_discount_rate)  숫자 입력 (%)
- 무료 제공 개월 (annual_free_months)   숫자 입녉 (개월)

[콘텐츠 포함 여부]
- 실행이력 보관 (storage_history_month)  숫자 입력 (개월, -1=무제한)
- 업무할당 (include_task_assign)        토글
- 그룹관리 (include_group_mgmt)         토글
- 누락알림 (include_miss_alert)          토글
- API연동 (include_api_v2)               토글
- 안전인식콘텐츠 (include_safety_content)  select (basic/advanced/custom)
- 대시보드 (include_dashboard)            select (basic/advanced/custom)
```

**UX 요구사항**:
- ENTERPRISE 플랜: 대부분 필드 disabled + `협의` 표시
- `monthly_base_fee` 수정 시 실시간 미리보기 (KRW 포맷 표시)
- 저장 시 포함된 디스카운트 요금 = monthly_base_fee × 10 자동 계산 표시

---

#### 탭 2: 단건 진단 요금

**화면 구성**: 테이블 형식 (6개 행)

```
[테이블 콼럼]
No. | 시설 유형 | 기초진단(원) | 공정진단(원) | 설비진단(원) | 종합리포트(원) | 활성화
```

**UX 요구사항**:
- 소계선 행에서 직접 수정 (inline edit)
  - 입력포쾸스 시 일반 텍스트 → `<input type="number">`로 전환
  - 포쾸스가 빠지면 연필 아이콘 표시
- 수정된 행은 노란색 ?틄 표시
- `저장` 시 변경된 행만 PATCH

---

#### 탭 3: 변경 이력

**화면 구성**: 읽기전용 테이블

```
[테이블 콼럼]
No. | 변경일시 | 테이블명 | 플랜명 | 필드명 | 도전 | 변경후
```

- 최근 50건 표시
- 포맷: 변경후 값 파란색 표시

---

### 3-3. `price-setting.page.js` 구조

```javascript
// 전체 흐름
const API = window.TAI_CONFIG.API_BASE;  // config.js에서 가져오는 기본 URL

// 코드 실행 시
// 1) GET /price-setting/saas-plans 호출 → 플랜 3개 콴포넌트 각각 렌더
// 2) GET /price-setting/diagnosis-reports 호출 → 테이블 렌더
// 3) GET /price-setting/change-logs 호출 → 이력 테이블 렌더

// 저장 버튼 (폴리숙)
async function saveAll() {
  // SaaS 플랜: 변경된 플랜만 PATCH
  for (const plan of changedPlans) {
    await fetch(`${API}/price-setting/saas-plans/${plan.id}`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(plan.changes)
    });
  }
  // 단건 진단: 변경된 행만 PATCH
  for (const row of changedDiagnosisRows) {
    await fetch(`${API}/price-setting/diagnosis-reports/${row.id}`, {
      method: 'PATCH',
      ...row.changes
    });
  }
  showToast('저장되었습니다.', 'success');
  reload(); // 이력 다시 로드
}

// 소수 변경시 뷰 업데이트
// monthly_base_fee 재입력 시 디스카운트 미리보기 자동 업데이트
function updateDiscount(planEl) {
  const base = parseFloat(planEl.querySelector('[name=monthly_base_fee]').value) || 0;
  const freeMonths = parseInt(planEl.querySelector('[name=annual_free_months]').value) || 0;
  const annualFee = base * (12 - freeMonths);
  planEl.querySelector('.preview-annual-fee').textContent = annualFee.toLocaleString() + '원';
}
```

---

### 3-4. 서비스 연동 (핵심)

**목적**: 관리자가 설정한 가격이 실제 서비스에서 가져왔져 사용됨

**어디서 가져오는지 (api.js 또는 해당 페이지)**:

```javascript
// 하단 제어 흐름 (직접 구현 시)

// 1. 백엔드에서 GET /price-setting/saas-plans 호출
// 2. 프론트 콘트랙트/결제 페이지에서:
//    플랜 목록을 DB에서 보여주고
//    가격도 DB에서 가져오는 것
//    하드코딩 금지

// 이미 구현된 my-contract.html, 결제 페이지에서
// price_saas_plan 데이터를 폼에 쓰고 있는 경우 새로 연동
// (my-contract.html에서 실제 사용하는지 확인 시간 없으면 pass)
```

---

## 4. 작업 순서

```
[1단계] 백엔드 먼저
  app/routers/price_setting.py 생성
  app/main.py에 router 등록
  데플로이 후 GET /price-setting/saas-plans 응답 확인

[2단계] 프론트엔드
  price-setting.html 생성
  price-setting.page.js 생성
  메뉴에 가격설정 링크 추가 (모든 tadmin html 포함)

[3단계] 통합 테스트
  1) 플랜 목록 로딩 확인
  2) 월기본료 수정 → 저장 → 변경이력 확인
  3) 단건진단 요금 수정 → 저장 → 변경이력 확인
```

---

## 5. 체크리스트

```
DB
  [x] price_saas_plan v2 콼럼 추가 완료
  [x] price_diagnosis_report 테이블 생성 + 기본데이터 완료
  [x] price_change_log 테이블 생성 완료

백엔드 (Cursor창)
  [ ] app/routers/price_setting.py 생성
  [ ] main.py 라우터 등록
  [ ] Railway 데플로이 후 쾀포인트 동작 확인

프론트엔드 (Cursor창)
  [ ] price-setting.html 생성
  [ ] price-setting.page.js 생성
  [ ] 모든 tadmin html 메뉴에 가격설정 링크 추가
  [ ] 동작 확인 (로딩/수정/저장/이력)
```

---

## 6. 참고사항

- `education-setting.html` 구조를 반드시 참고해서 동일한 레이아웃/스타일 적용
- 수실 종류 비교: `No.` 두 번째 콼럼, 첫 번째 체크박스 (가격설정은 단리 선택 불필요하면 체크박스 제거 가능)
- `config.js` 의 `window.TAI_CONFIG.API_BASE` 사용
- Toast 메시지: `tai/toast.js` 사용
- 인증 토큰: `localStorage.getItem('access_token')` 사용
