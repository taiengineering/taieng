# WO-THRESHOLD-QUALITY-002 — THRESHOLD 고도화 사이클 메모

작성: 2026-06-30 | 갱신: 2026-06-30 (모집단 정정 + 매핑 목적 명시)
상위: 17차 고정판 + WO-ARCHITECTURE-FREEZE-001
Boundary Check: Applicability 내부=YES / Boundary=NO / Contract=NO / Breaking=NO → 일반작업
**목적: 매핑 — 소비자 수치 입력값 ↔ 법령 수치 임계 의무 연결.**
방식: 맞는 건 매핑, 안 맞는 건 **메모 후 패스**(다른 소스 변경 없이 역할 한도 내). 문제는 나중에 모아 분석·수정.
검증: 조문 원문(semantic_clause.action_text) 글읽기 대조. 건수/목업 판단 금지.

---

## ★ THRESHOLD 진짜 모집단 = 소비자 수치 입력값 (diagnosis_input_fields, field_type='number')
**정정: "3건"은 특정 목업 사업장(280명) 발화 결과일 뿐. THRESHOLD 대상은 소비자가 입력하는 수치값 전체다.**
소비자 수치 입력값 = 판단 기준값 중 수치. 이것이 수치 임계(THRESHOLD)의 모집단. 중복제거 약 15종:

| field_code | 이름 | 섹터 |
|---|---|---|
| worker_count | 상시근로자 수 / 동시투입 인원 | BLD·CON·IND |
| total_floor_area | 연면적 | BLD·IND |
| floor_count | 지상 층수 | BLD |
| building_grade | 건물 등급 | BLD |
| water_tank_ton | 저수조 용량 | BLD |
| elevator_count | 승강기 대수 | BLD·IND |
| gas_capacity_kg | 가스 저장용량(kg) | BLD·IND |
| gas_capacity_m3 | 가스 저장용량(m³) | BLD |
| boiler_capacity_kw | 보일러 용량 | BLD |
| electric_capacity | 수전용량 | BLD·IND |
| transformer_capacity_kva | 변압기 용량 | BLD |
| annual_energy_toe | 연간 에너지 사용량 | BLD·IND |
| project_amount | 총 공사금액 | CON |
| subcontractor_count | 하도급 업체 수 | CON |

→ 현재 발화되는 THRESHOLD는 worker_count 1종에서 나온 3건뿐. 나머지 13종(연면적·층수·가스·수전·변압기·공사금액·저수조·보일러·승강기·에너지 등)은 **법령 수치 임계 의무가 있어야 하나 현재 THRESHOLD 미발화.** 이 15종 ↔ 법령 임계 의무 매핑이 THRESHOLD 고도화 본체.

---

## worker_count 사이클 결과 (원문 대조 1~3)

### 사이클 1 — 제17조 안전관리자 (clause 04f98e27)
- 원문: "…상시근로자 수, …선임방법은 **별표 3과 같다**." content_type=**DELEGATION**, executor="관계수급인"(오염)
- [안맞음·메모] executor 오염 / 임계가 별표3인데 위임문장에 걸림(별표 미추적). **패스.**

### 사이클 2 — 제19조 안전보건관리담당자 (clause 2f0efa7a)
- 원문: "…**사업주**는 …상시근로자 **20명 이상 50명 미만**…선임해야 한다." content_type=OBLIGATION ✓
- [맞음] 하한 20 = 원문 일치.
- [안맞음·메모] executor="해당하"(오염) / 상한 "50미만" 미반영 → 280명 과생성. **패스.**

### 사이클 3 — 제22조 산업보건의 (clause f876f02f)
- 원문: "…50명 이상인 사업장으로 한다." content_type=**DEFINITION**, executor="사업장"(오염)
- [맞음] 임계 50 = 원문 일치.
- [안맞음·메모] content=DEFINITION / 전제조건(보건관리자 대상) 미반영. **패스.**

---

## 문제 분류 (메모 후 패스 — 전부 GPT/승인 영역, 임의수정 불가)
- **A. executor 오염 3/3** ("관계수급인"·"해당하"·"사업장" → 실제 사업주). 의미추출(GPT).
- **B. content_type OBLIGATION 아님 2/3** (DELEGATION·DEFINITION). 의미추출(GPT).
- **C. 범위조건 미처리** (제19조 상한 50미만 → 과생성). 판정로직(GPT).
- **D. 별표(APPENDIX) 임계 미추적** (제17조). THRESHOLD 저발화 근본원인. 6/25 "별표 확장 병목" 일치.

---

## 다음 진행 = 매핑
소비자 수치 입력값 15종 각각을 **법령 수치 임계 의무와 매핑**한다.
- 방식: 입력값 1종 → 그 수치가 임계로 등장하는 법령 조문(원문) 대조 → 맞으면 매핑 기록, 안 맞으면 메모 후 패스 → 다음 입력값.
- 맞는 것 먼저. worker_count는 사이클 완료(문제 메모됨). 다음 입력값부터 매핑 진행.
