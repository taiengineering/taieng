# TAI Fix 업체등록 페이지 고도화 — 프론트엔드 작업지시서

**작성일:** 2026-04-15  
**대상 파일:** `nexas/provider-register.html`  
**방식:** 단계별 진행 — 각 단계 완료 확인 후 다음 단계로 이동

---

## 배경

현재 `nexas/provider-register.html`이 4단계 폼으로 존재.
아래 수정사항을 단계별로 적용합니다.

---

## 단계 1: Step 1 — 주소검색 API 연동

**프롬프트:**
```
nexas/provider-register.html을 읽어주세요.
Step 1(기본정보)의 "주소" 입력 필드를 수정합니다.

현재: 단순 text input
변경: 주소 검색 기능 추가

동작:
1. 사용자가 주소 입력 (2글자 이상)
2. GET https://api.taieng.co.kr/juso/search?query=입력값 호출
3. 결과 목록을 드롭다운으로 표시
4. 사용자가 선택하면:
   - road_address를 주소 필드에 표시
   - 선택된 주소의 adm_cd, rn_mgt_sn, udrt_yn, buld_mnnm, buld_slno를 저장
   - GET https://api.taieng.co.kr/juso/coord?admCd=...&rnMgtSn=...&udrtYn=...&buldMnnm=...&buldSlno=... 호출
   - 반환된 lat, lng를 전역 변수에 저장 (submitForm에서 사용)

UI 스타일:
- 기존 .qual-search, .qual-dropdown 스타일과 동일한 패턴
- 드롭다운 항목: 도로명주소 + 우편번호

【절대금지】 카카오 API 사용금지. 주소검색은 백엔드 /juso/search API만 사용.

이 단계에서는 Step 1의 주소 필드만 수정합니다.
다른 필드는 건드리지 않습니다.
main 브랜치에 커밋.
```

**완료 조건:** 주소 검색 드롭다운 동작, GPS 좌표 저장

---

## 단계 2: Step 2 — 인허가/인력 탭 분리

**프롬프트:**
```
nexas/provider-register.html의 Step 2(보유자격)를 수정합니다.

현재: 하나의 검색창에 면허/등록/자격증/역량이 맨어 있음
변경: 탭 2개로 분리

탭 1: "보유 인허가" (면허/등록/역량 — 회사 레벨)
  - 검색 → 선택 → 칩 표시
  - headcount 입력 없음 (있다/없다)
  - qual_type이 LICENSE, REGISTRATION, CAPABILITY인 것만 필터

탭 2: "보유 인력" (자격증 — 사람 레벨)
  - 검색 → 선택 → 몇명 입력 → 칩 표시
  - qual_type이 CERT인 것만 필터
  - headcount 입력 필수

UI:
- Bootstrap 탭 (nav-tabs) 사용
- 각 탭에 별도 검색창과 칩 영역
- 기존 색상 구분 유지 (LICENSE=파란, REGISTRATION=노란, CERT=초록, CAPABILITY=회색)

selectedQuals 객체는 기존과 동일하게 유지 (탭이 달라도 하나의 객체에 저장).
이 단계에서는 Step 2만 수정합니다.
main 브랜치에 커밋.
```

**완료 조건:** 인허가/인력 탭 분리 동작, 각 탭에서 검색/선택/칩 정상

---

## 단계 3: Step 4 — 완료 페이지 (알맿 → 페이지 전환)

**프롬프트:**
```
nexas/provider-register.html의 submitForm() 함수와 Step 4 영역을 수정합니다.

현재: alert('업체 등록 신청이 완료되었습니다.') 후 아무것도 안 함
변경: 폼 영역을 숨기고 완료 페이지를 표시

동작:
1. submitForm()에서 현재 console.log 대신 실제 API 호출:
   POST https://api.taieng.co.kr/connect/providers
   body: 기존 data 객체 + latitude, longitude 추가
2. 성공 시 form-wrap 영역을 숨기고, step-bar도 숨기고
3. 완료 페이지 표시:

완료 페이지 내용:
- 체크 아이콘 (크게, 초록색)
- "업체 등록 신청이 완료되었습니다" (큰 글씨)
- "축하합니다! [company_name]님"
- "축하합니다! TAI의 전문 파트너로 등록되었습니다."
- "초기 파트너 100개사 선착순 특별 혜택:"
  - "✅ 연결 수수료 3개월 면제"
  - "✅ 우선 매칭 배치"
  - "✅ 업체 프로필 상위 노출"
- "TAI에서 자격 확인 후 연락드리겠습니다. (영업일 기준 1~2일)"
- 버튼: "홈으로 돌아가기" → index.html로 이동

이 단계에서는 Step 4와 submitForm()만 수정합니다.
main 브랜치에 커밋.
```

**완료 조건:** API 호출 + 완료 페이지 표시, 알맿 없음

---

## 단계 4: 전체 통합 테스트

**프롬프트:**
```
nexas/provider-register.html을 브라우저에서 테스트해주세요.

https://new.taieng.co.kr/provider-register.html 열고:

1. Step 1: 회사명 입력, 주소 검색("테헤란로") → 드롭다운 확인 → 선택
2. Step 2: 인허가 탭에서 "전기공사" 검색 → 선택. 인력 탭에서 "전기기사" 검색 → 선택 → 3명 입력
3. Step 3: 전기 탭 → 전기점검/진단 체크. 지역: 서울, 경기 선택
4. Step 4: 요약 확인 → 등록 버튼 클릭 → 완료 페이지 표시 확인
5. DB 확인: fix_providers, fix_provider_qualifications, fix_provider_services에 데이터 저장 여부

문제가 있으면 보고, 없으면 "통합 테스트 완료"라고 합니다.
```

**완료 조건:** 전체 흐름 정상 동작 확인

---

## 참고: 주소 검색 API 응답 구조

```
GET /juso/search?query=테헤란로
응답:
{
  "success": true,
  "data": [
    {
      "road_address": "서울특별시 강남구 테헤란로 152",
      "jibun_address": "서울특별시 강남구 역삼동 735",
      "zip_code": "06236",
      "building_name": "강남파이난스센터",
      "sido": "서울특별시",
      "sigungu": "강남구",
      "adm_cd": "1168010100",
      "rn_mgt_sn": "116804163348",
      "udrt_yn": "0",
      "buld_mnnm": "152",
      "buld_slno": "0"
    },
    ...
  ],
  "count": 10
}

GET /juso/coord?admCd=1168010100&rnMgtSn=116804163348&udrtYn=0&buldMnnm=152&buldSlno=0
응답:
{
  "success": true,
  "data": { "lat": 37.5013, "lng": 127.0397 }
}
```

## 참고: 업체 등록 API

```
POST /connect/providers
요청:
{
  "company_name": "대성전기종합안전",
  "business_number": "123-45-67890",
  "representative": "홍길동",
  "phone": "02-1234-5678",
  "email": "info@company.co.kr",
  "address": "서울특별시 강남구 테헤란로 152",
  "latitude": 37.5013,
  "longitude": 127.0397,
  "established_year": 2010,
  "employee_count": 15,
  "service_regions": ["서울", "경기"],
  "qualifications": [
    {"qualification_id": 1, "headcount": 1},
    {"qualification_id": 4, "headcount": 3}
  ],
  "services": [
    {"subcategory_id": 1},
    {"subcategory_id": 4}
  ]
}

응답:
{
  "success": true,
  "data": { "provider_id": "uuid-..." }
}
```
