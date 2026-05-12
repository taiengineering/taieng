# 모바일 반응형 점검 및 수정 기획서 — 2026-05-09

> 점검 환경: Claude in Chrome (Browser 1, macOS), viewport **393×852** (iPhone 14 Pro 표준)  
> 점검 범위: footer.js 메뉴 + 대표 부속 페이지 총 **17개**  
> 목적: 일반 사용자 기준 사용 불편사항 식별 + 수정 우선순위 설정

---

## 📊 점검 결과 종합

### 페이지별 상태 (17개)

| # | 페이지 | 상태 | 주요 이슈 |
|---|---|---|---|
| 1 | `/` (홈) | ⚠️ | 4-step 카드 이미지가 viewport 거의 다 차지 → 스크롤 부담 |
| 2 | `service/diagnosis.html` | ⚠️ | "정보 입력/법령 분석/결과 제공" 3분할 이미지 → 패널당 130px 수준으로 입력항목 그림·글자 판독 불가 |
| 3 | `service/saas.html` | ✅ | 그룹별 챴터텍스트 카드 1열 OK |
| 4 | `service/inapp.html` | ✅ | 카테고리 필터 wrap 잘 됨 (최근 추가) |
| 5 | `free-diagnosis.html` | ✅ | 모던 블루 적용 후 잊습 |
| 6 | `contact.html` | ✅ | 5차 개편 후 잊습 (분야 버튼 3열 wrap, FAQ 카드 양호) |
| 7 | `faq.html` | ✅ | 카테고리 필터 wrap, accordion 정상 |
| 8 | `target/factory.html` | 🔴 | "공정/설비/작업자/기록" 4분할 이미지 → 패널 당 약 90px, 메시지 읽을 수 없음 |
| 9 | `target/building.html` | ✅ | hero + 텍스트 구조, 이미지 클레임 이슈 없음 |
| 10 | `target/construction.html` | ✅ | OK |
| 11 | `for-safety-manager.html` | 🔴 | "방법은 바꿔도 구조는 그대로" 데스크탑용 콜라주 이미지 → 재컴포즈 필요 |
| 12 | `for-business-owner.html` | ✅ | 아이콘 + 텍스트 카드 1열 OK |
| 13 | `safety-news.html` | 🔴 | 통계 5개(30547/3368/4294/1497/1926)를 한 줄로 강제 → 패널 당 약 70px, 숫자 글자 7px 수준 |
| 14 | `accident-cases.html` | ✅ | 통계 2개, 적절 |
| 15 | `law-updates.html` | ✅ | 통계 4개 2×2 그리드 OK |
| 16 | `precedent-search.html` | ✅ | 적절 |
| 17 | `about.html` | ✅ | hero + 인물 이미지 + 본문 레이아웃 적절 |
| 18 | `patents.html` | ✅ | 적절 |
| 19 | `log-in.html` | ✅ | 최근 개편 (모바일에서는 좌측 hero 숨김, 우측 폼만 표시) |

**요약**: 17개 중 **🔴 3개 심각**, **⚠️ 2개 불편**, 나머지 양호.

---

## 🎯 식별된 이슈 패턴 (5가지)

### Pattern A. 데스크탑용 가로-분할 이미지가 모바일에서 너무 작아서 판독 불가

**해당 페이지 (3개)**:
- `service/diagnosis.html`: "사업장 정보 하나로 의무가 정리됩니다" 섹션의 3분할 (정보 입력 / 법령 분석 / 결과 제공)
- `target/factory.html`: "사고는 몰라서가 아니라, 놓쳐서 발생합니다" 4분할 (공정/설비/작업자/기록)
- `for-safety-manager.html`: "방법은 바꿔도 구조는 그대로" 섹션의 데스크탑용 콜라주 이미지

**증상**: 가로로 3-4개 패널을 이어 만든 단일 이미지가 모바일 viewport 너비(393px)에 맞게 명시적 축소됨. 패널당 90~130px로 완전 압축되어 내부 글자가 7-9px 수준으로 읽힌 수 없음.

**근본 원인**: PNG/JPG 단일 이미지로 몀 패널 레이아웃을 하드코딩 → 반응형 불가.

**해결 방침**:
1. **A안 (권장)**: 이미지를 **각 패널별 개별 이미지**로 분리 또는 텍스트 카드로 재구성. 모바일에서는 1열 세로 배치.
   ```css
   @media (max-width: 768px) {
     .panel-row-image { display: none; }
     .panel-row-cards { display: grid; grid-template-columns: 1fr; gap: 16px; }
   }
   ```
2. **B안 (임시)**: 이미지에 lightbox/zoom 기능 추가. 사용자가 탭하면 확대 보기. (UX 적 권장도 낮음)
3. **C안 (최소 노력)**: 모바일에서 이미지 숨기고 계층 설명 텍스트로 대체. 서비스 메시지 손실 가능성 있음.

### Pattern B. 통계 수치 다수를 한 줄로 강제 (글자 깨짐)

**해당 페이지 (1개)**:
- `safety-news.html`: 5개 통계 (`30,547`/`3,368`/`4,294`/`1,497`/`1,926`)가 수평 5분할

**증상**: 393px viewport에 5개 카드 강제 → 카드 당 70px 수준 → 5자리 숫자(`30,547`)가 축소되어 7px 수준으로 표시 → 판독 불가

**관련 양호 패턴 (참고)**:
- `accident-cases.html`: 통계 2개 → 한 줄로 적절
- `law-updates.html`: 통계 4개 → 2×2 그리드로 적절

**해결 방침**:
```css
@media (max-width: 480px) {
  .news-stats-grid {
    grid-template-columns: repeat(2, 1fr);  /* 2열 + 줄바꿈 */
    gap: 8px;
  }
  /* 또는 가로 스와이프 (overflow-x: auto) */
}
```

### Pattern C. 카드 이미지가 viewport 거의 다 차지 → 정보 밀도 낮음

**해당 페이지 (1개)**:
- `/` (홈): 4개 차례적 카드 (01: 무슨 법이 적용되는지 / 02: 무엇을 해야 하는지 / 03: 하긴 했는데 맞는지 / 04: 그래서 항상 불안)

**증상**: 카드 당 높이 ~600px (이미지가 주도) → 카드 1개당 한 화면 거의 전부 차지 → 4개 다 보려면 스크롤 30+회

**해결 방침**:
```css
@media (max-width: 768px) {
  .home-step-card img {
    max-height: 200px;
    object-fit: cover;
  }
  /* 또는 카드 타이틀+코피 도해 이미지는 씀네일 키워서 텍스트 도마니어하게 */
}
```

### Pattern D. (잘되고 있는 참고 사례)

다음 패턴들은 **현재도 모바일에서 잘 작동** — 새 수정 시 참고:
- `contact.html` 분야 버튼 5개: `grid-template-columns: repeat(5,1fr)` → 720px 이하 `repeat(3,1fr)` → 480px 이하 `1fr 1fr`
- `faq.html` 카테고리 필터: `flex-wrap: wrap`으로 6개 자연 줄바꿈
- `for-business-owner.html` 아이콘 카드: 1열 + 적당한 높이
- `law-updates.html` 통계: 2×2 그리드

### Pattern E. 헤더 로고 안 보이는 경우 (경미함)

- `free-diagnosis.html`: 상단에서 헤더 로고가 회색 배경에 웰닝·흐복 읽히지 않음 (키 컴트라스트 낮음)
- 사용자 알아소 곤란.

**해결**: 헤더의 `tai-logo-text`에 `text-shadow` 추가 또는 logo PNG/SVG 교체.

---

## 🔧 수정 기획 — 우선순위별

### 🔴 P0 (사용 불가 · 즉시 수정)

#### P0-1. `target/factory.html` 4분할 이미지 재구성
- **파일**: `nexas/target/factory.html`
- **작업**: "사고는 몰라서가 아니라" 섹션의 단일 이미지 → 4개 카드로 분리
- **추정 시간**: 30분
- **이미지 소스 필요**: 4개 개별 아이콘/일러스트 (공정/설비/작업자/기록) — 사용자 제공 필요
- **fallback**: CSS로 원본 이미지를 `transform: scale(2)` + horizontal scroll 컴테이너

#### P0-2. `for-safety-manager.html` 콜라주 이미지 재구성
- **파일**: `nexas/for-safety-manager.html`
- **작업**: "방법은 바꿔도 구조는 그대로" 섹션의 잡화한 콜라주 → 5개 카드(엑셀/폴더/단톡방/내가 잇고/그래도 올릿 않음)로 분리
- **추정 시간**: 45분
- **이미지 소스 필요**: 5개 개별 아이콘 또는 일러스트

#### P0-3. `safety-news.html` 통계 레이아웃 수정
- **파일**: `nexas/safety-news.html`
- **작업**: 5-column 그리드 → 모바일에서 2-column 2.5줄 또는 가로 스와이프
- **추정 시간**: 15분
- **이미지 소스 필요**: 없음 (CSS만 수정)

### ⚠️ P1 (불편 · 다음 주 내 수정)

#### P1-1. `service/diagnosis.html` 3분할 이미지 재구성
- **파일**: `nexas/service/diagnosis.html`
- **작업**: 3분할 단일 이미지 → 3개 카드(정보 입력 / 법령 분석 / 결과 제공)로 분리
- **추정 시간**: 30분
- **이미지 소스 필요**: 3개 개별 이미지

### 🟡 P2 (정보 밀도 향상 · 여력 있을 때)

#### P2-1. 홈 4-step 카드 이미지 높이 제한
- **파일**: `nexas/index.html`
- **작업**: 카드 이미지에 `max-height: 200px; object-fit: cover` 적용
- **추정 시간**: 10분

#### P2-2. `free-diagnosis.html` 헤더 로고 가독성
- **파일**: `nexas/free-diagnosis.html` 또는 헤더 공통 CSS
- **작업**: 회색 배경 위 로고에 `text-shadow` 추가
- **추정 시간**: 5분

---

## 🔍 점검 범위 밖 파일 (주의 필요)

이번 점검에서는 제외되었으며 추가 점검 권장:
- `sign-up.html` (log-in.html과 동일 구조로 추정)
- `mypage/*` (로그인 필요 페이지)
- `terms.html`, `privacy.html` (약관 페이지)
- 개별 재해사례 상세 페이지 (`/accident-cases/{id}.html`)

---

## 💸 작업 순서 권장

1. **P0 병렬 수정** (1일 이내)
   - safety-news.html (CSS만) → 즉시 수정 가능
   - target/factory.html, for-safety-manager.html → 이미지 소스 확보 후 재구성
2. **P1 접근** (3-4일 이내)
   - service/diagnosis.html
3. **P2 마무리** (1주 이내)
   - 홈 + 헤더 가독성
4. **추가 점검** (추후)
   - sign-up, mypage, terms/privacy, 재해사례 상세 페이지

**권장 CSS 관리**: `nexas/assets/css/tai-mobile-fixes.css` 신규 파일로 모든 모바일 반응형 수정 집중. 개별 페이지 inline 수정 지양.

---

## 📦 이미지 자산 필요 목록

다음 이미지들은 재구성을 위해 개별 파일로 필요:

| 페이지 | 세션 | 필요 이미지 수 |
|---|---|---|
| service/diagnosis.html | "사업장 정보 하나로" | 3개 (정보 입력 / 법령 분석 / 결과 제공) |
| target/factory.html | "사고는 몰라서가" | 4개 (공정/설비/작업자/기록 각각) |
| for-safety-manager.html | "방법은 바꿔도" | 5개 (엑셀/폴더/단톡방/내가 잇고/그래도 올릿 않음) |

사용자게서 **원본 이미지 소스 파일** 또는 **각 패널별 개별 이미지**를 받으면 있는 그대로 적용 가능. 이미지 없으면 텍스트/아이콘 카드로 대체.

---

## 📝 다음 액션

1. 사용자 확인: 이미지 소스 파일 제공 또는 "텍스트/아이콘 카드로 재구성" 결정
2. P0-3 (safety-news.html) 변경은 이미지 없이 즉시 가능 → 우선 처리 권장
3. 추가 점검 필요 시: sign-up.html, mypage 포함 재점검

---

*작성: 2026-05-09 점검 세션*  
*담당: Claude (Anthropic) via Claude in Chrome (모바일 viewport 393×852)*  
*점검 소요 시간: 약 5분 (4차례 batch)*
