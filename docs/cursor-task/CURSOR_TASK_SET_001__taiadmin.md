# Cursor 작업지시서 — SET-001 추출 (확정)

**작성일**: 2026-05-04
**대상**: Cursor (TAI 회의실 외 별도 창)
**상태**: ✅ 즉시 시작 가능 (대표님 권장값 확정)

---

## 사용할 파일 (정확한 버전)

```
저장소: github.com/taiengineering/tai-admin
브랜치: main
경로: docs/extraction/

읽을 순서:
1. METHODOLOGY.md          ← 9단계 방법론
2. PROMPT_v3_0_1.md ★      ← LLM 프롬프트 (v3.0이 아니라 v3.0.1!)
3. SET_001_articles.json   ← article 20건 ID 목록
4. rule_patterns.yaml      ← 18개 룰 사전 등록 (Phase 1)
5. sql/select_set_001.sql  ← SET 재현 가능 선정
6. sql/audit_set_v2.sql ★  ← 검증 (v1이 아니라 v2!)
7. RULE_MINER_SPEC.md      ← rule_miner.py 명세 (Phase 2 진입 후 적용)
```

## 확정 설정값

| 항목 | 값 |
|---|---|
| LLM 모델 | `claude-sonnet-4-5` |
| API key | `ANTHROPIC_API_KEY` (환경변수) |
| Pass 전략 | 1-pass + self_check (비용 절감) |
| 예상 비용 | $5~7 (article 20 × 1 호출) |
| 예상 시간 | 15~30분 |
| PASS 기준 | **엄격** (audit 02~22 모두 0건) |
| 검수 후처리 | 자동 검증 통과 + 대표님 spot check 5건 |

## 작업 위치

```bash
mkdir -p ~/dev/tai-extraction-v3
cd ~/dev/tai-extraction-v3

# 파일 다운로드
mkdir -p prompts sql
curl -o prompts/v3_0_1.md https://raw.githubusercontent.com/taiengineering/tai-admin/main/docs/extraction/PROMPT_v3_0_1.md
curl -o sql/select_set_001.sql https://raw.githubusercontent.com/taiengineering/tai-admin/main/docs/extraction/sql/select_set_001.sql
curl -o sql/audit_set_v2.sql https://raw.githubusercontent.com/taiengineering/tai-admin/main/docs/extraction/sql/audit_set_v2.sql
curl -o SET_001_articles.json https://raw.githubusercontent.com/taiengineering/tai-admin/main/docs/extraction/SET_001_articles.json
curl -o rule_patterns.yaml https://raw.githubusercontent.com/taiengineering/tai-admin/main/docs/extraction/rule_patterns.yaml

# .env 작성
cat > .env <<EOF
ANTHROPIC_API_KEY=...  # 입력
SUPABASE_URL=https://vwlahtguyggrhvslabax.supabase.co
SUPABASE_SERVICE_KEY=... # 입력
EOF

# 의존성
pip install anthropic supabase python-dotenv pydantic pyyaml
```

## extract_iterative.py 작성 명세

```python
import os, json
from datetime import datetime, timezone
from pathlib import Path
from anthropic import Anthropic
from supabase import create_client
import yaml

# 환경
client = Anthropic()  # ANTHROPIC_API_KEY 자동
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])
PROMPT = Path('prompts/v3_0_1.md').read_text(encoding='utf-8')
SET_INFO = json.loads(Path('SET_001_articles.json').read_text(encoding='utf-8'))

SET_ID = 'SET-001'
CYCLE = 1
PROMPT_VERSION = 'v3.0.1'

def main():
    # 1. 기존 SET-001 cycle=1 데이터 삭제 (idempotent)
    sb.table('law_rule_drafts').delete().match({
        'ai_flags->>extraction_set': SET_ID,
        'ai_flags->>extraction_cycle': str(CYCLE)
    }).execute()
    # 위 syntax 안 되면 SQL로:
    # sb.rpc('execute_sql', {
    #   'query': f"DELETE FROM law_rule_drafts WHERE ai_flags->>'extraction_set'='{SET_ID}' AND (ai_flags->>'extraction_cycle')::int={CYCLE}"
    # })

    # 2. SET-001 article 20건의 article_text 가져오기
    article_ids = [a['article_id'] for a in SET_INFO['articles']]
    articles_data = sb.table('law_article').select('id,article_text,article_no,article_title,article_type,law_id').in_('id', article_ids).execute().data
    
    # law_master 정보도 join
    law_ids = list(set(a['law_id'] for a in articles_data))
    masters_data = sb.table('law_master').select('id,law_name,law_type_code').in_('id', law_ids).execute().data
    master_map = {m['id']: m for m in masters_data}
    
    # 3. 각 article에 대해 LLM 추출
    total_drafts = 0
    broken_count = 0
    for art in articles_data:
        m = master_map[art['law_id']]
        user_input = f"""law_name: {m['law_name']}
law_type_code: {m['law_type_code']}
article_no: {art['article_no']}
article_type: {art['article_type']}
article_title: {art['article_title']}
article_text: {art['article_text']}"""
        
        # LLM 호출
        resp = client.messages.create(
            model='claude-sonnet-4-5',
            max_tokens=4000,
            system=PROMPT,
            messages=[{'role': 'user', 'content': user_input}]
        )
        
        # JSON 파싱
        try:
            result_text = resp.content[0].text
            # JSON 블록 추출 (```json ... ``` 또는 raw)
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            result = json.loads(result_text)
        except Exception as e:
            print(f"파싱 실패 article {art['id']}: {e}")
            broken_count += 1
            continue
        
        # 4. DB 적재 (각 의무를 별도 row)
        if result.get('broken'):
            broken_count += 1
            continue
            
        for ob in result.get('extracted', []):
            ai_flags = {
                'extraction_set': SET_ID,
                'extraction_cycle': CYCLE,
                'prompt_version': PROMPT_VERSION,
                'extracted_at': datetime.now(timezone.utc).isoformat(),
                'from_pipeline': 'v3_iterative',
                'self_check': result.get('self_check'),
                'broken': False
            }
            sb.table('law_rule_drafts').insert({
                'law_name': m['law_name'],
                'law_article': f"제{art['article_no']}조",
                'article_id': art['id'],
                'article_text': art['article_text'],
                'obligation_summary': ob['obligation_summary'],
                'appointment_target': ob['appointment_target'],
                'obligation_type': ob['obligation_type'],
                'sector': ob.get('sector'),
                'condition_code': ob.get('condition_code'),
                'condition_operator': ob.get('condition_operator'),
                'condition_value': ob.get('condition_value'),
                'penalty_summary': ob.get('penalty_summary'),
                'ai_reasoning': ob['ai_reasoning'],
                'ai_confidence': ob['ai_confidence'],
                'ai_flags': ai_flags,
                'status': 'PENDING',
                'diagnosis_stage': ob.get('diagnosis_stage', 1)
            }).execute()
            total_drafts += 1
    
    # 5. 자동 검증 (audit_set_v2.sql)
    audit_sql = Path('sql/audit_set_v2.sql').read_text(encoding='utf-8')
    # SET-001로 이미 설정됨
    audit = sb.rpc('execute_sql', {'query': audit_sql}).execute().data
    
    # 6. 결과 출력
    issues = [r for r in audit if r['check_id'] != '01_drafts 추출 수' and int(r['value']) > 0]
    pass_status = len(issues) == 0
    
    report = {
        'set_id': SET_ID,
        'cycle': CYCLE,
        'prompt_version': PROMPT_VERSION,
        'articles_processed': len(articles_data),
        'extracted_drafts': total_drafts,
        'broken_articles': broken_count,
        'audit': audit,
        'issues': issues,
        'pass': pass_status,
        'next_step': 'PROMPT v3.0.2 강화 후 cycle 2' if not pass_status else 'SET-001 PASS! rule_miner 실행 → SET-002'
    }
    
    Path('output').mkdir(exist_ok=True)
    Path('output/set_001_cycle_1.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"SET-001 Cycle {CYCLE} ({PROMPT_VERSION})")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"처리: {len(articles_data)}/20 article")
    print(f"추출: {total_drafts} drafts")
    print(f"broken: {broken_count}")
    print(f"")
    print(f"검증 결과:")
    for r in audit:
        if r['check_id'] == '01_drafts 추출 수':
            print(f"  ℹ️  {r['check_id']}: {r['value']}")
        elif int(r['value']) == 0:
            print(f"  ✅ {r['check_id']}")
        else:
            print(f"  ❌ {r['check_id']}: {r['value']}")
    print(f"")
    print(f"PASS: {'YES ✅' if pass_status else 'NO ❌'}")
    print(f"다음: {report['next_step']}")

if __name__ == '__main__':
    main()
```

## 실행

```bash
cd ~/dev/tai-extraction-v3
python extract_iterative.py
```

## 결과 보고 양식

`output/set_001_cycle_1.json` 파일을 본 기획창(이 채팅창)에 첨부하거나 핵심 요약 복사:

```
SET-001 Cycle 1 결과
━━━━━━━━━━━━━━━━━━━━
처리: 20/20
추출 drafts: N
broken: N
PASS: YES/NO

(NO인 경우 issues 목록 첨부)
```

## 다음 단계 (PASS / FAIL 분기)

### PASS 시
1. ✅ SET-001 통과 — 대표님이 spot check 5건 (DB에서 무작위 select)
2. spot check 통과 시 → rule_miner.py 실행 → rule_patterns.yaml 업데이트
3. SET-002 article 선정 (random_seed='002') → 동일 흐름

### FAIL 시
1. issues 목록을 본 기획창에 보고
2. 기획창에서 ERROR_PATTERNS.md 업데이트 + PROMPT v3.0.2 강화
3. Cursor에서 cycle=2로 재실행

## 안전장치

- DELETE → INSERT 트랜잭션 (실패 시 rollback)
- API 호출 실패 시 article 1개 단위로 fail 처리, 나머지 계속
- timeout: article당 90초 (sonnet 처리 여유)
- broken article은 따로 기록, 정상 article는 영향 없음

## 비용 한도

- 정상 시: $5~7
- worst case (재호출 발생): $10
- $10 초과 시 자동 중단

---

**준비 완료. Cursor 진입.**
