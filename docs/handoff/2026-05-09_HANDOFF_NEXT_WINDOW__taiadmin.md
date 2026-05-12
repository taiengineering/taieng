# [Track B] Week 2 — admrule-kr 매핑 핸드오프 (다음 창 인계)

**작성일**: 2026-05-09  
**선행**: Track B Day 1 본질 작업 97% 완료 (Master Handoff v1.3)  
**대상**: 다음 Claude 회의실 창 (admrule-kr 매핑 진행)

---

## 1. 본 핸드오프의 위치

```
[Track B 영역]
├ ✅ Step 1 가족 매핑 (366건, 97.8% verified)
├ ✅ Step 2 위임 관계 (delegation 7,730 + inheritance 15,850 + citation_purpose 8 분류)
├ ✅ Step 3 외부 인용 (citation 7,179)
├ ✅ Step 2-F 룰 V2 보강 (1.83배)
├ ✅ Step 2-G citation_purpose 8 카테고리
└ 🔄 Week 2 admrule-kr 행정규칙 매핑 ← 본 핸드오프 시작점
```

**진행 단계**:
- ✅ admrule-kr clone 완료 (사용자)
- ✅ 디렉토리 구조 분석 완료
- ✅ frontmatter CSV 추출 완료 (20,877 row)
- 🔄 **현재**: railway run INSERT 실행 대기
- ⏳ 다음: 매핑 SQL 실행 (3 룰)
- ⏳ 검증 + 보고서 + Master Handoff v1.4

---

## 2. admrule-kr 분석 결과

### 2.1 디렉토리 구조 (legalize-kr와 다름)

```
admrule-kr/
├ {부처명}/
│ ├ _본부/
│ │ ├ 고시/{행정규칙명}/제정.md
│ │ ├ 훈령/{행정규칙명}/제정.md
│ │ ├ 예규/{행정규칙명}/제정.md
│ │ └ 공고/{행정규칙명}/제정.md
│ └ {외청명}/  (예: 조달청, 관세청, 국세청)
│   └ {rule_type}/{행정규칙명}/...
```

### 2.2 frontmatter 형식 (가장 중요)

```yaml
---
행정규칙ID: '81288'
행정규칙일련번호: '2100000275652'  ← 13자리 MST = TAI law_mst_no 1:1 매칭 ★
행정규칙명: '노동위원회 위임전결규정'  ← TAI law_name과 매칭 가능
행정규칙종류: '훈령'                   ← 고시/훈령/예규/지침/국무총리훈령/대통령훈령/공고/기타
상위기관명: '고용노동부'
소관부처명: '중앙노동위원회'
기관경로: ['고용노동부', '중앙노동위원회']
---
```

### 2.3 CSV 추출 결과 (사용자 작업 완료)

```
Found 21,026 .md files
Extracted 20,877 rows to admrule_kr_mapping.csv
Skipped: 149 (frontmatter 없는 파일)

Rule type 분포:
  고시: 10,258
  훈령: 6,267
  예규: 3,836
  공고: 204
  지침: 165
  국무총리훈령: 97
  대통령훈령: 42
  기타: 8

Ministry 분포 (top 10):
  국무총리: 3,441
  농림축산식품부: 1,897
  기후에너지환경부: 1,877
  해양수산부: 1,691
  행정안전부: 1,456
  문화체육관광부: 1,447
  국토교통부: 1,444
  산업통상부: 1,336
  보건복지부: 1,132
  과학기술정보통신부: 993

[OK] 모든 MST 13자리 숫자
```

---

## 3. TAI 행정규칙 386건 (매핑 대상)

| law_type_code | cnt | 분포 |
|---|---|---|
| NOTICE | 340 | 국가기술표준원 81 / 소방청 62 / 기후에너지환경부 28 / 산업통상부 24 / 화학물질안전원 24 / 국토교통부 23 / 행정안전부 23 / 고용노동부 18 / 등 |
| STANDARD | 42 | 국립소방연구원 40 / 산업통상부 2 |
| OTHER | 4 | 기후에너지환경부 2 / 조달청 1 / 원자력안전위원회 1 |

**TAI MST 패턴**: 모두 13자리 (`2100000` prefix + 6자리, 예: `2100000254546`)

---

## 4. 사전 준비 완료 사항

### 4.1 DB 테이블 (적용 완료)

```sql
CREATE TABLE admrule_kr_mapping_raw (
  id SERIAL PRIMARY KEY,
  directory_path text NOT NULL,
  directory_name text,
  filename text NOT NULL,
  fm_title text,                    -- 행정규칙명
  rule_type text,                   -- 고시/훈령/예규/...
  ministry_name text,               -- 상위기관명
  legal_mst text,                   -- 13자리 MST
  issue_number text,
  source_file text,
  created_at timestamptz DEFAULT now()
);
-- 인덱스: directory_name, filename, legal_mst, ministry_name, rule_type, fm_title
```

### 4.2 Scripts (commit 완료)

| 파일 | 위치 | 용도 |
|---|---|---|
| `extract_admrule_csv.py` | `docs/extraction/v3/scripts/` | frontmatter → CSV (사용자 실행 완료) |
| `insert_admrule_kr_mapping_raw.py` | `docs/extraction/v3/scripts/` | CSV → DB INSERT (railway run 대기) |

**CSV 파일**: `~/Desktop/tai-engineering/admrule-kr/admrule_kr_mapping.csv` (20,877 row)

### 4.3 Heredoc 명령 (사용자 화면에 이미 제공됨)

다음 창에서 사용자에게 **재안내 X** — 사용자 직전 작업이 INSERT 실행이므로:

```bash
# 사용자가 다음 명령 실행 후 결과 공유:
cd /Users/taiwangsim/Desktop/tai-engineering/tai-api
railway run python3 /Users/taiwangsim/Desktop/tai-engineering/admrule-kr/insert_admrule_kr_mapping_raw.py
```

**예상 결과**:
```
Using Supabase URL: https://vwlahtguyggrhvslabax.supabase.co
CSV rows: 20877
Batch 1 (1-100): ok (100 rows)
Batch 3 (201-300): ok (100 rows)
Batch 20 (1901-2000): ok (100 rows)
... (대략 10분 소요)
Batch 209 (20801-20877): ok (77 rows)

Inserted rows: 20877
admrule_kr_mapping_raw COUNT(*): 20877
```

---

## 5. 다음 작업 — 매핑 SQL 실행

### 5.1 매핑 룰 (3개)

| 룰 | 매칭 키 | 정확도 (예상) |
|---|---|---|
| **룰 1** | `행정규칙일련번호` (13자리) ↔ `law_mst_no` 1:1 | **95%+** |
| **룰 2** | 행정규칙명 정규화 ↔ law_name | 보강 (룰 1 실패 시) |
| **룰 3** | 부처+종류+이름 | 추가 보강 |

### 5.2 매핑 SQL (다음 창에서 실행)

**Step A: 매칭률 사전 측정**

```sql
-- TAI 386 행정규칙 ↔ admrule-kr 매칭률
WITH tai_admrule AS (
  SELECT id, law_mst_no, law_name, law_type_code, ministry_name
  FROM law_master
  WHERE law_type_code IN ('NOTICE', 'STANDARD', 'OTHER')
)
SELECT 
  COUNT(*) AS total,
  -- 룰 1: 13자리 MST 매칭
  SUM(CASE WHEN EXISTS (
    SELECT 1 FROM admrule_kr_mapping_raw 
    WHERE legal_mst = t.law_mst_no
  ) THEN 1 ELSE 0 END) AS rule1_mst,
  -- 룰 2: fm_title 매칭
  SUM(CASE WHEN EXISTS (
    SELECT 1 FROM admrule_kr_mapping_raw 
    WHERE REGEXP_REPLACE(fm_title, '\s+', '', 'g') 
        = REGEXP_REPLACE(t.law_name, '\s+', '', 'g')
  ) THEN 1 ELSE 0 END) AS rule2_title
FROM tai_admrule t;
```

**Step B: PRIMARY (행정규칙 자체) 매핑 INSERT**

행정규칙은 보통 본법의 종속이지만 일부는 독립적. law_family_mapping에 ADMINISTRATIVE_RULE family_role로 INSERT.

```sql
-- 행정규칙 PRIMARY INSERT (본법 위임받은 행정규칙)
-- family_role = 'ADMINISTRATIVE_RULE', parent_law_id는 본문 추출 또는 NULL
INSERT INTO law_family_mapping (
  law_master_id, parent_law_id, family_role, mapping_method, verified, mapping_notes
)
SELECT 
  lm.id,
  NULL,  -- parent는 본문 추출 후 채움 (Step C)
  'ADMINISTRATIVE_RULE',
  'admrule_kr_mst',
  true,
  'admrule-kr 매핑: ' || akr.fm_title || ' (' || akr.rule_type || ')'
FROM law_master lm
JOIN admrule_kr_mapping_raw akr ON akr.legal_mst = lm.law_mst_no
WHERE lm.law_type_code IN ('NOTICE', 'STANDARD', 'OTHER')
ON CONFLICT (law_master_id) DO NOTHING;
```

**Step C: parent_law_id 본문 추출 (검증 엔진 V1-A 재활용)**

```sql
-- 행정규칙 본문 article 1, 2에서 「~법」(이하 "법") 패턴 추출 → 본법 매핑
-- 룰 V1-A 패턴 3개 모두 적용 (Day 3과 동일)
```

**Step D: STANDARD 155 + NOTICE 11 자동 해소** (Step 2-A delegation target_law_id 미해소)

```sql
-- delegation의 STANDARD/NOTICE target_law_id 자동 매핑
-- source_law의 가족 + 행정규칙 부처 매칭
UPDATE law_article_delegation lad
SET target_law_id = (
  SELECT akr_lm.id 
  FROM admrule_kr_mapping_raw akr
  JOIN law_master akr_lm ON akr_lm.law_mst_no = akr.legal_mst
  WHERE akr_lm.law_type_code = lad.delegation_target_type
    AND akr.ministry_name = (SELECT ministry_name FROM law_master WHERE id = lad.source_law_id)
  LIMIT 1
)
WHERE lad.delegation_target_type IN ('STANDARD', 'NOTICE')
  AND lad.target_law_id IS NULL;
```

### 5.3 검증 (산안법 행정규칙 sample)

```sql
-- 산안법 가족 + 행정규칙 통합 조회 (Stage 분해 시 활용 패턴)
SELECT 
  child.law_name,
  child.law_type_code,
  lfm.family_role,
  lfm.mapping_method,
  parent.law_name AS parent
FROM law_family_mapping lfm
JOIN law_master child ON child.id = lfm.law_master_id
LEFT JOIN law_master parent ON parent.id = lfm.parent_law_id
WHERE child.domain_code = 'INDUSTRIAL_SAFETY'
ORDER BY 
  CASE child.law_type_code 
    WHEN 'LAW' THEN 1 
    WHEN 'ENFORCEMENT_DECREE' THEN 2 
    WHEN 'ENFORCEMENT_RULE' THEN 3 
    WHEN 'NOTICE' THEN 4 
    WHEN 'STANDARD' THEN 5 
    ELSE 6 
  END,
  child.law_name;
```

---

## 6. 사용자 원칙 (필수 정합)

| 원칙 | 적용 방식 |
|---|---|
| LLM 사용 X | ✓ 정규식 + ground truth만 (admrule-kr) |
| 법령 보전 | ✓ 직접 인용만 |
| 놓치는 것 = 리스크 | ✓ 386/386 매핑 목표 (TAI MST와 admrule-kr legal_mst 1:1) |
| 100% 매핑 | ✓ 룰 1 + 룰 2 + 룰 3 결합 |
| 오염 = 폐기 | ✓ TRUNCATE 후 재시도 |
| **검증도 엔진** | ✓ admrule-kr ground truth + 본문 추출 cross-validation |
| **추정 매핑 금지** | ✓ admrule-kr legal_mst 직접 매칭 우선 |

---

## 7. 산출물 (Track B 본질 작업, 다음 창 시작 시 인계)

### 7.1 DB 테이블 (8개)

| 테이블 | row | 의미 |
|---|---|---|
| `law_family_mapping` | 366 | 가족 (PRIMARY/시행령/시행규칙) — Week 2에 +386 ADMINISTRATIVE_RULE 추가 예정 |
| `law_article_delegation` | 7,730 | 위임 source-of-truth |
| `law_article_inheritance` | 15,850 | 자식→부모 인용 + 8 카테고리 분류 |
| `law_article_citation` | 7,179 | 외부 법령 인용 |
| `legalize_kr_mapping_raw` | 5,667 | legalize-kr ground truth |
| **`admrule_kr_mapping_raw`** | **0 (INSERT 대기)** | **admrule-kr ground truth (예정 20,877)** |
| `law_family_mapping_backup_20260509_v3_attempt1` | 366 | Day 1+2 폐기 백업 |
| `law_article_delegation_backup_20260509_v1` | 6,498 | 1차 INSERT 백업 |

### 7.2 View (2개)

- `v_law_family` — 가족 통합 조회
- `v_law_family_tree` — 본법 기준 가족 트리

### 7.3 검증 엔진 V1 — 5 룰

| 룰 | 입력 | 산출 |
|---|---|---|
| V1-A | 시행령/규칙/행정규칙 본문 | 자기 정의 패턴 (97.8% verified) |
| V1-B | legalize-kr 5,667 row | 가족 매핑 ground truth |
| V1-C | delegation × inheritance | cross-validate 86.5%~86.6% |
| V1-D | citation 7,179 row | TAI 추가 수집 우선순위 |
| V1-E | inheritance 직후 30자 | citation_purpose 8 분류 |

---

## 8. 다음 창 시작 시 첫 메시지 (사용자에게)

> **"Track B 다음 창입니다. admrule-kr INSERT 실행 결과 (Inserted rows + COUNT) 공유 부탁드립니다. 받으면 즉시 매핑 SQL 진행하겠습니다."**

---

## 9. 작업 흐름 (다음 창에서)

```
1. 사용자: railway run insert 결과 공유
   ↓
2. 매칭률 사전 측정 (룰 1 + 룰 2)
   ↓
3. PRIMARY ADMINISTRATIVE_RULE INSERT
   ↓
4. 본문 추출로 parent_law_id 채우기 (V1-A 재활용)
   ↓
5. STANDARD/NOTICE delegation target_law_id 자동 해소 (Step 2-A)
   ↓
6. 검증 (산안법 행정규칙 sample, 정의/구조/적용 분포)
   ↓
7. 보고서 push: docs/extraction/v3/log/Track_B_20260509_Week2.md
   ↓
8. Master Handoff v1.4 update (§17 신설 — Week 2 결과)
```

---

## 10. 참고 — 대화 chronology

다음 창에서 컨텍스트 빠르게 복원하려면 보고서 7건 읽기:

```
docs/extraction/v3/log/
├ Track_B_20260509.md           (Day 1 폐기 전)
├ Track_B_20260509_Day2.md      (Day 2 폐기 전)
├ Track_B_20260509_Day3.md      (Day 3 가족 매핑 ★)
├ Track_B_20260509_Step2.md     (위임 관계 ★)
├ Track_B_20260509_Step2E_Step3.md (cross-validate + 외부 인용 ★)
├ Track_B_20260509_Step2F.md    (룰 V2 보강 ★)
└ Track_B_20260509_Step2G.md    (citation_purpose 8 분류 ★)

docs/extraction/v3/MASTER_HANDOFF.md (v1.3) ★ — 우선 읽기
```

---

## 11. 주의사항

1. **사용자 INSERT 실행 결과 받기 전 매핑 SQL 실행 X** — admrule_kr_mapping_raw에 데이터 없는 상태로 매핑하면 모두 0 매칭
2. **TRUNCATE는 반드시 백업 먼저** — 사용자 원칙 정합
3. **사용자 검증 작업 0건** — 자동 매핑 + cross-validate 엔진만 사용
4. **다음 창에서 즉시 진행 가능** — 모든 사전 준비 완료, INSERT 결과만 받으면 됨

---

**END OF HANDOFF** — 다음 창에서 본 문서 + Master Handoff v1.3 + 보고서 7건 참조
