# 기획문서 (Planning Record) — MASTER-WO-TAI-SEARCH-DICT-001

> 이 파일은 Owner(심태왕)가 제공한 standalone Work Order 원문을 `feature/search-dictionary-v1`
> workstream의 **기획 기록(planning record)** 으로 저장한 것이다. 아래 "커밋 메모"는 Claude가
> 착수 시점에 남긴 provenance/anchor/경로 조정 근거이며, 그 이후 본문은 WO 원문이다.

---

## 커밋 메모 (Claude, 착수 기록)

```text
MASTER WO      = MASTER-WO-TAI-SEARCH-DICT-001
OBJECT         = OBJ-SEARCH-DICT
SOURCE         = Owner(심태왕) 제공 standalone WO
REGISTERED_AT  = 2026-09-16
REGISTERED_BY  = Claude (기획창)

DOC REPO       = taiengineering/taieng   (문서 전용 저장소)
DOC BRANCH     = feature/search-dictionary-v1
DOC MAIN ANCHOR= 5d3be9b52232395c39ea0538e6b459733846096f  (taieng main HEAD, 2026-09-06)

CODE REPO      = taiengineering/tai-api  (검색 서비스/컴파일러/테스트 대상, 향후 구현)
CODE MAIN ANCHOR = db024b57d9b81802f5dd18b18c69872735e3c3da  (tai-api main HEAD, 2026-09-14)
```

### 경로 조정 근거 (governance reconciliation)

WO §97은 산출물 폴더를 `docs/knowledge/search-dict/`로 권고하나, TAI 확정 거버넌스는
"모든 문서는 `taiengineering/taieng/docs/`에만 둔다 (tai-api/docs·tai-admin/docs 금지)"이다.
WO §97 후단 ("실제 repo 규칙이 다르면 동일 의미의 existing convention을 따른다")에 근거하여
두 규칙을 아래와 같이 조정한다.

```text
문서(Constitution/Contract/Census/Master/Benchmark/Audit/Handoff 등)
  → taieng/docs/knowledge/search-dict/  에 배치 (governance + WO 폴더명 동시 충족)

검색 코드(search service / compiler / tests / migration)
  → tai-api  (WO §58, RISK-04 본선과 동일 저장소, 별도 branch/PR)
```

따라서 이 workstream은 문서 PR(taieng)과 코드 PR(tai-api)로 분리되며, 두 PR 모두
독립 branch에서 진행하고 PR #366(RISK-04) branch에서 분기하지 않는다.

### 산출물 파일명 조정

WO에 명시된 구조화 산출물(SEARCH_CONSTITUTION_v1.md 등)은 WO 본문·테스트·컴파일러가
해당 경로를 계약으로 참조하므로 **WO 명시 파일명을 그대로 유지**한다.
일반 문서 명명 규칙(`{YYYY-MM-DD}_{title}.md`)은 이 기획 기록 파일에만 적용한다.

### 실행 환경 경계 (정직 고지)

현재 대화 세션의 로컬 실행 환경은 네트워크가 비활성화되어 있어 `kiwipiepy` 설치·형태소
분석 실행·pytest 실행·컴파일러 결정성 SHA 산출·벤치마크 latency 측정을 **이 세션에서
직접 검증 실행할 수 없다.** 따라서:

```text
이 세션에서 완결 가능 : Repo/Source Census, Constitution, Contract, 스키마·아키텍처 설계 문서,
                        read-only DB 조사 기반 term 후보 수집
실행 환경 필요(Cursor/Claude Code) : Kiwi baseline/after, compiler 실행·결정성 SHA,
                        검색 서비스 코드, pytest/regression, 벤치마크 recall·latency 실측
```

검증되지 않은 수치(benchmark/latency/determinism)를 임의로 채우지 않는다
(engineering-principle: "fabricating completion = integrity breach").
최종 상태는 실측 phase 완료 전까지 READY_FOR_OWNER_APPROVAL로 선언하지 않는다.

---

## WO 원문 (verbatim)

원본 Work Order 전문은 Owner가 제공한 `MASTER-WO-TAI-SEARCH-DICT-001` 문서와 동일하며,
본 workstream의 모든 phase·불변조건·exit criteria·금지사항의 기준 계약이다.
대표 불변조건 요약(전문은 Owner 원본 참조):

```text
SEARCH TERM            ≠ CANONICAL ID
SEARCH NORMALIZATION   ≠ SEMANTIC EQUIVALENCE
SAME NAME              ≠ SAME CONCEPT
MORPHOLOGICAL/TRIGRAM/LLM SIMILARITY ≠ CANONICAL MERGE

HARD STOP: RISK-04 frozen artifact 수정 / canonical 의미 변경 / similarity 기반 canonical
           자동 merge / production DB write / production migration / 법령 applicability
           판단 / legal obligation 판단 / credential 부재 / 사용권 불허 데이터 전체 복제

MERGE = OWNER DECISION (Claude 자동 merge 금지)
```

이 요약은 편의용이며, 판정 기준의 정본은 Owner 제공 WO 원문 전체다.
