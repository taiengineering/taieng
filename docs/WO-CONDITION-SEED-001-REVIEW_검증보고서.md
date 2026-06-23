# WO-CONDITION-SEED-001-REVIEW
# 초기 매핑 후보 검증 보고서

**작성일:** 2026-06-23 | **상태:** 검증 완료 / INSERT 미실행

---

## 검증 방식

실제 조문 텍스트(condition_text + action_text)를 직접 읽으면서 판단. 키워드 카운트 알고리즘에 의존하지 않음.

---

## 표 1: input_field별 분류 결과

| input_field | CONFIRMED | PENDING | PENDING_REVIEW | EXCLUDED | 합계 |
|---|---|---|---|---|---|
| has_tower_crane | 5 | 1 | 0 | 0 | 6 |
| has_boiler | 4 | 0 | 1 | 0 | 5 |
| has_diving | 14 | 5 | 2 | 0 | 21 |
| has_confined_space | 16 | 1 | 0 | 2 | 19 |
| has_blasting | 2 | 2 | 1 | 1 | 5 |
| has_high_pressure_gas | 5 | 3 | 5 | 2 | 15 |
| has_asbestos_demo | 7 | 5 | 0 | 6+4 | 22 |
| has_chemical_substance | 22 | 21 | 7 | 13 | 63 |
| **합계** | **75** | **38** | **16** | **28** | **156** |

**Phase 1 즉시 INSERT 대상: 53건 (has_chemical 제외 CONFIRMED)**
**Phase 2 PENDING INSERT: 38건 (review_status = PENDING)**
**제외 확정: 28건**

---

## 표 2: 즉시 INSERT 가능 후보 (Phase 1, 53건)

### has_tower_crane (5건)

| id | article_no | condition_code | 판단 근거 |
|---|---|---|---|
| 33d69d53 | 142 | EQUIPMENT_ACT:TOWER_CRANE:WALL_SUPPORT:33d6 | 타워크레인 자립고 이상시 벽체 지지. 조문 직결. |
| c408f352 | 142 | EQUIPMENT_ACT:TOWER_CRANE:WIRE_SUPPORT:c408 | 와이어로프 지지 준수사항. 조문 직결. |
| a9f6fa5d | 142 | EQUIPMENT_ACT:TOWER_CRANE:WALL_RULE:a9f6 | 벽체 지지 준수사항. 조문 직결. |
| d8116029 | 146 | WORK_ACT:TOWER_CRANE:SIGNAL:d811 | 타워크레인 사용 시 신호 담당자 배치. |
| c52ff010 | 37 | WORK_ACT:TOWER_CRANE:WIND_STOP:c52f | 순간풍속 10m/s 초과 시 작업중지. |

### has_boiler (4건)

| id | article_no | condition_code | 판단 근거 |
|---|---|---|---|
| 82e50bae | 116 | EQUIPMENT_ACT:BOILER:PRESSURE_RELIEF:82e5 | 보일러 압력방출장치 설치. 보일러 명시. |
| eeea64f4 | 117 | EQUIPMENT_ACT:BOILER:PRESSURE_SWITCH:eeea | 압력제한스위치 부착. 보일러 과열 방지. |
| c66b92fd | 118 | EQUIPMENT_ACT:BOILER:WATER_LEVEL:c66b | 고저수위 조절장치 경보등 설치. |
| c2e1dc40 | 119 | EQUIPMENT_ACT:BOILER:SAFETY_DEVICE:c2e1 | 보일러 폭발 예방 안전장치 관리. |

### has_diving (14건)

| id | article_no | condition_code |
|---|---|---|
| 474c9071 | 527 | EQUIPMENT_ACT:DIVING:PRESSURE_GAUGE:474c |
| 1abd72cf | 530 | EQUIPMENT_ACT:DIVING:RESERVE_GAS:1abd |
| 3838fa4d | 530 | EQUIPMENT_ACT:DIVING:AIR_TANK:3838 |
| 1eca7124 | 531 | EQUIPMENT_ACT:DIVING:PRESSURE_REG:1eca |
| abcd4d86 | 536 | WORK_ACT:DIVING:RECORD:abcd |
| fa285099 | 537 | WORK_ACT:DIVING:ASCENT_SPEED:fa28 |
| bcecae24 | 538 | WORK_ACT:DIVING:ACCIDENT:bcec |
| 084b909b | 544 | EQUIPMENT_ACT:DIVING:AIRFLOW:084b |
| ab50ff11 | 545 | WORK_ACT:DIVING:EMERGENCY_GAS:ab50 |
| b5af8758 | 545 | WORK_ACT:DIVING:SCUBA_PAIR:b5af |
| 66838d23 | 545 | WORK_ACT:DIVING:SCUBA_MONITOR:6683 |
| 320e20df | 547 | WORK_ACT:DIVING:SURFACE_MONITOR:320e |
| 85487f01 | 548 | WORK_ACT:DIVING:MARKER:8548 |
| 72465823 | 557 | WORK_ACT:DIVING:TIME_LIMIT:7246 |

*94857d8f(527조) PENDING_REVIEW: "고압작업자에게 가압이나 감압" 조건 — has_diving과 has_high_pressure_gas 공유. COMPOUND 처리 필요.*

### has_confined_space (16건)

| id | article_no | condition_code |
|---|---|---|
| 60f27afe | 619 | WORK_ACT:CONFINED_SPACE:PROGRAM:60f2 |
| bb6c51ab | 619 | WORK_ACT:CONFINED_SPACE:MEASURE:bb6c |
| 16f2fa60 | 619 | WORK_ACT:CONFINED_SPACE:AIRMASK:16f2 |
| 1567425d | 620 | WORK_ACT:CONFINED_SPACE:VENTILATION:1567 |
| b9f91548 | 621 | WORK_ACT:CONFINED_SPACE:HEADCOUNT:b9f9 |
| 2b88b62c | 622 | WORK_ACT:CONFINED_SPACE:RESTRICT:2b88 |
| 55de2aa4 | 622 | WORK_ACT:CONFINED_SPACE:SIGN:55de |
| 570a62ad | 624 | WORK_ACT:CONFINED_SPACE:FALL_PPE:570a |
| f1581a3d | 625 | WORK_ACT:CONFINED_SPACE:RESCUE_EQUIP:f158 |
| d4a06d16 | 626 | WORK_ACT:CONFINED_SPACE:MONITOR:d4a0 |
| ec332781 | 634 | WORK_ACT:CONFINED_SPACE:GAS_PIPE:ec33 |
| be2ce618 | 635 | WORK_ACT:CONFINED_SPACE:GAS_STOP:be2c |
| 474e9d61 | 636 | WORK_ACT:CONFINED_SPACE:AIROUT:474e |
| 6087c90c | 636 | WORK_ACT:CONFINED_SPACE:PIPE_SEAL:6087 |
| 4e59b845 | 639 | WORK_ACT:CONFINED_SPACE:EVAC:4e59 |
| 95aad783 | 641 | WORK_ACT:CONFINED_SPACE:INFORM:95aa |

### has_blasting (2건)

| id | condition_code |
|---|---|
| 6c64375e | WORK_ACT:BLASTING:SHELTER:6c64 |
| ac72a9f8 | FACILITY_ACT:BLASTING:LIGHTNING:ac72 |

### has_high_pressure_gas (5건)

| id | condition_code | applicable_sectors |
|---|---|---|
| 5d06396e | EQUIPMENT_ACT:PRESSURE_VESSEL:MARK:5d06 | ['INDUSTRIAL','CONSTRUCTION'] |
| 84a5df88 | EQUIPMENT_ACT:PRESSURE_VESSEL:COVER:84a5 | ['INDUSTRIAL','CONSTRUCTION'] |
| 5acf0b31 | WORK_ACT:HIGH_PRESSURE:CAISSON_LOWER:5acf | ['CONSTRUCTION'] |
| 3dc7e7d7 | FACILITY_ACT:HIGH_PRESSURE:COMPRESSOR_TEMP:3dc7 | ['CONSTRUCTION'] |
| 66e34ca9 | WORK_ACT:HIGH_PRESSURE:PILE_DRIVER:66e3 | ['CONSTRUCTION'] |

### has_asbestos_demo (7건)

| id | article_no | condition_code |
|---|---|---|
| 629726e5 | 489 | WORK_ACT:ASBESTOS:PLAN:6297 |
| 58164c96 | 489 | WORK_ACT:ASBESTOS:INFORM:5816 |
| 0fcf7b23 | 491 | WORK_ACT:ASBESTOS:PPE:0fcf |
| 34544e20 | 492 | WORK_ACT:ASBESTOS:RESTRICT_ENTRY:3454 |
| 54c965d4 | 493 | WORK_ACT:ASBESTOS:NO_SMOKING:54c9 |
| 9c3e6725 | 494 | WORK_ACT:ASBESTOS:HYGIENE:9c3e |
| caa138ea | 495 | WORK_ACT:ASBESTOS:METHOD:caa1 |

---

## 표 3: 사람 검토 필요 후보 (PENDING 38건 요약)

### has_chemical_substance PENDING (21건)

**A그룹 — APPLY에서 바로 INSERT 가능 (condition_text 명확):**

| id | article_no | 핵심 의무 |
|---|---|---|
| ba0ce664 | 422 | 실내작업장 국소배기장치 설치 |
| a7a547ae | 430 | 전체환기장치 배풍기 위치 |
| 3b470472 | 436 | 취급설비 작업수칙 수립 |
| aba6acd0 | 437 | 탱크 내부 작업 조치 |
| d8ab2a24 | 438 | 작업중지 시 출입금지 |
| a88ddcf3 | 434 | 누출 대비 약제·기구 구비 |
| dd47d6b8 | 434 | 100리터 이상 취급 경보설비 |
| 0c7463b5 | 449 | 작업배치 전 고지 |
| bbdeb5bc | 443 | 운반·저장 시 누출없는 용기 |
| 69dbb384 | 451 | 피부자극성 취급 시 보호복 |
| e4ef63d5 | 451 | 피부·눈 노출 우려 시 세척시설 |

**B그룹 — condition_text NULL, action_text 의미 판단 필요 (10건):**

| id | article_no | action_text 요약 | 의미 판단 |
|---|---|---|---|
| f805f7ed | 431 | 바닥 불침투성 재료 | 취급작업장 설비요건. 적절. |
| f857f0f1 | 432 | 부식방지 재료 | 취급설비 요건. 적절. |
| 9e1d8bd0 | 433 | 접합부 개스킷 | 누출방지. 적절. |
| f869ce8a | 435 | 밀폐식 구조 | 물질 방출장치. 적절. |
| ff53478c | 435 | 이상화학반응 방지장치 | 안전장치. 적절. |
| 66160e36 | 443 | 지정장소 저장 | 적절. |
| 02d6287a | 444 | 용기·포장 밀폐 보관 | 적절. |
| 336270b5 | 445 | 오염제거 청소 | 적절. |
| 5fc66433 | 446 | 관계외 출입 금지 | 적절. |
| 12b0c775 | 447 | 금연·음식물 섭취 금지 | 적절. |

**→ B그룹 판단: condition_text가 NULL이지만 action_text가 명확하고 has_chemical_substance=true 전제에서 항상 적용되는 의무. APPLY에서 INSERT 권장.**

### has_chemical_substance PENDING_REVIEW (7건)

허가대상 유해물질 관련 22건 중 오탐 아닌 것들:

| id | article_no | 의무 요약 | 판단 |
|---|---|---|---|
| f56138b4 | 460 | 허가대상 제조·사용 시 국소배기장치 | PENDING — 허가대상 별도 has_* 필요 가능 |
| b7af5999 | 461 | 허가대상 운반·저장 시 용기 | PENDING — 동일 |
| e3b8905c | 455 | 허가대상 오염물 배출 처리 | PENDING_REVIEW |
| 418513b4 | 464 | 허가대상 제조·사용 시 탈의실 | PENDING_REVIEW |
| 55899d77 | 469 | 허가대상 제조·사용 시 | PENDING_REVIEW |
| 5b87f264 | 470 | 허가대상 피부장해 유발 취급 | PENDING_REVIEW |
| fb35958a | 467 | 허가대상 시료채취 | PENDING_REVIEW |

**→ 허가대상 유해물질은 별도 has_permitted_hazmat 입력필드가 생기면 분리 가능. 현재는 has_chemical_substance에 PENDING으로 포함.**

### has_asbestos_demo PENDING (5건)

| id | article_no | 의무 요약 | 판단 |
|---|---|---|---|
| 3aefa4b2 | 487 | 노후화 석면분진 노출 우려 시 제거 | has_asbestos_demo 아닌 유지보수 맥락. PENDING_REVIEW |
| b7c79047 | 487 | 안정화 | 동일 |
| c340ac72 | 487 | 다른 자재로 대체 | 동일 |
| cd643912 | 497 | 석면 1% 이상 폐기물 처리 시 | 해체작업 후속조치. PENDING 유지. |
| e4bf77b6 | 497 | 국소배기장치 설치 | 동일. |

### has_blasting PENDING (2건)

| id | 판단 |
|---|---|
| a8341d62 | 발파작업 종사자 준수사항. action_text만 있음. APPLY에서 INSERT. |
| ac28a13d | 고압작업실 내 발파. COMPOUND — has_high_pressure_gas 연관. PENDING_REVIEW로 변경. |

### has_high_pressure_gas PENDING (3건)

| id | 판단 |
|---|---|
| e2f65944 | 잠함 내 굴착 금지 조건. has_high_pressure_gas와 연관 있으나 잠함 전용. PENDING. |
| 3dc7e7d7 | 이미 CONFIRMED로 이동 |
| 5d06396e | 이미 CONFIRMED로 이동 |

---

## 표 4: 제외 권고 (28건)

### 단편조각 제외 기준 (스택 패턴)

다음 중 하나에 해당하면 제외:
1. action_text = "착용하도록 하여야 한다" 단편
2. action_text = "포장을 하여야 한다" 단편
3. condition_text = "그 장소" / "이 경우" / "이를 사용하는 경우" 단편
4. 석면·베릴륨 제외 허가대상 유해물질 조문 (별도 분류 필요)
5. 조문 주제가 has_* 필드와 명백히 불일치

| id | article_no | 제외 사유 |
|---|---|---|
| 027d0122 | 153 | 리프트 피트 청소 = 밀폐공간 아님. 승강기 낙하방지. |
| 5f760824 | 301 | 전기위험 방지 조문. 밀폐공간 산소결핍과 무관. |
| 3dc9e223 | 채석장 | 채석장 특수조문. has_blasting 해당 안됨. |
| a8adc58a | 잠함 | 잠함굴착 전용. has_high_pressure_gas 아님. |
| 88c1c8f0 | 잠함 | 동일. |
| cf00582a | 453 | 허가대상(베릴륨·석면 제외). 타겟 없는 별도충만 단편. |
| 481a8141 | 453 | 동일. action_text 단편. |
| 426dc9b9 | 462 | 동일. |
| f68bb511 | 462 | action_text "알려야 한다" 단편. |
| c97b62c1 | 461 | action_text "단단하게 포장" 단편. |
| 75c666c5 | 461 | 동일. |
| 5862efa6 | 464 | action_text "용품과 용구" 단편. |
| c6ace8f5 | 464 | condition_text "이 경우" 단편. |
| 2b9f2076 | 465 | condition_text "이를 사용하는 경우" 단편. |
| d54cbe8b | 451 | action_text "착용하도록" 단편. |
| 833abbd2 | 510 | 동일. |
| db028a8c | 511 | 동일. |
| 834fd2f3 | 448 | action_text "용품과 용구" 단편. |
| a0b617e8 | 457 | condition_text "그 장소" 단편. |
| 7f701027 | 446 | 동일. |
| dd464a43 | 505 | action_text "표지 부착" 단편. |
| 17eaf15d | 629 | 보일러+밀폐공간 복합. has_boiler 제외, has_confined_space PENDING_REVIEW로 이동. |
| 3aefa4b2 | 487 | 석면 노후화 유지보수. has_asbestos_demo 해당 안됨. |
| b7c79047 | 487 | 동일. |
| c340ac72 | 487 | 동일. |
| 9423d115 | 438 | condition_text NULL + 중독 우려 시 즉시 중지. 상위 조문 맥락에 의존. |
| a3034be2 | 457 | action_text "제조하거나" 단편. |
| 3b86023d | 458 | 동일. |

---

## 중복 검증 결과

**semantic_clause_id 중복 확인:**
- 80135fef, 3cba36fb, 6edd3dd8: has_diving + has_high_pressure_gas 양쪽에 걸림. COMPOUND로 처리 예정 (별도 condition_code 부여, 양쪽 input_field에 각각 INSERT).
- 17eaf15d: has_boiler + has_confined_space. has_boiler에서 제외, has_confined_space PENDING_REVIEW.

**condition_code 충돌:** 없음. UUID 4자리 suffix로 고유성 보장.

---

## 최종 판단: APPLY 진행 권고

| 항목 | 건수 |
|---|---|
| Phase 1 즉시 INSERT (has_chemical 제외 CONFIRMED) | 53건 |
| Phase 2 INSERT (has_chemical PENDING) | 21건 |
| 총 1차 INSERT 대상 | **74건** |
| PENDING_REVIEW (별도 WO) | 16건 |
| EXCLUDED | 28건 |

**74건 기준 오탐률 목표: 0%** (EXCLUDED 제거, 단편조각 제거 완료)

---

*WO-CONDITION-SEED-001-REVIEW 완료. 승인 후 WO-CONDITION-SEED-001-APPLY 진행.*
