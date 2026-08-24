# WP-FRONT-01 — VUE3 ASSET INVENTORY

- baseline: `tai-admin@0a61fe5e4f287e7a3472c914b98387aa05c802b2`
- scope: `vue3/src/` (tai-admin)
- 방법: MCP read-only 직독 + GitHub code search 인덱스 카운트
- mutation: 0 (code / DB / API / repo)

## 1. 전체 수치

측정 방식을 EXACT(직독 열거)와 SEARCH-INDEX COUNT(GitHub code search)로 명시 구분한다.

| 항목 | 수치 | 측정 |
|---|---|---|
| vue3/src 최상위 디렉토리 | 13 | **EXACT** (직독 열거: @core, @layouts, assets, components, composables, constants, layouts, navigation, pages, plugins, stores, utils, views) |
| 최상위 파일 | 2 | **EXACT** (App.vue, main.ts) |
| pages 라우트 디렉토리 | 51 | **EXACT** (직독 열거) |
| pages 최상위 .vue | 4 | **EXACT** ([...error], forgot-password, login, reset-password) |
| `.vue` 파일 | 117 | SEARCH-INDEX COUNT |
| `.ts` 파일 | 193 | SEARCH-INDEX COUNT (테스트/@core/@layouts 포함) |
| indexed `.vue` + `.ts` | 310 | SEARCH-INDEX COUNT |
| `api.request` 사용 파일 | 94 | SEARCH-INDEX COUNT |
| `factory_id` 사용 파일 | 65 | SEARCH-INDEX COUNT |
| `/work-schedules` 참조 파일 | 6 | SEARCH-INDEX COUNT |

> **EXACT TOTAL FILE COUNT = NOT MEASURED.** MCP에 recursive git-tree 도구가 없어 vue3/src 전체 파일의 완전 열거는 수행하지 못했다. 117/193/310은 GitHub code search가 인덱싱한 텍스트 파일 기준의 count이며, assets의 css/json/svg 등 비인덱싱 파일은 포함하지 않으므로 **"정확한 전체 파일 수"가 아니다**. 이 수치는 SCOPE FREEZE 판단에는 충분하나 exact total의 증거로 인용해서는 안 된다. pages의 51개 라우트 디렉토리와 최상위 구조는 직독 열거로 EXACT 측정했다.

## 2. 디렉토리 역할

- `pages/` — 51개 라우트 디렉토리. 각 디렉토리는 대체로 `index.vue`(뷰) + `use{Name}List.ts`(조회 로직) + `use{Name}Panel.ts`(상세/편집) 조합. 파일 기반 라우팅(route slug = 디렉토리명).
- `composables/` — 7개 공통 컴포저블: `useAuth`, `useHelpCtx`, `useMenuCatalog`, `useRowSelection`, `useSupportAsk`, `useTaiApi`, `useToast` (+ `__tests__`).
- `utils/` — 페이지별 `*Format.ts`(표시 포맷/unwrap) + 공통 `statusLabels.ts`(status 라벨 정본).
- `stores/` — Pinia 스토어(`useSystemCodesStore`, `useTbmListStore` 등).
- `components/` — 공통 컴포넌트(`NoticeStrip.vue`, `SupportWidget.vue` 등).
- `@core/`, `@layouts/` — Vuexy 템플릿 프레임워크. 본 WP 대상 아님(프레임워크 계층).
- `constants/`, `navigation/`, `plugins/`, `layouts/`, `views/` — 프레임워크/라우팅/설정 계층.

## 3. inspection/schedule 직접 관련 자산 (핵심 대상)

| 디렉토리 | 파일 | flow |
|---|---|---|
| work-schedule-list | index.vue, useWorkScheduleList.ts, useWorkSchedulePanel.ts | D 작업일정 / E 담당자배정 |
| my-inspection | index.vue, useMyInspectionList.ts, useMyInspectionPanel.ts | B 세트 / C 일정 / F 시작 / G 완료 |
| inspection-anchor | index.vue, useInspectionAnchorList.ts | B 기준일 설정 |
| inspection-calendar | useInspectionCalendarList.ts (+index) | K 캘린더 / G 완료 |
| inspection-custom | useInspectionCustomList.ts, Panel | 커스텀 점검 |
| engine-schedule | useEngineScheduleList.ts, Panel | 스케줄 엔진 |
| safety-dashboard | useSafetyDashboard.ts | 통합 대시보드(일정 통계) |
| construction-inspection-* | list, anchor | 건설 점검 |

## 4. 공통 인프라 자산 (간접 의존)

- `composables/useTaiApi.ts` — 전 페이지 API wrapper. `request/list/upload/download`. BASE_URL prod `api.taieng.co.kr`, dev `/api` 프록시. 인증 `localStorage['access_token']` Bearer, 401→/login. 목록 파싱 계약 `data.data.items / data.data.total`.
- `composables/useAuth.ts` — 로그인/로그아웃/가드. 로그인 시 localStorage에 `factory_id`(=user.factory_id), `company_id`, `role_code`, 계약정보 저장.
- `composables/useRowSelection.ts` — 목록 선택 패턴(전 페이지 체크박스 선택).
- `utils/statusLabels.ts` — status 코드 라벨 정본(WS/WA/SITE/PTW/INSP_RESULT). "저장·전송·필터 비교는 영문 정본 유지" 명시.
- `utils/work-scheduleFormat.ts` — 작업일정 표시 유틸. STATUS_OPTIONS는 이미 canonical(planned/in_progress/completed).

## 5. 신뢰도 계층 (자산의 출처별)

- **원본 HTML/ES모듈 이식형** (실동작 화면 이식, 신뢰 높음): my-inspection, inspection-calendar, inspection-anchor, my-equipment, worker-list, document-forms, safety-dashboard.
- **라이브 관찰 신규작성형** (접근성 트리 캡처 기반, 계약 "추정" 표기): work-schedule-list, equipment-qr-manager.
  - 단, 본 WP의 백엔드 직독 결과 이 "추정" 계약들도 실제 백엔드에 존재함이 확인됨(§API_CONTRACT_AUDIT 참조).
