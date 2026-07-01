# THRESHOLD 연결 집행 — 발견 문제 기록

작성: 2026-07-01 (17차 연속) | 상위: `docs/2026-06-22_TAI_Safe_법령의무도출_설계문서_전체.md` 6장 THRESHOLD 갱신
성격: 별표 THRESHOLD → obligation 연결을 실제 집행하며 직독으로 확인된 문제. 향후 작업 근거로 명기.
DB: Supabase `vwlahtguyggrhvslabax` (서울). 검증=글읽기 직독, 건수/목업 판단 금지.

---

## 집행 개요
- 목적: 별표 THRESHOLD 자산(`appendix_runtime_metadata`)을 소비자 입력값 기반 의무로 연결(매핑).
- 원칙(대표 지시): **확실=매핑(CONFIRMED), 애매=보류(PENDING), 완전히 아닌 것=드롭(미적재).**
- Boundary Check: Applicability 내부=YES / Boundary=NO / Contract=NO / Breaking=NO → 일반작업.

---

## 문제 1 — 별표 THRESHOLD의 `law_id`가 전량 NULL (연결 키 결측)
- `appendix_runtime_metadata`(metadata_type='THRESHOLD' 24,626건)의 `law_id` 컬럼이 **전부 NULL**.
- 별표는 `law_name`(텍스트) + `source_article_no`(정수)만 보유 → 조문 테이블(`law_article`)과 잇는 FK(law_id) 없음.
- **영향**: 별표 → 조문 → semantic_clause 연결을 law_id 조인으로 불가. law_name 텍스트 매칭 우회 필요.
- **우회 성립**: `law_name → law_master.law_name` 매칭 성공.
  - 산업안전보건기준에 관한 규칙 → `0f62d48d-7061-423a-a87f-1f05b7a4b5f2` (별표 THRESHOLD 660)
  - 산업안전보건법 시행규칙 → `d2f4e80a-370a-41bc-bd04-4b71e5a1db75` (321)
  - 산업안전보건법 시행령 → `5562eb48-01d9-4d53-9a8a-1018e79b34c0` (176)
  - → law_master.id 획득 후 `law_article(law_id, article_no)` 조인 성립.
- **근본 해결(후속)**: 별표 수집 시 law_id 채우기, 또는 law_name→law_master 정규화 매핑 상시 유지.

## 문제 2 — metadata_type='THRESHOLD' 24,626건 = "수치 포함 조항" 전체 (의무 임계 아님)
- 직독 결과 대다수가 **설비·설계 규격(이행 기준 how)**이지, 소비자 입력으로 발생하는 의무 조건이 아님.
  - 예: "안전난간 90센티미터 이상", "배기관 53밀리미터 이하", "난간 2단 이상", "안전거리(별표8)", "특수화학설비 기준량(별표9)".
- **영향**: 24,626건 그대로 obligation 발화 시 규격 수치가 의무처럼 대량 오발화 → C급(무관) 폭증.
- **선별 기준**: 조문(semantic_clause)이 `content_type='OBLIGATION'` & `executor LIKE '%사업주%'`인 것만 의무 후보.
  - 산안 3법 "명" 임계 기준 3분류 실측: **확실(조문 의무 O) 27 / 애매(조문 있으나 의무 아님) 89 / 드롭(조문 매칭 안 됨) 0.**

## 문제 3 — "N명 이상"이라도 상시근로자 임계 ≠ 작업 배치 인원 (자동 구분 불가)
- 조문 의무가 있어도, 그 "N명"이 **사업장 상시근로자 수**인지 **작업 현장 배치 인원**인지 데이터만으로 구분 불가.
- 상시근로자 임계 (의무 O — CONFIRMED 후보):
  - 제19조 경보설비 50명 이상 / 시행령 제24조 안전보건관리담당자 20명 이상·50명 미만 / 시행령 제16조 안전관리자 300명 / 시행령 제29조 50명 이상 / 제662조 근골격계 예방프로그램 5명·10명 이상.
- 작업 배치 인원 (의무 X — PENDING 유지):
  - 제40조 신호 2명 이상 / 제222조 교시 2명 이상 / 제547조 잠수 2명 이상.
- **영향**: "확실"로 자동 분류돼도 작업방식 규정이 섞임 → 조문 원문 판독(사람/GPT) 후 최종 확정 필요.

---

## 집행 결과 (1차)
- 산안 3법 별표 THRESHOLD 중 조문 의무 매칭분을 `condition_mapping_candidate`에 **17건 PENDING 적재**.
  - condition_code 접두: `THRESHOLD:APPENDIX:` (+ 조문번호 + 연산자코드 + 임계값 + clause앞4자)
  - condition_source = `MANUAL` (제약: CONDITION_TEXT/ACTION_TEXT/MANUAL 중)
  - input_field = `worker_count`, input_operator = 별표 operator 매핑(이상→>= / 초과→> / 이하→<= / 미만→<)
  - review_status = `PENDING` (제약: CONFIRMED/HARVESTED/PENDING/REJECTED 중)
  - confidence = `0.60`, applicable_sectors = {INDUSTRIAL, CONSTRUCTION, BUILDING}
  - condition_text_raw = `[별표THRESHOLD] {법령} 제{조}조 · {임계원문}`
  - 멱등성: `ON CONFLICT DO NOTHING` + 유니크 `(semantic_clause_id, input_field, input_value, applicable_sectors)`, `condition_code`.
- **전부 PENDING(보류). CONFIRMED 승격 미실시** — 문제 3 판독 후 승격 예정.

### 적재 17건 (요약)
| 근거 | 임계 | 판정후보 |
|---|---|---|
| 제19조 경보설비 | worker_count >= 50 | CONFIRMED 후보 |
| 시행령 제24조 안전보건관리담당자 | >= 20 / < 50 / >= 1 | CONFIRMED 후보 (범위조건) |
| 시행령 제16조 안전관리자 | >= 300 | CONFIRMED 후보 |
| 시행령 제29조 | >= 50 | CONFIRMED 후보 |
| 제662조 근골격계 | >= 5 / >= 10 | CONFIRMED 후보 |
| 제40조 신호 / 제222조 교시 / 제547조 잠수 | >= 2 (일부 > 2) | PENDING 유지 (작업배치) |

---

## 미해결 · 후속
1. **CONFIRMED 승격 판정**: 상시근로자 임계 vs 작업배치 구분 — 조문 원문 판독(사람/GPT) 후 확정.
2. **범위 확대**: 산안 3법 외 별표 THRESHOLD(건축법·근로기준법·건설기계 안전기준 등) 처리 범위 결정.
3. **운영 반영 확인**: cmc 적재분이 운영 `obligation_instance` 발화로 이어지는지 = Applicability Engine(GPT 소관) 연결 여부. **주의: 6/25 감사에서 GPT Compiler는 cmc를 미사용으로 확인됨** → cmc 경로가 실제 운영 결과에 반영되는지 재확인 필요(반영 안 되면 별도 연결 경로 필요).
4. **law_id 결측 근본 해결**: 별표 수집 파이프라인에 law_id 채움 추가.

---

*17차 연속 · 2026-07-01 · TAI Engineering*
