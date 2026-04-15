# TAI Fix 프론트엔드 작업지시서 (v2)

**작성일:** 2026-04-15  
**방식:** 단계별 진행 — 각 단계 완료 확인 후 다음 단계로 이동  
**이전 버전:** workorder-provider-register-frontend.md (v1) — 보증금/전자계약 흐름 반영 전

---

## TAI Fix 전체 플로우 (확정)

페이지 2개가 필요합니다:

### 페이지 A: 업체 등록 (provider-register.html) — 공급자용
```
업체 정보 입력 → 자격/인력 등록 → 서비스 선택 → 등록 완료
```

### 페이지 B: 서비스 요청 (fix-request.html) — 발주자용 (이번 작업에서 새로 생성)
```
증상/상황 입력 → 서비스 분류 결과 표시 → 요청 접수 완료
```

---

## 파트 A: 업체 등록 페이지 고도화

### 단계 A-1: Step 1 — 주소검색 API 연동

**프롬프트:**
```
nexas/provider-register.html을 읽어주세요.
Step 1(기본정보)의 "주소" 입력 필드만 수정합니다.

현재: 단순 text input
변경: 주소 검색 + 드롭다운 선택 + GPS 좌표 저장

동작:
1. 사용자가 주소 입력 (2글자 이상)
2. GET https://api.taieng.co.kr/juso/search?query=입력값 호출
3. 결과 목록을 드롭다운으로 표시 (도로명주소 + 우편번호)
4. 선택 시:
   - road_address를 주소 필드에 표시
   - adm_cd, rn_mgt_sn, udrt_yn, buld_mnnm, buld_slno 저장
   - GET /juso/coord?admCd=...&rnMgtSn=...&udrtYn=...&buldMnnm=...&buldSlno=... 호출
   - lat, lng를 전역 변수에 저장

UI: 기존 .qual-search 스타일과 동일한 패턴.
【절대금지】 카카오 API 사용금지. /juso/search API만 사용.
이 단계에서는 Step 1의 주소 필드만 수정. 다른 것 안 건들임.
main 브랜치 커밋.
```

**완료 조건:** 주소 검색 드롭다운 동작, GPS 좌표 저장

---

### 단계 A-2: Step 2 — 인허가/인력 탭 분리

**프롬프트:**
```
nexas/provider-register.html의 Step 2(보유자격)만 수정.

현재: 하나의 검색창에 면허/등록/자격증/역량이 섹여 있음
변경: Bootstrap nav-tabs로 탭 2개 분리

탭 1: "보유 인허가" — LICENSE, REGISTRATION, CAPABILITY만 필터
  - 검색 → 선택 → 칩 표시 (인원수 없음, 있다/없다)

탭 2: "보유 인력" — CERT만 필터
  - 검색 → 선택 → 몇명 입력 → 칩 표시

기존 색상 구분 유지 (LICENSE=파란, REGISTRATION=노란, CERT=초록, CAPABILITY=회색).
selectedQuals 객체는 기존과 동일하게 유지.
이 단계에서는 Step 2만 수정. 다른 것 안 건들임.
main 브랜치 커밋.
```

**완료 조건:** 탭 분리 동작, 각 탭에서 검색/선택/칩 정상

---

### 단계 A-3: Step 4 — 완료 페이지

**프롬프트:**
```
nexas/provider-register.html의 submitForm()과 Step 4만 수정.

현재: alert() 후 아무것도 안 함
변경:

1. submitForm()에서 API 호출:
   POST https://api.taieng.co.kr/connect/providers
   body: 기존 data 객체 + latitude, longitude

2. 성공 시 form-wrap + step-bar 숨기고 완료 페이지 표시:
   - 체크 아이콘 (크게, 초록색)
   - "업체 등록 신청이 완료되었습니다" (큰 글씨)
   - "축하합니다! TAI의 전문 파트너로 등록되었습니다."
   - "초기 파트너 100개사 선착순 특별 혜택:"
     - ✅ 연결 수수료 3개월 면제
     - ✅ 우선 매칭 배치
     - ✅ 업체 프로필 상위 노출
   - "TAI에서 자격 확인 후 연락드리겠습니다. (영업일 기준 1~2일)"
   - 버튼: "홈으로 돌아가기" → index.html

3. 실패 시 에러 메시지 표시 (alert 아니고 인라인)

이 단계에서는 submitForm()과 Step 4만 수정. 다른 것 안 건들임.
main 브랜치 커밋.
```

**완료 조건:** API 호출 + 완료 페이지 표시

---

## 파트 B: 서비스 요청 페이지 (신규)

### 단계 B-1: fix-request.html 기본 구조 생성

**프롬프트:**
```
nexas/fix-request.html을 새로 만들어주세요.
provider-register.html과 동일한 헤더/푸터/CSS 구조 사용.

3단계 폼:

Step 1: 현장 정보
  - 업체명 (회사명)
  - 현장 주소 (주소검색 API 연동 — provider-register와 동일 방식)
  - 담당자 연락처 (이름, 핸드폰, 이메일)
  - 시설 유형 (건물/공장/건설현장 선택)

Step 2: 상황 입력
  - 대분류 선택 (8개 탭 — 전기/소방/기계설비/...)
  - 증상/상황 설명 (textarea, 필수)
  - 긴급도 선택 (긴급/보통/여유있음)
  - 사진 첨부 (선택, 최대 5장)
  - 예상 예산 (선택 — "모르겠음" 옵션 포함)

Step 3: 요청 확인 + 접수
  - 입력 정보 요약
  - "요청 접수" 버튼
  - 성공 시 완료 페이지:
    "요청이 접수되었습니다"
    "TAI가 적합한 전문 업체를 매칭하고 있습니다"
    "매칭된 업체의 견적서가 도착하면 알림을 보내드립니다"
    "예상 소요시간: 1~2영업일"

API 호출:
  POST https://api.taieng.co.kr/matching/requests
  body: { 현장정보 + 상황정보 }
  → 이 API는 아직 없을 수 있으므로, 없으면 console.log로 TODO 마킹

이 단계에서는 fix-request.html 한 파일만 생성. 다른 기존 파일 안 건들임.
main 브랜치 커밋.
```

**완료 조건:** fix-request.html 생성 + 3단계 폼 동작

---

## 파트 C: 통합 테스트

### 단계 C-1: 업체 등록 테스트

**프롬프트:**
```
https://new.taieng.co.kr/provider-register.html 열고:

1. Step 1: 회사명 입력, 주소 검색("테헤란로") → 드롭다운 확인 → 선택
2. Step 2: 인허가 탭에서 "전기공사" 검색→선택. 인력 탭에서 "전기기사" 검색→선택→3명
3. Step 3: 전기 탭 → 전기점검/진단 체크. 지역: 서울, 경기
4. Step 4: 요약 확인 → 등록 버튼 → 완료 페이지 확인
5. DB 확인: fix_providers + qualifications + services에 데이터 저장 여부

문제 있으면 보고, 없으면 "업체등록 테스트 완료"
```

### 단계 C-2: 서비스 요청 테스트

**프롬프트:**
```
https://new.taieng.co.kr/fix-request.html 열고:

1. Step 1: 회사명, 주소 검색, 담당자 정보 입력
2. Step 2: 전기 탭 선택, "분전반에서 타는 냄새가 난다" 입력, 긴급 선택
3. Step 3: 요약 확인 → 요청 접수 → 완료 페이지 확인

문제 있으면 보고, 없으면 "서비스요청 테스트 완료"
```

---

## 참고: API 응답 구조

### 주소 검색
```
GET /juso/search?query=테헤란로
→ { success, data: [{ road_address, zip_code, building_name, adm_cd, rn_mgt_sn, udrt_yn, buld_mnnm, buld_slno }] }

GET /juso/coord?admCd=...&rnMgtSn=...&udrtYn=...&buldMnnm=...&buldSlno=...
→ { success, data: { lat, lng } }
```

### 업체 등록
```
POST /connect/providers
body: { company_name, phone, email, address, latitude, longitude,
        service_regions, qualifications, services }
→ { success, data: { provider_id } }
```

### 서비스 요청
```
POST /matching/requests
body: { company_name, address, contact_name, contact_phone,
        facility_type, category_code, description, urgency, budget_min, budget_max }
→ { success, data: { request_id } }
```
