# TAI Safe SaaS 세션 기록 — 2026-05-26

> 세션 범위: 메뉴 개편 + 하도급관리 + 온보딩 + 결제→계약 자동화
> 배포: tai-api `3d851e9` Railway Online / tai-admin Cloudflare Pages

---

## 1. 완료 작업

### 1.1 메뉴 v6.0.0 개편
- `menu-tadmin.js` v5.8.0 → v6.0.0
- **삭제 7개**: safety-dashboard, safety-info, risk, qr-rfid, connect-service, operational-awareness, document-forms-menu
- **문서관리**: 아이콘 `tabler-file-text`, sub에 서식작성 통합 (기존 별도 메뉴 흡수)
- **점검관리(산업/건물)**: 작업관리(construction-work-list.html) sub 추가, NEW 배지 제거
- **건설관리**: 현장/공정/작업만 유지 (점검 관련 분리)
- **건설 점검관리**: `construction-inspection` 신규 메뉴 (점검항목/점검목록/업무일정)
- **작업근로자**: 산업·건설 분기 + 건설 하도급관리 추가
- FREE_MENU_DEFS 변경 없음 (connect-service 유지)
- tadmin/ ↔ site/ 동기화 확인 (SHA 동일 `0f9166c`)
- 커밋: tai-admin `b79fadc9` (Cursor)

### 1.2 하도급관리 신규 생성 (DB + BE + FE)

**DB:**
- `subcontractors` 테이블 생성 (23 컬럼)
- `construction_workers.subcontractor_id` FK 제약 추가
- RLS: service_role 전체접근 + authenticated CRUD + anon SELECT
- 마이그레이션: `create_subcontractors_table`

**BE:**
- `routers/subcontractors.py` v1.0.0
- 5개 엔드포인트: GET list, GET detail, POST, PUT, DELETE
- 하도급업체별 실제 소속 작업자 수(actual_worker_count) 조회
- soft delete (is_active=False, status=TERMINATED) + 소속 작업자 연결 해제
- `router_registry/construction.py`에 등록
- 커밋: tai-api `682cfda` (main 직접)

**FE:**
- `subcontract-management.html` 신규 페이지
- 현장 선택 → 하도급업체 목록 (체크박스+No. 컬럼 컨벤션)
- 업체 추가/수정 모달 (12개 필드)
- SweetAlert 해지 확인
- tadmin/ + site/ 동기화
- 커밋: tai-admin `7fc2c13`

### 1.3 대시보드 온보딩 체크리스트

**BE:**
- `routers/onboarding.py` — `GET /onboarding/status`
- 산업 5단계: 시설 → 공정 → 설비 → 점검항목 → 점검발행
- 건물 4단계: 시설 → 설비 → 점검항목 → 점검발행
- 건설 5단계: 공사장 → 공정 → 작업 → 점검항목 → 점검발행
- 각 단계 done/count + 전체 완료 여부 반환
- `router_registry/saas_core.py`에 등록
- 커밋: tai-api `51c39d8`

**FE:**
- `onboarding-checklist.js` v1.0.0 — 자동 렌더링 컴포넌트
- 프로그레스 바 + 단계별 체크/링크
- 미완료 → 해당 페이지 직접 링크, 완료 → 체크 아이콘 + 건수
- 전체 완료 시 닫기 (localStorage)
- `index.html`에 div + script 2줄 추가 (Cursor)
- 커밋: tai-admin `a474f8d`

### 1.4 결제→계약→알림 자동화
- `services/payment_post_process.py` 신규
- `on_payment_success` / `on_payment_success_sync`
- 결제 SUCCESS/PAID 시: contracts INSERT → payments.contract_id 연결 → 기존 ACTIVE 계약 EXPIRED
- SMS: `compat_send_sms` (MessageMi 경유), Email: TODO 로그, 인앱: notification_queue INSERT
- 멱등성: contract_id 있으면 스킵 → 기존 ACTIVE 갱신
- Hook 3곳: 카드승인(payment_svc.py), VBANK입금, 수동확인(payment_ops.py)
- payment.py 본문 주석 1줄만 추가
- 커밋: tai-api `3d851e9` (Cursor)

---

## 2. 파일 변경 전체

### tai-api (main)
| 커밋 | 파일 | 설명 |
|--------|------|------|
| 682cfda | routers/subcontractors.py | 하도급 CRUD v1.0.0 |
| 682cfda | router_registry/construction.py | subcontractors 등록 |
| 51c39d8 | routers/onboarding.py | 온보딩 상태 API |
| 51c39d8 | router_registry/saas_core.py | onboarding 등록 |
| 3d851e9 | services/payment_post_process.py | 결제 후처리 서비스 |
| 3d851e9 | services/payment_svc.py | process_card_success hook |
| 3d851e9 | routers/payment_ops.py | manual_confirm hook |
| 3d851e9 | routers/payment.py | 주석 1줄 |

### tai-admin (main)
| 커밋 | 파일 | 설명 |
|--------|------|------|
| b79fadc | tadmin/.../menu-tadmin.js | v6.0.0 |
| b79fadc | site/.../menu-tadmin.js | v6.0.0 동기화 |
| 7fc2c13 | tadmin/.../subcontract-management.html | 하도급관리 페이지 |
| 7fc2c13 | site/.../subcontract-management.html | 동기화 |
| a474f8d | tadmin/.../onboarding-checklist.js | 온보딩 컴포넌트 |
| a474f8d | site/.../onboarding-checklist.js | 동기화 |
| Cursor | tadmin/.../index.html | 온보딩 div+script 추가 |

### taieng (main)
| 커밋 | 파일 | 설명 |
|--------|------|------|
| 858a2b7 | docs/2026-05-26_payment_contract_flow.md | 결제→계약 작업지시 |

### Supabase Migrations
| 마이그레이션 | 설명 |
|--------------|------|
| create_subcontractors_table | 하도급업체 테이블 + FK + RLS |

---

## 3. 프로덕션 상태

| 항목 | 값 |
|------|-----|
| API version | 6.0.1 |
| tai-api main | `3d851e9` |
| tai-admin main | `a474f8d` + Cursor index.html |
| Railway | Online, /health 200 |
| 스케줄러 | /cron/reload 완료 |
| SUPABASE_KEY | service_role |
| menu-tadmin | v6.0.0 |
| plan-gate | v2.0.0 (기능잠금 없음) |
| 배포 방식 | railway up (자동배포 미복구) |

---

## 4. 다음 세션 우선순위

### P0
| # | 이슈 | 설명 |
|---|--------|------|
| 1 | summary 113건 vs obligation_counts 15건 불일치 | runtime 진단 결과 정합성 |
| 2 | Email 발송 유틸 구현 | payment_post_process에서 TODO |
| 3 | SaaS 테스트 결제 E2E 검증 | contracts 생성 + SMS 수신 확인 |
| 4 | PR #87 닫기 | dev→main PR, main 직접 커밋으로 대체됨 |

### P1
| # | 이슈 | 설명 |
|---|--------|------|
| 5 | Railway↔GitHub 자동배포 복구 | 현재 railway up 수동 |
| 6 | worker-list 로딩 이슈 | 작업근로자 페이지 데이터 미표시 |
| 7 | 모바일 UX 검증 | 전체 페이지 모바일 대응 |
| 8 | dev 브랜치 main 동기화 | dev가 main과 diverge 상태 |
| 9 | notification_queue 테이블 유무 확인 | 인앱 알림 INSERT 시 경고만 발생할 수 있음 |

### P2
| # | 이슈 | 설명 |
|---|--------|------|
| 10 | BE 라우터 서비스 레이어 분리 | legal_engine 77KB, construction 58KB, payment 52KB |
| 11 | report_forms.py, contract_kmong.py Gotenberg 마이그레이션 | xhtml2pdf → Gotenberg |
| 12 | 위험성평가/QR 오픈 준비 | 전문성 검토 후 |
| 13 | 전문가 매칭 오픈 준비 | 모수 확보 후 |
