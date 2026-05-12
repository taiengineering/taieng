# TAI 공공 API 활용 전략 v3.0

> 작성일: 2026-03-28 (v3.0 — 10개 API 전체 승인 완료 반영)
> 승인 기관: 공공데이터포털 (data.go.kr)
> 저장소: taiengineering/tai-admin

---

## 0. API 승인 현황 (2026-03-28 기준)

| # | API명 | 승인 | 만료 | 계정 |
|---|-------|------|------|------|
| 1 | 한국산업안전보건공단_물질안전보건자료(MSDS) | ✅ 2026-03-28 | 2028-03-28 | 개발 |
| 2 | 한국산업안전보건공단_안전보건법령 스마트검색 | ✅ 2026-03-28 | 2028-03-28 | 개발 |
| 3 | 한국산업안전보건공단_건설업 일별 중대재해 현황 | ✅ 2026-03-28 | 2028-03-28 | 개발 |
| 4 | 한국산업안전보건공단_안전보건자료 링크 서비스 | ✅ 2026-03-28 | 2028-03-28 | 개발 |
| 5 | 한국산업안전보건공단_국내재해사례 게시판 조회 | ✅ 2026-03-28 | 2028-03-28 | 개발 |
| 6 | 한국산업안전보건공단_기술지원규정(코샤가이드) | ✅ 2026-03-28 | 2028-03-28 | 개발 |
| 7 | 국세청_사업자등록정보 진위확인 및 상태조회 | ✅ 2026-03-28 | - | 개발 |
| 8 | 소방청_국가 위험물 정보 조회 | ✅ 2026-03-18 | 2028-03-18 | 개발 |
| 9 | 행정안전부_안전정보 통합공개 조회 | ✅ 2026-03-18 | 2028-03-18 | 개발 |
| 10 | 국토교통부_건축HUB_건축물대장정보 | ✅ 2026-03-18 | 2028-03-18 | **운영** (이미 연동) |

> 🎯 **10개 전체 승인 완료** — 즉시 개발 시작 가능

---

## 1. TAI 시스템 기존 자산 (중복 구축 방지)

| 자산 | 현황 | 비고 |
|------|------|------|
| law_article (조문 DB) | **36,913건** | 법령 원문 이미 보유 ✅ |
| law_master | **409개** 법령 | |
| KOSHA GUIDE 공정 데이터 | **357개** 공정 DB 반영 | process_equipment_map |
| 건축물대장 API | **연동 완료** (운영) | building_register.py |
| 법령엔진 룰 | **396개 룰** | legal_engine v2.0.0 |
| 설비-공정 매핑 | **1,187,745건** | v_equipment_unified |
| LAW_API_OC | **이미 발급** (taieng) | 법제처 법령검색 |
| BUILDING_API_KEY | **이미 발급** | 건축물대장 |

---

## 2. 공공 API 10종 — 활용 전략 (v3 최종)

---

### #1. MSDS (물질안전보건자료)

| 항목 | 내용 |
|------|------|
| **API** | 한국산업안전보건공단_물질안전보건자료(MSDS) 조회 서비스 |
| **승인** | ✅ 2026-03-28 ~ 2028-03-28 |
| **핵심 활용** | 화학물질 취급 시설 → 물질 유해정보 자동조회 → 법령룰 정확도 향상 |

**고도화 활용 (3종):**

1. **법령엔진 정확도 향상 (핵심)**
   - 시설 설문 시 취급 화학물질 입력 → MSDS API 조회
   - 지정수량 초과 여부 자동 계산 → 유해화학물질 관련 룰(산안법 제104조 등) 자동 트리거
   - 현재 수동 적용 불가인 화학물질 조건 룰 20~30개 활성화 가능

2. **위험성평가 자동화**
   - 취급 물질 MSDS → 유해·위험요인 자동 분류 → 위험성평가 보고서 초안 생성
   - TAI Care 서비스 컨설팅 기초 자료 활용

3. **교육관리 연동**
   - 취급 화학물질 기반 필수 교육 과목 자동 추출
   - "특수건강검진 대상 물질" 자동 감지 → 건강검진 일정 알림

**백엔드 개발 명세:**
```
router: routers/msds_api.py
endpoints:
  GET  /msds/search?query={화학물질명}       → KOSHA MSDS API 프록시
  POST /msds/factory/{id}/analyze            → 시설 취급물질 분석 → 법령룰 연동
  GET  /msds/material/{cas_no}               → CAS 번호 기반 단건 조회
DB: factory_materials 테이블 신규
  (factory_id, cas_no, material_name, quantity, unit, unit_code)
env: MSDS_API_KEY (Railway 추가 필요)
```

**우선순위: 🟡 2~4주**

---

### #2. 법령 스마트검색 (안전보건법령)

| 항목 | 내용 |
|------|------|
| **API** | 한국산업안전보건공단_안전보건법령 스마트검색 |
| **승인** | ✅ 2026-03-28 ~ 2028-03-28 |
| **핵심 활용** | 판정 결과 각 룰 옆 "조문 원문 보기" 버튼 |

**⚠️ 중요: law_article 36,913건 이미 DB 보유**
→ 외부 API 실시간 호출 불필요, DB 내 조회로 충분
→ KOSHA 법령 API는 산업안전보건법 특화 조문 보완 및 개정 감지에 활용

**고도화 활용 (3종):**

1. **법령진단 결과 UI — [조문 원문 보기] 버튼 (즉시)**
   - factory-list.html 탭5 각 룰 카드 옆 버튼 추가
   - law_article DB 조회 → 조문 원문 모달 표시 (외부 API 불필요)

2. **KOSHA 특화 법령 보완**
   - KOSHA API로 산업안전보건 관련 최신 조문 보완
   - law_article DB에 없는 고시·예규·훈령 보충

3. **법령 개정 감지 알림**
   - KOSHA 법령 API로 월 1회 개정 여부 확인
   - 개정 시 관련 룰 플래그 → 어드민 알림 + 고객 이메일

**백엔드 개발 명세:**
```
기존 law_article 테이블 활용 (즉시):
  GET /laws/{law_id}/articles              → DB 조회
배치 (월 1회):
  POST /admin/law-sync                     → KOSHA API → DB 비교 → 개정 감지
프론트:
  factory-list.html 탭5 → [조문 보기] 버튼
env: KOSHA_LAW_API_KEY (Railway 추가 필요)
```

**우선순위: 🔴 즉시** (DB 이미 있음, 버튼만 추가)

---

### #3. 건설업 일별 중대재해 현황

| 항목 | 내용 |
|------|------|
| **API** | 한국산업안전보건공단_건설업 일별 중대재해 현황 |
| **승인** | ✅ 2026-03-28 ~ 2028-03-28 |
| **갱신 주기** | **일별(Daily)** ← 원안 맞음 ✅ |
| **핵심 활용** | 매일 자동 업데이트 → SEO + 마케팅 소재 |

> ✅ **원안 검증 완료** — "일별 중대재해 현황" API이므로 매일 업데이트 가능

**고도화 활용 (3종):**

1. **홈페이지 safety-news.html 자동 피드 (매일)**
   - 건설업 일별 중대재해 자동 파싱 → posts 테이블 저장
   - 카테고리=사고사례, SEO 콘텐츠 자동 생성

2. **대시보드 위험 지수 위젯 (실시간)**
   - 최근 7일 건설업 중대재해 발생 건수 트렌드 그래프
   - "이번 주 건설업 중대재해 ○건 발생" 실시간 표시

3. **TAI Care 영업 도구**
   - "오늘 건설업 중대재해 ○건" → 영업 담당자 알림
   - 마케팅 문구: ✅ "매일 자동 업데이트" 원안 그대로 사용 가능

**백엔드 개발 명세:**
```
배치 (매일 오전 6시):
  POST /admin/disaster-stats-sync-daily  → KOSHA API → posts 테이블
DB: posts 테이블 (이미 설계 완료)
  category='사고사례', source='KOSHA_DAILY'
  title='[날짜] 건설업 중대재해 현황', content=JSON
프론트:
  safety-news.html → 자동 피드 표시
  대시보드 위젯: GET /dashboard/disaster-stats?days=7
env: KOSHA_DISASTER_API_KEY (Railway 추가 필요)
```

**우선순위: 🟡 2~4주**

---

### #4. 안전보건자료 링크 서비스

| 항목 | 내용 |
|------|------|
| **API** | 한국산업안전보건공단_안전보건자료 링크 서비스 |
| **승인** | ✅ 2026-03-28 ~ 2028-03-28 |
| **핵심 활용** | 교육관리 모듈 — 법정교육 과목별 KOSHA 자료 자동 연결 |

> ✅ v2.0에서 "API 없음 ⚠️ URL 매핑 테이블로 대체" 판단 → **수정: 공식 API 있음**
> URL 매핑 테이블 불필요, API 직접 호출로 구현

**고도화 활용 (3종):**

1. **교육관리 모듈 — 법정교육 과목별 KOSHA 자료 연결**
   - 법정교육 과목(안전보건교육, 특수교육 등) → API 호출 → 관련 자료 목록 표시
   - "KOSHA 공식 교육자료" 배지 부여 → 신뢰성 강화

2. **설비/공정 연관 안전보건자료 제공**
   - 등록 설비 기반 → 관련 안전보건 자료 자동 추천
   - 점검 체크리스트 생성 시 자료 자동 첨부

3. **TAI Safe 서비스 가치 향상**
   - 법령진단 결과 하단 → 관련 안전보건자료 링크 자동 표시
   - 마케팅 문구: ✅ "KOSHA 공식 기술지침 자동 안내"

**백엔드 개발 명세:**
```
router: routers/kosha_api.py (통합)
endpoints:
  GET /kosha/safety-materials?keyword={키워드}  → KOSHA 자료 링크 API 프록시
  GET /kosha/safety-materials/by-education/{code} → 교육과목별 자료
DB: education_materials 테이블 신규
  (education_code, title, kosha_url, file_type, source='KOSHA_API')
env: KOSHA_MATERIALS_API_KEY (Railway 추가 필요)
```

**우선순위: 🟡 2~4주**

---

### #5. 국내 재해사례 게시판

| 항목 | 내용 |
|------|------|
| **API** | 한국산업안전보건공단_국내재해사례 게시판 정보 조회서비스 |
| **승인** | ✅ 2026-03-28 ~ 2028-03-28 |
| **핵심 활용** | 고객 업종과 유사한 재해사례 3건 자동 표시 |

**고도화 활용 (3종):**

1. **법령진단 결과 연동 (핵심)**
   - 법령 판정 후 고객 KSIC 업종 → 동일 업종 재해사례 3건 자동 표시
   - "귀사와 같은 제조업에서 이런 사고가 발생했습니다" → 경각심 + CTA
   - 위치: factory-list.html 탭5 법령진단 결과 하단

2. **홈페이지 콘텐츠 자동화**
   - safety-news.html 사고사례 탭 자동 피드
   - SEO: 업종별 사고사례 URL 자동 생성 (`/safety-news/case/제조업`)

3. **TAI Care 영업 도구**
   - 상담 시 고객 업종 재해사례 즉시 조회
   - "최근 3년 귀사 업종 중대재해 ○건, 평균 과태료 ○억원"

**백엔드 개발 명세:**
```
router: routers/kosha_api.py
endpoints:
  GET /kosha/accident-cases?ksic={code}&limit=3  → 업종별 사례 조회
  GET /kosha/accident-cases/{id}                  → 사례 상세
DB: accident_cases 테이블 신규
  (id, ksic_code, title, accident_type, year, source_url, summary)
배치 (주 1회): API 호출 → accident_cases 테이블 동기화
env: KOSHA_ACCIDENT_API_KEY (Railway 추가 필요)
```

**우선순위: 🟡 2~4주**

---

### #6. KOSHA GUIDE (기술지원규정)

| 항목 | 내용 |
|------|------|
| **API** | 한국산업안전보건공단_기술지원규정(코샤가이드) 조회 서비스 |
| **승인** | ✅ 2026-03-28 ~ 2028-03-28 |
| **핵심 활용** | 판정 결과 각 룰 옆 "기술지침 보기" 버튼 |

> ✅ v2.0에서 "API 없음 ⚠️" 판단 → **수정: 공식 API 있음**
> DB URL 매핑 불필요, API 직접 호출 가능
> 단, 이미 DB에 KOSHA GUIDE 기반 공정 데이터(357개) 보유 — 연동 강화 방향

**고도화 활용 (3종):**

1. **법령진단 결과 [기술지침 보기] 버튼 (즉시)**
   - factory-list.html 탭5 각 룰 카드 옆 버튼
   - KOSHA GUIDE API 호출 → 관련 기술지침 PDF 링크 표시
   - 기존 DB의 KOSHA GUIDE 공정과 연결 강화

2. **공정관리 KOSHA 출처 강조**
   - process-list.html → KOSHA 소스 공정 녹색 배지 + "KOSHA GUIDE 기반" 툴팁
   - 마케팅 문구: ✅ "KOSHA 공식 기술지침 자동 안내"

3. **설비 점검 기준 자동 연결**
   - 설비 자산 관리 → 해당 설비 KOSHA GUIDE 점검 기준 자동 연결
   - 점검 체크리스트 자동 생성 시 GUIDE 기준 적용

**백엔드 개발 명세:**
```
router: routers/kosha_api.py
endpoints:
  GET /kosha/guides?keyword={키워드}         → KOSHA GUIDE API 프록시
  GET /kosha/guides/{guide_no}               → GUIDE 상세 (PDF URL 포함)
  GET /kosha/guides/by-rule/{rule_code}      → 룰별 관련 GUIDE 조회
DB: kosha_guides 테이블 신규
  (guide_no, title, pdf_url, related_rule_codes, related_process_ids)
law_master: kosha_guide_no 컬럼 추가
프론트: factory-list.html 탭5 룰 카드 → [기술지침 보기] 버튼
env: KOSHA_GUIDE_API_KEY (Railway 추가 필요)
```

**우선순위: 🔴 즉시** (버튼 추가 + API 연동)

---

### #7. 국세청 사업자 상태 검증

| 항목 | 내용 |
|------|------|
| **API** | 국세청_사업자등록정보 진위확인 및 상태조회 서비스 |
| **승인** | ✅ 2026-03-28 |
| **요청 방식** | POST, JSON, 10건 이하 배치 조회 가능 |
| **핵심 활용** | 선임연결/수선중개 — 공급자 등록 시 사업자 상태 실시간 검증 |

**고도화 활용 (3종):**

1. **공급자 등록 시 실시간 검증 (핵심)**
   - apply-manager.html / apply-repair.html 폼 제출 시 자동 검증
   - POST /verify/business → 국세청 API → 정상/휴폐업 반환
   - 어드민 승인 전 자동 검증 상태 배지 표시

2. **정기 재검증 (월 1회)**
   - 등록된 공급자 사업자 상태 월 1회 자동 재검증
   - 폐업 감지 시 → 자동 비활성화 + 관리자 알림

3. **계약 전 최종 확인**
   - 선임 매칭 / 수선 계약 직전 실시간 재검증
   - "계약 시점 기준 정상 사업자 확인" 로그 저장 → 법적 증빙

**백엔드 개발 명세:**
```
router: routers/kosha_api.py 또는 routers/verify.py
endpoint:
  POST /verify/business
    body: { biz_no: "0000000000" }
    returns: { valid: bool, status: "계속사업자"|"휴업자"|"폐업자", biz_name: str }
배치 (월 1회): POST /admin/verify/suppliers → 전체 공급자 재검증
env: NTS_API_KEY (Railway 추가 필요)
```

**우선순위: 🔴 즉시**

---

### #8. 소방청 위험물 정보

| 항목 | 내용 |
|------|------|
| **API** | 소방청_국가 위험물 정보 조회 서비스 |
| **승인** | ✅ 2026-03-18 ~ 2028-03-18 |
| **핵심 활용** | 위험물 지정수량 자동계산 → 선임의무 판정 |

**고도화 활용 (2종):**

1. **법령엔진 정확도 향상 (핵심)**
   - 시설 설문 시 취급 위험물 종류·수량 입력
   - 소방청 API로 지정수량 자동 조회 + 배수 계산 (실제 수량 / 지정수량)
   - 배수 > 1 → 위험물안전관리자 선임의무 룰 자동 트리거
   - 현재 수동 적용 불가인 위험물 룰 5~10개 자동화

2. **MSDS와 통합 위험 분석**
   - MSDS(#1) + 소방청 위험물 → 통합 화학물질 위험도 분석
   - 위험성평가 보고서 자동 초안 (TAI Care 서비스 강화)

**백엔드 개발 명세:**
```
router: routers/kosha_api.py
endpoints:
  GET  /dangerous-goods?type={위험물분류}    → 소방청 API 프록시
  POST /dangerous-goods/calculate
    body: { materials: [{type, quantity, unit}] }
    returns: { total_ratio: float, requires_manager: bool, applicable_rules: [] }
DB: dangerous_goods_master 테이블
  (type_code, name, designated_quantity, unit, hazard_grade)
env: FIRE_HAZMAT_API_KEY (Railway 추가 필요)
```

**우선순위: 🟢 1~2개월**

---

### #9. 행정안전부 안전정보 통합공개

| 항목 | 내용 |
|------|------|
| **API** | 행정안전부_안전정보 통합공개 조회 서비스 |
| **승인** | ✅ 2026-03-18 ~ 2028-03-18 |
| **데이터** | 시군구별 5개 분야 안전등급 (교통사고/화재/범죄/생활안전/자살) |
| **핵심 활용** | 시설 위치 기반 지역 안전정보 표시 |

**고도화 활용 (2종):**

1. **대시보드 위젯 — 지역 안전등급 표시**
   - 시설 주소(시군구) → 행안부 안전등급 조회
   - 탑 5개 시설 안전등급 지도 표시
   - "인천 남동구 화재 안전등급 3등급" → TAI Care 상담 CTA

2. **시설 등록 시 자동 리스크 사전 경고**
   - 시설 주소 입력 → 해당 지역 안전등급 즉시 표시
   - 등급 낮을수록 강화된 법령 준수 권고 메시지

**백엔드 개발 명세:**
```
router: routers/kosha_api.py
endpoints:
  GET /region-safety?sigungu_code={code}  → 시군구 안전등급
  GET /region-safety/factory/{id}         → 시설 위치 기반 안전등급
DB: region_safety_index 테이블 (연 1회 갱신)
  (sigungu_code, sigungu_name, fire_grade, traffic_grade, crime_grade, updated_at)
배치 (연 1회): 전체 교체
env: REGION_SAFETY_API_KEY (Railway 추가 필요)
프론트: 대시보드 위젯 추가 (tadmin index.html)
```

**우선순위: 🟡 2~4주**

---

### #10. 건축물대장 (이미 연동 완료)

| 항목 | 내용 |
|------|------|
| **API** | 국토교통부_건축HUB_건축물대장정보 서비스 |
| **승인** | ✅ **운영 계정** (2026-03-18 ~ 2028-03-18) |
| **현재 상태** | **이미 연동 완료** — building_register.py, BUILDING_API_KEY 발급 |

**추가 활용 방안 (3종):**

1. **층별개요 → 복합시설 층별 법령 적용 (백엔드 기획 반영)**
   - 건축물대장 층별개요 → 각 층 용도 자동 파악
   - 복합 건축물에서 층별 법령 적용 구분
   - 예: 1층 판매 + 3층 사무소 → 각 층별 다른 법령 세트 적용

2. **주용도코드 기반 KSIC 자동 추천**
   - 연면적/용도/층수 자동 입력 (현재 구현) → 주용도코드 기반 KSIC 추천 자동화

3. **건축물 노후도 리스크 분석**
   - 사용승인일 → 건물 연령 계산 → 노후 시설 안전 경고
   - TAI Care Pro 연결: "건물 築30년 이상 — 정밀안전진단 권고"

**우선순위: 🟢 1~2개월**

---

## 3. 우선순위별 개발 로드맵

### 🔴 즉시 (이번 주)

| # | 작업 | 담당 | 기대효과 |
|---|------|------|----------|
| 1 | `routers/kosha_api.py` 신규 생성 + 7개 엔드포인트 뼈대 | 백엔드 | API 통합 허브 |
| 2 | `POST /verify/business` 국세청 사업자 검증 구현 | 백엔드 | 공급자 신뢰성 |
| 3 | factory-list.html 탭5 룰 카드 → [조문 보기] 버튼 | 프론트 | law_article DB 활용 |
| 4 | factory-list.html 탭5 룰 카드 → [기술지침 보기] 버튼 | 프론트 | KOSHA GUIDE 활용 |

### 🟡 2~4주

| # | 작업 | 담당 | 기대효과 |
|---|------|------|----------|
| 5 | 건설업 일별 중대재해 배치 → safety-news.html 자동 피드 | 백엔드+프론트 | 매일 자동 콘텐츠 |
| 6 | 재해사례 API → 법령진단 결과 하단 표시 | 백엔드+프론트 | 고객 전환율 향상 |
| 7 | 안전보건자료 링크 API → 교육관리 모듈 연결 | 백엔드+프론트 | 교육관리 완성도 |
| 8 | 대시보드 위젯 3개 (재해율/지역안전등급/재해사례) | 프론트 | 대시보드 가치 향상 |
| 9 | 국세청 월 1회 공급자 자동 재검증 배치 | 백엔드 | 공급자 신뢰성 유지 |

### 🟢 1~2개월

| # | 작업 | 담당 | 기대효과 |
|---|------|------|----------|
| 10 | MSDS API 연동 → 화학물질 법령 룰 자동화 | 백엔드 | 룰 20~30개 추가 활성화 |
| 11 | 소방청 위험물 계산 → 위험물 선임 룰 자동화 | 백엔드 | 룰 5~10개 추가 활성화 |
| 12 | 건축물대장 층별개요 → 복합시설 층별 법령 적용 | 백엔드 | 진단 정확도 최상위 |

---

## 4. 서비스별 연동 구조 (최종 확정)

| # | API | 연동 서비스 | 핵심 활용 | 우선순위 |
|---|-----|-----------|----------|----------|
| 1 | MSDS | 법령진단 + TAI Care | 화학물질 → 룰 자동화 | 🟢 |
| 2 | 안전보건법령 스마트검색 | 법령진단 + 어드민 | [조문 보기] 버튼 | 🔴 |
| 3 | 건설업 일별 중대재해 | 홈페이지 + 대시보드 | 매일 자동 피드 + 위젯 | 🟡 |
| 4 | 안전보건자료 링크 | 교육관리 | 교육 과목별 자료 연결 | 🟡 |
| 5 | 국내 재해사례 | 법령진단 + 홈페이지 | 업종별 사례 3건 자동 표시 | 🟡 |
| 6 | KOSHA GUIDE | 법령진단 | [기술지침 보기] 버튼 | 🔴 |
| 7 | 국세청 사업자 | 선임연결 + 수선중개 | 공급자 등록/재검증 | 🔴 |
| 8 | 소방청 위험물 | 법령진단 | 위험물 선임 룰 자동화 | 🟢 |
| 9 | 행안부 안전정보 | 대시보드 | 지역별 안전등급 위젯 | 🟡 |
| 10 | 건축물대장 (완료) | 시설등록 | 층별개요 → 복합시설 법령 | 🟢 |

---

## 5. 마케팅 활용 문구 (최종 확정)

```
✅ "국가 공식 데이터 10종 연동"
   → 근거: KOSHA(6개), 국세청, 소방청, 행안부, 국토부 10개 API 승인 완료
   → 즉시 사용 가능 ✅

✅ "국세청 실시간 검증 플랫폼"
   → 근거: POST /verify/business 구현 후 사용 가능
   → 이번 주 구현 후 사용 ✅

✅ "KOSHA 공식 기술지침 자동 안내"
   → 근거: KOSHA GUIDE API 승인 완료 + [기술지침 보기] 버튼
   → 이번 주 구현 후 사용 ✅

✅ "중대재해처벌법 원문 즉시 확인"
   → 근거: law_article 36,913건 DB 보유 + 안전보건법령 API
   → 즉시 구현 후 사용 ✅

✅ "매일 자동 업데이트" (원안 복원)
   → 근거: 건설업 일별 중대재해 현황 API (일별 갱신 확인)
   → 2~4주 구현 후 사용 ✅
```

---

## 6. 신규 DB 테이블 목록

| 테이블명 | 용도 | 우선순위 |
|----------|------|----------|
| `factory_materials` | 시설별 취급 화학물질 (MSDS) | 🟢 |
| `accident_cases` | 재해사례 | 🟡 |
| `education_materials` | KOSHA 안전보건자료 링크 | 🟡 |
| `kosha_guides` | KOSHA GUIDE 매핑 | 🔴 |
| `dangerous_goods_master` | 위험물 지정수량 기준표 | 🟢 |
| `region_safety_index` | 지역안전지수 | 🟡 |

---

## 7. 환경변수 추가 목록

| 변수명 | 용도 | 상태 |
|--------|------|------|
| `LAW_API_OC` | 법제처 법령검색 | ✅ 이미 발급 (taieng) |
| `BUILDING_API_KEY` | 건축물대장 | ✅ 이미 발급 |
| `NTS_API_KEY` | 국세청 사업자 검증 | 🔴 즉시 추가 필요 |
| `KOSHA_LAW_API_KEY` | 안전보건법령 스마트검색 | 🔴 추가 필요 |
| `KOSHA_GUIDE_API_KEY` | KOSHA GUIDE 조회 | 🔴 추가 필요 |
| `KOSHA_DISASTER_API_KEY` | 건설업 일별 중대재해 | 🟡 추가 필요 |
| `KOSHA_ACCIDENT_API_KEY` | 국내 재해사례 | 🟡 추가 필요 |
| `KOSHA_MATERIALS_API_KEY` | 안전보건자료 링크 | 🟡 추가 필요 |
| `MSDS_API_KEY` | MSDS 조회 | 🟢 추가 필요 |
| `FIRE_HAZMAT_API_KEY` | 소방청 위험물 | 🟢 추가 필요 |
| `REGION_SAFETY_API_KEY` | 행안부 안전정보 | 🟡 추가 필요 |

> 📌 공공데이터포털 마이페이지 → 각 API 인증키 확인 후 Railway 환경변수에 추가

---

## 8. kosha_api.py 엔드포인트 전체 구성

```python
# routers/kosha_api.py — 공공API 통합 라우터 (신규 생성)

# 국세청 사업자 검증 🔴
POST /verify/business

# KOSHA GUIDE 🔴
GET  /kosha/guides
GET  /kosha/guides/{guide_no}
GET  /kosha/guides/by-rule/{rule_code}

# 재해사례 🟡
GET  /kosha/accident-cases
GET  /kosha/accident-cases/{id}

# 안전보건자료 링크 🟡
GET  /kosha/safety-materials
GET  /kosha/safety-materials/by-education/{code}

# 건설업 중대재해 (배치) 🟡
POST /admin/disaster-stats-sync-daily

# 지역안전지수 🟡
GET  /region-safety
GET  /region-safety/factory/{id}

# MSDS 🟢
GET  /msds/search
POST /msds/factory/{id}/analyze

# 소방청 위험물 🟢
GET  /dangerous-goods
POST /dangerous-goods/calculate

# 배치 작업
POST /admin/law-sync              (월 1회)
POST /admin/verify/suppliers      (월 1회)
```

---

## 9. v2 → v3 변경사항 요약

| 항목 | v2.0 판단 | v3.0 수정 (실제) |
|------|----------|----------------|
| 건설업 중대재해 갱신 | ⚠️ 월 1회만 가능 → "최신 통계 자동 반영"으로 수정 | ✅ **일별 API 존재** → "매일 자동 업데이트" 원안 복원 |
| 안전보건자료 링크 API | ⚠️ API 없음 → URL 매핑 테이블로 대체 | ✅ **공식 API 있음** → 직접 연동으로 변경 |
| KOSHA GUIDE API | ⚠️ API 없음 → URL 매핑 테이블로 대체 | ✅ **공식 API 있음** → 직접 연동으로 변경 |
| 소방청 위험물 | ✅ 부분 확인 | ✅ **승인 완료 확인** |
| 행안부 안전정보 | ✅ 실제 존재 | ✅ **승인 완료 확인** |
| 모든 API 승인 상태 | 일부 미확인 | ✅ **10개 전체 승인 완료** |
