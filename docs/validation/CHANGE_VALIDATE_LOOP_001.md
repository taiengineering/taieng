# CHANGE-VALIDATE LOOP 001 — 첫 변경-검증-롤백
# WO-CHANGE-VALIDATE-LOOP-001

**작성일**: 2026-06-21
**원칙**: 조사 종료. 변경 1건 → 실행 → Coverage 측정 → 유지/롤백.
**결과**: 변경 실행 + 측정 + 롤백 완료. 판정 C.

---

## 기준선 (변경 전)

```
건설 결과 (factory_id 7b9bf18d, 테스트 건설현장):
  total 114~138
  PRESENT (정답지 의무) = 0
  WRONG (소방+전기) = 135/138 (98%)
  소방시설 시행규칙 = 15건 포함
```

---

## 변경 (1건)

```
대상: law_sector_mapping, law_id 01c23728
      "소방시설 설치 및 관리에 관한 법률 시행규칙"
변경 전 sectors: [BUILDING, INDUSTRIAL, CONSTRUCTION]   (auto_regex, 전섹터 오매핑)
변경 후 sectors: [BUILDING, INDUSTRIAL]                 (CONSTRUCTION 제거)
가설: 소방시설 점검은 "건물(시설)" 의무이지 건설 공사 의무 아님 →
      CONSTRUCTION 제거 시 건설 결과에서 빠져 WRONG 감소.
백업: 롤백값 = [BUILDING, INDUSTRIAL, CONSTRUCTION]
```

---

## 실행 (동일 프로브 재실행)

```
POST /diagnosis/factory-test-run {factory_id: 7b9bf18d}  → 200
새 토큰 41ccabaa. compiler_core가 새 매핑으로 temp-factory 재평가.
```

---

## 결과 Reading (변경 후)

```
                  변경 전        변경 후       변화
total             114            99           -15
소방시설 시행규칙  15건           0건          ★ 제거 성공
WRONG (소방+전기)  135(98%)       96(97%)      절대 -39, 비율 -1%p
PRESENT (정답지)   0              0            변화 없음 ★
정상 의무 손실     -              없음          (작업환경측정/방사선/친환경주택 유지)
```

```
변경이 정확히 작동: sector filter가 새 매핑(CONSTRUCTION 제거)을 반영,
소방시설 시행규칙 15건이 건설 결과에서 완전히 빠짐.
부작용 없음(정상 의무 손실 0).
```

---

## 판정

```
A (PRESENT 증가 + WRONG 증가 없음)  → 아님 (PRESENT 0 불변)
B (PRESENT 증가 + 경미 부작용)       → 아님
C (변화 없음)                        → ★ 해당
D (WRONG 증가/오염 증가)             → 아님

판정 근거:
  - 핵심 지표 PRESENT = 0 → 0 (불변). 정답지 의무는 여전히 안 나옴.
  - WRONG 절대수는 39 줄었으나 비율은 98→97%로 사실상 불변.
    = 소방 1건 빼도 다른 소방 법령이 자리를 채움(소방 미매핑 100개).
  - 1건 매핑 수정으론 PRESENT를 못 만듦(PRESENT는 binding 문제).

→ 등급 C (변화 없음에 수렴).
```

---

## 결정: 롤백

```
규칙: C/D → 즉시 롤백.
실행: sectors 원복 [BUILDING, INDUSTRIAL, CONSTRUCTION].
검증: RESTORED_OK (기준선 일치).
```

---

## ★ 이 루프가 가르쳐 준 것 (메타)

```
1. WRONG(소방 오염)은 "1건씩 매핑 수정"으로 안 줄어든다.
   소방 미매핑/오매핑이 100개 규모 → 1건 빼면 다른 게 채움.
   = law_sector_mapping 수정은 "전체 소방 일괄 재매핑"이어야 효과.
     (단 어느 소방법이 어느 섹터인가 = 법령해석 = GPT, 대량 작업)

2. PRESENT(정답지 의무)는 mapping 수정으로 절대 안 늘어난다.
   PRESENT 0의 원인은 binding 부재(P1)이지 mapping이 아님.
   = WRONG와 PRESENT는 독립 문제. mapping은 WRONG만 건드림.

3. 따라서 "PRESENT 0→1"을 만드는 유일한 길 = binding 생성(GPT).
   Claude가 실행 가능한 mapping 변경으로는 PRESENT를 못 올린다.
   → 다음 실효적 루프는 GPT binding 1건 생성 후 Claude가 재실행·측정.
```

---

## 성공 기준

```
- 변경 1건 실행            → ✅ (소방시설 시행규칙 CONSTRUCTION 제거)
- 동일 프로브 재실행       → ✅ (factory-test-run 200)
- Coverage 측정           → ✅ (PRESENT 0→0, WRONG 98→97%)
- 유지/롤백 결정          → ✅ (C → 롤백)
- 롤백 검증               → ✅ (RESTORED_OK)
- 실제 수치 변화 측정      → ✅ (소방 시행규칙 15→0)
```

---

## 완료 문장

```
조사 대신 변경-검증-롤백 루프를 수행하였다.
law_sector_mapping 1건(소방시설 시행규칙 CONSTRUCTION 제거)을 변경하고
동일 프로브를 재실행한 결과, 해당 법령 15건은 결과에서 제거됐으나
PRESENT는 0→0 불변, WRONG는 98→97%로 사실상 불변(C)이었다.
규칙에 따라 즉시 롤백하고 기준선을 복원하였다.
이 루프는 PRESENT를 올리는 길이 mapping이 아니라 binding(GPT)임을 실측으로 확인했다.
```
