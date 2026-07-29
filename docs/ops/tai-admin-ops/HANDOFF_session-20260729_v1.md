---

class: records
type: HANDOFF
scope: ops
project: tai-admin-ops
title: TAI 어드민 1인 운영체계 — 세션 핸드오프 (2026-07-29)
version: 1
status: DONE
owner: taiwang
---

# TAI 어드민 1인 운영체계 — 핸드오프 (2026-07-29)

다른 계정에서 이 작업을 이어받는 새 세션을 위한 단일 진입 문서.
**먼저 이 문서를 끝까지 읽고, §1 골을 재확인한 뒤 §7 다음 작업으로 진행할 것.**

---

## 0. 이어받기 즉시 체크리스트

1. **guri-cf MCP 연결 확인** — `guri-cf:goal(action="show", code="G-ms4je4z3-33eada")` 호출해 ACTIVE 확인. 골은 세션 바뀌어도 유지됨(code로 조회).
2. **모든 guri-cf 호출에 `goal="G-ms4je4z3-33eada"` 전달** (작업 승인·감사 장치).
3. **execute_sql은 반드시 `project_ref="vwlahtguyggrhvslabax"` 명시** — 미지정 시 기본값(`iapzwbysfzootqnldtan`, 테이블 2개)으로 가서 헛조사됨. tai-api 실DB는 `vwlahtguyggrhvslabax`(서울, 599테이블).
4. **운영 소스는 `feat/admin-rebuild` 브랜치의 `admin-vue3/` 디렉토리** — main의 `vue3/`는 구버전(GitHub 코드검색은 main만 봄, 주의).

---

## 1. 골 (재생성 불필요 — 이미 ACTIVE)

- **code**: `G-ms4je4z3-33eada`
- **project**: `tai-admin-ops`
- **title**: TAI 어드민 1인 운영체계 구축 — 정밀분석
- **purpose**: 1인이 TAI 서비스(법령진단·SaaS 2종)의 관제와 운영을 admin.taieng.co.kr 어드민에서 전부 수행할 수 있게 한다.
- **pass_criteria**: 향후 발생할 수 있는 소비자 이슈(결제·환불·계정·데이터·문의) 및 서비스 이슈(장애·발송실패·배치실패)에 대해 어드민 화면만으로 대응이 전부 가능한 수준.
- **scope**: admin.taieng.co.kr 어드민. 서비스 범위는 **법령진단·SaaS 2종 + 교육**만. 미서비스(수선/매칭/전문가/견적/컨설팅/건설)는 제외.
- **exit_condition**: 운영 가능 수준 — 운영 필수 화면 목록 확정, 결손 기능 식별, 우선순위 구축계획 확정.

새 세션에서 골이 안 보이면 재조회: `goal(action="show", code="G-ms4je4z3-33eada")`. **새로 set 하지 말 것**(중복 생성 금지).

---

## 2. 인프라·리소스 (불변, 실측 확정)

**레포 (taiengineering org):**
- `tai-api` — FastAPI 백엔드, `main` push → Railway 싱가포르 자동배포
- `tai-admin` — 프론트(private). **운영 = `feat/admin-rebuild` 브랜치 `admin-vue3/`**
- `taieng` — 마케팅 + 문서. **모든 작업문서는 `docs/ops/tai-admin-ops/`에 저장**

**admin.taieng.co.kr 배포:**
- Cloudflare Pages 프로젝트 `tai-admin-admin-vue3` (project_id `d9af0928-def9-4037-9634-6ff16ab28329`)
- build `pnpm run build`, root_dir `admin-vue3`, 프로덕션 브랜치 `feat/admin-rebuild`
- env: VITE_API_BASE_URL=https://api.taieng.co.kr, VITE_TOKEN_KEY=access_token, VITE_LOGIN_PATH=/login
- 배포 확인: `cloudflare_api(GET /accounts/{account}/pages/projects/tai-admin-admin-vue3/deployments?per_page=N)` — path의 `{account}`는 플레이스홀더 그대로 사용

**DB (Supabase 서울):**
- tai-api 운영 DB ref = **`vwlahtguyggrhvslabax`** (599 테이블)
- execute_sql 기본값(`iapzwbysfzootqnldtan`)은 다른 프로젝트 — **반드시 project_ref 명시**

**결제:** KG이니시스. **카카오 API 전면금지.**

---

## 3. guri-cf MCP 도구·규범 (불변)

- `goal` — action set/show/close/list. 이미 ACTIVE, 재조회만.
- `github_get_file(owner,repo,path,ref,project,goal)` — ref로 브랜치 지정, 평문 반환.
- `github_put_file(branch,owner,repo,path,content,message,goal,project)` — SHA 불필요, 전체 덮어쓰기.
- `github_api(method,path,goal)` — REST. 코드검색은 main 브랜치만 봄(주의).
- `execute_sql(sql,project_ref,goal)` — **project_ref 필수**.
- `cloudflare_api(method,path,goal,project)` — 배포 상태 조회.

**제약:**
- 컨테이너 네트워크 비활성 — curl·web_fetch·tarball 불가.
- 200줄+ 대형 파일은 Cursor 사용 권장(단 이번 세션은 github_put_file 전체 재커밋으로 처리함).
- base64 수작업 전사 절대금지(한글 오염) — github_get_file로 평문 취득.
- 문서: 경로 `docs/ops/tai-admin-ops/`, frontmatter 필수 8필드(class[plans/records/normative]·type·scope·project·title·version·status·owner).

---

## 4. 이번 세션(2026-07-29) 완료 작업 — 커밋 해시 포함

### 4-1. 무한로딩 사고 hotfix ✅
- **증상**: admin.taieng.co.kr 접속 시 데스크톱·모바일 공통 무한로딩.
- **진짜 원인**: `navigation/horizontal/index.ts`가 **존재하지 않는 route name `report-v1-legacy`** 참조 → Vuetify 메뉴 렌더 시 router.resolve 실패 → 앱 마운트 멈춤. (실재 폴더는 `report_v1` 언더스코어)
- **수정**: `report-v1-legacy` → `report_v1`. **커밋 4d19138** (배포 success).
- 교훈: navigation route name은 반드시 `admin-vue3/src/pages/<slug>/` 실재 폴더와 대조.

### 4-2. 상태값 DB 전수조사 ✅ (실측, project_ref=vwlahtguyggrhvslabax)
- **payments.status_code: 132건 전부 PENDING** (SUCCESS·FAILED·CANCELLED 0). pg_method 전부 NULL.
- **subscriptions.status: PENDING 31 + FAILED 1 (ACTIVE 0)** → MRR·활성구독 0의 근본원인.
- diagnosis_purchases.status: PAID 16 (유일 정상완료). contracts: ACTIVE 4.
- refunds·credits·tax_invoices·notice_banner: 0행.
- **결론: 목업이 완료상태 없이 초기상태(PENDING)로만 적재됨. 화면 문제 아닌 데이터 문제. [사용자: DB는 목업이라 상관없음]**

### 4-3. 전역변수(system_codes) 전수조사 ✅
- 약 200개 카테고리. 상태 관련 정본은 **대부분 정상 등록됨**: payment_status(PENDING·SUCCESS·FAILED·CANCELLED), payment_method_type, service_status, invoice_status, report_status, education_status, notification_status, user_status, schedule_status, matching_status 등.
- **발견 문제 3 (미해결, 남은 과제):**
  1. **대소문자 중복 카테고리** — contract_status(11)/CONTRACT_STATUS(8), condition_operator/CONDITION_OPERATOR, inspection_type/INSPECTION_TYPE, inspection_cycle_unit/INSPECTION_CYCLE_UNIT, user_role 2벌(001·002·025 vs 010~022), building_use·construction_lv3·industry_type 이름중복. **정본 확정 필요.**
  2. **쓰레기 카테고리** — test, testaa, testaaaaaa, 빈("") 1건. **삭제대상.**
  3. **subscription_status 카테고리 없음** — DB subscriptions.status는 PENDING/FAILED/ACTIVE 쓰는데 전역변수 부재(service_status로 대용 추정).

### 4-4. 하드코딩 규칙위반(유형A) 교정 ✅ — 이번 세션 핵심 산출물
**규칙(WORKPLAN 3layer §3-3·§5-3): "코드값(상태값) 조회는 SystemCodesStore.get() 전역변수를 통해서만. 하드코딩 금지."**

위반 유형 분류(사용자 확정: **유형A만 교정, 유형B 색상매핑은 UI 로직으로 유지**):
- **유형A** = 필터/선택 옵션 배열 하드코딩 (전역변수로 100% 대체 가능) → 교정 대상
- **유형B** = 상태→색상 매핑(statusColor/typeColor) (전역변수에 색상 필드 없음) → 유지

**교정 완료 2건:**
| 화면 | 위반 | 교정 | 커밋 |
|---|---|---|---|
| payment-ledger | statusOptions 배열 하드코딩 | payment_status 전역변수 조회(usePaymentLedger.init) | c8fbce2(composable)·37cc531(index.vue) |
| notice | CHANNELS·BANNER_TYPES 상수 하드코딩 | 전역변수 신설 후 조회(useNotice.init) | 70d54ae(composable)·de3a873(index.vue) |

**전역변수 신설(system_codes INSERT, ON CONFLICT DO NOTHING):**
- `notice_channel`: MARKETING(마케팅)·SAFE(세이프) — 2건
- `banner_type`: INFO(정보)·WARNING(경고)·MAINTENANCE(점검)·EVENT(이벤트) — 4건

**확인 결과**: 기존 화면 contract-list·factory-list는 이미 필터옵션을 `codes.get()`으로 조회 → 유형A 위반 없음(준수). 유형A 위반은 이번에 새로 만든 payment-ledger·notice 2개에만 있었음.

---

## 5. 운영자 관점 진단 — [사용자 지시: 추가만 진행] 확정 4항목

우선순위순:
1. **주문/결제 처리 액션 (최우선)** — 결제원장이 조회만 되고 승인·취소·환불·증빙 버튼 없음. 백엔드 API는 전부 존재.
2. **상단 통합검색** — global_search_svc 완성됐으나 상단바 미연결.
3. **문의 답장** — inquiry 목록만, 답장 기능 미연결.
4. **관제홈 처리대기 → 실처리 연결.**

**주문처리 액션 백엔드 API (실측, schemas/payment.py):**
- 수동활성화(입금확인): `POST /payments/manual/confirm` body `{payment_id, contract_id}` — **contract_id 필수인데 ledger 응답에 없음 → 백엔드 ledger 응답 보강 선행 필요**
- 취소: `POST /payments/{id}/cancel` `{reason, cancelled_by}` — payment_id만, 지금 안전하게 붙일 수 있는 유일 액션
- 전액환불: `POST /payments/{id}/refund` `{reason, cancelled_by}` (이니시스 실호출)
- 부분환불: `POST /payments/{id}/refund/partial` `{amount, reason, by}`
- 세금계산서/현금영수증: `POST /payments/{id}/invoice/tax`·`/cash` (팝빌)
- 크레딧: `POST /payments/{id}/credit`

**안전원칙**: 환불·증빙은 실결제(B-1)·팝빌(A-2) 게이트 미완 → "수동활성화·취소"까지만, 환불·증빙은 게이트 후.

**통합검색**: `services/global_search_svc.py` 완성(회사·회원·사업장·결제 교차검색, {type,id,title,subtitle,company_id} 반환). 상단바 컴포넌트 `admin-vue3/src/layouts/components/NavSearchBar.vue`·`@core/components/AppBarSearch.vue` 존재하나 `DefaultLayoutWithHorizontalNav.vue` navbar에 미포함.

---

## 6. 3계층 아키텍처 규칙 (준수 필수)

정본: `taieng/docs/WORKPLAN_object-oriented-3layer_20260721.md` (= 프로젝트지식 tai-frontend-rebuild_WORKPLAN_object-oriented-3layer_2026-07-21.md). safe(tadmin) 대상이나 admin 동일 적용.

- **Shell**: 레이아웃/네비(프레임워크 흡수)
- **공유 오브젝트**: ApiClient(`useTaiApi`, `request()`), **SystemCodesStore(`useSystemCodesStore`, 계약 `get(categories)`)**, Toast(`useToast`), Auth(`useAuth`), RowSelection(`useRowSelection`), ApiError(`apiErrorMessage`)
- **Page 오브젝트**: 각 페이지의 store(필요시) + composable(useXxxList.ts) + index.vue

**§5-3 체크리스트(위반 금지):**
1. 원본 정독 후 이식
2. `window.` 직접대입·인라인 onclick 없음
3. **API 접근은 ApiClient, 코드값(상태값) 조회는 SystemCodesStore 통해서만**
4. build·typecheck 통과
5. 컴포넌트 간 내부 ref 직접참조 금지(props/emit/공개반환값만)
6. 패리티 편차 기록

**모범 패턴 (factory-list/useFactoryList.ts, contract-list/useContractList.ts):**
```
const codes = useSystemCodesStore()
const d = await codes.get('service_type,contract_status')  // → {category: [{code, code_name, ...}]}
statusOptions.value = d.contract_status || []
```

---

## 7. 다음 작업 (이어받아 진행)

우선순위 판단 후 진행. 사용자는 "추가만 진행" 지시 유지 중.

1. **[선택] 유형A 위반 기존화면 마저 스캔** — member-list·education-list·inquiry-list·anon-diagnosis-list 등 활성화면. contract-list·factory-list는 준수 확인됨. (전수 미완)
2. **주문/결제 처리 액션 추가 (§5-1, 최우선 후보)** — 먼저 `POST /payments/{id}/cancel`(payment_id만 필요, 안전)부터 결제원장 상세 드로어에 버튼 추가. 수동활성화는 ledger 응답에 contract_id 추가하는 백엔드 보강 선행.
3. **상단 통합검색 연결 (§5-2)** — DefaultLayoutWithHorizontalNav navbar에 NavSearchBar 추가 + global_search API 연결.
4. **전역변수 정합성 교정 (§4-3 문제 3)** — 대소문자 중복 정본 확정, test 카테고리 삭제, subscription_status 신설 여부.

**진행 시 원칙:**
- 실측 없이 가정 금지(이번 세션 사고들 다 가정 실수: admin=레거시 오판, report-v1-legacy 미대조, execute_sql 기본DB).
- 완료판정 IMPLEMENTED/VERIFIED/DONE/PENDING만. 검증없는 완료선언 금지.
- 사용자는 단어 하나("네","진행","b","a")로 승인. 질문 최소화·즉시실행. 한국어. ask_user_input_v0(팝업) 금지.
- INSERT: ON CONFLICT DO NOTHING. CONFIRMED/실데이터 신중.

---

## 8. 남은 사람 게이트 (PENDING)

- A-2 팝빌(세금계산서 실발행), B-1 이니시스 환불(첫 실결제 검증), C-1 목업 데이터 정리, D 프론트 연결(WO-20 완료).
- KG이니시스 승인 후 taieng.co.kr → new.taieng.co.kr 전환.
- vertical=horizontal 재사용(모바일 전체메뉴)은 롤백된 상태 — 로딩 해결 확인 후 안전 재적용 PENDING.

---

## 9. 기존 문서 링크 (taieng/docs/ops/tai-admin-ops/)

**계획·분석·리서치·런북:**
- [ANALYSIS_tai-admin-ops-precision_v1](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/ANALYSIS_tai-admin-ops-precision_v1.md) — 정밀분석
- [PLAN_admin-rebuild_v1](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/PLAN_admin-rebuild_v1.md) · [v2](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/PLAN_admin-rebuild_v2.md) · [v3](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/PLAN_admin-rebuild_v3.md)
- [WORKPLAN_admin-rebuild-object-oriented_v1](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKPLAN_admin-rebuild-object-oriented_v1.md)
- [RESEARCH_saas-admin-benchmark_v1](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/RESEARCH_saas-admin-benchmark_v1.md)
- [RUNBOOK_human-gates_v1](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/RUNBOOK_human-gates_v1.md) — 사람 게이트 런북

**3계층 규칙 정본:**
- [WORKPLAN_object-oriented-3layer_20260721](https://github.com/taiengineering/taieng/blob/main/docs/WORKPLAN_object-oriented-3layer_20260721.md)

**워크오더 (WO1~21):**
- [WO1 환불서비스](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo1-refund-service_v1.md) · [WO2 감사훅](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo2-audit-hook_v1.md) · [WO3 크레딧원장](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo3-credit-ledger_v1.md) · [WO4 증빙서비스](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo4-invoice-service_v1.md) · [WO5 소프트삭제](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo5-soft-delete_v1.md)
- [WO6 고객360](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo6-customer360_v1.md) · [WO7 결제원장](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo7-payment-ledger_v1.md) · [WO8 알림디스패처](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo8-notify-dispatcher_v1.md) · [WO9 파일통합](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo9-files-unified_v1.md) · [WO9b 시설축](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo9b-factory-axis_v1.md)
- [WO10 연동헬스](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo10-integration-health_v1.md) · [WO11 통합검색](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo11-global-search_v1.md) · [WO12 자동화엔진](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo12-automation-engine_v1.md) · [WO13 관제홈](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo13-ops-home_v1.md) · [WO14 경영지표](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo14-stats-provider_v1.md)
- [WO15 세금계산서](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo15-tax-ops_v1.md) · [WO16 공지배너](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo16-notice-banner_v1.md) · [WO17 온보딩](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo17-onboarding_v1.md) · [WO19 어드민메뉴](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo19-admin-menu_v1.md) · [WO20 운영화면](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo20-ops-screens_v1.md) · [WO21 모바일](https://github.com/taiengineering/taieng/blob/main/docs/ops/tai-admin-ops/WORKORDER_wo21-mobile_v1.md)

**이 핸드오프 문서:**
- HANDOFF_session-20260729_v1 (본 문서, 같은 폴더)

---

## 10. 이번 세션 커밋 요약 (feat/admin-rebuild)

| 커밋 | 내용 |
|---|---|
| 4d19138 | hotfix: 무한로딩 원인 report-v1-legacy → report_v1 |
| c8fbce2 | fix(payment-ledger): usePaymentLedger 전역변수(payment_status) 조회 추가 |
| 37cc531 | fix(payment-ledger): index.vue 하드코딩 statusOptions 제거, init() 연결 |
| 70d54ae | fix(notice): useNotice 전역변수(notice_channel·banner_type) 조회 추가 |
| de3a873 | fix(notice): index.vue 하드코딩 CHANNELS·BANNER_TYPES 제거, init() 연결 |

**DB 변경 (vwlahtguyggrhvslabax):** system_codes에 notice_channel 2건 + banner_type 4건 INSERT.
