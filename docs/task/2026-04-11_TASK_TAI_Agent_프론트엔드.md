# TAI Agent — 프론트엔드 작업지시서

> 작성일: 2026-04-11
> 담당: 프론튴드창 (taiengineering/taieng repo, nexas/)
> 우선순위: 높음

---

## 배경

**TAI Agent** = 수선연결 + 대행연결 통합 서비스

법령진단 리포트에서 "직접 처리할 수 없는 항목"을 외부 전문업체에 맡기는 통합 서비스.

```수선연결 (설비 수리) + 대행연결 (법정 서류/검사/점검 위탁)```

---

## 작업 대상 파일

| 파일 | 작업 |
|---|---|
| `nexas/index-3.html` | TAI Agent 서비스 소개 페이지 (신규) |
| `nexas/index.html` | 히어로 슬라이드 TAI Agent 연결 (5번째 클릭 확인) |

---

## 작업 1. nexas/index-3.html 신규 생성

### URL
`new.taieng.co.kr/index-3.html`

### 페이지 전체 구조

```
[GNB - 기존링 tai-nav]

[Hero 섹션]
  - 태그: "TAI Agent"
  - 타이틀: "이건 제가 대신 해드리겠습니다"
  - 서브타이틀: "법령진단 후 직접 처리할 수 없는 항목, TAI가 적합한 전문업체를 연결합니다"
  - CTA: "무료 보견따기" → free-diagnosis.html
  - 스타일: 기존 hero1 이수동 (다크 그라디언트)

[2개서비스 소개 섹션]
  파란색 카드: "🔧 수선연결" - 고장난 설비 수리
  초록색 카드: "📋 대행연결" - 법정 서류/검사/점검 위탁
  각 카드에 핵심 특징 3가지

[대행 서비스 목록 섹션] ← API 로드
  섹터 탭: [건설] [산업] [건물·시설]
  각 탭별 서비스 리스트 카드

[수선 서비스 안내 섹션] ← 정적 UI
  "설비가 고장났나요?"
  수선 요청 방법 안내

[필요 방식 알거든 바로 요청 섹션]
  CTA: "대행 요청하기" / "수선 요청하기"

[Footer]
```

### 대행 서비스 목록 API 호출

```javascript
const API = 'https://api.taieng.co.kr';

async function loadAgentServices(sector) {
  const res = await fetch(`${API}/agent-service?sector=${sector}`);
  const d = await res.json();
  return d.data || [];
}
```

### 렌더링 규칙

```
서비스 카드 1개 = [서비스명] + [가격/표시문구] + [문의하기 버튼]

- price === 0  → 표시문구 우선, 없으면 "별도문의"
- price > 0   → price_display 우선, 없으면 price.toLocaleString() + '원~'
- 버튼: "요청하기" → contact.html?type=agent&service=[service_code]
```

### 디자인 요구사항

- tai-main.css 기존 스타일 사용
- 햤더 스타일: `var(--navy)` 배경 + 다크 튤은
- 서비스 카드: 흰 배경, 파란 악센트 (수선) / 초록 악센트 (대행)
- API 로드 중 spinner 표시
- API 실패 시 실패 메시지 표시 (fallback 하드코딩 금지)

---

## 작업 2. nexas/index.html — TAI Agent 연결 확인

메인 홈페이지의 5번째 히어로 슬라이드 (`s-bg5`) 소개 코피 수정:

```html
<!-- 현재 -->
<span class="hero-tag">전문가 연결 — 수선</span>
<h1 class="hero-h1">이번에도<br>고장이네.</h1>
<a href="index-3.html" class="btn-red">수선 전문가 찾기</a>

<!-- 수정 후 -->
<span class="hero-tag">TAI Agent</span>
<h1 class="hero-h1">직접 할 수 없는 일<br>대신 해드리겠습니다.</h1>
<a href="index-3.html" class="btn-red">TAI Agent 보기</a>
```

---

## 갈을김 가장 짜리스한 포인트

**법령진단 리포트에서 바로 링크:**

횩시에 index-3.html TAI Agent 페이지를 링크 걸을 수 있어야 함.
다음 단계에서 safe.taieng.co.kr 진단 결과 화면에서
"이 항목은 TAI Agent에 요청하세요" 뺄지와 링크 연결.
(지금은 페이지 생성만 연결은 나중)

---

## 완료 기준

- [ ] `nexas/index-3.html` 생성 완료
- [ ] 대행 서비스 목록 API 로드 정상 (건설 12개 / 산업 7개 / 건물 6개)
- [ ] 대행 요청 버튼 → contact.html 링크
- [ ] `nexas/index.html` 5번째 히어로 코피 수정
- [ ] 구냠 nav TAI AGENT 메뉴 확인 (index-3.html 링크)
