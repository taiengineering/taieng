# Track C — v1 시드 INSERT 결과 명세

**실행일**: 2026-05-09  
**대상 테이블**: `dict_legal_terms`  
**소스**: `law_master` (752 active) + 화이트리스트 15  
**결과**: 190건 등록 (verified=TRUE 186 / verified=FALSE 4 QUARANTINE)

---

## 실행 원칙 자체 점검

사용자 "사람이 검증할 수 없음, Cursor 등에 위탁" 요청 → §2.1 "LLM 절대 사용 금지" 환기 → ground truth 검증 불요 논리 확립 → 사용자 채택

| 절대원칙 | 계획 | 실행 결과 |
|---|---|---|
| ① LLM X | SQL + ground truth + 화이트리스트 | ✅ LLM 개입 0 |
| ② 법령 보전 | law_master 직접 인용 | ✅ 변형 0 |
| ③ 놓치는 것 = 리스크 | QUARANTINE 보존 | ✅ 4건 verified=FALSE |
| ④ 100% 매핑 | source 컬럼 출처 추적 | ✅ 모든 row에 source 명시 |
| ⑤ 오염 = 폐기 | ON CONFLICT 처리 + dry-run 교차 | ✅ 예측 190건 = 실제 190건 |

---

## INSERT 결과 상세

### A. AGENCY_NAME — 30건 (26 verified=TRUE / 4 QUARANTINE)

| # | term | verified | notes |
|---|---|---|---|
| 1 | 기후에너지환경부 | TRUE | ministry_distinct |
| 2 | 국토교통부 | TRUE | ministry_distinct |
| 3 | 소방청 | TRUE | ministry_distinct |
| 4 | 국가기술표준원 | TRUE | ministry_distinct |
| 5 | 보건복지부 | TRUE | ministry_distinct |
| 6 | 행정안전부 | TRUE | ministry_distinct |
| 7 | 고용노동부 | TRUE | ministry_distinct |
| 8–26 | … | TRUE | ministry_distinct |
| Q1 | 산업통상부 | **FALSE** | QUARANTINE: data_quality_review (정식 "산업통상자원부" 의심) |
| Q2 | 방송미디어통신위원회 | **FALSE** | QUARANTINE: data_quality_review (정식 "방송통신위원회" 의심) |
| Q3 | 중앙소방학교 | **FALSE** | QUARANTINE: agency_category (학교 → ministry?) |
| Q4 | 한국전통문화대학교 | **FALSE** | QUARANTINE: agency_category (대학교 → ministry?) |

### B. LAW_NAME — 145건 (정식 123 + 약칭 22)

**정식 명칭 (LAW 본법, 123건)**
- 단일어 (공백 없음): 53건 — 예: `건축법`, `근로기준법`, `노인복지법`
- 다단어 (공백 포함): **70건** — 예: `고압가스 안전관리법`, `건축물의 분양에 관한 법률`
- 최단 3자 — `건축법` 계열
- 최장 49자 — `고용보험ㅎ산업재해보상보험의 보험관계 성립신고 등의 촉진을 위한 특별조치법`

**약칭 (22건)**
정식 명칭 중 18%만 정부 약칭 보유. 모두 단일어 (공백 0).
예: `고압가스법`, `탄소중립기본법`, `노후계획도시정비법`

### C. TECH_TERM — 15건 (화이트리스트)

**legal_form (13)**
법률 / 법 / 시행령 / 시행규칙 / 대통령령 / 총리령 / 부령 / 고시 / 훈령 / 예규 / 공고 / 규칙 / 규정

**attachment (2)**
별표 / 별지

---

## 후속 작업

### Track A 테스트 권장
```python
from engine.morpheme import MorphemeEngine
from db.supabase_client import get_supabase

engine = MorphemeEngine(supabase=get_supabase())
# 기대: "MorphemeEngine 자동 사전 로드: 186개" 로그
assert engine.user_dict_size == 186

# 다단어 법령명 NNP 토큰화 확인
tokens, _ = engine.analyze("고압가스 안전관리법 제10조에 따라 등록한다.")
# 기대: 첫 토큰이 "고압가스 안전관리법" / "NNP"
```

### morpheme.py 호출 일괄 업데이트 (선택, 권장)
```sql
-- 추후 morpheme.py 호출 후 계산된 결과로 일괄 UPDATE
UPDATE dict_legal_terms
SET frequency = X, score = Y, updated_at = now()
WHERE term = ?;
```

### GENERIC 추출 (Week 3 예정)
- `tai-api/scripts/v3/extract_generic_candidates.py` (Cursor 위임 가능 — 코드 작성만)
- 입력: law_article_part.part_text 전체 (143,549)
- 추출: NNG/NNP/NF 명사, 이미 dict_legal_terms에 있는 term 제외
- 룰베이스 자동 검증 → verified=TRUE 또는 verified=FALSE 자동 표시
