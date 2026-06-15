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

---

## 4부 (이어서): 전 거름망 값 단위화 완성 + 1000행 버그 해결

### ★ 대표 원칙: "원칙 1에 1룰. 나중에 합한다."
- 실제 진단에서 KEEP가 전부 rule 24(BUSINESS 묶음 정규식)에 걸림 → 어느 값 때문인지 추적 불가.
  "수도사업자/가스사업자/판촉영업자"(비고객 업종)가 rule 24의 "사업자"에 걸려 KEEP됨.
- 대표 지적: BUSINESS도 **1룰=1값**으로 풀어야 추적된다. 합치는 건 나중에.

### BUSINESS·FRAGMENT 패턴도 값 단위로 전개
- BUSINESS 패턴(rule 24,25,36,39)이 잡던 executor 860개 값 → 한 값=한 룰(exact, KEEP) 전개.
  패턴 끄고 측정: BUSINESS 6,603→6,533 (70건 중복정리, 빠짐 아님 — `~려는 자` 값은 이미 박힘 확인).
  → BUSINESS 패턴 룰 4개 삭제.
- FRAGMENT 패턴(동사조각·숫자치수)도 값 전개 → 분포 동일(4,281 유지) → 패턴 룰 삭제.
- **결과: 거름망 전체가 word(값) 단위, pattern 0개.** "원칙 1에 1룰" 완성.

### 묶음 DROP 정규식 삭제 (3부 잔여)
- AUTHORITY/SPECIAL_FACILITY/DELEGATED_ORG 묶음 정규식 6개 → 값으로 전개 확인 후 삭제.
- 끈 상태 측정해 분포 동일(값이 다 받침) 확인 후 DELETE.

### 1000행 버그 해결 (PostgREST RPC 제한)
- 증상: 어댑터가 함수 결과를 1000건만 받음(by_class에 1000 합계).
- 해결: ① 함수 diagnose_clauses_common()이 DROP 제외하고 KEEP+보류만 반환(불필요한 17000건 안 보냄).
        ② Python _fetch_sieved_clauses가 .range() 페이지네이션으로 전체 수신.
- 검증(실제 진단, 건설 factory): clauses_returned **13,971**(=KEEP 6,475 + 보류 7,496).
  by_class = BUSINESS 6,475 / AMBIGUOUS 7,496. rule_id 추적 작동(사업주 2212, 건설사업자 1768,
  전기사업자 1854, 노무제공플랫폼사업자 1579, 타이어제작자등 2108 …).

### 글읽기 관찰 (다음 단계 재료)
- KEEP에 건설 무관 업종 잔존: 타이어제작자·전기사업자·전기통신사업자·노무제공플랫폼사업자·제조업자.
- 이는 정상 — 공용 거름은 "사업장 주체냐"만 봄. "건설이냐"는 다음 단계(섹터/업종). 대표 순서대로.
- **이제 값 단위라 뺄 수 있음**: 비고객 업종 값 룰만 끄면 됨(묶음이면 불가했음).

---

## 5부: 분해 후 원본 삭제 + common_value 통일 (대표 원칙)

### ★ 대표 원칙: "분해 후에는 기존 것 삭제가 바람직하다"
- 분해(값 전개) 후 원본을 남기면 또 해석 대상이 됨. off(비활성)만 해둔 것도 같이 삭제.

### 정리 내역
- 비활성(off) 룰 삭제: sector 폐기 룰 6개(SECTOR_MISMATCH, 통째거름 폐기분) DELETE.
- stage=common의 FRAGMENT word 22개 → 21개는 common_value에 중복(전개 시 들어감)이라 삭제,
  남은 1개("벌금", 데이터에 없어 전개 안 됨)는 common_value로 stage 이동(값 룰 한 곳 통일).
- 결과: **모든 룰이 stage=common_value / rule_kind=word 단위. 패턴 0, 비활성 0, 중복 0, 폐기잔재 0.**

### 거름망 최종 (5부 시점) — 2,230개 값 룰
| class | verdict | 룰 |
|---|---|---|
| BUSINESS | KEEP | 787 |
| AUTHORITY | DROP | 680 |
| FRAGMENT | DROP | 574 |
| DELEGATED_ORG | DROP | 98 |
| SPECIAL_FACILITY | DROP | 91 |
- 분포 유지: AUTHORITY 38.2% / 보류 23.2% / BUSINESS 20.9% / FRAGMENT 13.7% / DELEGATED 2.8% / SPECIAL 1.1%.

---

## 거름망 최종 구조
```
field_kind=executor, rule_kind=word(값), stage=common_value, 2,230개:
  [DROP] AUTHORITY / SPECIAL_FACILITY / DELEGATED_ORG / FRAGMENT  → 값 단위, rule_id 추적
  [KEEP] BUSINESS(사업장 주체 값)  → 값 단위
  [보류] 미매치 = KEEP_REVIEW (빠짐없이)
[함수] sieve_executor() 판정+rule_id / run_common_sieve() 측정 / diagnose_clauses_common() 진단(KEEP+보류, 페이지네이션)
실제 진단 = 13,971건(KEEP 6,475 + 보류 7,496), DROP은 DB에서 제외.
```

## 다음 (이 창에서 계속)
- 섹터 거름 설계 (공용 다음, 통째거름 아님). 비고객 업종(타이어·전기·통신·플랫폼) 값 단위로 처리.
- KSIC 공정명사 뽑기 C구조 (process_law_map, 거름망 통과분에 합치기 — "나중에 합한다").
- 보류 7,496(AMBIGUOUS) 줄이기 — 단 개인(누구든지/근로자) 위주라 빠짐 위험, 신중히.

## DB 변경 (3·4·5부 누적)
- `legal_sieve_rule`: stage(common_value로 통일), field_kind=executor, rule_kind=word
- 값 단위 2,230개 (BUSINESS 787 / AUTHORITY 680 / FRAGMENT 574 / DELEGATED 98 / SPECIAL 91). 패턴·비활성·중복 전부 삭제.
- 함수: sieve_executor(text), run_common_sieve(), diagnose_clauses_common()
- tai-api: legal_engine_adapter_run.py — DB 함수 호출 + .range() 페이지네이션 (커밋 7f37fe8, 69deaef)
