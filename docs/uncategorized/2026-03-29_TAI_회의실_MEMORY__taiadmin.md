# TAI 회의실 메모리 — 2026-03-29

---

## 환경 정보
- API: api.taieng.co.kr (Railway)
- DB: Supabase (xntdkrjhgcscmqctdzyo)
- 프론트: taieng.co.kr (Cloudflare Pages)
- 최고관리자: hetto@kakao.com / 심태왕

---

## 오늘 완료된 작업

### 1. 홈페이지 모달 최종 수정 ✅
- 건물·시설: 소방·전기·설비 / 점검·선임·유지보수
- 공장·산업현장: 안전관리·중대재해방어 / 설비점검·선임
- 안전관리 전문가: 기술자 및 대행업체
- 전문 설비 시공업체: 전기·소방·설비 등 수선·시공·점검

### 2. 슬롯머신 신뢰지표 바 ✅
- threshold 0 (1px만 보여도 트리거)
- closeModal() 시 tryFireSlot() 호출
- 실제 DB 수치: 법령 415개 / 공정 6,957개 / 설비 118만+ / 점검 67개

### 3. Cursor 작업지시서 완성 ✅
- 파일: docs/TAI_Cursor_작업지시서_navbar_footer_개편.md
- 18개 HTML 파일 navbar/footer 개편
- 서비스 드롭다운 1열, 위험성진단·정밀안전점검 → TAI Care 하위
- 상단: 서비스+안전정보만 / 우측: 로그인+회원가입 / 로그인후 유저명

### 4. 신고서식 자동화 백엔드 ✅
- legal_obligations 테이블: 생성 + 11건
- obligation_form_mapping 테이블: 생성 + 11건
- OSHACT-FORM-002 form_json 적재 완료
- report_forms.py v2.0.2: WeasyPrint → xhtml2pdf 전환

### 5. 법령진단 3단계 재구성 기획 완료 ✅
- 섹터 4개 분리: BUILDING / MANUFACTURING / CONSTRUCTION / SPECIAL_FACILITY
- 단계별 과금 구조 확정
- GPT 수집 프롬프트 (API 원문 기반) 작성
- 프론트엔드 + 백엔드 기획서 docx 생성

---

## 핵심 결정사항

### 법령진단 재구성
- 기존: 건물 기반 단일 트랙 (문제)
- 신규: 섹터 선택 → 섹터별 완전히 다른 입력폼 → 3단계
- 건설업 핵심 변수: **공사금액** (근로자수가 아님)
- 제조업 핵심 변수: **KSIC 업종코드**

### 법령 수집 방식
- GPT 단독(기억) → ❌ 사용 금지
- API 원문 수집 → GPT 변환 → ✅ 확정
- 사용 API: KOSHA 법령스마트검색 + 법제처 + 소방청 국가위험물

### PDF 라이브러리
- WeasyPrint → Railway libgobject-2.0-0 오류 → 실패
- **xhtml2pdf (순수 Python)** → v2.0.2 배포 중

---

## 내일 우선 작업

| 순서 | 작업 | 창 |
|------|------|----|
| 1 | PDF v2.0.2 배포 확인 + preview-pdf 테스트 | 백엔드 창 |
| 2 | DB 컬럼 추가 (sector / diagnosis_stage 등) | 백엔드 창 |
| 3 | 기존 396개 룰 sector=BUILDING 업데이트 | 백엔드 창 |
| 4 | Cursor navbar/footer 개편 18개 파일 | Cursor |
| 5 | GPT 법령 수집 시작 (건물 소방룰부터) | GPT 창 |

---

## 파일 현황
- `docs/TAI_GPT_수집프롬프트_법령진단_3단계.md`
- `docs/TAI_법령진단_3단계_기획서.md`
- `docs/TAI_Cursor_작업지시서_navbar_footer_개편.md`
- `docs/TAI_Backend_작업지시서_신고서식_PDF자동화.md` (tai-api)
