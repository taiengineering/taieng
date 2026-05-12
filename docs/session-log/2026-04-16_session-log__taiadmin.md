# 2026-04-16 작업 세션 로그 (최종)

## 저장소별 커밋 내역

---

### tai-admin (safe.taieng.co.kr)

#### 버그 수정

| 파일 | 내용 |
|------|------|
| `tadmin/full-version/_redirects` | SPA fallback 200 규칙 제거 — 건설 페이지 index.html 덮어쓰기 버그 수정 |
| `construction-work-list.html` | BUG-A: `is_high_risk`→`special_work_type` / BUG-B: `ptw_reject_reason`→`notes` / 위험작업 드롭다운 6종 |
| `construction-worker-list.html` | BUG-B: `phone`→`worker_phone` / BUG-C: IN/OUT 2버튼→IN/OUT/OFFSITE 3버튼 |

#### FN-03 법령진단 입력 폼 UX 전면 개편 (BE-05 완료 후 착수 → 완료)

**공통 컴포넌트 6종** (`tadmin/full-version/assets/js/diagnosis-inputs/`)

| 파일 | 설명 |
|------|------|
| `tri-state-toggle.js` | 예/아니오/모름 3지선다. `TriStateToggle.initAll()` 일괄 초기화 지원 |
| `process-table.js` | 공정 목록 테이블. `mode='basic'\|'worker'` (worker: 직영/하도급/교대 컬럼) |
| `subcontractor-table.js` | 하도급 업체 테이블. company/공종/인원/안전관리자 여부 |
| `multi-select-group.js` | 그룹화 체크박스+접힘. 카운트 배지 |
| `autofill-address.js` | juso.go.kr 주소팝업 + `/diagnosis/autofill/address` 건축물대장 자동채움 |
| `autofill-biz.js` | 사업자번호 자동하이픈 + `/diagnosis/autofill/biz` 공공데이터 자동채움 |

**HTML 입력화면 6종** (`tadmin/full-version/html/horizontal-menu-template/`)

| 파일 | 주요 변경 |
|------|-----------|
| `diagnosis-input-building.html` | 36개 필드 중 25개 TriState 변환 / 5그룹 접힘(소방/위험물/수질/다중이용/특수) / AutofillAddress+Biz |
| `diagnosis-input-construction.html` | ProcessTable + SubcontractorTable + 위험시설9종 그룹 + operation_shift |
| `diagnosis-input-industry-paid1.html` | operation_shift 필수 / 위험물 9종 MultiSelectGroup / 안전·전기·환경 그룹 |
| `diagnosis-input-industry-paid2.html` | process_worker_data → ProcessTable(mode=worker) + SubcontractorTable |
| `diagnosis-input-industry-paid3.html` | 설비 10종 MultiSelectGroup + TriState 5종 + 수치 입력 |
| `diagnosis-fill-gaps.html` | PAID_PENDING_INPUT 전용 / '모름' 항목 목록 로드 / TriState로 보완 입력 / PATCH /fill-gaps |

#### 문서

| 파일 | 내용 |
|------|------|
| `docs/workorder-fn03-input-ux.md` | FN-03 단독 워크오더 |
| `docs/workorder-frontend-20260416.md` | FN-03/04/05 통합 작업지시서 |
| `docs/session-log-20260416.md` | 본 파일 |

---

### taieng (new.taieng.co.kr)

| 파일 | 내용 |
|------|------|
| `nexas/pricing.html` | FN-02 v3: 법령진단 4종 카드 직노출 / 특수시설 3종 확장 / DB 가격 정규화 |
| `nexas/index.html` | 히어로 이메일 인풋 제거 → 버튼 단독 / 멘트: "우리도 법령위반 아닌지 확인하기 →" |
| `nexas/assets/css/tai-main.css` | 버튼 수직 정렬 전역 픽스: inline-block → inline-flex + align-items:center |

---

### tai-api (api.taieng.co.kr)

| 파일 | 내용 |
|------|------|
| `docs/workorder-be01-legal-engine-source.md` | 법령엔진 역추적: master_building_legal_rules 단독 소스 확정 |

---

### Supabase DB

| 작업 | 내용 |
|------|------|
| `deprecate_master_legal_condition_tables_2026_04_16` | DEPRECATED 테이블 코멘트 migration |

---

## 핵심 기술 결정 사항

### 버그 수정
1. **_redirects** — SPA fallback 200 규칙 전체 제거
2. **건설 스키마 3건** — is_high_risk/phone/IN-OUT 실제 DB 컬럼에 맞게 정정
3. **버튼 수직 정렬** — Noto Sans KR 디센더 문제. inline-flex 전역 교체

### FN-03 설계 결정
- TriStateToggle: `true | false | null` 3값. hidden input으로 form 직렬화
- ProcessTable: mode 파라미터로 basic/worker 분기. hazardOptions 주입 가능
- AutofillAddress: juso.go.kr 팝업 방식 (카카오 금지). 건축물대장 자동채움은 `onFill` 콜백
- MultiSelectGroup: 15개↑ 체크박스 접힘 강제. 카운트 배지 실시간 업데이트
- fill-gaps: `/diagnosis/{id}/fill-gaps` PATCH API로 선택 업데이트 전송

### BE-01 분석
- `master_legal_requirement_conditions` / `master_legal_inspection_rules` → DEPRECATED (0건, 미참조)
- 실제 법령 엔진 소스: `master_building_legal_rules` (2,287건)

---

## 완료 조건 달성 현황 (FN-03)

| 조건 | 결과 |
|------|------|
| 체크박스 연속 15개↑ 화면 0개 | ✅ 전 화면 그룹 접힘 처리 |
| 자유텍스트 필드 0개 (주소·회사명 제외) | ✅ |
| 주소 자동채움 | ✅ juso.go.kr + /autofill/address |
| 사업자번호 자동채움 | ✅ /autofill/biz |
| operation_shift 라디오 전 sector | ✅ BUILDING/CONSTRUCTION/INDUSTRY 모두 |
| '모름' 결제 후 보완 동선 | ✅ fill-gaps.html + PAID_PENDING_INPUT |
| 카카오 API 금지 | ✅ juso.go.kr + MessageMi 사용 |

---

## PENDING (다음 세션)

- [ ] **FN-05** 착수 — BE-06 완료, v2026.04 스키마 기준 리포트 렌더러
- [ ] **FN-04** 착수 — BE-07 완료, ROI 대시보드 PDF
- [ ] E2E 건설 6페이지 플로우 최종 검증
- [ ] KG이니시스 MID 실값 교체 + INIStdPay.pay() 주석 해제
- [ ] SB-06: /precedents/collect 1회 수동 실행 (산재판례 0건)
- [ ] FN-03 모바일 375px 실제 기기 검증
