# TAI 비즈니스 메모리 — 2026-03-29

---

## 오늘 확정된 사항

### 법령진단 서비스 3단계 재구성 확정
기존 건물 기반 단일 트랙 → **섹터별 완전 분리** 구조로 전환

**4개 섹터:**
- BUILDING (건물·시설): 연면적/용도/층수/수전용량
- MANUFACTURING (공장·제조업): KSIC업종/근로자수/위험물 → **KSIC가 핵심**
- CONSTRUCTION (건설현장): 공사금액/근로자수/공사종류 → **공사금액이 핵심**
- SPECIAL_FACILITY (특수시설): 병원/학교/복지시설 별도 기준

**3단계 과금 구조:**
- 1단계 (무료): 섹터 + 기초정보 → 주요 선임의무·법령 카테고리
- 2단계 (유료): 공정 선택 → 법령별 의무 + 신고일정
- 3단계 (유료): 설비 등록 → 법정검사 일정 + D-day

### 법령 수집 방식 확정
- **API + GPT 연계** 방식 (GPT 기억 기반 금지)
- KOSHA 법령 스마트검색 API → 원문 수집 → GPT 변환 → JSON
- 법제처 별표(별표3, 별표22 등) → GPT 변환
- 수집 후 master_building_legal_rules 배치 적재

### 신고서식 자동화 방향 확정
- **목표: PDF 다운로드까지** (기관 자동 제출 제외)
- xhtml2pdf 채택 (WeasyPrint Railway 불가)
- DB 완성: legal_obligations 11건 + obligation_form_mapping 11건
- OSHACT-FORM-002 form_json 완성

---

## 서비스 현황 (2026-03-29 기준)

### 홈페이지 (taieng.co.kr)
- 모달 5카드: 최종 텍스트 확정
- 슬롯머신 신뢰지표: 415개 법령 / 6,957개 공정 / 118만+ 설비 / 67개 점검
- Navbar/Footer 개편: Cursor 작업지시서 완성 (실행 대기)

### API (api.taieng.co.kr)
- report_forms.py v2.0.2 (xhtml2pdf 전환) 배포 진행 중
- /report-forms/templates → ✅ 200
- /report-forms/obligations → ✅ 200
- /report-forms/submissions/preview-pdf → ⏳ v2.0.2 배포 후 확인 필요

### DB 현황
| 테이블 | 건수 |
|--------|------|
| master_building_legal_rules | 396개 (모두 BUILDING 기반, 재구성 필요) |
| legal_obligations | 11건 |
| obligation_form_mapping | 11건 |
| form_templates | 11개 (form_json: FORM-002만 완성) |
| factories | 9개 |

---

## 비즈니스 현황

### 매출 파이프라인
- 크몽 survey.html: 17건 접수 확인 (2026-03-24 기준)
- 서비스 신청 → 수동 대응 단계
- 오프라인 서비스 우선, SaaS 플랫폼 준비 병행

### 자격증 취득 계획
- 현재 추진 중: 전기기사, 산업안전기사, 설비보전기사 (동시 3개)
- 시험: ~40일 (2026년 3월말 기준)
- 자격증 취득 후: 안전관리전문기관 지정 절차 추진

### 안전관리전문기관 지정 요건
- 필요 인원: 최소 3명 (산업안전지도사 1명 포함)
- 현재 보유: 미보유
- 해결 경로: 직접 취득(6~12개월) / 채용 / 기관 파트너십

---

## 중기 로드맵 (확정)

| 단계 | 내용 | 시점 |
|------|------|------|
| 즉시 | 1단계 법령진단 완성 + 홈페이지 개편 | 이번 주 |
| 단기 | GPT 법령 수집 → DB 적재 → 섹터별 룰 완성 | 2주 내 |
| 중기 | 2·3단계 유료 기능 출시 | 자격증 취득 후 |
| 중기 | 안전관리전문기관 지정 추진 | 자격증 취득 후 |
| 장기 | SaaS 플랫폼 확장 + 인력 확충 | Phase 2 |

---

## 내일 진행할 핵심 작업

1. **백엔드 창** — PDF v2.0.2 확인 + DB 컬럼 추가 (sector, diagnosis_stage)
2. **백엔드 창** — 기존 396개 룰 BUILDING/stage1 마이그레이션
3. **GPT 창** — 소방/전기 1단계 룰 수집 시작 (건물 섹터부터)
4. **Cursor** — Navbar/Footer 18개 파일 개편

---

## 환경 정보
- API: api.taieng.co.kr (Railway)
- DB: Supabase (xntdkrjhgcscmqctdzyo)
- GitHub: taiengineering/tai-admin (프론트), taiengineering/tai-api (백엔드)
- 최고관리자: hetto@kakao.com / role_code: 001
- JUSO_API_KEY: U01TX0FVVEgyMDI2MDMxODEyMjUxNjExNzc1MTc=
- Resend: noreply@taieng.co.kr 발신
