# new.taieng.co.kr 웹사이트 정리 작업 지시서
> 2026-04-13 기획창 분석. 프론트엔드 창에서 이 문서 기반으로 작업.

---

## 현황 요약

- 사이트맵 기획(22페이지) 기반 신규 페이지 대부분 생성 완료
- 구 페이지(index-1~6 등)가 삭제되지 않고 공존 중
- 네비게이션이 2가지 버전으로 섹여 있음
- AI 생성 텍스트 검수 누락으로 깨진 한국어 존재

---

## PHASE 1: 구 페이지 삭제 ██ CRITICAL

아래 파일들을 **완전 삭제**한다 (리다이렉트 없음).

### 레거시 메인 페이지 (6개)
```
index-1.html      ← TAI Safe (구) → 신규: for-safety-manager.html + service/saas.html
index-2.html      ← TAI Manager (구) → 신규: for-safety-manager.html
index-3.html      ← TAI Agent (구) → 신규: service/consulting.html + service/repair.html
index-4.html      ← TAI Care (구) → 신규: service/appointment.html
index-5.html      ← 안전정보 허브 (구) → 신규: safety-news.html
index-6.html      ← 미사용
```

### 레거시 서비스/기타 페이지 (8개)
```
construction.html       ← → target/construction.html로 이전됨
service.html            ← → service/ 개별 페이지로 이전됨
service-details.html    ← 구 템플릿 잔재
tai-fix.html            ← 미사용
blog.html               ← 구 블로그 (신규: safety-news.html)
blog-single.html        ← 구 블로그 상세 (신규: safety-news-detail.html)
demo.html               ← Nexas 템플릿 데모 페이지
diagnosis-start.html    ← → free-diagnosis.html로 이전됨
```

### 삭제 후 확인
- site-map.html의 "기타 · 레거시" 섹션 전체 제거
- 삭제된 페이지를 가리키는 모든 내부 링크 제거 (아래 Phase 2에서 처리)

---

## PHASE 2: 네비게이션 통일 ██ CRITICAL

### 현재 문제
페이지마다 메뉴가 다름:

| 페이지 그룹 | 메뉴 3번째 항목 | 안전정보 링크 |
|------------|-----------------|------------------|
| 신규 (index, for-*, service/*, target/*) | TAI AGENT | safety-news.html |
| 구버전 (about, pricing, contact) | TAI FIX | index-5.html |

### 해결: 단일 header.js 만들어서 전 페이지 적용

**새 네비게이션 구조 (사이트맵 기획 기반):**
```
로고(홈)  |  서비스 ▼  |  대상별 ▼  |  요금제  |  회사소개 ▼  |  [무료 진단]  |  [로그인]
             ├ 교육사업        ├ 건물·시설              ├ 회사소개
             ├ 인앱 서비스      ├ 제조공장               ├ 특허출원
             ├ 수선 연결        └ 건설현장               ├ FAQ
             ├ 컨설팅                                    └ 안전정보
             ├ 선임 연결
             ├ SaaS 구독
             └ 법령진단
```

**적용 대상:** 아래 전체 신규 페이지 (22개 + 보조 페이지)
```
index.html
for-safety-manager.html
for-business-owner.html
service/education.html
service/inapp.html
service/repair.html
service/consulting.html
service/appointment.html
service/saas.html
service/diagnosis.html
target/building.html
target/factory.html
target/construction.html
pricing.html
free-diagnosis.html
free-diagnosis-result.html
contact.html
about.html
patents.html
faq.html
safety-news.html
safety-news-detail.html
log-in.html
sign-up.html
terms.html
privacy.html
site-map.html
```

**구현 방법:**
1. `assets/js/header.js` 생성 — 네비게이션 HTML을 JS로 동적 삽입
2. 각 페이지의 기존 `<nav>` 내용을 제거하고 `<script src="../assets/js/header.js"></script>`로 교체
3. 경로 주의: `service/*.html`은 `../assets/js/header.js`, 나머지는 `./assets/js/header.js`

**푸터도 동일하게 footer.js 통일** (현재 구/신 푸터 혹시 다를 수 있음)

---

## PHASE 3: 텍스트 깨짐 수정 ██ HIGH

### 확인된 깨짐
| 페이지 | 깨진 텍스트 | 수정 |
|--------|-----------|------|
| target/building.html | "하나라도 눈치지 않으면 과태료를 못 플다" | → "하나라도 놓치면 과태료를 피할 수 없습니다" |
| target/building.html | "모든 녕일기를 자동으로 기억합니다" | → "모든 일정을 자동으로 기억합니다" |

### 전수 검사 필요 페이지 (AI 생성 텍스트 검수)
아래 페이지들은 신규 생성된 페이지로, 한국어 자연스러움·맞춤법·전문용어 정확성을 검수해야 함:
```
for-safety-manager.html
for-business-owner.html
service/education.html
service/inapp.html
service/repair.html
service/consulting.html
service/appointment.html
service/saas.html
service/diagnosis.html
target/building.html      ← 깨짐 확인됨
target/factory.html
target/construction.html
```

**검수 기준:**
- 한국어 자연스러움 (미완성 문장, 의미 불명 표현)
- 맞춤법 오류
- 산업안전 전문용어 정확성
- "신고서식 자동화" 등 확정된 용어 사용 여부 ("Automated Filing" → "신고서식 자동화")
- 【절대 금지】 소개비/소개수수료/인력소개/소개료 등 소개 관련 용어

---

## PHASE 4: 내부 링크 정리 ██ HIGH

### 구 페이지를 가리키는 링크 전체 교체

| 구 링크 | 신규 링크 | 위치 |
|---------|---------|------|
| index-1.html | service/saas.html | 메인 페이지 "역할 선택" 카드, 기타 |
| index-2.html | for-safety-manager.html | 메인 페이지 "안전관리자" 카드 |
| index-3.html | service/consulting.html | 메인 페이지 "대행" 카드 |
| index-3.html#fix | service/repair.html | 메인 페이지 "수선" 링크 |
| index-4.html | service/appointment.html | 메인 페이지 "전문가" 카드 |
| index-5.html | safety-news.html | 네비게이션 |

### 메인 페이지(index.html) "나는 어디에 해당하나요" 섹션 수정

현재 4개 카드가 모두 구 페이지를 가리킴:

| 카드 | 현재 링크 | 변경 후 |
|------|-----------|--------|
| 사업장 경영자/총무 | index-1.html | **for-business-owner.html** |
| 안전관리자/겸직 | index-2.html | **for-safety-manager.html** |
| 안전관리 여력 없는 사업장 | index-3.html | **service/consulting.html** |
| 안전 전문가/대행업체 | index-4.html | **service/appointment.html** |

### 기타 내부 링크 점검

전체 페이지에서 `index-1` ~ `index-6`, `construction.html`, `service.html`, `blog.html`, `demo.html` 등을 검색해서 남아있는 링크를 전부 제거하거나 신규 페이지로 교체.

검색 키워드:
```
index-1.html
index-2.html
index-3.html
index-4.html
index-5.html
index-6.html
construction.html
service.html
service-details.html
tai-fix.html
blog.html
blog-single.html
diagnosis-start.html
demo.html
```

---

## PHASE 5: pricing.html 가격 표시 수정 █ MEDIUM

### 현재 문제
- "가격 정보를 불러오는 중..."으로 JS 로딩에 의존
- API 호출 실패 시 빈 페이지
- 가격 정보는 전환의 가장 중요한 요소

### 해결
- HTML에 기본 가격표를 하드코딩 (fallback)
- JS는 최신 가격으로 업데이트하는 용도로만

**하드코딩 가격 (확정된 정보):**
- SaaS: 79,000원/월 (기본) / 149,000원/월 (프리미엄) / 커스텀 (엔터프라이즈)
- 법령진단: 건물/산업/건설 3종 (건설이 가장 높음)
- "크레딧" 단어 사용 금지 → "포함 수량" / "초과 건수" 사용

---

## PHASE 6: 구조적 개선 █ LOW

### 6-1. 메인 페이지 구조 점검

현재 index.html 섹션 순서:
1. 히어로 ("법령위반 중이십니까?") ✓ 고정 1개 OK
2. 신뢰 지표 (10억/347%/3분/무료) ✓
3. 역할 선택 4개 카드 ✓ (링크만 교체 필요)
4. 3단계 작동 방식 ✓
5. 스크린샷 3장 ✓ ("실제 서비스 스크린샷으로 교체 예정" 상태)
6. 숫자 통계 ✓
7. CTA ✓

→ 사이트맵 기획대로 잘 되어 있음. 링크 교체만 하면 됨.

### 6-2. 역할별 랜딩 페이지 점검

- for-safety-manager.html: 내용 우수. "도입 전 vs 도입 후" 비교가 효과적.
- for-business-owner.html: 내용 우수. 법적 리스크 강조가 적절.

→ 두 페이지 모두 품질 좋음. 텍스트 검수만 하면 됨.

### 6-3. 서비스 페이지 7개

- 수익 크기순으로 잘 배치되어 있음
- 각 페이지의 CTA가 무료진단 또는 문의하기로 수렴 ✓
- 텍스트 검수 필요

### 6-4. 특허 페이지

- patents.html: 6건 특허 정보 잘 표시됨
- 네비게이션이 없음 (헤더 없이 단독 페이지) → header.js 적용 필요

---

## 작업 순서 요약

| 순서 | 작업 | 우선순위 | 비고 |
|------|------|----------|------|
| 1 | 구 페이지 14개 삭제 | CRITICAL | 파일 삭제 |
| 2 | header.js 생성 + 전 페이지 적용 | CRITICAL | 네비게이션 통일 |
| 3 | 전 페이지 내부 링크에서 구 페이지 링크 제거/교체 | CRITICAL | 특히 index.html 역할선택 카드 |
| 4 | target/building.html 텍스트 수정 | HIGH | 확인된 깨짐 |
| 5 | 신규 12개 페이지 텍스트 전수 검수 | HIGH | AI 생성 텍스트 품질 확인 |
| 6 | pricing.html 가격 하드코딩 fallback | MEDIUM | API 실패 대비 |
| 7 | site-map.html 레거시 섹션 제거 | LOW | 정리 |

---

## 현재 살리는 페이지 최종 목록 (27개)

```
[메인]     index.html
[역할별]   for-safety-manager.html, for-business-owner.html
[서비스]   service/education.html, service/inapp.html, service/repair.html,
           service/consulting.html, service/appointment.html, service/saas.html,
           service/diagnosis.html
[대상별]   target/building.html, target/factory.html, target/construction.html
[전환]     pricing.html, free-diagnosis.html, free-diagnosis-result.html, contact.html
[신뢰]     about.html, patents.html, faq.html, safety-news.html, safety-news-detail.html
[인증]     log-in.html, sign-up.html
[법적]     terms.html, privacy.html
[점검]     site-map.html
[마이페이지] mypage/ (14개 하위 페이지 — 별도 작업)
```

---

## 참고 문서
- `docs/sitemap-taieng-co-kr.md` — 사이트맵 기획 (22페이지 구조)
- `docs/session-2026-04-12-planning.md` — 기획 세션 전체 기록
