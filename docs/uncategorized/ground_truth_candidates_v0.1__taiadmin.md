# Track C — ground truth 후보 명세 + 검증 요청 (v0.1)

**작성일**: 2026-05-09  
**소스**: `law_master` 테이블 (752 전체 active)  
**용도**: Track A `morpheme.py` 대기 없이 LAW_NAME + AGENCY_NAME + TECH_TERM 즉시 산출 가능

---

## A. AGENCY_NAME 후보 — 30개 (전체 표시, 검증 요청)

콤마 구분 다중 ministry_name은 분리 후 dedupe.

| 등록 결정 | 부처명 | law_count | pos_tag | 비고 |
|---|---|---|---|---|
| ? | 기후에너지환경부 | 108 | NNP | 환경부 신 명칭 |
| ? | 국토교통부 | 107 | NNP | |
| ? | 소방청 | 82 | NNP | |
| ? | 국가기술표준원 | 81 | NNP | |
| ⚠️ | 산업통상부 | 67 | NNP | **정식 명칭 "산업통상자원부" 아닌가? Track B 확인** |
| ? | 보건복지부 | 64 | NNP | |
| ? | 행정안전부 | 50 | NNP | |
| ? | 고용노동부 | 42 | NNP | |
| ? | 국립소방연구원 | 41 | NNP | |
| ? | 식품의약품안전처 | 25 | NNP | |
| ? | 화학물질안전원 | 24 | NNP | |
| ? | 국립환경과학원 | 14 | NNP | |
| ? | 교육부 | 13 | NNP | |
| ? | 해양수산부 | 11 | NNP | |
| ? | 과학기술정보통신부 | 10 | NNP | |
| ? | 원자력안전위원회 | 6 | NNP | |
| ? | 국방부 | 5 | NNP | |
| ? | 산림청 | 4 | NNP | |
| ? | 질병관리청 | 3 | NNP | |
| ? | 대법원 | 3 | NNP | 입법 권한 보유 |
| ? | 문화체육관광부 | 3 | NNP | |
| ? | 중소벤처기업부 | 2 | NNP | |
| ? | 방송미디어통신위원회 | 2 | NNP | 정식 명칭 확인 필요 (방송통신위원회?) |
| ? | 법무부 | 1 | NNP | |
| ? | 국립수산과학원 | 1 | NNP | |
| ? | 조달청 | 1 | NNP | |
| ? | 국립전파연구원 | 1 | NNP | |
| ? | 경찰청 | 1 | NNP | |
| ⚠️ | 중앙소방학교 | 1 | NNP | **학교가 ministry? 카테고리 검토** |
| ⚠️ | 한국전통문화대학교 | 1 | NNP | **대학교가 ministry? 카테고리 검토** |

**검증 요청**: 30건 일괄 승인 가능한지, ⚠️ 표시 3건 개별 결정 요함

---

## B. LAW_NAME 후보 — LAW 본법 123 + 약칭 (권고 범위)

### 등록 대상 (권고)
- LAW 123건 전수 (정식 명칭, law_name)
- 약칭 (law_name_short, 빈 문자열 제외) — 예상 ~30건
- **총 예상 산출: 약 150 LAW_NAME**

### Sample (LAW 본법 가나다순 첫 30건 — 파턴 검증용)

| law_name | law_name_short | 공백 존재 | 소관 |
|---|---|---|---|
| 건설기계관리법 | — | X | 국토교통부 |
| 건설기술 진흥법 | — | ✓ | 국토교통부 |
| 건설산업기본법 | — | X | 국토교통부 |
| 건설폐기물의 재활용촉진에 관한 법률 | — | ✓ | 국토교통부,기후에너지환경부 |
| 건축기본법 | — | X | 국토교통부 |
| 건축물관리법 | — | X | 국토교통부 |
| 건축물의 분양에 관한 법률 | — | ✓ | 국토교통부 |
| 건축법 | — | X | 국토교통부 |
| 고압가스 안전관리법 | 고압가스법 | ✓ | 산업통상부 |
| 고용보험 및 산업재해보상보험의 보험료징수 등에 관한 법률 | 고용산재보험료징수법 | ✓ | 고용노동부 |
| 고용보험ㅎ산업재해보상보험의 보험관계 성립신고 등의 촉진을 위한 특별조치법 | 고용산재보험신고법 | ✓ | 고용노동부 |
| ... | ... | | |
| 근로기준법 | — | X | 고용노동부 |
| ... | | | |

→ 패턴:
- 단일 NNP 가능: 50% 이상 (공백 없는 명칭)
- 다단어 (공백 존재): 30–40% — **Kiwi 사용자 사전 등록 필수**
- 특수문자 (ㅎ 등): 대부분 약칭으로 대체 가능

### LAW_NAME 등록 정책 (권고)
- 본법 123건 전수 verified=false INSERT (pos_tag='NNP')
- 약칭 빈문자열 제외 후 추가 INSERT
- 사용자 검증 시 sample 30건씩 확인 → verified=true 일괄 UPDATE

### 등록 제외 (권고)
- ENFORCEMENT_DECREE 121: "OO법 시행령" 패턴 — 본법 + "시행령" Kiwi 분해로 처리
- ENFORCEMENT_RULE 122: "OO법 시행규칙" 패턴 — 동일
- NOTICE 340: 명칭이 너무 길고 NNP 부적합 — Track E rule_objectify에서 law_master 직접 참조
- STANDARD 42: 동일
- OTHER 4: 동일

---

## C. TECH_TERM 제안 화이트리스트 (15건)

### 법령 형식 용어
| term | pos_tag | 근거 (law_type_code) | 비고 |
|---|---|---|---|
| 법률 | NNG | LAW | |
| 법 | NNG | LAW | 동의어, "~법" 패턴 |
| 시행령 | NNG | ENFORCEMENT_DECREE | |
| 시행규칙 | NNG | ENFORCEMENT_RULE | |
| 대통령령 | NNG | — | df 5.12% |
| 총리령 | NNG | — | df 0.12% |
| 부령 | NNG | — | df 4.02% |
| 고시 | NNG | NOTICE | df 2.59%, 다의성 주의 |
| 훈령 | NNG | — | df 0.14% |
| 예규 | NNG | — | df 0.14% |
| 공고 | NNG | — | |
| 규칙 | NNG | — | 해석/적용 모호성 주의 |
| 규정 | NNG | — | |
| 별표 | NNG | — | df 2.85% (첨부자료 참조) |
| 별지 | NNG | — | df 2.59% (서식 참조) |

### 검증 요청
- 15건 일괄 승인 가능? 추가/제외 수정?

---

## D. INSERT 코드 설계 (의사코드, 실행 보류)

```python
# /tai-api/scripts/v3/track_c/seed_dict_legal_terms.py
# 실행 시점: 사용자 결정 3건 응답 후

import math
from db.supabase_client import get_supabase

sb = get_supabase()
TOTAL_DOCS = 143549  # law_article_part 전체

def tfidf(freq: int, df: int) -> float:
    if df == 0: return 0.0
    return round(math.log(1 + freq) * math.log(TOTAL_DOCS / df), 4)

# 1. AGENCY_NAME 등록 (30건)
agencies = sb.from_('law_master').select('ministry_name').execute()
# ... 콤마 분리 + dedupe + 의심 케이스 제외
# 각 agency에 대해 law_article_part.part_text에서 LIKE '%에이전시%' 빈도 + DF 계산
for agency in agencies_clean:
    freq, df = count_in_articles(agency)
    sb.from_('dict_legal_terms').insert({
        'term': agency,
        'pos_tag': 'NNP',
        'term_type': 'AGENCY_NAME',
        'frequency': freq,
        'score': tfidf(freq, df),
        'source': 'law_master.ministry_name:ground_truth',
        'verified': False,  # 사용자 검증 후 true
        'notes': f'law_count={law_count}, df={df}'
    }).execute()

# 2. LAW_NAME 등록 (LAW 123 + 약칭)
laws = sb.from_('law_master').select('law_name, law_name_short') \
         .eq('law_type_code', 'LAW').eq('is_active', True).execute()
for law in laws:
    # 정식 명칭
    insert_term(law['law_name'], 'NNP', 'LAW_NAME', source='law_master.law_name:ground_truth')
    # 약칭 (비어있으면 skip)
    if law['law_name_short'] and law['law_name_short'].strip():
        if law['law_name_short'] != law['law_name']:
            insert_term(law['law_name_short'], 'NNP', 'LAW_NAME', 
                       source='law_master.law_name_short:ground_truth')

# 3. TECH_TERM 일괄 등록 (화이트리스트 15건)
for term in TECH_TERM_WHITELIST:
    freq, df = count_in_articles(term)
    insert_term(term, 'NNG', 'TECH_TERM', source='manual:whitelist',
                frequency=freq, score=tfidf(freq, df))
```

---

## E. 이후 작업 (Track A `morpheme.py` 완성 후)

1. **GENERIC 추출**: Kiwi NNG/NNP/NF 분해 결과에서 LAW_NAME/AGENCY_NAME/TECH_TERM에 속하지 않는 도메인 명사 추출
2. **Kiwi 사용자 사전 등록 테스트**: 다단어 법령명이 NNP로 토큰화되는지 검증
3. **Cross-check**: surface baseline (Top 200) vs Kiwi 분해 결과 일치/이상점 분석
4. **사용자 검증**: GENERIC Top 100 sample 교대 검증 → verified=true UPDATE
