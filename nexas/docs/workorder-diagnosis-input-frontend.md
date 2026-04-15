# 법령진단 입력 폼 — 프론트엔드 작업지시서

**작성일:** 2026-04-15  
**방식:** 단계별 진행  

---

## 배경

백엔드 API `GET /diagnosis/fields?sector=BUILDING&tier=PAID`로 입력항목을 조회하고,
프론트에서 동적으로 폼을 생성하는 구조.

## 가격 체계 (확정)

| 섹터 | FREE | 유료 |
|---|---|---|
| 소형건물 (<5,000㎡) | 0원 | 99,000원 |
| 대형건물 (≥5,000㎡) | 0원 | 249,000원 |
| 제조·산업 | 0원 | 79K / 149K / 249K |
| 건설현장 | 0원 | 199,000원 |

---

## 단계 1: 진단 입력 페이지 기본 구조 생성

**프롬프트:**
```
현재 safe.taieng.co.kr의 진단 입력 페이지가 어디에 있는지 확인해주세요.
tai-admin 리포에서 아래 파일들을 검색:
- my-diagnosis.html
- diagnosis 관련 페이지

현재 어떤 섹터의 입력 폼이 있고, 어떤 게 없는지 파악.
수정하지 말고 현황만 파악.
```

**완료 조건:** 현재 진단 폼 현황 파악

---

## 단계 2: 섹터 선택 화면

**프롬프트:**
```
진단 시작 화면을 수정합니다.
사용자가 섹터를 선택하는 단계.

4개 섹터 카드:

1. 소형건물
   아이콘: 🏠
   설명: "5,000㎡ 미만 건물"
   가격: "무료 진단 / 유료 99,000원"

2. 대형건물
   아이콘: 🏢
   설명: "5,000㎡ 이상 건물"
   가격: "무료 진단 / 유료 249,000원"

3. 제조·산업
   아이콘: 🏭
   설명: "공장, 제조업"
   가격: "무료 진단 / 유료 79,000원~"

4. 건설현장
   아이콘: 🏗
   설명: "건설 공사 현장"
   가격: "무료 진단 / 유료 199,000원"

선택 시 localStorage에 diagnosis_sector 저장.
이 단계에서는 섹터 선택 화면만 수정.
```

**완료 조건:** 4개 섹터 카드 표시, 선택 동작

---

## 단계 3: FREE 진단 입력 폼 (동적 생성)

**프롬프트:**
```
섹터 선택 후 FREE 진단 입력 폼을 만듭니다.

API 호출:
GET https://api.taieng.co.kr/diagnosis/fields?sector={sector}&tier=FREE

응답의 groups 배열을 순회하며 동적으로 폼 생성:

- field_type별 입력 컨트롤:
  number → <input type="number"> + unit 표시
  boolean → 토글 스위치 (Yes/No)
  select → <select> (input_options에서 옵션)
  text → <input type="text">
  multi_select → 체크박스 그룹

- is_required=true → 필수 표시 (*)
- help_text → 입력 필드 아래 도움말
- placeholder → input placeholder
- auto_source='building_register' → 주소 입력 후 자동 채움 (이후 구현)

각 그룹은 접을 수 있는 섹션으로 표시.
입력값은 전역 객체에 { field_code: value } 형태로 저장.

FREE 진단 결과는 즉시 표시 (기존 로직 유지).
"더 정확한 진단을 원하시면 유료 진단을 이용하세요" CTA 버튼.

이 단계에서는 FREE 폼만 구현.
```

**완료 조건:** API에서 필드 읽어와서 동적 폼 생성, 입력값 수집

---

## 단계 4: 유료 진단 입력 폼 + 결제 연동

**프롬프트:**
```
FREE 진단 결과 화면에서 "유료 진단" CTA 클릭 시.

산업 섹터일 경우: 등급 선택 화면 표시
  베이직 (79K) - "회사 + 위험물 전체"
  스탠다드 (149K) - "베이직 + 공정 입력"
  프리미엄 (249K) - "스탠다드 + 설비 입력"

건물/건설은 등급 선택 없이 바로 진행.
건물의 경우 FREE 단계에서 입력한 연면적으로 자동 판단:
  GET /diagnosis/pricing?sector=BUILDING&total_floor_area={value}
  → 99K or 249K 표시

등급 선택/확인 후:
  API로 해당 tier의 입력항목 조회
  GET /diagnosis/fields?sector={sector}&tier={tier}
  동적 폼 생성 (단계 3과 동일 로직)
  FREE에서 이미 입력한 항목은 자동 채움 (중복 입력 방지)

입력 완료 후 결제 버튼 (이니시스 연동 — 기존 payment 흐름).
결제 완료 후 진단 실행 + 결과 표시.

이 단계에서는 유료 진단 폼 + 결제 연동만 구현.
```

**완료 조건:** 유료 진단 폼 + 결제 동작

---

## 단계 5: 건축물대장 자동 조회 연동

**프롬프트:**
```
건물 섹터에서 주소 입력 시 건축물대장 API를 자동 호출하여
연면적, 층수, 용도, 건축연도를 자동 채움.

auto_source='building_register'인 필드를 찾아서:

1. 주소 입력 후 /juso/search API로 주소 선택
2. 선택된 주소로 /building-register/search API 호출
3. 반환된 데이터로 자동 채움:
   total_floor_area → 연면적
   floor_count → 지상 층수
   basement_count → 지하 층수
   building_use_type → 용도
   built_year → 건축연도
   main_structure → 주구조

4. 연면적 자동 채움 후 가격 자동 판단:
   "연면적 8,200㎡ → 대형건물 (249,000원)" 안내 표시

5. 건축연도 2009년 이전 → "석면 사용 가능성" 자동 경고

이 단계에서는 건축물대장 연동만 구현.
건축물대장 API가 없으면 수동 입력 펴백으로 처리.
```

**완료 조건:** 주소 입력 → 건축물대장 자동조회 → 자동채움 + 가격판단

---

## 단계 6: 통합 테스트

**프롬프트:**
```
전체 흐름 테스트.

테스트 1: 건물 FREE
  섹터 선택(소형건물) → 주소 입력 → 건축물대장 자동조회
  → 근로자수 입력 → 진단 실행 → 결과 표시

테스트 2: 건물 PAID
  FREE 결과에서 "유료 진단" CTA → 추가 항목 입력 (36필드)
  → 결제 → 진단 실행 → 상세 결과

테스트 3: 산업 PAID2
  섹터 선택(제조) → FREE 진단 → 유료 → 스탠다드(149K) 선택
  → PAID1+PAID2 필드 표시 → 입력 → 결제 → 결과

테스트 4: 건설 PAID
  섹터 선택(건설) → FREE(공사금액+인원) → 유료(199K)
  → 24필드 입력 → 결제 → 결과

문제 있으면 보고, 없으면 "통합 테스트 완료"
```

---

## 참고: API 응답 구조

### 입력항목 조회
```
GET /diagnosis/fields?sector=BUILDING&tier=PAID
응답:
{
  "success": true,
  "data": {
    "sector": "BUILDING",
    "tier": "PAID",
    "field_count": 36,
    "groups": [
      {
        "group": "건축물대장",
        "fields": [
          {
            "field_code": "total_floor_area",
            "field_name": "연면적",
            "field_type": "number",
            "unit": "㎡",
            "is_required": true,
            "auto_source": "building_register"
          }
        ]
      }
    ]
  }
}
```

### 가격 판단
```
GET /diagnosis/pricing?sector=BUILDING&total_floor_area=8000
응답:
{
  "success": true,
  "data": {
    "sector": "BUILDING",
    "determined_type": "BUILDING_LARGE_V2",
    "label": "대형건물 (5,000㎡ 이상)",
    "paid_fee": 249000
  }
}
```
