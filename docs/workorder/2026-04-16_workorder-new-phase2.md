# [FRONTEND-NEW] new.taieng.co.kr Phase 2 — 마케팅 사이트 전면 진행

**작성일:** 2026-04-16  
**담당 윈도우:** frontend-new (taieng repo)  
**출식 도메인:** new.taieng.co.kr (Cloudflare Pages)

---

## 작업 목록

| # | ID | 작업 | 우선순위 |
|---|---|---|---|
| 1 | FN-01 | nexas/pricing.html 신규 (SaaS + 법령진단 통합 요금표) | 🔴 |
| 2 | FN-02 | for-safety-manager.html | 🟡 |
| 3 | FN-03 | for-business-owner.html | 🟡 |
| 4 | FN-04 | service/ 하위 7개 페이지 | 🟡 |
| 5 | FN-05 | target/ 하위 3개 페이지 | 🟡 |
| 6 | FN-06 | 사이트맵 확정본 기반 전체 리디자인 | 🟢 |

---

## FN-01 🔴 nexas/pricing.html — 통합 요금표 (최우선)

### 두 개 요금 파트 합산
**SaaS 구독** (과금구조_기획서_v1.0 기준)
- STARTER 79,000원/월 / BUSINESS 149,000원/월 / ENTERPRISE 협의
- 포함 인원 + 초과 단가 + SMS·카카오·서류 **포함건수** 표기
- ⚠️ 크레딧 미노출 (내부 회계용). UI에는 "포함 N건 / 초과 건당 X원" 형식

**법령진단 단건** (요금체계_v2.0 기준)
- 건물 99K / 제조 249K / 건설 399K (6종류 시설별 4등급 가격표)
- **단일 결제 서비스 제공기간 12개월** 명시 (KG이니시심사 통과 조건)
- 리포트 재발행·조회 12개월 포함

### 결제 플로우
- **KG이니시스 바로 결제** (문의가 아닌 직접 결제)
- SaaS: 정기결제 MID (발급 대기 중) 접속 시 안내 페이지
- 법령진단: 일반결제 MID 활성 (초기 보증보험 200만원, 월 정산 한도 33만원, 익월 8일 정산)

### UI 구조
```
[탭 1: SaaS 구독]           [탭 2: 법령진단 단건]
  └ 3개 카드              └ 시설별 선택 → 4등급 카드 6셋

[결제 특전]
  └ 이벤트/쿠폰 영역 (협의 가능)

[FAQ]
  └ 언제 결제되나요? / 환불규정 / 세금계산서
```

### 오흐립 방지
- "성과보수" × "성과 정산금" ○ / "인력소개" × "연결 서비스료" ○ (금지 용어 메모리 준수)
- 대행기관 가격과 비교 금지 — 비교 대상은 엑셀·종이(무료) + 과태료 리스크
- 카카오 API 금지 — 주소검색 juso.go.kr 사용

---

## FN-02 • FN-03 그룹지 페이지

### for-safety-manager.html
- 안전관리자 — 겁직 포함 — 입장에서 본 TAI Safe
- "혼자 다 하지 않아도 되는 구조" 핵심 메시지 (모듈 특허 연계)
- 지시→모니터링→이상대응 역할 전환 시나리오
- CTA: "무료 진단받기" (법령진단 결제 페이지로 연결)

### for-business-owner.html
- 대표·사업주 입장에서 본 TAI Safe
- 중대재해처벌법 / 산업안전보건법 과태료 리스크 강조
- "애매한 요식행위" 구조적 문제 해결
- CTA: "도입 상담 받기"

두 페이지는 기존 nexas 레이아웃 재사용. 섹션 구조:
1. Hero (공감되는 조어들)
2. "이런 상황 있으세요?" Pain points
3. TAI Safe 핵심 값에 대한 소개
4. 사례/효과 (지금은 가상 예시 OK)
5. 가격 + CTA

---

## FN-04 🟡 service/ 하위 7개 페이지

메모리 TASK 목록에 "7개" 명시. 사이트맵 확정본 기준 경로 확인 후 실제 후보:

1. `service/saas.html` — SaaS 기능 전체 소개 (알림·점검·교육·서류 등)
2. `service/law-diagnosis.html` — 법령진단 상세 (단건 결제)
3. `service/inspection.html` — 점검·TBM 기능 전용
4. `service/education.html` — 교육사업 (수익최상위)
5. `service/document-autogen.html` — 자동신고·문서서식·라벨자동생성 (인앱서비스)
6. `service/matching.html` — 수선연결·전문가매칭 (⚠️ "연결 서비스"로 명시, 인력소개 표현 금지)
7. `service/consulting.html` — 컬설팅·선임

어떠한 이유로든 "대행"이라 표현 금지 — TAI는 "직접 하게 해주는 도구 + 연결 플랫폼" 포지셔닝.

---

## FN-05 🟡 target/ 하위 3개 페이지

시설유형별 진입 페이지:

1. `target/building.html` — 건물관리 사업단지·업무시설 대상 (건물 법령진단 99K)
2. `target/manufacturing.html` — 공장·제조업체 대상 (제조 법령진단 249K)
3. `target/construction.html` — 건설현장·시공사 대상 (건설 법령진단 399K)

각 페이지 구조:
1. Hero ("제조업체 안전관리, 3분에 확인하세요")
2. 해당 업종 전용 리스크 요약 (몇 가지 질문으로 미리보기)
3. 해당 업종 TAI Safe 지원 기능
4. 해당 업종 법령진단 상품 CTA
5. 소규모 배려한 헤로 문구 (5인에서 50인 확대)

---

## FN-06 🟢 사이트맵 기반 전체 리디자인

- 2026-04-12 사이트맵 확정본 기준 (대표 현장 보유)
- FN-01부터 FN-05까지 개별 페이지 완료 후에 시작
- 메인 헤더 · 푸터 · 네비게이션 재정리
- 특허출원 메뉴명이 "TAI 기술력"으로 변경되었으므로 footer.js 반영 여부 다시 점검

---

## 작업 규칙

- taieng repo **main 브랜치**에 커밋 (Cloudflare Pages auto-deploy)
- 기존 nexas 레이아웃/스타일 일관성 유지
- 폰트: Pretendard, Noto Sans KR
- 다국어: 한국어 우선, 영어 대응 서식 준비
- 이미지: /assets/img/ 다운로드 또는 SVG 자체 제작
- CTA 연결: pricing.html → /front-pages/pricing.html (tai-admin 기존 결제 페이지 활용)

---

## 완료 기준

- [ ] FN-01 pricing.html KG이니시스 바로결제연결 확인
- [ ] FN-02/03 그룹지 2개 두 줄기 옵션 모두 구현
- [ ] FN-04 service/ 7개 레이아웃 일차 완성 (상세 텍스트는 draft로)
- [ ] FN-05 target/ 3개 페이지 완성
- [ ] FN-06 헤더/푸터/사이트맵 정렬
- [ ] 모바일 반응형 전수 검사

---

## 참고

- TAI 특허 현황: 총 8건 + 상표 1건 (메모리 #11 참조)
- 금지 용어: 소개비·소개수수료·인력소개·소개료 (메모리 #12)
- 패턴: 카카오 관련 API 사용처 모두 제거 (메모리 #24)
- 백에드 데이터 소스: `api.taieng.co.kr/public/pricing/saas-plans`, `/public/pricing/diagnosis-reports` 이미 존재 (dev 포함, main 아직 배포 안됨)
