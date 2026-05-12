# [Cursor 위탁] Phase 2.1 — rule_classify_subtype 전체 23 룰 철저한 재설계

**작성일**: 2026-05-10  
**작성자**: PM 창 (Claude 기획창)  
**위탁 대상**: Cursor (TAI Backend / Railway 환경)  
**선행 결정**: 사용자 PM 결정 — "철저한 재설계 (Kiwi sample 100+ 점검 후 전체 23 룰 재작성)"  
**선행 인계**: `Cursor_Stage_1_2_Phase_2_Spec.md` (Phase 2.0 명세) + Phase 2 실행 보고서 (commit `49d1eed2`, push 대기)

---

## 0. 본 명세의 위치

### 0.1 Phase 2.0 결과 (DB ground truth 확정)

| 지표 | 임계 | 실측 | 결과 |
|---|---|---|---|
| Stage 1 tokenization_json | ≤0.1% NULL | **0.00%** | ✅ PASS |
| Stage 1 split_rule_id | ~95% NULL | **100% NULL** | ⚠️ INFO |
| **Stage 2 sub_type 분류율** | **≥70%** | **5.62%** | ❌ **FAIL** |
| 100조문 sample | ≥70% | 6.54% | ❌ FAIL |
| 6하원칙 executor | ≥50% | 34.99% | ❌ FAIL |
| 6하원칙 what | ≥50% | **58.09%** | ✅ PASS |

→ **분류율 5.62%는 Phase 1 baseline 5.41% 대비 +0.21%p만 증가**. 23 룰 중 6 룰 0건 매칭.

### 0.2 PM 창 진단 결과 (마스터 §2.7/§2.8 정합 — DB가 ground truth)

PM 창에서 sample 6건 직접 점검 후 발견한 **본질 원인 4가지**:

| # | 본질 원인 | 룰 작성 (시안) | Kiwi 실제 출력 |
|---|---|---|---|
| 1 | 자모 종성 표기 불일치 ★ | `ㄹ/ETM` (한글 자음 U+3139) | **`ᆯ/ETM`** (conjoining jamo U+11AF) |
| 2 | 자모 종성 표기 불일치 ★ | `ㄴ/ETM` (한글 자음 U+3134) | **`ᆫ/ETM`** (conjoining jamo U+11AB) |
| 3 | EF 어미 통합 토큰의 자모 | `ㄴ다/EF` | **`ᆫ다/EF`** (자모 종성으로 시작) |
| 4 | NNB/NNG 통합 차이 | `자/NNB` | 케이스별: `자/NNB` 또는 `자가/NNG` (격조사 통합) 또는 `한/MM` |

**0건 룰 6개 본질 원인**:
- AUTHORITY_HEADER_TAIL4 (할 수 있다): `ㄹ/ETM` 매칭 X
- PROHIBITION_HEADER_NOT_ALLOW (할 수 없다): `ㄹ/ETM` 매칭 X
- PROHIBITION_HEADER_NOT_DOEN (~지 아니된다): `ㄴ다/EF` 매칭 X
- PROHIBITION_HEADER_KEUMJI (금지한다): 별도 점검 필요
- OBLIGATION_DETAIL_ITEM_GEOT (~할 것): `ㄹ/ETM` 매칭 X
- PENALTY_VIOLATOR_ITEM_JA (~한 자): `한/ETM`이 실제로는 `XSA/XSV/VV + ᆫ/ETM` 분해 + 자/NNB ↔ 자가/NNG 모호

→ **본 진단은 reference만**. Cursor는 §3 sample 점검으로 직접 검증 후 룰 작성 (마스터 §2.7).

### 0.3 본 명세의 본질

**전체 23 룰을 0부터 재작성**. 단순 자모 정정이 아니라 Kiwi 실제 출력 ground truth 기반 패턴 도출 + 전체 룰 검증.

작업 흐름:
```
[1] 사전 점검 + 백업
   ↓
[2] 25 sub_type별 sample 100+ Kiwi 토큰화 결과 직접 점검
   ↓
[3] 점검 결과 기반 룰 패턴 도출 (PM 진단은 reference만)
   ↓
[4] rule_classify_subtype 23 룰 UPDATE (또는 폐기 후 신규 INSERT)
   ↓
[5] Phase 2 재실행 (UNCLASSIFIED 143,220만 대상)
   ↓
[6] 검증 + 보고서 + commit
```

---

## 1. 절대 원칙 (마스터 §2 — 본 작업 100% 정합 필수)

### 1.1 LLM 사용 X (마스터 §2.1)
- 룰 작성 시 LLM 호출 금지 — Kiwi sample 분석 + 룰베이스 추론만
- "LLM에게 패턴 도움" 절대 X

### 1.2 법령 보전 (마스터 §2.2)
- source_text 변경 X
- tokenization_json 변경 X (Phase 2.0에서 채워진 결과 보전)

### 1.3 누락 0건 (마스터 §2.3)
- 룰 매칭 안 된 row → UNCLASSIFIED 유지 (절대 강제 분류 X)
- 본 작업으로 분류율 ≥ 50% 도달이 1차 목표 (≥ 70% 이상적)

### 1.4 100% 매핑 (마스터 §2.4)
- stage_2_elements row 수 = 151,751 (변동 X)
- 본 작업 = UPDATE만 (룰 UPDATE + sub_type UPDATE)

### 1.5 오염 = 데이터셋 단위 폐기 (마스터 §2.5)
- 룰 재실행 도중 오염 발견 → 백업 롤백 → 룰 재정정 → 재실행
- "일부 룰만 정정 후 진행" 금지

### 1.6 Phase 1/2.0 결과 보전 (마스터 §2.7)
- Phase 1 분류 5종 (DELETED, EXCEPTION_CLAUSE, DEFINITION_INTRO, TITLE_HEADER, DATE_EFFECTIVE) 8,209건 — **절대 변경 X**
- Phase 2.0 분류 9종 추가 (OBLIGATION_HEADER 182, DEFINITION_HEADER 36, DELEGATION_ACTIVE 13, AS_본다 5, PENALTY_HEADER 6, EXEMPTION_HEADER 1, WEAK_한다단순 18, WEAK_있다단순 61) 322건 — **재검증 후 결정** (룰 정확성 확인 후 보전 또는 재분류)

### 1.7 DB가 ground truth (마스터 §2.7 v1.4)
- 진입 시 1차 작업 = DB 사실 재확인
- PM 진단(§0.2)은 **reference만**, sample 점검으로 직접 검증

### 1.8 검증 부담 0 (마스터 §2.6)
- 사용자 sample 검증 요청 X
- Kiwi 토큰화 결과를 "결정적 ground truth"로 활용 (Kiwi 자체가 룰베이스 형태소 분석기)

---

## 2. 작업 환경

| 항목 | 값 |
|---|---|
| Supabase Project ID | `vwlahtguyggrhvslabax` (서울) |
| 작업 환경 | `railway run python3 ...` (Railway) |
| 코드 base | `taiengineering/tai-api` (engine/morpheme.py / engine/stage_2.py / engine/subtype_rule_match.py) |
| Kiwi 자동 로드 | `engine.user_dict_size == 1725` |
| 룰 DB | `rule_classify_subtype` (현재 23 룰, enabled=true) |

### 2.1 진입 점검 SQL (필수, 마스터 §2.7)

```sql
-- 1. row 수 + 분류 분포
SELECT 'stage_1_clauses' AS tbl, COUNT(*) AS rows FROM stage_1_clauses
UNION ALL SELECT 'stage_2_elements', COUNT(*) FROM stage_2_elements
UNION ALL SELECT 'rule_classify_subtype enabled', COUNT(*) FROM rule_classify_subtype WHERE enabled = true;
-- 예상: 151,751 / 151,751 / 23

-- 2. sub_type 현재 분포 (Phase 2.0 결과)
SELECT sub_type, COUNT(*) FROM stage_2_elements GROUP BY sub_type ORDER BY COUNT(*) DESC;
-- 예상 합계 151,751
-- UNCLASSIFIED 143,220, EXCEPTION_CLAUSE 6,117, DELETED 1,768, OBLIGATION_HEADER 182, ...

-- 3. tokenization_json 채움률 (Phase 2.0에서 채워짐)
SELECT 100.0 * COUNT(*) FILTER (WHERE tokenization_json IS NOT NULL) / COUNT(*) AS filled_pct
FROM stage_1_clauses;
-- 예상: 100% 채움
```

→ 결과가 명세와 다르면 즉시 정지 + PM 회신.

---

## 3. Sample 점검 절차 (본 작업의 핵심)

### 3.1 점검 대상 (25 sub_type 카테고리별 100+ sample)

| 카테고리 | sub_type | 점검 sample 수 | source_text 패턴 (참고) |
|---|---|---|---|
| HEADER (8 sub_type) | OBLIGATION_HEADER | 20+ | "~여야 한다", "~해야 한다" |
| | PROHIBITION_HEADER | 20+ | "할 수 없다", "지 아니된다", "금지한다", "지 못한다" |
| | PENALTY_HEADER | 20+ | "처한다", "과한다", "부과한다" |
| | AUTHORITY_HEADER | 20+ | "할 수 있다" |
| | EXEMPTION_HEADER | 20+ | "적용하지 아니한다", "제외한다" |
| | DEFINITION_HEADER | 20+ | "말한다", "이라 한다" |
| | DELEGATION_ACTIVE | 20+ | "대통령령으로 정한다", "~령으로 정한다" |
| | AS_본다 | 20+ | "으로 본다", "라 본다" |
| ITEM (6 sub_type) | OBLIGATION_DETAIL_ITEM | 20+ | "~할 것" (enumeration 자식) |
| | PENALTY_VIOLATOR_ITEM | 20+ | "~한 자" (처벌 대상) |
| | AUTHORITY_TARGET_ITEM | 20+ | "~할 수 있는 자" |
| | EXEMPTION_TARGET_ITEM | 20+ | "~인 경우" (적용제외 대상) |
| | DEFINITION_TARGET_ITEM | 20+ | "~란" (정의 용어) |
| | PROHIBITION_TARGET_ITEM | 20+ | enumeration 자식, PROHIBITION 종속 |
| 단편 (5 sub_type) | DELETED, DEFINITION_INTRO, TITLE_HEADER, DATE_EFFECTIVE | (Phase 1 적용 완료) | 본 작업 대상 X |
| | PARSE_FRAGMENT | 5+ (확인용) | 파싱 단편 |
| 단서/약함 (3 sub_type) | EXCEPTION_CLAUSE | (Phase 1 적용) | "다만, ..." |
| | WEAK_한다단순 | 10+ | "~한다." 단순 종결 |
| | WEAK_있다단순 | 10+ | "~있다." 단순 종결 |

**최소 점검 sample**: 25 sub_type × 20 sample = **500 sample** (현실적). 충분한 다양성 확보 필수.

### 3.2 점검 방법

각 카테고리에 대해 다음 절차:

```python
# 예: AUTHORITY_HEADER (할 수 있다)
import json
from db.supabase_client import get_supabase
from engine.morpheme import MorphemeEngine

sb = get_supabase()
engine = MorphemeEngine()

# 1. 패턴별 sample 추출 (DB에서 source_text 검색)
sample_texts = sb.table('stage_1_clauses').select(
    'source_text, tokenization_json'
).filter('source_text', 'like', '%할 수 있다.').limit(20).execute().data

# 2. 토큰화 결과 정밀 분석
for s in sample_texts:
    tokens = s['tokenization_json']
    last_8 = tokens[-8:]  # 마지막 8 토큰
    print(f"\nText: ...{s['source_text'][-30:]}")
    for t in last_8:
        print(f"  {t['form']}/{t['tag']} (start={t['start']}, len={t['len']})")
    # 마지막 종결 패턴 시그니처 추출
    signature = " + ".join([f"{t['form']}/{t['tag']}" for t in last_8[-5:]])
    print(f"  Signature: {signature}")

# 3. 패턴 빈도 집계
# - 가장 빈번한 시그니처 1-3개를 룰로 정의
# - 다양성 (XSV/VX/VV 등 보조 어미 차이) 모두 룰로 분리
```

### 3.3 점검 결과 정리 형식

각 sub_type 카테고리별로 다음 표 작성 (Phase 2.1 보고서 §3에 통합):

| 카테고리 | sample size | Kiwi 실제 시그니처 (TOP 3) | 빈도 | 룰 패턴 (정정/신규) |
|---|---|---|---|---|
| AUTHORITY_HEADER | 20 | `ᆯ/ETM + 수/NNB + 있/VA + 다/EF` | 18/20 | `ᆯ/ETM + 수/NNB + 있/VA + 다/EF` (4 토큰 TAIL_POS) |
| | | `ᆯ/ETM + 수/NNB + 있/VV + 다/EF` | 2/20 | (보강 룰: 있/VV 케이스) |
| ... | | | | |

### 3.4 임의판단 금지 규칙 (Sample 점검)

| 항목 | 금지 | 허용 |
|---|---|---|
| 패턴 추론 | LLM 사용 / 인간 직관만으로 패턴 도출 | sample 빈도 분석 (≥ 50% 빈도 시그니처만 룰로 채택) |
| 카테고리 분류 | "유사해 보이는" sample 임의 추가 | source_text의 정확 substring 매칭 |
| 0건 매칭 룰 | "이 정도면 매칭될 것" 가정 | sample에서 실제 매칭 시그니처 직접 확인 |
| Sample size | 20 미만으로 패턴 도출 | 카테고리당 최소 20 sample (다양성 확보) |

---

## 4. 룰 재작성 원칙 (PM 가이드)

### 4.1 패턴 작성 규칙

#### 규칙 1: Kiwi 실제 출력 정확 반영
- 자모 종성: **`ᆯ`/`ᆫ`/`ᆼ`/`ᆻ` 등 conjoining jamo (U+11A8~U+11FF)** 사용
- 한글 자음 (U+3130~U+318F) 절대 X
- EF 어미 통합 토큰 (`ᆫ다/EF`, `ᆯ다/EF` 등) — Kiwi 출력 그대로

#### 규칙 2: 다양성 룰 분리 (priority 인접)
같은 sub_type이라도 다양한 종결 패턴을 별도 룰로 작성:

```
priority 40-49: AUTHORITY_HEADER 룰 (다양성)
- priority 40: AUTHORITY_HEADER_VA_DDA   (있/VA + 다/EF)
- priority 41: AUTHORITY_HEADER_VV_DDA   (있/VV + 다/EF, 동사 케이스)
- priority 42: AUTHORITY_HEADER_NDA      (있/VA + ᆫ다/EF, 어미 통합 케이스)
```

#### 규칙 3: TAIL_POS 토큰 수 정밀
- 4 토큰 (가장 짧은 시그니처): 정확도 높지만 false positive 위험
- 6 토큰 (긴 시그니처): false positive 낮지만 매칭 누락 가능
- **권고**: 카테고리별 최적 토큰 수 sample 점검 결과로 결정

#### 규칙 4: HEAD_TOKEN vs TAIL_POS
- HEAD_TOKEN: source_text 시작 패턴 (예: TITLE_HEADER, DEFINITION_INTRO, EXCEPTION_CLAUSE)
- TAIL_POS: 종결 패턴 (HEADER 8 + ITEM 6 + WEAK 2)

#### 규칙 5: COMPOSITE 룰 (정규식 + POS 조합)
- DELETED, DEFINITION_INTRO, TITLE_HEADER, DATE_EFFECTIVE는 정규식만으로 정확 매칭됨 (Phase 1)
- 본 작업은 **TAIL_POS / HEAD_TOKEN 룰 재작성 중심**

### 4.2 priority 재정의 (참고)

```
priority 5-9: 단편 (REGEX, Phase 1 적용 완료)
  - DELETED_EXACT (5)
  - DEFINITION_INTRO_PATTERN (6)
  - TITLE_HEADER_ARTICLE (7)
  - DATE_EFFECTIVE_SIHAENG (8)
  - EXCEPTION_CLAUSE_DAMAN (9)

priority 10-19: OBLIGATION (의무, 가장 빈번)
priority 20-29: PROHIBITION (금지, 다양성 큼)
priority 30-39: PENALTY (처벌)
priority 40-49: AUTHORITY (권한, 가장 빈번)
priority 50-59: EXEMPTION (적용제외)
priority 60-69: DEFINITION (정의)
priority 70-79: DELEGATION_ACTIVE (위임)
priority 80-89: AS_본다 (간주)
priority 90-99: 예약

priority 100-149: ITEM 6 (parent 종속)
priority 150-199: 예약

priority 200-209: WEAK fallback (어느 룰도 매칭 안 될 때)
priority 210-249: 예약

priority 300+: 보조 룰 (필요 시)
```

### 4.3 룰 UPDATE vs 폐기-신규 INSERT

#### 옵션 A — UPDATE (권고)
- 기존 23 룰의 pattern jsonb를 UPDATE
- 룰 ID 보전 (Phase 2.0의 stage_2_elements.applied_rules와 호환)
- 백업 후 진행

```sql
-- 예: AUTHORITY_HEADER_TAIL4 정정
UPDATE rule_classify_subtype
SET pattern = jsonb_build_object(
  'tail_pos', jsonb_build_array(
    jsonb_build_object('form', 'ᆯ', 'tag', 'ETM'),
    jsonb_build_object('form', '수', 'tag', 'NNB'),
    jsonb_build_object('form', '있', 'tag', 'VA'),
    jsonb_build_object('form', '다', 'tag', 'EF')
  )
), updated_at = NOW()
WHERE rule_name = 'AUTHORITY_HEADER_TAIL4';
```

#### 옵션 B — 폐기 + 재INSERT
- 기존 23 룰 disabled = false (소프트 폐기)
- 신규 룰 INSERT (룰 수 증가 가능, 다양성 룰 분리 시)

→ **권고**: 옵션 A (단순 패턴 정정 + 다양성 룰 INSERT)

### 4.4 pattern jsonb 구조 (DB CHECK 정합)

```sql
-- 현재 rule_classify_subtype 컬럼 + pattern jsonb 구조 확인
SELECT pattern FROM rule_classify_subtype LIMIT 1;
```

→ Cursor가 진입 시 직접 확인 후 `pattern` jsonb 구조에 맞춰 작성.

---

## 5. 백업 (필수, 마스터 §3.2 정합)

```sql
-- 룰 + 분류 결과 모두 백업
CREATE TABLE rule_classify_subtype_backup_20260510_pre_phase2_1 AS 
  SELECT * FROM rule_classify_subtype;

CREATE TABLE stage_2_elements_backup_20260510_pre_phase2_1 AS 
  SELECT * FROM stage_2_elements;

-- 검증
SELECT 
  (SELECT COUNT(*) FROM rule_classify_subtype_backup_20260510_pre_phase2_1) AS rules_backup,
  (SELECT COUNT(*) FROM stage_2_elements_backup_20260510_pre_phase2_1) AS elems_backup;
-- 예상: 23 / 151,751
```

→ 백업 row 수 다르면 즉시 정지.

---

## 6. 작업 절차 (체크리스트)

### 6.1 사전 점검 (필수)
- [ ] §2.1 진입 점검 SQL 실행
- [ ] sub_type 분포 + tokenization_json 채움률 확인 (DB ground truth)

### 6.2 백업 (필수)
- [ ] §5 백업 SQL 실행, row 수 정합 확인

### 6.3 Sample 점검 (본 작업 핵심, 약 4-8시간 예상)
- [ ] 25 sub_type 카테고리 × 20 sample = 500 sample Kiwi 토큰화 점검
- [ ] §3.3 표 형식으로 시그니처 정리
- [ ] 카테고리별 TOP 3 시그니처 도출

### 6.4 룰 재작성 + UPDATE
- [ ] 25 sub_type별 룰 패턴 작성 (다양성 룰 포함, 23 + α 룰)
- [ ] DB pattern jsonb 구조 정확 확인
- [ ] rule_classify_subtype UPDATE (또는 disabled + INSERT)
- [ ] 룰 적용 후 룰 수 확인 (~ 25-35 룰 예상)

### 6.5 Phase 2 재실행 (engine/subtype_rule_match.py 활용)
- [ ] Phase 2.0 분류 322건 (UNCLASSIFIED 외) **재검증** — 룰 변경에 따라 재분류 필요할 수 있음
- [ ] **Phase 1 분류 8,209건은 절대 변경 X** (DELETED/EXCEPTION_CLAUSE 등)
- [ ] UNCLASSIFIED 143,220건 + Phase 2.0 분류 322건 = 143,542건 대상으로 재실행 (안전한 접근)
- [ ] 또는 옵션: stage_2_elements UNCLASSIFIED 외 sub_type을 임시 BACKUP 후 UNCLASSIFIED로 재설정 → 재분류

### 6.6 6하원칙 분해 (sub_type ≠ UNCLASSIFIED row 대상)
- [ ] Phase 2.0의 six_w_heuristic.py 그대로 활용 (executor 룰 보강 가능)
- [ ] executor ≥ 50% 도달 위해 시그니처 보강 (선택)

### 6.7 검증
- [ ] 5.41% (Phase 1) → 5.62% (Phase 2.0) → ?% (Phase 2.1) 확인
- [ ] 임계: 분류율 ≥ 50% (1차 목표) / ≥ 70% (이상적)
- [ ] 100조문 sample 검증 (§5.7.4 Phase 2.0 명세 동일)

### 6.8 verification_log
- [ ] Phase 2.1 entry 6 row INSERT (Phase 2.0과 동일 check_name + verified_by 갱신)

### 6.9 보고서 + commit
- [ ] `docs/extraction/v3/log/Track_E_20260510_Phase2_1.md` 작성
- [ ] commit message: `docs(v3): Track E Phase 2.1 — 23 룰 전체 재설계 (Kiwi sample 100+ 점검)`

---

## 7. 검증 임계 (마스터 §3.4)

| check_name | 임계 (1차 목표) | 임계 (이상적) | 결과 |
|---|---|---|---|
| **phase_2_1_classify_pct** | **≥ 50%** | ≥ 70% | UNCLASSIFIED 외 비율 |
| phase_2_1_sample_100 | ≥ 50% | ≥ 70% | 100조문 sample |
| phase_2_1_six_w_executor | ≥ 50% | ≥ 70% | 6하원칙 executor (보강 시) |
| phase_2_1_six_w_what | ≥ 50% | ≥ 70% | 6하원칙 what |
| **phase_2_1_zero_match_rules** | **0** | 0 | **0건 매칭 룰 = 0개** (모든 룰이 ≥ 1건 매칭) |
| phase_1_results_preserved | 8,209 row 동일 | 8,209 동일 | Phase 1 분류 보전 검증 |

### 7.1 1차 목표 도달 시 (분류율 ≥ 50%)
- 본 작업 완료 + commit + Stage 3 진입 검토 가능

### 7.2 1차 목표 미달 시 (분류율 < 50%)
- **즉시 정지** + PM 회신
- 추가 sample 점검 (500 → 1000+) 또는 sub_type 재정의 검토

### 7.3 이상적 도달 시 (분류율 ≥ 70%)
- Stage 3 진입 가능 게이트 도달

---

## 8. 임의판단 금지 규칙 (Cursor 자체 판단 X)

| 영역 | 금지 | 허용 |
|---|---|---|
| 패턴 도출 | "이 정도면 매칭될 것" 가정 | sample ≥ 20개 빈도 분석 |
| 자모 종성 | 한글 자음 `ㄹ/ㄴ` (U+3139/U+3134) | conjoining jamo `ᆯ/ᆫ` (U+11AF/U+11AB) |
| Phase 1 결과 | 변경 / 덮어쓰기 | 100% 보전 (8,209 row) |
| Phase 2.0 결과 | 무조건 보전 | 룰 변경 시 재검증 후 결정 |
| sub_type | DB CHECK 외 새 enum | 25 enum만 |
| 룰 ID 변경 | 무작위 변경 | UPDATE만 (옵션 A) 또는 신규 INSERT (옵션 B) |
| LLM 호출 | 어떤 형태든 X | Kiwi + 정규식 + 빈도 분석 |
| 임계 미달 시 | 강제 진행 / 룰 임의 추가 | 즉시 정지 + PM 회신 |
| sample 부족 | 20 미만으로 패턴 도출 | 카테고리당 ≥ 20 sample |
| 다양성 룰 분리 | 단일 룰로 모든 케이스 처리 시도 | 패턴 다양성 시 별도 priority 룰 |

---

## 9. 중단 트리거 (즉시 정지 + PM 회신)

다음 발생 시 작업 중단:

1. 진입 점검 SQL 결과가 명세와 다름
2. Sample 추출 시 카테고리당 20 sample 부족 (DB에 충분한 데이터 없음)
3. Kiwi 토큰화 실패율 > 1%
4. 룰 UPDATE 후 Phase 1 분류 8,209 row 변동 발견
5. 분류율 < 50% (1차 임계 미달)
6. 0건 매칭 룰 ≥ 3개 (재설계 의도와 불일치)
7. row 수 변동 (151,751 → 다른 수)
8. backup row 수 != 본체 row 수

---

## 10. 본 명세 외 작업 (절대 X)

- ❌ Stage 3 진입 (rule_objectify 적용)
- ❌ v3.0 마스터 객체 테이블 마이그레이션
- ❌ 신규 sub_type CHECK 추가
- ❌ Tier 2 본법 수집
- ❌ Phase 1 결과 변경
- ❌ rule_classify_if_pattern 변경 (sub_type만 본 작업 대상)

---

## 11. 보고서 양식

```markdown
# [Track E] Phase 2.1 — 23 룰 전체 재설계 결과

## 1. 사전 점검
- (진입 SQL 결과)

## 2. 백업
- rule_classify_subtype_backup_20260510_pre_phase2_1: ___ rows
- stage_2_elements_backup_20260510_pre_phase2_1: ___ rows

## 3. Sample 점검 결과 (25 sub_type × 20 sample)
| sub_type | sample size | TOP 시그니처 (빈도) | 룰 패턴 (정정/신규) |
|---|---|---|---|
| AUTHORITY_HEADER | 20 | `ᆯ/ETM + 수/NNB + 있/VA + 다/EF` (18/20) | TAIL_POS 4 토큰 |
| ... | | | |

## 4. 룰 변경 사항
| rule_name | 변경 전 | 변경 후 | 변동 |
|---|---|---|---|
| AUTHORITY_HEADER_TAIL4 | `ㄹ/ETM + ...` | `ᆯ/ETM + ...` | 자모 정정 |
| ... | | | |

## 5. 룰 수 변화
- 변경 전: 23 (활성 23)
- 변경 후: ___ (활성 ___)

## 6. Phase 2 재실행 결과 — sub_type 분포
| sub_type | Phase 1 | Phase 2.0 | Phase 2.1 | 변화 |
|---|---|---|---|---|
| OBLIGATION_HEADER | 0 | 182 | ___ | +___ |
| AUTHORITY_HEADER | 0 | 0 | ___ | +___ |
| PROHIBITION_HEADER | 0 | 0 | ___ | +___ |
| ... |
| **UNCLASSIFIED** | 143,542 | 143,220 | ___ | -___ |

**총 정확 분류율: ___% (Phase 2.0 5.62% 대비 +___%p)**

## 7. 검증 결과
| check_name | 임계 | 실측 | status |
|---|---|---|---|
| phase_2_1_classify_pct | ≥ 50% | ___% | PASS/FAIL |
| phase_2_1_sample_100 | ≥ 50% | ___% | PASS/FAIL |
| phase_2_1_zero_match_rules | 0 | ___ | PASS/FAIL |
| phase_1_results_preserved | 8,209 | ___ | PASS/FAIL |

## 8. 절대 원칙 점검
| 원칙 | 적용 |
|---|---|
| ① LLM X | ✅ |
| ② 법령 보전 | ✅ |
| ... |

## 9. 다음 단계
- Stage 3 진입 가능 여부: 분류율 ≥ 70% 도달 시 즉시 가능, 50-70%는 6하원칙 보강 후 검토
- v3.0 마스터 객체 테이블 결정 (사용자 펜딩)
```

---

## 12. 환경 정보

| 항목 | 값 |
|---|---|
| 코드 base | `taiengineering/tai-api` (engine/subtype_rule_match.py — Phase 2.0에서 작성됨) |
| 실행 | `railway run python3 scripts/track_e_phase2_1_run.py` (신규 스크립트 또는 기존 + 옵션) |
| 룰 변경 SQL | DB 직접 (Cursor SQL 실행) |
| 보고서 commit | `taiengineering/tai-admin` repo, `docs/extraction/v3/log/Track_E_20260510_Phase2_1.md` |
| 코드 commit | `taiengineering/tai-api` repo, scripts + (필요 시) engine 보강 |

**push 정책**: Cursor 회신 "tai-admin/tai-api 별도 저장소, 원격 push 필요" — 본 작업 commit 후 사용자 push 결정 받기.

---

**END — 23 룰 전체 재설계로 Phase 2 → Phase 2.1 분류율 ≥ 50% (1차 목표) / ≥ 70% (이상적) 도달.**
