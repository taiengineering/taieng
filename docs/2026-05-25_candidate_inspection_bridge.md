# runtime_candidate → inspection_sets 브리지 작업지시

> 작성일: 2026-05-25
> 목표: Legal Adapter가 runtime_candidate 생성 시 inspection_sets도 동시 생성
> 원칙: 엔진 아키텍처 파일 절대 수정 금지

---

## 배경

- `inspection-anchor.html`은 `GET /inspection-sets?factory_id=` 호출
- `runtime_candidate`를 읽지 않음
- runtime_candidate 3건이 있지만 점검항목관리에 표시 안 됨
- inspection_sets에 동시 생성해야 FE에 보임

## 수정 대상

### `services/legal_adapter.py`

`project_rules()` 함수에서 `project_candidate()` 호출 후,
같은 데이터로 `inspection_sets` INSERT 추가.

```python
# project_candidate 후 추가
if candidate_type in ('inspection', 'appointment', 'report', 'training', 'compliance_check'):
    _create_inspection_set(
        tenant_id=tenant_id,
        facility_id=facility_id,
        candidate=inp,
        rule=rule,
        candidate_result=result,
    )
```

### 신규 함수 `_create_inspection_set()`

```python
_CANDIDATE_TO_OBLIGATION = {
    'inspection': 'INSPECT',
    'appointment': 'APPOINT',
    'report': 'REPORT',
    'training': 'DOCUMENT',
    'compliance_check': 'ACTION',
    'permit': 'DOCUMENT',
}

_DEFAULT_CYCLES = {
    'INSPECT': ('year', 1),
    'BEFORE_WORK': ('day', 1),
    'REPORT': ('year', 1),
    'DOCUMENT': ('year', 1),
    'NOTIFY': ('year', 1),
    'APPOINT': ('year', 1),
    'ACTION': ('year', 1),
}

def _create_inspection_set(tenant_id, facility_id, candidate, rule, candidate_result):
    """
    runtime_candidate 생성 시 inspection_sets에도 INSERT.
    중복 방지: law_name + law_article + factory_id 기준.
    """
    sb = get_supabase()
    
    law_name = rule.get('law_name') or ''
    law_article = rule.get('article') or ''
    obl_type = _CANDIDATE_TO_OBLIGATION.get(candidate.candidate_type, 'OTHER')
    cycle_unit, cycle_value = _DEFAULT_CYCLES.get(obl_type, ('year', 1))
    
    # 중복 방지
    existing = sb.table('inspection_sets').select('id') \
        .eq('factory_id', facility_id) \
        .eq('law_name', law_name) \
        .eq('law_article', law_article) \
        .execute()
    if existing.data:
        return  # 이미 존재
    
    set_id = str(uuid.uuid4())
    row = {
        'id': set_id,
        'company_id': tenant_id,
        'factory_id': facility_id,
        'inspection_set_name': candidate.title[:200],
        'law_name': law_name,
        'law_article': law_article,
        'obligation_type': obl_type,
        'obligation_summary': candidate.description or candidate.title,
        'cycle_unit': cycle_unit,
        'cycle_value': cycle_value,
        'source': 'LEGAL_ENGINE',
        'is_active': True,
    }
    sb.table('inspection_sets').insert(row).execute()
```

### 중복 방지 중요

같은 factory_id + law_name + law_article로 이미 존재하면 INSERT 스킵.
진단을 여러 번 실행해도 중복 생성 없음.

## 검증

1. `runtime_candidate` 3건에 대응하는 `inspection_sets` 3건 생성 확인
2. `inspection-anchor.html`에서 해당 factory로 접속 시 데이터 표시
3. 중복 실행 시 추가 생성 없음

## 배포

```bash
cd ~/tai-api
git add -A
git commit -m "feat: Legal Adapter — runtime_candidate 생성 시 inspection_sets 동시 생성"
git push origin main
railway up
curl -X POST https://api.taieng.co.kr/cron/reload
```

## 배포 후 검증

```bash
# Legal Adapter 재호출로 검증
curl -s -X POST https://api.taieng.co.kr/runtime/legal-adapter/project \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "e8f2e585-c8f9-4974-b63f-4b2503da224d",
    "facility_id": "c1938931-b2f8-4a15-ad56-e2e674540b0b",
    "matched_rules": [
      {"rule_id": "bridge-test-001", "rule_kind": "INSPECTION", "title": "안전보건교육 실시", "law_name": "산업안전보건법", "article": "제29조", "severity": "high"}
    ]
  }'
```

DB 확인:
```sql
SELECT id, inspection_set_name, law_name, law_article, obligation_type, source
FROM inspection_sets
WHERE factory_id = 'c1938931-b2f8-4a15-ad56-e2e674540b0b'
AND source = 'LEGAL_ENGINE'
ORDER BY created_at DESC;
```

## 주의
- `runtime_activation_service.py` 수정 없음 (기존 흐름 유지)
- `inspection-anchor.html` 수정 없음 (기존 FE 유지)
- 엔진 파일 수정 없음
