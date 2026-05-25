# 소비자 경험 QA + 수정 작업지시

> 작성일: 2026-05-25
> 목표: 소비자가 실제 사용할 때 에러/불편 없는지 확인 + 즉시 수정
> 원칙: 엔진 아키텍처 파일 절대 수정 금지

---

## 경로 1: 무료진단 (taieng.co.kr)

### 분석 대상 파일
- `nexas/free-diagnosis.html` (53KB) — 진단 입력 페이지
- `nexas/free-diagnosis-result.html` (39KB) — 결과 페이지
- `nexas/assets/js/tai-free-diagnosis.js` — API 허더
- `routers/anonymous_diagnosis.py` — 백엔드
- `routers/diagnosis_integrated.py` — 진단 실행

### 확인 순서

1. `free-diagnosis.html`에서 어떤 URL로 POST하는지 찾기
   - `TAI_API_BASE` + 어떤 path?
   - 요청 body 필드는?
   - 응답으로 무엇을 기대하는지?

2. 해당 API 엔드포인트가 실제로 존재하는지 확인
   - `router_registry/`에 등록되어 있는지
   - 라우터 파일의 prefix + path가 FE 호출과 일치하는지

3. 불일치 시 → 즉시 수정
   - FE가 호출하는 URL이 정확한지
   - BE에 해당 엔드포인트가 있는지
   - 없으면 추가 또는 FE URL 수정

4. `free-diagnosis-result.html`이 어떤 URL로 GET하는지
   - query param으로 token을 어떻게 읽는지
   - 해당 GET 엔드포인트 존재 여부
   - 응답 데이터를 FE가 어떻게 렌더링하는지

### 수정 원칙
- FE가 호출하는 URL이 정답 → BE를 맞춤
- BE가 정답인데 FE가 다르면 → FE를 수정 (nexas/ 파일)
- 양쪽 다 없으면 → 새로 구현

---

## 경로 2: 유료진단 (taieng.co.kr)

### 분석 대상
- `nexas/paid-diagnosis-result.html` (41KB)
- `routers/diagnosis_result_web.py` — `GET /diagnosis/paid-result/{token}`

### 확인
1. `paid-diagnosis-result.html`에서 토큰을 어떻게 읽는지 (URL param? hash?)
2. 어떤 GET URL을 호출하는지
3. 해당 엔드포인트의 응답 형식이 FE 기대값과 일치하는지
4. 토큰 파라미터 에러 원인 특정 + 수정

---

## 경로 3: SaaS 점검항목관리 (safe.taieng.co.kr)

### 분석 대상
- `tadmin/full-version/html/horizontal-menu-template/inspection-anchor.html`
- `routers/runtime_candidate_api.py` — `GET /runtime/candidates`

### 확인
1. `inspection-anchor.html`이 어떤 API를 호출하는지
2. 그 API가 `runtime_candidate` 테이블을 읽는지 또는 다른 테이블을 읽는지
3. 현재 `runtime_candidate`에 3건이 있으므로 표시되어야 함
4. 표시 안 되면 FE 호출 URL과 BE 엔드포인트 매칭 확인 + 수정

---

## 작업 방법

각 경로별로:
1. HTML 파일을 열고 API 호출 코드 찾기 (fetch/ajax/axios)
2. URL + method + body + 기대 응답 추출
3. 해당 BE 엔드포인트 존재 확인
4. 불일치 → 수정
5. 수정 후 로컬에서 `py_compile` 확인

### 보고 형식

각 경로별:
```
## 경로 N: [name]

### FE 호출
- URL: POST https://api.taieng.co.kr/xxx
- Body: {field1, field2, ...}
- 기대 응답: {token, result, ...}

### BE 상태
- 엔드포인트 존재: ✅/❌
- 응답 형식 일치: ✅/❌

### 문제
- [description]

### 수정
- [file]: [description]

### 결과
- ✅ 정상 / ❌ 미해결
```

## 배포

전체 수정 완료 후:
```bash
cd ~/tai-api
git add -A
git commit -m "fix: 소비자 경험 QA — 무료/유료진단 + 점검항목관리 에러 수정"
git push origin main
railway up
curl -X POST https://api.taieng.co.kr/cron/reload
```

taieng 레포 수정이 있으면:
```bash
cd ~/taieng
git add -A
git commit -m "fix: 무료/유료진단 FE API URL 수정"
git push origin main
```

## 주의
- engine/ 디렉토리 파일 절대 수정 금지
- diagnosis_transform.py 수정 금지 (import만 사용)
- 수정 전후 `/health` 200 유지
