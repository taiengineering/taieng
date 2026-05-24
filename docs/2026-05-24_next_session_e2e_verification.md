# 다음 세션 작업지시 — 고객 시나리오 E2E 오픈 검증

**작성일:** 2026-05-24
**목적:** 기술 디버깅이 아니라 실제 오픈 가능 여부 판단

---

## 현재까지 확인된 사항

- 문서 시스템 (Gotenberg, Storage, document_svc, documents schema): **정상**
- register_generated() 와이어링: **4개 파일 완료** (main 반영)
- 진단 PDF runtime: **실증 완료** (HTTP 302)
- TBM route loaded=6/7: **runtime investigation 수준** (deploy logs 시작 부분 확인 필요)

---

## Priority 1 — 고객 시나리오 E2E

### 시나리오 A: 신규 고객
1. 회원가입
2. 로그인
3. 회사 생성
4. 현장 생성
5. 작업자 등록
6. 점검표 실행
7. PDF 다운로드
8. 로그아웃 → 재로그인 → 데이터 유지 확인

### 시나리오 B: 유료 전환
1. 무료체험 시작
2. 플랜 선택
3. 결제 (KG이니시스)
4. subscription 생성
5. 플랜 적용 + 기능 제한 반영
6. 관리자 화면 반영

---

## Priority 2 — 모바일 + 관리자

### 모바일 검증
- 버튼 크기, 한손 사용, 입력 단계, PDF 다운로드, 스크롤, 속도

### 관리자 운영
- 사용자/결제/구독 조회, 문의 대응, 로그 확인

---

## TBM route 처리 (시작 시 1분)

1. Railway Deploy Logs 시작 부분 확인
2. `[document_engine] FAILED` 여부 확인
3. import error 특정
4. 최소 수정만

**금지:** route 구조 재설계, registry 리팩토링, engine 수정

---

## 판단 기준

"실제 고객이 가입하고 돈 내고 사용할 수 있는가"
