# TAI Admin 오픈 기준 진척도 분석

> 작성일: 2026-04-02  
> 기준: admin.taieng.co.kr (총관리자 Admin)

---

## 전체 진척도 요약

| 오픈 기준 | 진척도 | 예상 소요 |
|---------|--------|----------|
| 총관리자 내부 운영 (대표님 단독) | **70~75%** | 1~2주 |
| 법령엔진 핵심 기능 오픈 | **55~60%** | 2~3주 |
| 외부 고객 (안전관리자) 공개 오픈 | **35~40%** | 4~6주 |

---

## 메뉴별 상세 현황

### ✅ 완료 (파일 존재)

| 메뉴 | 파일명 | API 연동 | 비고 |
|------|--------|---------|------|
| 로그인 | auth-login-cover.html | ✅ | 실제 연동 완료 |
| 회원가입 | auth-register.html | ✅ | 이메일 인증 |
| 회원관리 | member-list.html | ✅ | |
| 회사관리 | company-list.html | ✅ | JUSO 연동 |
| 시설관리 | factory-list.html | ✅ | JUSO + 건축물대장 |
| 알림설정 | notification-setting.html | 🟡 Mock일부 | |
| 계약관리 | contract-list.html | 🔴 503오류 | |
| 견적관리 | quote-list.html | ✅ | 17건 접수 확인 |
| 문의관리 | inquiry-list.html | ✅ | |
| 권한관리 | permission.html | 🔴 API미연동 | 파일만 있음 |
| 교육설정 | education-setting.html | 🔴 API미연동 | 파일만 있음 |
| 교육관리 | education-list.html | 🔴 API미연동 | 파일만 있음 |
| 설비관리 | equipment-list.html | 🟡 | |
| 수선관리 | repair-list.html | 🟡 | |
| 전역변수 | system-codes.html | 🔴 CRUD미완성 | 읽기만 됨 |
| 엔진설정>설비 | engine-equipment.html | ✅ | |
| 엔진설정>법규 | engine-legal.html | ✅ | |
| 엔진설정>모델 | engine-model.html | ✅ | |
| 가격설정 | price-setting.html | ✅ | 백엔드 연동 완료 |
| 공정관리 | facility-process.html | 🟡 불완전 | |

---

### 🔴 없거나 미완성 (파일 없음)

| 메뉴 | 파일명 | 상태 |
|------|--------|------|
| **대시보드** | index.html (껍데기) | 통계·차트 없음 |
| 위험관리 > 사고관리 | ❌ | 미구현 |
| 위험관리 > 법위반관리 | ❌ | 미구현 |
| 위험관리 > 위험관리 | ❌ | 미구현 |
| 위험관리 > 미교육관리 | ❌ | 미구현 |
| 위험관리 > 위험성평가 | ❌ | 미구현 |
| TBM관리 | ❌ | 미구현 |
| 수선관리 > 정산관리 | ❌ | 미구현 |
| 문서관리 > 신고관리 | ❌ | 미구현 |
| 문서관리 > 제출문서관리 | ❌ | 미구현 |
| 엔진설정 > 문서 | ❌ | 오늘 기획 완료 |
| 설정 > 문서(doc-setting) | doc-setting.html (껍데기) | 내용 없음 |
| 협력사관리 | ❌ | 미구현 |

---

## 오픈 불가 핵심 이유 3가지

```
1. 대시보드 미완성
   → 로그인 후 첫 화면 = 빈 화면
   → 서비스 신뢰도의 첫인상
   → 최우선 해결 필요

2. API 연동 구멍
   → 권한관리: 파일 있지만 API 미연동
   → 교육관리: 파일 있지만 API 미연동
   → system-codes CRUD: 읽기만 됨, 쓰기 안 됨
   → /contracts: 503 오류

3. 핵심 운영 메뉴 미구현
   → 위험관리 5개 페이지 없음
   → TBM관리 없음
   → 문서관리 2개 없음
   → 이것들이 SaaS 핵심 기능
```

---

## 즉시 해결 우선순위

| 순위 | 작업 | 담당 | 이유 |
|------|------|------|------|
| 🔴 1 | 대시보드 콘텐츠 (index.html) | 프론트 | 로그인 후 첫 화면 |
| 🔴 2 | /contracts 503 오류 수정 | 백엔드 | 계약관리 전체 먹통 |
| 🔴 3 | system-codes POST/PATCH/DELETE | 백엔드 | 엔진 데이터 관리 불가 |
| 🟡 4 | 권한관리 API 연동 | 프론트 | 파일 있음, API만 연결 |
| 🟡 5 | 교육관리 API 연동 | 프론트 | 파일 있음, API만 연결 |
| 🟢 6 | 위험관리 5개 페이지 | 프론트 | 오픈 후 점진적 추가 가능 |
| 🟢 7 | 엔진설정 > 문서 메뉴 | 프론트+백엔드 | 오늘 기획+작업지시서 완료 |

---

## 법령엔진 현황 (별도)

```
법령엔진 자체는 별도 평가:
  master_building_legal_rules: 921건
  의무유형: ACTION/INSPECT/REPORT/NOTIFY/APPOINT/DOCUMENT
  DOCUMENT 의무 52건 오늘 수집 완료
  API 정상 작동: /legal-engine/diagnose/step1~3

부족한 것:
  건설 섹터 알고리즘 (구조적 차이로 별도 구현 필요)
  form_code 매핑 (80건 미매핑)
  12개 법령 추가 수집 (data.go.kr API 활용)
  document_form_master 테이블 (오늘 기획 완료)
```

---

## 오늘(2026-04-02) 새로 추가된 것

```
비즈니스 창 완료:
  DOCUMENT 의무 52건 DB 수집 완료
  엔진설정 > 문서 메뉴 기획서
  프론트엔드 작업지시서 (engine-document.html)
  백엔드 작업지시서 (engine_document.py)
  과금구조 기획서 v1.0
  브랜드 네이밍 전략 (TAI Safe 확정)
  법령진단 회원가입 전환전략 기획서
  TAI 비즈니스 메모리 20260402
```
