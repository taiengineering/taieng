# 진단 → Runtime Binding Engine 연결 작업지시

> 작성일: 2026-05-25
> 목표: 진단 실행 후 Legal Adapter v2 호출을 추가하여 runtime_candidate 생성
> 원칙: 엔진 아키텍처 파일 절대 수정 금지

---

## 배경

Runtime Binding Layer가 5/18~19에 구축되었으나, 진단 실행 경로에서 호출되지 않아 단절됨.

현재:
```
진단 실행 → full_result 저장 → 끝 (단절)
```

목표:
```
진단 실행 → full_result 저장
  → Legal Adapter v2 호출 (services/legal_adapter.py :: project_rules)
    → Binding Engine → runtime_candidate 생성
      → 점검항목관리 페이지에 표시
```

## 수정 대상

### 1. `routers/diagnosis_integrated.py`

`/diagnosis/run` 엔드포인트에서, SaaS 고객 진단 시 (factory_id + company_id 존재) Legal Adapter 호출 추가.

```python
# full_result 저장 후
if factory_id and company_id:
    try:
        from services.legal_adapter import project_rules
        rules_for_binding = _convert_rules_table_to_matched_rules(full_result.get('rules_table', []))
        binding_result = await project_rules(
            tenant_id=str(company_id),
            facility_id=str(factory_id),
            matched_rules=rules_for_binding,
            trace_id=f"diagnosis-{diagnosis_id}"
        )
        logger.info(f"Binding Engine: {binding_result['stats']}")
    except Exception as e:
        logger.warning(f"Binding Engine 호출 실패 (non-blocking): {e}")
```

**중요**: anonymous 진단(Nexas 무료/유료)은 tenant_id/facility_id가 없으므로 binding 호출 없음.

### 2. `services/diagnosis_runtime_step1.py`

변환 함수 추가:

```python
def _convert_rules_table_to_matched_rules(rules_table: list[dict]) -> list[dict]:
    """
    full_result의 rules_table 항목을 Legal Adapter가 기대하는 matched_rules 형식으로 변환.
    
    Legal Adapter 기대 필드:
    - rule_kind: INSPECTION / APPOINTMENT / REPORT / TRAINING / PERMIT / PROHIBITION
    - id 또는 rule_id: 고유 ID
    - title 또는 rule_text: 의무 요약
    - law_name: 법령명
    - article: 조문
    - severity: critical/high/medium/low
    - description: 상세 설명
    
    rules_table 현재 필드:
    - obligation_summary, law_name, law_article, rule_kind, 
      penalty_summary, category, who, what, when
    """
    matched = []
    for i, rule in enumerate(rules_table):
        # rule_kind 매핑: FAMILY 코드 → Legal Adapter 기대값
        raw_kind = (rule.get('rule_kind') or rule.get('category') or '').upper()
        
        # FAMILY 코드 → 표준 rule_kind 변환
        kind_map = {
            'APPOINT_FAMILY': 'APPOINTMENT', 'APPOINT': 'APPOINTMENT',
            'PRESERVE_FAMILY': 'INSPECTION', 'PRESERVE': 'INSPECTION',
            'REPORT_FAMILY': 'REPORT', 'REPORT': 'REPORT',
            'TRAINING_FAMILY': 'TRAINING', 'TRAINING': 'TRAINING',
            'MANDATORY_FAMILY': 'INSPECTION', 'MANDATORY': 'INSPECTION',
            'PROHIBITION_FAMILY': 'PROHIBITION', 'PROHIBITION': 'PROHIBITION',
            'PERMISSIVE_FAMILY': 'STANDARD',  # residual로 처리됨
            '선임': 'APPOINTMENT', '점검': 'INSPECTION',
            '신고': 'REPORT', '교육': 'TRAINING', '서류': 'REPORT',
        }
        rule_kind = kind_map.get(raw_kind, raw_kind)
        
        matched.append({
            'rule_id': f"diag-{i}",
            'rule_kind': rule_kind,
            'title': rule.get('obligation_summary') or rule.get('what') or f"Rule {i}",
            'description': f"{rule.get('who', '')} | {rule.get('what', '')} | {rule.get('when', '')}".strip(' |'),
            'law_name': rule.get('law_name'),
            'article': rule.get('law_article'),
            'severity': 'high' if '과태료' in (rule.get('penalty_summary') or '') else 'medium',
        })
    return matched
```

### 3. 수정하지 않는 파일

- `services/legal_adapter.py` — 그대로 사용
- `services/runtime_binding_engine.py` — 그대로 사용
- `services/runtime_activation_service.py` — 그대로 사용
- `engine/*` — 절대 수정 금지

## 검증

### 검증 1: runtime_candidate 생성 확인
```sql
SELECT count(*) FROM runtime_candidate;
-- 진단 전: 0건
-- 진단 후: N건 (진단 결과 rules_table 항목 수에 비례)
```

### 검증 2: 점검항목관리 페이지
```
https://safe.taieng.co.kr/html/horizontal-menu-template/inspection-anchor.html
→ 데이터가 표시되어야 함
```

### 검증 3: Cockpit API
```bash
curl -s "https://api.taieng.co.kr/runtime/candidates" -H "Authorization: Bearer {token}"
→ candidates 목록 반환
```

### 검증 4: anonymous 진단은 binding 없음
```
taieng.co.kr/free-diagnosis.html 에서 진단 실행
→ runtime_candidate 건수 변동 없음 (정상)
```

## 배포

```bash
cd ~/tai-api
git add -A
git commit -m "feat: 진단 → Legal Adapter v2 연결 — runtime_candidate 자동 생성"
git push origin main
railway up
curl -X POST https://api.taieng.co.kr/cron/reload
```

## 주의

- Legal Adapter는 async 함수 — diagnosis_integrated의 엔드포인트가 async인지 확인
- 실패 시 non-blocking (try/except) — 진단 결과 자체는 항상 저장
- `project_rules`은 Supabase client를 내부에서 사용 — `get_supabase()` import 확인
