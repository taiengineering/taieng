# TAI 법령엔진 v3.0 — 의미 요소 분해 엔진 구축 마스터 핸드오프

**문서 버전**: 1.6  
**작성일**: 2026-05-10  
**대상**: TAI Engineering 모든 작업 트랙 (Track A~E)  
**선행 문서**: `docs/extraction/HANDOFF_2026-05-09_v20_apply_completed.md` (v2.0 종결)

---

## 1. 본 문서의 목적

TAI 법령엔진 v2.0의 한계 — AI 의미해석 기반 분해로 인한 데이터 오염 — 가 정량 검증되었다.

오염 증거:
- `where_text` 22.1% 채움 통계 → 실측 의미적 채움률 0.6%
- 의미절 분류 정확도: PENALTY 23%, OBLIGATION 41.9%, AUTHORITY 67%
- 단편 의미절 38,764건 (24.2%) 잘못된 type 분류
- enumeration source/target 의미가 부모-자식 묶음 단위로만 해석 가능

v3.0은 **3단 의미 요소 분해 + 엔진 형태 + 형태소 분석기 + 엄격 룰베이스**로 재구축한다.

본 문서는 5개 멀티 트랙(A~E)이 동일 원칙·동일 작업 순서로 진행하기 위한 마스터 문서다. **모든 트랙은 작업 시작 전 §2 (절대 원칙)을 숙지해야 한다.**

---

## 2. 절대 원칙 (위배 시 작업 중단 + 데이터 폐기)

### 2.1 LLM 절대 사용 금지
- GPT/Claude/Gemini 등 모든 LLM 호출 금지
- 의미해석 / 자연어 추론 / 임의 매핑 작업에 LLM 활용 X
- **허용**: 정규식, 룰베이스, 형태소 분석기 (Kiwi), 사전 매핑, 사람 검증
- **이유**: LLM은 통제 불가능 + 거짓말. 여러 번 엔진 완성에 도달했지만 모두 오염 확인.
- **예외 없음**: "검증용으로만", "참고용으로만"도 X

### 2.2 법령 보전
- 법령 텍스트는 의미해석 임의 변경 X
- 분해 시 원본 source_text 보존 + 별도 컬럼에 추출
- 단어 변경, 의역, 요약 모두 금지
- 추출은 **직접 인용**만 (원문 substring)

### 2.3 놓치는 것 = TAI 리스크
- 모든 의미절은 어떻게든 처리·보전되어야 함 (분해 안 하더라도 보전)
- "분해 어려우니 제외" = 금지
- 단편 의미절도 sub_type=DELETED/PARSE_FRAGMENT/UNCLASSIFIED로 분류해서 보전
- 누락 0건 = 절대 원칙

### 2.4 100% 매핑 (로스리스 변환)
- 한 단계(N) → 다음 단계(N+1) 변환 시 정보 손실 X
- 카운트 매핑: N의 row 수 = N+1에서 추적 가능한 row 수
- 누락 0 / 중복 0 검증 필수
- 모든 row는 이전 단계 row의 link 컬럼 보유

### 2.5 오염 = 데이터셋 단위 폐기
- 부분 polish 금지 (오염된 부분만 수정 X)
- 오염 발견 시 해당 stage 데이터셋 전체 truncate
- 룰 수정 후 재실행
- 백업은 보존 (롤백 가능)

### 2.6 (v1.1) 사용자 검증 부담 0
- 사용자에게 매핑/추출 결과 검증 떠넘김 = 금지
- 검증도 결정적 룰베이스 자동화 (정규식 + ground truth + 형태소 분석)
- "verified=false 후 사용자 확인" 패턴 = 원칙 위배
- **올바른 패턴**: 검증된 ground truth 직접 사용 + 검증 엔진은 cross-validation 용

### 2.7 (v1.1) 추정 매핑 금지 — Ground Truth 우선
- 외부 ground truth 활용 (legalize-kr, admrule-kr) > TAI 자체 추정
- 추정 결과를 검증 엔진으로 수정 = "수정의 수정" = 사용자 원칙 위배
- 처음부터 ground truth 사용 → 검증 엔진은 보완 (별도 디렉토리 케이스 5%)
- **(v1.4) 진입 절차에도 적용**: 인계 문서는 참고, DB가 ground truth. 새 인스턴스 진입 시 1차 작업 = DB 사실 재확인.

---

## 3. 개발 규정

### 3.1 코드 규정
- **언어**: Python 3.10+ (백엔드), TypeScript (kordoc 영역만)
- **프레임워크**: FastAPI (TAI 표준)
- **DB 클라이언트**: `from db.supabase_client import get_supabase`
- **파일 길이 제한**: 400줄 / 15KB (초과 시 모듈 분리)
- **계층 분리**: Router (HTTP) / Service (비즈니스) / Schema (Pydantic) / Tests
- **로깅**: 모든 룰 적용 결과 로그
- **타입 힌트**: 모든 함수 signature

### 3.2 DB 규정
- **Project ID**: `vwlahtguyggrhvslabax` (Supabase 서울)
- **DDL**: `apply_migration`
- **DML**: `execute_sql`
- **대용량 INSERT**: 100건 단위 청크
- **TRUNCATE**: 단독 실행 + 백업 필수 (`{table}_backup_YYYYMMDD_v3`)

### 3.3 Git/배포 규정
- **Repo**: `taiengineering/tai-admin` (main only), `taiengineering/tai-api` (main/dev)
- **MCP**: `github-tai`, `github-tai-admin` (200줄 이상은 Cursor 직접 편집)
- **(v1.5) 모노레포 + sub-repo 구조**: 
  - `tai-engineering/` (모노레포 루트): `origin = tai-engineering.git`, **`upstream = tai-api.git`**
  - `tai-engineering/tai-api/` (sub-repo): **origin only** (tai-api.git)
  - rebase 명령은 모노레포 루트에서 실행해야 의미: `cd /Users/taiwangsim/Desktop/tai-engineering` → `git fetch upstream dev && git rebase -X ours --empty=drop upstream/dev`
  - sub-repo에서 push, 모노레포 루트는 mirror 받음

### 3.4 검증 규정
- 각 Stage 완료 시 검증 hook 자동 실행
- Sample 단위 = **조문** (의미절 X), 크기 = 100조문
- 사용자 검증 작업 = **0건**

---

## 4. 아키텍처

### 4.1 데이터 흐름 (v1.6 갱신)

```
[Stage 0] 법령 원본 (보전)
   ├ law_master 768 (v1.6: +16 Tier 1 LAW)
   ├ law_article 33,929 (+62 형법·민법 부분 수집)
   └ law_article_part 143,549
        │
        │ Track B: 가족 매핑 + 위임/인용 관계 + 행정규칙 매핑 ✅ (Tier 1 보강 완료)
        ↓
   law_family_mapping (768) + law_article_delegation (7,730)
   + law_article_inheritance (15,850) + law_article_citation (7,179, matched 4,057 = 56.51%)
   + legalize_kr_mapping_raw (5,667 GT) + admrule_kr_mapping_raw (20,877 GT)
        │
        │ Track A: 엔진 인프라 ✅ + Track C: 도메인 사전 ✅ v1.2
        ↓
   dict_legal_terms (14,942 row, verified=true 1,725) + morpheme.py 자동 로드 정합
        │
        │ ★ Step 2 폐기 ✅ (v1.6, 308,093 row truncate 백업 보전)
        ↓
   [Stage 1] stage_1_clauses 151,751 ✅ (v1.6 Phase 1)
        │
        ↓
   [Stage 2] stage_2_elements 151,751 ✅ (v1.6 Phase 1, sub_type 5.41% + Kiwi 정밀화 펜딩)
        │
        ↓
   [Stage 3] stage_3_objects (룰 시안 22개 + v3.0 마스터 결정 펜딩)
```

### 4.2 엔진 구성

```
[엔진 모듈]
MorphemeEngine (Kiwi) ✅ / Stage1Splitter / Stage2Decomposer / Stage3Objectifier / Validator

[룰 DB]
dict_legal_terms ✅ / rule_clause_split ✅ (11) / rule_pos_to_role / rule_ending_normalize 
/ rule_classify_subtype ✅ (23) / rule_classify_if_pattern ✅ (8) / rule_objectify (시안 22)

[산출물]
stage_1_clauses ✅ (151,751) / stage_2_elements ✅ (151,751) / stage_3_objects (펜딩) / verification_log (11 row)
```

---

## 5. 25 Sub-type 분류 (Stage 2 핵심)

| 카테고리 | sub_type | 식별 룰 (어말/패턴) |
|---|---|---|
| HEADER | OBLIGATION_HEADER | `하여야 한다` / `해야 한다` |
| HEADER | PROHIBITION_HEADER | `할 수 없다` / `아니 된다` / `금지한다` |
| HEADER | PENALTY_HEADER | `처한다` / `과한다` / `부과한다` |
| HEADER | AUTHORITY_HEADER | `할 수 있다` |
| HEADER | EXEMPTION_HEADER | `적용하지 아니한다` / `제외한다` |
| HEADER | DEFINITION_HEADER | `말한다` / `이라 한다` |
| HEADER | DELEGATION_ACTIVE | `대통령령으로 정한다` / `~령으로 정한다` |
| HEADER | AS_본다 | `으로 본다` / `라 본다` |
| ITEM | OBLIGATION_DETAIL_ITEM | enumeration 자식 + `할 것` |
| ITEM | PENALTY_VIOLATOR_ITEM | enumeration 자식 + `한 자` |
| ITEM | AUTHORITY_TARGET_ITEM | enumeration 자식, AUTHORITY 종속 |
| ITEM | EXEMPTION_TARGET_ITEM | enumeration 자식, EXEMPTION 종속 |
| ITEM | DEFINITION_TARGET_ITEM | enumeration 자식, DEFINITION 종속 |
| ITEM | PROHIBITION_TARGET_ITEM | enumeration 자식, PROHIBITION 종속 |
| 단편 | DELETED | source_text == '삭제' |
| 단편 | DEFINITION_INTRO | "이 법에서 사용하는 용어..." |
| 단편 | TITLE_HEADER | 조문 제목 |
| 단편 | DATE_EFFECTIVE | 시행일 정보 |
| 단편 | PARSE_FRAGMENT | 파싱 잔여 단편 |
| 단편 | DELEGATED_WAIVER | 위임 후 미정의 |
| 단편 | ENUMERATION_ITEM | 단순 enumeration 자식 |
| 단서 | EXCEPTION_CLAUSE | "다만, ~인 경우에는" |
| 약함 | WEAK_한다단순 | `한다.` 단순 종결 |
| 약함 | WEAK_있다단순 | `있다.` 단순 종결 |
| 미정의 | UNCLASSIFIED | 위 어느 룰도 적용 안 됨 |

---

## 6. 7 IF 패턴

| if_pattern | 식별 패턴 | 본질 |
|---|---|---|
| UNCONDITIONAL | IF 표현 없음 | 무조건적 |
| CONDITIONAL_EVENT | "~한 경우" / "~ 발생 시" | 사건 트리거 |
| CONDITIONAL_THRESHOLD | "5천제곱미터 이상" | 임계값 |
| CONDITIONAL_QUALIFICATION | "~인 자는" | 자격 조건 |
| CONDITIONAL_TIMING | "~ 후 30일 이내" | 시점 조건 |
| CONDITIONAL_NEGATION | "~에 해당하지 아니하는 경우" | 부정 IF |
| CONDITIONAL_GENERAL | 기타 | - |

각 의미절은 **(sub_type, if_pattern)** 두 속성 동시 보유.

---

## 7. 멀티 트랙 작업 분담 (v1.6 갱신)

### Track A — 엔진 인프라 ✅ 안정화 announce (P2 측정 다른 창 진행 중)
- **주체**: Cursor / Claude Code (TAI Backend 창)
- **목표**: Kiwi + DB 스키마 + 모듈 + 검증 hook
- **상태**: **안정화 announce 도달 + Track E Stage 1/2 인프라로 활용 중** (P0 해결 + 정지점 1 통과)
- **산출물 명세 8개 100% 도달**:
  - requirements.txt, DB migration (12 테이블), engine/morpheme.py (Kiwi + 자동 로드 페이지네이션), engine/stage_1.py / stage_2.py / stage_3.py, validator.py, 단위 테스트 ≥ 80% (실 85%)
- **핵심 commit**: `91c12da6` (morpheme.py 페이지네이션 패치) — `taiengineering/tai-api` dev
- **검증 (정지점 1)**: pytest 126 passed (직전 baseline 114 + 신규 12) / coverage 85% (morpheme.py 96%) / 두 트리 diff 0
- **자동 로드 정합**: `engine.user_dict_size == 1725` (Track C v1.2 ground truth 그대로 활용)
- **잔여 trackpoint** (안정화 호환):
  - **P1**: 다단어 토큰화 3건 (`'하수도법 시행규칙'`, `'하수도법 시행령'`, `'체외진단의료기기법 시행령'`) — 가설 F~I (add_user_word with whitespace / ZWJ / user_dict_path / blocklist) 미시도
  - **P2**: 실 환경 wall time 측정 — **다른 창 측정 진행 중** (사용자 결정 2026-05-10)
- **상세**: `docs/extraction/v3/handoff/Track_A_handoff_20260509_EOD.md` + §18.1-3

### Track B — 가족 매핑 + 위임/인용 관계 + 행정규칙 매핑 ✅ + Tier 1 자동 보강 (v1.6)
- **주체**: 사용자 + Claude 기획창 (TAI 회의실)
- **목표**: 법령 간 모든 관계 정의 (가족 + 조문 단위 위임 + 외부 인용 + 행정규칙)
- **기간**: Day 1 (2026-05-09) + Week 2 + 2026-05-10 Tier 1 자동 보강
- **상태**: **본질 작업 100% 완료 + Tier 1 추가 수집 보강 (citation 38.33% → 56.51%, +18.18%p)**
- **산출물 (5개 raw + 4 관계 테이블 + 2 view)**:
  - `legalize_kr_mapping_raw` 5,667 / `admrule_kr_mapping_raw` 20,877
  - `law_family_mapping` 768 (PRIMARY 139, ORPHAN 4, ADMINISTRATIVE_RULE 386 with parent_filled 221/null 165) — v1.6 Tier 1 보강 후
  - `law_article_delegation` 7,730 / `law_article_inheritance` 15,850 / `law_article_citation` 7,179 (matched 4,057 = 56.51%)
  - `v_law_family` / `v_law_family_tree` view
- **검증 엔진 V1 — 5 룰**: §15.4 참조
- **(v1.6) Tier 1 자동 보강 결과** (§19.6):
  - 16 LAW PRIMARY INSERT (Tier 1 14 + 군형법/난민법 누락분)
  - ORPHAN 6 → 4 (방송통신발전기본법/도로교통법 자식 V1-A 매칭)
  - ADMINISTRATIVE_RULE parent_null 168 → 165 (3건)
  - **citation 매핑 +1,305건 (38.33% → 56.51%)** — 핵심 효과
  - 형법·민법 부분 수집 (49 인용 조번호 → 67 row, partial_merge=True)
- **상세**: §14 (Step 1) + §15 (Step 2-3) + §16 (Step 2-F + 2-G) + §17 (Week 2) + §19 (v1.6)

### Track C — 법령 도메인 사전 ✅ v1.2 본분 완수 (v1.3 Stage 분해 시점 적용 후보)
- **주체**: Claude 기획창 + 사용자 (TAI Data 창)
- **목표**: dict_legal_terms v1 (500-1,000 어휘)
- **상태**: **v1.2 본분 완수** / Week 4 마일스톤 Day 1 추월
- **산출물**:
  - `dict_legal_terms` 14,942 row (verified=true **1,725**, verified=false 13,217 보전)
  - 분포: LAW_NAME 423 (다단어 344) / AGENCY_NAME 26 / TECH_TERM 15 / GENERIC 1,261
  - QUARANTINE 4건 (verified=false, notes 보존)
  - 사용자 검증 작업 0건 (ground truth + 룰베이스 자동 검증)
  - Top 30 sanity 93% (28/30 도메인 적합)
- **추월 사유**: 사용자 검증 단계 자체를 ground truth + 룰베이스 자동 검증으로 대체
- **펜딩**:
  - Track A P2 다른 창 측정 회신 → v1.3 적용 영향 분석
  - v1.3 설계 시안 (`docs/extraction/v3/track_c/v1_3_design_proposal.md`) — Stage 2 Phase 2 Kiwi 정밀화 시점 적용 후보
  - QUARANTINE 4건 결정
- **상세**: `docs/extraction/v3/handoff/Track_C_handoff_20260509_EOD.md` + §18.4-6

### Track D — 별표·서식 처리 (kordoc) ✅ Phase 1 종결 (v1.6)
- **주체**: Cursor (TAI Backend 부속 창)
- **목표**: 법령 별표 PDF/HWP 자동 변환 파이프라인
- **기간**: Week 1-2 (완전 독립)
- **상태**: **Phase 1 종결** (사용자 결정 옵션 D, 2026-05-10) — 별도 창 작업 + Phase 2 가설 무효 발견
- **(v1.6) Phase 1 결과** (§19.2):
  - law_attachment 460 + zip child 862 = 1,322 row 변환
  - CLEAN 1,225 (정상) + POLLUTED_PUA 81 (보전) + UNSUPPORTED_FORMAT 9 (zip parent) + IMAGE_PDF 5 (OCR 후속) + NO_STORAGE 2
  - **텍스트 보전율 98.8%** (1,306/1,322)
- **(v1.6) Phase 2 진단 결과 — 가설 100% 무효**:
  - 1,322건 중 **99.5% (1,300건)** = 외부 참조 표준 (KS/KC/KDS/KCS/공정시험기준 ES) — 법령 별표 X
  - 0.5% (6건) = 개정이유서/관보 메타
  - **별표·서식 본문은 사실상 부재** — v2에서 이미 law_article/law_article_part에 통합된 영역
  - 사용자 결정: **옵션 D — Phase 1 종결, 다른 트랙 진행** (마스터 §2.2 위배 위험 회피 + v2 통합 영역 중복 회피)

### Track E — Stage 분해 사이클 (메인) ✅ Stage 1/2 Phase 1 완료 + Stage 3 시안 (v1.6)
- **주체**: Claude 기획창 + Cursor (TAI 회의실 메인)
- **목표**: Stage 1 → Stage 2 → Stage 3 순차 완성
- **기간**: Week 5-12 (정밀) / Week 5-8 (MVP)
- **시작 조건**: Track A ✅ + Track B ✅ + Track C ✅ + Track D ✅ → ★ Step 2 폐기 ✅ → Stage 1 진입
- **현재**: Stage 1 Phase 1 ✅ + Stage 2 Phase 1 ✅ + Stage 3 룰 시안 작성 (Phase 2 Kiwi 정밀화 + v3.0 마스터 결정 대기)
- **(v1.6) Stage 1 Phase 1 완료** (§19.4):
  - 룰 11 INSERT (rule_clause_split, 10 enabled + 1 disabled)
  - **stage_1_clauses 151,751 row** (= law_article_part 143,549 + 다중 종결 분리 +8,202)
  - 검증 5/5 PASS (count_mapping / duplicate / empty / position / text_hash)
  - 시안 정정: ENUMERATION 룰 4건 무효 발견 — law_article_part가 이미 항/호/목/단서 단위 계층 분리 완료, DELIMITER 종결 분리만 본 적용
- **(v1.6) Stage 2 Phase 1 완료** (§19.5):
  - if_pattern 8 룰 INSERT (REGEX) + sub_type 23 룰 시안 INSERT (TAIL_POS/HEAD_TOKEN/COMPOSITE)
  - **stage_2_elements 151,751 row** (1:1)
  - sub_type 정확 분류: 5.41% (DELETED 1,768 + EXCEPTION_CLAUSE 6,117 + DEFINITION_INTRO 142 + TITLE_HEADER 94 + DATE_EFFECTIVE 88) + UNCLASSIFIED 94.59% (Kiwi 정밀화 펜딩)
  - if_pattern 명시 분류: 17.58% (CONDITIONAL_*)
  - 검증 6/6 (5 PASS + 1 INFO)
- **(v1.6) Stage 3 룰 시안 작성** (§19.8):
  - 22 rule_objectify 룰 (HEADER 8 + ITEM 6 + 단편 4 + metadata/weak 4)
  - sub_type → target_master_table 매핑 (24 sub_type → 10 마스터 객체 테이블)
  - v3.0 마스터 객체 테이블 10 CREATE TABLE 시안 (object_duty/prohibition/penalty/authority/exemption/definition/delegation/deeming/metadata/uncategorized)
- **펜딩**:
  - Cursor Phase 2 (Kiwi 정밀화): tokenization_json + split_rule_id + UNCLASSIFIED 143,542건 정밀 분류 + 6하원칙 분해
  - v3.0 마스터 객체 테이블 정의 결정 (옵션 A/B/C)
  - Stage 3 진입 (Phase 2 + 마스터 결정 후)

---

## 8. 스케줄 (v1.6 갱신)

### Week 1 (2026-05-09)
- **Track A**: ✅ Kiwi 설치 → DB 스키마 → 엔진 모듈 → 정지점 1 통과 → **안정화 announce**
- **Track B**: ✅ Day 1-3 본질 작업 + Step 2-A~G + Week 2 admrule-kr 완료
- **Track C**: ✅ v1.2 본분 완수 (1,725 verified, Week 4 마일스톤 Day 1 추월)
- **Track D**: ✅ Phase 1 종결 (사용자 결정 옵션 D, 2026-05-10)

### Week 2 (2026-05-10)
- **Track A**: P1 다단어 3건 (안정화 호환) / **P2 다른 창 측정 진행 중**
- **Track B**: ✅ **Tier 1 자동 보강 완료** (citation +18.18%p, ORPHAN -2, AdmRule parent +3) + **형법·민법 부분 수집** (49 인용 조번호 → 67 row)
- **Track C**: Track A P2 회신 후 v1.3 적용 여부 판단
- **Track D**: ✅ Phase 1 종결 (별표 본문 부재 발견 + v2 통합 영역 중복 회피)

### Week 3 (2026-05-10)
- ✅ **★ Step 2 폐기**: semantic_clause + relation truncate (308,093 row, 백업 보전)
- ✅ **Track E Stage 1 Phase 1**: 151,751 stage_1_clauses 적재 (5/5 PASS)
- ✅ **Track E Stage 2 Phase 1**: 151,751 stage_2_elements 적재 (정규식 5.41% + Kiwi 정밀화 펜딩)
- ✅ **Track E Stage 3 룰 시안**: 22 rule_objectify + 10 마스터 객체 테이블 신규 정의 시안
- ⏳ **Tier 2 본법 13건 수집** (Cursor) — 통계법/도서관법/정부조직법/비상대비법 + AdmRule 추가 본법

### Week 4
- ⏳ **Cursor Stage 2 Phase 2** (Kiwi 정밀화): tokenization_json + UNCLASSIFIED 143,542건 정밀 분류 + 6하원칙 분해
- ⏳ **v3.0 마스터 객체 테이블 정의 결정** (옵션 A: 신규 10 테이블 / B: master_rule_v2 활용 / C: stage_3_objects jsonb)
- ⏳ **Track E Stage 3 진입** (Phase 2 + 마스터 결정 후)

### Week 5-12 — Stage 3 + 마스터 합성

### 마일스톤 (v1.6 실적 갱신)

| 시점 | 마일스톤 | 실적 |
|---|---|---|
| End Week 1 | Kiwi 작동 + Track B Step 1+2+3 완료 | ✅ Day 1 모두 달성 (A 안정화 / B 본질 100% / C v1.2) |
| End Week 2 | Track B 100% 완료 (admrule-kr 매핑 포함) | ✅ Day 1 + Tier 1 보강 (Day 2) |
| End Week 4 | 인프라 완성 + Step 2 폐기 | ✅ A 안정화 (Week 1) + Step 2 폐기 (Week 3) ★ Day 2 추월 |
| End Week 6 | Stage 1 완료 | ✅ **Stage 1 Phase 1 Week 3 (Day 2 추월)** + Phase 2 Cursor 펜딩 |
| End Week 10 | Stage 2 완료 | ✅ **Stage 2 Phase 1 Week 3 (Day 2 추월)** + Phase 2 Kiwi 정밀화 펜딩 |
| End Week 12 | Stage 3 + 마스터 합성 완료 | ⏳ Stage 3 룰 시안 작성 (Week 3) + 적용은 Phase 2 + 마스터 결정 후 |

→ **Day 2 누적 추월**: Track B/C/D + Step 2 폐기 + Stage 1/2 Phase 1 + Stage 3 시안. 본 PM 창 단일 일자(2026-05-10) 작업으로 Week 3-6 마일스톤을 Day 2에 일부 도달.

---

## 9-11. 검증 절차 / 협업 / 도구

(v1.0~1.2 동일, 변경사항 §15-§19 참조)

---

## 12. 용어 정의

- **3단 분해**: 의미절 분리(Stage 1) → 역할별 분해(Stage 2) → 객체화(Stage 3)
- **HEADER / ITEM / 단편 / IF 차원**: §5, §6 참조
- **로스리스 변환**: 정보 손실 0%
- **PRIMARY / ENFORCEMENT_DECREE / RULE / ADMINISTRATIVE_RULE**: 가족 매핑 분류
- **(v1.1) ORPHAN**: 본법이 TAI 미수집
- **(v1.1) Ground Truth**: 외부 검증 데이터 (legalize-kr / admrule-kr)
- **(v1.1) Validator V1-A (자기 정의 패턴)**: 시행령/규칙/행정규칙 본문의 「~법」(이하 "법")
- **(v1.2) Delegation**: 본법 본문의 위임 표현 추출 ("대통령령으로 정한다") — source 측
- **(v1.2) Inheritance**: 시행령/시행규칙 본문의 부모 인용 추출 ("법 제N조") — target 측
- **(v1.2) Citation**: 외부 법령 인용 ("「~법」 제N조" cross-reference)
- **(v1.2) Cross-validate**: Delegation × Inheritance 양방향 일치 검증
- **(v1.3) Citation Purpose**: 인용 목적 8 카테고리 분류 (DELEGATION_DIRECT / DELEGATION_FOLLOW / DEFINITION_QUOTE / STRUCTURAL_REF / APPLICATION_REF / APPLICATION_ACT / GENERAL / UNCLASSIFIED)
- **(v1.3) is_first_in_article**: inheritance row가 자식 article의 첫 매칭 인용 여부 (Stage 분해 시 핵심 부모 식별 우선)
- **(v1.4) admrule-kr GT**: 행정규칙 ground truth (20,877 row, 13자리 MST 1:1 + title 정규화 매칭)
- **(v1.4) ADMINISTRATIVE_RULE family_role**: NOTICE/STANDARD/OTHER 행정규칙 (TAI 386건)
- **(v1.5) Track A 안정화 announce**: 산출물 명세 8개 100% + P0 해결 + 정지점 1 통과 + dict 자동 로드 1,725건 정합 도달
- **(v1.5) P0 (Track A)**: dict 자동 로드 1,000건 미스터리 (PostgREST max-rows 제약). commit `91c12da6`로 페이지네이션 해소
- **(v1.5) P1 (Track A)**: 다단어 LAW_NAME 토큰화 3건 (안정화 호환 trackpoint)
- **(v1.5) P2 (Track A)**: 실 환경 wall time 측정 (Track C 회신 펜딩)
- **(v1.6) Tier 1-4**: TAI 추가 수집 우선순위 (Tier 1 = 인용 100회 이상 14 본법, Tier 2-4 후속)
- **(v1.6) partial_merge**: collect_v2 부분 적재 옵션 (DELETED 우회, 형법·민법 49 조번호 적용)
- **(v1.6) target_master_table**: Stage 3 객체화 대상 마스터 테이블 (object_duty/prohibition/penalty/authority/exemption/definition/delegation/deeming 등)
- **(v1.6) field_mapping jsonb**: rule_objectify의 필드 매핑 (stage_2_elements → master_object 변환 패턴)

---

## 13. 변경 이력

- **v1.0** (2026-05-09): 초기 작성 — LLM 사용 금지 + 3단 분해 + 25 sub_type + 7 IF 패턴 + Kiwi/legalize-kr/kordoc + 멀티 트랙 12주 스케줄
- **v1.1** (2026-05-09): Track B Day 1~3 완료 — 절대 원칙 §2.6/§2.7 추가 + Track B 366건 매핑 + 검증 엔진 V1-A 도입 + §14 신설
- **v1.2** (2026-05-09): Track B Step 2 + Step 3 완료 — 위임 7,730 + inheritance 8,641 + citation 7,179 + 검증 엔진 V1 4룰 + TAI 추가 수집 12건 우선순위 + §15 신설
- **v1.3** (2026-05-09): Track B Step 2-F + Step 2-G 완료 — inheritance 보강 (8,641 → 15,850, 1.83배) + citation_purpose 8 카테고리 분류 + 위임 전용 cross-validate 86.6% + 검증 엔진 V1 5룰 (V1-E 추가) + §16 신설
- **v1.4** (2026-05-09): Track B Week 2 admrule-kr 매핑 완료 — `admrule_kr_mapping_raw` 20,877 + ADMINISTRATIVE_RULE 386 (룰 1 MST 319 + 룰 2 title 66 + V1-A fallback 1) + parent_law_id 218 (V1-A 확장 적용) + delegation STANDARD/NOTICE 166 NULL 유지 (§2.7 정합) + §17 신설 + §2.7 진입 절차 적용 명시
- **v1.5** (2026-05-09): Track A 안정화 announce 명시 (commit `91c12da6` P0 해결 + 정지점 1 통과 / 126 passed / coverage 85% / morpheme.py 96%) + Track C v1.2 본분 완수 명시 (dict_legal_terms 14,942 row, verified=true 1,725) + §3.3 모노레포 + sub-repo 구조 정정 + §18 신설 (Track A 안정화 + Track C 본분 완수)
- **v1.6** (2026-05-10): **Track D Phase 1 종결** (옵션 D, 1,322 row 보전율 98.8%, Phase 2 가설 무효 발견) + **★ Step 2 폐기** (semantic_clause/relation 308,093 row truncate, 백업 보전) + **Track E Stage 1 Phase 1** (151,751 stage_1_clauses 적재, 5/5 PASS, ENUMERATION 룰 무효 발견 후 DELIMITER 11 룰 본 적용) + **Track E Stage 2 Phase 1** (151,751 stage_2_elements, sub_type 5.41% + if_pattern 17.58%, 6/6 검증, 룰 31개) + **Track B Tier 1 자동 보강** (citation 38.33% → 56.51%, +18.18%p, ORPHAN 6→4, AdmRule parent +3) + **형법·민법 부분 수집** (49 인용 조번호 → 67 row, partial_merge=True, 옵션 A 보전 처리) + **Track E Stage 3 룰 시안** (22 rule_objectify + 10 v3.0 마스터 객체 테이블 시안) + §19 신설

---

## 14. (v1.1) Track B Day 3 결과 — Step 1 가족 매핑

### 14.1 작업 흐름 (교훈)

Day 1 추정 매핑 + Day 2 INSERT + Day 3 검증 엔진 수정 → 사용자 지적 → **Day 1+2 폐기 후 legalize-kr ground truth 재진행**.

→ 결과: 366/366 (100%) 매핑, 358/366 (97.8%) verified=true, 사용자 검증 작업 0건

### 14.2 매핑 결과 (366건)

| family_role | mapping_method | cnt | verified |
|---|---|---|---|
| PRIMARY (LAW) | legalize_kr_mst | 123 | 123 ✓ |
| ENFORCEMENT_DECREE | legalize_kr_mst | 116 | 114 |
| ENFORCEMENT_DECREE | validator_v1_self_def | 4 | 4 ✓ |
| ENFORCEMENT_RULE | legalize_kr_mst | 98 | 98 ✓ |
| ENFORCEMENT_RULE | validator_v1_self_def | 19 | 19 ✓ |
| ORPHAN | orphan_no_parent | 6 | 0 |
| **합계** | - | **366** | **358 (97.8%)** |

### 14.3 ORPHAN 6건 (v1.6 갱신)

통계법, 도서관법, 정부조직법, 방송통신발전 기본법, 비상대비에 관한 법률, 도로교통법

→ **v1.6 Tier 1 보강 후**: 방송통신발전 기본법 + 도로교통법 자식 2건 V1-A 매칭 해소 (ORPHAN 6→4). 잔여 4건 (통계법/도서관법/정부조직법/비상대비법) Tier 2 수집 트리거.

---

## 19. (v1.6) 본 PM 창 작업 통합 — Track D 종결 + Step 2 폐기 + Track E Stage 1/2 Phase 1 + Tier 1 보강 + 형법·민법 부분 수집 + Stage 3 시안

### 19.1 v1.6 작업 본질

본 §19는 **2026-05-10 PM 창 단일 일자 작업의 종합 보고서**. 본 PM 창에서 SQL-only 환경으로 Track A 인프라를 활용해 다음 7가지 본질적 작업을 완료:

1. Track D Phase 1 종결 (사용자 결정 옵션 D)
2. ★ Step 2 폐기 (v2.0 오염 데이터 truncate)
3. Track E Stage 1 Phase 1 (의미절 분리)
4. Track E Stage 2 Phase 1 (sub_type + if_pattern 분류)
5. Track B Tier 1 자동 보강 (citation +18.18%p)
6. 형법·민법 부분 수집 (49 인용 조번호 → 67 row)
7. Track E Stage 3 룰 시안 작성 (22 rule_objectify + 10 마스터 객체 테이블)

### 19.2 Track D Phase 1 종결 (사용자 결정 옵션 D)

**Phase 1 결과**:
- law_attachment 460 + zip child 862 = 1,322 row 변환
- CLEAN 1,225 / POLLUTED_PUA 81 (보전) / UNSUPPORTED_FORMAT 9 (zip parent) / IMAGE_PDF 5 / NO_STORAGE 2
- **텍스트 보전율 98.8%** (1,306/1,322)

**Phase 2 진단 결과 (가설 100% 무효)**:
- 1,322건 중 **99.5% (1,300건)** = 외부 참조 표준 (KS/KC/KDS/KCS/공정시험기준 ES) — **법령 별표 X**
- 0.5% (6건) = 개정이유서/관보 메타 — 별표 본문 X
- 별표·서식 본문은 사실상 부재 — v2에서 이미 law_article/law_article_part에 통합

**사용자 결정 — 옵션 D (Phase 1 종결)**:
- 사유: 마스터 §2.2 위배 위험 회피 (외부 표준은 법령 본문 아님) + v2 통합 영역 중복 회피 + Phase 1 산출물은 보전 상태로 Track E 분해 시 활용 가능

### 19.3 ★ Step 2 폐기 (v2.0 오염 데이터)

**백업 (마스터 §3.2 정합)**:
- `semantic_clause_backup_20260510_v3_step2_discard` 160,372 row
- `semantic_clause_relation_backup_20260510_v3_step2_discard` 147,721 row

**TRUNCATE 결과**: 308,093 row → 0 row (데이터 손실 0, 백업 보전).

마스터 §2.5 (오염 = 데이터셋 단위 폐기) + §3.2 (백업 후 truncate) 정합.

### 19.4 Track E Stage 1 Phase 1 — 의미절 분리

**DB ground truth 발견 (시안 정정, §2.8 정합)**:
- law_article_part는 이미 항(61,223)/proviso(4,195+1,874)/clause(65,819)/subclause(10,438) = 143,549 계층 분리 완료
- 시안의 ENUMERATION 룰 4건 (NUMERIC/KOREAN/PAREN + EXCEPTION_DANSEO) 무효 발견
- DELIMITER 종결 분리 11 룰만 본 적용 (10 enabled + 1 disabled)

**룰 11 INSERT (rule_clause_split)**:
- DELIMITER_HANDA (한다., 5,135건) / ITDA (있다., 1,624) / MALHANDA (말한다., 969) / DOEN (된다., 216) / JEONGHANDA (정한다., 173) / BONDA (본다., 37) / OPDA (없다., 30) / AHNHANDA (아니한다., 15) / AHNDOEN (아니된다., 7) / CHEOHANDA (처한다., 6) / GWAHANDA (과한다., 0 disabled)

**stage_1_clauses 본 적재** (단일 INSERT-SELECT, 마스터 §2.3 + §2.4 정합):
- 입력: 143,549 part
- 출력: **151,751 stage_1_clauses** (= 143,549 fallback + 8,202 다중 종결 분리)
- 검증 5/5 PASS: count_mapping (143,549 distinct part_id) / duplicate_position (0) / empty_source_text (0) / position_starts_zero (143,549) / text_hash_filled (0 NULL)

**한계 (Cursor Phase 2 위탁)**:
- tokenization_json: NULL (Kiwi 메타데이터, 후속)
- split_rule_id: NULL (정확 룰 추적 후속)
- char_start/end: NULL (정밀 위치 후속)

### 19.5 Track E Stage 2 Phase 1 — sub_type + if_pattern 분류

**DB CHECK 발견 (시안 정정)**:
- `rule_classify_subtype.match_strategy` ∈ {TAIL_POS, HEAD_TOKEN, POS_SEQUENCE, COMPOSITE} — **REGEX 없음**
- → sub_type 분류는 본질적으로 Kiwi 토큰화 필수

**if_pattern 8 룰 INSERT (REGEX 가능)**: NEGATION_HAEDANG / EVENT_GYEONGWOO / EVENT_BALSAENG / THRESHOLD / TIMING / QUALIFICATION_JA / QUALIFICATION_GEOT / GENERAL_HAGOJA

**sub_type 23 룰 시안 INSERT** (17 카테고리):
- HEADER 8 (TAIL_POS, Kiwi 적용 후속): OBLIGATION/PROHIBITION 3종/PENALTY 3종/AUTHORITY/EXEMPTION 2종/DEFINITION 2종/DELEGATION_ACTIVE/AS_본다
- ITEM 2 (TAIL_POS): OBLIGATION_DETAIL_ITEM / PENALTY_VIOLATOR_ITEM
- 단편 5 (COMPOSITE/HEAD_TOKEN, 본 창 직접 적용): DELETED_EXACT / DEFINITION_INTRO / TITLE_HEADER / DATE_EFFECTIVE / EXCEPTION_CLAUSE_DAMAN
- 약함 2: WEAK_한다단순 / WEAK_있다단순

**stage_2_elements 적재 (151,751 row, 1:1 매핑)**:
- sub_type 정확 분류: **5.41%** (8,209건) — UNCLASSIFIED 94.59% (143,542, Kiwi 정밀화 펜딩)
  - EXCEPTION_CLAUSE 6,117 (proviso 6,069 + 추가 48) / DELETED 1,768 / DEFINITION_INTRO 142 / TITLE_HEADER 94 / DATE_EFFECTIVE 88
- if_pattern 명시 분류: **17.58%** (26,675건) — UNCONDITIONAL 82.42%
  - CONDITIONAL_EVENT 11,780 / THRESHOLD 7,360 / GENERAL 3,286 / TIMING 3,005 / QUALIFICATION 1,156 / NEGATION 88
- 검증 6/6 (5 PASS + 1 INFO)

### 19.6 Track B Tier 1 자동 보강 (citation +18.18%p)

**Tier 1 14 본법 적재 (Cursor)**:
- 전자정부법, 형법, 고등교육법, 민법, 자동차관리법, 국민건강보험법, 개인정보보호법, 산업표준화법, 국가표준기본법, 국민기초생활보장법, 도로법, 초중등교육법, 도로교통법, 방송통신발전기본법
- 12/14 정상 (article_count 46-229), 2/14 (형법 2조 / 민법 3조) 부분 적재 — 별도 부분 수집 트리거

**자동 보강 4 SQL** (PM 창 직접 실행):
- A: 16 LAW PRIMARY INSERT (Tier 1 14 + 누락 군형법/난민법)
- B: ORPHAN 2건 V1-A 매칭 UPDATE (방송통신설비/어린이보호구역 → 방송통신발전기본법/도로교통법)
- C: ADMINISTRATIVE_RULE parent_law_id UPDATE (V1-A 추출 but TAI 미수집 3건 자동 해소)
- D: citation cited_law_id 매칭 (+1,305 row 신규 매칭)

**Before/After**:
| 지표 | Before | After | 변화 |
|---|---|---|---|
| family_mapping_total | 752 | 768 | +16 |
| ORPHAN | 6 | 4 | -2 |
| AdmRule parent_filled | 218 | 221 | +3 |
| **citation_matched** | **2,752** | **4,057** | **+1,305** |
| **citation_match_pct** | **38.33%** | **56.51%** | **+18.18%p ★** |

**백업 3종**: `law_family_mapping_backup_20260510_v3_tier1_pre_boost` (752) / `law_article_citation_backup_20260510_v3_tier1_pre_boost` (7,179) / `law_article_inheritance_backup_20260510_v3_tier1_pre_boost` (15,850)

### 19.7 형법·민법 부분 수집 (사용자 PM 결정)

**데이터 검증 (DB 인용 분포)**:
- 형법 459조 중 **18조만 인용** (3.9%, 125회)
- 민법 1307조 중 **31조만 인용** (2.4%, 92회)
- 전체 1,766조 중 **49조만 (2.8%)** = TAI 작업 모집단

**사용자 결정**: "범위 큰 일반법 + 다른 법령과 충돌 위험 → 부분 수집 (49조만)"

**Cursor 코드 + 실행**:
- `collect_v2.save_law_to_db(..., partial_merge=True)` 추가 (DELETED 우회)
- `tai-api/scripts/tai_hyungbeob_minbeob_partial_collect.py` 신규
- `railway run python3 scripts/tai_hyungbeob_minbeob_partial_collect.py` 실행

**적재 결과 (DB 직접 점검, §2.8 정합)**:
- Cursor 회신: 형법 25 + 민법 37 = 62 신규 row
- DB 실측: 형법 27 + 민법 40 = **67 row** (Cursor 옵션 A 안전 처리, 기존 5 row 보전 + 신규 62)
- 49 인용 조번호 vs 67 조문 행: "조의N" 분리 (예: 형법 제129조 + 제129조의2)

**적재 후 매핑 효과 검증**:
- citation cited_law_id (형법 125/125, 민법 92/92): **이미 100% 매칭** (이전 자동 보강 Step D law_name 기준) → Step D 재실행 효과 0
- inheritance V2 (외부 「~법」 인용): **0건** (일반법 자체 완결적 본문) → V2 재실행 효과 0
- **본 적재의 본질적 가치**: Track E Stage 분해 시점 발현 (형법 제129조 본문, 민법 제32조/제777조 본문 등 dict_legal_terms 활용 + Stage 2/3 역할별 분해 가능)

### 19.8 Track E Stage 3 룰 시안 작성

**시안 본질** (`Track_E_Stage3_Rules_Design.md`, 731줄, 29KB):
- 22 rule_objectify 룰 (HEADER 8 + ITEM 6 + 단편 4 + metadata/weak 4)
- 24 sub_type → 10 target_master_table 매핑
- field_mapping jsonb 시안 (8 핵심 객체 정확 매핑)
- v3.0 마스터 객체 테이블 10 CREATE TABLE 시안 (object_duty/prohibition/penalty/authority/exemption/definition/delegation/deeming/metadata/uncategorized)

**적용 절차 (후속)**:
1. v3.0 마스터 객체 테이블 마이그레이션 (10 CREATE TABLE)
2. rule_objectify 22 룰 INSERT
3. Stage 2 Phase 2 (Cursor Kiwi) 완료 (UNCLASSIFIED ≥ 90% 정밀 분류)
4. stage_3_objects 적재 (130,000~140,000 row 예상)
5. target_master_id UPSERT
6. 검증 (sample 정확도 ≥ 90%)

**진입 조건 (마스터 §3.4)**:
- Stage 2 sub_type 정확 분류 ≥ 90% (현재 5.41% → Kiwi 정밀화 후 70-85% 도달 후)
- 6하원칙 분해 sample 정확도 ≥ 90%

### 19.9 v1.6 EOD DB 상태 종합

| 항목 | 값 | 변화 (시작 대비) |
|---|---|---|
| law_master | 768 | +16 (Tier 1 14 + 군형법/난민법) |
| law_article (형법·민법) | +62 row 신규 | (인용 49 조번호 100%) |
| law_family_mapping | 768 (PRIMARY 139, ORPHAN 4, AdmRule parent_filled 221) | citation +18.18%p |
| **citation 매핑률** | **56.51%** | (시작 38.33% → 본 갱신) |
| dict_legal_terms | 14,942 (verified=true 1,725) | (변동 X) |
| stage_1_clauses | **151,751** | (Stage 1 신규) |
| stage_2_elements | **151,751** | (Stage 2 신규) |
| rule_clause_split | 11 (10 enabled) | (Stage 1 룰) |
| rule_classify_if_pattern | 8 | (Stage 2 룰) |
| rule_classify_subtype | 23 | (Stage 2 룰) |
| verification_log | 11 row (Stage 1: 5, Stage 2: 6) | (Track A validator.py 정합) |

### 19.10 v1.6 EOD 펜딩 사항 (다음 단계 PM 종합)

| 우선순위 | 작업 | 위탁 | 본질 |
|---|---|---|---|
| 1 | Cursor Stage 1 Phase 2 | Cursor (Python+Kiwi) | tokenization_json + split_rule_id + char_start/end (151,751) |
| 2 | Cursor Stage 2 Phase 2 | Cursor (Python+Kiwi) | UNCLASSIFIED 143,542건 정밀 분류 (HEADER 8 + ITEM 2 + WEAK 2 룰 18개) + 6하원칙 분해 |
| 3 | v3.0 마스터 객체 테이블 결정 | 사용자 | 옵션 A (신규 10 테이블) / B (master_rule_v2 활용) / C (jsonb only) |
| 4 | Tier 2 본법 13건 수집 | Cursor | 통계법/도서관법/정부조직법/비상대비법 + AdmRule 본법 |
| 5 | Track A P2 실환경 wall time | 다른 창 진행 중 | Track C v1.3 적용 영향 분석 회신 |
| 6 | Stage 3 진입 (Phase 2 + 마스터 결정 후) | Track E | 22 rule_objectify 적용 + stage_3_objects 적재 |
| 7 | QUARANTINE 4건 결정 (Track C) | 사용자 | 산업통상부 / 방송미디어통신위 / 중앙소방학교 / 한국전통문화대학교 |

### 19.11 v1.6 절대 원칙 점검 (마스터 §2)

| 원칙 | 본 v1.6 적용 |
|---|---|
| ① LLM X | ✅ 모든 작업 SQL/룰베이스 + Track A Kiwi 인프라 |
| ② 법령 보전 | ✅ source_text 모두 보전 / 형법·민법 67 row 보전 / Step 2 폐기는 백업 보전 |
| ③ 누락 0건 | ✅ Stage 1/2 누락 0 (143,549 distinct part_id, 151,751 distinct clause_id) / Tier 1 보강 누락 0 |
| ④ 100% 매핑 | ✅ Stage 1 1:N 분리 + Stage 2 1:1 매핑 + citation +1,305 |
| ⑤ 오염 = 폐기 | ✅ Step 2 폐기 (semantic_clause/relation 308,093 truncate, 백업 보전) |
| ⑥ 검증 부담 0 | ✅ 모든 작업 결정적 SQL + verification_log 자동 |
| ⑦ Ground Truth 우선 | ✅ DB 사실 점검 후 시안 정정 (§19.4 ENUMERATION 무효 발견 + §19.5 REGEX 불가 발견) |
| ⑧ DB가 ground truth | ✅ Cursor 회신 (62) vs DB 실측 (67), Track D Phase 1 12/14 vs 부분 적재 2건 발견, ENUMERATION 룰 0건 매칭 발견 |

---

**참고**: §15-§18 (Track B Day 3 ~ Track A 안정화 + Track C v1.2)은 v1.5 본문에 포함된 상세 영역. 본 commit은 §19 신규 추가 + §7/§8/§13 갱신 + §1-§6 보전 영역.

---

**END OF DOCUMENT v1.6**
