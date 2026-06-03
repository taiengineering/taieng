# [Cursor 작업지시] 도입문의 링크 오배선 수정: fix-request.html → contact.html (2026-06-03)

## 배경 / 문제
- `contact.html` = 일반 **문의하기 페이지**(문의 폼, 분야 버튼에 "TAI Safe 도입"/"법령진단 문의" 포함). 쿼리 파라미터 안 읽음.
- `fix-request.html` = **전문가/업체 매칭 채팅**(수선·선임·컨설팅 연결, 3턴 무료→가입). `<title>전문가 매칭 | TAI Fix</title>`.
- 사이트 여러 곳의 **"도입 문의 / 상담 / 문의"** 버튼이 잘못해서 `fix-request.html?...type=general`(매칭 챗)으로 연결돼 있음. → **`contact.html`** 로 가야 함.

## 작업 범위
- 대상: `nexas/` 전체 — `*.html`, `service/*.html`, `assets/js/*.js`(header.js, footer.js, tai-pricing-config.js 포함).
- `nexas/` 바깥(다른 repo)·DB·결제 함수 로직은 건드리지 않는다.

## 규칙 (occurrence별 판단)
`fix-request.html` 링크/리다이렉트를 전부 찾은 뒤, **버튼의 보이는 텍스트·맥락**으로 분류:

### A. contact.html 로 변경 (도입/상담/문의 의도)
버튼/링크 텍스트가 다음에 해당하면 목적지를 `contact.html`(파라미터 제거)로 변경:
- "도입 문의", "도입 문의하기", "도입 문의 · 특전 상담", "구독 문의", "상담", "문의하기", "도입 상담" 등 영업/도입/문의 성격
- 경로 주의: 루트 페이지 → `contact.html`, `service/` 하위 페이지 → `../contact.html`
- `?from=...&type=general` 등 쿼리스트링은 **삭제**(contact.html은 파라미터를 사용하지 않음)
- 예) `href="fix-request.html?from=pricing&type=general"` → `href="contact.html"`
- 예) `../fix-request.html?from=saas&type=general` (config CUSTOM "도입 문의") → `../contact.html`

### B. 그대로 유지 (수선·매칭·연결 의도)
다음은 **변경 금지**(fix-request.html이 정상 목적지):
- "전문가 매칭", "수선 요청", "업체 연결", "매칭 시작", "보수 요청" 등
- `type=repair`, `type=appointment`, `type=consulting`
- `connect.html`, `for-repair.html` 등 연결/수선 페이지의 매칭 CTA

### C. 보류 (확인 필요 — 변경하지 말고 보고만)
- `pricing.html`의 결제 리다이렉트 `proceedDiagPayment()` → `fix-request.html?...&goods=...&amount=...` : 이건 "도입문의"가 아니라 결제 임시 흐름이므로 **이번엔 건드리지 말고**, 발견 위치만 보고하라.
- 헤더/푸터(header.js/footer.js) 내 네비 항목이 fix-request로 가는 경우: 텍스트가 "문의"면 A에 해당하나, 애매하면 보고만.

## 완료 기준
1. A 규칙에 해당하는 모든 도입/상담/문의 버튼이 `contact.html`(또는 `../contact.html`)로 변경됨.
2. B(수선·매칭)는 그대로.
3. 변경된 파일 목록 + 각 파일의 before→after(라인) 보고.
4. C 항목(결제 리다이렉트, 헤더/푸터 애매 케이스) 위치 목록 별도 보고.
5. `git grep -n "fix-request" nexas/` 결과를 변경 전/후로 첨부.

불확실하면 멈추고 질문하라. (특히 A/B 판단이 애매한 occurrence는 변경하지 말고 보고)
