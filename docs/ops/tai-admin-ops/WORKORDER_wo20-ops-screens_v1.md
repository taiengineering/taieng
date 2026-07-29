---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-20 운영도구 화면 이식 (Cursor 핸드오프)
version: 1
status: ACTIVE
owner: taiwang
---

# WO-20 — 운영도구 화면 admin-vue3 이식 (Cursor 핸드오프)

- **작성일:** 2026-07-29
- **Goal:** G-ms4je4z3-33eada
- **브랜치:** `feat/admin-rebuild` (admin.taieng.co.kr 운영 소스)
- **선행 완료:** 관제홈(ops-home) 파일럿 이식 완료 — **이게 참조 템플릿**.

---

## 0. 배경

P1·P2에서 운영 API 6종을 만들었으나 admin에 화면이 없어 WO-19 메뉴에서 주석 처리됨.
이 WO는 그 6종 중 나머지 5종의 Vue 페이지를 이식해 메뉴를 활성화한다.

## 1. 확립된 패턴 (관제홈 참조)

**참조 파일(이미 커밋됨):**
- `admin-vue3/src/pages/ops-home/useOpsHome.ts` (composable, b47ed37)
- `admin-vue3/src/pages/ops-home/index.vue` (페이지, b2cf3f2)

**규칙:**
1. 페이지 = `src/pages/<slug>/index.vue` + `src/pages/<slug>/useX.ts`.
2. API: `import { useTaiApi } from '@/composables/useTaiApi'` → `api.request('GET', '/path')`.
   오류: `import { apiErrorMessage } from '@/composables/useApiError'` → err면 throw → catch 폴백(무토스트).
3. 응답: `r.data.xxx`. UI: Vuetify(VCard/VRow/VCol/VChip/VAvatar/VProgressCircular). Bootstrap 금지.
4. `definePage({ name: '<slug>' })`. `onMounted(load)`. loading 스피너·error 폴백 필수.
5. 한 파일 400줄 이하. 표 많으면 useX.ts에 로직 분리.
6. 이식 완료 후 `admin-vue3/src/navigation/horizontal/index.ts`의 해당 ⊕ 주석 1줄 해제.

## 2. 이식 대상 5종 (slug / API / 핵심 필드)

### 2-1. 경영지표 — slug `stats-business`, 그룹 '매출·결제'
- **API:** `GET /stats/business` (services/stats_provider_svc.get_stats)
- **응답:** `revenue{total_success, by_product[], diagnosis_paid_total}` · `subscription_metrics{mrr, active_count}` · `payment_health{success_rate, ...}` · `conversion{diagnosis_to_saas_rate, ...}`
- **화면:** MRR·총매출·성공률·전환율 지표 카드 4 + 제품별 매출 표. (목업 결제 0이라 대부분 0 반환 정상)

### 2-2. 세금계산서 — slug `tax-ops`, 그룹 '매출·결제'
- **API:** `GET /tax/ops`(요약) · `GET /tax/unissued`(미발행) · `GET /tax/issued`(발행목록)
- **응답:** invoice_status_summary · unissued_payments[] · issued_list[]
- **화면:** 발행/미발행 건수 카드 + 미발행 결제 표(payment_id·company·supply_cost) + 발행목록 표(nts_confirm_num). 리스트 첫 컬럼=전체선택 체크박스, 둘째=No.(개발규칙)

### 2-3. 온보딩 현황 — slug `onboarding-ops`, 그룹 '고객'
- **API:** `GET /companies/{id}/onboarding` (services/onboarding_svc.get_checklist) — **회사별**.
- **주의:** 단일회사 API라, 목록화면은 회사 선택 → 체크리스트 4단계(company_info·factory_added·diagnosis_done·subscription_active) + progress_pct·next_step 표시. 회사 선택은 company-list 재사용 또는 자동완성.
- **화면:** 회사 검색/선택 → 진행률 바 + 4단계 체크리스트 + next_step 안내.

### 2-4. 공지배너 — slug `notice`, 그룹 '커뮤니케이션'
- **API:** 어드민 CRUD `GET/POST/PATCH/DELETE /notices` + 토글 + `GET /notices/active?channel=`
- **응답:** notice_banner 행(title·body·channels[MARKETING|SAFE]·banner_type·link_url·starts_at·ends_at·priority·enabled)
- **화면:** 공지 목록 표(채널·유형·기간·활성 토글) + 생성/수정 다이얼로그(채널 다중선택·기간·우선순위). 리스트 규칙(체크박스·No.).

### 2-5. 결제내역·원장 — slug `payment-ledger`, 그룹 '매출·결제'
- **API:** `GET /payments/ledger` (routers/payment_ledger.py — 응답 구조는 라우터 확인 필요)
- **주의:** 라이브 `payment-list`(구 slug)는 status todo였음. 신규 payment-ledger로 이식.
- **화면:** 결제 목록 표(회사·금액·상태·수단·일시) + 상태/기간 필터. 리스트 규칙(체크박스·No.).

## 3. 각 이식 후 필수

- navigation `horizontal/index.ts`의 해당 ⊕ 주석 해제(1줄).
- Cloudflare Pages(feat/admin-rebuild) 배포 확인 + 해당 화면 접속 육안.

## 4. 완료 판정

5종 페이지 + composable 커밋, navigation 5개 주석 해제, 배포 후 각 화면 로드 확인(사용자 게이트).
API가 목업 0을 반환해도 화면이 정상 렌더(0/빈 표)면 PASS.
