---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-19 어드민 메뉴 정리
version: 2
status: DONE
owner: taiwang
---

# WO-19 — 어드민 메뉴 정리 (admin.taieng.co.kr)

- **작성일:** 2026-07-29 (v2: 구현 완료)
- **Goal:** G-ms4je4z3-33eada
- **최종:** IMPLEMENTED. 배포 후 육안 확인은 사용자 게이트.

---

## 1. 현황 (실측)

- 운영자 어드민 메뉴 = `admin/full-version/assets/js/tai/menu-nav.js`의 `MENU` 배열 하나(원래 12그룹).
- tadmin(safe SaaS)·site(마케팅)는 별개 — 무변경.

## 2. 구현 (완료, 커밋 b0aafc3)

**b 방식: 미서비스 삭제(주석) + 엔진 강등.** 로직(guardAdminAccess/buildMenuHtml/renderMenu) 무변경, MENU 배열만 재구성.

**유지(무변경):** 상황감시 / 고객 / 결제 / 마케팅 / 교육 / SaaS / 법령진단 / 위험(산업) / 시스템.
- 마케팅(지식인관리) 보존 — 사용자 지시.

**주석 처리(미서비스, 오픈 시 해제):**
- 결제: 견적관리·견적설정.
- 매칭 그룹 전체(상담·수선·수선설정·선임연결·크몽계약·크몽편집).
- 위험: 건설 섹션 6개(건설현장~건설TBM).

**하단 강등:** 엔진(13) + 관제엔진(4) → **개발자도구** 단일 그룹, 배열 맨 끝. 엔진 격리 자산의 관측 경로는 보존하되 최하단.

**결과:** 12그룹 → 10그룹. 서비스/운영 메뉴가 상단, 엔진은 최하단.

## 3. 검증

| 항목 | 상태 | 근거 |
|---|---|---|
| 유지 그룹 링크·status 무변경 | VERIFIED | 재조회 diff — 상황감시~시스템 동일 |
| 미서비스 주석(JS 유효) | VERIFIED | 배열 요소 주석, 문법 정상 |
| 엔진 개발자도구 강등 | VERIFIED | 맨 끝 그룹, 관측 링크 보존 |
| 사이드바 육안 | PENDING | Cloudflare Pages 배포 후 사용자 확인 |

## 4. 산출물

1. `admin/full-version/assets/js/tai/menu-nav.js` (MENU 재구성, b0aafc3)

## 5. 후속

- 미서비스 오픈 시 해당 주석 블록 해제.
- Vue3 이식(WO-20) 시 이 정리된 구조를 신규 navigation 기준으로 반영.
