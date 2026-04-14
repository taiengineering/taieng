# 기획 세션 2026-04-14 최종 기록

> 기획창(Opus) 작성
> 이전 세션: 2026-04-13 (Fly.io 이전, 사이트맵, 모니터링)

---

## 확정된 사항 (전체)

### 1. TAI 비즈니스 모델 명확화
- TAI는 대행이 아님
- SaaS = 안전관리를 직접 하게 해주는 도구
- 법령진단 = 미리 알고 대비하게 하는 1회성 리포트 서비스 (일정생성·TBM·신고서식은 SaaS 기능)
- 선임/수선/진단 = 연결하고 수수료를 받는 역할
- 대행기관은 경쟁자가 아니라 연결 서비스의 공급자(파트너)
- 가격 비교 대상 = 엑셀/종이(무료) + 과태료 리스크

### 2. 가격체계 전체 확정

#### 법령진단 (1회성 리포트)
| 유형 | 무료 | 유료1 | 유료2 | 유료3 |
|------|------|-------|-------|-------|
| 건물 | 0원 | **299,000원** | - | - |
| 산업 | 0원 | **99,000원** | **199,000원** | **249,000원** |
| 건설 | 0원 | **299,000원** | - | - |

#### SaaS (시설당/현장당 월정액)
| 섹터 | 플랜1 | 플랜2 | 플랜3 | 커스텀 |
|--------|--------|--------|--------|--------|
| 건물 | BASIC **59K** | STANDARD **99K** | - | 협의 |
| 산업 | STARTER **79K** | BUSINESS **149K** | PRO **249K** | 협의(350K~) |
| 건설 | STANDARD **199K** | PREMIUM **399K** | - | 협의(500K~) |

#### SMS/카카오/서류/TBM
- 당연히 제공되는 것이므로 건수 제한 없음
- 가격표에서 노출하지 않음

#### 연결 수수료
- 미확정
- 사전등록 방식으로 모수 확보 후 정식 오픈 예정
- 확정 원칙: 거래 성사 시만 수수료, 공급자 부담, 수요자 무료

### 3. 과금 기준
- SaaS 과금 기준: **시설당** (기존 인원 기반에서 변경)
- 건설은 "현장당"
- 인원 수와 무관

### 4. 결제 프로세스
- KG이니시스로 바로 결제 (문의가 아닌 직접 결제)
- 현재 KG이니시스 승인 대기 중 → 준비 중 모달 표시

### 5. 어드민 가격 수정 → 사이트 즉시 반영
- pricing.html이 API에서 가격을 가져오는 구조
- 캐시 TTL 5분
- API 실패 시 하드코딩 fallback

---

## DB 반영 완료

### price_saas_plan (10개 활성)
- 새 컬럼 추가: billing_unit, sms_included, kakao_included, doc_included, include_tbm
- 구버전 22개 is_active=false
- SMS/카카오/서류 전체 -1(무제한), include_tbm 전체 true
- 검증 완료 ✅

### price_diagnosis_report (3개 활성)
- BUILDING_V2: 무료 + 299K
- INDUSTRY_V2: 무료 + 99K + 199K + 249K
- CONSTRUCTION_V2: 무료 + 299K
- 구버전 6개 is_active=false
- 검증 완료 ✅

### connect_pre_registration
- 테이블 생성 완료

---

## 코드 반영 완료

### 백엔드 (tai-api)
- routers/public_pricing.py 생성 ✅
- routers/connect_registration.py 생성 ✅
- main.py 라우터 등록 ✅

### 프론트 (pricing.html)
- SMS/카카오/서류 포함 건수 노출 삭제 ✅
- 초과 과금 안내 삭제 ✅
- 가격/구조 전면 재작성 필요 (미완료)

---

## 웹사이트 리빌드 (14단계 완료)

- new.taieng.co.kr 전체 페이지 리빌드 ✅
- header.js / footer.js 통일 ✅
- 네비게이션 통일 ✅
- 텍스트 검수 ✅
- 대표님 피드백: "이전보다 많이 좋아졌다. 구조가 특히 잘 풀었다."

---

## 미완료 작업

### 긴급 (pricing.html 전면 재작성)
- 작업지시서: docs/workorder-pricing-html-rebuild.md
- SaaS 탭: 섹터별 서브탭 + 확정 가격
- 법령진단 탭: 무료+유료 단계 구조
- API 연동 (어드민 수정 → 사이트 자동 반영)

### 가격 제안서 포지셔닝 수정
- docs/TAI_가격체계_제안서_v3.0.md — 대행 비교 부분 엑셀/종이+과태료 중심으로 수정 완료

### 기타 웹사이트 고도화
- 서비스 소개 정확도 검토 (대표님 피드백: "다르게 소개된 부분 있음")
- 빠진 기능 추가
- 실제 스크린샷으로 placeholder 교체
- connect.html 사전등록 페이지 신규
- header.js 메뉴 업데이트 (연결 서비스)

### 백엔드/프론트 (기존)
- 법령진단 → 자동일정 → 배정 → 알림 파이프라인 연결
- menu-tadmin.js sector 필터링
- safe.taieng.co.kr 대시보드
- 알림 발송 확인 (메세지미 연결 완료이나 발송 0건)

---

## 커밋 목록 (taieng 레포)

| 파일 | 내용 |
|------|------|
| docs/workorder-website-rebuild-v5.md | 웹사이트 리빌드 기획서 |
| docs/session-2026-04-14-planning.md | 세션 기록 (초기) |
| docs/TAI_가격체계_제안서_v3.0.md | 가격체계 제안서 (최종) |
| docs/workorder-pricing-backend.md | 백엔드 작업지시서 |
| docs/workorder-pricing-frontend.md | 프론트 작업지시서 |
| docs/workorder-pricing-html-rebuild.md | pricing.html 전면 재작성 지시서 |

## 커밋 목록 (tai-admin 레포)

| 파일 | 내용 |
|------|------|
| docs/session-2026-04-14-summary.md | 세션 요약 (초기) |
