# TAI 회의실 메모리 — 2026-03-28

---

## 환경 정보
- API: api.taieng.co.kr (Railway)
- DB: Supabase (xntdkrjhgcscmqctdzyo)
- 프론트: taieng.co.kr (Cloudflare Pages)
- 최고관리자: hetto@kakao.com / 심태왕 / role_code: 001

---

## 오늘 완료된 작업

### 1. 홈페이지 모달 5카드 텍스트 수정 ✅
| 카드 | 수정 후 |
|------|----------|
| 🏢 건물·시설 | 소방·전기·설비 / 점검·선임·유지보수 |
| 🏾d 공장·산업현장 | 안전관리·중대재해방어 / 설비점검·선임 |
| 🛡️ 안전관리 전문가 | 기술자 및 대행업체 |
| 🔧 전문 설비 시공업체 | 전기·소방·설비 등 수선·시공·점검 |

### 2. 다음 2작업 Cursor 작업지시서 작성 ✅
- **파일:** `docs/TAI_Cursor_작업지시서_navbar_footer_개편.md` (tai-admin)
- Navbar 서비스 드롭다운 1열 나열
- 위험성진단·정밀안전점검 → TAI Care 하부
- 상단 메뉴: 서비스 + 안전정보 2개만 유지
- 우측 버튼: "서비스 신청" → "회원가입" / 로그인 후 유저명 + 마이페이지
- **대상 18개 HTML 파일 (survey 제외)**

### 3. 홈페이지 신뢰지표 바 슬롯머신 컨터 화 ✅
- DB 실제 수치 기반으로 교체
- **법령 415개** (28,663개 조문 포함)
- **공정 6,957개** (501개 업종 커버)
- **설비-공정 매핑 118만+건** (1,188,161건)
- **자동 점검 세트 67개**
- IntersectionObserver threshold 0 (품허우 수정), closeModal() 시 tryFireSlot() 호출

### 4. 신고서식 자동화 백엔드 완료 ✅
**타곳: PDF 다운로드까지 (기관 자동 제출 제외)**

#### DB (Supabase 직접 적재 완료)
| 테이블 | 상태 |
|--------|------|
| `legal_obligations` | ✅ 생성 + 11건 적재 |
| `obligation_form_mapping` | ✅ 생성 + 11건 적재 |
| `form_templates.form_json` | ✅ OSHACT-FORM-002 적재 |
| `form_templates` | 11개 서식, form_json 1개 완료 |

#### API 상태 (report_forms.py v2.0.2)
| 엔드포인트 | 상태 |
|-----------|------|
| `GET /report-forms/templates` | ✅ 200 |
| `GET /report-forms/obligations` | ✅ 200 |
| `POST /report-forms/submissions/preview-pdf` | ⚠️ **배포 진행 중** |

#### PDF 라이브러리 변경 이력
1. WeasyPrint → Railway `libgobject-2.0-0` 없음 → 실패
2. nixpacks.toml GTK 패키지 추가 → Nix 패키지명 불일치 → 실패
3. **xhtml2pdf (순수 Python, reportlab+html5lib)** → Railway pip install만으로 동작 → **v2.0.2 배포 중**

---

## 내일 진행할 작업 (우선순위)

### 🔴 긴급
1. **PDF 생성 확인** — v2.0.2 배포 완료 후 preview-pdf 테스트
   - Railway 버전 v2.0.1 → v2.0.2 전환 확인
   - OSHACT-FORM-002 샘플 데이터로 PDF blob 수신 확인
   - HTML 템플릿 파일이 Railway에 실제 존재하는지 확인 필요
     (`routers/templates/forms/OSHACT_FORM_002.html`)

2. **Cursor 작업 지시** — 18개 HTML navbar/footer 개편

### 🟡 이후
3. 나머지 서식 form_json 적재 (GPT 파싱 대기 중)
   - OSHACT-FORM-001, 003, 003-2, 004, 005, 030, 031
4. tadmin 서류작성 페이지 구현 (프론트)
5. 법령진단 루려 → report_events 자동 생성 연결

---

## 주요 이슈 현황

| 이슈 | 상태 |
|------|------|
| contracts 라우터 503 | 미해결 |
| 로그인 2.5초 지연 | 미해결 |
| 공정 4단계 셀렉트 | 다음 세션 |
| 법령판정 탭5 | 다음 세션 |

---

## 신고서식 자동화 전체 흐름 (목표)
```
법령진단 루려 발생
  ↓
legal_obligations + master_building_legal_rules 연결
  ↓
report_events 생성 (D-day 자동 계산)
  ↓
tadmin 대시보드 D-day 카드
  ↓
[서류 작성] 버튼
  ↓
HTML 입력폼 자동채움
  ↓
form_submissions 저장
  ↓
PDF 생성 (xhtml2pdf) ← 현재 여기
  ↓
다운로우 제공 ← 최종 목표
```

---

## 코드 파일 위치
- 프론트: `site/full-version/html/front-pages/index.html`
- 백엔드: `routers/report_forms.py v2.0.2` (xhtml2pdf)
- HTML 템플릿: `routers/templates/forms/OSHACT_FORM_002.html`
- Cursor 작업지시서: `docs/TAI_Cursor_작업지시서_navbar_footer_개편.md`
