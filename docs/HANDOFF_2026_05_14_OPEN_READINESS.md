# TAI Safe 오픈 준비 — 세션 핸드오프 (2026-05-14)

## 세션 성과 요약

이 세션에서 **P0 12개 중 10개 완료**. 모든 0건 핵심 테이블에 실데이터 생성 확인.

### 완료된 E2E 플로우

| 플로우 | 이전 | 현재 | 상태 |
|--------|------|------|------|
| 진단→SaaS Setup→Register | 0건 | session 1 / candidate 50 / reg 1 | ✅ |
| 스케줄 생성→점검 시작→결과 기록→완료→자동생성 | 0건 | schedule 59 / inspection 1 / results 3 | ✅ |
| 증빙 업로드→검증→검토 승인 | verification 0건 | verification 1 / review +1 | ✅ |
| 문서 생성→PDF 출력 | generated_doc 0건 | generated_doc 1 (GENERATED) | ✅ |
| 결제 페이지 접근 | - | pricing 200, billing/pay 200 | ✅ |
| 이니시스 승인 | 대기 | 완료 | ✅ |
| 익명 무료진단 | 500 에러 | GPT 수정 완료 | ✅ |

### 코드 변경사항

1. **services/profile_matcher.py** (신규) — 30개 precompiled factory 대상 deterministic 매칭
2. **services/diagnosis_service.py** (수정) — ProfileMatcher 연결 + TYPE_MAP 수정 (compiler task_types)
3. **DB: diagnosis_session** — match_info 컬럼 추가, UNSUPPORTED_SECTOR 상태 추가
4. **DB: safety_inspections** — FK를 work_assignments→work_schedules로 변경
5. **DB: get_precompiled_factory_ids()** — RPC 함수 생성

### 발견된 버그 및 수정

- TYPE_MAP이 compiler의 `_TASK_CANDIDATE` 접미사를 처리 못함 → 수정 완료
- profile_matcher가 limit(1000)으로 distinct factory_id 못 가져옴 → RPC 함수로 해결
- safety_inspections FK가 미사용 work_assignments를 참조 → work_schedules로 변경
- anonymous_diagnosis.py의 supabase 변수 미정의 → GPT에서 수정 완료

---

## 남은 작업 (Claude 영역)

### P0 (1건)
- **SAAS-01**: 회원가입→사업장등록→구독 프론트 E2E — API는 동작, 프론트 플로우 검증 필요
  - subscriptions 25건 중 active 0건 (전부 PENDING) — 결제 콜백 후 활성화 로직 확인 필요

### P1 (9건)
- **WORKER-01**: worker_registry 0건 — 작업자 등록/초대 플로우 구현
- **WORKER-02**: 작업자 모바일 점검입력 UX (3~5초)
- **MKT-01**: 22개 모듈 카탈로그 팩트체크 (inapp.html, 20KB+, Cursor 작업)
- **MKT-02**: 필터 탭 JS + 카드 클릭 모달 (Cursor 작업)
- **MKT-03**: 도메인 전환 new.taieng.co.kr → taieng.co.kr (Cloudflare DNS)
- **ADM-01**: 어드민 대시보드 핵심 지표 (가입/매출/점검률)
- **ADM-02**: 고객사/결제/구독 관리 화면 검증
- **DIAG-02**: 진단 결과 PDF 리포트 E2E (Gotenberg)
- **DIAG-03**: 무료진단→유료전환→가입 플로우

### P2 (4건)
- **WORKER-03**: 작업자 홈 대시보드
- **ADM-03**: 리스트 페이지 컨벤션 (전체선택+순번) 일괄 적용
- **DOC-03**: 프론트엔드 서식 작성/미리보기/다운로드 UI
- **SAAS-04**: TBM 플로우 검증 (tbm_meetings 1건)

---

## GPT 영역 (Claude 절대 금지)

- Admin Review Queue 229건 법령 판단
- token_family_registry 확장 (UNKNOWN 78%→40%)
- Document Requirement/Schema 철학 결정
- Runtime Compiler (방향 B, 후속)

---

## MVP 서식 10개 (DOC-01 선정 완료)

1. 안전보건관리체계 구축계획서 (id: 65e92560)
2. 안전관리자선임보고서 (id: 74cf8ca2)
3. 위험성평가 실시결과서 (id: 6a78a819)
4. 작업환경측정결과서
5. 특수건강진단결과서
6. 산업재해발생보고서
7. 작업허가서(위험작업)
8. 위험성평가 개선조치계획서
9. 안전점검 종합보고서
10. 물질안전보건자료 교육기록

---

## 다음 세션 시작 프롬프트

```
이전 세션에서 P0 E2E 10개 완료.
남은 작업: SAAS-01(구독 활성화), WORKER-01~02(작업자), MKT-01~03(마케팅사이트), ADM-01~02(어드민), DIAG-02~03(진단 PDF/전환).
docs/HANDOFF_2026_05_14_OPEN_READINESS.md 참조.
```
