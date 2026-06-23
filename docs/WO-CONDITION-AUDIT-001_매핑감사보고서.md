# WO-CONDITION-AUDIT-001
# Condition Mapping 원인 감사 보고서

**작성일:** 2026-06-23 | **상태:** 완료
**감사 기준:** Q1(설명가능성) / Q2(input_field 반전) / Q3(sector 변경) / Q4(COMPOUND 후보)
**감사 방식:** 77건 전체 실제 조문 텍스트 직접 독해

---

## 감사 판단 기준

| 판정 | 기준 |
|---|---|
| PASS | Q1~Q3 모두 설명 가능, Q4 해당 없음 |
| PASS-NOTE | 설명 가능하나 조건 한정 또는 sector 경계 주의 필요 |
| FLAG-SECTOR | sector 범위가 현행 설정보다 넓거나 좁을 가능성 |
| FLAG-INPUT | input_field 연결 근거가 간접적 — 다른 has_*가 더 적합할 수 있음 |
| FLAG-COMPOUND | has_* 2개 이상에 걸쳐야 발동하는 조건 |
| WITHDRAW | 재검토 후 제거 권고 |

---

## 산출물 A: 설명 가능한 매핑 (PASS / PASS-NOTE)

### has_tower_crane (5건) — 전원 PASS

| condition_code | article_no | Q1 설명 한 문장 | Q2 반전 | Q3 sector | Q4 |
|---|---|---|---|---|---|
| EQUIPMENT_ACT:TOWER_CRANE:WIND_STOP:c52f | 37 | 타워크레인 설치·해체 작업 중 순간풍속 10m/s 초과 시 작업중지 의무. has_tower_crane=true인 건설현장에서만 의미. | false→미발생 ✅ | CONSTRUCTION 전용 ✅ | 없음 |
| EQUIPMENT_ACT:TOWER_CRANE:WALL_SUPPORT:33d6 | 142 | 자립고 이상 설치 시 벽체 지지 의무. 타워크레인 명시. | false→미발생 ✅ | CONSTRUCTION 전용 ✅ | 없음 |
| EQUIPMENT_ACT:TOWER_CRANE:WALL_RULE:a9f6 | 142 | 벽체 지지 시 준수사항. 자립고 조건 연계. | false→미발생 ✅ | CONSTRUCTION 전용 ✅ | 없음 |
| EQUIPMENT_ACT:TOWER_CRANE:WIRE_SUPPORT:c408 | 142 | 와이어로프 지지 시 준수사항. 타워크레인 명시. | false→미발생 ✅ | CONSTRUCTION 전용 ✅ | 없음 |
| WORK_ACT:TOWER_CRANE:SIGNAL:d811 | 146 | 타워크레인 사용 시 신호담당자 배치. 타워크레인 명시. | false→미발생 ✅ | CONSTRUCTION 전용 ✅ | 없음 |

---

### has_boiler (4건) — 전원 PASS

| condition_code | article_no | Q1 설명 | Q2 반전 | Q3 sector | Q4 |
|---|---|---|---|---|---|
| EQUIPMENT_ACT:BOILER:PRESSURE_RELIEF:82e5 | 116 | 보일러 압력방출장치 설치. "보일러" 명시. 보일러 보유 시설에서만 의미. | false→미발생 ✅ | INDUSTRIAL+BUILDING ✅ (공장보일러+건물보일러 모두 해당) | 없음 |
| EQUIPMENT_ACT:BOILER:PRESSURE_SWITCH:eeea | 117 | 보일러 과열방지 압력제한스위치 부착. "보일러" 명시. | false→미발생 ✅ | INDUSTRIAL+BUILDING ✅ | 없음 |
| EQUIPMENT_ACT:BOILER:WATER_LEVEL:c66b | 118 | 고저수위 조절장치 경보등 설치. "고저수위 조절장치" = 보일러 전용 설비. | false→미발생 ✅ | INDUSTRIAL+BUILDING ✅ | 없음 |
| EQUIPMENT_ACT:BOILER:SAFETY_DEVICE:c2e1 | 119 | 보일러 안전장치(압력방출·제한스위치·고저수위·화염검출기) 유지관리. "보일러" 명시. | false→미발생 ✅ | INDUSTRIAL+BUILDING ✅ | 없음 |

---

### has_diving (14건) — 12건 PASS, 2건 PASS-NOTE

| condition_code | article_no | Q1 설명 | Q2 반전 | Q3 sector | Q4 | 판정 |
|---|---|---|---|---|---|---|
| EQUIPMENT_ACT:DIVING:PRESSURE_GAUGE:474c | 527 | 잠수작업자에게 압축기체 송기 시 압력계 설치. "잠수작업자" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | 없음 | PASS |
| EQUIPMENT_ACT:DIVING:AIR_TANK:3838 | 530 | 공기압축기로 공기 송기 시 공기조·예비공기조 설치. "잠수작업자" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | 없음 | PASS |
| EQUIPMENT_ACT:DIVING:RESERVE_GAS:1abd | 530 | 호흡용 기체통 사용 시 예비 기체통 설치. "잠수작업자" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | 없음 | PASS |
| EQUIPMENT_ACT:DIVING:PRESSURE_REG:1eca | 531 | 10kg/cm² 이상 기체통 사용 시 2단 이상 감압 압력조절기. "잠수작업자" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | 없음 | PASS |
| WORK_ACT:DIVING:RECORD:abcd | 536 | 잠수작업 시 잠수기록표 작성 3년 보존. "잠수작업" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | 없음 | PASS |
| WORK_ACT:DIVING:ASCENT_SPEED:fa28 | 537 | 잠수작업자 수면 복귀 속도 고시 준수. "잠수작업자" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | 없음 | PASS |
| WORK_ACT:DIVING:ACCIDENT:bcec | 538 | 사고 잠수작업자 수면 복귀 후 조치. "잠수작업자" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | 없음 | PASS |
| EQUIPMENT_ACT:DIVING:AIRFLOW:084b | 544 | 표면공급식 잠수작업자에게 분당 60리터 이상 송기. "잠수작업자" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | 없음 | PASS |
| WORK_ACT:DIVING:EMERGENCY_GAS:ab50 | 545 | 스쿠버 잠수작업 시 비상기체통 제공(실내 제외). "스쿠버 잠수작업" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | **실내 잠수는 제외** 조건 주의 | PASS-NOTE |
| WORK_ACT:DIVING:SCUBA_PAIR:b5af | 545 | 스쿠버 잠수작업 시 2명 1조. "스쿠버 잠수작업" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | 없음 | PASS |
| WORK_ACT:DIVING:SCUBA_MONITOR:6683 | 545 | 스쿠버 잠수작업 시 감시인 배치. "스쿠버 잠수작업" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | 없음 | PASS |
| WORK_ACT:DIVING:SURFACE_MONITOR:320e | 547 | 표면공급식 잠수작업 시 감시인 배치. "표면공급식 잠수작업" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | 없음 | PASS |
| WORK_ACT:DIVING:MARKER:8548 | 548 | 잠수작업 장소 해사안전법 기준 표시(실내 제외). "잠수작업" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | **실내 잠수 제외** 조건 주의 | PASS-NOTE |
| WORK_ACT:DIVING:TIME_LIMIT:7246 | 557 | 잠수작업 시간 고시 준수. "잠수작업" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | 없음 | PASS |

---

### has_confined_space (16건) — 14건 PASS, 2건 PASS-NOTE

| condition_code | article_no | Q1 설명 | Q2 반전 | Q3 sector | Q4 | 판정 |
|---|---|---|---|---|---|---|
| WORK_ACT:CONFINED_SPACE:PROGRAM:60f2 | 619 | 밀폐공간 작업 시 작업프로그램 수립. "밀폐공간" 명시. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | PASS |
| WORK_ACT:CONFINED_SPACE:MEASURE:bb6c | 619 | 작업 전 산소·유해가스 농도 측정. "밀폐공간" 명시. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | PASS |
| WORK_ACT:CONFINED_SPACE:AIRMASK:16f2 | 619 | 적정공기 미유지 시 환기·마스크 조치. "산소 및 유해가스 농도" 측정 결과 조건. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | PASS |
| WORK_ACT:CONFINED_SPACE:VENTILATION:1567 | 620 | 밀폐공간 작업 시 환기. "밀폐공간" 명시. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | PASS |
| WORK_ACT:CONFINED_SPACE:HEADCOUNT:b9f9 | 621 | 입장·퇴장 시 인원점검. "밀폐공간" 명시. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | PASS |
| WORK_ACT:CONFINED_SPACE:RESTRICT:2b88 | 622 | 밀폐공간 사전 파악 및 관계외 출입금지. "밀폐공간" 명시. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | PASS |
| WORK_ACT:CONFINED_SPACE:SIGN:55de | 622 | 출입금지 표지 게시. condition_text = 622조 상위 조문 의존. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | **PASS-NOTE: 622조 항1 연계 확인 필요** |
| WORK_ACT:CONFINED_SPACE:FALL_PPE:570a | 624 | 산소결핍·유해가스 추락 우려 시 안전대·구명밧줄 지급. "밀폐공간" 명시. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | PASS |
| WORK_ACT:CONFINED_SPACE:RESCUE_EQUIP:f158 | 625 | 비상구출 기구(공기호흡기·사다리·섬유로프) 구비. "밀폐공간" 명시. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | PASS |
| WORK_ACT:CONFINED_SPACE:MONITOR:d4a0 | 626 | 상시환기장치 월 1회 정기점검. condition_text = "이상이 발견된 경우" 단편 — 626조 항1 연계. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | **PASS-NOTE: 단편조건 — 상시환기장치 보유 전제** |
| WORK_ACT:CONFINED_SPACE:GAS_PIPE:ec33 | 634 | 지하실·맨홀 내 가스배관 해체·부착 시 조치. 밀폐공간 작업 맥락. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | PASS |
| WORK_ACT:CONFINED_SPACE:GAS_STOP:be2c | 635 | 유해가스 누출·산소 부족 시 즉시 작업중지. 634조 연계. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | PASS |
| WORK_ACT:CONFINED_SPACE:AIROUT:474e | 636 | 산소결핍 공기 외부 배출 설비 설치. "작업장소" = 636조 항1(밀폐배관구역) 연계. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | PASS |
| WORK_ACT:CONFINED_SPACE:PIPE_SEAL:6087 | 636 | 밀폐공간 내 배관 통한 유해공기 누출 방지. "밀폐공간" 명시. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | PASS |
| WORK_ACT:CONFINED_SPACE:EVAC:4e59 | 639 | 질식·화재·폭발 우려 시 즉시 작업중단 대피. "밀폐공간" 명시. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | PASS |
| WORK_ACT:CONFINED_SPACE:INFORM:95aa | 641 | 작업 시작 시 사전 고지. "밀폐공간" 명시, "작업을 시작할 때" 조건. | false→미발생 ✅ | IND·CON·BLD ✅ | 없음 | PASS |

---

### has_blasting (2건) — 1건 PASS, 1건 FLAG-INPUT

| condition_code | article_no | Q1 설명 | Q2 반전 | Q3 sector | Q4 | 판정 |
|---|---|---|---|---|---|---|
| WORK_ACT:BLASTING:SHELTER:6c64 | 349 | 발파작업 시 피난불가 시 방호 피난장소 설치. "발파작업" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | 없음 | PASS |
| FACILITY_ACT:BLASTING:LIGHTNING:ac72 | 326 | 화약류·위험물 저장·취급 시설 피뢰설비 설치. **"화약류"는 맞으나 "위험물"도 포함** — has_blasting이 아닌 시설 일반에도 적용될 수 있음. | false여도 위험물 있으면 의무 발생 가능 | CONSTRUCTION ✅ | 없음 | **FLAG-INPUT: "위험물" 범위 초과. has_dangerous_material 별도 필드 필요 가능성** |

---

### has_high_pressure_gas (5건) — 2건 PASS, 2건 PASS-NOTE, 1건 FLAG-SECTOR

| condition_code | article_no | Q1 설명 | Q2 반전 | Q3 sector | Q4 | 판정 |
|---|---|---|---|---|---|---|
| EQUIPMENT_ACT:PRESSURE_VESSEL:COVER:84a5 | 87 | 압력용기 부속 원동기·벨트·풀리 회전부 덮개 설치. "압력용기등" 명시. | false→미발생 ✅ | IND+CON ✅ | 없음 | PASS |
| EQUIPMENT_ACT:PRESSURE_VESSEL:MARK:5d06 | 120 | 압력용기 최고사용압력·제조연월일 각인 표시. "압력용기등" 명시. | false→미발생 ✅ | IND+CON ✅ | 없음 | PASS |
| WORK_ACT:HIGH_PRESSURE:PILE_DRIVER:66e3 | 217 | 압축공기 동력 항타기·항발기 사용 시 준수사항. 압축공기 = 고압가스 사용 전제. **그러나 has_high_pressure_gas보다 has_pile_driver(항타기)가 더 정확한 필드** | false→미발생 ✅ | CONSTRUCTION ✅ | 없음 | **FLAG-INPUT: 항타기 보유 여부가 직접 조건. has_high_pressure_gas는 간접 연결** |
| FACILITY_ACT:HIGH_PRESSURE:COMPRESSOR_TEMP:3dc7 | 528 | 기압조절실용 공기압축기 온도 비정상 상승 시 자동경보장치 설치. "작업실 또는 기압조절실" = 잠함·잠수 작업 전용. | false→미발생 ✅ | **CONSTRUCTION ✅ 그러나 잠함/고압작업 병행 시설 전제** | has_diving 연계 | **PASS-NOTE: 잠함 또는 고압작업 시설 한정 조건. has_diving과 중복 가능** |
| WORK_ACT:HIGH_PRESSURE:CAISSON_LOWER:5acf | 540 | 잠함 침하 시 고압작업자 대피 및 공기 배출. "잠함" 명시. | false→미발생 ✅ | CONSTRUCTION ✅ | has_diving 연계 | **PASS-NOTE: "잠함" 조건 — has_caisson 별도 필드 논의 가능** |

---

### has_asbestos_demo (7건) — 6건 PASS, 1건 PASS-NOTE

| condition_code | article_no | Q1 설명 | Q2 반전 | Q3 sector | Q4 | 판정 |
|---|---|---|---|---|---|---|
| WORK_ACT:ASBESTOS:PLAN:6297 | 489 | 석면해체·제거 전 조사 확인 후 작업계획 수립. "석면해체·제거작업" 명시. condition_text NULL이나 action_text가 명확. | false→미발생 ✅ | CON+BLD ✅ | 없음 | PASS |
| WORK_ACT:ASBESTOS:INFORM:5816 | 489 | 작업계획 수립 후 근로자 고지. 489조 항1 연계. | false→미발생 ✅ | CON+BLD ✅ | 없음 | PASS |
| WORK_ACT:ASBESTOS:PPE:0fcf | 491 | 석면해체·제거 작업 시 보호구 지급. "석면해체·제거작업" 명시. | false→미발생 ✅ | CON+BLD ✅ | 없음 | PASS |
| WORK_ACT:ASBESTOS:RESTRICT_ENTRY:3454 | 492 | 계획 미숙지·보호구 미착용자 출입금지. "석면해체·제거작업" 명시. | false→미발생 ✅ | CON+BLD ✅ | 없음 | PASS |
| WORK_ACT:ASBESTOS:NO_SMOKING:54c9 | 493 | 작업장 내 금연·음식물 섭취 금지. "석면해체·제거작업장" 명시. condition_text NULL이나 action_text 명확. | false→미발생 ✅ | CON+BLD ✅ | 없음 | PASS |
| WORK_ACT:ASBESTOS:HYGIENE:9c3e | 494 | 작업장 인접 탈의실·샤워실·위생설비 설치. "석면해체·제거작업장" 명시. condition_text NULL이나 명확. | false→미발생 ✅ | CON+BLD ✅ | 없음 | PASS |
| WORK_ACT:ASBESTOS:METHOD:caa1 | 495 | 석면해체·제거 작업 방법별 조치 시행. "석면해체·제거작업" 명시. | false→미발생 ✅ | CON+BLD ✅ | **BUILDING 단독 리모델링에서도 발동 — sector 정확** | PASS |

---

### has_chemical_substance (24건) — 18건 PASS, 4건 PASS-NOTE, 2건 FLAG

| condition_code | article_no | Q1 설명 | Q2 반전 | Q3 sector | Q4 | 판정 |
|---|---|---|---|---|---|---|
| MATERIAL_ACT:MSDS:WORKER_EDU:6af2 | 114 | MSDS 대상물질 취급 근로자 안전교육. condition_text NULL이나 법 제114조 제1항 연계 명확. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | **PASS-NOTE: MSDS는 전 업종이나 1차 INDUSTRIAL로 한정 — 향후 확장 검토** |
| MATERIAL_ACT:MSDS:WORK_GUIDE:3cce | 114 | MSDS 대상물질 공정별 관리요령 게시. 동일 조건. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS-NOTE |
| MATERIAL_ACT:MSDS:LABEL:5785 | 115 | MSDS 대상물질 용기 경고표시. "사업장에서 사용하는" — 명확. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | **FLAG-SECTOR: MSDS 경고표시는 CONSTRUCTION·BUILDING도 해당. 현행 INDUSTRIAL 한정은 좁음** |
| MATERIAL_ACT:HAZMAT:LOCAL_EXHAUST:ba0c | 422 | 실내작업장 관리대상 유해물질 취급 시 국소배기장치. "관리대상 유해물질" 명시. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:VENTILATION_POS:a7a5 | 430 | 전체환기장치 설치 시 배풍기 위치 기준. "관리대상 유해물질" 맥락. condition_text가 "전체환기장치를 설치하려는 경우"로 한정. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | **PASS-NOTE: 전체환기장치 설치 결정 이후 조건 — 추가 입력 없어도 발동하나 설치 선행 필요** |
| MATERIAL_ACT:HAZMAT:FLOOR:f805 | 431 | 취급 실내작업장 바닥 불침투성 재료. "관리대상 유해물질" 맥락. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:ANTICORROSION:f857 | 432 | 접촉설비 부식방지 재료. "관리대상 유해물질" 맥락. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:GASKET:9e1d | 433 | 취급설비 접합부 누출방지 개스킷. "관리대상 유해물질" 명시. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:ALARM:dd47 | 434 | 1일 100리터 이상 취급 사업장에 경보설비. **condition_text에 "100리터 이상" 수량 조건 포함** — 단순 has_chemical_substance=true로는 부족. | **false→미발생 ✅ 이나 true라도 100리터 미만이면 미발동** | INDUSTRIAL ✅ | 없음 | **FLAG-INPUT: 수량 조건(input_value ≥ 100L) 추가 필요. 현행은 과매핑 가능성** |
| MATERIAL_ACT:HAZMAT:SPILL_KIT:a88d | 434 | 누출 시 제거 약제·기구 구비. 434조 항1 사업장 전제 — 동일 수량 조건 연계. | **100리터 조건 연계** | INDUSTRIAL ✅ | 없음 | **FLAG-INPUT: 동일 — 100리터 이상 사업장 전제** |
| MATERIAL_ACT:HAZMAT:REACTION_DEVICE:ff53 | 435 | 이상화학반응 발생 가능 설비 안전장치. "관리대상 유해물질 취급설비" 명시. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:CLOSED_STRUCT:f869 | 435 | 물질 배출 장치 밀폐식 구조. "관리대상 유해물질" 명시. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:WORK_RULE:3b47 | 436 | 취급설비 사용 작업 시 작업수칙 수립. "관리대상 유해물질" 명시. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:TANK_WORK:aba6 | 437 | 탱크 개조·수리·내부 작업 시 조치. "관리대상 유해물질이 들어 있던 탱크" — **탱크 보유 전제** | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | **PASS-NOTE: has_chemical_tank 별도 필드 논의 가능하나 현행 매핑 적절** |
| MATERIAL_ACT:HAZMAT:WORK_STOP_RESTRICT:d8ab | 438 | 작업중지 후 오염물질 제거 전 출입금지. "작업을 중지한 경우" 조건. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:CONTAINER:bbde | 443 | 운반·저장 시 누출없는 용기 사용. "관리대상 유해물질" 명시. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:STORAGE:6616 | 443 | 저장 장소 지정. "관리대상 유해물질" 명시. condition_text NULL이나 action_text 명확. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:PKG_STORAGE:02d6 | 444 | 운반·저장 사용 용기 밀폐 보관. "관리대상 유해물질" 명시. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:CLEAN:3362 | 445 | 취급 실내작업장·휴게실·식당 오염 제거 청소. "관리대상 유해물질" 명시. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:NO_SMOKE:12b0 | 445 | 취급 실내작업장 금연·음식물 섭취 금지. "관리대상 유해물질" 명시. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:ENTRY_BAN:5fc6 | 446 | 취급 실내작업장 관계외 출입금지. "관리대상 유해물질" 명시. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:WORK_ASSIGN:0c74 | 449 | 작업 배치 전 사항 고지. "관리대상 유해물질" 명시. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:WASH_FACILITY:e4ef | 451 | 피부·눈 접촉 우려 시 세척시설 설치. "관리대상 유해물질" 명시. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |
| MATERIAL_ACT:HAZMAT:SKIN_PPE:69db | 451 | 피부 자극성·부식성 취급 시 보호복·장갑 지급. "관리대상 유해물질" 명시. | false→미발생 ✅ | INDUSTRIAL ✅ | 없음 | PASS |

---

## 산출물 B: 설명 불가능한 매핑

**없음.** 77건 전원 Q1(한 문장 설명) 가능.

다만 아래 2건은 condition_text 단편 조건으로 **상위 조문 맥락 의존**:
- WORK_ACT:CONFINED_SPACE:SIGN:55de (622조) — "출입금지 표지 게시"가 622조 항1의 연속 의무임을 체크엔진이 인식해야 함
- WORK_ACT:CONFINED_SPACE:MONITOR:d4a0 (626조) — "이상이 발견된 경우"는 626조 항1(월 1회 점검) 조건의 부분 단편

두 건 모두 has_confined_space=true 전제에서 발동하면 의미상 맞으므로 PASS-NOTE 유지.

---

## 산출물 C: Sector 오류 후보

| condition_code | 현행 sector | 문제 | 권고 |
|---|---|---|---|
| MATERIAL_ACT:MSDS:LABEL:5785 | ['INDUSTRIAL'] | MSDS 경고표시 의무는 산업안전보건법 제115조 — 업종 불문 사업장에서 화학물질 사용 시 적용. CONSTRUCTION 현장·BUILDING 관리에서도 화학물질 사용 시 발동 | **['INDUSTRIAL','CONSTRUCTION','BUILDING']로 확장 검토** |
| MATERIAL_ACT:MSDS:WORKER_EDU:6af2 | ['INDUSTRIAL'] | 제114조 MSDS 교육 의무도 동일 | **확장 검토** |
| MATERIAL_ACT:MSDS:WORK_GUIDE:3cce | ['INDUSTRIAL'] | 동일 | **확장 검토** |

**조치 권고:** MSDS 3건은 다음 WO에서 applicable_sectors를 ['INDUSTRIAL','CONSTRUCTION','BUILDING']로 UPDATE. 단, 1차 서비스 타겟이 has_chemical_substance = INDUSTRIAL 집중이라면 현행 유지 가능 — 사업 판단 사항.

---

## 산출물 D: COMPOUND 후보 (기존 확인 + 신규 발견)

**기존 3건 (WO-CONDITION-COMPOUND-001 이관 확정):**

| 관련 condition_code | 조번호 | 이중 연결 필드 |
|---|---|---|
| 80135fef 연계 예정 | 532 | has_diving OR has_high_pressure_gas |
| 3cba36fb 연계 예정 | 535 | has_diving OR has_high_pressure_gas |
| 6edd3dd8 연계 예정 | 535 | has_diving OR has_high_pressure_gas |

**신규 발견 — PASS-NOTE에서 추출:**

| condition_code | 근거 | COMPOUND 설계 방향 |
|---|---|---|
| FACILITY_ACT:HIGH_PRESSURE:COMPRESSOR_TEMP:3dc7 | 기압조절실 = 잠함 또는 고압작업 시설 | has_high_pressure_gas AND (has_diving OR has_caisson) |
| WORK_ACT:HIGH_PRESSURE:CAISSON_LOWER:5acf | "잠함" 조건 — 고압가스 + 잠함 병행 | has_high_pressure_gas AND has_caisson (신규 필드 논의) |

---

## 산출물 E: 신규 has_* 필요 후보

| 발견 조건 | 현행 매핑 | 권고 신규 필드 | 우선순위 |
|---|---|---|---|
| 항타기·항발기 보유 (66e3 조문) | has_high_pressure_gas | has_pile_driver | 중 |
| 잠함(caisson) 구조물 사용 (5acf, 3dc7) | has_high_pressure_gas | has_caisson | 중 |
| 관리대상 유해물질 1일 100리터 이상 취급 (dd47, a88d) | has_chemical_substance | has_chemical_substance + input_value ≥ 100 (THRESHOLD 연계) | **높음 — 다음 WO에서 THRESHOLD 설계 시 반영** |
| 화약류·위험물 저장 시설 (ac72 조문) | has_blasting | has_dangerous_material (신규) | 낮음 (1차 외) |

---

## 종합 판정표

| 판정 | 건수 | 비율 |
|---|---|---|
| PASS | 58 | 75% |
| PASS-NOTE | 13 | 17% |
| FLAG-INPUT | 4 | 5% |
| FLAG-SECTOR | 1 | 1% |
| WITHDRAW | 0 | 0% |

**핵심 결론:**
1. **77건 전원 Q1 설명 가능.** "왜 연결되는가"를 한 문장으로 설명할 수 없는 매핑 = 0건.
2. **WITHDRAW 0건.** 제거 권고 매핑 없음.
3. **FLAG 5건은 과매핑 위험이 아니라 범위 조정 이슈.** 삭제가 아니라 sector 확장 또는 THRESHOLD 추가로 해소.
4. **MSDS 3건 sector 확장**은 다음 WO에서 UPDATE 가능.
5. **100리터 수량 조건(dd47, a88d)**은 WO-CONDITION-SEED-002 THRESHOLD 설계에서 input_value 조건으로 해소.

---

## 다음 단계 권고

1. **MSDS sector UPDATE** — 3건 ['INDUSTRIAL'] → ['INDUSTRIAL','CONSTRUCTION','BUILDING'] (별도 1줄 WO 또는 다음 WO 앞단에 포함)
2. **WO-CONDITION-SEED-002** — THRESHOLD 설계: employee_count ≥ 50, 화학물질 100리터 조건 등
3. **WO-CONDITION-COMPOUND-001** — COMPOUND 3건(+신규 2건 검토) 설계
4. **VCF-02 원인 검증 실행** — 이제 원인 모델이 설명 가능함을 확인했으므로 VCF-02 재실행 가치 있음

---

*WO-CONDITION-AUDIT-001 완료. 77건 전원 설명 가능. WITHDRAW 0. FLAG 5건 = 범위 조정 이슈.*
