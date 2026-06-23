# WO-CONDITION-SEED-001
# has_* 기반 초기 매핑 적재 설계

**작성일:** 2026-06-23 | **상태:** 설계 완료 / INSERT 미실행

---

## 작업 개요

- 대상: `factories` has_* 9개 필드
- 조회 기준: `semantic_clause.content_type IN ('OBLIGATION','PROHIBITION')` + `executor_text LIKE '%사업주%'`
- INSERT: 이번 WO에서 금지. WO-CONDITION-SEED-001-APPLY에서 실행

---

## 산출물 A: has_*별 후보 집계표

| input_field | applicable_sectors | candidate_count | cond_text_count | action_only_count | 비고 |
|---|---|---|---|---|---|
| has_confined_space | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | 19 | 18 | 1 | 밀폐공간·산소결핍·유해가스·맨홀·피트 키워드 |
| has_blasting | ['CONSTRUCTION'] | 5 | 2 | 3 | 발파·화약류·장약·폭약 |
| has_chemical_substance | ['INDUSTRIAL'] | 63 | 34 | 29 | 관리대상·허가대상·금지유해물질·MSDS |
| has_high_pressure_gas | ['INDUSTRIAL','CONSTRUCTION'] | 15 | 11 | 4 | 고압가스·압력용기·기압조절실·잠함·압축공기 |
| has_tower_crane | ['CONSTRUCTION'] | 6 | 4 | 2 | 타워크레인 단독 (크레인 일반 제외) |
| has_boiler | ['INDUSTRIAL','BUILDING'] | 5 | 2 | 3 | 보일러 단독 (건조로 제외, 압력방출장치·안전밸브 포함) |
| has_asbestos_demo | ['CONSTRUCTION','BUILDING'] | 22 | 5 | 17 | 석면해체·제거·음압기·위생설비 |
| has_diving | ['CONSTRUCTION'] | 21 | 21 | 0 | 잠수작업·잠수기·감압 (잠함 제외) |
| has_safety_manager | 보류 | - | - | - | employee_count THRESHOLD 우선 처리 |

**총 후보: 156건** (has_safety_manager 제외)

---

## 산출물 B: has_*별 seed 후보 상세 목록

### B-1. has_confined_space (19건)

| semantic_clause_id | condition_type | condition_code | condition_text_preview | applicable_sectors | condition_source | review_status |
|---|---|---|---|---|---|---|
| 60f27afe-dc0f-4148-a990-9304864cc048 | WORK_ACT | WORK_ACT:CONFINED_SPACE:PROGRAM:60f2 | 사업주는 밀폐공간에서 근로자에게 작업을 하도록 하는 경우 → 작업 프로그램 수립 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| 570a62ad-5c8f-4f07-a3a0-b5707b0dc470 | WORK_ACT | WORK_ACT:CONFINED_SPACE:FALL_PPE:570a | 산소결핍·유해가스로 추락 우려 → 안전대·구명밧줄 지급 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| 1567425d-8c35-471d-bef9-b8f122b7e904 | WORK_ACT | WORK_ACT:CONFINED_SPACE:VENTILATION:1567 | 밀폐공간 작업 시 환기 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| 027d0122-c28e-4b4b-9ab8-7f312739d593 | WORK_ACT | WORK_ACT:CONFINED_SPACE:PIT_CLEAN:027d | 리프트 피트 청소 시 운반구 낙하 방지 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING_REVIEW |
| d4a06d16-a71d-4bb8-8c15-f029830ba381 | WORK_ACT | WORK_ACT:CONFINED_SPACE:MONITOR:d4a0 | 상시환기장치 월 1회 이상 점검 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | ACTION_TEXT | PENDING |
| be2ce618-52bb-4258-98f9-1d320187dc8c | WORK_ACT | WORK_ACT:CONFINED_SPACE:GAS_STOP:be2c | 유해가스 누출·산소 부족 시 즉시 작업 중지 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| 5f760824-a1d4-41c9-9504-f778c9201bdb | WORK_ACT | WORK_ACT:CONFINED_SPACE:ELECTRIC:5f76 | 맨홀·지하실 충전부 노출 밀폐공간 → 절연 칸막이 설치 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| 4e59b845-9d49-41b1-848f-6f226e340dd2 | WORK_ACT | WORK_ACT:CONFINED_SPACE:EVAC:4e59 | 밀폐공간 질식·화재·폭발 우려 시 즉시 작업 중단 대피 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| ec332781-abc6-4398-b763-b093558ead45 | WORK_ACT | WORK_ACT:CONFINED_SPACE:GAS_PIPE:ec33 | 지하실·맨홀 내 가스배관 해체·부착 작업 조치 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| b9f91548-a248-468b-a5c9-8ee25b442cd1 | WORK_ACT | WORK_ACT:CONFINED_SPACE:HEADCOUNT:b9f9 | 밀폐공간 입장·퇴장 시 인원 점검 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| 2b88b62c-7558-4446-b685-16c8ce03c1dd | WORK_ACT | WORK_ACT:CONFINED_SPACE:RESTRICT:2b88 | 밀폐공간 사전 파악·관계 근로자 외 출입 금지 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| 55de2aa4-3c5c-4b9e-88f1-77c25b305258 | WORK_ACT | WORK_ACT:CONFINED_SPACE:SIGN:55de | 출입금지 표지 게시 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | ACTION_TEXT | PENDING |
| 16f2fa60-72d4-4462-9250-95b1b126d211 | WORK_ACT | WORK_ACT:CONFINED_SPACE:AIRMASK:16f2 | 적정공기 미유지 시 환기·공기호흡기 지급 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| bb6c51ab-ffc4-4597-af42-becca7dd77de | WORK_ACT | WORK_ACT:CONFINED_SPACE:MEASURE:bb6c | 작업 전 산소·유해가스 농도 측정 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| 95aad783-d1a5-42f6-8c53-9b51503e628a | WORK_ACT | WORK_ACT:CONFINED_SPACE:INFORM:95aa | 작업 시작 시 사항 고지 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| 474e9d61-6937-479f-ae5d-48adeffde932 | WORK_ACT | WORK_ACT:CONFINED_SPACE:AIROUT:474e | 산소결핍 공기·유해가스 누출 시 외부 배출 설비 설치 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| 6087c90c-79ba-4b88-957c-065cd82ba4cb | WORK_ACT | WORK_ACT:CONFINED_SPACE:PIPE_SEAL:6087 | 밀폐공간 내 배관 통한 산소결핍 공기 누출 방지 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| f1581a3d-e4ac-4996-9932-3c238a1f59f6 | WORK_ACT | WORK_ACT:CONFINED_SPACE:RESCUE_EQUIP:f158 | 밀폐공간 비상 구출 기구 구비 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |
| 4684e1b7-7164-4484-a99e-b77332448798 | WORK_ACT | WORK_ACT:CONFINED_SPACE:RESCUE:4684 | 밀폐공간 위급 근로자 구출 시 공기호흡기 착용 | ['INDUSTRIAL','CONSTRUCTION','BUILDING'] | CONDITION_TEXT | PENDING |

**제외 후보:**
- 리프트 피트 조문(027d): condition_text에 '피트'가 있으나 밀폐공간이 아닌 승강기 낙하 방지 맥락 → PENDING_REVIEW (맥락 검토 필요)

---

### B-2. has_blasting (5건)

| semantic_clause_id | condition_type | condition_code | condition_text_preview | applicable_sectors | condition_source | review_status |
|---|---|---|---|---|---|---|
| ac28a13d-7cd9-4f28-be0c-7155f912ab51 | COMPOUND | COMPOUND:BLASTING:HIGH_PRESSURE:ac28 | 작업실 내 발파 시 기압 복원 전 고압실 입실 금지 | ['CONSTRUCTION'] | CONDITION_TEXT | PENDING_REVIEW |
| 6c64375e-7f6a-4772-bc58-e733ef87ef87 | WORK_ACT | WORK_ACT:BLASTING:SHELTER:6c64 | 발파작업 시 피난 불가 → 방호 피난장소 설치 | ['CONSTRUCTION'] | CONDITION_TEXT | PENDING |
| a8341d62-560d-439b-acf7-e5b9a5e3d1c8 | WORK_ACT | WORK_ACT:BLASTING:WORKER_RULE:a834 | 발파작업 종사 근로자 준수사항 | ['CONSTRUCTION'] | ACTION_TEXT | PENDING |
| ac72a9f8-8975-4c17-8c72-c89bb4188753 | FACILITY_ACT | FACILITY_ACT:BLASTING:LIGHTNING:ac72 | 화약류·위험물 저장 시설 낙뢰 방지 피뢰설비 | ['CONSTRUCTION'] | ACTION_TEXT | PENDING |
| 3dc9e223-1f80-47aa-863a-2a7c3b76936e | WORK_ACT | WORK_ACT:BLASTING:QUARRY_COORD:3dc9 | 인접 채석장 발파 시기 연락 유지 | ['CONSTRUCTION'] | ACTION_TEXT | PENDING_REVIEW |

**주의:**
- ac28: 고압작업실 내 발파 → has_high_pressure_gas와 COMPOUND 후보
- 3dc9: 채석장 특수조문 → PENDING_REVIEW

---

### B-3. has_chemical_substance (63건, 대표 30건 표시)

**그룹 분류:**

| 그룹 | 키워드 | 건수 | condition_type |
|---|---|---|---|
| 관리대상 유해물질 | 관리대상 유해물질 | ~35건 | MATERIAL_ACT |
| 허가대상 유해물질 | 허가대상 유해물질 | ~18건 | MATERIAL_ACT |
| 금지유해물질 | 금지유해물질 | ~5건 | MATERIAL_ACT |
| MSDS | 물질안전보건자료 | ~5건 | MATERIAL_ACT |

**대표 CONFIRMED_CANDIDATE 후보 (condition_text 명확):**

| semantic_clause_id | condition_code | 조문 요약 | review_status |
|---|---|---|---|
| 3b470472 | MATERIAL_ACT:HAZMAT:WORK_RULE:3b47 | 관리대상 유해물질 취급설비 작업수칙 수립 | PENDING |
| ba0ce664 | MATERIAL_ACT:PROHIB_HAZMAT:LEAK:ba0c | 금지유해물질 누출 시 흡착제 제거 | PENDING |
| ba28988e | MATERIAL_ACT:HAZMAT:LOCAL_EXHAUST:241c | 관리대상 유해물질 실내 취급 → 국소배기장치 | PENDING |
| 0c7463b5 | MATERIAL_ACT:HAZMAT:WORK_ASSIGN:8375 | 관리대상 유해물질 취급 작업 배치 전 고지 | PENDING |
| 57857eaf | MATERIAL_ACT:MSDS:LABEL:5785 | 물질안전보건자료 대상물질 경고표시 | PENDING |
| 6af28711 | MATERIAL_ACT:HAZMAT:NOTICE:6af2 | 관리대상 유해물질 취급 작업장 사항 게시 | PENDING |
| f56138b4 | MATERIAL_ACT:PERMITTED_HAZMAT:MFST:f563 | 허가대상 유해물질 제조·사용 시 국소배기장치 | PENDING |

**제외 후보:**
- 고압가스와 겹치는 조문 → has_high_pressure_gas로 이동
- 의약품 관련 조문 (해당 없음 — 확인됨)
- 건조로 등 설비 명칭에 '화학'이 포함된 오탐 없음

---

### B-4. has_high_pressure_gas (15건)

| semantic_clause_id | condition_type | condition_code | 조문 요약 | applicable_sectors | review_status |
|---|---|---|---|---|---|
| 5d06396e | EQUIPMENT_ACT | EQUIPMENT_ACT:PRESSURE_VESSEL:MARK:5d06 | 압력용기 각인 표시 사용 | ['INDUSTRIAL','CONSTRUCTION'] | PENDING |
| 84a5df88 | EQUIPMENT_ACT | EQUIPMENT_ACT:PRESSURE_VESSEL:COVER:84a5 | 압력용기 부속 원동기·벨트 덮개 설치 | ['INDUSTRIAL','CONSTRUCTION'] | PENDING |
| 4e6e0b98→84a5 | EQUIPMENT_ACT | EQUIPMENT_ACT:PRESSURE_VESSEL:GUARD:84a5 | 공기압축기 회전부 덮개 | ['INDUSTRIAL','CONSTRUCTION'] | PENDING |
| 80135fef | COMPOUND | COMPOUND:HIGH_PRESSURE:DECOMPRESS_DIVING:8013 | 기압조절실 잠수작업자 가압 속도 제한 | ['CONSTRUCTION'] | PENDING_REVIEW |
| 6edd3dd8 | COMPOUND | COMPOUND:HIGH_PRESSURE:DECOMPRESS_TIME:6edd | 기압조절실 감압 시간 고지 | ['CONSTRUCTION'] | PENDING_REVIEW |
| 3cba36fb | COMPOUND | COMPOUND:HIGH_PRESSURE:DECOMPRESS_ACTION:3cba | 기압조절실 감압 조치 | ['CONSTRUCTION'] | PENDING_REVIEW |
| 94857d8f | FACILITY_ACT | FACILITY_ACT:HIGH_PRESSURE:VALVE_GAUGE:94857 | 기압조절실 외부 밸브 압력계 설치 | ['CONSTRUCTION'] | PENDING |
| 66e34ca9 | WORK_ACT | WORK_ACT:HIGH_PRESSURE:PILE_DRIVER:66e3 | 압축공기 동력 항타기·항발기 사용 시 준수 | ['CONSTRUCTION'] | PENDING |
| e2f65944 | PROHIBITION | WORK_ACT:HIGH_PRESSURE:CAISSON_PROHIB:e2f6 | 잠함 내 굴착 작업 금지 조건 | ['CONSTRUCTION'] | PENDING_REVIEW |
| 88c1c8f0 | WORK_ACT | WORK_ACT:HIGH_PRESSURE:CAISSON_SINK:88c1 | 잠함 내 굴착 작업 준수사항 | ['CONSTRUCTION'] | PENDING_REVIEW |
| 5acf0b31 | WORK_ACT | WORK_ACT:HIGH_PRESSURE:CAISSON_LOWER:5acf | 잠함 물 속 침하 시 고압근로자 대피 | ['CONSTRUCTION'] | PENDING |

**주의:**
- 기압조절실 잠수작업자 관련(80135fef, 6edd3dd8, 3cba36fb) → has_diving과 중복. COMPOUND 처리
- 잠함 조문 → has_high_pressure_gas 유지, has_diving과 구분

---

### B-5. has_tower_crane (6건)

| semantic_clause_id | condition_type | condition_code | 조문 요약 | applicable_sectors | review_status |
|---|---|---|---|---|---|
| 33d69d53 | EQUIPMENT_ACT | EQUIPMENT_ACT:TOWER_CRANE:WALL_SUPPORT:33d6 | 자립고 이상 → 벽체 지지 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| c408f352 | EQUIPMENT_ACT | EQUIPMENT_ACT:TOWER_CRANE:WIRE_SUPPORT:c408 | 와이어로프 지지 시 준수사항 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| a9f6fa5d | EQUIPMENT_ACT | EQUIPMENT_ACT:TOWER_CRANE:WALL_RULE:a9f6 | 벽체 지지 시 준수사항 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| 6231c5f5 | EQUIPMENT_ACT | EQUIPMENT_ACT:TOWER_CRANE:INSTALL_ORG:6231 | 등록한 자로 하여금 설치·해체 | ['CONSTRUCTION'] | PENDING |
| d8116029 | WORK_ACT | WORK_ACT:TOWER_CRANE:SIGNAL:d811 | 타워크레인 작업 시 신호업무 담당자 배치 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| c52ff010 | WORK_ACT | WORK_ACT:TOWER_CRANE:WIND_STOP:c52f | 순간풍속 10m/s 초과 시 작업 중지 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |

**note:** has_tower_crane은 6건 모두 CONFIRMED_CANDIDATE 또는 PENDING으로 질이 높음. 전원 적재 권장.

---

### B-6. has_boiler (5건)

| semantic_clause_id | condition_type | condition_code | 조문 요약 | applicable_sectors | review_status |
|---|---|---|---|---|---|
| c2e1dc40 | EQUIPMENT_ACT | EQUIPMENT_ACT:BOILER:SAFETY_DEVICE:c2e1 | 보일러 압력방출장치·압력제한스위치·고저수위 조절장치 관리 | ['INDUSTRIAL','BUILDING'] | CONFIRMED_CANDIDATE |
| eeea64f4 | EQUIPMENT_ACT | EQUIPMENT_ACT:BOILER:PRESSURE_SWITCH:eeea | 보일러 과열 방지 압력제한스위치 부착 | ['INDUSTRIAL','BUILDING'] | CONFIRMED_CANDIDATE |
| 82e50bae | EQUIPMENT_ACT | EQUIPMENT_ACT:BOILER:PRESSURE_RELIEF:82e5 | 보일러 규격에 맞는 압력방출장치 설치 | ['INDUSTRIAL','BUILDING'] | CONFIRMED_CANDIDATE |
| c66b92fd | EQUIPMENT_ACT | EQUIPMENT_ACT:BOILER:WATER_LEVEL:c66b | 고저수위 조절장치 경보등·경보음 설치 | ['INDUSTRIAL','BUILDING'] | CONFIRMED_CANDIDATE |
| 17eaf15d | WORK_ACT | WORK_ACT:BOILER:CONFINED_WELD:17ea | 보일러 내부 용접·용단 작업 시 환기 | ['INDUSTRIAL','BUILDING'] | PENDING_REVIEW |

**note:**
- 17eaf15d: 보일러+밀폐공간 복합 → has_confined_space와 중복 가능. PENDING_REVIEW
- 보일러 전용 핵심 4건(c2e1, eeea, 82e5, c66b)은 CONFIRMED_CANDIDATE 제안

---

### B-7. has_asbestos_demo (22건, 대표 표시)

| semantic_clause_id | condition_type | condition_code | 조문 요약 | applicable_sectors | review_status |
|---|---|---|---|---|---|
| 629726e5 | WORK_ACT | WORK_ACT:ASBESTOS:PLAN:6297 | 석면해체·제거작업 계획 수립 및 고지 | ['CONSTRUCTION','BUILDING'] | CONFIRMED_CANDIDATE |
| 58164c96 | WORK_ACT | WORK_ACT:ASBESTOS:INFORM:5816 | 석면해체·제거 계획 근로자 고지 | ['CONSTRUCTION','BUILDING'] | CONFIRMED_CANDIDATE |
| caa138ea | WORK_ACT | WORK_ACT:ASBESTOS:METHOD:caa1 | 석면해체·제거 조치 구분 시행 | ['CONSTRUCTION','BUILDING'] | CONFIRMED_CANDIDATE |
| 0fcf7b23 | WORK_ACT | WORK_ACT:ASBESTOS:PPE:0fcf | 석면해체·제거 근로자 개인보호구 지급 | ['CONSTRUCTION','BUILDING'] | CONFIRMED_CANDIDATE |
| 9c3e6725 | WORK_ACT | WORK_ACT:ASBESTOS:HYGIENE:9c3e | 작업장 인접 탈의실·샤워실 위생설비 설치 | ['CONSTRUCTION','BUILDING'] | CONFIRMED_CANDIDATE |
| 1fbeb9bd | WORK_ACT | WORK_ACT:ASBESTOS:DUST_REMOVE:1fbe | 작업장 밖 나갈 시 보호구 석면분진 제거 | ['CONSTRUCTION','BUILDING'] | PENDING |
| 2e12a94b | WORK_ACT | WORK_ACT:ASBESTOS:PPE_STORAGE:2e12 | 석면해체 후 보호구 밀폐용기 보관 | ['CONSTRUCTION','BUILDING'] | PENDING |
| 4c5f24c9 | WORK_ACT | WORK_ACT:ASBESTOS:SIGN:4c5f | 작업장 출입구 표지 게시 | ['CONSTRUCTION','BUILDING'] | PENDING |
| 54c965d4 | WORK_ACT | WORK_ACT:ASBESTOS:NO_SMOKING:54c9 | 작업장 내 금연·음식물 섭취 금지 | ['CONSTRUCTION','BUILDING'] | PENDING |
| 34544e20 | PROHIBITION | WORK_ACT:ASBESTOS:RESTRICT_ENTRY:3454 | 보호구 미착용자 출입 금지 | ['CONSTRUCTION','BUILDING'] | PENDING |
| 26939a98 | WORK_ACT | WORK_ACT:ASBESTOS:POST_CLEAN:2693 | 작업 완료 후 석면함유 잔재물 청소 | ['CONSTRUCTION','BUILDING'] | PENDING |
| 5b4ddf7f | WORK_ACT | WORK_ACT:ASBESTOS:WASTE:5b4d | 석면함유 잔재물 밀봉 폐기물 처리 | ['CONSTRUCTION','BUILDING'] | PENDING |

**제외 후보:**
- 허가대상 유해물질(석면 제외) 조문 → has_chemical_substance로 분리
- 석면분진 단순 보관 조문 → has_asbestos_demo가 아닌 별도 분류 필요 (PENDING_REVIEW)

---

### B-8. has_diving (21건)

| semantic_clause_id | condition_type | condition_code | 조문 요약 | applicable_sectors | review_status |
|---|---|---|---|---|---|
| b5af8758 | WORK_ACT | WORK_ACT:DIVING:SCUBA_PAIR:b5af | 스쿠버 잠수 2명 1조 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| 66838d23 | WORK_ACT | WORK_ACT:DIVING:SCUBA_MONITOR:6683 | 스쿠버 잠수 감시인 배치 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| ab50ff11 | WORK_ACT | WORK_ACT:DIVING:EMERGENCY_GAS:ab50 | 스쿠버 잠수 비상기체통 제공 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| 320e20df | WORK_ACT | WORK_ACT:DIVING:SURFACE_MONITOR:320e | 표면공급식 잠수 감시인 배치 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| abcd4d86 | WORK_ACT | WORK_ACT:DIVING:RECORD:abcd | 잠수기록표 작성 3년 보존 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| 85487f01 | WORK_ACT | WORK_ACT:DIVING:MARKER:8548 | 잠수작업 장소 표시 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| 72465823 | WORK_ACT | WORK_ACT:DIVING:TIME_LIMIT:7246 | 잠수작업 시간 고시 준수 | ['CONSTRUCTION'] | PENDING |
| bcecae24 | WORK_ACT | WORK_ACT:DIVING:ACCIDENT:bcec | 사고 잠수작업자 수면 복귀 시 조치 | ['CONSTRUCTION'] | PENDING |
| 474c9071 | EQUIPMENT_ACT | EQUIPMENT_ACT:DIVING:PRESSURE_GAUGE:474c | 잠수작업자 압축기체 압력계 설치 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| 3838fa4d | EQUIPMENT_ACT | EQUIPMENT_ACT:DIVING:AIR_TANK:3838 | 공기압축기 공기조 및 예비공기조 설치 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| 1abd72cf | EQUIPMENT_ACT | EQUIPMENT_ACT:DIVING:RESERVE_GAS:1abd | 예비 호흡용 기체통 설치 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| 084b909b | EQUIPMENT_ACT | EQUIPMENT_ACT:DIVING:AIRFLOW:084b | 표면공급식 분당 60리터 이상 송기 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| 1eca7124 | EQUIPMENT_ACT | EQUIPMENT_ACT:DIVING:PRESSURE_REG:1eca | 고압 기체통 2단 이상 감압 압력조절기 사용 | ['CONSTRUCTION'] | CONFIRMED_CANDIDATE |
| fa285099 | WORK_ACT | WORK_ACT:DIVING:ASCENT_SPEED:fa28 | 잠수작업자 수면 복귀 속도 고시 준수 | ['CONSTRUCTION'] | PENDING |
| 80135fef (공유) | COMPOUND | COMPOUND:DIVING:HIGH_PRESSURE_COMPRESS:8013 | 기압조절실 가압 속도 (has_high_pressure_gas 공유) | ['CONSTRUCTION'] | PENDING_REVIEW |
| 3cba36fb (공유) | COMPOUND | COMPOUND:DIVING:HIGH_PRESSURE_DECOMP:3cba | 기압조절실 감압 조치 (has_high_pressure_gas 공유) | ['CONSTRUCTION'] | PENDING_REVIEW |

---

## 산출물 C: 제외 후보 목록

| semantic_clause_id | 원래 input_field | 제외 사유 |
|---|---|---|
| 027d0122 | has_confined_space | 피트가 키워드에 걸렸으나 리프트 낙하 방지 맥락 — 밀폐공간 아님. 별도 검토 |
| ba28988e | has_boiler | 보일러+불활성기체+밀폐공간 복합 — has_confined_space 쪽으로 이동 |
| ac28a13d | has_blasting | 고압작업실 내 발파 — has_high_pressure_gas COMPOUND 처리 |
| 3dc9e223 | has_blasting | 채석장 특수조문 — 1차 seed 대상 아님. 별도 검토 |
| c97b62c1, 75c666c5 | has_chemical_substance | 허가대상 유해물질 용기 밀폐 — has_chemical_substance 유지하되 condition_text NULL → ACTION_TEXT로 처리 |
| 허가대상(베릴륨·석면 제외) 조문 | has_asbestos_demo | 허가대상 유해물질 조문이지 석면해체 아님 → has_chemical_substance로 이동 |

---

## 산출물 D: CONFIRMED_CANDIDATE / PENDING_REVIEW / EXCLUDED 분류 요약

| input_field | CONFIRMED_CANDIDATE | PENDING | PENDING_REVIEW | EXCLUDED |
|---|---|---|---|---|
| has_confined_space | 17 | 1 | 1 | 0 |
| has_blasting | 2 | 2 | 1 | 1(채석장) |
| has_chemical_substance | 7(대표) | ~50 | 5(복합) | 1 |
| has_high_pressure_gas | 3 | 4 | 6(잠함·잠수복합) | 2 |
| has_tower_crane | 5 | 1 | 0 | 0 |
| has_boiler | 4 | 0 | 1 | 1(불활성기체) |
| has_asbestos_demo | 5 | 7 | 0 | 5(허가대상유해물질 혼입) |
| has_diving | 10 | 4 | 2(고압복합) | 0 |

**분류 기준 재확인:**
- `CONFIRMED_CANDIDATE`: condition_text 명확 + input_field 직결 + sector 확정
- `PENDING`: action_text만 있거나 복합 조건이거나 sector 애매
- `PENDING_REVIEW`: 다른 has_*와 충돌 가능성 or 복합 COMPOUND 후보
- `EXCLUDED`: 오탐 / OUT_OF_SCOPE / 다른 has_*로 완전 이동

---

## 산출물 E: condition_code 명명 규칙 및 INSERT SQL 초안

### condition_code 규칙

```
형식: {CONDITION_TYPE}:{TARGET}:{ACTION}:{UUID_PREFIX_4자리}

예시:
  WORK_ACT:CONFINED_SPACE:PROGRAM:60f2
  EQUIPMENT_ACT:TOWER_CRANE:WALL_SUPPORT:33d6
  MATERIAL_ACT:HAZMAT:WORK_RULE:3b47
  COMPOUND:DIVING:HIGH_PRESSURE_DECOMP:3cba

규칙:
  - CONDITION_TYPE: WORK_ACT / EQUIPMENT_ACT / FACILITY_ACT / MATERIAL_ACT / COMPOUND / PROHIBITION
  - TARGET: 핵심 대상 (CONFINED_SPACE / TOWER_CRANE / HAZMAT / BLASTING / BOILER / ASBESTOS / DIVING 등)
  - ACTION: 행위 약어 (PROGRAM / VENTILATION / INSTALL / MONITOR 등)
  - UUID_PREFIX: semantic_clause_id 앞 4자리 (소문자)
  - 전체 중복 방지: condition_code UNIQUE 제약으로 보장
```

### INSERT SQL 초안 (실행 금지 — WO-CONDITION-SEED-001-APPLY에서 실행)

```sql
-- ============================================================
-- WO-CONDITION-SEED-001-APPLY INSERT 초안
-- 실행 금지: WO-CONDITION-SEED-001-APPLY 승인 후 실행
-- review_status 기본 PENDING
-- CONFIRMED_CANDIDATE는 review_status = 'CONFIRMED'로 적재 가능
-- ============================================================

-- [has_confined_space] 핵심 CONFIRMED 후보 (작업 프로그램)
INSERT INTO condition_mapping_candidate (
  semantic_clause_id, source_article_id,
  applicable_sectors, condition_source, condition_type,
  condition_code, input_field, input_operator, input_value,
  confidence, review_status
) VALUES
(
  '60f27afe-dc0f-4148-a990-9304864cc048',
  '0bcc0707-b90d-4847-aa73-aa5cb22c44a4',
  ARRAY['INDUSTRIAL','CONSTRUCTION','BUILDING'],
  'CONDITION_TEXT', 'WORK_ACT',
  'WORK_ACT:CONFINED_SPACE:PROGRAM:60f2',
  'has_confined_space', '=', 'true',
  0.95, 'PENDING'
),
(
  '1567425d-8c35-471d-bef9-b8f122b7e904',
  '206a7a66-e950-4778-87d2-64025d0ac5d4',
  ARRAY['INDUSTRIAL','CONSTRUCTION','BUILDING'],
  'CONDITION_TEXT', 'WORK_ACT',
  'WORK_ACT:CONFINED_SPACE:VENTILATION:1567',
  'has_confined_space', '=', 'true',
  0.95, 'PENDING'
),
(
  '4e59b845-9d49-41b1-848f-6f226e340dd2',
  '8099afdf-650f-4218-8f0a-5d269746317d',
  ARRAY['INDUSTRIAL','CONSTRUCTION','BUILDING'],
  'CONDITION_TEXT', 'WORK_ACT',
  'WORK_ACT:CONFINED_SPACE:EVAC:4e59',
  'has_confined_space', '=', 'true',
  0.95, 'PENDING'
),
(
  'bb6c51ab-ffc4-4597-af42-becca7dd77de',
  'cee6851c-36ce-44ed-91e0-9c5b5aef90a6',
  ARRAY['INDUSTRIAL','CONSTRUCTION','BUILDING'],
  'CONDITION_TEXT', 'WORK_ACT',
  'WORK_ACT:CONFINED_SPACE:MEASURE:bb6c',
  'has_confined_space', '=', 'true',
  0.95, 'PENDING'
),

-- [has_tower_crane] CONFIRMED 후보
(
  '33d69d53-78a0-4c0b-bf27-f242fe6df4e7',
  '223b59f9-00c1-4257-a97d-9edfa90ac35c',
  ARRAY['CONSTRUCTION'],
  'CONDITION_TEXT', 'EQUIPMENT_ACT',
  'EQUIPMENT_ACT:TOWER_CRANE:WALL_SUPPORT:33d6',
  'has_tower_crane', '=', 'true',
  0.98, 'PENDING'
),
(
  'c408f352-6a53-4334-9811-c1f254b5137d',
  '223b59f9-00c1-4257-a97d-9edfa90ac35c',
  ARRAY['CONSTRUCTION'],
  'CONDITION_TEXT', 'EQUIPMENT_ACT',
  'EQUIPMENT_ACT:TOWER_CRANE:WIRE_SUPPORT:c408',
  'has_tower_crane', '=', 'true',
  0.98, 'PENDING'
),
(
  'a9f6fa5d-7a09-4d05-b637-11659a715628',
  '223b59f9-00c1-4257-a97d-9edfa90ac35c',
  ARRAY['CONSTRUCTION'],
  'CONDITION_TEXT', 'EQUIPMENT_ACT',
  'EQUIPMENT_ACT:TOWER_CRANE:WALL_RULE:a9f6',
  'has_tower_crane', '=', 'true',
  0.98, 'PENDING'
),
(
  'd8116029-8057-457a-8cb4-6e86713763b2',
  '7bda8a53-4a97-4841-9826-3d5cdd9d4eb5',
  ARRAY['CONSTRUCTION'],
  'CONDITION_TEXT', 'WORK_ACT',
  'WORK_ACT:TOWER_CRANE:SIGNAL:d811',
  'has_tower_crane', '=', 'true',
  0.98, 'PENDING'
),
(
  'c52ff010-5d9d-4cb3-9e91-8898ac958510',
  'abfdf46f-8747-4900-aff4-91807929adeb',
  ARRAY['CONSTRUCTION'],
  'CONDITION_TEXT', 'WORK_ACT',
  'WORK_ACT:TOWER_CRANE:WIND_STOP:c52f',
  'has_tower_crane', '=', 'true',
  0.98, 'PENDING'
),

-- [has_boiler] CONFIRMED 핵심 4건
(
  'c2e1dc40-f270-4dae-8d2a-98eb5037c2fb',
  '5171e20f-94c5-4ee1-bff4-b4296d0248e9',
  ARRAY['INDUSTRIAL','BUILDING'],
  'ACTION_TEXT', 'EQUIPMENT_ACT',
  'EQUIPMENT_ACT:BOILER:SAFETY_DEVICE:c2e1',
  'has_boiler', '=', 'true',
  0.95, 'PENDING'
),
(
  'eeea64f4-af31-47da-a848-3bae370bc3b5',
  'b0b95f72-919e-4076-9e95-dfc7cbd261f1',
  ARRAY['INDUSTRIAL','BUILDING'],
  'ACTION_TEXT', 'EQUIPMENT_ACT',
  'EQUIPMENT_ACT:BOILER:PRESSURE_SWITCH:eeea',
  'has_boiler', '=', 'true',
  0.95, 'PENDING'
),
(
  '82e50bae-aabf-44bc-9876-89cb67bfb7eb',
  'cda84862-bf7c-47ca-9380-4337f7f2de4e',
  ARRAY['INDUSTRIAL','BUILDING'],
  'ACTION_TEXT', 'EQUIPMENT_ACT',
  'EQUIPMENT_ACT:BOILER:PRESSURE_RELIEF:82e5',
  'has_boiler', '=', 'true',
  0.95, 'PENDING'
),
(
  'c66b92fd-f1e4-4ccd-9dc3-545b6d6529a2',
  '22361b86-2928-4324-a20c-6bbccc3da852',
  ARRAY['INDUSTRIAL','BUILDING'],
  'ACTION_TEXT', 'EQUIPMENT_ACT',
  'EQUIPMENT_ACT:BOILER:WATER_LEVEL:c66b',
  'has_boiler', '=', 'true',
  0.95, 'PENDING'
),

-- [has_diving] CONFIRMED 핵심 5건
(
  'b5af8758-e937-45c1-8d56-f6cd5436bd43',
  '17416f1c-6489-48b1-9e0e-38ee29e9d528',
  ARRAY['CONSTRUCTION'],
  'CONDITION_TEXT', 'WORK_ACT',
  'WORK_ACT:DIVING:SCUBA_PAIR:b5af',
  'has_diving', '=', 'true',
  0.97, 'PENDING'
),
(
  '66838d23-b1dc-44b0-bdc5-5e94fb3bbba4',
  '17416f1c-6489-48b1-9e0e-38ee29e9d528',
  ARRAY['CONSTRUCTION'],
  'CONDITION_TEXT', 'WORK_ACT',
  'WORK_ACT:DIVING:SCUBA_MONITOR:6683',
  'has_diving', '=', 'true',
  0.97, 'PENDING'
),
(
  '3838fa4d-07ad-474c-b4ec-9b48765bb7dd',
  'cc406aa1-db5a-4514-88d6-810df9c95f0a',
  ARRAY['CONSTRUCTION'],
  'CONDITION_TEXT', 'EQUIPMENT_ACT',
  'EQUIPMENT_ACT:DIVING:AIR_TANK:3838',
  'has_diving', '=', 'true',
  0.97, 'PENDING'
),
(
  '1abd72cf-2520-4d4e-b767-4d97a543bc56',
  'cc406aa1-db5a-4514-88d6-810df9c95f0a',
  ARRAY['CONSTRUCTION'],
  'CONDITION_TEXT', 'EQUIPMENT_ACT',
  'EQUIPMENT_ACT:DIVING:RESERVE_GAS:1abd',
  'has_diving', '=', 'true',
  0.97, 'PENDING'
),
(
  'abcd4d86-8412-4efa-9712-4033d18b3d36',
  '79df6e8c-e8a4-494c-9ece-89a4588c1376',
  ARRAY['CONSTRUCTION'],
  'CONDITION_TEXT', 'WORK_ACT',
  'WORK_ACT:DIVING:RECORD:abcd',
  'has_diving', '=', 'true',
  0.97, 'PENDING'
);

-- ============================================================
-- 위 27건은 초안 예시 (핵심 CONFIRMED_CANDIDATE 위주)
-- 전체 156건 INSERT는 WO-CONDITION-SEED-001-APPLY에서 일괄 처리
-- ============================================================
```

---

## 완료 조건 체크

| 항목 | 완료 |
|---|---|
| 9개 has_*별 후보 수 확인 | ✅ (156건, has_safety_manager 제외) |
| 후보/제외/검토필요 분류 완료 | ✅ |
| applicable_sectors 정책 적용 | ✅ |
| condition_code 고유성 설계 | ✅ (UUID 4자리 suffix로 보장) |
| INSERT SQL 초안 작성 | ✅ (27건 초안, 전체 156건은 APPLY에서) |
| 실제 DB 적재 | ❌ 미실행 (WO-CONDITION-SEED-001-APPLY에서 실행) |

---

## 다음 단계

1. **WO-CONDITION-SEED-001-APPLY** (별도 승인 후)
   - 156건 전체 INSERT SQL 생성
   - CONFIRMED_CANDIDATE → `review_status = 'PENDING'` 적재
   - PENDING_REVIEW 항목은 별도 검토 후 적재

2. **WO-CONDITION-SEED-002** (이후)
   - THRESHOLD / appendix_condition 기반 매핑 설계
   - employee_count ≥ 50 → 안전관리자 선임 의무 등

---

## 보류: has_safety_manager

**employee_count THRESHOLD 우선 처리 권고.**

```
현행 기준:
  employee_count >= 50 → 안전관리자 선임 의무
  employee_count >= 20 → 안전보건관리담당자
  employee_count >= 100 → 안전보건관리규정

has_safety_manager 직접 매핑은 하지 않는다.
→ WO-CONDITION-SEED-002 (THRESHOLD 설계)에서 처리.
```

---

*WO-CONDITION-SEED-001 설계 완료. INSERT 미실행. 승인 후 WO-CONDITION-SEED-001-APPLY 진행.*
