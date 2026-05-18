# Runtime Cockpit 구현 리포트

**일자**: 2026-05-19

## 구현 화면

1. **Summary Cards** — 전체/overdue/점검/허가/문서미완/증빙미완 6종
2. **Task List** — 상태배지 + 우선순위 + completeness bar + overdue 표시
3. **Filter Bar** — 전체/overdue/점검/허가/보고/교육/선임/준수확인
4. **Task Detail Panel** — 클릭 시 상세 정보 + 문서/증빙 completeness
5. **Activity Timeline** — 최근 8건 이벤트 (생성/overdue)
6. **Notification Ready** — overdue task에 알림 예정 배지

## 사용 API

- `GET /runtime/cockpit/tasks?tenant_id=...`

## 파일 위치

`tadmin/full-version/html/horizontal-menu-template/runtime-cockpit.html`

## Cursor 작업지시서

1. 다운로드된 `runtime-cockpit.html`을 tai-admin의 위 경로에 배치
2. Vuexy navbar/sidebar 통합 (기존 페이지 참조)
3. Mock 데이터 제거 후 실제 API 연결 테스트
