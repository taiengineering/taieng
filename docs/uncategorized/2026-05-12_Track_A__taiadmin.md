# [Track A] 2026-05-09 — Track A 산출물 명세 100% 도달 (최종 보고)

> **작업일**: 2026-05-09 (토)
> **파일명**: 사용자 지정 `Track_A_20260512.md` 그대로 유지
> **본 보고서 범위**: Day 1 검증 → Day 2 인프라 → Day 3 stage_1 → Day 3 후반 stage_2/3/validator + mock supabase + Track C 자동 로드 검증
> **Track A 상태**: ✅ **산출물 명세 100% 도달, 본 트랙 종료**

---

## ✅ Track A 산출물 명세 (마스터 §7.1) 최종 점검

| 산출물 | 상태 | 커밋 |
|---|---|---|
| `requirements.txt` (Kiwi 추가) | ✅ | `831a9165` |
| DB migration 12 테이블 | ✅ | apply_migration 3회 |
| `engine/morpheme.py` | ✅ 90% | `76d14838` + `a9c131d8` |
| `engine/stage_1_splitter.py` | ✅ 75% | `d7a228d3` |
| `engine/stage_2_decomposer.py` | ✅ 74% | `8f65b9ee` |
| `engine/stage_3_objectifier.py` | ✅ 72% | `00a58e7b` |
| `engine/validator.py` | ✅ 99% | `91dad1a5` |
| 단위 테스트 ≥ 80% | ✅ **83%** (105/105 passed) | `6338ce85` |

미커버 라인은 stage_1/2/3의 `load_*` / `insert_*` 분기 — 단순 라인 커버는 mock supabase로 가능하나, **실제 인터페이스 검증 = integration test** 영역. Track E 사이클에서 자연 검증.

---

## Done (전체 Day 1~3)

### Day 1 — Phase 1 검증
- ✅ MASTER_HANDOFF §2 절대 원칙 5개 숙지
- ✅ `requirements.txt`: kiwipiepy + kiwipiepy-model 추가 (`831a9165`)
- ✅ `scripts/v3/test_kiwi_hello.py` 작성 + Cursor 실행 통과 (`b825ca0e`)
- ✅ Kiwi 0.22 동작 검증 — 10 sub_type tail-3 baseline 확보 (§부속자료 1)

### Day 2 — 인프라 + 엔진 골격
- ✅ DB Migration 1 (`v3_track_a_g1_rules_dict`) — 룰/사전 7 테이블
- ✅ DB Migration 2 (`v3_track_a_g2_stage_outputs`) — 단계 산출물 3 테이블 + FK 5
- ✅ DB Migration 3 (`v3_track_a_g3_verification_log`) — 검증 로그 1 테이블
- ✅ 12 테이블 종합 검증 통과 (11 신규 + 기존 `law_family_mapping`)
- ✅ `engine/morpheme.py` (`76d14838`) + `tests/v3/test_morpheme.py` — 21 passed
- ✅ Cursor pytest 통과

### Day 3 — Stage 모듈 + Track C 권고 반영 + validator
- ✅ `engine/stage_1_splitter.py` (`d7a228d3`) — 룰 0개 fallback / text_hash 중복 검출 / chunk INSERT
- ✅ Track C 권고 반영 (`a9c131d8`):
  - `MorphemeEngine.__init__` 시그니처 변경: `supabase`, `auto_load_verified_dict` 추가
  - `add_user_word` 다단어 분기: 공백 포함 → `Kiwi.add_re_word(re.escape(term), tag)`
  - `morpheme.py` 오탈자 정정 (캐싀화 → 캡슐화)
  - 신규 테스트 6 (TestMultiWordTerm 3 + TestAutoLoad 3)
- ✅ `engine/stage_2_decomposer.py` (`8f65b9ee`) — 8 역할 + 25 sub_type + 7 IF, fallback 보존
- ✅ `engine/stage_3_objectifier.py` (`00a58e7b`) — UNCLASSIFIED/DELETED/PARSE_FRAGMENT skip
- ✅ `engine/validator.py` (`91dad1a5`) — 마스터 §3.4 임계값 + 평가 + 입력 검증
- ✅ `tests/v3/conftest.py` mock supabase + `test_validator_db.py` (`6338ce85`) — 7 신규 케이스
- ✅ `scripts/v3/verify_dict_loading.py` (`a0282cd9`) — Track C 자동 로드 검증 스크립트

---

## Track C v1 시드 자동 로드 검증 결과 (Railway env, 2026-05-09)

**검증 스크립트**: `python3 scripts/v3/verify_dict_loading.py` exit code = 0

| 단계 | 검증 항목 | 결과 |
|---|---|---|
| 1 | DB 사실 (verified=TRUE 186 = LAW_NAME 145 + AGENCY_NAME 26 + TECH_TERM 15) | ✅ |
| 1 | 다단어 LAW_NAME 70건 (term LIKE '% %') | ✅ |
| 2 | `MorphemeEngine(supabase=sb).user_dict_size == 186` | ✅ |
| 3 | 토큰화 sample: `"고압가스 안전관리법 제10조에 따라 등록한다."` → 첫 토큰 `"고압가스 안전관리법" / NNP` | ✅ |
| 4 | 다단어 LAW_NAME 70건 일괄 토큰화 → 모두 단일 NNP | ✅ |

**결론**: `Kiwi.add_re_word` 정규식 분기 동작 정상. Track C가 추가 사전 확장 시 동일 인터페이스 사용 가능.

---

## 최종 단위 테스트 결과 (commit `6338ce85`)

```
pytest tests/v3/ -v --cov=engine --cov-report=term-missing
105 passed in 8.27s
```

| 모듈 | Coverage | 미커버 라인 |
|---|---|---|
| `engine/morpheme.py` | 90% | 87, 180–182, 194–195, 215–219 |
| `engine/stage_1_splitter.py` | 75% | 81–90, 119, 155–167 |
| `engine/stage_2_decomposer.py` | 74% | 96–129, 176, 220–232 |
| `engine/stage_3_objectifier.py` | 72% | 77–86, 122, 142, 156–168 |
| `engine/validator.py` | 99% | 200 |
| **Total** | **83%** | — |

미커버 라인 분류:
- 모두 `load_*` / `insert_*` 의 supabase 호출 본체
- mock supabase로 시그니처 검증은 validator에 적용 (test_validator_db.py)
- 나머지 모듈도 동일 패턴 적용 가능 — 단순 라인 커버보다 **Track E 사이클의 실제 INSERT 흐름이 진짜 검증**

---

## 부속 자료 1: Kiwi 토큰화 결과 — 10 sub_type baseline tail-3 패턴

| sub_type | tail-3 분해 | 시그니처 |
|---|---|---|
| OBLIGATION_HEADER | `하/VX + ᆫ다/EF + ./SF` | `어야/EC + 하/VX + ᆫ다/EF` |
| PROHIBITION_HEADER | `없/VA + 다/EF + ./SF` | `ᆯ/ETM + 수/NNB + 없/VA + 다/EF` |
| PENALTY_HEADER | `처하/VV + ᆫ다/EF + ./SF` | `처하/VV + ᆫ다/EF` (단일 동사) |
| AUTHORITY_HEADER | `있/VA + 다/EF + ./SF` | `ᆯ/ETM + 수/NNB + 있/VA + 다/EF` |
| DEFINITION_HEADER | `하/XSV + ᆫ다/EF + ./SF` | `말/NNG + 하/XSV + ᆫ다/EF` |
| DELEGATION_ACTIVE | `정하/VV + ᆫ다/EF + ./SF` | `령/(NNG suffix) + 으로/JKB + 정하/VV + ᆫ다/EF` |
| EXEMPTION_HEADER | `아니하/VX + ᆫ다/EF + ./SF` | `지/EC + 아니하/VX + ᆫ다/EF` |
| OBLIGATION_DETAIL_ITEM | `하/XSV + ᆯ/ETM + 것/NNB` | **EF 없음** + `것/NNB` 종결 |
| PENALTY_VIOLATOR_ITEM | `아니하/VX + ᆫ/ETM + 자/NNB` | **EF 없음** + `자/NNB` 종결 |
| EXCEPTION_CLAUSE | `아니하/VX + 다/EF + ./SF` | head=`다만/MAG` (강력) |

### 핵심 발견 (Stage 2 룰 직결)
1. **HEADER vs ITEM = EF 존재 여부** (1차 분별자, `MorphemeEngine.has_ef_terminator()` 활용)
2. **PENALTY**: `처하/VV` 단일 형태소 안정
3. **DELEGATION**: `정하/VV + ᆫ다/EF` 안정
4. **EXCEPTION head**: `다만/MAG` 단일 토큰 강력 검출

### 주의 (정밀화 필수)
- PROHIBITION ↔ AUTHORITY 대칭 (tail-1 1글자 차이) — 변형에 취약
- DEFINITION ↔ DELEGATION 둘 다 `~한다`이지만 Kiwi 분해 다름 → 분해 구조로 분기
- EXEMPTION ↔ EXCEPTION 어말 동일 → head 토큰 검사 필수

### 보너스
- `이/VCP` 잠복 패턴 → DEFINITION_INTRO (`~란`) 안정 검출
- `제38조제1항` → `제/XPN+SN+NNB+제/XPN+SN+NNG` → cross_reference 룰베이스 즉시 가능

---

## 부속 자료 2: 인프라 12 테이블 검증 결과

### Migration 적용

| Migration | name | 결과 |
|---|---|---|
| 1 | `v3_track_a_g1_rules_dict` | success |
| 2 | `v3_track_a_g2_stage_outputs` | success |
| 3 | `v3_track_a_g3_verification_log` | success |

### FK 관계 5개

| Source | Column | → Target | Policy |
|---|---|---|---|
| stage_1_clauses | part_id | law_article_part.id | RESTRICT (원본 보호) |
| stage_1_clauses | split_rule_id | rule_clause_split.id | SET NULL |
| stage_2_elements | clause_id | stage_1_clauses.id | CASCADE |
| stage_3_objects | element_id | stage_2_elements.id | CASCADE |
| stage_3_objects | mapping_rule_id | rule_objectify.id | SET NULL |

---

## 부속 자료 3: 엔진 모듈 인터페이스 (최종 요약)

### MorphemeEngine (Track C 권고 반영)
```python
# DB 자동 로드 (Track C verified=TRUE 186건 즉시 사용)
engine = MorphemeEngine(supabase=sb)  # 또는 supabase=None

# 토큰화
tokens = engine.tokenize(text)
results = engine.tokenize_batch(texts)
tokens, meta = engine.analyze(text)  # meta: tail_3 / head_1 / has_ef / last_tag / last_form / token_count

# Stage 2 룰 매칭용 (static helper)
MorphemeEngine.get_tail_signature(tokens, n=3)
MorphemeEngine.get_head_signature(tokens, n=1)
MorphemeEngine.has_ef_terminator(tokens)

# 사전 (다단어 자동 분기)
engine.add_user_word(term, pos_tag, score)  # 공백 포함 → Kiwi.add_re_word
engine.load_dict_terms([{"term": ..., "pos_tag": ..., "score": ...}, ...])
engine.load_verified_dict_from_db(supabase, term_type="LAW_NAME", limit=1000)
```

### Stage1Splitter
```python
splitter = Stage1Splitter(morpheme_engine, supabase)
splitter.load_rules()
clauses = splitter.split(part_id, part_text)
all_clauses = splitter.split_batch([(p1, t1), ...])
splitter.insert_clauses(clauses, chunk_size=100)
```

### Stage2Decomposer
```python
decomposer = Stage2Decomposer(morpheme_engine, supabase)
counts = decomposer.load_rules()  # → {"subtype": N, "if_pattern": M, "role": K}
elements = decomposer.decompose_batch(stage_1_rows)
decomposer.insert_elements(elements)
# fallback: sub_type='UNCLASSIFIED', if_pattern='UNCONDITIONAL', confidence=0.0
```

### Stage3Objectifier
```python
objectifier = Stage3Objectifier(supabase)
objectifier.load_rules()
objects = objectifier.objectify_batch(stage_2_rows)
# SKIP_MAPPING_SUBTYPES = {UNCLASSIFIED, DELETED, PARSE_FRAGMENT} → None
objectifier.insert_objects(objects)
```

### Validator
```python
v = Validator(supabase)

# 평가 (staticmethod, DB 의존 X)
r = Validator.evaluate_count_mapping(expected=100, actual=100, stage=1)  # PASS / FAIL
r = Validator.evaluate_sample_accuracy(stage=1, accuracy=0.96, sample_size=100)  # PASS / WARNING (5%p) / FAIL
r = Validator.evaluate_duplicates(duplicate_count=0, stage=1)  # PASS / FAIL

# 기록 (DB 의존, 입력 검증 포함)
v.log(r)              # → True/False
v.log_batch([r1, r2]) # → 삽입된 row 수

# 임계값 (마스터 §3.4)
SAMPLE_ACCURACY_THRESHOLDS = {1: 0.95, 2: 0.90, 3: 0.90}
```

---

## 트랙 간 협업 (Track A 종료 시점)

### Track C (도메인 사전) — 활성 협업 중
- ✅ v1 시드 INSERT 완료 (verified=TRUE 186건)
- ✅ 자동 로드 인터페이스 검증 완료 (`MorphemeEngine(supabase=sb)`)
- ✅ 다단어 70건 단일 NNP 토큰화 검증
- 🟢 추가 사전 확장 시 즉시 활용 가능 (verified=true 표시만 하면 다음 인스턴스부터 반영)

### Track B (가족 매핑)
- 기존 `law_family_mapping` 테이블 그대로 사용 OK
- 본 트랙 작업 영향 0건

### Track D (kordoc)
- 영향 없음

### Track E (Stage 분해 사이클) — 본 트랙 인프라 위에서 시작
- **Track A 인프라 100% 준비 완료**
- 사용 가능: morpheme + stage_1/2/3 + validator + 12 DB 테이블 + tail-3 baseline
- Track E 진입 조건 (마스터 §8): Track A Week 4 ✅ + Track B Week 3 + Track C Week 4

---

## 결정 사항 (최종)

| 항목 | 상태 |
|---|---|
| Day 2 sample 100건 (tokenize_sample_100.py) | Day 4+ 처리 (재설계 또는 폐기) |
| 보고서 파일명 (5/12 vs 5/9) | 사용자 지시 우선, 5/12 유지 |
| morpheme.py 오탈자 (캐싀화 → 캡슐화) | ✅ 처리 완료 (commit `a9c131d8`) |
| Track A 종료 announce | ✅ 산출물 명세 100% + 단위 테스트 83% 달성 |

---

## Track A 종료 통보

본 트랙은 마스터 §7.1 산출물 명세 100% 도달로 종료합니다. 후속 작업은 다른 트랙 결과 (Track B 가족 매핑 / Track C 사전 보강 / Track D kordoc) 받으면 Track E 사이클에서 통합됩니다.

**남은 housekeeping (선택적, 우선순위 낮음)**:
1. `tokenize_sample_100.py` 재설계 (DB 의존성 제거 → JSON 번들링)
2. 다른 모듈 (stage_1/2/3) 에도 mock supabase 케이스 추가 (현재 72~75% → 90%+ 회복 가능, 단순 라인 커버)
3. 보고서 파일명 정정 (5/12 → 5/9)

위 3건은 Track E 진입 시 또는 별도 housekeeping 세션에서 처리.
