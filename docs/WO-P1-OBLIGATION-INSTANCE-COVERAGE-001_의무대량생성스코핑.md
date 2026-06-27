# WO-P1-OBLIGATION-INSTANCE-COVERAGE-001 — obligation_instance 대량 생성 스코핑·계획

**작성일:** 2026-06-27 | **성격:** 읽기 전용 조사·계획(데이터 INSERT 0). 새 엔진/법령 생성 금지.
**핵심 결론:** P1은 "단순 데이터 복제"가 아니라 **기존 엔진 컴포넌트의 배치 오케스트레이션 + 시설 속성 데이터 확보** 문제다. 실병목은 `facility_profiles`(2시설)와 시설 속성 희소성(최우수 시설조차 applicability의 78%가 MISSING_DATA). 무검증 대량 INSERT 금지.

---

## 의존 체인 + 실데이터 커버리지 (직독)
```
factories                5,812
  ↓ facility_profile_service (services/facility_profile_service.py — 존재)
facility_profiles            2   ← ★1차 병목 (THRESHOLD/EXISTS 시설속성 평가에 필수)
  ↓ Applicability 엔진
facility_applicability   5,344 시설 / 3,943,852행   ← 폭은 넓으나…
  └ 테스트 시설 738행 중 MISSING_DATA 574(78%)        ← profiles 부재로 평가 불가 다수
  ↓ obligation 생성기 (배치 WO-MVP-001-LIVE = 일회성, 재현 코드 없음)
obligation_instance          1 시설 / 171행 (UNIVERSAL 93 + THRESHOLD 3 + EXISTS 등)
```

## 직독으로 확정된 사실
```
1. obligation_instance 생성기는 리포에 재현 가능한 코드가 없음 (배치명 WO-MVP-001-LIVE는 테스트파일에만 존재 = 일회성).
2. obligation_instance.source_clause_id ↔ facility_applicability.part_id 매치 0
   → obligation_instance는 facility_applicability의 단순 투영이 아님(별도 생성 로직 = 엔진).
3. UNIVERSAL(93): fired_by=sector, applicable_sectors=[INDUSTRIAL,CONSTRUCTION,BUILDING] → 속성 불요(섹터 결정적).
   THRESHOLD/EXISTS: 시설 속성(근로자수·has_*·면적 등) 의존 → facility_profiles 필요.
4. facility_profile_service / facility_profile_api / exists_input_service 는 존재(프로파일 생성 기계 있음).
   단 profiles가 2시설뿐 = 아직 대량 실행 안 됨. 그리고 프로파일 생성은 시설 원천속성 데이터가 있어야 의미 있음.
```

## P1을 막는 진짜 병목 (우선순위)
```
P1-0 (최우선·전제): facility_profiles 대량 생성
   - 기계: facility_profile_service (존재). 입력: 시설 원천속성(factories/외부 데이터).
   - 현재 2/5,812. 시설 속성 데이터가 실제로 있는지(있어야 프로파일이 MISSING 아닌 값) 먼저 확인 필요.
P1-A (엔진): obligation_instance 생성기 productionize
   - 일회성 배치를 재현 가능 함수로. UNIVERSAL=섹터복제(결정적) + THRESHOLD/EXISTS=프로파일 기반 평가.
   - 법령해석 로직 = GPT 전담 영역.
```

## 역할 분리 (절대 규칙 적용)
```
GPT (엔진/법령해석): obligation_instance 생성기 productionize, 트리거 발화 로직, EXISTS/THRESHOLD 평가.
Claude (DB·검증·데이터 op):
   - facility_profiles 배치 실행 검증 + 결과 "글 읽기" 검증(값 정상/ MISSING 비율).
   - obligation_instance 생성 결과를 조문 단위로 의미 검증(카운트 금지, 글 읽기).
   - ON CONFLICT DO NOTHING·CONFIRMED 미수정·테스트 코호트 우선 원칙 관리.
   - 단, "어느 조항이 어느 시설에 발화되는가"(법령해석)는 절대 직접 INSERT/판정하지 않음.
```

## 안전 실행 계획 (검증된 방식부터 — 대량 INSERT 전)
```
STEP 0  시설 원천속성 가용성 진단: factories에 sector/ksic/근로자수/면적/has_* 등이 실제로 채워진 시설 수 집계.
        → 채워진 게 거의 없으면 P1-0는 "속성 데이터 확보"가 선행(프로파일 생성만으론 MISSING 양산).
STEP 1  테스트 코호트 선정: 섹터별 대표 5~10개 시설(속성 보유분).
STEP 2  facility_profile_service로 코호트 프로파일 생성 → Claude가 값/MISSING 비율 글읽기 검증.
STEP 3  GPT가 obligation 생성기로 코호트 obligation_instance 생성(UNIVERSAL+THRESHOLD+EXISTS).
STEP 4  Claude가 코호트 obligation을 조문 단위 의미 검증(이 시설·이 의무유형 정합?).
STEP 5  코호트 PASS 후에만 점진 확대(섹터별 → 전체). 단계마다 글읽기 검증.
```

## 지금 하지 말 것 (위험)
```
- obligation_instance 5,344×N 무검증 대량 INSERT (의미 오매핑 대량 양산 = 가장 위험한 패턴).
- THRESHOLD/EXISTS를 facility_profiles 없이 복제 (시설 속성 거짓 단정 → 잘못된 법적 의무 부여).
- UNIVERSAL 93을 섹터 검증 없이 전 시설 복제 (BUILDING/CONSTRUCTION 전용 universal 세트 존재 여부 GPT 확인 전).
```

## 대표 결정 필요 2건
```
A. 시설 원천속성 데이터 현황: 5,812 시설 중 속성(근로자수·업종·has_*)이 실제 채워진 비율은?
   (거의 없으면 P1은 데이터 확보가 선행 — 프로파일/생성만으론 MISSING 양산)
B. obligation_instance 생성기 productionize 담당: GPT가 일회성 배치를 재현 함수로 만들고,
   Claude가 프로파일 배치·검증·코호트 글읽기 검증을 맡는 분담으로 진행할지.
```

## Boundary 준수
```
데이터 INSERT/수정 0 (조사·계획만). 법령해석/엔진 미수정. facility_applicability/obligation_instance 미변경.
다음: STEP 0(속성 가용성 진단) 승인 시 Claude가 즉시 집계 → 코호트 선정.
```

*WO-P1-OBLIGATION-INSTANCE-COVERAGE-001 — P1 실병목=facility_profiles(2)+속성 희소성. 생성기는 일회성(엔진=GPT). 테스트 코호트→글읽기 검증→점진 확대. 무검증 대량 INSERT 금지.*
