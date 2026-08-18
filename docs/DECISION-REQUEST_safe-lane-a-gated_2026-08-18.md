# 결정 요청 — 레인 A 다음 배치가 막힌 지점 (실측 근거)

> 2026-08-18 · 캠페인 레인 A · 근거: DB 직독 + LEDGER
> 다음 수정 배치(9·47·55·58 등)는 **코드가 아니라 정본 결정**에 막혀 있다. 코드만 고치면 데이터가 남거나 오염을 되살린다.
> 각 항목에 "실측 결과 + 필요한 결정 + 결정 후 처리자"를 적는다. 결정만 주면 곧바로 적용한다.

---

## 1. §58 공사금액 단위 — 【운영자】 단위 정본

- 스키마는 **억원**을 명시(`contract_amount … 단위: 억원`).
- **라이브 실측 1건**: `contract_amount = 12000000000`(120억) — **원 단위로 저장**됨(BUILDING).
- 계산식 `int(contract_amount // 150)` → 저장만 눌러도 **선임 인원 8천만명**으로 덮어씀.

**결정:** 단위 정본 = **억원** 확정? (확정 시 저가 처리)
- (a) 오염 행 정리: 원단위로 들어간 값 ÷100,000,000 또는 재입력 기준 확정
- (b) 화면 「공사금액(억)」 셀 표기 정합
결정 없이 코드만 고치면 기존 원단위 데이터가 남아 계속 오판정.

## 2. §8·§9 어휘 정본 — 【운영자】 (한 묶음)

**§8 result_code** — 앱 `ok`·`bad`·`hold` → 서버 `NORMAL/ABNORMAL` 2값 매핑. **`hold`(보류)가 `ABNORMAL`(이상)로 오기록.** DB엔 시드 `PASS` 도 혼재(3갈래).
**§9 status_code** — `work_assignments` **5,689건 전부 `READY`**, `assigned_user_id` 0건. 그런데 배정 생성 코드는 `PENDING` 을 넣음(다른 경로가 만든 값). 홈 배너는 `PENDING,OVERDUE` 만 조회 → **`READY` 는 배너에 영영 안 잡힘.**

**결정:**
- result_code 정본 3값(예: `PASS`/`FAIL`/`HOLD`, 보류를 이상과 분리)
- status_code 정본: `READY` 를 `PENDING` 으로 정규화할지 / 배너 조회에 `READY` 포함할지
결정 후 저가 (a) 매핑 코드 (b) 기존 데이터 일괄 정리.

## 3. §47 법령룰 마스터 테이블 — 【GPT/엔진】

- `routers/inspection_schedule.py` 는 `master_building_legal_rules` 를 읽는다.
- **실측: 그 테이블은 없다.** `master_building_legal_rules_legacy_contaminated`(83컬럼)만 존재 — **"오염된 레거시"로 격리 개명**됨.
- 그 결과 일정관리 탭1의 **룰 목록·시설 목록·세트 생성 3기능이 런타임 불능.**

**결정(엔진 소유):** 오염 데이터를 법령 제품에 되살리면 위험하므로 저는 손대지 않는다.
- (a) 레거시 정제 후 정본 테이블 복원 / (b) 클린 재구축 / (c) 라우터를 legacy 로 임시 연결
어느 쪽이든 **엔진(GPT) 판단** 필요. (프런트 키 불일치 `schedule_status`↔`status_code` 는 그 다음 Cursor 건.)

## 4. §55 진단 1단계 드롭다운 데이터 — 【운영자/엔진】

- 화면은 `diagnosis_building_use`·`diagnosis_ksic_major`·`diagnosis_construction_type`·`diagnosis_special_facility` 를 부른다.
- **실측: `system_codes` 에 `diagnosis*` 0건.** 존재하는 것: `building_use`(26)·`construction_lv1~4`·`facility_lv1~4`·`CONSTRUCTION_*`. **`ksic_major` 는 어디에도 없음.**

**결정:** 4종을 각각 어떤 기존 카테고리로 매핑할지(예: `diagnosis_building_use`←`building_use`) + **없는 `ksic_major` 데이터 출처**(KSIC 대분류를 신규 시드?). 매핑·데이터 확정되면 저가 시드/별칭 처리.

---

## 게이팅 없는 잔여(대용량 → Cursor 소형 지시서 대상)

- **§7** 작업자 `is_active` 무시 — `WorkerCreate` 에 `is_active` 필드 추가 + 생성 시 반영(현재 True 하드코딩). `worker_registry.py` 28.5KB → Cursor.
- **§49** 서식 「과태료」 전건 공백 — `penalty`↔`penalty_summary` 별칭은 서버 가능(부분). `obligation_name`·`standard_form_code` 는 컬럼 부재라 불가. 서식 라우터 확인 후 판단.
- **§37** 휴무일 삭제 성공 오표시 — 전송부 ㉮(tai-admin #28)가 `res.ok` 를 throw 하므로 **병합·라이브 후 자동 해소 여부 확인**.

## 처리 원칙
검증 없는 완료 금지 · 오염 데이터 임의 복원 금지 · 어휘/단위 정본 없이 코드만 고치지 않기. 결정이 오면 §번호별로 즉시 적용한다.
