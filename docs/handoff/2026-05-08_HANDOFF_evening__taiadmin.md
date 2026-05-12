# HANDOFF 2026-05-08 evening — master_rule_v2 변환 진입 (DDL/코드 정정 후 전체 변환 직전)

> 오늘 후반 작업 — Phase B (semantic_clause → master_rule_v2 변환) 진입.
> 5개 점검 → DDL 정정 3개 → 코드 정정 4개 → dry-run 통과 → 전체 변환 직전.

---

## 0. CURRENT STATE (30초)

```yaml
last_action: dry-run sample 100 통과 (CHECK 제약 5개 모두 충족 예상)
next_action: |
  cd docs/extraction/scripts/
  railway run python3 convert_clause_to_rule.py --apply --sample-size 100000 2>&1 | tee /tmp/convert_apply.log
  
  ⚠️ 첫 라인이 "fetched semantic_clause: 58495 rows"인지 확인 (페이지네이션 정상)
  ⚠️ 1000 근처 숫자면 즉시 중단 (페이지네이션 사고 재발)

after_apply_completes:
  - 검증 SQL 8개 (LEGAL_RULE_PIPELINE.md § 5.5)
  - LEGAL_RULE_PIPELINE.md § 0/5/7/8 갱신
  - 작업지시서 정정 push (현재 작업지시서는 잘못된 컬럼명 + 잘못된 cycle_type 매핑 상태)

state_snapshot:
  semantic_clause:        58,495 v1.9.1 ✅
  master_rule_v2:         0 rows (DDL 정정 완료, 변환 대기)
  master_rule_executor:   0
  master_rule_condition:  0
  master_rule_exception:  0
  master_rule_relation:   0
```

---

## 1. 사용자 핵심 원칙 (오늘 확립)

1. **"열 개를 더 만드는 것보다 한 개를 놓치지 않는 게 중요"** — false negative 방지 우선
2. **"제외는 하지 않고, 전체를 다 작업하고, 사용 단계에서 어떻게 사용을 할지 결정"** — 데이터 레이어 보존, 비즈니스 로직 레이어 분리
3. **"분해기는 서버 보관 (운영 레포 push OK)"** — 법령 개정 시 재실행 필요한 파이프라인 자산
4. **"매핑 및 분해 과정까지 하나의 문서로 통합"** — 흩어진 작업지시서/PATTERN_MINING/HANDOFF 분산 금지
5. **"나보다 Claude가 이해하기 좋은 방식으로"** — 문서를 AI agent의 작업 시작점으로 최적화

이 5원칙이 오늘 후반 모든 결정의 기준.

---

## 2. 5개 점검 결과 → 변환 정책

### 점검 결과 종합

| 점검 | 결과 | 결정 |
|---|---|---|
| 1. None 698건 | 의무 어말 39건 보유 | 변환 포함 (rule_kind 역추론) |
| 2. DELEGATION 9,032건 | executor 보유 4,166 (정부 입법 행위) | rule_kind=DELEGATION 보존, 사용 단계 제외 |
| 3. DEFINITION 6,448건 | 의무 어말 106건 보유 | 변환 포함 (rule_kind 역추론) |
| 4. 룰 그룹화 | paragraph 단위 81% 단순 | 1:1 변환 OK |
| 5. scope 보강 | 10.2%만 키워드 보유 | Phase B 후속 (시행규칙 분해) |

### 변환 정책 (확정)

```yaml
모든_의미절_변환: true   # 제외 없음, 의미절 1 = 룰 1
rule_kind_보존: content_type 그대로 → master_rule_v2.rule_kind
None_DEFINITION_역추론: 의무/권한/금지 어말 보유 시 OBLIGATION/AUTHORITY/PROHIBITION으로 보정 (145건)
신뢰도: 옵션 B (핵심 4 base 0.7 + 보조 +0.075 each)
action_category: 14 (13 + 'other')
EXCEPTION: Phase B 무시 (5건뿐)
사물_주어: WHO NULL + needs_review
```

---

## 3. DDL 정정 (3개)

### 3.1 rule_kind 컬럼 추가 (오전)

```sql
ALTER TABLE master_rule_v2 
  ADD COLUMN rule_kind text NOT NULL DEFAULT 'UNCLASSIFIED';

ALTER TABLE master_rule_v2 
  ADD CONSTRAINT master_rule_v2_rule_kind_check 
  CHECK (rule_kind IN (
    'OBLIGATION','PROHIBITION','AUTHORITY',
    'DELEGATION','DEFINITION','STATEMENT','UNCLASSIFIED'
  ));

CREATE INDEX idx_mrv2_kind ON master_rule_v2(rule_kind);
CREATE INDEX idx_mrv2_kind_status ON master_rule_v2(rule_kind, status);
```

### 3.2 CHECK 제약 충돌 5개 발견 → DDL 3개 정정 (저녁)

`--apply` 첫 시도 시 발견된 충돌:
```
APIError: violates check constraint "master_rule_v2_action_category_check"
```

원인: 어제 만든 DDL (DESIGN_master_rule_v2_2026-05-07)과 오늘 작업지시서 불일치.

| 제약 | 어제 DDL | 작업지시서/코드 | 해결 |
|---|---|---|---|
| `action_category_check` | 13개 소문자 | 'OTHER' 등 14개 대문자 | DDL에 'other' 추가 |
| `cycle_consistency` | ONCE/ON_EVENT/DAILY/WEEKLY/MONTHLY/YEARLY | BASE_EVENT/RECURRING/INTERVAL/DUE | DDL에 'DUE' 추가 + 코드 매핑 |
| `sectors_nonempty` | array_length >= 1 | INACTIVE 161건 sectors=[] | DDL: NULL 또는 빈 배열 허용 |
| `sectors_valid` | 4개 (BUILDING/INDUSTRIAL/CONSTRUCTION/SPECIAL_FACILITY) | semantic_clause에 실제 같은 4개 | 그대로, COMMON 없음 확인 |
| `rule_kind_check` | 위 3.1에서 추가됨 | OK | 그대로 |

**DDL 3개 정정 적용** (migration: `fix_master_rule_v2_constraints_for_conversion`):

```sql
-- action_category에 'other' 추가
ALTER TABLE master_rule_v2 DROP CONSTRAINT master_rule_v2_action_category_check;
ALTER TABLE master_rule_v2 ADD CONSTRAINT master_rule_v2_action_category_check
  CHECK (action_category_code = ANY (ARRAY[
    'system_management','risk_assessment','education','inspection','measurement',
    'report','installation','recordkeeping','notification','action',
    'work_method','approval','protection','other'
  ]));

-- cycle_consistency에 'DUE' 추가
ALTER TABLE master_rule_v2 DROP CONSTRAINT master_rule_v2_cycle_consistency;
ALTER TABLE master_rule_v2 ADD CONSTRAINT master_rule_v2_cycle_consistency CHECK (
  when_cycle_type IS NULL
  OR when_cycle_type = 'ONCE'
  OR (when_cycle_type = 'ON_EVENT' AND when_base_event IS NOT NULL)
  OR (when_cycle_type = 'DUE' AND when_due_days IS NOT NULL)
  OR (when_cycle_type = ANY (ARRAY['DAILY','WEEKLY','MONTHLY','YEARLY']) 
      AND when_cycle_value IS NOT NULL AND when_cycle_unit IS NOT NULL)
);

-- sectors_nonempty 완화
ALTER TABLE master_rule_v2 DROP CONSTRAINT master_rule_v2_sectors_nonempty;
ALTER TABLE master_rule_v2 ADD CONSTRAINT master_rule_v2_sectors_nonempty CHECK (
  sectors IS NULL OR array_length(sectors, 1) >= 0
);
```

---

## 4. 코드 정정 (4개) — `convert_clause_to_rule.py`

### 4.1 페이지네이션 누락 (잠재 사고)

`--apply --sample-size 100000` 첫 시도 시 `fetched semantic_clause: 1000 rows`만. Supabase default 1000 limit. 분해기 v1.9.1 사고와 같은 패턴.

```python
# 정정: range(offset, offset + chunk - 1) 루프
def fetch_clauses(sample_size, start_from=0):
    all_clauses = []
    offset = start_from
    while len(all_clauses) < sample_size:
        chunk_size = min(1000, sample_size - len(all_clauses))
        def _do():
            return supabase.from_("semantic_clause").select(...).order("id")\
                .range(offset, offset + chunk_size - 1).execute()
        res = with_retry(_do)
        batch = res.data or []
        if not batch:
            break
        all_clauses.extend(batch)
        if len(batch) < chunk_size:
            break
        offset += chunk_size
    return all_clauses[:sample_size]
```

### 4.2 action_category_code 소문자

```python
def classify_action_category(action_text):
    if not action_text:
        return 'other'
    rules = [
        (r'점검|진단|검사|확인',         'inspection'),
        (r'위험성\s*평가|위해\s*평가',    'risk_assessment'),
        (r'교육|훈련',                    'education'),
        (r'측정|계측',                    'measurement'),
        (r'보고|신고|통보|통지|제출',     'report'),
        (r'설치|비치|구비',               'installation'),
        (r'기록|보존|작성|보관',          'recordkeeping'),
        (r'알림|고지|공지|공표',          'notification'),
        (r'조치|시정|개선|보호',          'action'),
        (r'작업\s*방법|작업\s*절차',      'work_method'),
        (r'승인|허가|인가|면허',          'approval'),
        (r'보호구|보호\s*장비|안전\s*장비', 'protection'),
        (r'체계|시스템|구축',             'system_management'),
    ]
    for pattern, code in rules:
        if re.search(pattern, action_text):
            return code
    return 'other'
```

### 4.3 when_cycle_type DDL 7값 매핑

```python
# BASE_EVENT/RECURRING/INTERVAL/DUE → ON_EVENT/YEARLY/MONTHLY/WEEKLY/DAILY/DUE
def parse_when(cycle_text, action_text):
    when = {...}
    
    # base_event (cycle_text 또는 action_text)
    if action_text:
        m = re.search(r'(작업\s*전|...|즉시|지체\s*없이)', action_text)
        if m:
            when['when_base_event'] = m.group(1)
            when['when_cycle_type'] = 'ON_EVENT'  # ← 'BASE_EVENT' 아님
    
    # 매년/매월/매주/매일
    m = re.search(r'매(년|월|주|일)', cycle_text)
    if m:
        type_map = {'년':'YEARLY','월':'MONTHLY','주':'WEEKLY','일':'DAILY'}
        when['when_cycle_type'] = type_map[m.group(1)]
        when['when_cycle_value'] = 1
        when['when_cycle_unit'] = unit_map[m.group(1)]
    
    # N년/N개월 마다 → YEARLY/MONTHLY
    # N일 이내 → DUE + due_days=N
```

### 4.4 sectors=[] 처리

```python
def get_sectors_for_rule(clause):
    """INACTIVE 161건은 sectors=[] (DDL 정정 후 허용)"""
    s = clause.get('sectors') or []
    return s if isinstance(s, list) else []
```

---

## 5. dry-run 검증 (sample 100, 통과)

### 출력 통계
```
[CONVERT] 100 clauses → 100 rules (1:1)         ✅
[INSERT 예정] master_rule_v2: 100 rows
[INSERT 예정] master_rule_executor: 114 rows (89 + 25 + 0)
[INSERT 예정] master_rule_condition: 49 rows
[INSERT 예정] master_rule_exception: 0 rows

rule_kind:
  OBLIGATION: 63
  AUTHORITY:  15
  DELEGATION: 15
  DEFINITION:  6
  PROHIBITION: 1

confidence avg: 0.71
needs_review:   48 / 100 (48.0%)
```

### sample 5건 검증

| # | rule_kind | action_category | when | sectors | 검증 |
|---|---|---|---|---|---|
| 1 | AUTHORITY | other | NULL | [BUILDING, CONSTRUCTION] | ✅ |
| 2 | OBLIGATION | inspection | NULL | [BUILDING, INDUSTRIAL] | ✅ |
| 3 | OBLIGATION | report | NULL | [BUILDING] | ✅ |
| 4 | OBLIGATION | report | NULL | [BUILDING, INDUSTRIAL] | ✅ |
| 5 | OBLIGATION | report | **ON_EVENT/즉시** | [BUILDING, INDUSTRIAL, CONSTRUCTION] | ⭐ base_event 정확 |

→ 모든 CHECK 제약 (5개) 통과 예상. 전체 변환 진행 가능.

---

## 6. 전체 변환 명령 + 모니터링

```bash
cd docs/extraction/scripts/

railway run python3 convert_clause_to_rule.py --apply --sample-size 100000 2>&1 | tee /tmp/convert_apply.log
```

### ⚠️ 첫 라인 체크포인트 (페이지네이션 검증)

```
[INFO] fetched semantic_clause: 58495 rows  ← 정상
[INFO] fetched semantic_clause: 1000 rows   ← 사고, 즉시 중단
```

### 정상 진행 패턴

```
[INFO] fetched semantic_clause: 58495 rows
[CONVERT] 58495 clauses → 58495 rules (1:1)
[INSERT] master_rule_v2: 58495 rows
[INSERT] master_rule_executor: ~67000 rows
[INSERT] master_rule_condition: ~28500 rows
[INSERT] master_rule_exception: 5 rows
[STATS] rule_kind: ...
[DONE]
```

### 사고 가능 패턴
- CHECK 위반 → 잡힌 row content 분석
- timeout → batch_size 줄이기
- partial INSERT → master_rule_v2 truncate 후 재시도

```sql
-- 재변환 전 truncate (필요 시 Supabase MCP로)
TRUNCATE master_rule_relation, master_rule_exception, master_rule_condition, 
         master_rule_executor, master_rule_v2 CASCADE;
```

---

## 7. 변환 완료 후 검증 SQL 8개

`LEGAL_RULE_PIPELINE.md § 5.5` 그대로:

```sql
-- 1. row 수 = 58,495
SELECT COUNT(*) FROM master_rule_v2;

-- 2. rule_kind 분포 (None 698 → UNCLASSIFIED, 또는 의무 어말 145 역추론)
SELECT rule_kind, COUNT(*) FROM master_rule_v2 GROUP BY 1 ORDER BY 2 DESC;

-- 3. FK 무결성
SELECT COUNT(*) FROM master_rule_v2 mrv
LEFT JOIN semantic_clause sc ON mrv.source_clause_id = sc.id
WHERE sc.id IS NULL;
-- 예상: 0

-- 4. master_rule_executor 분포
SELECT role, COUNT(*) FROM master_rule_executor GROUP BY 1;

-- 5. master_rule_condition 행 수
SELECT COUNT(*) FROM master_rule_condition;

-- 6. action_category 분포 (14값)
SELECT action_category_code, COUNT(*) FROM master_rule_v2 GROUP BY 1 ORDER BY 2 DESC;

-- 7. confidence 분포
SELECT 
  CASE 
    WHEN generation_confidence >= 0.85 THEN 'high'
    WHEN generation_confidence >= 0.7 THEN 'medium'
    ELSE 'low'
  END AS bucket,
  COUNT(*)
FROM master_rule_v2 GROUP BY 1;

-- 8. sectors 보존
SELECT COUNT(*) FROM master_rule_v2 WHERE sectors IS NULL OR sectors = '{}';
-- 예상: 161 (INACTIVE)
```

---

## 8. 변환 후 통합 문서 갱신 (예정)

### LEGAL_RULE_PIPELINE.md
- § 0 CURRENT STATE — pipeline_status.step_3_mapping: pending → done
- § 2.3 master_rule_v2 — 0 rows → 58,495
- § 5 STEP 3 — 매핑 정확 통계로 갱신
- § 7 INCIDENT LOG — CHECK 제약 5개 충돌 + 페이지네이션 사고 추가
- § 8 VERSION HISTORY — convert_clause_to_rule.py v1.0 추가

### 작업지시서 (CURSOR_TASK_2026-05-08_convert_clause_to_rule.md)
- § 4 rule_code 생성: `law_id` (not `source_law_id`) + `law_master.law_name` JOIN 정정
- § 5 action_category: 소문자 14개 명시
- § 6 when 파싱: DDL 7값 매핑으로 정정
- § 9 argparse: 페이지네이션 처리 추가

---

## 9. INCIDENTS (오늘)

### 9.1 분해기 --sample-size default 50 (오전, 복구 완료)

`decompose_v1.py --apply` 시 50건만 INSERT. argparse default 50 인줄 모름.

복구: `TRUNCATE iter1; INSERT iter1 SELECT * FROM semantic_clause` + `--sample-size 100000` 명시 재실행.

### 9.2 작업지시서의 잘못된 컬럼명 (저녁, 복구 완료)

`fetch_article_meta`에서 `law_article.source_law_id` SELECT 시도 → 컬럼 없음 에러. 실제 컬럼명은 `law_id`.

복구: Cursor 패치 — `law_id` 사용 + `law_master.law_name` JOIN.

### 9.3 CHECK 제약 5개 충돌 (저녁, 복구 완료)

`--apply` 시도 시 `action_category_check` violation. DDL은 13개 소문자, 코드는 14개 대문자.

복구: DDL 3개 정정 + 코드 4개 정정.

### 9.4 페이지네이션 누락 (저녁, 복구 완료)

`sample_size=100000` 줬는데 `fetched 1000 rows`만. Supabase default 1000.

복구: range(offset, offset+chunk-1) 루프.

### 학습

이 4개 사고 모두 같은 패턴:
- **DDL/실제 스키마 vs 작업지시서/코드 불일치** — 작업지시서 작성 시 실제 DDL을 확인 안 함
- **외부 도구 default값** — argparse default, Supabase default limit

다음에는:
1. 작업지시서 작성 전 `information_schema.columns` + CHECK 제약 모두 확인
2. argparse default는 명시적 (sample_size=58500 또는 --all 옵션)
3. Supabase fetch는 항상 페이지네이션 가정

---

## 10. 다음 세션 시작 방식

**프롬프트**:
> `docs/extraction/HANDOFF_2026-05-08_evening.md` 보고 § 0 CURRENT STATE의 next_action 진행.

또는:
> 어제 evening 핸드오프 보고 master_rule_v2 변환 진행. dry-run 통과한 상태에서 전체 변환 명령부터.

---

## 11. 참조 문서 (변경 사항 반영 후)

```
docs/extraction/
├── LEGAL_RULE_PIPELINE.md           # 통합 마스터 (변환 완료 후 갱신 예정)
├── HANDOFF_2026-05-08.md            # v1.9.1 본 적용 핸드오프
├── HANDOFF_2026-05-08_evening.md    # 본 문서 (Phase B 진입)
│
├── CURSOR_TASK_2026-05-08_convert_clause_to_rule.md  # 작업지시서 (정정 예정)
├── CURSOR_TASK_2026-05-08_decompose_v18_v2.md
├── CURSOR_TASK_2026-05-08_decompose_v19.md
├── CURSOR_TASK_2026-05-08_decompose_v191.md
│
├── PATTERN_MINING_2026-05-08.md
├── PATTERN_MINING_2026-05-08_v2.md
│
├── DESIGN_master_rule_v2_2026-05-07.md   # 어제 5 테이블 스키마 (v1)
│
└── scripts/
    ├── decompose_v1.py                    # v1.9.1
    └── convert_clause_to_rule.py          # v1.0 (오늘 작성)
```

---

## 작업 원칙 (불변, 오늘 추가 1개 포함)

1. AI/LLM 호출 0%
2. 검증 없는 완료 선언 금지
3. 패턴 발견 → 룰 보강 → 재반복
4. **누락 (false negative) 방지가 잘못 변환보다 어렵다** ⭐ 오늘 사용자 원칙
5. **모든 의미절 변환, 사용 정책은 사용 단계 (View)** ⭐ 오늘 사용자 원칙
6. ask_user_input_v0 사용 금지
7. 200줄+ 파일은 GitHub MCP 직접 수정 금지 → Cursor 로컬
8. 분해기는 운영 레포 보관 (파이프라인 자산) ⭐ 오늘 정정
9. 본 적용 전 안전망 복구 필수
10. **--sample-size 등 default 명시 + Supabase 1000 limit 가정** ⭐ 오늘 사고 학습
11. **작업지시서 작성 전 DDL CHECK 제약 모두 확인** ⭐ 오늘 사고 학습
12. **AI agent 친화 문서 (사람보다 다음 Claude가 빠르게 파악)** ⭐ 오늘 사용자 원칙
