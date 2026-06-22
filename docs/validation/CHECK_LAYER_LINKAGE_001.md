# CHECK LAYER LINKAGE #001 — 입력→VR→Check→Draft→결과 연결 추적
# WO-CHECK-LAYER-LINKAGE-001

**성격**: 추적 WO (수정 0, SELECT만). 위험요소 입력이 결과까지 어느 단계에서 끊기는지 특정.
**방법**: draft_slot의 binding_field 실측 + 위험요소 article의 draft·slot 전수 조회.

---

## STEP-1~2 위험요소 입력 → binding 연결 (실측)

```
draft_slot에서 binding_field로 위험요소 입력(has_tower_crane/has_asbestos_demo/
has_blasting/has_confined_space 등)을 사용하는 slot:
  → 0개. (정규식 tower|crane|asbestos|blast|confined|diving 및 has_* 전수 조회 결과 없음)

위험요소 5종 article의 draft·slot을 전수 조회한 결과,
binding_field가 채워진 slot은 단 1개:
  잠수 "표면공급식 잠수작업 시 조치" draft d4d9c1c0
    IF_NUMERIC, binding_field=employee_count, operator='>=', value='0'
  → 이것이 잠수만 결과에 나오는 유일한 이유.
```

---

## STEP-3~5 위험요소별 단계 추적

### 타워크레인
```
입력(has_tower_crane): 존재 (factories 컬럼, 목업에 true)
Draft: 존재 (타워크레인의 지지/고정/제동장치/조종실/정밀진단/대여계약 심사 등 다수)
Slot: 존재하나 전부 binding_field=null
  - 대부분 THEN_ACTION/REFERENCE (조건 아님)
  - IF_CONDITION 있음(지지/조종실/대여계약): binding 없음
  - IF_NUMERIC 1개(고정 c0f6e2df): operator='<=', value=null, binding 없음
VR→Check 연결: 없음 (has_tower_crane을 읽는 slot 0개)
결과: 미출현
```

### 석면
```
입력(has_asbestos_demo): 존재
Draft: 존재 (석면조사/해체제거작업 시 조치/비산방지계획/건축물석면조사 등 매우 다수)
Slot: 존재하나 전부 binding_field=null
  - IF_CONDITION 다수(해체제거작업 시 조치 5588437b 등): binding 없음
  - IF_NUMERIC 일부: operator만 있고 binding_field=null
VR→Check 연결: 없음
결과: 미출현
```

### 발파
```
입력(has_blasting): 존재
Draft: (화약류 관련 article — 조회 결과 위험요소 직결 draft 빈약)
Slot: binding_field=null
VR→Check 연결: 없음
결과: 미출현
```

### 밀폐공간
```
입력(has_confined_space): 존재
Draft: (밀폐공간 작업 관련)
Slot: binding_field=null
VR→Check 연결: 없음
결과: 미출현
```

### 잠수 (유일한 출현)
```
입력(has_diving): 존재
Draft: 존재 (표면공급식 잠수작업 시 조치 / 잠수기록 작성보존 / 잠수설비 점검)
Slot: "표면공급식 잠수작업 시 조치" draft d4d9c1c0의 IF_NUMERIC에
       binding_field=employee_count >= 0 (우리가 이전에 건 것)
VR→Check 연결: employee_count로 연결됨 (단 has_diving이 아니라 employee_count)
결과: 출현 ★ (단 has_diving 때문이 아니라 employee_count>=0이 항상 참이라서)
```

---

## STEP-6 최종 결론 (어느 단계에서 끊기는가)

```
타워크레인을 입력했는데 왜 결과가 안 나오는가?
  → 입력 존재 / Draft 존재 / 그러나 어떤 draft_slot도 has_tower_crane을
    binding_field로 사용하지 않음.
    = 입력(VR) → Check(slot 조건) 연결이 없음. "VR→Check 단계에서 끊김."

석면을 입력했는데 왜 결과가 안 나오는가?
  → 동일. Draft는 풍부하나 slot의 binding_field가 전부 null.
    = VR→Check 단계에서 끊김.

발파를 입력했는데 왜 결과가 안 나오는가?
  → 동일. VR→Check 단계에서 끊김.

밀폐공간을 입력했는데 왜 결과가 안 나오는가?
  → 동일. VR→Check 단계에서 끊김.

(대조) 잠수는 왜 나오는가?
  → 유일하게 slot에 binding(employee_count>=0)이 걸려 있어서.
    단 이는 has_diving 입력과 연결된 것이 아니라, employee_count가 항상 참이라
    출현하는 것. 즉 "올바른 위험요소 연결"이 아니라 "우리가 건 임시 binding"의 결과.
```

### 끊긴 지점 = 공통적으로 동일
```
입력(has_*)  존재
   ↓
VR           존재 (factories 플래그 = VR 변수)
   ↓
Check/slot   ★ 여기서 끊김 — 위험요소 draft의 slot 중 has_* 또는 위험요소
             조건을 binding_field로 쓰는 것이 0개. 조건이 비어 있음(null).
   ↓
Draft        존재 (article·draft는 풍부하게 있음)
   ↓
결과         미출현 (slot 조건이 비어 평가가 위험요소 입력과 무관)
```

---

## 한 줄 정리

```
위험요소 4종(타워크레인/석면/발파/밀폐)은
"입력→VR"까지는 살아 있으나, "VR→Check(slot binding)" 단계에서 끊긴다.
Draft는 충분히 존재하지만, 그 draft의 slot 어디에도 위험요소 입력을
조건으로 연결한 binding이 없다(binding_field=null).
잠수만 employee_count>=0 binding 때문에 우연히 출현할 뿐이다.

∴ 끊어진 링크 = "위험요소 입력 → draft_slot 조건" 바인딩의 부재.
   다음 작업(별도 WO)은 이 slot들에 위험요소 조건을 연결하는 것이며,
   이는 binding_field/condition 설계로서 GPT/엔진 영역이다.
```

## 완료 문장
```
입력→VR→Check→Draft→결과 연결을 실측 추적한 결과, 위험요소 4종은
입력과 Draft가 모두 존재하나 draft_slot의 binding_field가 전부 비어 있어
"VR→Check 단계"에서 연결이 끊긴다. 잠수만 employee_count>=0 binding으로
출현하며 이는 위험요소 입력과 무관하다. 끊어진 링크는 "위험요소 입력→slot 조건"
바인딩의 부재로 특정되었다. 수정 없이 추적만 수행하였다.
```
