# TAI 15차 개발 핸드오프 (2026-06) — GPT 작성

> 출처: GPT 핸드오프 (대표 전달, 2026-06-11). 원문 보존.
> 지위: 작업 방식 전환의 기준 문서. fable v4(법령엔진 재개발 16차 시도)는 폐기하고 본 문서의 방식으로 복귀.

## 가장 중요한 결론

15차 개발의 목적은 레이어 객체화, 계약 표준화, 엔진 분해가 아니다.

목적은 다음 하나였다.

**소비자가 입력한 정보가 실제 법령진단 결과에 반영되는가?**

레이어 분해와 계약 정리는 이를 조사하기 위한 도구였다.

---

## 절대 잊지 말 것 — 반복된 실패 패턴

결과가 이상함 → 특정 모듈 의심 → 수정 → 다른 곳 문제 발견 → 또 수정 → 루프

15차에서 얻은 가장 큰 교훈:

**부분을 보면 반드시 루프에 빠진다.**

- Carrier만 보면 Carrier 문제처럼 보인다.
- Rule만 보면 Rule 문제처럼 보인다.
- Engine만 보면 Engine 문제처럼 보인다.

반드시 **Consumer Input → Final Result** 전체 흐름으로 관찰해야 한다.

---

## 15차에서 실제 확인된 것 (Root Cause 분류)

### ENGINE BUG — 존재하나 주원인 아님
- ADR-005 UNKNOWN → 0 default
- Track B debt 일부

### CARRIER GAP — 대량 발견, 실제 주요 원인
- IC-02
- KSIC projection 누락
- Building Use 연결 누락
- Construction Risk projection 누락

### INPUT GAP — 다수 발견
- API ksic_major
- 굴착/밀폐 입력 부재
- 건설 위험 입력 누락

### RULE GAP — 일부, 단 Carrier 복구 이후에만 관찰 가능
### SCHEMA GAP — 일부 (has_tunnel_bridge, has_high_work)

---

## 15차에서 완료된 것

### 구조 (분해 완료)
Input Layer / Applicability Layer / Compiler Layer / Output Layer / Engine Contract Stack

### Contract (정의 완료)
InputContract / LegalContract / CheckResultContract / CompilerPackage /
RefineryAssemblyResult / StoredDiagnosisResult

### Carrier Repair (완료)
GAP-001 KSIC / GAP-002 Building Use / GAP-003 Construction Risk

### Root Cause Classification (분류 체계 확립)
ENGINE BUG / CARRIER GAP / INPUT GAP / RULE GAP / SCHEMA GAP / EXPECTED

---

## 가장 중요한 실측 결과

### REALWORLD_VALIDATION_001 — KSIC
- 무KSIC → 5건 / C10·C20·C25 → 154건 / +121 의무 증가
- **입력 → 결과 반영 확인됨**

### Building Use (사무실/병원/학교/판매시설/창고) → 결과 동일
### Construction Risk (일반/터널/밀폐/발파/철거) → 결과 동일

주의: 이 결과만 보고 "Rule Data 문제다 / Engine 문제다"라고 판단하면 안 됨.

---

## RULE_SEMANTICS_AUDIT 핵심
- IF_SCOPE 513건 (equipment_type 260 / facility_type 220 / process_type 33)
- draft_value 전부 NULL
- 즉, Engine은 값 비교 가능하지만 비교할 값이 없음.
- 그러나 이것도 부분 관찰이므로 즉시 Rule Data 보강으로 가면 안 됨.

---

## 현재 단계의 관찰 방식

### 잘못된 방식
IF_SCOPE 분석 / draft_value 분석 / binding_field 분석 → 수정 → 정답 아님

### 올바른 방식
대표 사업장 입력 → 최종 결과 → 왜 이런 결과가 나왔는가? → 그때만 내부 추적

---

## 현재 검증 대상 / 특수 제외
- 검증 대상: ① 산업(제조) ② 건설 ③ 건물
- 특수(병원·학교·항만·철도·원전 등)는 격리 상태 — 현재 엔진 품질 판단 기준으로 사용 안 함.

---

## 작업 원칙 (Claude / Cursor)

지금부터는 **정적 분석 중심이 아니라 동적 관찰 중심.**

GPT 방식(문서·코드·구조 분석)은 충분히 수행됨.
다음 단계: 실행 → 관찰 → 증거 → 판단.

반드시 MCP로 실제 실행 흐름(InputContract → … → StoredDiagnosisResult)을 관찰.
추론으로 결론 내리지 말 것.

### 금지사항
다음 중 하나를 보고 바로 수정 금지:
IF_SCOPE / draft_value / binding_field / facility_type / process_type /
equipment_type / Rule Data / Engine V2

반드시 소비자 입력 → 최종 결과 관찰 후, 필요할 때만 내부 추적.

---

## 현재 판단
15차는 끝난 것이 아니다. 그러나 Carrier 중심 조사 단계는 사실상 완료.
지금부터는 Consumer Input → Final Result End-to-End 관찰 단계.

여기서 발견되는 문제가 진짜 Engine 문제인지, Rule 문제인지, Schema 문제인지 판단해야 한다.

**부분을 보면 반드시 15차 이전의 루프로 되돌아간다.**
