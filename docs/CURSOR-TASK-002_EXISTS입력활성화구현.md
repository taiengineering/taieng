# CURSOR-TASK-002
# EXISTS 입력 활성화 구현

**작성일:** 2026-06-25 | **대상:** Cursor / Claude Code (로컬 편집 → git push → Railway 배포)
**선행 명세:** docs/WO-EXISTS-ACTIVATION-SPEC-001_EXISTS입력활성화명세.md
**선행 검증:** docs/CURSOR-TASK-001_어댑터연결구현.md (함정 사례 포함)
**헌법:** docs/WO-ARCHITECTURE-FREEZE-001_프로젝트헌법.md

---

## 이 작업의 유일한 목적 (최상단 고정)

```
입력이 Generator까지 도달하도록 연결한다.

그 외 아무것도 하지 않는다.
구조를 바꾸는 방향으로 흐르면 멈추고 헌법을 다시 읽는다.
```

---

## 절대 수정 금지 (구현 전 확인)

```
① Applicability Engine 로직   (cmc / obligation_instance 생성기)
② Trigger Generator           (trigger_generator / trigger_obligation_generator)
③ Check Engine                (GPT Compiler / facility_applicability 계보)
④ Data Contract               (WO-DATA-CONTRACT-001 — 필드 추가/변경 금지)
⑤ Boundary Lock               (WO-BOUNDARY-LOCK-001 — 레이어 책임 불변)

has_*는 기존 입력표준(diagnosis_input_fields)에 이미 정의됨.
→ 새 필드/Trigger/Mapping/Harvest 생성 없음.
→ 이번 작업은 "입력 저장 경로 연결" 1개가 전부.
```

---

## Boundary Check (헌법 TASK-007)

```
Applicability 내부 작업인가?    NO  (입력단 — 입력 파이프 연결)
Boundary 변경 필요한가?         NO
Data Contract 변경 필요한가?    NO  (has_*는 기존 표준)
Breaking Change인가?            NO
→ 입력단 작업이나 경계/계약 무변경. Review 불필요.
```

---

## Scope

```
포함:
  - sector별 MVP 입력 UI 노출
  - has_* 저장
  - Input Contract Builder 연결
  - facility_profiles 입력 동기화
  - 기존 Adapter 그대로 사용

제외:
  - Trigger 수정 / cmc 수정 / Harvest 수정
  - Check Engine 수정 / Data Contract 변경 / Boundary 변경
```

---

## TASK-001: sector 선택 → MVP 질문 자동 노출

```
입력 소스: diagnosis_input_fields (field_name = 질문 문구, 이미 존재)
  WHERE field_type='boolean' AND field_code IN (sector별 MVP 세트)

[INDUSTRIAL] 7문항 (→ 약 230 의무)
  유해물질 취급        has_hazardous_material   68
  분진작업 유무        has_dust_work            37
  화학물질 취급        has_chemical_substance   32
  밀폐공간 유무        has_confined_space       26
  크레인/호이스트 유무 has_crane                25
  고소작업 유무        has_high_place_work      19  (help: 2m 이상)
  용접 공정 유무       has_welding              18

[CONSTRUCTION] 7문항 (→ 약 145 의무)
  잠수작업 유무        has_diving               27
  밀폐공간 유무        has_confined_space       26
  석면해체 유무        has_asbestos_demo        23
  굴착작업 유무        has_excavation           23
  비계 사용 유무       has_scaffold             22
  항타/항발작업 유무   has_pile_work            17
  타워크레인 유무      has_tower_crane           7

[BUILDING] 3문항 (→ 약 46 의무)
  석면 사용 여부       has_asbestos             23  (help: 건축연도 2009년 이전 자동경고)
  밀폐공간 유무        has_confined_space       16
  석면해체 유무        has_asbestos_demo         7

UX 원칙 (토스): sector 선택 후 해당 세트만 노출. 그 전엔 숨김.
```

---

## TASK-002: field_code 그대로 저장

```
저장 시 field_code를 절대 변경하지 않는다.
  has_welding → has_welding   (O)
  has_crane   → has_crane     (O)
  용접유무    → has_welding   (X — 한글명 저장 금지)

generator가 input_field로 정확히 이 field_code를 매칭한다.
→ 이름이 다르면 EXISTS 매칭 0 (살아나지 않음).
```

---

## TASK-003: 동의어 변환 (확인된 것만)

```
허용 (WO-EXISTS-INPUT-TRACE-001에서 확인된 2건만):
  has_gas       → has_high_pressure_gas
  has_hazardous → has_hazardous_material

★ 새 동의어 규칙 생성 금지.
  위 2건은 public_diagnosis_requests의 약식명 → 정식 field_code.
  그 외 필드는 이미 정식명이므로 변환 불필요.
```

---

## TASK-004: Input Contract Builder

```
Builder가 하나의 Contract로 조립 (sector + worker_count + has_*):

{
  "factory_id": "...",
  "sector": "INDUSTRIAL",       // facility_profiles
  "ksic_code": "...",
  "worker_count": 280,          // facility_profiles (THRESHOLD용)
  "has_hazardous_material": true,
  "has_welding": true,
  "has_crane": true
  // ... 입력된 has_*만 true, 나머지 false/생략
}

Applicability Engine은 Builder만 읽는다.
→ Builder가 facility_profiles + has_* 저장소를 병합.
→ 저장 위치(facility_profiles vs 별도)는 Cursor 판단.
  단 generator가 읽는 곳에 has_*가 도달해야 함 (핵심).

★ 현재 갭 (WO-DIAGNOSIS-TO-OBLIGATION-PIPELINE-001):
  facility_profiles.profile_snapshot엔 has_* 없음.
  → 이 저장 경로 연결이 이번 작업의 핵심.
```

---

## TASK-005: 실제 Factory 검증

```
테스트: factory e9c56af6 (또는 신규)
  sector: INDUSTRIAL
  worker_count: 280
  has_welding: true
  has_crane: true
  has_chemical_substance: true

기대 결과 (3종 동시 생성):
  UNIVERSAL  93   (sector=INDUSTRIAL baseline)
  THRESHOLD   3   (worker 280 ≥ 20/50 + 안전관리자)
  EXISTS     75   (welding 18 + crane 25 + chemical 32)
  ─────────────
  합계      171   (기존 96 + EXISTS 75)

★ 함정 주의 (CURSOR-TASK-001 검증에서 확인):
  - obligation_count는 candidate와 같아야 정상.
    executor 필터 없음 → 건수 감소 없음 (95→95였던 사례).
  - executor_text가 "해당하"/"사업장"인 THRESHOLD 2건은
    파싱 오류일 뿐 실제 사업주 의무 → 거르면 안 됨.
```

---

## TASK-006: Trace Log (필수)

```
입력 has_*
  ↓  [무엇이 들어왔나]
Builder
  ↓  [Contract에 has_* 몇 개 담겼나]
Applicability (generator)
  ↓  [obligation_instance 몇 건, EXISTS 몇 건]
obligation_instance
  ↓  [Glue 변환]
Glue
  ↓  [candidate 몇 건]
Adapter
  ↓  [obligations 몇 건]
Check Engine

검증 포인트:
  - 입력 has_* 개수 = Builder Contract has_* 개수 (누락 0)
  - 각 has_*=true가 대응 EXISTS 의무로 살아났는가
  - 단계별 건수 + 소요시간 기록
```

---

## 성공 기준

```
Coverage:
  현재 20.4% → EXISTS 활성 약 31%

또는 의무 수:
  상위 10개 has_* 입력 → 355개 EXISTS 의무 활성

테스트 factory:
  has_welding+crane+chemical → EXISTS 75건 생성
  UNIVERSAL+THRESHOLD+EXISTS 동시 = 171건
```

---

## 함정 체크리스트 (지난 검증 교훈)

```
□ field_code 한글 변환 안 했는가? (has_welding 그대로)
□ 동의어는 확인된 2건만? (새 규칙 안 만들었나)
□ executor "해당하"/"사업장" THRESHOLD 2건 안 걸렀나?
□ facility_profiles에 has_* 실제 저장됐나? (profile_snapshot 확인)
□ generator가 그 저장 위치를 읽나? (도달 확인)
□ PostgREST 임베디드 조인 안 되면 2-step 폴백? (FK 없음)
□ Check Engine / Adapter / cmc diff 0인가?
```

---

## Cursor 인계 요약

```
신규/수정 파일 (입력단):
  - 진단 UI: sector별 MVP has_* 노출 (diagnosis_input_fields 기반)
  - 저장 로직: has_* → facility_profiles (또는 Builder 읽는 위치)
  - Input Contract Builder: sector+worker_count+has_* 조립
    (services/obligation_instance_adapter.py 인접 or 신규)

무수정 (호출만):
  - obligation_instance_adapter (CURSOR-TASK-001 산출)
  - build_obligations_from_trigger_candidates
  - Check Engine / 정제레이어

배포:
  - main push → Railway 자동배포
  - 실제 factory 호출 → Trace Log → Claude 창에서 Coverage 재측정
```

---

## 완료 후 다음 (Claude 후속)

```
Cursor 구현·배포 완료 시:
  → Claude가 obligation_instance 증가분 DB 검증
  → WO-COVERAGE-GAP-002: EXISTS 활성 실측 Coverage 재측정
  → 20.4% → 실제 몇 %인지 baseline 갱신
```

---

*CURSOR-TASK-002. EXISTS 입력 활성화 구현 인계장.*
*유일 목적: 입력이 Generator까지 도달하도록 연결한다.*
*절대 수정 금지: Applicability/Trigger/Check Engine/Data Contract/Boundary.*
*핵심 작업: has_* 저장경로 1개 연결. 명세는 WO-EXISTS-ACTIVATION-SPEC-001 참조.*
