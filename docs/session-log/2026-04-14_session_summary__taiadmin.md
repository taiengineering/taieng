# 2026-04-14 기획 세션 최종 요약

## 웹사이트 리빌드 완료 (14단계) ✅
- repo: taiengineering/taieng (nexas/ 폴더)
- 상세 기록: taieng repo의 docs/session-2026-04-14-planning.md
- 기획서: taieng repo의 docs/workorder-website-rebuild-v5.md
- 대표님 피드백: "구조가 특히 잘 풀렸다. 서비스 소개 정확도+빠진 기능은 고도화에서."

---

## 가격체계 전체 확정 ✅

### TAI 역할 정의
- TAI는 대행이 아님
- SaaS = 안전관리를 직접 하게 해주는 도구
- 법령진단 = 미리 알고 대비하게 하는 1회성 리포트 서비스 (일정생성·TBM·신고서식은 SaaS 기능)
- 선임/수선/진단 = 연결하고 수수료를 받는 역할
- 대행기관은 경쟁자가 아니라 연결 서비스의 공급자(파트너)

### 법령진단 (1회성 리포트)
| 유형 | 구조 | 가격 |
|------|------|------|
| 건물 | 무료 + 종합 | 0 + 299,000원 |
| 산업 | 무료 + 표준 + 설비 + 종합 | 0 + 99K + 199K + 249K |
| 건설 | 무료 + 종합 | 0 + 299,000원 |

### SaaS (시설당/현장당 월정액)
| 섹터 | 플랜1 | 플랜2 | 플랜3 | 커스텀 |
|------|-------|-------|-------|--------|
| 건물 | BASIC 59K | STANDARD 99K | - | 협의 |
| 산업 | STARTER 79K | BUSINESS 149K | PRO 249K | 협의(350K~) |
| 건설 | STANDARD 199K | PREMIUM 399K | - | 협의(500K~) |

### SMS/카카오/서류/TBM
- 당연히 제공. 건수 제한 없음. 가격표에 노출하지 않음.

### 연결 수수료
- 미확정. 사전등록 방식으로 모수 확보 후 정식 오픈 예정.
- 확정 원칙: 거래 성사 시만 수수료, 공급자 부담, 수요자 무료.

---

## DB 반영 완료 ✅

### price_saas_plan
- 10개 활성 (섹터별 분리, 시설당 과금)
- 22개 비활성 (구버전)
- 새 컬럼: billing_unit, sms_included(-1), kakao_included(-1), doc_included(-1), include_tbm(true)

### price_diagnosis_report
- 3개 활성: BUILDING_V2(299K), INDUSTRY_V2(99K/199K/249K), CONSTRUCTION_V2(299K)
- 6개 비활성 (구버전)

### connect_pre_registration
- 테이블 생성 완료

---

## 백엔드 반영 완료 ✅
- routers/public_pricing.py (공개 가격 API)
- routers/connect_registration.py (연결 사전등록 API)
- main.py 라우터 등록

## 프론트 부분 완료
- pricing.html SMS/카카오/서류 노출 삭제 ✅
- pricing.html 가격/구조 전면 재작성 ❌ (미완료)

---

## 미완료 → 다음 세션

### 긴급: pricing.html 전면 재작성
- 작업지시서: taieng repo의 docs/workorder-pricing-html-rebuild.md
- SaaS 탭: 섹터별 서브탭 + 확정 가격
- 법령진단 탭: 무료+유료 단계 구조
- API 연동 (어드민 수정 → 사이트 자동 반영)

### 연결 서비스
- connect.html 사전등록 페이지 신규
- header.js 메뉴 업데이트

### 웹사이트 고도화
- 서비스 소개 정확도 + 빠진 기능 추가
- 실제 스크린샷으로 placeholder 교체

### 관련 문서 위치 (taieng repo)
- docs/TAI_가격체계_제안서_v3.0.md — 가격 제안서 (확정)
- docs/workorder-pricing-backend.md — 백엔드 지시서
- docs/workorder-pricing-frontend.md — 프론트 지시서
- docs/workorder-pricing-html-rebuild.md — pricing.html 재작성 지시서
- docs/session-2026-04-14-final.md — 세션 최종 기록
