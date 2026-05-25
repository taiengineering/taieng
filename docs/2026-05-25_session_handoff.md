# 세션 핸드오프 2026-05-25

## 완료 작업

### 1. 인프라 복구
- GitHub↔Railway 연결 끊김 발견 → `railway up` CLI 수동 배포 체계 확립
- `router_registry` v1.1.0: `total` 필드 + per-module 로깅 추가
- TBM route 미로드 해결: `document_engine` 7/7 정상 로드
- documents INSERT 실증 완료
- diagnosis_report.py 코드 손상 없음 확인

### 2. Runtime 엔진 전환 (Phase 1~3)
- Phase 1: 흐름 분석 완료 (Cursor) → `engine_flow_map.md`
- Phase 2: Legacy/Runtime/Mixed 분류 완료
- Phase 3: `/diagnosis/run` runtime compiler 전환
  - `services/diagnosis_runtime_step1.py` 신규
  - `routers/diagnosis_result_web.py` v1.1.0
  - `diagnosis_result_web`, `diagnosis_runtime_projection` registry 등록
  - diagnosis 그룹: 11 → 13 로드
  - engine_version: `v3.0-runtime-compiler` 고정
  - Legacy 경로 `# LEGACY - ISOLATED` 주석 처리

### 3. 결과 정제 파이프라인 연결
- `diagnosis_transform.py`의 BE-08 정제 함수 import 연결
- FAMILY→한글 변환 (`CATEGORY_MAP` 경유)
- `law_article + rule_kind` 기준 중복 제거
- `obligation_counts`: 한글 카테고리 (서류, 선임, 신고)

### 4. WHO/WHAT/WHEN 슬롯 데이터 연결
- `rule_candidate_slot` (146,595건) → 진단 결과 enrichment
- DB JOIN 경로: `law_master → law_version → law_article → rule_candidate → rule_candidate_slot`
- `law_article` 파싱: 정규식 `r'제(\d+)조'`
- 프로덕션 검증: 15건 중 13건 WHO/WHAT 채움
- 산업안전보건법 제29조: who=`고용노동부장관·사업주`, what=`안전보건교육·할 수 있다`

## 프로덕션 상태

| 항목 | 상태 |
|------|------|
| API version | 6.0.1 |
| 전체 모듈 | 186 loaded, 1 failed (external) |
| diagnosis 그룹 | 13/13 ok |
| document_engine | 7/7 ok |
| 배포 방식 | `railway up` (GitHub 자동배포 미복구) |

## 미해결 이슈

### P0 — 다음 세션
1. **summary↔obligation_counts 수치 불일치**: total 113 vs 서류10+선임2+신고3=15
2. **rules_table 2건 WHO/WHAT 미채움**: 해당 조문의 `rule_candidate`가 없거나 슬롯 누락
3. **when 필드 대부분 비어있음**: DEADLINE/FREQUENCY 슬롯 커버리지 확인 필요
4. **무료진단 결과 페이지**: `free-diagnosis-result.html` 실제 렌더링 검증
5. **유료진단 결과 페이지**: 토큰 파라미터 에러 수정 필요

### P1 — 운영 검증
6. **E2E 고객 흐름**: 로그인→현장→작업자→점검→PDF (worker-list 로딩 이슈 미해결)
7. **Railway↔GitHub 자동배포 복구**: `github.com/settings/installations` Railway 앱 재인증
8. **TBM create/sign 페이지**: stub 상태 (P1)

### P2
9. **점검항목 매핑**: runtime_checklist_item → inspection_set_items 연결
10. **모바일 UX 검증**

## 핵심 발견

### master_rule_v2 비어있음
- 메모리의 58,495건은 과거 데이터
- 현재 runtime 엔진은 `rule_candidate`(34,456) + `rule_candidate_slot`(146,595) 체계 사용
- `master_rule_v2` 관련 테이블 전부 0건

### 데이터 경로
```
law_master → law_version → law_article(35,412)
  → rule_candidate(34,456)
    → rule_candidate_slot(146,595): ACTOR/OBLIGATION/ACTION/DEADLINE/FREQUENCY
    → rule_candidate_relation(59,116)
```

## 커밋 이력 (tai-api main)
- `7a998b7` router_registry v1.1.0
- `b1b4292` main.py v6.0.1
- Phase 3 runtime 전환 (Cursor 커밋들)
- `74f05e7` slot enrichment law_master JOIN 수정
