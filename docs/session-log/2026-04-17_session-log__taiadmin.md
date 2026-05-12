# 2026-04-17 작업 세션 로그

## 저장소별 커밋 내역

---

### tai-admin (safe.taieng.co.kr) — main 브랜치

#### FN-07: 점검 미이행 대시보드 (BE-10 완료 후 착수)

| 파일 | 유형 | 내용 |
|------|------|------|
| `tadmin/full-version/html/horizontal-menu-template/safety-dashboard.html` | 수정 (이전 세션) | 미이행 위젯 내장: GET /overdue/summary + /overdue/history TOP3 + [독촉] 버튼 + 과태료 추정(건당 3,000,000원 상수) |
| `tadmin/full-version/assets/js/tai/menu-tadmin.js` | 수정 v5.2.0 (이전 세션) | 위험관리 하위 '미이행 관리' 메뉴 추가 → overdue-list.html |
| `tadmin/full-version/html/horizontal-menu-template/overdue-list.html` | **신규** | 미이행 상세 페이지: 필터바(기간/레벨/해소여부) + 테이블(select-all/No./작업자/점검내용/기한/경과일/레벨/상태/액션) + [독촉][재배정][해소] 모달 + 일괄해소 + 법적리스크 카드(산안법 §36/§93/§167, 중대재해법 §6) + 과태료 추정 |
| `tadmin/full-version/app/index.html` | 수정 | 작업자 홈 미이행 배너: GET /work-assignments?overdue_only=true + OVERDUE/PENDING 기한초과 필터 + "지금 하기 →" 링크 |
| `tadmin/full-version/html/horizontal-menu-template/factory-list.html` | 수정 | 시설 상세옵션 탭에 `notification_time` (현장별 알림 시간) `<input type="time">` 추가 + collectFactoryBody() 수집 |

#### FN-06: 법령진단 결과 렌더러 (BE-08 Transform API 기반)

| 파일 | 유형 | 내용 |
|------|------|------|
| `tadmin/full-version/html/horizontal-menu-template/diagnosis-result-v2.html` | **신규** | GET /diagnosis/transform/{id} 단일 호출 기반 65/35 레이아웃. severity 배지(CRITICAL pulse 애니메이션) + 5탭(선임/점검/신고/교육/서류) + evidence 접힘 + ROI 카드(가격 하드코딩 0건) + 스케줄 히트맵 + SaaS CTA + schema_version 불일치 배너 + 스켈레톤 로딩 + @media print |
| `docs/workorder-FN06-summary.md` | **신규** | FN-06 요약 워크오더 |

#### FN-03: 법령진단 입력 폼 UX 전면 개편

| 파일 | 유형 | 내용 |
|------|------|------|
| `assets/js/diagnosis-inputs/tri-state-toggle.js` | **신규** | 예/아니오/모름 3지선다. TriStateToggle.initAll() 지원 |
| `assets/js/diagnosis-inputs/process-table.js` | **신규** | 공정 목록 테이블. mode='basic'\|'worker' |
| `assets/js/diagnosis-inputs/subcontractor-table.js` | **신규** | 하도급 업체 테이블 |
| `assets/js/diagnosis-inputs/multi-select-group.js` | **신규** | 그룹화 체크박스+접힘. 카운트 배지 |
| `assets/js/diagnosis-inputs/autofill-address.js` | **신규** | juso.go.kr 주소검색 + /diagnosis/autofill/address 건축물대장 자동채움 |
| `assets/js/diagnosis-inputs/autofill-biz.js` | **신규** | 사업자번호 자동하이픈 + /diagnosis/autofill/biz 공공데이터 자동채움 |
| `diagnosis-input-building.html` | **신규** | BUILDING 36필드 중 25개 TriState 변환 / 5그룹 접힘 |
| `diagnosis-input-construction.html` | **신규** | CONSTRUCTION ProcessTable + SubcontractorTable + 위험시설9종 |
| `diagnosis-input-industry-paid1.html` | **신규** | INDUSTRY PAID1 operation_shift 필수 + 위험물 9종 MultiSelect |
| `diagnosis-input-industry-paid2.html` | **신규** | INDUSTRY PAID2 process_worker_data → ProcessTable(mode=worker) |
| `diagnosis-input-industry-paid3.html` | **신규** | INDUSTRY PAID3 설비 10종 MultiSelect |
| `diagnosis-fill-gaps.html` | **신규** | PAID_PENDING_INPUT 전용 '모름' 보완 UX. PATCH /fill-gaps |

#### FN-01: pricing.html v4 (taiengineering/taieng main)

| 파일 | 유형 | 내용 |
|------|------|------|
| `nexas/pricing.html` | 수정 v4 | 3섹터 서브탭(건물/산업/건설) + API 기반 가격 + 포함건수/초과건수 표시(크레딧 미노출) + KG이니시스 연동 + SaaS 도입 문의 모달 |

---

### tai-api (api.taieng.co.kr) — dev 브랜치

#### BE-08: Transform 레이어

| 파일 | 유형 | 내용 |
|------|------|------|
| `routers/diagnosis_transform.py` | **신규** v1.0.0 | result_data JSONB 읽기 전용 Transform. 폴백 체인: headline/severity/obligations/warnings/exposure/inspection_schedule |
| `docs/workorder-BE08-result-transform.md` | **신규** | BE-08 워크오더 |
| `docs/workorder-FN06-result-renderer.md` | **신규** | FN-06 상세 워크오더 |
| `main.py` | 확인 (이미 v5.27.0) | diagnosis_transform_router 등록 완료 |

---

### Supabase DB

| Migration | 내용 |
|-----------|------|
| `be08_diagnosis_transform_columns` | `factory_diagnosis_results`: expires_at(timestamptz), refund_at(timestamptz), refund_reason(text) / `master_building_legal_rules`: is_retroactive(boolean DEFAULT false) |
| `factories.notification_time` 확인 | 이미 존재 (time without time zone, DEFAULT '07:00:00') — UI만 추가 |

---

## 핵심 기술 결정 사항

### FN-07 설계
- 과태료 상수: `PENALTY_PER_ITEM = 3_000_000` (건당 300만원, 하드코딩 아님)
- 워크오더 API: GET /overdue/summary + /overdue/history + POST /overdue/resolve/{id}
- 독촉: POST /overdue/urge/{id} (별도 엔드포인트)
- 재배정: PATCH /overdue/reassign/{id}
- 작업자 홈 배너: OVERDUE 상태 OR (PENDING AND scheduled_date < today) 필터

### FN-06 설계
- Transform API 단일 호출 — 엔진 API 직접 호출 0건
- schema_version != v2026.04 시 DANGER 배너 + 렌더링 계속 (중단 아님)
- ROI 수치: API 응답값만 (하드코딩 0건)

### notification_time
- DB: factories.notification_time (time without time zone, DEFAULT '07:00:00')
- UI: `<input type="time">` — DB 반환값 'HH:MM:SS' → 'HH:MM' substring 변환
- 저장: PATCH /factories/{id} body.notification_time

---

## PENDING (다음 세션)

- [ ] **FN-05** 착수 — BE-06 완료, v2026.04 스키마 기준 리포트 렌더러
- [ ] **FN-04** 착수 — BE-07 완료, ROI 대시보드
- [ ] overdue API `/overdue/urge/{id}` BE 구현 확인 (FN-07 독촉 버튼 연동)
- [ ] overdue API `/overdue/reassign/{id}` BE 구현 확인
- [ ] KG이니시스 MID 실값 교체 + INIStdPay.pay() 주석 해제
- [ ] SB-06: /precedents/collect 1회 수동 실행 (산재판례 0건)
- [ ] FN-03 모바일 375px 실제 기기 검증
- [ ] FN-07 overdue-list.html 모바일 반응형 검증
