---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-19 어드민 메뉴 정리 (운영자 관점 재설계)
version: 4
status: DONE
owner: taiwang
---

# WO-19 — 어드민 메뉴 정리 (admin.taieng.co.kr)

- **작성일:** 2026-07-29 (v4: 구현 완료)
- **Goal:** G-ms4je4z3-33eada
- **최종:** IMPLEMENTED. 배포(Cloudflare Pages feat/admin-rebuild) 후 사이드바 육안 확인은 사용자 게이트.

---

## 0. 정정 이력

- v1/v2: `main`의 레거시 admin/menu-nav.js 수정 → **구자산 오류**, 원복 완료(efc807e, blob fa4be19).
- v3: 대상 정정(admin.taieng.co.kr = feat/admin-rebuild의 admin-vue3) + 운영자 관점 재설계.
- **v4: 구현 완료** (커밋 b108a9b, feat/admin-rebuild).

## 1. 구현 결과 (커밋 b108a9b)

**오브젝트:** `admin-vue3/src/navigation/horizontal/index.ts` (이 어드민은 horizontal 레이아웃 사용. vertical은 대시보드 1건만 — 무수정).

**12그룹(도메인) → 7표시그룹(운영자 관점):**
1. **관제** — 자동QA·내부API·외부API (+⊕관제홈 주석)
2. **고객** — 회사관리·시설관리·회원관리·문의관리 (+⊕온보딩 주석, 인력 주석)
3. **매출·결제** — 구독/계약·가격설정 (+⊕경영지표·결제원장·세금계산서 주석, 견적 주석)
4. **서비스 운영** — 법령진단 5·교육 2·SaaS 4 (안전관리 데이터 제거)
5. **커뮤니케이션** — 메일 2·알림 2·푸시 (+⊕공지배너 주석)
6. **마케팅** — 지식인관리 + 마케팅엔진 18 (**원본 무수정**, 45cm 공유)
7. **개발자도구**(최하단) — 엔진 12 + 관제엔진 4 + 다이어그램

**제거(주석, 오픈 시 해제):** 매칭 그룹 전체 / 견적 2 / 인력 / **위험 그룹 통째**(산업 4 + 건설 5 + 지도).

**설계 결정(사용자 지시):**
- 위험 그룹 제거 — 운영자는 해당 회사 SaaS(safe)에 직접 로그인해 점검(admin 중복 불요).
- 고객 그룹: 회사관리를 시설관리보다 위(회사→시설N 상위개념).

## 2. 검증

| 항목 | 상태 | 근거 |
|---|---|---|
| 마케팅 그룹 원본 무수정 | VERIFIED | 원문 평문 복사, route name 18개 동일 |
| 실재 route만 활성(404 방지) | VERIFIED | admin-vue3/src/pages 78개 대조 — 활성 항목 전부 실재 |
| ⊕신설(미구현) 주석 처리 | VERIFIED | ops-home·stats-business·tax-ops·onboarding-ops·notice·payment-ledger 미존재 → 주석 |
| 엔진 개발자도구 강등 | VERIFIED | 최하단 그룹, 관측 경로 보존 |
| vertical 무영향 | VERIFIED | horizontal 레이아웃 사용, vertical=대시보드 1건 |
| 사이드바 육안 | PENDING | Cloudflare Pages 배포 후 사용자 확인 |

## 3. 후속

- **⊕ 신설 6종의 Vue 페이지 이식**(관제홈·경영지표·세금계산서·온보딩·공지배너·결제원장) → WO-20/D그룹. 이식 시 route name 부여하며 주석 해제.
- 회사관리에 "해당 회사 SaaS 대리로그인" 버튼(고객360 WO-6 확장) — 별도.
- 미서비스 오픈 시 해당 그룹 주석 해제.

## 4. 산출물

1. `admin-vue3/src/navigation/horizontal/index.ts` (재구성, b108a9b, feat/admin-rebuild)
