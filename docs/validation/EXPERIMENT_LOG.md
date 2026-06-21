# EXPERIMENT LOG — PRESENT 0→1 실험 기록
# WO-FIRST-PRESENT-EXPERIMENT-001

**원칙**: 정답 찾기 아님. 실제 필드로 실험 → 결과로 판단 → 실패 시 롤백.

---

## 실험 #001

```
대상: 안전관리계획의 수립 (건설기술 진흥법 시행령)
slot: 58deee47-495a-4abd-a11b-97e8d68ba731 (draft 8b23dac4, IF_NUMERIC)

[변경 전 백업]
  binding_field: NULL
  operator: '<='  value: '20'  unit: '일'
  family: DEADLINE_THRESHOLD_FAMILY  raw_token: "20일 이내"

[변경 후]
  binding_field: 'monetary_value'  operator: '>='  value: '1'
  (실값 근거: 테스트 건설현장 construction_amount=5000000000(50억),
   >= 1 = 모든 건설공사 매칭 보장 목적)

[실행]
  POST factory-test-run {factory_id: 7b9bf18d} → 200
  새 token: 87c0dde2-f677-428b-a143-4665e261a8d7

[결과 측정]
                  기준선    실험후    변화
  PRESENT 안전관리계획  0        0       변화 없음 ★
  total           114       114
  WRONG           ~135(98%) 111(97%)  변화 없음 수준

[판정] C (PRESENT 변화 없음)
[결정] 즉시 롤백 → RESTORED_OK (binding_field NULL, <=20 복원)
```

---

## 실험 #001 관찰 (다음 실험용, 조사 아님)

```
binding_field를 채웠는데도 PRESENT 0→0.
= "binding_field 부재"만이 PRESENT 0의 원인이 아님.

가능한 다음 실험 변수 (정답 아닌 시도 후보):
  1. binding_field 이름 불일치:
     'monetary_value'를 facility 평가가 construction_amount 컬럼에
     매핑 못 했을 수 있음. → 다른 필드명(construction_amount 직접?) 시도.
  2. slot이 DEADLINE family라 평가 제외:
     family_name=DEADLINE_THRESHOLD_FAMILY인 slot은 _load_draft_slot_groups
     적재 후에도 evaluate에서 제외될 수 있음. → 다른 slot(67c35621 IF_CONDITION 등) 시도.
  3. draft 8b23dac4가 "통보해야 한다"(행정절차) → applicability는 떠도
     task 변환에서 누락될 수 있음. → THEN_ACTION이 의무인 다른 draft 시도.
  4. _load_draft_slot_groups가 IF_NUMERIC 적재 시 operator+value 필수 →
     채웠으나 binding_field-facility 매핑 단계에서 끊겼을 가능성.

★ 위는 "다음 실험에서 바꿔볼 변수"이지 조사 대상 아님.
  실험 #002에서 변수 1개 바꿔 재시도 가능.
```

---

## 성공 기준 대조

```
FP-01 binding 1건만 변경    → ✅ (slot 58deee47 단건)
FP-02 건설 프로브 재실행     → ✅ (200, token 87c0dde2)
FP-03 결과페이지 Reading     → ✅ (rules_table 측정)
FP-04 PRESENT 0→1 확인       → ✗ (0→0, 미달)
FP-05 유지/롤백 결정         → ✅ (C → 롤백, RESTORED_OK)
FP-06 조사 루프 0건          → ✅ (실험만, 조사 안 함)
```

---

## 완료 문장

```
안전관리계획 의무를 대상으로 첫 PRESENT 생성 실험을 수행하였다.
slot 58deee47에 binding_field=monetary_value, >=1을 적용하고 건설 프로브를
재실행한 결과, PRESENT는 0→0 불변(C)이었고 즉시 롤백하여 기준선을 복원하였다.
실험으로 "binding_field 부재만이 PRESENT 0의 원인이 아님"을 확인하였고,
다음 실험 변수(필드명/slot/draft 선택)를 후보로 남겼다.
정답 찾기 없이 실험-측정-롤백 1회를 완료하였다.
```

---

## 실험 누적

```
#001  slot 58deee47 / monetary_value >=1  →  PRESENT 0→0  →  롤백
#002  (대기)
```
