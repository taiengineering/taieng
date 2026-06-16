# 세션 핸드오프 — 법령엔진 15E

**작성일**: 2026-06-16  
**다음 세션 시작점**: Domain Rule WO 설계 또는 D-004B-PILOT 확장

---

## ★ 이 문서 하나만 읽으면 됩니다

현행 기준: `docs/2026-06-11_LEGAL_ENGINE_V4_LAYER_REDESIGN.md` (v2.1)  
구현 WO: `docs/2026-06-16_WO_D_PIPELINE_IMPL.md`  
Actor WO: `docs/2026-06-16_WO_LEG_COMPILER_003.md`

---

## 오늘 완료한 것

### WO-D-001~007 ✅
### WO-APPENDIX-COLLECT-001 ✅
### WO-LEG-Compiler-003 Actor Resolution ✅
- `actor_resolution_pattern` 81개
- `semantic_clause_actor_resolution` 24,127건

### K-01~05 측정 ✅

| 구분 | 결과 |
|---|---|
| total | 260건 |
| actor_overlay_coverage | 117건 (45%) |
| AUTHORITY | 69건 → 제거 후보 |
| BUSINESS | 34건 |
| FRAGMENT | 11건 |
| ASSOCIATION | 3건 |
| UNKNOWN | 143건 |

**K-05 글읽기 결론:**
- BUSINESS 34건 중 실제 적용 가능: ~9건 (산안법계)
- Domain 오염: ~25건 (CONSTRUCTOR/MANAGER 계열)
- → Actor 문제 + Domain 문제 둘 다 존재 확인

### WO-D-004B-PILOT-SAFETY-MANAGER ✅

엔드포인트: `GET /pilot/safety-manager/evaluate?facility_id=...`

화성 제2공장 (C28, 280명) 실측:
```json
{
  "verdict": "REQUIRED",
  "required_count": 1,
  "matched_conditions": ["제1호부터 제27호까지 외의 사업 50명 이상 999명 미만 안전관리자 1명"]
}
```

---

## 다음 세션 해야 할 것

### 우선순위 1 — Domain Rule WO 설계

BUSINESS actor인데 오염인 것들:
- `ACTOR:CONSTRUCTOR` → INDUSTRIAL sector 매핑 금지
  - 소방시설공사업법, 건설산업기본법, 정보통신공사업법, 화재예방법 건설현장
- `ACTOR:MANAGER` (건물/주택) → INDUSTRIAL sector 매핑 금지
  - 공동주택관리법, 건축물관리법, 소방시설 자체점검, 초고층건물법

설계 방향: `law_sector_mapping`에 CONSTRUCTOR 개념 추가 기준 필요 (GPT 영역)

### 우선순위 2 — D-004B-PILOT 확장

현재 파일럿 한계:
- `appendix_condition` 7건만 (별표3 일부)
- KSIC 텍스트 매칭 (코드 매핑 미완)
- 안전관리자만 (보건관리자 미포함)

다음 확장 후보:
- 보건관리자 선임 기준 (별표5) 추가
- KSIC 코드 직접 매핑

---

## 커밋 이력 (15D~15E)

| SHA | 내용 |
|---|---|
| 48f082f | WO-LEG-Compiler-003 초기본 |
| b5526e5 | WO 위치 명확화 + K-01~05 추가 |
| 30a005e | refinery_api Actor Overlay 1차 연결 |
| 6c74f43 | Actor 연결 경로 수정 (draft_id→article_id) |
| 9576d19 | actor_map 로직 개선 |
| 0dd8845 | chunked 방식으로 변경 |
| 35b8775 | D-004B-PILOT 구현 |
| c16b9d9 | registry 등록 |

## DB 생성 완료

- `actor_resolution_pattern` (81건)
- `semantic_clause_actor_resolution` (24,127건)
- `law_appendix` + `appendix_condition` (7건)

---

## 절대 금지 (유효)

```
GPT 전속 테이블 수정 금지:
  constraint_node, rule_candidate, executable_draft, draft_slot
  semantic_clause_actor_resolution에 DROP 컬럼 추가 금지

삭제 금지:
  evaluate_single_factory
  evaluate_draft_for_facility
  semantic_clause_fix 직접 수정

D-004B 전체 확대 독단 착수 금지 (사장님 승인 필수)
SPECIAL_FACILITY 섹터 수정 금지 (의도적 휴면)
```

## 테스트 사업장

`facility_id`: `e9c56af6-5de7-487d-bd2e-0d452291a562`  
화성 제2공장, INDUSTRIAL, C28 전기장비 제조업, 280명
