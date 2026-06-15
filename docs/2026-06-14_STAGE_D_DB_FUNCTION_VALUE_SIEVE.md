# 2026-06-14 (3부) 거름망 DB+함수 전환 + 값 단위 전개 + 구분값

## 한 줄 요약
거름망을 **소스(Python) 처리 → DB+함수 처리**로 전환. 묶음 규칙을 **값 단위(한 값=한 망)**로
전개해 추적 가능하게. 규칙 정체를 **구분값(field_kind/rule_kind)**으로 박아 재해석 불필요.

---

## 1. ★ 대표 지적: 묶어서 빼면 문제 못 찾는다

### 문제
- 공용 거름을 만들며 **여러 패턴을 한 묶음(class_label 정규식 뭉치)으로 묶어서** DROP함.
  예: DELEGATED_ORG 한 규칙에 "관리기관|검사기관|인증기관|협회|조합…" 십수 개.
- 대표 지적: **"섹션으로 묶어서 빼면 어느 값에서 틀렸는지 추적이 안 돼 문제를 못 찾는다.
  섹션의 값을 기준으로 빼야 한다."** = 어제 원칙 "한 망=한 조건"을 어긴 것.

### 판단 (값 기준이 옳음)
| | 묶어서 빼기 | 값 기준으로 빼기 |
|---|---|---|
| 한 망 | 여러 조건(기관 십수개) | 한 조건(값 하나) |
| 추적 | 묶음까지만 | 값마다 몇 건 걸렀나 |
| 문제 발견 | 못 찾음 | 어느 값이 틀렸는지 보임 |
- 값 수백 개 = 행 수백 개. 어제 원칙 "노가다 효율적, 수백 장 돼도 빠짐없다" 그대로.

---

## 2. 방향 전환: 소스 → DB + 함수 (대표 결정)

### 이유
- 규칙은 이미 테이블(legal_sieve_rule)에 있는데 적용 로직은 Python(legal_engine_policy.py)에
  분리. 규칙 바꿔도 코드 배포 필요, 측정도 매번 SQL 새로 짬.
- **규칙도 DB, 적용도 DB 함수**로 합치면: 규칙 추가(행) → 즉시 적용 → 즉시 측정.
- 메모리의 하이브리드 아키텍처 방향(로직을 DB 쪽으로)과 일치.

### 구현
```
[테이블] legal_sieve_rule
  - stage=common        : 패턴 묶음 (BUSINESS·FRAGMENT 정규식)
  - stage=common_value  : 값 단위 1,442개 (한 값=한 망) ← 묶음을 전개
[함수] sieve_executor(executor) → (class_label, decision, rule_id, priority, match_kind)
        priority 순 첫 매치, exact>contains>regex. 미매치=0행(보류, 빠짐없이).
[함수] run_common_sieve() → 분포 측정 (SELECT * FROM run_common_sieve())
```

### 값 단위 전개 결과 (stage=common_value)
- AUTHORITY 680 / FRAGMENT 573 / DELEGATED_ORG 98 / SPECIAL_FACILITY 91 = **1,442개 값 행**
- 함수 결과가 묶음과 정확히 일치(전개 검증): AUTHORITY 38.1% / 보류 23.2% / BUSINESS 21.2%
  / FRAGMENT 13.7% / DELEGATED 2.8% / SPECIAL 1.0%.
- 이제 trace에 rule_id 남음 → "국토교통부장관이 잘못 걸렸다" 하면 그 행만 끄면 됨(추적·수정).

---

## 3. 구분값 박기 (대표 요청: 나중에 해석 안 하게)

### 추가 컬럼
- **field_kind**: 무엇을 보는 규칙인가 — executor / clause_sector / condition …
- **rule_kind**: 규칙 성격 — **word**(단어 한 값, exact, 한 망=한 단어) / **pattern**(어미·형태, regex)
- (기존) class_label=섹션(AUTHORITY/BUSINESS/FRAGMENT/SPECIAL_FACILITY/DELEGATED_ORG), verdict=처분(KEEP/DROP)

### 한 규칙이 네 값으로 완전히 읽힘 (재해석 불필요)
- 예: `executor / word / AUTHORITY / DROP` = "수범자를 보는 단어 규칙, 행정청, 버림"
- 현황: executor·word = AUTHORITY 680/FRAGMENT 595/DELEGATED 98/SPECIAL 91 (값 단위)
        executor·pattern = BUSINESS 3/AUTHORITY 3/FRAGMENT 4/DELEGATED 1/SPECIAL 2 (어미·형태)
- BUSINESS가 pattern만인 것 = 원칙(BUSINESS 안 넓힘)과 일치. 검증된 패턴만.

---

## 4. 거름망 최종 구조 (이 시점)
```
field_kind=executor 기준:
  [DROP] AUTHORITY(행정청) / SPECIAL_FACILITY(병원·학교·의료인) / DELEGATED_ORG(검사·인증·위탁기관)
         / FRAGMENT(조각·숫자치수)  → 명백한 것만, 값 단위로 추적
  [KEEP] BUSINESS(검증된 사업장 주체만, 안 넓힘 — pattern 3개)
  [보류] 미매치 = KEEP_REVIEW (빠짐없이, 결과에 남김)
순서(priority): FRAGMENT 10~22 → BUSINESS 28~30 → AUTHORITY 40~41 → SPECIAL 42~43 → DELEGATED 44
```

---

## 5. 다음 (이 창에서 계속)
- (가) 묶음 DROP 정규식(stage=common) 끌지 — 값 단위가 대체. 새 값은 보류로(빠짐없이) → 권고.
- (나) DB 함수를 Python policy에 연결 (또는 어댑터가 함수 직접 호출).
- (다) 섹터 거름 설계 (공용 다음 단계, 올바른 방식 = 통째거름 아님).
- (라) KSIC 공정명사 뽑기 C구조 구현 (process_law_map 검수2 = 거름망 통과분만).

## DB 변경 (이번 3부)
- `legal_sieve_rule.stage` 컬럼 활용 (common/common_value/sector)
- 값 단위 전개: common_value 1,442개 행 (묶음 DROP → 값 exact)
- `legal_sieve_rule.field_kind`, `rule_kind` 컬럼 추가 + 전체 채움
- 함수 `sieve_executor(text)`, `run_common_sieve()` 생성
