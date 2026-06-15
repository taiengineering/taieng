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
- 보류(매칭 0): 2,968
- **단일 룰 매칭(순서 무관): 2,229**
- 여러 룰 같은 verdict: 0
- **여러 룰 다른 verdict(순서 영향): 0**
- → **현재 거름망은 순서 영향 0.** 값 단위(exact)라 한 값이 정확히 한 룰에만 매칭.
  priority가 결과를 바꾸는 룰이 하나도 없음.

### 의미
- **지금**: priority는 사실상 무의미(장식). 순서 바꿔도 결과 동일 → 룰 추가/삭제 시 순서 신경 안 써도 됨.
- **나중**: clause_sector 거름·패턴 룰을 더해 "한 값이 두 룰에 충돌"하면 그때 순서가 생김.
  그 룰만 order_sensitive=true로 박음 → "이 룰은 순서 중요, 건드릴 때 조심"이 한눈에.

### 적용
- 컬럼 `order_sensitive boolean DEFAULT false` 추가. 현 word 룰 전부 false(측정 근거).
- 향후 충돌 가능 룰(패턴/교차 field) 추가 시 true 표시.

---

## 거름망 최종 구조 (6부 시점)
```
구분값: field_kind=executor / rule_kind=word / order_sensitive=false (전부)
stage=common_value, 2,230개 값 룰:
  [DROP] AUTHORITY 680 / SPECIAL_FACILITY 91 / DELEGATED_ORG 98 / FRAGMENT 574  → rule_id 추적
  [KEEP] BUSINESS 787  → 값 단위
  [보류] 미매치 = KEEP_REVIEW (빠짐없이)
순서 영향 0 (priority 무의미, 안심하고 룰 추가/삭제 가능)
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
