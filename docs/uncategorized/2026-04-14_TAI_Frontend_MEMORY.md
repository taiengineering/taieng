# TAI 프론트엔드 세션 작업내역 — 2026-04-14

> 레포: taiengineering/taieng (nexas 마케팅 사이트)
> 작업창: 프론트엔드 전담창
> 브랜치: main (taieng 레포는 main 직접 커밋)

---

## 이번 세션 완료 작업

### 1. index.html 리빌드 (단계 11)
- 파일: `nexas/index.html`
- Nexas 원본 템플릿(index-1.html) 기반으로 전면 리빌드
- 기존 커스텀 CSS 전면 제거 → 원본 Nexas CSS 클래스 방식으로 교체
- 섹션 구성:
  - `banner-area`: "아직도 엑셀로 안전관리 하십니까?" + 이메일 input-group
  - `service-area`: 현실 공감 3카드 (엑셀관리/법령몰라/서류쓰느라)
  - `featured-area`: 역할 선택 4카드 (아코디언 → 그리드 전환)
  - `management-area`: 3단계 작동 방식
  - `counter-area`: 2080+/6건/3가지/0원
  - `app-screen-area`: owl carousel
  - `subscribe-area`: CTA
- 커밋: `d6f3c08`

---

### 2. service/diagnosis.html 리빌드 (단계 12)
- 파일: `nexas/service/diagnosis.html`
- 섹션 구성:
  - 히어로: "몰라서 맞았던 벌금, 이제 알고 대비할 수 있습니다"
  - 무료 vs 유료 비교 테이블 (7개 항목, 유료 헤더 빨간색)
  - 법령진단 가치 4블록 (문서증거/법변경대응/비용효율/정확한의무)
  - 진단 유형 가격 3종 (건물/산업/건설, 건설 `featured` 강조)
  - `subscribe-area` CTA
- 커밋: `68c044b`

---

### 3. service/education.html 리빌드 (단계 13)
- 파일: `nexas/service/education.html`
- 섹션 구성:
  - 히어로: "법정 안전교육, 이제 TAI에서 한번에"
  - 법정 교육 종류 5개 + CTA 카드 (6열 그리드)
  - TAI 교육 장점 4카드 (온라인/오프라인/이수관리/수료증)
  - SaaS 연동 강조 섹션 (다크 배경, saas.html 링크)
  - `subscribe-area` CTA
- 히어로 CTA: `contact.html` (교육신청/단체문의 모두)
- 커밋: `0dc5ba2`

---

### 4. service/inapp.html 리빌드 (단계 13)
- 파일: `nexas/service/inapp.html`
- 섹션 구성:
  - 히어로: "안전 관련 귀찮은 것들, TAI가 다 대행합니다"
  - 포함 기능 8개 4열 그리드 (신고서식/점검일지/화학물질라벨/MSDS/TBM/KOSHA/회의록/경영진보고서)
  - 강조 섹션 (다크 배경, 인용구 2개)
  - `subscribe-area` CTA
- CTA: 무료시작 → `free-diagnosis.html`, 요금제확인 → `pricing.html`
- 커밋: `4ce21f6`

---

### 5. 전 페이지 네비 통일 + 텍스트 전수검수 (단계 14)

#### 파트 A: 네비게이션 확인 결과

| 파일 | header.js | nav-auth.js | footer.js | 조치 |
|---|---|---|---|---|
| faq.html | ✅ | ✅ | ✅ | 이상 없음 |
| safety-news.html | ✅ | ✅ | ✅ | 이상 없음 |
| safety-news-detail.html | ✅ | ✅ | ✅ | 이상 없음 |
| sign-up.html | — | — | — | redirect 파일, 네비 불필요 |
| site-map.html | hardcoded (의도적) | — | ✅ | 내부점검용 standalone 유지 |
| pricing.html | ✅ | ✅ | ✅ | 이상 없음 |
| **for-business-owner.html** | ❌ 하드코딩 nav | ✅ | ✅ | **수정 완료** |
| **for-safety-manager.html** | ✅ | ❌ 누락 | ✅ | **nav-auth.js 추가** |
| **target/building.html** | ✅ | ❌ 누락 | ✅ | **nav-auth.js 추가** |
| service/saas.html | ✅ | ❌ 누락 | ✅ | 다음 세션 처리 권고 |

#### 파트 B: 텍스트 검수 결과

| 검수 기준 | 결과 |
|---|---|
| 절대 금지 용어 (소개비/소개수수료/인력소개/소개료) | 전 파일 미발견 ✅ |
| 크레딧 사용 금지 | pricing.html "포함 수량"/"초과 건수" 정상 ✅ |
| "서류 자동제출" 구 용어 | "신고서식 자동화" 올바르게 사용 ✅ |
| 구 페이지 링크 (index-1~6, blog.html) | 전 파일 미발견 ✅ |
| 맞춤법 오류 | **appointment.html "알맞는" → "알맞은" 수정 완료** |

#### 파트 C: site-map.html 갱신

- 최종 갱신일: 2026-04-13 → **2026-04-14** 업데이트
- 커밋: `d03931a`

---

## 커밋 목록 (이번 세션, taieng repo)

| SHA | 내용 |
|---|---|
| `d6f3c08` | rebuild: index.html — Nexas 원본 템플릿 기반 메인 페이지 리빌드 |
| `68c044b` | rebuild: service/diagnosis.html — 법령진단 페이지 리빌드 |
| `0dc5ba2` | rebuild: service/education.html — 교육사업 페이지 리빌드 |
| `4ce21f6` | rebuild: service/inapp.html — 인앱 서비스 페이지 리빌드 |
| `d03931a` | final: 전수검수 1차 — for-business-owner 하드코딩nav 제거 + sitemap 날짜 갱신 |
| `bd51d51` | final: nav-auth.js 추가 — for-safety-manager, target/building |
| `1950bd3` | final: 텍스트 검수 — appointment.html "알맞는" → "알맞은" 수정 |

---

## 미완료/다음 세션 권고 사항

### service/saas.html
- nav-auth.js 누락 상태
- 스크립트 끝부분에 `<script src="../assets/js/nav-auth.js"></script>` 삽입 필요
- header.js 와 footer.js 사이에 위치

### 미확인 파일 (nav-auth.js 상태 미점검)
- `target/factory.html`
- `target/construction.html`
- `log-in.html`, `terms.html`, `privacy.html`, `patents.html`
- `contact.html`, `free-diagnosis.html`, `free-diagnosis-result.html`
- `about.html`, `service/repair.html`

---

## 개발 규칙 확인 (taieng nexas 사이트)

- Nexas 원본 CSS 클래스명 최대 활용 (banner-area, service-area 등)
- `body class="sc5"` 유지 (보라색 테마)
- 헤더: `<div id="tai-header"></div>` + `header.js` + `nav-auth.js`
- 푸터: `<div id="tai-footer"></div>` + `footer.js`
- service/ 하위 파일 경로: `../assets/` (한 단계 상위)
- target/ 하위 파일 경로: `../assets/` (한 단계 상위)
- 절대 금지: 소개비, 소개수수료, 인력소개, 소개료, 크레딧
- 확정 용어: 신고서식 자동화 (서류 자동제출 X), 매칭 서비스료, 성과 정산금

---

*생성일: 2026-04-14 | 프론트엔드 전담창*
