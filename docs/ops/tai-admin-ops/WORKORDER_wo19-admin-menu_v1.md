---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-19 어드민 메뉴 정리 (운영자 관점 재설계)
version: 3
status: ACTIVE
owner: taiwang
---

# WO-19 — 어드민 메뉴 정리 (admin.taieng.co.kr)

- **작성일:** 2026-07-29 (v3: 대상 정정 + 운영자 관점 재설계)
- **Goal:** G-ms4je4z3-33eada

---

## 0. 정정 이력 (중요)

- **v1/v2 오류:** `main` 브랜치의 레거시 `admin/full-version/assets/js/tai/menu-nav.js`를 수정했으나, 이는 **미배포 구자산**이었음. 원복 완료(커밋 efc807e, blob fa4be19 복원).
- **실측 확정:** admin.taieng.co.kr 운영 소스 = **`feat/admin-rebuild` 브랜치의 `admin-vue3/`** (Cloudflare Pages `tai-admin-admin-vue3`, Domains에 admin.taieng.co.kr). 메뉴 정의 = `admin-vue3/src/navigation/horizontal/index.ts` (blob 41c029a). vertical은 horizontal 재사용.
- tadmin = safe SaaS(사용자용), 별개. site = 마케팅. 모두 무관.

## 1. 현황 (실측, 12그룹)

대시보드 / 상황감시 / 고객 / 결제 / **마케팅(+엔진 17)** / 교육 / SaaS / 매칭 / 법령진단 / 위험(산업+건설) / 엔진(13) / 관제엔진(4).

## 2. 운영자 관점 재설계 (12 → 6 표시그룹 + 개발자도구)

**설계 원칙:** 도메인 분류(개발자 관점) → "지금 무슨 일을 하는가"(운영자 관점). 하루 시작점(관제) 최상단, 엔진·미서비스는 시야에서 제거. P1·P2 운영도구(⊕) 제자리 배치.

**1. 관제** (tabler-dashboard): 관제홈⊕ / 자동QA / 내부API / 외부API
**2. 고객** (tabler-users): 회사관리 / 시설관리 / 회원관리 / 문의관리 / 온보딩현황⊕
  - 회사관리가 시설관리보다 위(회사→시설N 상위개념).
**3. 매출·결제** (tabler-credit-card): 경영지표⊕ / 결제내역·원장 / 구독·계약 / 세금계산서⊕ / 가격설정
**4. 서비스 운영** (tabler-briefcase): 법령진단(익명·리포트·뷰어·진단연결) / 교육(이수·마스터) / SaaS설정(권한·알림·문서·FAQ)
  - **안전관리 데이터(위험 그룹) 제거** — 운영자는 해당 회사 SaaS(safe)에 직접 로그인해 점검(사용자 지시). admin 중복 불요.
**5. 커뮤니케이션** (tabler-mail): 메일(목록·발송)✅Gmail / 알림(센터·관리·푸시) / 공지배너⊕
**6. 마케팅** (tabler-speakerphone): 지식인관리 + 마케팅엔진 17 — **보존**(mkt 서빙 WO-201/202, 45cm 공유 브랜치이므로 절대 무수정)
**7. 개발자도구** (tabler-cpu, 최하단): 엔진 13 + 관제엔진 4 + 다이어그램

## 3. 제거 (주석 — 오픈 시 복원)

- **매칭** 전체(상담·수선·수선설정·선임연결·크몽·크몽편집)
- **결제**의 견적관리·견적설정
- **위험** 그룹 통째(산업 공정·설비·시설설비·점검 + 건설 5 + 지도) — SaaS로 일원화
- 인력/전문가(personnel) — 선임 미서비스

## 4. ⊕ 신설 항목 = P1·P2 산출물의 화면 연결 지점 (D그룹 게이트)

관제홈(WO-13)·온보딩(WO-17)·경영지표(WO-14)·세금계산서(WO-15)·결제원장(WO-7)·공지배너(WO-16). 지금은 API만 있고 화면 미연결 → 이 메뉴가 연결의 지도. 메뉴엔 route name 자리를 잡되, 페이지 미구현분은 후속(WO-20 Vue 이식/D그룹)에서 채움.

## 5. 완료 판정 (IMPLEMENTED)

- `admin-vue3/src/navigation/horizontal/index.ts` 재구성(feat/admin-rebuild 브랜치).
- 마케팅 그룹 무변경(45cm 공유). 개발자도구 강등. 미서비스 주석.
- 배포(Cloudflare Pages, feat/admin-rebuild) 후 사이드바 육안 확인(사용자 게이트).

## 6. 후속

- 회사관리에 "해당 회사 SaaS 대리로그인" 버튼(고객360 WO-6 확장) — 별도 작업.
- ⊕ 신설 메뉴의 실제 페이지(Vue) 구현 — WO-20/D그룹.
