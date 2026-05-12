#!/usr/bin/env python3
"""
classify_articles_v1.py — content_type 다중 분류 (v3.0)

v3.0 변경 (2026-05-06):
- update_chunked 함수에 정기 재연결 추가 (오버쿼리 방지):
  - reset_every rows마다 supabase 재연결 + 1초 대기 (기본 500)
  - 105K parts UPDATE 같은 대용량 작업에서 connection pool 이슈 방지

v2.9 변경: 5개 룰 보강 (PROHIBITION_cannot_general, seoneun_anhdoenda, OBLIGATION_handa_after_paren, jinda, doeenda_space)
v2.8 변경: OBLIGATION_dunda + handa_space + doeenda
v2.7 변경: EXCEPTION_haji_anihanda 종결 조건 + RIGHT_have
v2.6 변경: EXCEPTION_haji_anihanda + AUTHORITY_general_can
v2.5 변경: parts에 article 본문 fallback traversal + RIGHT_have
v2.4 변경: OBLIGATION_ya_handa, handa_general, badaya 보강
v2.3 변경: DEFINITION_colon, OBLIGATION_eoya_handa, haeng_handa 확장
v2.2 변경: 6개 룰 추가
v2.1 변경: PROHIBITION_cannot (?<!초과), AUXILIARY_old_law_cite 후처리

원칙 (불변): AI 임의해석 0, 100% 커버 + 정확성 우선

Usage:
    railway run python3 docs/extraction/scripts/classify_articles_v1.py --dry-run --target part_general
    railway run python3 docs/extraction/scripts/classify_articles_v1.py --target part_general
    railway run python3 docs/extraction/scripts/classify_articles_v1.py --reset --target all
"""

import argparse
import os
import re
import sys
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

try:
    import httpx
    from supabase import Client, create_client
except ImportError:
    print("[ERROR] pip install supabase httpx", file=sys.stderr)
    sys.exit(1)


SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("SUPABASE_KEY")
)
if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 없음.", file=sys.stderr)
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


RETRY_EXCEPTIONS = (
    httpx.RemoteProtocolError, httpx.ConnectError, httpx.ReadTimeout,
    httpx.WriteTimeout, httpx.PoolTimeout, httpx.ConnectTimeout,
    httpx.NetworkError, ConnectionError,
)


def reset_supabase():
    global supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def with_retry(func, max_retries=5, initial_delay=1.0):
    for attempt in range(max_retries):
        try:
            return func()
        except RETRY_EXCEPTIONS as e:
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                print(f"  [RETRY {attempt+1}/{max_retries}] {type(e).__name__}: 대기 {delay:.1f}s + 재연결")
                time.sleep(delay)
                reset_supabase()
            else:
                raise


# ============================================================
# 룰 정의 v3.0 (룰은 v2.9와 동일)
# ============================================================
TYPE_PRIORITY = {
    'EXCEPTION': 1,
    'PENALTY': 2,
    'PROHIBITION': 3,
    'DEFINITION': 4,
    'NOTIFICATION': 5,
    'RECOMMENDATION': 6,
    'OBLIGATION': 7,
    'AUTHORITY': 8,
    'RIGHT': 9,
    'AUXILIARY': 10,
}


RULES = [
    ('rule:EXCEPTION_proviso_daman',
     re.compile(r'(?:^|\n)\s*다만,'), 'EXCEPTION'),
    ('rule:EXCEPTION_proviso_apply_not',
     re.compile(r'적용하지 (?:않을|아니할) 수 있다'), 'EXCEPTION'),
    ('rule:EXCEPTION_proviso_install_not',
     re.compile(r'설치하지 (?:않을|아니할) 수 있다'), 'EXCEPTION'),
    ('rule:EXCEPTION_proviso_geureohji',
     re.compile(r'그러하지 아니하다|그렇지 (?:아니하다|않다)'), 'EXCEPTION'),
    ('rule:EXCEPTION_proviso_exclude_decl',
     re.compile(r'(?:산입|포함|적용)하지 (?:아니한다|않는다|않은다)'), 'EXCEPTION'),
    ('rule:EXCEPTION_haji_anihanda',
     re.compile(r'[가-힣]+하지 (?:아니한다|않는다|않은다|아니할 수 있다)(?:\s|\.|$|\n|\)|<|＜|,)'), 'EXCEPTION'),
    ('rule:EXCEPTION_proviso_exclude_can',
     re.compile(r'(?:산입|포함|적용)하지 않을 수 있다'), 'EXCEPTION'),
    ('rule:EXCEPTION_proviso_jeoyae',
     re.compile(r'제외한다|제외할 수 있다'), 'EXCEPTION'),
    ('rule:EXCEPTION_proviso_clause_disable',
     re.compile(r'단서를 적용하지 않는다'), 'EXCEPTION'),

    ('rule:PENALTY_money_jail', re.compile(r'벌금|과태료|징역'), 'PENALTY'),
    ('rule:PENALTY_action', re.compile(r'처(?:한다|벌)|부과한다|과한다'), 'PENALTY'),

    ('rule:PROHIBITION_anidoenda',
     re.compile(r'아니 (?:된|되)다|아니된다|하여서는 안 된다|해서는 안 된다'), 'PROHIBITION'),
    ('rule:PROHIBITION_seoneun_anhdoenda',
     re.compile(r'[가-힣]+서는 안 (?:된|되)다(?:\s|\.|$|\n)'), 'PROHIBITION'),
    ('rule:PROHIBITION_geumji', re.compile(r'(?:사용을\s*)?금지(?:한다|된다)'), 'PROHIBITION'),
    ('rule:PROHIBITION_cannot',
     re.compile(r'(?<!초과)할 수 없다(?:\s|\.|$|\n)'), 'PROHIBITION'),
    ('rule:PROHIBITION_cannot_general',
     re.compile(r'[가-힣]+\s*수 없다(?:\s|\.|$|\n|,)'), 'PROHIBITION'),
    ('rule:PROHIBITION_haji_motanda',
     re.compile(r'[가-힣]+하지 못한다(?:\s|\.|$|\n)'), 'PROHIBITION'),

    ('rule:DEFINITION_irahanda',
     re.compile(r'이라 한다|라 한다|이라 함은|라 함은|이라 하며|라 하며'), 'DEFINITION'),
    ('rule:DEFINITION_malhanda',
     re.compile(r'을 말한다|를 말한다'), 'DEFINITION'),
    ('rule:DEFINITION_robonda', re.compile(r'로 본다'), 'DEFINITION'),
    ('rule:DEFINITION_quoted_term',
     re.compile(r'"[^"]+"란\s|"[^"]+"이란\s'), 'DEFINITION'),
    ('rule:DEFINITION_define_term',
     re.compile(r'로 정의된다|(?:으로|로) 정의한다|(?:이라고|라고) 정의'), 'DEFINITION'),
    ('rule:DEFINITION_term_section',
     re.compile(r'^(?:\d+(?:\.\d+)*\s*)?용어의 정의|^(?:\d+(?:\.\d+)*\s*)?기호의 정의'), 'DEFINITION'),
    ('rule:DEFINITION_eun_neun_ida',
     re.compile(r'(?:은|는) [^.]{2,80}(?:이다|입니다)(?:\s|\.|$|\n)'), 'DEFINITION'),
    ('rule:DEFINITION_colon',
     re.compile(r'^[^.\n]{1,40}[:：]\s'), 'DEFINITION'),

    ('rule:NOTIFICATION_alryo',
     re.compile(r'알려야 한다|알려야 하며|공지하여야|공지해야|고지하여야|고지해야|통지(?:하여야|해야|한다)|통보(?:하여야|해야|한다)'), 'NOTIFICATION'),

    ('rule:RECOMMENDATION_norok',
     re.compile(r'노력하여야|노력해야'), 'RECOMMENDATION'),
    ('rule:RECOMMENDATION_gwongo',
     re.compile(r'권고한다|권장한다'), 'RECOMMENDATION'),

    ('rule:OBLIGATION_hayeoyahanda',
     re.compile(r'하여야 한다|해야 한다|하여야 하며|해야 하며'), 'OBLIGATION'),
    ('rule:OBLIGATION_isseoya',
     re.compile(r'있어야 한다|있어야 하며|있어야 할 것|없어야 한다|없도록 한다|없도록 할 것'), 'OBLIGATION'),
    ('rule:OBLIGATION_dueoya',
     re.compile(r'두어야 한다|갖추어야 한다|갖춰야 한다'), 'OBLIGATION'),
    ('rule:OBLIGATION_dunda',
     re.compile(r'[가-힣]+\s*둔다(?:\s|\.|$|\n)'), 'OBLIGATION'),
    ('rule:OBLIGATION_doeeoya',
     re.compile(r'되어야 한다|되어야 할 것|되어야 하며|작성되어야|설치되어야|운전되어야'), 'OBLIGATION'),
    ('rule:OBLIGATION_doeenda',
     re.compile(r'[가-힣]+된다(?:\s|\.|$|\n)'), 'OBLIGATION'),
    ('rule:OBLIGATION_doeenda_space',
     re.compile(r'[가-힣]+\s+된다(?:\s|\.|$|\n)'), 'OBLIGATION'),
    ('rule:OBLIGATION_anhcommand',
     re.compile(r'하지 않아야 한다|하지 않아야 하며|하지 않도록 한다|않도록 할 것'), 'OBLIGATION'),
    ('rule:OBLIGATION_eoya_handa',
     re.compile(r'[가-힣]+(?:어야|아야|여야|이어야) 한다'), 'OBLIGATION'),
    ('rule:OBLIGATION_ya_handa',
     re.compile(r'[가-힣]+야 한다(?:\s|\.|$|\n)'), 'OBLIGATION'),
    ('rule:OBLIGATION_handa_general',
     re.compile(r'[가-힣]+한다(?:\s|\.|$|\n)'), 'OBLIGATION'),
    ('rule:OBLIGATION_handa_space',
     re.compile(r'[가-힣]+\s+한다(?:\s|\.|$|\n)'), 'OBLIGATION'),
    ('rule:OBLIGATION_handa_after_paren',
     re.compile(r'\)한다(?:\s|\.|$|\n)'), 'OBLIGATION'),
    ('rule:OBLIGATION_jinda',
     re.compile(r'(?:의무|책임|효력)(?:가|를|이) (?:진|있|가진)다(?:\s|\.|$|\n|,|고|며)'), 'OBLIGATION'),
    ('rule:OBLIGATION_geot_general',
     re.compile(r'[가-힣]+\s+것(?:\s|\.|$|\n|\)|<|>|＜|＞)'), 'OBLIGATION'),
    ('rule:OBLIGATION_jjunsoo',
     re.compile(r'준수할 것|준수하여야|준수해야|적합한 것|적합해야'), 'OBLIGATION'),
    ('rule:OBLIGATION_quote_specific',
     re.compile(r'에 따라야 한다|기준에 따른다|규정에 따른다|기술기준에 따른다|건설기준에 따른다'), 'OBLIGATION'),
    ('rule:OBLIGATION_ttara_gen',
     re.compile(r'(?:에|을|를) 따른다'), 'OBLIGATION'),
    ('rule:OBLIGATION_ro_handa',
     re.compile(r'(?:으로|로) 한다(?:\s|\.|$|\n)'), 'OBLIGATION'),
    ('rule:OBLIGATION_isang_ihaheoya',
     re.compile(r'이상이어야 한다|이하여야 한다|이상으로 한다|이하로 한다'), 'OBLIGATION'),
    ('rule:OBLIGATION_badaya',
     re.compile(r'받아야 (?:한다|하며|하는|할)'), 'OBLIGATION'),
    ('rule:OBLIGATION_haeng_handa',
     re.compile(r'준용한다|적용한다|실시한다|운영한다|분류한다|반영한다|설치ㆍ운영한다|규정한다|위탁한다|지원한다|지급한다|징수한다|부담한다|구분한다|판정한다|선정한다|결정한다|지정한다|발급한다|승인한다'), 'OBLIGATION'),
    ('rule:OBLIGATION_jeonghanda',
     re.compile(r'(?:정한다|고시한다)(?:\s|\.|$|\n)'), 'OBLIGATION'),
    ('rule:OBLIGATION_uihanda',
     re.compile(r'에 의한다(?:\s|\.|$|\n)'), 'OBLIGATION'),
    ('rule:OBLIGATION_hanhanda',
     re.compile(r'한한다|초과할 수 없다'), 'OBLIGATION'),
    ('rule:OBLIGATION_gwa_gatda',
     re.compile(r'(?:과|와) 같다(?:\s|\.|$|\n)'), 'OBLIGATION'),
    ('rule:OBLIGATION_seolchi_handa',
     re.compile(r'설치한다(?:\s|\.|$|\n)|효력을 가진다'), 'OBLIGATION'),

    ('rule:AUTHORITY_admin_can',
     re.compile(r'(?:장관|청장|시장|군수|구청장|시·도지사|위원장|공무원|소방서장|소방본부장|경찰서장|국토교통부장관)[가-힣\s,·]*(?:은|는|이|가)[^.]*할 수 있다'),
     'AUTHORITY'),
    ('rule:AUTHORITY_punish',
     re.compile(r'처분할 수 있다|명할 수 있다|취소할 수 있다'), 'AUTHORITY'),
    ('rule:AUTHORITY_general_can',
     re.compile(r'(?:정부|국가(?:와|는|이|가)|지방자치단체|위원회|공단|관리청|발주청|소방관서장|중앙행정기관|행정기관|관계 [가-힣\s]{1,15}장|관할 [가-힣\s]{1,15}장)(?:[가-힣\s,·및\(\)]*)?(?:은|는|이|가|와)[^.]*할 수 있다'),
     'AUTHORITY'),

    ('rule:RIGHT_ja_can',
     re.compile(r'(?:자|관계인|소유자|점유자|관리자)는[^.]*할 수 있다|(?:자|관계인|소유자|점유자|관리자)가[^.]*할 수 있다'),
     'RIGHT'),
    ('rule:RIGHT_request',
     re.compile(r'요청할 수 있다|신청할 수 있다|청구할 수 있다'), 'RIGHT'),
    ('rule:RIGHT_follow_can',
     re.compile(r'따를 수 있다|선택할 수 있다'), 'RIGHT'),
    ('rule:RIGHT_action_can',
     re.compile(r'설치할 수 있다|설치 할 수 있다|인정할 수 있다|설정할 수 있다|결정할 수 있다|적용할 수 있다|정할 수 있다|분류할 수 있다|수행할 수 있다|이용할 수 있다|선정할 수 있다'), 'RIGHT'),
    ('rule:RIGHT_ro_can',
     re.compile(r'(?:으로|로) 할 수 있다(?:\s|\.|$|\n)'), 'RIGHT'),
    ('rule:RIGHT_general_can',
     re.compile(r'[가-힣]+\s*수 있다(?:\s|\.|$|\n|,|고)'), 'RIGHT'),
    ('rule:RIGHT_have',
     re.compile(r'(?:권리|의무)(?:가|를) (?:있|가진)다(?:\s|\.|$|\n|,|고|며)'), 'RIGHT'),

    ('rule:AUXILIARY_deleted',
     re.compile(r'^\s*\d+(?:\.\d+)*\s*[<＜]\s*삭제'), 'AUXILIARY'),
    ('rule:AUXILIARY_deleted_law',
     re.compile(r'^\s*(?:제\d+조(?:의\d+)?\s*)?삭제\s*[<＜]'), 'AUXILIARY'),
    ('rule:AUXILIARY_enforcement_date',
     re.compile(r'\d{4}년\s*\d+월\s*\d+일부터 시행|발령일(?:로)?부터 시행|이 (?:기준|규정|법|령)은 .*부터 시행한다'), 'AUXILIARY'),
    ('rule:AUXILIARY_old_law_cite',
     re.compile(r'시행 전에[^.]*에 따른다|종전의 .*?에 따른다'), 'AUXILIARY'),
    ('rule:AUXILIARY_period_pass',
     re.compile(r'\d+개월이 경과한 날부터 시행'), 'AUXILIARY'),
    ('rule:AUXILIARY_empty_section',
     re.compile(r'내용\s*없음|해당\s*없음'), 'AUXILIARY'),
    ('rule:AUXILIARY_ref_section_title',
     re.compile(r'^\s*\d+(?:\.\d+)*\s*관련 (?:법규|기준)|^\s*\d+(?:\.\d+)*\s*참고 (?:기준|문헌)'), 'AUXILIARY'),
]


def classify_text(text: str) -> Tuple[List[str], List[str]]:
    if not text:
        return [], []

    matched_rules = []
    matched_types_set = set()

    for rule_id, pattern, ctype in RULES:
        if pattern.search(text):
            matched_rules.append(rule_id)
            matched_types_set.add(ctype)

    if 'rule:AUXILIARY_old_law_cite' in matched_rules:
        oblig_conflict_rules = {'rule:OBLIGATION_ttara_gen', 'rule:OBLIGATION_quote_specific'}
        matched_rules = [r for r in matched_rules if r not in oblig_conflict_rules]
        has_other_oblig = any(
            r.startswith('rule:OBLIGATION') and r not in oblig_conflict_rules
            for r in matched_rules
        )
        if not has_other_oblig:
            matched_types_set.discard('OBLIGATION')

    sorted_types = sorted(matched_types_set, key=lambda t: TYPE_PRIORITY.get(t, 99))
    return sorted_types, matched_rules


def primary_type(types: List[str]) -> Optional[str]:
    if not types:
        return None
    return min(types, key=lambda t: TYPE_PRIORITY.get(t, 99))


def confidence_level(num_rules: int, is_inherited: bool) -> str:
    if is_inherited:
        return 'LOW'
    if num_rules >= 2:
        return 'HIGH'
    if num_rules == 1:
        return 'MEDIUM'
    return 'NONE'


def fetch_all_paged(table, columns, filters=None, in_filter=None, not_filter=None,
                    page_size=1000, hard_limit=None):
    all_rows = []
    offset = 0
    while True:
        def _fetch():
            q = supabase.from_(table).select(columns)
            if filters:
                for k, v in filters.items():
                    q = q.eq(k, v)
            if in_filter:
                col, vals = in_filter
                q = q.in_(col, list(vals))
            if not_filter:
                col, vals = not_filter
                q = q.not_.in_(col, list(vals))
            q = q.range(offset, offset + page_size - 1)
            return q.execute().data
        batch = with_retry(_fetch)
        if not batch:
            break
        all_rows.extend(batch)
        if hard_limit and len(all_rows) >= hard_limit:
            all_rows = all_rows[:hard_limit]
            break
        if len(batch) < page_size:
            break
        offset += page_size
    return all_rows


def update_chunked(table, updates, chunk_size=100, key_col='id', reset_every=500):
    """v3.0: 정기 재연결로 오버쿼리 방지.
    
    reset_every rows마다 supabase 클라이언트 재생성 + 1초 대기.
    105K parts UPDATE 같은 대용량 작업에서 connection pool exhaustion 방지.
    """
    total = 0
    rows_since_reset = 0
    for i in range(0, len(updates), chunk_size):
        chunk = updates[i:i + chunk_size]
        for row in chunk:
            row_id = row.pop(key_col)
            try:
                with_retry(lambda: supabase.from_(table).update(row).eq(key_col, row_id).execute())
                total += 1
                rows_since_reset += 1
            except Exception as e:
                print(f"  [WARN] {table} {key_col}={row_id} update fail: {str(e)[:100]}")
                continue
        # 진행 보고
        processed = min(i + chunk_size, len(updates))
        if processed % 500 == 0 or processed == len(updates):
            print(f"  [PROGRESS] {table}: {processed}/{len(updates)} updated")
        # 정기 재연결 (오버쿼리 방지)
        if rows_since_reset >= reset_every:
            print(f"  [RECONNECT] {processed}/{len(updates)}: supabase 재연결 + 1s 대기")
            reset_supabase()
            time.sleep(1)
            rows_since_reset = 0
    return total


def classify_nftc_kds(args):
    print("\n" + "=" * 70)
    print("[1/4] NFTC/KDS leaf articles 분류 (law_article)")
    print("=" * 70)

    print("\n[FETCH] NFTC/KDS articles 전체 (leaf + parent)...")
    all_articles = []
    offset = 0
    while True:
        def _fetch():
            return supabase.from_('law_article').select(
                'id,parent_article_id,article_text,article_internal_key,article_type,law_id'
            ).or_(
                'article_internal_key.like.NFTC%,article_internal_key.like.KDS%'
            ).range(offset, offset + 999).execute().data
        batch = with_retry(_fetch)
        if not batch:
            break
        all_articles.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000

    print(f"[INFO] 가져온 articles: {len(all_articles)}")

    has_child = set()
    for a in all_articles:
        if a.get('parent_article_id'):
            has_child.add(a['parent_article_id'])

    leaf_ids = {a['id'] for a in all_articles if a['id'] not in has_child}
    print(f"[INFO] leaf articles: {len(leaf_ids)}")

    article_by_id = {a['id']: a for a in all_articles}
    direct_classification = {}

    for a in all_articles:
        types, rules = classify_text(a.get('article_text') or '')
        direct_classification[a['id']] = (types, rules)

    direct_count = sum(1 for t, _ in direct_classification.values() if t)
    print(f"[INFO] 직접 매칭: {direct_count}/{len(all_articles)} ({100*direct_count/len(all_articles):.1f}%)")

    final_classification = {}
    inherited_count = 0
    null_count = 0

    for leaf_id in leaf_ids:
        types, rules = direct_classification[leaf_id]
        if types:
            final_classification[leaf_id] = (types, rules, confidence_level(len(rules), False), 'direct')
            continue

        cur = article_by_id[leaf_id]
        depth = 0
        inherited_types = None
        inherited_rules = None

        while cur and cur.get('parent_article_id') and depth < 10:
            parent = article_by_id.get(cur['parent_article_id'])
            if not parent:
                break
            ptypes, prules = direct_classification[parent['id']]
            if ptypes:
                inherited_types = ptypes
                inherited_rules = prules + ['inherited:from_' + (parent.get('article_internal_key') or parent['id'][:8])]
                break
            cur = parent
            depth += 1

        if inherited_types:
            final_classification[leaf_id] = (inherited_types, inherited_rules, 'LOW', 'inherited')
            inherited_count += 1
        else:
            final_classification[leaf_id] = (None, ['_NULL_NEEDS_REVIEW'], 'NONE', 'null_needs_review')
            null_count += 1

    print(f"\n[RESULT]")
    print(f"  - direct 매칭: {len(leaf_ids) - inherited_count - null_count}")
    print(f"  - 부모 상속: {inherited_count}")
    print(f"  - NULL_NEEDS_REVIEW: {null_count}")

    if args.dry_run:
        type_dist = defaultdict(int)
        for types, _, _, source in final_classification.values():
            if types:
                type_dist[(primary_type(types), source)] += 1
            else:
                type_dist[(None, source)] += 1
        print("\n[DRY-RUN 분포]")
        for (ptype, source), cnt in sorted(type_dist.items(), key=lambda x: -x[1]):
            print(f"  {source:20} {ptype or 'NULL':25} {cnt}")

        null_leaves = [(lid, article_by_id[lid]) for lid, (t, _, _, s) in final_classification.items()
                       if s == 'null_needs_review']
        if null_leaves:
            print(f"\n[DRY-RUN NULL leaf sample] (총 {len(null_leaves)}건)")
            for lid, a in null_leaves[:20]:
                key = a.get('article_internal_key', '')
                text = (a.get('article_text') or '')[:120].replace('\n', ' ')
                print(f"  [{key}] {text}")
        return

    print(f"\n[UPDATE] law_article에 분류 결과 INSERT 중...")
    from datetime import datetime
    now_iso = datetime.now().isoformat()
    updates = []
    for leaf_id, (types, rules, confidence, source) in final_classification.items():
        updates.append({
            'id': leaf_id,
            'content_types': types,
            'primary_content_type': primary_type(types) if types else None,
            'classification_confidence': confidence,
            'classified_by_rules': rules,
            'classified_at': now_iso,
        })

    total = update_chunked('law_article', updates, chunk_size=50, key_col='id')
    print(f"[DONE] {total}/{len(updates)} articles updated")


def classify_parts(args, target_filter):
    print("\n" + "=" * 70)
    print(f"[Parts 분류] target={target_filter}")
    print("=" * 70)

    print("\n[FETCH] parts 가져오는 중...")
    KEC_LAW_ID = '64209405-1a40-4f0a-aa8a-6f3e55917001'

    if target_filter == 'general':
        all_parts = []
        offset = 0
        empty_retry_used = False  # 빈 batch 1회 retry (false-negative 방지)
        fetched_since_reset = 0
        RESET_THRESHOLD = 10000  # 10K fetch마다 supabase 재연결
        while True:
            def _fetch():
                q = supabase.from_('law_article_part').select(
                    'id,article_id,parent_id,part_text,part_type,depth'
                )
                if getattr(args, 'null_only', False):
                    q = q.is_('content_types', 'null').is_('classification_confidence', 'null')
                return q.order('id').range(offset, offset + 999).execute().data
            batch = with_retry(_fetch)
            if not batch:
                if empty_retry_used:
                    break
                empty_retry_used = True
                print(f"  [WARN] empty batch at offset={offset}, 재연결 후 한 번 더 시도")
                reset_supabase()
                time.sleep(2)
                continue
            empty_retry_used = False
            all_parts.extend(batch)
            fetched_since_reset += len(batch)
            if len(batch) < 1000:
                break
            offset += 1000
            if fetched_since_reset >= RESET_THRESHOLD:
                print(f"  [FETCH-RECONNECT] {len(all_parts)} fetched, 재연결")
                reset_supabase()
                time.sleep(1)
                fetched_since_reset = 0
        print(f"[INFO] 전체 fetch: {len(all_parts)} parts")

        # dedup 안전장치 (PostgREST 페이지네이션 일관성 보강)
        seen_ids = set()
        deduped = []
        for p in all_parts:
            if p['id'] not in seen_ids:
                seen_ids.add(p['id'])
                deduped.append(p)
        if len(deduped) != len(all_parts):
            print(f"[WARN] fetch 중복 제거: {len(all_parts)} → {len(deduped)} "
                  f"({len(all_parts) - len(deduped)} 중복)")
        all_parts = deduped

        article_ids = list({p['article_id'] for p in all_parts if p.get('article_id')})
        article_types = {}
        for i in range(0, len(article_ids), 200):
            chunk = article_ids[i:i + 200]
            def _fetch_a():
                return supabase.from_('law_article').select('id,article_type,law_id,article_text').in_(
                    'id', chunk
                ).execute().data
            res = with_retry(_fetch_a)
            for r in res:
                article_types[r['id']] = (r.get('article_type'), r.get('law_id'), r.get('article_text'))

        target_parts = [
            p for p in all_parts
            if (article_types.get(p['article_id'], (None, None, None))[0] == '조문'
                and article_types.get(p['article_id'], (None, None, None))[1] != KEC_LAW_ID)
        ]
    elif target_filter == 'bonchik':
        all_parts = []
        offset = 0
        empty_retry_used = False  # 빈 batch 1회 retry (false-negative 방지)
        fetched_since_reset = 0
        RESET_THRESHOLD = 10000  # 10K fetch마다 supabase 재연결
        while True:
            def _fetch():
                q = supabase.from_('law_article_part').select(
                    'id,article_id,parent_id,part_text,part_type,depth'
                )
                if getattr(args, 'null_only', False):
                    q = q.is_('content_types', 'null').is_('classification_confidence', 'null')
                return q.order('id').range(offset, offset + 999).execute().data
            batch = with_retry(_fetch)
            if not batch:
                if empty_retry_used:
                    break
                empty_retry_used = True
                print(f"  [WARN] empty batch at offset={offset}, 재연결 후 한 번 더 시도")
                reset_supabase()
                time.sleep(2)
                continue
            empty_retry_used = False
            all_parts.extend(batch)
            fetched_since_reset += len(batch)
            if len(batch) < 1000:
                break
            offset += 1000
            if fetched_since_reset >= RESET_THRESHOLD:
                print(f"  [FETCH-RECONNECT] {len(all_parts)} fetched, 재연결")
                reset_supabase()
                time.sleep(1)
                fetched_since_reset = 0
        print(f"[INFO] 전체 fetch: {len(all_parts)} parts")

        # dedup 안전장치 (PostgREST 페이지네이션 일관성 보강)
        seen_ids = set()
        deduped = []
        for p in all_parts:
            if p['id'] not in seen_ids:
                seen_ids.add(p['id'])
                deduped.append(p)
        if len(deduped) != len(all_parts):
            print(f"[WARN] fetch 중복 제거: {len(all_parts)} → {len(deduped)} "
                  f"({len(all_parts) - len(deduped)} 중복)")
        all_parts = deduped

        article_ids = list({p['article_id'] for p in all_parts if p.get('article_id')})
        article_types = {}
        for i in range(0, len(article_ids), 200):
            chunk = article_ids[i:i + 200]
            def _fetch_a():
                return supabase.from_('law_article').select('id,article_type,law_id,article_text').in_(
                    'id', chunk
                ).execute().data
            res = with_retry(_fetch_a)
            for r in res:
                article_types[r['id']] = (r.get('article_type'), r.get('law_id'), r.get('article_text'))

        target_parts = [
            p for p in all_parts
            if article_types.get(p['article_id'], (None, None, None))[0] == '본칙'
        ]
    elif target_filter == 'kec':
        kec_articles = with_retry(lambda: supabase.from_('law_article').select('id,article_text').eq(
            'law_id', KEC_LAW_ID).execute().data)
        kec_article_ids = {a['id'] for a in kec_articles}
        article_types = {a['id']: (None, KEC_LAW_ID, a.get('article_text')) for a in kec_articles}
        all_parts = []
        for i in range(0, len(kec_article_ids), 200):
            chunk = list(kec_article_ids)[i:i + 200]
            def _fetch():
                return supabase.from_('law_article_part').select(
                    'id,article_id,parent_id,part_text,part_type,depth'
                ).in_('article_id', chunk).order('id').execute().data
            batch = with_retry(_fetch)
            all_parts.extend(batch)
        target_parts = all_parts
    else:
        print(f"[ERROR] unknown target: {target_filter}")
        return

    print(f"[INFO] target parts: {len(target_parts)}")

    if not target_parts:
        print("[INFO] 처리할 parts 없음")
        return

    direct_classification = {}
    for p in target_parts:
        types, rules = classify_text(p.get('part_text') or '')
        if p.get('part_type') == 'proviso' and 'EXCEPTION' not in types:
            types = ['EXCEPTION'] + [t for t in types if t != 'EXCEPTION']
            rules = rules + ['rule:EXCEPTION_part_type_proviso']
        direct_classification[p['id']] = (types, rules)

    article_classification = {}
    for aid, ainfo in article_types.items():
        if len(ainfo) >= 3 and ainfo[2]:
            a_types, a_rules = classify_text(ainfo[2])
            if a_types:
                article_classification[aid] = (a_types, a_rules)

    print(f"[INFO] article 본문 분류된 articles: {len(article_classification)}")

    part_by_id = {p['id']: p for p in target_parts}
    has_child_part = set()
    for p in target_parts:
        if p.get('parent_id'):
            has_child_part.add(p['parent_id'])

    leaf_parts = [p for p in target_parts if p['id'] not in has_child_part]
    print(f"[INFO] leaf parts: {len(leaf_parts)}")

    # null-only 모드: parent가 이미 적용된 part일 수 있어 별도 DB 조회
    applied_parent_class = {}
    if getattr(args, 'null_only', False):
        needed_parent_ids = list({
            p['parent_id'] for p in target_parts
            if p.get('parent_id') and p['parent_id'] not in part_by_id
        })
        print(f"[INFO] null-only: applied parent 조회 대상 {len(needed_parent_ids)}건")
        for i in range(0, len(needed_parent_ids), 200):
            chunk = needed_parent_ids[i:i + 200]
            def _fetch_pp():
                return supabase.from_('law_article_part').select(
                    'id,content_types,primary_content_type,classification_confidence,classified_by_rules'
                ).in_('id', chunk).execute().data
            res = with_retry(_fetch_pp)
            for r in res:
                if r.get('content_types') and r.get('primary_content_type') and r.get('classification_confidence') in ('HIGH','MEDIUM','LOW'):
                    applied_parent_class[r['id']] = (r['content_types'], r.get('classified_by_rules') or [])
        print(f"[INFO] null-only: applied parent 분류 확보 {len(applied_parent_class)}건")

    final_classification = {}
    inherited_count = 0
    inherited_from_article_count = 0
    null_count = 0

    for leaf in leaf_parts:
        leaf_id = leaf['id']
        types, rules = direct_classification[leaf_id]
        if types:
            final_classification[leaf_id] = (types, rules, confidence_level(len(rules), False), 'direct')
            continue

        cur = leaf
        depth = 0
        inherited_types = None
        inherited_rules = None

        while cur and cur.get('parent_id') and depth < 10:
            parent = part_by_id.get(cur['parent_id'])
            if not parent:
                # null-only 모드: 이미 적용된 parent 시도
                if getattr(args, 'null_only', False):
                    ap = applied_parent_class.get(cur['parent_id'])
                    if ap:
                        inherited_types = ap[0]
                        inherited_rules = ap[1] + ['inherited:from_applied_parent_' + cur['parent_id'][:8]]
                break
            ptypes, prules = direct_classification[parent['id']]
            if ptypes:
                inherited_types = ptypes
                inherited_rules = prules + ['inherited:from_part_' + parent['id'][:8]]
                break
            cur = parent
            depth += 1

        if not inherited_types and leaf.get('article_id'):
            a_class = article_classification.get(leaf['article_id'])
            if a_class:
                a_types, a_rules = a_class
                inherited_types = a_types
                inherited_rules = a_rules + ['inherited:from_article_' + leaf['article_id'][:8]]
                inherited_from_article_count += 1

        if inherited_types:
            final_classification[leaf_id] = (inherited_types, inherited_rules, 'LOW', 'inherited')
            inherited_count += 1
        else:
            final_classification[leaf_id] = (None, ['_NULL_NEEDS_REVIEW'], 'NONE', 'null_needs_review')
            null_count += 1

    for p in target_parts:
        if p['id'] in final_classification:
            continue
        types, rules = direct_classification[p['id']]
        if types:
            final_classification[p['id']] = (types, rules, confidence_level(len(rules), False), 'direct')
        else:
            final_classification[p['id']] = (None, ['_NULL_NEEDS_REVIEW'], 'NONE', 'null_internal')

    # 안전장치: 모든 target_parts가 final_classification에 들어갔는지 검증
    expected_count = len(target_parts)
    actual_count = len(final_classification)
    if expected_count != actual_count:
        missing = [p for p in target_parts if p['id'] not in final_classification]
        print(f"\n[CRITICAL] final_classification 누락 발견!")
        print(f"  expected: {expected_count}, actual: {actual_count}, missing: {len(missing)}")
        print(f"  missing sample (5):")
        for m in missing[:5]:
            text = (m.get('part_text') or '')[:100].replace('\n', ' ')
            print(f"    [{m.get('part_type')} d={m.get('depth')}] {text}")
        if not args.dry_run:
            print(f"[CRITICAL] DB update 중단. dry-run으로 원인 진단 필요.")
            sys.exit(1)

    print(f"\n[RESULT]")
    print(f"  - leaf direct: {sum(1 for v in final_classification.values() if v[3] == 'direct')}")
    print(f"  - leaf inherited (parent chain): {inherited_count - inherited_from_article_count}")
    print(f"  - leaf inherited (article 본문 fallback): {inherited_from_article_count}")
    print(f"  - leaf NULL: {null_count}")
    print(f"  - 총 분류 (leaf + internal): {len(final_classification)}")

    if args.dry_run:
        type_dist = defaultdict(int)
        for types, _, _, source in final_classification.values():
            if types:
                type_dist[(primary_type(types), source)] += 1
            else:
                type_dist[(None, source)] += 1
        print("\n[DRY-RUN 분포]")
        for (ptype, source), cnt in sorted(type_dist.items(), key=lambda x: -x[1]):
            print(f"  {source:20} {ptype or 'NULL':25} {cnt}")

        null_leaves = [(lid, part_by_id[lid]) for lid, (t, _, _, s) in final_classification.items()
                       if s == 'null_needs_review' and lid in part_by_id]
        if null_leaves:
            print(f"\n[DRY-RUN NULL leaf sample] (총 {len(null_leaves)}건)")
            for lid, p in null_leaves[:25]:
                pt = p.get('part_type', '')
                text = (p.get('part_text') or '')[:120].replace('\n', ' ')
                print(f"  [{pt}] {text}")
        return

    print(f"\n[UPDATE] law_article_part에 분류 결과 INSERT 중...")
    from datetime import datetime
    now_iso = datetime.now().isoformat()
    updates = []
    for part_id, (types, rules, confidence, source) in final_classification.items():
        updates.append({
            'id': part_id,
            'content_types': types,
            'primary_content_type': primary_type(types) if types else None,
            'classification_confidence': confidence,
            'classified_by_rules': rules,
            'classified_at': now_iso,
        })

    total = update_chunked('law_article_part', updates, chunk_size=50, key_col='id')
    print(f"[DONE] {total}/{len(updates)} parts updated")


def main():
    parser = argparse.ArgumentParser(description="content_type 분류 v3.0")
    parser.add_argument('--target', required=True,
                        choices=['nftc_kds', 'part_general', 'part_bonchik', 'part_kec', 'all'],
                        help='분류 대상')
    parser.add_argument('--dry-run', action='store_true',
                        help='DB 변경 안 하고 분포 + NULL sample 출력')
    parser.add_argument('--reset', action='store_true',
                        help='기존 분류 컬럼 모두 NULL로 초기화 후 재분류')
    parser.add_argument('--null-only', action='store_true',
        help='NULL parts(content_types IS NULL AND classification_confidence IS NULL)만 '
             '재처리. 이미 적용된 분류는 건드리지 않음. v3.0 누락 fix용 우회 모드.')
    args = parser.parse_args()

    if args.null_only and args.reset:
        print("[ERROR] --null-only와 --reset은 동시 사용 불가", file=sys.stderr)
        sys.exit(1)

    if args.reset and not args.dry_run:
        confirm = input(f"WARNING: target={args.target}의 모든 분류 결과 NULL로 초기화. 계속? [y/N] ")
        if confirm.lower() != 'y':
            print("[INFO] 취소")
            return

        if args.target in ('nftc_kds', 'all'):
            print("[RESET] law_article 분류 컬럼 NULL...")
            with_retry(lambda: supabase.from_('law_article').update({
                'content_types': None,
                'primary_content_type': None,
                'classification_confidence': None,
                'classified_by_rules': None,
                'classified_at': None,
            }).not_.is_('content_types', 'null').execute())

        if args.target in ('part_general', 'part_bonchik', 'part_kec', 'all'):
            print("[RESET] law_article_part 분류 컬럼 NULL...")
            with_retry(lambda: supabase.from_('law_article_part').update({
                'content_types': None,
                'primary_content_type': None,
                'classification_confidence': None,
                'classified_by_rules': None,
                'classified_at': None,
            }).not_.is_('content_types', 'null').execute())

    if args.target == 'nftc_kds':
        classify_nftc_kds(args)
    elif args.target == 'part_general':
        classify_parts(args, 'general')
    elif args.target == 'part_bonchik':
        classify_parts(args, 'bonchik')
    elif args.target == 'part_kec':
        classify_parts(args, 'kec')
    elif args.target == 'all':
        classify_nftc_kds(args)
        classify_parts(args, 'general')
        classify_parts(args, 'bonchik')
        classify_parts(args, 'kec')


if __name__ == "__main__":
    main()
