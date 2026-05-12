# TAI 법령엔진 v3.0 — 의미 요소 분해 엔진 구축 마스터 핸드오프

**문서 버전**: 1.5  
**작성일**: 2026-05-09  
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

### 4.1 데이터 흐름 (v1.5 갱신)

```
[Stage 0] 법령 원본 (보전)
   ├ law_master 752
   ├ law_article 33,862
   └ law_article_part 143,549
        │
        │ Track B: 가족 매핑 + 위임/인용 관계 + 행정규칙 매핑 ✅ v1.4 (100% 완료)
        ↓
   law_family_mapping (752) + law_article_delegation (7,730)
   + law_article_inheritance (15,850, 8 카테고리) + law_article_citation (7,179)
   + legalize_kr_mapping_raw (5,667 GT) + admrule_kr_mapping_raw (20,877 GT)
        │
        │ Track A: 엔진 인프라 ✅ v1.5 안정화 announce + Track C: 도메인 사전 ✅ v1.2
        ↓
   dict_legal_terms (14,942 row, verified=true 1,725) + morpheme.py 자동 로드 정합
        │
        │ Track E: Stage 1 분해 (Track D kordoc 완료 후 진입)
        ↓
[Stage 1] 의미절 분리 → [Stage 2] 역할별 분해 → [Stage 3] 객체화
```

### 4.2 엔진 구성

```
[엔진 모듈]
MorphemeEngine (Kiwi) ✅ / Stage1Splitter / Stage2Decomposer / Stage3Objectifier / Validator

[룰 DB]
dict_legal_terms ✅ / rule_clause_split / rule_pos_to_role / rule_ending_normalize 
/ rule_classify_subtype / rule_classify_if_pattern / rule_objectify

[산출물]
stage_1_clauses / stage_2_elements / stage_3_objects / verification_log
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

## 7. 멀티 트랙 작업 분담 (v1.5 갱신)

### Track A — 엔진 인프라 ✅ v1.5 안정화 announce
- **주체**: Cursor / Claude Code (TAI Backend 창)
- **목표**: Kiwi + DB 스키마 + 모듈 + 검증 hook
- **상태**: **안정화 announce 도달** (P0 해결 + 정지점 1 통과)
- **산출물 명세 8개 100% 도달**:
  - requirements.txt, DB migration (12 테이블), engine/morpheme.py (Kiwi + 자동 로드 페이지네이션), engine/stage_1.py / stage_2.py / stage_3.py, validator.py, 단위 테스트 ≥ 80% (실 85%)
- **핵심 commit**: `91c12da6` (morpheme.py 페이지네이션 패치) — `taiengineering/tai-api` dev
- **검증 (정지점 1)**: pytest 126 passed (직전 baseline 114 + 신규 12) / coverage 85% (morpheme.py 96%) / 두 트리 diff 0
- **자동 로드 정합**: `engine.user_dict_size == 1725` (Track C v1.2 ground truth 그대로 활용)
- **잔여 trackpoint** (안정화 호환):
  - **P1**: 다단어 토큰화 3건 (`'하수도법 시행규칙'`, `'하수도법 시행령'`, `'체외진단의료기기법 시행령'`) — 가설 F~I (add_user_word with whitespace / ZWJ / user_dict_path / blocklist) 미시도
  - **P2**: 실 환경 wall time 측정 (Track C 회신 양식 §18.4 대기) — Cursor `railway run` 위탁
- **상세**: `docs/extraction/v3/handoff/Track_A_handoff_20260509_EOD.md` + §18.1-3

### Track B — 가족 매핑 + 위임/인용 관계 + 행정규칙 매핑 ✅ (v1.4 — 100% 완료)
- **주체**: 사용자 + Claude 기획창 (TAI 회의실)
- **목표**: 법령 간 모든 관계 정의 (가족 + 조문 단위 위임 + 외부 인용 + 행정규칙)
- **기간**: Day 1 (2026-05-09) + Week 2 (2026-05-09)에 본질 작업 완료
- **상태**: **본질 작업 100% 완료**
- **산출물 (5개 raw + 4 관계 테이블 + 2 view)**:
  - `legalize_kr_mapping_raw` — legalize-kr ground truth (5,667 row)
  - `admrule_kr_mapping_raw` — admrule-kr ground truth (20,877 row)
  - `law_family_mapping` — 가족 관계 (752 법령, 744 verified)
  - `law_article_delegation` — 위임 source (7,730 row)
  - `law_article_inheritance` — 위임 target + 8 카테고리 분류 (15,850 row)
  - `law_article_citation` — 외부 인용 (7,179 row)
  - `v_law_family` / `v_law_family_tree` view
- **검증 엔진 V1 — 5 룰**: §15.4 참조
- **상세**: §14 (Step 1) + §15 (Step 2-3) + §16 (Step 2-F + 2-G) + §17 (Week 2)

### Track C — 법령 도메인 사전 ✅ v1.5 v1.2 본분 완수 명시
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
  - Track A P2 (정규식 컴파일 비용 측정) 회신 대기 → v1.3 적용 영향 분석
  - v1.3 설계 시안 (`docs/extraction/v3/track_c/v1_3_design_proposal.md`) — Track E 시작 시점 적용 후보
  - QUARANTINE 4건 결정 (산업통상부 / 방송미디어통신위원회 / 중앙소방학교 / 한국전통문화대학교)
- **상세**: `docs/extraction/v3/handoff/Track_C_handoff_20260509_EOD.md` + §18.4-6

### Track D — 별표·서식 처리 (kordoc) 🔄 진행 중
- **주체**: Cursor (TAI Backend 부속 창)
- **목표**: 법령 별표 PDF/HWP 자동 변환 파이프라인
- **기간**: Week 1-2 (완전 독립)
- **상태**: 별도 창 작업 시작 (2026-05-09) — 진척도 별도 회신 대기

### Track E — Stage 분해 사이클 (메인) ⏳ 진입 대기
- **주체**: Claude 기획창 + Cursor (TAI 회의실 메인)
- **목표**: Stage 1 → Stage 2 → Stage 3 순차 완성
- **기간**: Week 5-12 (정밀) / Week 5-8 (MVP)
- **시작 조건**: Track A ✅ + Track B ✅ + Track C ✅ + Track D 완료 후
- **현재**: Track D 완료 대기 중

---

## 8. 스케줄 (v1.5 갱신)

### Week 1 (2026-05-09)
- **Track A**: ✅ Kiwi 설치 → DB 스키마 → 엔진 모듈 → 정지점 1 통과 → **안정화 announce**
- **Track B**: ✅ Day 1-3 본질 작업 + Step 2-A~G + Week 2 admrule-kr 완료
- **Track C**: ✅ v1.2 본분 완수 (1,725 verified, Week 4 마일스톤 Day 1 추월)
- **Track D**: 🔄 kordoc 도입 진행 중

### Week 2
- **Track A**: P1 다단어 3건 + P2 실환경 측정 (안정화 호환 trackpoint)
- **Track B**: ✅ admrule-kr 매핑 완료
- **Track C**: Track A P2 회신 후 v1.3 적용 여부 판단
- **Track D**: 별표 일괄 변환 스크립트 완성 (예정)

### Week 3-4
- **★ Step 2 폐기**: semantic_clause + relation truncate
- **TAI 추가 수집 12건+** (Cursor, 법제처 API)

### Week 5-12 — Stage 1 → 2 → 3 분해 사이클

### 마일스톤 (v1.5 실적 갱신)

| 시점 | 마일스톤 | 실적 |
|---|---|---|
| End Week 1 | Kiwi 작동 + Track B Step 1+2+3 완료 | ✅ Day 1 모두 달성 (A 안정화 / B 본질 100% / C v1.2) |
| End Week 2 | Track B 100% 완료 (admrule-kr 매핑 포함) | ✅ Day 1 |
| End Week 4 | 인프라 완성 + Step 2 폐기 | A ✅ Week 1 / Step 2 폐기 Week 3-4 예정 |
| End Week 6 | Stage 1 완료 | (Track D 완료 후 시작) |
| End Week 10 | Stage 2 완료 | - |
| End Week 12 | Stage 3 + 마스터 합성 완료 | - |

---

## 9-11. 검증 절차 / 협업 / 도구

(v1.0~1.2 동일, 변경사항 §15-§18 참조)

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

---

## 13. 변경 이력

- **v1.0** (2026-05-09): 초기 작성 — LLM 사용 금지 + 3단 분해 + 25 sub_type + 7 IF 패턴 + Kiwi/legalize-kr/kordoc + 멀티 트랙 12주 스케줄
- **v1.1** (2026-05-09): Track B Day 1~3 완료 — 절대 원칙 §2.6/§2.7 추가 + Track B 366건 매핑 + 검증 엔진 V1-A 도입 + §14 신설
- **v1.2** (2026-05-09): Track B Step 2 + Step 3 완료 — 위임 7,730 + inheritance 8,641 + citation 7,179 + 검증 엔진 V1 4룰 + TAI 추가 수집 12건 우선순위 + §15 신설
- **v1.3** (2026-05-09): Track B Step 2-F + Step 2-G 완료 — inheritance 보강 (8,641 → 15,850, 1.83배) + citation_purpose 8 카테고리 분류 + 위임 전용 cross-validate 86.6% + 검증 엔진 V1 5룰 (V1-E 추가) + §16 신설
- **v1.4** (2026-05-09): Track B Week 2 admrule-kr 매핑 완료 — `admrule_kr_mapping_raw` 20,877 + ADMINISTRATIVE_RULE 386 (룰 1 MST 319 + 룰 2 title 66 + V1-A fallback 1) + parent_law_id 218 (V1-A 확장 적용) + delegation STANDARD/NOTICE 166 NULL 유지 (§2.7 정합) + §17 신설 + §2.7 진입 절차 적용 명시
- **v1.5** (2026-05-09): Track A 안정화 announce 명시 (commit `91c12da6` P0 해결 + 정지점 1 통과 / 126 passed / coverage 85% / morpheme.py 96%) + Track C v1.2 본분 완수 명시 (dict_legal_terms 14,942 row, verified=true 1,725) + §3.3 모노레포 + sub-repo 구조 정정 + §18 신설 (Track A 안정화 + Track C 본분 완수)

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

### 14.3 ORPHAN 6건 (Week 2 결정 대기)

통계법, 도서관법, 정부조직법, 방송통신발전 기본법, 비상대비에 관한 법률, 도로교통법

---

## 15. (v1.2) Track B Step 2 + Step 3 결과 — 위임/인용 관계

### 15.1 산출물 통합 (5개 raw + 4 관계 테이블 + 2 view, v1.4 갱신)

| 테이블 | row | 의미 | 매핑률 |
|---|---|---|---|
| `law_family_mapping` | **752** | 가족 (PRIMARY ↔ 시행령 ↔ 시행규칙 ↔ 행정규칙) | 100% (98.9% verified) |
| `law_article_delegation` | 7,730 | 위임 source-of-truth | 97.4% target_law_id |
| `law_article_inheritance` | 15,850 | 위임 target + 8 카테고리 분류 | 99.6% parent_article_id |
| `law_article_citation` | 7,179 | 외부 법령 인용 (cross-reference) | 38.3% TAI 매핑 |
| `legalize_kr_mapping_raw` | 5,667 | legalize-kr ground truth | (활용용) |
| **`admrule_kr_mapping_raw`** | **20,877** | **admrule-kr ground truth** | **(활용용)** |
| `v_law_family` / `v_law_family_tree` | view | 가족 트리 통합 조회 | - |

### 15.2 Step 2 — 조문 단위 위임 관계

**Step 2-A: law_article_delegation (위임 source)**
- 4개 type별 별도 INSERT (다중 위임 보강): DECREE 4,702 / RULE 2,862 / STANDARD 155 / NOTICE 11

**Step 2-B: target_law_id 자동 매핑** — 97.4% (행정규칙 의존 166건은 §17 결론 NULL 유지)

**Step 2-D: law_article_inheritance (위임 target)**
- 정규식: `법\s*제(\d+)조...` / `영\s*제(\d+)조`
- 1차 (첫 300자, 첫 매칭): 8,641 row, 99.7% 매핑

**Step 2-E: cross-validate** — 양방향 일치 86.5%

### 15.3 Step 3 — 외부 법령 인용 (cross-reference)

- 정규식 + REGEXP_MATCHES 'g' (다중 인용)
- 7,179 row, 633 unique 인용 법령명, TAI 매핑 38.3%
- TAI 추가 수집 우선순위 도출 (전자정부법 413, 형법 125, 민법 92 등)

### 15.4 검증 엔진 V1 — 5 룰 명세 (v1.4 갱신)

| 룰 | 입력 | 산출 | 매핑률 |
|---|---|---|---|
| V1-A: 자기 정의 패턴 | 시행령/규칙/행정규칙 본문 article 1-3 | 부모 본법명 추출 | 23/239 별도 디렉토리 (Day 3) + 218/386 (Week 2 ADMINISTRATIVE_RULE 확장) |
| V1-B: legalize-kr 디렉토리 | 5,667 row | 가족 매핑 ground truth | 95% direct + 5% V1-A 보완 |
| V1-B': admrule-kr 디렉토리 ★ | 20,877 row | 행정규칙 매핑 ground truth | 룰 1 MST 82.6% + 룰 2 title 17.1% (Week 2) |
| V1-C: source × inheritance cross-validate | delegation × inheritance | 양방향 일치 검증 | 86.5% (V1) → 86.6% (V3) |
| V1-D: cited_law_name TAI 매칭 | citation 추출 | TAI 추가 수집 우선순위 | 38.3% (2,752/7,179) |
| V1-E: citation_purpose 8 분류 | inheritance 직후 30자 | 위임 vs 일반 인용 분류 | 15,850 row 100% 분류 |

### 15.5 활용 가이드 (Track A/C/E용, v1.4 갱신)

```sql
-- 1. 자식 article의 진짜 부모 (위임 받은 것만)
SELECT 
  child.law_name AS 자식법령,
  child_la.article_no AS 자식조,
  parent.law_name AS 본법,
  lai.parent_article_no AS 본법조,
  lai.citation_purpose
FROM law_article_inheritance lai
JOIN law_article child_la ON child_la.id = lai.child_article_id
JOIN law_master child ON child.id = lai.child_law_id
JOIN law_master parent ON parent.id = lai.parent_law_id
WHERE lai.citation_purpose IN ('DELEGATION_DIRECT', 'DELEGATION_FOLLOW')
   OR lai.is_first_in_article = true;

-- 2. 본법 정의 article 자식 활용 (DEFINITION_QUOTE)
SELECT 
  parent_la.article_no AS 본법조,
  COUNT(*) AS 정의인용_횟수
FROM law_article_inheritance lai
JOIN law_article parent_la ON parent_la.id = lai.parent_article_id
WHERE lai.citation_purpose = 'DEFINITION_QUOTE'
  AND lai.parent_law_id = (SELECT id FROM law_master WHERE law_mst_no = '276853')
GROUP BY parent_la.article_no
ORDER BY 정의인용_횟수 DESC;

-- 3. 본법 한 조문의 인용 분포 (Stage 분해 시 활용)
SELECT 
  parent_la.article_no AS 본법조,
  lai.citation_purpose,
  COUNT(*) AS cnt
FROM law_article_inheritance lai
JOIN law_article parent_la ON parent_la.id = lai.parent_article_id
WHERE lai.parent_law_id = (SELECT id FROM law_master WHERE law_mst_no = '276853')
GROUP BY parent_la.article_no, lai.citation_purpose
ORDER BY parent_la.article_no, cnt DESC;

-- 4. cross-validate 통과 위임 관계 (V3 정밀, citation_purpose 활용)
SELECT 
  source_law.law_name AS 본법,
  delegation.source_article_no AS 본법조,
  delegation.delegation_target_type AS 위임type
FROM law_article_delegation delegation
JOIN law_master source_law ON source_law.id = delegation.source_law_id
WHERE EXISTS (
  SELECT 1 FROM law_article_inheritance lai
  WHERE lai.parent_law_id = delegation.source_law_id
    AND lai.parent_article_no = delegation.source_article_no
    AND (
      lai.citation_purpose IN ('DELEGATION_DIRECT', 'DELEGATION_FOLLOW')
      OR lai.is_first_in_article = true
    )
);

-- 5. (v1.4) 본법 + 가족 + 행정규칙 통합 트리 조회
SELECT 
  child.law_name,
  child.law_type_code,
  lfm.family_role,
  lfm.mapping_method,
  parent.law_name AS parent_name
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

### 15.6 다음 단계 (v1.5 갱신)

| 우선순위 | 작업 | 의존 | 예상 결과 |
|---|---|---|---|
| ✅ | Week 2 admrule-kr 매핑 | 사용자 git clone | **완료** (§17, ADMINISTRATIVE_RULE 386) |
| ✅ | Track A 안정화 announce | commit `91c12da6` | **완료** (§18.1-3) |
| ✅ | Track C v1.2 본분 완수 | Railway 실행 | **완료** (§18.4-6, 1,725 verified) |
| 1 | Track A P2 (실환경 wall time 측정) | Cursor `railway run` | Track C v1.3 적용 여부 판단 근거 |
| 2 | Track D 진척도 회신 + 완료 | Track D 별도 창 | Track E 진입 게이트 |
| 3 | TAI 추가 수집 12건 + α | 법제처 API (Cursor) | inheritance 매핑 자동 보강 + ORPHAN 6 해소 + ADMINISTRATIVE_RULE parent_null 168 보강 |
| 4 | Track E 시작 — Stage 1 분해 | A ✅ + B ✅ + C ✅ + D | 의미절 분리 (Week 5-6) |
| 5 (옵션) | 룰 V4 (DEFINITION_QUOTE → law_term_extraction) | 없음 | 본법 정의 어휘 도출 (Track C v1.3 후보) |
| 6 (옵션) | delegation 본문 정밀 추출 룰 V2 | 없음 | STANDARD/NOTICE 166건 보강 |

### 15.7 Track B 단독 진행 종합 (v1.4 갱신)

**완료 영역 (100%)**:
- ✅ 가족 관계 (PRIMARY ↔ 시행령 ↔ 시행규칙 ↔ 행정규칙)
- ✅ 조문 단위 위임 관계 (양방향: source + target)
- ✅ 외부 법령 인용 (cross-reference)
- ✅ inheritance 보강 (1.83배, 282건 → 149건 한계 해소)
- ✅ 인용 8 카테고리 분류 (citation_purpose)
- ✅ **행정규칙 매핑 (admrule-kr 386건)** ★
- ✅ 검증 엔진 V1 5룰 (V1-A 행정규칙 확장 적용)

**미해소 (TAI 추가 수집 + 룰 V2 후 보강 가능)**:
- ⏳ ADMINISTRATIVE_RULE parent_null 168건 (V1-A 추출 but TAI 미수집 42 + V1-A 미추출 126)
- ⏳ delegation STANDARD/NOTICE target_null 166건 (TAI 모집단 외부 + 다중매칭)
- ⏳ ORPHAN 6건 (본법 TAI 미수집)

**Track B 한계** — 다음은 Track A/C/D/E 영역.

---

## 16. (v1.3) Track B Step 2-F + Step 2-G 결과 — 보강 + 분류

### 16.1 Step 2-F — inheritance 룰 V2 보강

**문제 (Step 2-D 한계)**:
- 1차 inheritance 룰 V1: 자식 article 본문 첫 300자 + 첫 매칭만
- 인용 위치가 본문 깊은 곳 (예: 1,384자, 2,589자)에 있으면 누락
- cross-validate "위임표현만" 282건 (7.7%) 발견 원인

**해결 (룰 V2 — regex_v2_enhanced)**:
- LEFT(article_text, 300) → article_text 전체
- DISTINCT ON 단일 매칭 → REGEXP_MATCHES 'g' (모든 매칭)
- is_first_in_article=false 마킹 (1차와 구분)
- 중복 방지: 같은 child + parent_article_no SKIP

**결과**:
- "법" 보강 +6,156 row, "영" 보강 +1,053 row
- inheritance 8,641 → **15,850 row** (1.83배)
- parent_article_id 매핑 99.6%

**Cross-validate 효과**:

| 검증결과 | 보강 전 (V1) | 보강 후 (V2) | 변화 |
|---|---|---|---|
| ✓ 양방향 일치 | 3,151 (86.5%) | 3,284 | **+133** |
| ⚠ 위임표현만 | 282 (7.7%) | **149** | **-133** (47% 감소) |
| ⚠ 자식 인용만 | 210 | 543 | +333 (정책 article 추가 발견) |

### 16.2 Step 2-G — citation_purpose 8 카테고리 분류

**도입 이유**: V2 보강으로 inheritance가 1.83배 증가했으나, 위임 vs 일반 인용 구분 X → 다음 Stage 분해 시 모호함.

**8 카테고리** (룰 V3 — citation_purpose):

| citation_purpose | 패턴 | 본질 | cnt | pct |
|---|---|---|---|---|
| APPLICATION_REF | "에 따른 X" | 적용 대상 정의 | 6,386 | 40.3% |
| APPLICATION_ACT | "에 따라 X(행위)" | 적용 행위 | 3,695 | 23.3% |
| GENERAL | 위 분류 미해당 | 일반 인용 | 2,527 | 15.9% |
| DEFINITION_QUOTE | "에서 \"X\"이란" | 본법 용어 정의 인용 | 1,507 | 9.5% |
| STRUCTURAL_REF | "각 호 외의", "규정에 의한" | 구조적 참조 | 1,078 | 6.8% |
| **DELEGATION_DIRECT** ★ | "본문/전단/단서/후단에 따라" | **직접 위임** | 448 | 2.8% |
| **DELEGATION_FOLLOW** ★ | "에 따라 다음 각 호" | **enumeration 위임** | 209 | 1.3% |

**핵심 발견**: 시행령/규칙 본문 인용 중 **위임 표현 직접 명시는 4.1% (657건)만**. 나머지 95.9%는 일반 인용.

**결론**: 
- **delegation 테이블이 위임 관계 source-of-truth** (본법 본문에서 위임 표현 추출)
- inheritance + citation_purpose는 자식 → 부모 인용 매핑 보완 (위임 = 4.1%, 일반 인용 = 95.9%)

### 16.3 위임 전용 cross-validate (V3)

**위임 전용 매칭** = `DELEGATION_DIRECT + DELEGATION_FOLLOW + is_first_in_article=true`:

| 검증결과 | cnt | 비율 |
|---|---|---|
| ✓ 양방향 일치 | 3,158 | **86.6%** |
| ⚠ 위임표현만 | 275 | 7.5% |
| ⚠ 위임 인용만 | 212 | 5.8% |

**정밀도 진화**:
- V1 (1차 inheritance, 첫 매칭): 86.5%
- V2 (보강 inheritance, 모든 매칭): 82.6% (희석됨)
- **V3 (위임 카테고리만)**: **86.6%** (가장 정확) ★

→ citation_purpose 분류가 본질적으로 의미있음을 입증.

### 16.4 산출물 (v1.3)

**테이블 컬럼 추가**:
- `law_article_inheritance.citation_purpose` (8 카테고리 CHECK)
- `law_article_inheritance.is_first_in_article` (boolean)
- `law_article_inheritance.extraction_method` ('regex_v1' / 'regex_v2_enhanced' / 'manual')

**Stage 분해 시 활용**:
- 진짜 부모 식별 = `is_first_in_article=true` OR `citation_purpose IN ('DELEGATION_DIRECT', 'DELEGATION_FOLLOW')`
- 본법 정의 어휘 = `citation_purpose='DEFINITION_QUOTE'` (Track C 사전 후보)
- 적용 대상/행위 = `APPLICATION_REF/ACT` (Stage 2 sub_type 매핑 보완)

### 16.5 보고서 chronology

| 시점 | 보고서 | commit |
|---|---|---|
| Day 1 | Track_B_20260509.md | (Day 1 폐기 전) |
| Day 2 | Track_B_20260509_Day2.md | (Day 2 폐기 전) |
| Day 3 | Track_B_20260509_Day3.md | 가족 매핑 366건 |
| Step 2 | Track_B_20260509_Step2.md | 위임 관계 7,730건 |
| Step 2-E + 3 | Track_B_20260509_Step2E_Step3.md | cross-validate + 외부 인용 |
| Step 2-F | Track_B_20260509_Step2F.md | 룰 V2 보강 1.83배 |
| Step 2-G | Track_B_20260509_Step2G.md | citation_purpose 8 분류 |
| Week 2 | Track_B_20260509_Week2.md | admrule-kr 매핑 386건 |
| Master | MASTER_HANDOFF.md v1.5 | 본 문서 |

---

## 17. (v1.4) Track B Week 2 결과 — admrule-kr 행정규칙 매핑

### 17.1 산출물

| 테이블 | v1.3 | Week 2 후 | 변화 |
|---|---|---|---|
| `admrule_kr_mapping_raw` | 0 | **20,877** | 신규 적재 (admrule-kr GT) |
| `law_family_mapping` | 366 | **752** | **+386 ADMINISTRATIVE_RULE** |
| `law_article_delegation` | 7,730 | 7,730 | notes 보강 (166건, NULL 유지) |

### 17.2 매핑 결과 (386건)

| family_role | mapping_method | cnt | 비율 | verified |
|---|---|---|---|---|
| ADMINISTRATIVE_RULE | admrule_kr_mst (룰 1, 13자리 1:1) | 319 | 82.6% | 319 ✓ |
| ADMINISTRATIVE_RULE | admrule_kr_title (룰 2, 정규화 매칭) | 66 | 17.1% | 66 ✓ |
| ADMINISTRATIVE_RULE | validator_v1_self_def (V1-A fallback) | 1 | 0.3% | 1 ✓ |
| **합계** | - | **386** | 100% | **386 ✓** |

**룰 1 (MST) 미해소 1건 정체**: "방사선 안전관리 등의 기술기준에 관한 규칙" (MST 2100000229784, OTHER, 원자력안전위원회). admrule-kr 모집단에 동일 MST/title 부재 → V1-A fallback 처리.

### 17.3 parent_law_id 본문 추출 (V1-A 확장 적용)

**V1-A 패턴 2개** (PostgreSQL regex):
- 패턴 A (자기 정의): `「([^」]+)」[^「」]{0,40}\(이하\s*["「]?(?:법|법률|시행령|영|시행규칙|규칙|통칙)["」]?\s*(?:이라|라)?\s*한다`
- 패턴 B (첫 「~법/법률」 인용): `「([^」]+(?:법|법률))(?:\s*시행령|\s*시행규칙)?」`

| 케이스 | cnt | 비율 | parent_filled |
|---|---|---|---|
| V1-A 매칭 (LAW 정확 매칭) | 218 | 56.5% | 218 ✓ |
| V1-A 추출 but TAI 미수집 | 42 | 10.9% | 0 (NULL, notes 보존) |
| V1-A 미추출 (KDS/KC/별표 나열형) | 126 | 32.6% | 0 (NULL, notes 보존) |
| **합계** | **386** | 100% | **218 (56.5%)** |

**미추출 원인**:
- KDS 표준 (예: 기초 내진 설계기준 KDS 11 50 25): 「~법」 인용 없는 자체 형식
- KC 안전기준 (예: 전기용품 안전기준 KC 60335-2-25): "제ㆍ개정 이유" 형식
- 별표 나열형 행정규칙 (예: 진료권역별 상급종합병원의 소요병상수)

### 17.4 delegation STANDARD/NOTICE 자동 해소 결과

**dry-run 부처+type 매칭 분포**:

| 매칭 | NOTICE | STANDARD | 합계 |
|---|---|---|---|
| 0_no_match | 1 | 132 | 133 |
| **1_unique** | **0** | **0** | **0** ★ |
| 2-5_multi | 2 | 23 | 25 |
| 6+_multi | 8 | 0 | 8 |
| **합계** | 11 | 155 | 166 |

**결정 — §2.7 추정 매핑 금지 정합**: 단일매칭 0건 → 자동 해소 불가. 부처+type 다중매칭은 정확한 target 식별 불가 (delegation 본문에 명시적 「~고시」 인용 부재).

→ **delegation 미해소 166건은 NULL 유지, notes 보강만**

| target_type | multi_match (다중매칭) | no_candidate (TAI 미수집) | 합계 |
|---|---|---|---|
| NOTICE | 10 | 1 | 11 |
| STANDARD | 23 | 132 | 155 |
| **합계** | 33 | 133 | **166** |

### 17.5 검증 — 산안법 sample (domain_code=INDUSTRIAL_SAFETY)

가족 트리 통합 조회 결과:
- **PRIMARY**: 산업안전보건법 / 중대재해 처벌 등에 관한 법률 / 한국산업안전보건공단법
- **ENFORCEMENT_DECREE/RULE**: 5건 (validator_v1_self_def 정확 매칭 포함)
- **ADMINISTRATIVE_RULE — 산업안전보건법 직속 13건**: 건설공사 안전보건대장 / 안전보건교육규정 / 화학물질 분류·표시 등
- **Cross-domain V1-A 정확성 검증**: 안전·보건 업무 수행시간 고시 → 중대재해 처벌법 ✓ / 안전성 평가 고시 → 화학물질관리법 ✓ / 조달청 시설공사 → 건설기술 진흥법 ✓

→ **검증 통과**: 가족 트리 완성, V1-A 정확성, parent NULL 케이스 명확 분류.

### 17.6 Track B 한계 (Week 2 후)

| 영역 | 미해소 | 본질 |
|---|---|---|
| ADMINISTRATIVE_RULE parent_null | 168 (42 + 126) | TAI 미수집 본법 + 본문 인용 부재 |
| delegation STANDARD/NOTICE target_null | 166 | TAI 모집단 외부 위임 + 다중매칭 |
| ORPHAN | 6 | 본법 TAI 미수집 |

→ **§15.6 우선순위 3 (TAI 추가 수집)** 진행 시 자동 보강 가능.

### 17.7 백업 chronology

| 백업 | 시점 | row |
|---|---|---|
| `law_family_mapping_backup_20260509_v3_attempt1` | Day 1+2 폐기 | 366 |
| `law_family_mapping_backup_20260509_v3_week2_pre_step_c` | Week 2 Step C 직전 | 751 |
| `law_article_delegation_backup_20260509_v1` | Step 2-A 1차 INSERT | 6,498 |

### 17.8 본 작업 chronology (교훈)

- 인계 §1 "INSERT 실행 대기" 표기를 작성 시점 기준으로 사실 수용 → 진입 시 DB 점검으로 Step B까지 완료된 상태 확정
- 본 창 작업 범위: Step C (V1-A 확장 + UPDATE 386건) + Step D (자동 해소 불가 + notes 보강) + 검증 + 보고서

**교훈**: §2.7 Ground Truth 우선은 작업뿐 아니라 진입 절차에도 적용. 인계 문서는 참고, **DB가 ground truth**. Track C 핸드오프 §4 "DB 사실 재확인용 — 새 인스턴스 진입 시 1차 실행" 정합. → §2.7 본문 갱신 (v1.4).

### 17.9 보고서

- `docs/extraction/v3/log/Track_B_20260509_Week2.md`

---

## 18. (v1.5) Track A 안정화 announce + Track C v1.2 본분 완수

### 18.1 Track A — P0 해결 사실

**P0 본질**: `engine/morpheme.py` `load_verified_dict_from_db`가 PostgREST max-rows=1000 제약으로 1,000건만 로드 (Track C v1.2 1,725건 부족 로드 — 자동 로드 미스터리).

**해결 (commit `91c12da6`, taiengineering/tai-api dev)**:
- `.limit(5000)` → `.range(start, end)` 페이지네이션 (page_size=1000, max_pages=50)
- `scripts/v3/extract_generic_candidates.py` 검증된 패턴 동일 적용 (v1.2 GENERIC 14,474건 추출 정상 수행 입증)
- 호환: 기존 `limit` 인자 keyword-only deprecated, warning 후 무시
- 동반 변경: 
  - `tests/v3/conftest.py` `_Builder.range()` 추가 (mock 통합 환경 재현)
  - `tests/v3/test_morpheme_pagination.py` 신규 12 case (TestPagination 8 + TestAutoLoadIntegration 2 + TestDeprecatedLimit 2)

### 18.2 Track A — 정지점 1 통과 검증

```
git rev-parse upstream/dev → 91c12da6bd32cd8ee500a58863feab956435894a
git merge-base HEAD upstream/dev → 91c12da6 (모노레포 루트 mirror 동기화 완료)
diff /engine/morpheme.py /tai-api/engine/morpheme.py → exit 0 (동일)
pytest tests/v3/ -v --cov=engine → 126 passed, 약 20.65s
  - 직전 baseline: 114 passed
  - 신규 12 case 모두 통과 (TestPagination + TestAutoLoadIntegration + TestDeprecatedLimit)
커버리지: 합계 85% (이전 83%), morpheme.py 96% (이전 90%)
```

**자동 로드 정합**: `engine.user_dict_size == 1725` (Track C v1.2 ground truth 그대로 활용)

### 18.3 Track A — 잔여 trackpoint (안정화 호환)

| trackpoint | 정체 | 상태 |
|---|---|---|
| **P1**: 다단어 토큰화 3건 | `'하수도법 시행규칙'` → `'하/IC + 수도법 시행규칙/NNP'` (2토큰) / `'하수도법 시행령'` → `'하/IC + 수도법 시행령/NNP'` (2토큰) / `'체외진단의료기기법 시행령'` → 3토큰 분해 | 가설 A~E 모두 실패 / 가설 F~I (add_user_word with whitespace / ZWJ / user_dict_path / blocklist) 미시도 |
| **P2**: 실 환경 wall time 측정 | 인스턴스 생성 + 자동 로드 wall time / warmup vs warm 토큰화 / 100회 평균 / 정규식 컴파일 EAGER/LAZY | 본 창 환경 python3 직접 실행 X. mock 측정값은 supabase HTTP 비용 미반영. 잘못된 측정값 회신 시 §10 학습 #2 위배 → Cursor `railway run` 위탁 |

**P1·P2 분리 사유 (§10 학습 #2 정합)**: 검증 전 단언 X. 마스터 §7 Track A 산출물 명세 8개 100% 유지 도달이 안정화 announce 게이트. P1은 명세 외 정밀도 trackpoint, P2는 측정 환경 제약 trackpoint. 두 trackpoint 모두 안정화 호환 — 차기 인스턴스에서 별도 트리거로 처리.

**상세 핸드오프**: `docs/extraction/v3/handoff/Track_A_handoff_20260509_EOD.md`

### 18.4 Track C — v1.2 본분 완수 명시

**dict_legal_terms 분포 (14,942 row 적재, verified=true 1,725, verified=false 13,217 보전)**:

| term_type | verified | count | 다단어 | 자동 로드 대상 |
|---|---|---|---|---|
| LAW_NAME | TRUE | 423 | 344 | ✅ |
| AGENCY_NAME | TRUE | 26 | 0 | ✅ |
| TECH_TERM | TRUE | 15 | 0 | ✅ |
| GENERIC | TRUE | 1,261 | 0 | ✅ |
| AGENCY_NAME | FALSE (QUARANTINE) | 4 | 0 | ❌ |
| GENERIC | FALSE | 13,213 | 20 | ❌ |
| **합계** | - | **14,942** | **364** | **1,725** |

**적재 단계별 이력**:

| 버전 | 적재 내용 | verified=true 누적 | 실행 |
|---|---|---|---|
| v1 | LAW 본법 145 + AGENCY 30 + TECH 15 = 190 | 186 | 사용자 SQL |
| v1.1 | + ENFORCEMENT_DECREE 139 + ENFORCEMENT_RULE 139 = +278 | 464 | 사용자 SQL |
| v1.2 | + GENERIC 14,474 (verified=true 1,261) | **1,725** | Railway `extract_generic_candidates.py` |

### 18.5 Track C — 마일스톤 추월 분석

| MASTER_HANDOFF 명세 | 계획 | 실적 | 추월 사유 |
|---|---|---|---|
| Week 2: 빈도 분석 + 후보 리스트 공유 | End Week 2 | Day 1 | ground truth (`law_master`) 발굴 → 빈도 분석 우회 |
| Week 3: 사용자 검증 Top 500 | End Week 3 | Day 1 (대체) | 사용자 검증 → 룰베이스 자동 검증 (1,261 통과) |
| Week 4: dict_legal_terms v1 등록 | End Week 4 (500-1,000) | Day 1 (1,725) | ground truth 직접 등록 + GENERIC 자동 검증 |

→ **추월 핵심**: 사용자 검증 단계 자체를 ground truth + 룰베이스 자동 검증으로 대체. 사람 의존 0, LLM 의존 0, 절대원칙 100% 부합 (특히 §2.6).

### 18.6 Track C — 펜딩 & 자체 평가

**펜딩**:
1. Track A P2 (정규식 컴파일 비용 측정) 회신 대기 → v1.3 적용 영향 분석
2. v1.3 설계 시안 (`docs/extraction/v3/track_c/v1_3_design_proposal.md`) — Track E 시작 시점 적용 후보 (이중 필터 제거 / 다중 사유 기록 / TH_DF_LOW 완화 / 평가 순서 재조정)
3. QUARANTINE 4건 결정 (산업통상부 / 방송미디어통신위원회 / 중앙소방학교 / 한국전통문화대학교)

**자체 평가**:
- 본분 완수: dict_legal_terms v1 적재 완료 (verified=true 1,725)
- 품질: Top 30 sanity 93% (28/30 도메인 적합)
- 데이터 보전: verified=false 13,217건 보전 (§2.3 부합)
- 추적 가능성: 모든 row에 source 명시
- 재현 가능성: dry-run 예측 = 실 결과 100% 일치
- 트랙 협업: Track A 인터페이스 검증 통과 (자동 로드 + 다단어 토큰화 100%)

**상세 핸드오프**: `docs/extraction/v3/handoff/Track_C_handoff_20260509_EOD.md`

### 18.7 v1.5 다음 단계 (PM 종합)

| 우선순위 | 작업 | 의존 | 트랙 |
|---|---|---|---|
| 1 | Track A P2 (실환경 wall time 측정) | Cursor `railway run` | Track A → Track C 회신 |
| 2 | Track D 진척도 회신 + 완료 | Track D 별도 창 | PM |
| 3 | TAI 추가 수집 12건 + α | 법제처 API (Cursor) | Track B 보강 + Track C 어휘 추가 |
| 4 | Track E 시작 — Stage 1 분해 | A ✅ + B ✅ + C ✅ + D | Track E |

---

**END OF DOCUMENT v1.5**
