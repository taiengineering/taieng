# rule_miner.py 명세

**작성일**: 2026-05-04
**역할**: SET PASS 후 새 룰 자동 추출 → rule_patterns.yaml 누적
**목표**: AI → 결정론적 프로그램 진화 (Phase 1 → 2 → 3 → 4)

## 실행 시점

```bash
# SET-XXX PASS 직후 자동 실행
python rule_miner.py --set SET-001
```

## 처리 순서

```python
def mine_rules(set_id: str):
    """SET-XXX의 결과에서 새 패턴 추출"""
    
    # 1. 해당 SET의 drafts 모두 가져옴
    drafts = get_drafts(set_id)
    skipped = get_skipped_articles(set_id)
    
    # 2. SKIP 룰 채굴
    new_skip_rules = mine_skip_patterns(skipped)
    # - skipped article들의 title 공통 정규식 추출
    # - 새 패턴이 기존 SKIP_001~007에 없으면 추가
    
    # 3. EXTRACT 룰 채굴 
    new_extract_rules = mine_extraction_patterns(drafts)
    # - 항(①②③) 단위 분해 빈도 측정
    # - 복합 동사("및", "또는") 분해 패턴
    
    # 4. CONDITION 룰 채굴
    new_cond_rules = mine_condition_patterns(drafts)
    # - condition_value 정규식 패턴 누적
    # - 새 unit (㎡, kg, 명 등) 발견
    
    # 5. SUBJECT 룰 채굴
    new_subj_rules = mine_subject_patterns(drafts)
    # - appointment_target 새 매핑 (예: "제조업자", "공사감독자")
    
    # 6. 통계 업데이트
    stats = compute_coverage(drafts, all_rules)
    
    # 7. rule_patterns.yaml 업데이트
    update_yaml(new_rules, stats)
    
    # 8. Phase 전환 체크
    if stats['rule_coverage_pct'] >= 30 and current_phase == 1:
        suggest_phase_transition(2)
```

## 채굴 알고리즘

### Skip 룰 채굴
```python
def mine_skip_patterns(skipped_articles):
    """
    skipped article들의 article_title에서 공통 정규식 추출.
    
    예: skipped article 50건 중 
        "수수료" 5건, "수수료 및 보증금" 3건 → '수수료' 패턴 발견
    
    빈도 ≥ 3건 + 기존 룰 안 잡힘 → 새 SKIP 룰 후보
    """
    titles = [a['article_title'] for a in skipped_articles]
    
    # 1. 단어 빈도
    word_freq = count_words(titles)
    
    # 2. 빈도 ≥ 3 + 기존 룰 미커버
    candidates = [w for w, f in word_freq.items() 
                  if f >= 3 and not covered_by_existing_rules(w)]
    
    # 3. YAML 추가 후보
    return [
        {'id': next_skip_id(), 'name': w, 
         'pattern_type': 'title_regex', 'pattern': w,
         'action': 'skipped', 'confidence': 0.85,
         'discovered_in': set_id, 'validated_count': word_freq[w]}
        for w in candidates
    ]
```

### Condition 룰 채굴
```python
def mine_condition_patterns(drafts):
    """
    condition_value의 정규식 패턴 추출.
    
    예: condition_value="100kg 이상" 5건, "500kg 이상" 3건
    → 패턴 r'(\d+)\s*kg\s*(이상|이하)' 발견
    """
    cond_values = [d['condition_value'] for d in drafts 
                   if d['condition_value']]
    
    # 정규식 추론
    patterns = infer_regex_patterns(cond_values)
    # 빈도 ≥ 3 + 기존 미커버 → 새 COND 룰
    return new_rules
```

## 출력

### rule_patterns.yaml 업데이트
```yaml
stats:
  total_rules: 23      # 18 → 23 (5개 추가)
  rule_coverage_pct: 32  # 0 → 32 ★ Phase 2 진입 가능
  last_set: SET-005
  ai_calls_saved_pct: 30
```

### 콘솔 출력
```
SET-005 PASS — 룰 채굴 결과
────────────────────────────
새 SKIP 룰: 2개
  SKIP_009: "수수료" (validated_count=5)
  SKIP_010: "공시" (validated_count=4)

새 COND 룰: 1개
  COND_004: 가스용량 (kg/m³ 단위)

새 SUBJ 룰: 0개
새 EXTRACT 룰: 0개

통계:
  총 룰: 23 (이전 18)
  커버리지: 32% (이전 0%)
  AI 호출 절감 추정: 30%

★ Phase 2 진입 권장 (커버리지 ≥ 30%)
```

## Phase 전환 권장 기준

| Phase | 룰 커버리지 | AI 비용 | 동작 |
|---|---:|---:|---|
| 1 | 0~30% | 100% | 모든 article AI 추출 |
| 2 | 30~70% | 50~70% | 룰 매칭 article은 룰 후처리, 나머지 AI |
| 3 | 70~95% | 10~30% | 룰 우선, AI fallback |
| 4 | 95%+ | <5% | 거의 룰만, 신규 법령만 AI |

## 의존성

- Python 3.11+
- `pyyaml`, `regex` (정규식 추론)
- 입력: rule_patterns.yaml + DB drafts
- 출력: rule_patterns.yaml 업데이트

## 안전장치

- **백업**: 매 실행 전 rule_patterns.yaml.bak 생성
- **검증**: 새 룰 추가 후 기존 SET-001~XXX에 회귀 테스트
- **수동 승인**: confidence < 0.85 룰은 사람 검토 후 활성화
