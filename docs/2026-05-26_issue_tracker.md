# TAI Safe 이슈 트래커 — 2026-05-26 업데이트

> 이전 세션(05-25) 이슈 + 금일(05-26) 발생/해결 이슈 통합

---

## 해결된 이슈

| # | 이슈 | 해결 | 세션 |
|---|--------|------|------|
| 1 | 메뉴에 미서비스 항목 7개 노출 | menu-tadmin.js v6.0.0 삭제 | 05-26 |
| 2 | 문서관리+문서 메뉴 분리 | 문서관리에 서식작성 통합 | 05-26 |
| 3 | construction-work-list 산업 미노출 | 점검관리 sub에 작업관리 추가 | 05-26 |
| 4 | 건설 점검관리 건설관리에 묻힘 | construction-inspection 분리 | 05-26 |
| 5 | 하도급관리 페이지 없음 | DB+BE+FE 전체 신규 생성 | 05-26 |
| 6 | 결제 후 계약 수동 생성 필요 | payment_post_process 자동화 | 05-26 |
| 7 | 결제 완료 알림 없음 | SMS(compat_send_sms) + 인앱 | 05-26 |
| 8 | 온보딩 가이드 없음 | onboarding API + checklist.js | 05-26 |
| 9 | 시설유형 드롭다운 비어있음 | FE 수정 + RLS (05-25) | 05-25 |
| 10 | KSIC 검색 빈 결과 | BE 엔드포인트 + RLS (05-25) | 05-25 |
| 11 | GoTrue 로그인 실패 | auth.users NULL 필드 수정 (05-25) | 05-25 |
| 12 | 메뉴 잠김 (applyMenuLock) | v5.8.0 비활성화 (05-25) | 05-25 |
| 13 | plan-gate 기능 잠금 | v2.0.0 GATE_CONFIG 비움 (05-25) | 05-25 |
| 14 | RLS 근본 문제 (anon 키) | service_role 전환 (05-25) | 05-25 |
| 15 | KSIC 코드 형식 불일치 | C2591 수정 (05-25) | 05-25 |

---

## 미해결 이슈

### P0 — 즉시
| # | 이슈 | 설명 | 담당 |
|---|--------|------|------|
| 16 | summary 113건 vs obligation_counts 15건 | runtime 진단 결과 정합성 불일치 | Claude |
| 17 | Email 발송 유틸 미구현 | payment_post_process에서 TODO | Cursor |
| 18 | SaaS 테스트 결제 E2E 미검증 | contracts 생성 + SMS 확인 필요 | 수동 |
| 19 | PR #87 정리 | dev→main PR, main 직접 커밋으로 대체 — 닫기 필요 | GitHub |

### P1
| # | 이슈 | 설명 |
|---|--------|------|
| 20 | Railway↔GitHub 자동배포 미복구 | railway up 수동 배포 중 |
| 21 | worker-list 로딩 이슈 | 작업근로자 페이지 데이터 미표시 |
| 22 | 모바일 UX 미검증 | 전체 페이지 모바일 대응 |
| 23 | dev 브랜치 diverge | dev↔main 동기화 필요 |
| 24 | notification_queue 테이블 유무 | 인앱 알림 INSERT 시 경고 가능 |
| 25 | auth.users NULL 필드 (saas-test 외) | 나머지 계정 정리 |
| 26 | FREE_MENU connect-service 판단 | 무료 메뉴에서 전문가매칭 유지/제거 결정 |

### P2
| # | 이슈 | 설명 |
|---|--------|------|
| 27 | BE 대형 라우터 서비스 분리 | legal_engine 77KB, construction 58KB, payment 52KB |
| 28 | report_forms/contract_kmong Gotenberg 전환 | xhtml2pdf → Gotenberg |
| 29 | 위험성평가/QR 오픈 | 전문성 검토 후 |
| 30 | 전문가 매칭 오픈 | 모수 확보 후 |
| 31 | runtime_notification_queue 400 에러 | 스키마/쿼리 문제 |
| 32 | KOSHA API APICODE_ERROR 90 | data.go.kr 포털 활성화 필요 |
