# DECISION — 단일섹터 확정 · 섹터를 백엔드 스코프에 병합하지 않음

> 2026-08-20, 기획창. 관련 설계: `2026-08-20_safe-auth-scope-module-design.md`.

## 결정
1. **회사 = 단일섹터** (다중섹터 미허용). 운영자 확정.
2. 따라서 **company_id 스코프 하나로 "산업/건설 안 섞임"이 자동 달성**된다(자기 회사만 → 그 회사는 한 섹터). 섹터를 백엔드 보안 스코프에 **병합하지 않는다**.
3. 섹터의 화면 분리는 **기존 프론트 메뉴 게이트로 유지**한다.

## 근거 (실측)
- `users.sector` ↔ `factories.sector` 어휘 정합(BUILDING/INDUSTRIAL/CONSTRUCTION/SPECIAL_FACILITY). `companies.business_sector`는 대소문자·업종어휘·null(67) 범벅 → 섹터 분리에 부적합.
- 섹터 게이팅 실체 = `tai-admin vue3/src/navigation/gate.ts` `filterNavByContract()`:
  - `localStorage.contract_sector`(계약 섹터) 기준으로 **사이드바 메뉴만 필터**. 데이터 접근 미제어.
  - 실패-오픈(섹터 미확정·role 001/002 → 전체 노출). 어휘 정규화(INDUSTRY→INDUSTRIAL, BUILDING→FACILITY).
- 병합 시 위험: 5중 어휘 서버 등호 비교(취약) + 다중섹터 데이터 은닉 + 프론트 게이트 중복. 단일섹터면 애초에 불필요.

## 보안 스코프와 독립된 후속 (지금 안 함 — 인지·기록)
1. **단일섹터 강제 지점 부재**: `companies.business_sector`가 자유입력이라 "1회사=1섹터"가 등록 플로우에서 강제되지 않음. 등록/계약 시 섹터 고정·검증하는 별도 작업 필요.
2. **오염 데이터**: 다중섹터 회사 **105/178개** 실재(시드/테스트 가능성). 실데이터면 런칭 전 정리 대상. 되돌릴 수 없는 정리라 **원문 대조 후 별도 실행**.

## 진행 상태 (auth·scope 롤아웃)
- [x] 헬퍼 2개 가산 — `require_company_id`·`scoped_list_company` (company_scope.py, commit `ef547c8`, GET검증)
- [ ] Wave 1: companies · personnel · documents
- [ ] Wave 2: tbm · safety_meetings · risk_assessments(+ra_*) · work_schedules · overdue_checker
- [ ] Wave 3: inspection_* · equipment_* · corrective_actions · subcontractors · construction_workflow · templates
- [ ] Wave 4: org
