# TAI Safe 작업지시서 — 2026-04-01

> 백엔드 API 전체 완료 (TBM·안전회의·위험성평가·법령진단 접근체크)  
> 내일은 **프론트 전용** 작업입니다.  
> 모든 작업: **Cursor (프론트 창)**

---

## ✅ 백엔드 완료 목록 (확인 불필요)

```
POST/GET/PATCH  /tbm
POST            /tbm/transcribe (STT)
POST            /tbm/{id}/complete
POST/GET/PATCH  /safety-meetings
GET             /safety-meetings/schedule
POST/GET/PATCH  /risk-assessments
GET             /risk-assessments/dashboard
GET             /diagnosis/access-check?factory_id=&step=
```

---

## 🔴 Priority 1 — 법령진단 전면 재설계 (5개 파일)

**참고: `docs/TAI_Cursor_작업지시서_법령진단_프론트_반응형_20260331.md`**

### 신규/재작성 파일

| 파일 | 작업 | 핵심 내용 |
|------|------|----------|
| `diagnosis-step1.html` | **전면 재작성** | Hero헤더+스테퍼+섹터카드4개+입력폼 |
| `diagnosis-result.html` | **신규** | 리스크카드+무료영역+블러잠금+결제유도 |
| `diagnosis-step2.html` | **신규** | 공정선택+잠금배너(SaaS구독불가명시) |
| `diagnosis-step3.html` | **신규** | 설비등록+잠금배너 |
| `construction-step1.html` | **신규** | 녹색Hero+공사금액+실시간선임기준안내 |

### 디자인 필수 요소
```
diagnosis-hero: 그라디언트 헤더 (짙은파랑 → 하늘색)
섹터카드: min-height 140px, 호버효과, 2열 반응형
스테퍼: 1단계(무료) · 2단계(🔒) · 3단계(🔒)
max-width: 860px (웹) + 모바일 완전 반응형
auth-guard.js HEAD 삽입 필수
```

### 잠금 배너 핵심 문구
```
🔒 유료 서비스입니다
법령진단은 SaaS 구독과 별도로 과금됩니다.
[단건 구매하기]
※ STARTER/BUSINESS/ENTERPRISE 구독으로는 해제되지 않습니다.
```

### 블러 처리 (diagnosis-result.html)
```javascript
// 무료 공개: 선임의무 여부, 법령 카테고리 뱃지
// 블러 처리: 과태료금액·법령명·의무항목수
// 접근체크: GET /diagnosis/access-check?factory_id=&step=2
const SECTOR_PRICES = {
  BUILDING:         { s2: 29000, s3: 59000,  report: 99000  },
  MANUFACTURING:    { s2: 49000, s3: 99000,  report: 249000 },
  SPECIAL_FACILITY: { s2: 49000, s3: 99000,  report: 199000 },
  CONSTRUCTION:     { s2: 79000, s3: 149000, report: 399000 },
};
```

### construction-step1.html 특이사항
```javascript
// 공사금액 입력 시 실시간 선임 기준 안내
// 건축: 150억 이상 → 안전관리자 선임 의무
// 토목: 120억 이상 → 안전관리자 선임 의무
// 하도급 근로자 포함 안내 (산안법 시행령 제16조③)
```

---

## 🔴 Priority 2 — TBM·안전회의·위험성평가 (3개 파일)

**참고: `docs/TAI_Cursor_작업지시서_TBM_안전회의_위험성평가_20260331.md`**

| 파일 | 핵심 기능 |
|------|----------|
| `tbm-list.html` | 목록+등록 사이드패널+🎙️녹음버튼(Web Speech API)+참석자 |
| `safety-meeting-list.html` | 목록+등록 모달+파일첨부+보존기한 D-day |
| `risk-assessment-list.html` | 목록+등록 모달+빈도×강도 자동계산+파일첨부 |

### TBM 녹음 버튼 (핵심 차별점)
```javascript
// Web Speech API (브라우저 내장, 비용 0원)
const recognition = new (window.SpeechRecognition
  || window.webkitSpeechRecognition)();
recognition.lang = 'ko-KR';
recognition.continuous = true;
recognition.interimResults = true;
// 녹음 중 실시간 텍스트 표시
// 완료 시 transcript_text 필드에 저장
// POST /tbm/transcribe 로 서버 저장
```

### 위험성 자동 계산
```javascript
// 빈도(1-4) × 강도(1-4) = 위험성 점수
// 4이하  → 허용가능  (green badge)
// 5~9   → 개선필요  (yellow badge)
// 10이상 → 즉시개선  (red badge)
```

### 안전회의 보존 기한 D-day 표시
```javascript
// 3년 보존 의무
// 등록일 + 3년 = 보존 만료일
// D-day 경고: 만료 90일 전부터 표시
```

---

## 🟡 Priority 3 — 교육 발령·이수 관리 (2개 파일)

**참고: `docs/TAI_Cursor_작업지시서_교육발령_이수관리_20260331.md`**

| 파일 | 핵심 기능 |
|------|----------|
| `education-list.html` | 요약카드4개+목록+발령모달+이수 사이드패널 |
| `education-setting.html` | 교육마스터 목록+회사별 링크 설정 모달 |

### 요약 카드 (education-list.html)
```javascript
// GET /education/assignments/summary?factory_id=
// 전체 N건 / 완료 N건(%) / 대기 N건 / 초과 N건
```

### 교육 링크 우선순위
```javascript
// 1순위: company_education_setting.custom_url (회사 직접 설정)
// 2순위: education_master.source_url (KOSHA 기본값)
// 이수증 업로드: 카메라 직접 촬영 or 파일 업로드
```

---

## 🟡 Priority 4 — 작업자 등록 보완

**참고: `docs/TAI_Cursor_작업지시서_작업자등록_20260331.md`**

`worker-list.html` 기존 파일 확인 후 미완성 부분 보완:
```
□ 수동 등록 사이드패널 (이름+연락처+직종 필수)
□ 파일 업로드 모달 (SheetJS 파싱 + 미리보기)
□ 엑셀 템플릿 다운로드 버튼
□ 앱 초대 버튼 (개별/일괄)
```

---

## menu-tadmin.js 메뉴 추가

```javascript
// 아래 3개 메뉴 추가 (TBM·안전회의·위험성평가)
{ label: 'TBM 관리',      href: 'tbm-list.html' }
{ label: '안전보건 회의', href: 'safety-meeting-list.html' }
{ label: '위험성평가',    href: 'risk-assessment-list.html' }
```

---

## 📋 전체 체크리스트

```
프론트 (Cursor)
□ diagnosis-step1.html 전면 재작성
□ diagnosis-result.html 신규 (블러+잠금배너)
□ diagnosis-step2.html 신규 (공정선택+잠금배너)
□ diagnosis-step3.html 신규 (설비등록+잠금배너)
□ construction-step1.html 신규 (건설전용)
□ tbm-list.html 신규 (녹음 기능)
□ safety-meeting-list.html 신규
□ risk-assessment-list.html 신규
□ education-list.html 신규
□ education-setting.html 신규
□ worker-list.html 미완성 보완
□ menu-tadmin.js 메뉴 3개 추가
□ GitHub push
```

---

## ⚠️ 핵심 주의사항

```
1. 법령진단 잠금
   SaaS 구독(STARTER/BUSINESS/ENTERPRISE) → 해제 안 됨
   diagnosis_purchases 단건 결제 기록만 확인

2. TBM 녹음
   Web Speech API (브라우저 내장, 비용 0원)
   Chrome/Edge 지원, Safari 제한적

3. 위험성평가
   현재: 문서 업로드 + 기본 입력만
   AI 자동생성: 추후 TAI CARE 서비스로 별도 제공

4. my-company.html
   수정 금지 (전체 필드 유지)

5. factory_id
   반드시 UUID 형식 사용
   localStorage에서 current_factory_id 로드
```

---

## 🔑 테스트 계정 / 환경

```
테스트 계정: safety-mgr@korean-safe.co.kr / tai1234!
factory UUID: 9ec1ac44-3a80-486c-9aff-eebcc74d9ee3 (1호 테스트공장)
API: https://api.taieng.co.kr (v4.8.0+)
tadmin: https://tadmin.taieng.co.kr
```
