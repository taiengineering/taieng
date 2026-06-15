# 2026-06-14 (3부) 거름망 DB+함수 전환 + 값 단위 전개 + 구분값

## 한 줄 요약
거름망을 **소스(Python) 처리 → DB+함수 처리**로 전환. 묶음 규칙을 **값 단위(한 값=한 망)**로
전개해 추적 가능하게. 규칙 정체를 **구분값(field_kind/rule_kind/order_sensitive)**으로 박아 재해석 불필요.

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
[테이블] legal_sieve_rule (stage=common_value, 값 단위)
[함수] sieve_executor(executor) → (class_label, decision, rule_id, priority, match_kind)
        priority 순 첫 매치, exact>contains>regex. 미매치=0행(보류, 빠짐없이).
[함수] run_common_sieve() → 분포 측정
[함수] diagnose_clauses_common() → 진단(KEEP+보류, DROP 제외)
```

---

## 3. 구분값 박기 (대표 요청: 나중에 해석 안 하게)

### 추가 컬럼 (한 룰이 다섯 값으로 완전히 읽힘 — 재해석 불필요)
- **field_kind**: 무엇을 보나 — executor / clause_sector / condition …
- **rule_kind**: 단어냐 패턴이냐 — word(exact, 한 값) / pattern(regex, 어미·형태)
- **order_sensitive**: 순서(priority) 영향 여부 (6부 참조)
- class_label: 섹션 / verdict: 처분
- 예: `executor / word / order_sensitive=false / AUTHORITY / DROP`

---

## 4부: 전 거름망 값 단위화 완성 + 1000행 버그 해결

### ★ 대표 원칙: "원칙 1에 1룰. 나중에 합한다."
- 실제 진단에서 KEEP가 전부 rule 24(BUSINESS 묶음)에 걸림 → 추적 불가. "수도사업자/가스사업자"
  (비고객 업종)가 rule 24 "사업자"에 걸려 KEEP. → BUSINESS도 1룰=1값으로 전개.
- BUSINESS 패턴(860값)·FRAGMENT 패턴 모두 값 전개 → 패턴 룰 전부 삭제. 거름망 전체 word 단위.

### 1000행 버그 해결 (PostgREST RPC 제한)
- 함수가 DROP 제외 KEEP+보류만 반환 + Python .range() 페이지네이션.
- 검증: 실제 진단 13,971건(KEEP 6,475+보류 7,496). rule_id 추적 작동.
- KEEP 잔존 비고객 업종(타이어·전기·통신·플랫폼)은 정상 — 공용은 "사업장 주체냐"만. 섹터는 다음.

---

## 5부: 분해 후 원본 삭제 + common_value 통일
- 대표 원칙 "분해 후 기존 것 삭제": 비활성 sector 룰 6개 삭제, common FRAGMENT 중복 21개 삭제,
  '벌금' common_value 이동. 모든 룰 stage=common_value/word. 패턴·비활성·중복·폐기잔재 0.
- 최종 2,230개: BUSINESS 787 / AUTHORITY 680 / FRAGMENT 574 / DELEGATED 98 / SPECIAL 91.

---

## 6부: 순서 영향 구분값 (order_sensitive)

### ★ 대표 요청: "순서에 영향 있는 것과 없는 것을 구분할 수 있다면 그 값도 구분 필요"

### 측정 (실제 데이터 5,197개 distinct executor)
- 보류(매칭 0): 2,968 / **단일 룰 매칭(순서 무관): 2,229** / 여러 룰 다른 verdict(순서 영향): **0**
- → **현재 거름망은 순서 영향 0.** 값 단위(exact)라 한 값이 정확히 한 룰에만 매칭. priority 무의미.

### 의미
- **지금**: priority 무의미(장식). 순서 바꿔도 결과 동일 → 룰 추가/삭제 시 순서 신경 안 써도 됨.
- **나중**: clause_sector·패턴 룰 더해 "한 값이 두 룰 충돌"하면 그 룰만 order_sensitive=true.
- 컬럼 `order_sensitive boolean DEFAULT false` 추가. 현 word 룰 전부 false.

---

## 7부: ★ 거름 데이터는 정방향 전용 — 체크엔진 검증룰 아님 (대표 확정)

### 질문 (대표)
- "이걸 다 만들면 공식으로 변형이 가능하겠다. 이 데이터는 검증룰이 되는가?"

### 답 (확정)
- **공식으로 변형 가능 → 맞음.** `sieve_executor()` 함수가 그 공식. 데이터(값 룰)=변수, 함수=고정.
  규칙을 데이터로 분리했기에 함수는 고정이고 데이터만 바꾸면 판정이 바뀜(rules-as-code).
- **이 데이터가 검증룰인가 → 아니오.** 거름 데이터(legal_sieve_rule)는 **정방향 전용**.
  - 이유(대표): **"체크엔진은 원본(법조문)까지 쫓아간다."**
  - 거름 데이터는 원본이 아니라 **원본에서 추출한 파생 판정**(executor→처분). 이걸 검증 기준으로
    쓰면 "추출 결과로 추출을 검증하는" **순환**이 됨. 검증은 원본 기준이어야 함.
- **거름 데이터의 정확한 용도**: 입력 → 의무 거르기/뽑기 (정방향). 여기까지.
- **검증(체크엔진)**: 별개 메커니즘. 원본(법조문)까지 추적해 대조. 거름 데이터 안 씀.
  (메모리: 체크엔진=services/check_engine.py, 범용·무판단·무데이터 코어, 45cm API 연결 예정)
- **단, 활용 여지**: 거름 데이터는 검증 *기준*은 못 되나, 검증 *대상을 좁히는 전처리*로는 가능.
  체크엔진의 원본 추적은 비싸므로 "거름 KEEP분만 원본 검증" → 효율. 거름=1차필터, 체크엔진=원본 정밀.

### 박아두는 못 (잘못된 길 방지)
- **거름 데이터를 체크엔진 검증룰로 쓰지 말 것.** 파생 판정이라 순환. 검증은 원본 추적이 정본.

---

## 거름망 최종 구조 (7부 시점)
```
구분값: field_kind=executor / rule_kind=word / order_sensitive=false (전부)
stage=common_value, 2,230개 값 룰:
  [DROP] AUTHORITY 680 / SPECIAL_FACILITY 91 / DELEGATED_ORG 98 / FRAGMENT 574  → rule_id 추적
  [KEEP] BUSINESS 787  → 값 단위
  [보류] 미매치 = KEEP_REVIEW (빠짐없이)
순서 영향 0 (priority 무의미)
용도: 정방향 전용(거르기/뽑기). 체크엔진 검증룰 아님(원본 추적이 정본).
[함수] sieve_executor() / run_common_sieve() / diagnose_clauses_common()
실제 진단 = 13,971건(KEEP 6,475 + 보류 7,496), DROP은 DB에서 제외.
```

## 다음
- 섹터 거름 설계 (공용 다음, 통째거름 아님). 비고객 업종 값 단위로 처리. ← order_sensitive=true 첫 등장 예상.
- KSIC 공정명사 뽑기 C구조 (process_law_map, 거름망 통과분에 합치기 — "나중에 합한다").
- 보류 7,496 줄이기 — 개인(누구든지/근로자) 위주라 빠짐 위험, 신중히.

## DB 변경 (3~6부 누적)
- `legal_sieve_rule`: stage=common_value, field_kind=executor, rule_kind=word, order_sensitive=false
- 값 단위 2,230개. 패턴·비활성·중복 전부 삭제.
- 함수: sieve_executor(text), run_common_sieve(), diagnose_clauses_common()
- tai-api: legal_engine_adapter_run.py — DB 함수 호출 + .range() 페이지네이션 (커밋 7f37fe8, 69deaef)
