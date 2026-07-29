---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-20 운영도구 화면 이식
version: 2
status: DONE
owner: taiwang
---

# WO-20 — 운영도구 화면 admin-vue3 이식

- **작성일:** 2026-07-29 (v2: 6종 전부 이식 완료)
- **Goal:** G-ms4je4z3-33eada
- **브랜치:** `feat/admin-rebuild` (admin.taieng.co.kr 운영 소스)
- **방식:** Claude 직접 이식(방식 b) — 각 API 응답을 실측하며 정확도 담보.

---

## 0. 배경

P1·P2에서 운영 API 6종을 만들었으나 admin에 화면이 없어 WO-19 메뉴에서 주석 처리됨.
이 WO는 그 6종 Vue 페이지를 전부 이식해 메뉴를 활성화한다.

## 1. 확립된 패턴 (관제홈이 참조 템플릿)

1. 페이지 = `src/pages/<slug>/index.vue` + `src/pages/<slug>/useX.ts`(composable).
2. API: `useTaiApi().request('GET','/path')`. 오류: `apiErrorMessage(r)` → err면 throw → catch 폴백(무토스트).
3. 응답 `r.data.xxx`. UI: Vuetify(VCard/VRow/VCol/VChip/VTable/VDialog/VNavigationDrawer). Bootstrap 금지.
4. `definePage({ name: '<slug>' })`. `onMounted(load)`. loading 스피너·error 폴백 필수.
5. 이식 후 navigation `horizontal/index.ts` 해당 항목 주석 해제.

## 2. 이식 완료 6종 (실측 기반)

| slug | 그룹 | API(실측) | 화면 | 커밋 |
|---|---|---|---|---|
| `ops-home` | 관제 | GET /ops/home | 처리대기·이상신호·오늘의숫자·자산현황 | b47ed37·b2cf3f2 |
| `stats-business` | 매출·결제 | GET /stats/business | KPI 4카드(MRR·매출·성공률·전환율)+매출·구독·건전성 | 545e0ac·f6269e2 |
| `tax-ops` | 매출·결제 | GET /tax/ops·unissued·issued | 요약카드+탭(미발행 결제/발행 목록) | 5d736bd·e7c4d81 |
| `payment-ledger` | 매출·결제 | GET /payments + /payments/{id}/ledger | 필터·목록·페이지네이션+원장 드로어(환불·증빙·크레딧) *조회전용* | a829349·d4c17e0 |
| `notice` | 커뮤니케이션 | GET/POST/PATCH/DELETE /notices | 목록(활성토글)+생성/수정 다이얼로그(채널·유형·기간) | ce1776e·ec23ea8 |
| `onboarding-ops` | 고객 | GET /companies/{id}/onboarding | 회사검색+진행률바·4단계 체크리스트·next_step | 955eeb0·b919f86 |

navigation 활성화: 292dc86·737245e·fe097bc·16d9c0c·ac14f00·4a608e4.

## 3. 실측으로 잡은 오류(중요)

- WO-20 v1 문서의 API 필드명은 메모리 기반이라 부정확했음. 실제 이식 시 services/*.py·routers/*.py 실측으로 정정:
  - stats: `total_paid`(not total_success), `subscription.mrr`, `payment_health.success_rate_pct` 등.
  - **payment-ledger는 목록 API가 아님** — `/payments/{id}/ledger`는 결제 1건의 환불·증빙·크레딧 통합 조회. 목록은 payment_ops의 `/payments`(v_payments_list). → 목록+상세 드로어 구조로 이식.

## 4. 조회전용/후속

- **결제원장:** 환불·증빙·크레딧 **발행 액션(POST)은 조회전용으로 제외** — 첫 실결제 검증(B-1) 이후 별도 이식. 드로어에 안내 표시.
- **온보딩:** 회사별 단일 API라 회사 검색/선택 UI로 감쌈.

## 5. 완료 판정

- 6종 페이지+composable 커밋 완료, navigation 6개 활성화 완료.
- **배포(Cloudflare Pages feat/admin-rebuild) 후 각 화면 로드 확인은 사용자 게이트.**
  목업 데이터로 0/빈 표여도 화면이 정상 렌더되면 PASS.

## 6. 남은 후속

- 결제원장 액션 버튼(환불·증빙 발행) — B-1 이후.
- 회사관리 "해당 회사 SaaS 대리로그인"(고객360 WO-6 확장) — 별도.
- 남은 사람 게이트: A-2 팝빌, B-1 이니시스 환불, C-1 목업 정리.
