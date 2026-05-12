# TAI 회의실 Memory — 2026-04-01

## 오늘 완료된 작업

### 프론트 (Cursor, 7b17a92)

| 파일 | 작업 |
|------|------|
| `diagnosis-step1.html` | Hero+스테퍼+섹터카드4개+입력폼(BUILDING/MFG/SPECIAL) 재작성 |
| `diagnosis-result.html` | 리스크카드+무료영역+블러잠금+결제유도 신규 |
| `diagnosis-step2.html` | 공정선택+잠금배너(SaaS불가명시) 신규 |
| `diagnosis-step3.html` | 설비등록+잠금배너 신규 |
| `construction-step1.html` | 녹색Hero+공사금액+실시간선임기준안내 신규 |
| `tbm-list.html` | 목록+등록사이드패널+녹음버튼(Web Speech API) 신규 |
| `safety-meeting-list.html` | 목록+등록모달+파일첨부+보존기한 D-day 신규 |
| `risk-assessment-list.html` | 목록+등록모달+빈도×강도자동계산+파일첨부 신규 |
| `education-list.html` | style 중복 제거 |
| `education-setting.html` | style 중복 제거 |
| `worker-list.html` | auth-guard, 행클릭 수정패널, bulk URL 정리 |
| `menu-tadmin.js` v2.3.0 | TBM/안전회의/위험성평가 메뉴 추가 |
| `diagnosis-purchase.html` | 단건 결제 페이지 신규 (섹터별 가격+POST /diagnosis/purchases) |

### 추가 확인사항
- 병합 충돌 발생 → 로컬(ours) 유지로 머지 완료
- construction-step1.html: GET/POST /construction/sites, POST /construction/engine/safety-manager 가정
- 목록 API 경로: LIST_PATH 변수로 추상화 (배포 경로 다르면 HTML 상단에서 수정)

## 미완료 (내일 우선)

### 🔴 백엔드 API 미구현
| API | 상태 |
|-----|------|
| POST/GET/PATCH /tbm | ❌ 미구현 |
| POST /tbm/transcribe (STT) | ❌ 미구현 |
| POST/GET/PATCH /safety-meetings | ❌ 미구현 |
| GET /safety-meetings/schedule | ❌ 미구현 |
| POST/GET/PATCH /risk-assessments | ❌ 미구현 |
| GET /risk-assessments/dashboard | ❌ 미구현 |
| GET /diagnosis/access-check | ❌ 미구현 |
| POST /diagnosis/purchases | ❌ 미구현 |

### 🟡 프론트 검증 필요
- 각 페이지 API 경로(LIST_PATH) 실제 배포 경로와 맞는지 확인
- diagnosis-step1.html Hero 디자인 실 화면 확인
- 법령진단 잠금 배너 동작 확인

## 내일 시작 프롬프트 (백엔드 창)
```
docs/TAI_Cursor_작업지시서_TBM_안전회의_위험성평가_20260331.md 읽고
아래 API 구현해줘:
1. POST/GET/PATCH /tbm + POST /tbm/transcribe
2. POST/GET/PATCH /safety-meetings + GET /safety-meetings/schedule
3. POST/GET/PATCH /risk-assessments + GET /risk-assessments/dashboard
4. GET /diagnosis/access-check?factory_id=&step=
   → diagnosis_purchases 단건 결제 기록만 확인 (SaaS 레벨 무시)
5. POST /diagnosis/purchases
Railway 배포 후 알려줘
```
