# 어드민 가격설정 페이지 수정 작업지시서

## 대상 파일
`admin/full-version/assets/js/tai/pages/price-setting.page.js` (39KB)

## 배경
- DB에 features, target, is_recommended, is_custom (SaaS) / features, icon, goods_name, is_recommended, is_special, sub_label (진단) 컨럼 추가 완료
- 백엔드 PATCH API에 해당 필드 지원 완료 (`/price-setting/saas-plans/{id}`, `/price-setting/diagnosis-reports/{id}`)
- pricing.html은 pricing-v2.js로 DB 완전 연동 완료
- 어드민 페이지만 미수정 상태

## 수정 1: SaaS 탭 — 하드코딩 제거, DB 직접 렌더링

### 현재 문제
- `SECTOR_META`에 INDUSTRY_L1~L4, FACILITY_L1~L4 하드코딩 → 실제 DB에는 BUILDING_BASIC, INDUSTRY_STARTER_V2 등 다른 코드
- 하드코딩 카드만 보여주고, DB의 실제 플랜은 표시 안 됨

### 수정 방향
1. `SECTOR_META` 삭제
2. 서브탭을 BUILDING / INDUSTRY / CONSTRUCTION으로 변경
3. `loadSaasPlans()`에서 `/price-setting/saas-plans?sector=BUILDING` 등으로 로드
4. 각 플랜 카드에 아래 필드 편집 추가:
   - `plan_name` (text)
   - `display_name` (text)
   - `description` (text)
   - `target` (text)
   - `features` (textarea, JSON 배열 — 예: `["\ubc95\ub839 \uc790\ub3d9 \ud310\uc815", "\uc810\uac80 \uc77c\uc815 \uc790\ub3d9"]`)
   - `is_recommended` (checkbox)
   - `is_custom` (checkbox)
   - `sector_code` (select: BUILDING/INDUSTRY/CONSTRUCTION)
5. `savePlan()`에 위 필드들을 body에 포함

## 수정 2: 법령진단 탭 — 새 필드 컨럼 추가

### 현재 문제
- 테이블에 basic_fee, process_fee, equipment_fee, total_report_fee, is_active만 표시
- goods_name, icon, features, sub_label, is_recommended, is_special 편집 불가

### 수정 방향
`loadDiagnosisReports()` 함수의 테이블 렌더링에 컨럼 추가:

| 컨럼 | 필드 | 타입 |
|---|---|---|
| 상품명 | facility_type_name | text input |
| 아이콘 | icon | text input (이모지) |
| 결제상품명 | goods_name | text input |
| 보조레이블 | sub_label | text input |
| 서비스 내용 | features | textarea (JSON) |
| 추천 | is_recommended | checkbox |
| 특수시설 | is_special | checkbox |

`saveDiagnosisRow()` body에 해당 필드 포함:
```js
var body = {
  basic_fee: ...,
  process_fee: ...,
  equipment_fee: ...,
  total_report_fee: ...,
  is_active: ...,
  // 신규
  facility_type_name: fv('facility_type_name'),
  icon: fv('icon'),
  goods_name: fv('goods_name'),
  sub_label: fv('sub_label'),
  features: JSON.parse(fv('features') || '[]'),
  is_recommended: fb('is_recommended'),
  is_special: fb('is_special'),
};
```

## 수정 후 저장 시 API 캐시 초기화

저장 성공 후 `DELETE /public/pricing/cache` 호출하여 프라이싱 페이지에 즉시 반영:
```js
await apiCall('DELETE', '/public/pricing/cache');
```

## 서비스 레이어 규칙
- 파일 최대 400행 (15KB)
- 현재 39KB — 수정 후도 단일 파일 유지 (탭별 분리는 후속)
