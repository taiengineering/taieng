# 전체 사이트 CTA 버튼 → fix-request 채팅 링크 변경 작업지시서

## 개요

사이트 전체에서 선임·수선·컨설팅 관련 "이용문의", "문의하기", "알아보기" 등의 버튼 링크를
**모두 `/nexas/fix-request.html`로 통일**합니다.

대화형 매칭 시스템으로 전환되었으므로, 별도 문의 폼이나 외부 링크가 아닌
fix-request 채팅 페이지로 이동해야 합니다.

## 변경 규칙

### 링크 형식

```
/nexas/fix-request.html?from={컨텍스트}&type={서비스유형}
```

| 파라미터 | 설명 | 예시 값 |
|---------|------|--------|
| from | 어디서 왔는지 | diagnosis, saas, pricing, nav, landing |
| type | 어떤 서비스 문의인지 | appointment (선임), repair (수선), consulting (컨설팅), general (일반) |

예시:
- 선임 연결 버튼 → `/nexas/fix-request.html?from=landing&type=appointment`
- 수선 요청 버튼 → `/nexas/fix-request.html?from=diagnosis&type=repair`
- 컨설팅 문의 버튼 → `/nexas/fix-request.html?from=saas&type=consulting`
- 일반 문의/도입문의 → `/nexas/fix-request.html?from=nav&type=general`

## 변경 대상 페이지 (전체 스캔 필요)

아래는 예상 대상입니다. **실제 작업 시 nexas/ 폴더 전체를 grep으로 스캔**하여 누락 없이 처리해주세요.

### 1. 공통 네비게이션 (nav-auth.js 또는 각 페이지 nav)

- "도입 문의" 버튼 → `?from=nav&type=general`
- "이용 문의" 링크 → `?from=nav&type=general`
- 서비스 드롭다운 내 "선임 연결" → `?from=nav&type=appointment`
- 서비스 드롭다운 내 "수선 연결" → `?from=nav&type=repair`
- 서비스 드롭다운 내 "컨설팅" → `?from=nav&type=consulting`

### 2. free-diagnosis.html (법령진단 랜딩)

- "경영자 가이드 보기" → 그대로 유지 (가이드 페이지)
- "안전관리 대행 알아보기" → `?from=diagnosis&type=consulting`
- "전문가 등록 알아보기" → 별도 페이지 유지 (전문가용)
- "안전관리자 가이드 보기" → 그대로 유지
- 결과 페이지 내 "유료 진단" CTA → 그대로 유지 (결제 플로우)
- 결과 페이지 내 "전문가 상담" 또는 "수선 요청" 버튼 → `?from=diagnosis-result&type=repair`

### 3. service/saas.html (SaaS 페이지)

- "도입 문의" 또는 "상담 신청" 버튼 → `?from=saas&type=general`

### 4. 가격/요금제 페이지

- "문의하기" 버튼 → `?from=pricing&type=general`

### 5. 역할별/대상별 페이지 (for-safety-manager, for-business-owner 등)

- 하단 CTA "시작하기" → 무료 진단 유지
- "전문가 상담" 또는 "문의" 버튼 → `?from={페이지명}&type=general`

### 6. 푸터 (전 페이지 공통)

- "도입 문의" 링크 → `?from=footer&type=general`

## 스캔 명령어

Cursor/Code에서 아래 grep으로 대상을 찾으세요:

```bash
# nexas/ 폴더 전체에서 문의 관련 링크/버튼 검색
grep -rn '문의\|상담\|알아보기\|이용하기\|연결하기\|요청하기' nexas/ --include='*.html' --include='*.js'

# mailto 링크 검색 (이것도 fix-request로 변경 대상)
grep -rn 'mailto:\|tel:' nexas/ --include='*.html' --include='*.js'

# 기존 외부 링크 검색
grep -rn 'href="#"\|href="javascript' nexas/ --include='*.html'
```

## fix-request.html 측 수정 (from/type 파라미터 처리)

fix-request.html의 startChat() 함수에서 URL 파라미터를 읽어 첫 인사를 변경:

```javascript
// startChat() 내부에 추가
const params = new URLSearchParams(window.location.search);
const fromPage = params.get('from') || '';
const serviceType = params.get('type') || 'general';

const greetings = {
  'appointment': '안녕하세요! 안전관리자 선임이 필요하신 상황이시군요. 사업장 규모와 업종을 말씀해주시면 적합한 전문가를 연결해드리겠습니다.',
  'repair': '안녕하세요! 설비 수선·보수가 필요하신가요? 어떤 설비에서 어떤 문제가 발생했는지 편하게 말씀해주세요.',
  'consulting': '안녕하세요! 안전관리 컨설팅에 대해 알아보고 계시군요. 현재 사업장의 안전관리 상황을 간단히 알려주시면 맞춤 안내를 드리겠습니다.',
  'general': '안녕하세요. TAI 매칭 전문가입니다. 어떤 상황인지 편하게 말씀해주세요.'
};

const greeting = greetings[serviceType] || greetings['general'];
```

## 금지 사항

- mailto: 링크 사용 금지 (이메일 문의 → 채팅으로 대체)
- 카카오톡 상담 링크 금지
- 외부 폼(Google Forms 등) 링크 금지
- 기존 fix-request.html의 채팅 JS 로직 변경 금지 (인사 메시지 분기만 추가)

## 완료 기준

1. `grep -rn '문의\|상담' nexas/` 결과에서 fix-request 외 다른 곳으로 가는 링크 0건
2. 각 버튼에 적절한 from/type 파라미터 포함
3. fix-request.html에서 type별 인사 메시지 분기 동작
4. 모든 페이지에서 해당 버튼 클릭 → fix-request 페이지 정상 이동 확인
