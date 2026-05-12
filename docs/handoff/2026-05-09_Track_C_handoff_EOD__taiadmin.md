# Track C 핸드오프 — 2026-05-09 EOD

**작성**: Track C 인스턴스 (2026-05-09 EOD)
**대상**: 차기 Track C 인스턴스
**용도**: 새 작업창에서 Track C 컨텍스트 자력 복원
**우선 숙지 순서**: 본 문서 → MASTER_HANDOFF v1.0 → Track_C_20260509.md → 필요 시 v1_3_design_proposal.md

---

## 1. 한 문단 요약

Track C v1.2 본분 완수 상태. dict_legal_terms 14,942 row 적재 (verified=true 1,725, verified=false 13,217 보전). v3.0 목표 500-1,000 대비 172% 달성, Week 4 마일스톤 1일에 추월. 절대원칙 5개 누적 통과. 다음 트리거 대기.

## 2. 본 트랙 정체성 (재확인)

- **Track ID**: C — 법령 도메인 사전
- **기간 명세**: Week 2-4 (실 완료 Week 2 Day 1)
- **입출력**: `law_article_part.part_text` (143,549) + `law_master` (752 active) → `dict_legal_terms` 14,942
- **선행 의존**: Track A Phase 1 (Kiwi 설치) — 완료. Track A Day 2 (`engine/morpheme.py`) — 완료.
- **권한 범위**:
  - ✅ Supabase MCP — SELECT / INSERT / UPDATE
  - ✅ GitHub MCP (taiengineering/tai-admin, taiengineering/tai-api dev)
  - ❌ Railway 실행 환경 직접 접근 — 사용자 또는 Track A 위탁
  - ❌ Kiwi 직접 호출 — Track A `morpheme.py`를 통한 간접만 (자동 로드 인터페이스)

## 3. 절대원칙 (MASTER_HANDOFF §2 — 위배 시 트랙 정지)

1. **LLM X** — Cursor/GPT/Claude/Gemini 의미해석 위탁 X. Kiwi + 룰베이스 + ground truth만.
2. **법령 보전** — 어휘 변형 0. `t.form` 또는 ground truth 직접 사용.
3. **놓치는 것 = 리스크** — 미달 후보도 `verified=false`로 적재.
4. **100% 매핑** — 모든 row에 `source` 명시 (예: `law_master.law_name:ground_truth`, `law_article_part.part_text:kiwi-extraction`).
5. **오염 = 폐기** — dry-run 예측 = 실 결과 일치 시에만 진행.

본 트랙 누적 점검: v1, v1.1, v1.2 모든 단계 통과.

## 4. DB 현황 (2026-05-09 EOD 점검)

### dict_legal_terms 분포

| term_type | verified | count | 다단어 | 자동 로드 대상 |
|---|---|---|---|---|
| LAW_NAME | TRUE | 423 | 344 | ✅ |
| AGENCY_NAME | TRUE | 26 | 0 | ✅ |
| TECH_TERM | TRUE | 15 | 0 | ✅ |
| GENERIC | TRUE | 1,261 | 0 | ✅ |
| AGENCY_NAME | FALSE (QUARANTINE) | 4 | 0 | ❌ |
| GENERIC | FALSE | 13,213 | 20 | ❌ |
| **합계** | | **14,942** | **364** | **1,725** |

### 검증 코드 (DB 사실 재확인용 — 새 인스턴스 진입 시 1차 실행)

```sql
SELECT term_type, verified, COUNT(*) AS count,
       COUNT(*) FILTER (WHERE term ~ ' ') AS multiword
FROM dict_legal_terms
GROUP BY term_type, verified
ORDER BY term_type, verified DESC;
```

### Track A morpheme.py 자동 로드 검증

```python
engine = MorphemeEngine(supabase=get_supabase())
assert engine.user_dict_size == 1725  # v1.2 EOD 기준
```

## 5. 적재 단계별 이력

| 버전 | 적재 내용 | verified=true 누적 | commit |
|---|---|---|---|
| v1 | LAW 본법 145 + AGENCY 30 + TECH 15 = 190 | 186 | 사용자가 SQL 실행 (본 인스턴스) |
| v1.1 | + ENFORCEMENT_DECREE 139 + ENFORCEMENT_RULE 139 = +278 | 464 | 사용자가 SQL 실행 (본 인스턴스) |
| v1.2 | + GENERIC 14,474 (verified=true 1,261) | **1,725** | 사용자 Railway 실행 — `extract_generic_candidates.py` |

## 6. 사용자 결정 이력 (재진입 시 컨텍스트 보전 필수)

| # | 결정 사항 | 결과 |
|---|---|---|
| 1 | 소스: `semantic_clause` vs `law_article_part` | `law_article_part.part_text` (Stage 0 원본, 폐기 영향 X) |
| 2 | 부서명/법령명 단일 NNP vs 분해 등록 | 단일 NNP (DDL term_type enum이 사실상 강제) |
| 3 | 합성어 / cross_reference 등록 | 미등록 (Kiwi/Track E 위임) |
| 4 | "사람 검증 불가, Cursor 등 위탁" | §2.1 환기 → ground truth는 검증 불요 → verified=true 직접 등록 (사용자 채택) |
| 5 | LAW_NAME 등록 범위 | A안 (LAW 본법) → B안 (+ ENFORCEMENT_DECREE/RULE) — 시점 단계 격상 |
| 6 | QUARANTINE 4건 (산업통상부, 방송미디어통신위원회, 중앙소방학교, 한국전통문화대학교) | verified=false + notes 보존, 향후 결정 위임 |
| 7 | Week 3 범위 (A/B/C) | B안 (GENERIC + LAW_NAME 확장) |
| 8 | GENERIC 코드 작성 (A/B) | A안 (Track C 직접 작성, Cursor 위임 회피) |
| 9 | dry-run 결과 후 임계 재조정 vs 즉시 INSERT | 즉시 INSERT (사전 합의 룰 신뢰성 ↑) |

## 7. 펜딩 사항 (다음 트리거 가능성)

### 7.1 Track A 정규식 컴파일 비용 측정 결과 대기

- Track A가 옵션 A/B/C를 검토 중이라고 회신했으나 본 작업창에 명세 미공유
- verified=true 464 → 1,725 (3.7배) 증가에 따른 morpheme.py 인스턴스 생성 시간 영향
- 측정 결과 + 옵션 명세 수령 시 Track C 권고 작성 진입

### 7.2 v1.3 설계 시안 (Track E 시작 시점 적용 후보)

- 위치: `docs/extraction/v3/track_c/v1_3_design_proposal.md`
- 수정 4가지: 이중 필터 제거 / 다중 사유 기록 / TH_DF_LOW 완화 (0.001 → 0.0001) / 평가 순서 재조정
- 적용 조건: Track E 시작 후 Stage 2/3 룰이 dict 커버리지 부족 도출 시
- v1.2 결과 품질은 양호 (Top 30 sanity 93%) → 즉시 재적재 불요

### 7.3 QUARANTINE 4건 결정

- `산업통상부` — 정식 "산업통상자원부" 의심 (Track B data quality 인계 가능)
- `방송미디어통신위원회` — 정식 "방송통신위원회" 의심
- `중앙소방학교` / `한국전통문화대학교` — 학교가 ministry 적합성 검토
- 결정 시 verified=true UPDATE 또는 정정 후 재INSERT (정정 시 절대원칙 2 약한 위배 검토 필요)

### 7.4 (선택) v1.1 464건 frequency/score 일괄 UPDATE

- 현재 v1.1 ground truth 어휘 (LAW_NAME 423 + AGENCY_NAME 26 + TECH_TERM 15)는 frequency=0, score=0
- GENERIC과 동일 파이프라인으로 측정 가능
- 우선순위 낮음 (Stage 2/3 룰이 frequency/score 직접 사용 시 필요)

### 7.5 KSIC / Process 카테고리 추가

- v3.0 목표 외 추가 사양
- Track E 시작 시 필요 여부 재판단

## 8. 트랙간 영향 / 의존 관계

| 트랙 | 본 트랙 영향 | 본 트랙 의존 |
|---|---|---|
| Track A (Kiwi 형태소) | dict_legal_terms 변경 → 다음 morpheme 인스턴스 자동 반영 | morpheme.py 인터페이스 사용 |
| Track B (법령 수집) | 영향 X (SELECT만) | law_master ground truth 사용 |
| Track D (Stage 1 룰) | 미시작 | 영향 X |
| Track E (Stage 2/3 룰) | dict_legal_terms 직접 의존 (rule_pos_to_role) | 시작 후 dict 커버리지 피드백 가능 |

### 트랙간 통보 양식

`docs/extraction/v3/log/Track_C_20260509.md` 끝부분에 Track A 통보 양식 보존. 동일 형식으로 미래 통보 작성.

## 9. 산출물 인덱스 (taiengineering/tai-admin, main branch)

| 파일 | 용도 |
|---|---|
| `docs/extraction/v3/log/Track_C_20260509.md` | 일일 로그 (3차 갱신, v1.2 종결 보고) |
| `docs/extraction/v3/track_c/baseline_surface_top200.md` | 초기 surface 빈도 분석 (Kiwi 도입 전 baseline) |
| `docs/extraction/v3/track_c/frequency_analysis_v0.1.sql` | 빈도 분석 SQL 초안 |
| `docs/extraction/v3/track_c/ground_truth_candidates_v0.1.md` | law_master ground truth 발굴 명세 |
| `docs/extraction/v3/track_c/seed_v1_result.md` | v1 시드 INSERT 결과 명세 |
| `docs/extraction/v3/track_c/v1_3_design_proposal.md` | v1.3 설계 시안 (Track A 피드백 반영) |
| `docs/extraction/v3/handoff/Track_C_handoff_20260509_EOD.md` | **본 문서** |

### tai-api (dev branch)
| 파일 | 용도 |
|---|---|
| `scripts/v3/extract_generic_candidates.py` | GENERIC 추출 + 룰베이스 자동 검증 (commit `fc5a7916`) |

## 10. 새 인스턴스 진입 시 권고 행동

### 즉시 (모든 트리거 공통)
1. 본 문서 (`Track_C_handoff_20260509_EOD.md`) 정독
2. `docs/extraction/v3/MASTER_HANDOFF.md` v1.0 절대원칙 §2 재확인
3. SQL 1건으로 DB 사실 재확인 (§4 검증 SQL)
4. `docs/extraction/v3/log/Track_C_*.md` 최신 일일 로그 확인 (펜딩 사항 갱신 여부)

### 트리거별 분기

**Track A 정규식 컴파일 측정 결과 수령**:
- 옵션 명세 분석 → Track C 권고 작성 → push
- 본 작업창 측정 권한 X 명시
- v1.3 적용 영향 분석 (다단어 344건 → 새 다단어 추가 시 비용)

**사용자 새 결정 (예: QUARANTINE 결정, KSIC 추가, v1.1 freq/score UPDATE)**:
- 절대원칙 5개 자체 점검부터
- ground truth 우선 활용 (검증 부담 0)
- dry-run → 결과 확인 → 실 적재 순서

**Track E 시작 통보 + dict 커버리지 부족 피드백**:
- 부족 어휘 카테고리 분석 → v1.3 설계 시안 적용 여부 판단
- 새 raw 추출 vs verified=false 13,213 중 재평가 결정
- 새 카테고리 (KSIC, Process 등) 도입 결정

**기타 (Track B/D 인계)**:
- 영향 분석 → 본 작업창 작업 vs 다른 트랙 위임 결정
- 본 트랙 본분 (도메인 사전) 외 작업 거부 + 적정 트랙 안내

## 11. 사후 학습 자산 (실수 반복 방지)

1. **이중 필터는 룰 가시성을 죽인다** — process_chunk 사전 필터 + build_insert_rows 평가 룰 중복으로 4 룰 dead. 분기 시점은 한 곳으로.
2. **fail-fast는 운영용, 분석은 다중 기록** — 룰 작동 빈도 측정에는 모든 룰 평가가 필요.
3. **임계값은 도메인 데이터로 사전 계산** — `TH_DF_LOW = 0.001`이 144 articles임을 설계 시점에 명시했어야 함.
4. **다른 트랙 피드백을 추상적 수정보다 우선** — Track A의 구체 수치 분석이 v1.3 설계의 출발점.
5. **사용자 "검증 위탁" = §2.1 위배 신호** — Cursor/LLM에 의미판단 위탁 요청 시 ground truth 검증 불요 솔루션으로 우회.
6. **트랙간 통보 누락 주의** — 결정 시점마다 영향 받는 다른 트랙 동시 통보. fact-check 인식 차이 방지.

## 12. 마일스톤 추월 분석

| MASTER_HANDOFF 명세 | 계획 | 실적 | 추월 사유 |
|---|---|---|---|
| Week 2: 빈도 분석 + 후보 리스트 공유 | End Week 2 | Day 1 | ground truth (`law_master`) 발굴 → 빈도 분석 우회 |
| Week 3: 사용자 검증 Top 500 | End Week 3 | Day 1 (대체) | 사용자 검증 → 룰베이스 자동 검증 (1,261 통과) |
| Week 4: dict_legal_terms v1 등록 | End Week 4 (500-1,000) | Day 1 (1,725) | ground truth 직접 등록 + GENERIC 자동 검증 |

추월의 핵심: **사용자 검증 단계 자체를 ground truth + 룰베이스 자동 검증으로 대체**. 사람 의존 0, LLM 의존 0, 절대원칙 100% 부합.

## 13. 본 트랙 종료 시점 자체 평가

- **본분 완수**: dict_legal_terms v1 적재 완료 (verified=true 1,725)
- **품질**: Top 30 sanity 93% (28/30 도메인 적합)
- **데이터 보전**: verified=false 13,217건 보전 (절대원칙 3 부합)
- **추적 가능성**: 모든 row에 source 명시
- **재현 가능성**: dry-run 예측 = 실 결과 100% 일치
- **트랙 협업**: Track A 인터페이스 검증 통과 (자동 로드 + 다단어 토큰화 100%)

다음 트리거 대기 모드로 전환.

---

**핸드오프 작성 완료. 차기 인스턴스 진입 즉시 §10 행동 가이드 적용.**
