# 세션 로그 2026-05-26 (후반)

> 시간: 05-26 13:00 ~ 22:00 KST
> 범위: SaaS 소비자 오픈 점검 + 법령 상태 마크 시스템

---

## 완료 작업

### 시설 폼 (factory-list.html)
- 롤백 `42d4359e` 후 Cursor 재작업
- 탭 4개 → 2개 (기본정보/담당자)
- 상세옵션 탭 삭제 → 기본정보 하단에 섹터별 필드 통합
- 법령진단 탭 삭제
- 상태 필드 disabled (표시 전용)
- 담당자 탭: 구분 선택 + 등록폼 + 하단 리스트 + 수정
- 등록설비/설비목록보기 삭제
- KSIC 필드 복원 (Claude Code) — 공정관리 의존성
- 목록 컨럼: 업종 → 시설유형

### 회사정보 (my-company.html)
- 단일 편집 → 목록+사이드패널 구조로 전환
- BE `created_by` 필터 추가 (GET /companies)
- FE `created_by` 파라미터 전달

### BE 라우터 등록
- `factory_process_v3` → inspection 그룹 등록 (공정관리 404 해결)
- `legal_status_api` v1.0.0 생성 + 등록
  - GET /legal-status/summary
  - GET /legal-status/pending
  - POST /legal-status/factories/{id}/mark-applied
  - POST /legal-status/factories/{id}/mark-needs-update
  - POST /legal-status/batch-apply

### 법령 적용 상태 마크 시스템
- 설계 문서: `docs/2026-05-26_legal_status_system.md`
- DB 마이그레이션 완료:
  - `factories.legal_status` (NOT_APPLIED/NEEDS_UPDATE/APPLIED)
  - `factories.legal_applied_at`
  - `factory_process.legal_status` (NOT_MAPPED/MAPPED)
  - `equipment_assets.legal_status` (NOT_MAPPED/MAPPED)
  - 인덱스 3개

### 버그 수정
- `my-equipment.html` JS SyntaxError: `(isReg?' already:''` → `(isReg?' already':''` 따옴표 수정
- `equipment_assets.py` `/summary` 엔드포인트 추가 (/{asset_id} 라우트 순서 버그)
- Railway 배포: `railway up` CLI Dockerfile 인식 실패 → GitHub auto-deploy로 전환

---

## 미해결 이슈

### 🔴 P0: inspection_sets 500 에러
- `GET /inspection-sets?factory_id=...` → 500 Internal Server Error
- 원인: `services/inspection_sets_svc/` 패키지가 로컬에 없음
- GitHub에는 존재 — `git reset --hard origin/main`으로 동기화 필요
- **상태: 로컬 동기화 대기 중**

### 🟡 P1: 법령 상태 마크 FE 구현
- factory-list.html에 법령마크 배지 + 전체법령적용 버튼
- 작업지시: `tai-api/docs/2026-05-26_cursor_legal_status_ui.md`
- **상태: Claude Code/Cursor 작업 대기**

### 🟡 P1: equipment_assets /summary 배포
- Claude Code로 로컬 수정 완료
- **상태: 커밋+푸시+배포 대기**

### 🟡 P2: 회사정보 created_by 백필
- 128개 회사 중 12개만 created_by 설정, 116개 NULL (synthetic)
- 새로 등록하는 회사는 정상 동작 (스키마에 created_by 추가됨)

---

## Railway 배포 교훈

- `railway up` CLI: Dockerfile 인식 실패 (로컬 업로드 문제) → **사용 금지**
- `railway redeploy`: 이전 실패 배포 재시도 → **사용 금지**
- **정상 방법**: GitHub auto-deploy (빈 커밋 푸시)
  ```
  git commit --allow-empty -m "deploy: description" && git push origin main
  ```
- MCP로 커밋하면 GitHub auto-deploy 자동 트리거
- 배포 확인: `curl https://api.taieng.co.kr/` 로 모듈 수 확인

---

## Cursor/AI 도구 교훈

- Cursor가 탭 삭제 등 과잘 수정 → **"변경하지 않는 것" 명시 필수**
- KSIC 제거 후 공정관리 동작 안 함 → **의존성 확인 후 삭제**
- Claude Code: 대형 파일 수술적 수정에 적합 (KSIC 복원, summary 추가)
- 롤백 시점 확인 후 작업 지시 (참조 커밋 명시)

---

## 문서 커밋 이력

| 파일 | 위치 |
|------|------|
| 법령 적용 상태 설계 | `taieng/docs/2026-05-26_legal_status_system.md` |
| 시설폼 v3 작업지시 | `taieng/docs/2026-05-26_cursor_factory_form_v3.md` |
| KSIC 복원 작업지시 | `taieng/docs/2026-05-26_cursor_factory_ksic_restore.md` |
| 법령마크 FE 작업지시 | `tai-api/docs/2026-05-26_cursor_legal_status_ui.md` |
