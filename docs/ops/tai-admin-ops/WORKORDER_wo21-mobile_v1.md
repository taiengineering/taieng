---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-21 어드민 모바일 대응
version: 1
status: DONE
owner: taiwang
---

# WO-21 — 어드민 모바일 대응 (admin.taieng.co.kr)

- **작성일:** 2026-07-29
- **Goal:** G-ms4je4z3-33eada
- **브랜치:** `feat/admin-rebuild`

---

## 0. 문제

모바일 햄버거 메뉴에 "대시보드" 1건만 노출.

## 1. 원인 (실측)

- `layouts/default.vue`의 `switchToVerticalNavOnLtOverlayNavBreakpoint()` → 모바일(브레이크포인트 이하)에서 **vertical nav 레이아웃으로 자동 전환**.
- `DefaultLayoutWithVerticalNav.vue`는 `import navItems from '@/navigation/vertical'` → 햄버거(tabler-menu-2) 드로어가 vertical nav를 사용.
- `navigation/vertical/index.ts`에 대시보드 1건만 있었음 → 모바일 햄버거에 대시보드만 노출.
- (데스크톱은 horizontal nav 사용 — 전체 메뉴 정상 노출됨.)

## 2. 해결

- **`navigation/vertical/index.ts` → horizontal 재사용**: 두 nav 아이템 구조 동일({title,to,icon,children})이라 `export default horizontalNav`로 재사용. 모바일 햄버거에 전체 7그룹 노출. 데스크톱 무영향.
- 커밋 ea60bd1.

## 3. 페이지별 모바일 반응형 점검·수정

| 페이지 | 조치 | 커밋 |
|---|---|---|
| ops-home | 오늘의 숫자 cols=4 → cols=6 sm=4(모바일 2열) | d457e23 |
| payment-ledger | 원장 드로어 width 반응형(useDisplay mobile→340), 필터 min-width, 표 text-no-wrap | c22fdbf |
| notice | 다이얼로그 VCol cols=12 sm=6(세로 쌓임), 필터 min-width, 표 text-no-wrap | 37ee644 |
| stats-business | KPI cols=6 lg=3(기존 OK), 표 VTable 자동 가로스크롤 — 수정 불요 | — |
| tax-ops | 요약 cols=6 lg=3(기존 OK), 탭 표 VTable 자동 가로스크롤 — 수정 불요 | — |
| onboarding-ops | 좌우 cols=12 md=5·7(기존 OK, 모바일 세로) — 수정 불요 | — |

### 반응형 원칙(확립)
- 카드 그리드: 모바일 최소 cols=6(2열) 이상, 좁은 카드는 cols=12.
- 드로어: `useDisplay().mobile` → 모바일 폭 축소.
- 다이얼로그 내부 입력: cols=12 sm=6(모바일 세로).
- 넓은 표: VTable 기본 `.v-table__wrapper` overflow-x auto로 가로 스크롤. 셀은 text-no-wrap로 줄바꿈 방지.

## 4. 완료 판정

- 햄버거 전체 메뉴 노출 수정 완료(ea60bd1).
- 페이지 3종 반응형 수정, 3종 기존 OK 확인.
- **배포(Cloudflare Pages feat/admin-rebuild) 후 모바일 육안 확인은 사용자 게이트:**
  1. 햄버거에 7그룹 전체 노출되는지
  2. 각 페이지 모바일 폭에서 가로 넘침·잘림 없는지
  3. 결제원장 원장 드로어·공지 다이얼로그가 화면 안에 들어오는지
