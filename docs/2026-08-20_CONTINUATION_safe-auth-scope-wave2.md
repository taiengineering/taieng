# CONTINUATION — safe auth·scope (Wave 2 진행중 · 직접MCP 전환)

> 2026-08-20 기획창. 앞선 핸드오프: `2026-08-20_HANDOFF_safe-auth-scope-wave1-done.md`. 설계: `2026-08-20_safe-auth-scope-module-design.md`. 이 문서 = Wave 2 중간 스냅샷.

## 작업 방식 변경 (중요)
- **Cursor 미사용. 직접 MCP로 작업**(운영자 지시 — Cursor 결과가 일률적이지 않음).
- 절차: fresh `get_file_contents` → 전체 파일 재작성(`create_or_update_file`, sha 필수) → **배포 SUCCESS로 무결성 확인**(대형 파일 재현 오류·구문/import 파손 감지) → 비로그인 401 블랙박스는 운영자 확인.
- **주의**: 대형 파일(20KB+)을 컨텍스트가 꽉 찬 상태에서 재작성하면 출력 truncation → 잘린 파일 push → /health 503. **여유 있을 때 큰 파일부터.**

## 완료 (tai-api main, 배포 SUCCESS)
```
ef547c8  company_scope 헬퍼 2개 가산
7c61574  companies 인증·스코프
6d5a89a5 미출시 9개 라우터 격리
03e1350  documents 인증·스코프
f3ea782  safety_meetings 인증·스코프 (Cursor)
9189875  work_schedules 인증·스코프 (Cursor)
326fc5e  risk_assessments 인증·스코프 (직접MCP) — SUCCESS 확인
4f01094  ra_items 인증·스코프 (직접MCP) — BUILDING(배포 확인 필요)
```

## Wave 2 진행: 4/6 (+ra_items)
- ✅ safety_meetings · work_schedules · risk_assessments · ra_items
- ⬜ **ra_report** (다음) · **ra_settings** · **overdue_checker** · **tbm**(서명 3엔드포인트 공개 예외 — 라우터 단위 게이트 금지)

## 스코프 패턴 (확립)
- 생성: `require_company_id(current, sb)` 토큰강제(ALL은 body 폴백: `_forced or body.company_id`)
- 목록: `scoped_list_company(current, sb, company_id)` → deny면 빈결과, 아니면 `company_id = scoped_cid`
- 단건: 행 조회 → `_ensure_own_company(row.company_id, current, sb, msg)` (변경·삭제 前 선행)
- **자식(부모 경유)**: ra_items 패턴 — `_ensure_assessment_own`/`_ensure_item_own`/`_ensure_control_own` 체인. ra_report·ra_settings도 동일(부모 risk_assessments.company_id 경유).
- 배치 id목록: `_owned_ids(sb, ids, current)` 로 타사 skip (work_schedules 참조)
- 시설 경유: `_ensure_factory_own(sb, factory_id, current)`
- `_is_uuid` 가드·업무로직 불변, 공개 엔드포인트 없으면 전 엔드포인트 로그인.

## Wave 3~4 잔여 (미착수)
- Wave 3: inspection_checklist·inspection_sets·inspection_setup · equipment_assets·equipment_checkins · corrective_actions · subcontractors · construction_workflow_router · safety_template · tbm_templates
- Wave 4: org (부서→팀→그룹 부모체인)

## 격리 잔여 (미출시)
- `connect_provider`(TAI Fix 공급자가격) — 등록위치 미확인 → 찾아 격리
- `connect_registration`(사전등록 리드폼) — 유지/격리 **제품결정 대기**
- `fix_chat` — TAI Fix 상담 추정, 미독 → 확인 후 격리

## 다음 액션 (새 창)
ra_items 배포 SUCCESS 확인 → `ra_report` fresh 읽기 → 부모경유 소유확인 배선 → 직접 MCP 재작성 → 배포 검증. 이어서 ra_settings · overdue_checker · tbm.
