#!/usr/bin/env python3
"""
TAI 법령엔진 정정 스크립트 (AI 정정 단계)

needs_review=true drafts 대상 fresh prompt 재추출 → 1차와 비교 → 패턴 발견.

자기 충족 회피 메커니즘:
- 1차 obligations 비공개 (fresh prompt에 노출 안 함)
- article_text만 보고 새로 추출
- 같은 모델·같은 PROMPT지만 1차 결정 anchor 없음 → 부분 분리
- 1차 vs fresh 비교 → 차이가 약점 신호

판정 로직:
- match (target+type 같고 summary substring 50%+ 겹침) → confirmed
- 1차에만 있음 → over_extraction (검토 필요)
- fresh에만 있음 → recall_gap (1차 누락 — 가장 위험!)
- 패턴 누적 → patterns_<set>_<cycle>.json 파일 출력 (rule_patterns.yaml v1.3 후보)

DB 변경:
- match: status 변경 안 함 (draft 유지), needs_review=false
- over_extraction: status 변경 안 함, ai_flags['correction_note']='over_extraction_suspected'
- recall_gap: 새 draft INSERT (cycle 동일, ai_flags['source']='correction_round')

자기 충족 강화 회피:
- 본 스크립트는 rule_patterns.yaml 자동 갱신 안 함
- patterns_xxx.json 출력만 → 사람이 review 후 수동 갱신

실행:
  $ railway run python correct_drafts.py --set SET-003 --cycle 1
  $ railway run python correct_drafts.py --set SET-003 --cycle 1 --dry-run
  $ railway run python correct_drafts.py --set SET-003 --cycle 1 --limit 20

작성: 2026-05-05 (S14 세션)
"""

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import anthropic
except ImportError:
    print("[ERROR] pip install anthropic", file=sys.stderr)
    sys.exit(1)

try:
    from supabase import Client, create_client
except ImportError:
    print("[ERROR] pip install supabase", file=sys.stderr)
    sys.exit(1)


# ============================================================
# 환경변수
# ============================================================
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("SUPABASE_KEY")
)
if not ANTHROPIC_API_KEY:
    print("[ERROR] ANTHROPIC_API_KEY 없음.", file=sys.stderr)
    sys.exit(1)
if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] SUPABASE 환경변수 없음.", file=sys.stderr)
    sys.exit(1)

MODEL = os.environ.get("CORRECT_MODEL", "claude-opus-4-7")
COST_LIMIT_USD = float(os.environ.get("COST_LIMIT_USD", "5.0"))
INPUT_PRICE_PER_MTOK = 15.0
OUTPUT_PRICE_PER_MTOK = 75.0

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
total_cost_usd = 0.0


# ============================================================
# Fresh PROMPT (extract와 동일하나 1차 결과 비공개)
# ============================================================
SYSTEM_PROMPT = """\
당신은 TAI 법령엔진 의무 추출기입니다. 대한민국 법령 조문에서 **현장 적용 의무**만 정확히 추출합니다.

## 핵심 원칙
1. 환각 금지: article_text에 명시적으로 있는 내용만 추출.
2. 다중 의무 분해: 주체 다르면 분해, 동사 다르면 분해. 의심스러우면 분해 (통합은 후처리).
3. 모호하면 추출하고 confidence_in_completeness=medium 표시 (누락 회피).

## SKIP 패턴
- SKIP_001 정의 / SKIP_002 벌칙 / SKIP_003 부칙 / SKIP_004 재검토
- SKIP_005 권한 위임 / SKIP_006 목적 / SKIP_007 적용범위
- SKIP_009 수수료 / SKIP_010 벌칙·과태료 징수 / SKIP_011 준용

## 권한·재량 (의무 아님)
- "할 수 있다", "필요하다고 인정하면" → 추출 안 함
- "하여야 한다", "되어야 한다", "해서는 아니 된다" → 의무

## 출력 (JSON, 코드 펜스 없이)
{
  "obligations": [
    {"obligation_summary": "...", "appointment_target": "...", "obligation_type": "ACTION",
     "sector": "INDUSTRIAL", "ai_reasoning": "...", "ai_confidence": 90}
  ],
  "self_check": {"reasoning": "...", "extracted_count": N,
                 "skipped_paragraphs": ["SKIP_xxx ..."],
                 "confidence_in_completeness": "high|medium|low"}
}

8종 type: ACTION/INSTALL/REPORT/INSPECT/EDUCATION/RECORD/APPOINT/POSSESS
8종 sector: BUILDING/INDUSTRIAL/CONSTRUCTION/CHEMICAL/GAS/ELECTRIC/FIRE/ENV
"""

USER_PROMPT_TEMPLATE = """\
다음 법령 조문에서 의무를 추출하세요.

law_name: {law_name}
article_no: {article_no}
article_title: {article_title}

article_text:
```
{article_text}
```

JSON만 출력 (코드 펜스 없이).
"""


# ============================================================
# 비교 로직
# ============================================================
def normalize_summary(s: str) -> str:
    """비교용 normalize: 가운뎃점, 공백, 구두점 제거."""
    s = re.sub(r"[ㆍ・·]", "·", s)
    s = re.sub(r"[\s,.]+", "", s)
    return s


def summary_overlap_ratio(a: str, b: str) -> float:
    """단순 substring 기반 overlap (0.0~1.0).
    더 정교한 비교는 trigram·embedding 필요 (TODO)."""
    na = normalize_summary(a)
    nb = normalize_summary(b)
    if not na or not nb:
        return 0.0
    shorter, longer = (na, nb) if len(na) <= len(nb) else (nb, na)
    if shorter in longer:
        return len(shorter) / len(longer)
    # n-gram 기반 overlap
    n = 5
    if len(shorter) < n:
        return 0.0
    grams_short = {shorter[i:i + n] for i in range(len(shorter) - n + 1)}
    grams_long = {longer[i:i + n] for i in range(len(longer) - n + 1)}
    if not grams_short:
        return 0.0
    return len(grams_short & grams_long) / len(grams_short)


def match_obligations(orig: List[Dict[str, Any]], fresh: List[Dict[str, Any]],
                      threshold: float = 0.5) -> Dict[str, List[Tuple]]:
    """1차 vs fresh obligations 매칭.
    return: {'match': [(orig_idx, fresh_idx, ratio)], 'orig_only': [...], 'fresh_only': [...]}"""
    n_orig = len(orig)
    n_fresh = len(fresh)
    matched_fresh = set()
    matched_orig = set()
    matches = []

    for i, o in enumerate(orig):
        best_j = -1
        best_ratio = 0.0
        for j, f in enumerate(fresh):
            if j in matched_fresh:
                continue
            # target + type 일치 우선
            if (o.get("appointment_target") == f.get("appointment_target")
                    and o.get("obligation_type") == f.get("obligation_type")):
                ratio = summary_overlap_ratio(o["obligation_summary"], f["obligation_summary"])
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_j = j
        if best_j >= 0 and best_ratio >= threshold:
            matches.append((i, best_j, best_ratio))
            matched_orig.add(i)
            matched_fresh.add(best_j)

    orig_only = [i for i in range(n_orig) if i not in matched_orig]
    fresh_only = [j for j in range(n_fresh) if j not in matched_fresh]
    return {"match": matches, "orig_only": orig_only, "fresh_only": fresh_only}


# ============================================================
# DB 조회·UPDATE
# ============================================================
def fetch_review_articles(set_id: str, cycle: int, limit: int) -> Dict[str, List[Dict[str, Any]]]:
    """needs_review=true drafts를 article 단위로 그룹."""
    res = (
        supabase.table("law_rule_drafts")
        .select("id, article_id, law_name, law_article, article_text, "
                "obligation_summary, appointment_target, obligation_type, sector, "
                "ai_reasoning, ai_confidence, ai_flags, status")
        .eq("ai_flags->>extraction_set", set_id)
        .eq("ai_flags->>extraction_cycle", str(cycle))
        .eq("ai_flags->>needs_review", "true")
        .neq("status", "placeholder")
        .execute()
    )
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for d in res.data:
        if d.get("article_id"):
            grouped[d["article_id"]].append(d)
    # limit articles
    if limit and len(grouped) > limit:
        grouped = dict(list(grouped.items())[:limit])
    return grouped


def fetch_article_meta(article_id: str) -> Optional[Dict[str, Any]]:
    res = (
        supabase.table("law_article")
        .select("id, article_no, article_title, article_text")
        .eq("id", article_id)
        .execute()
    )
    return res.data[0] if res.data else None


def call_fresh_llm(law_name: str, article_no: int, article_title: str, article_text: str
                   ) -> Tuple[Dict[str, Any], float]:
    global total_cost_usd
    if total_cost_usd >= COST_LIMIT_USD:
        raise RuntimeError(f"비용 한도 초과: ${total_cost_usd:.2f}")

    user_msg = USER_PROMPT_TEMPLATE.format(
        law_name=law_name, article_no=article_no,
        article_title=article_title or "", article_text=article_text
    )
    response = client.messages.create(
        model=MODEL, max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n", "", text)
        text = re.sub(r"\n```$", "", text)
    cost = (response.usage.input_tokens / 1_000_000 * INPUT_PRICE_PER_MTOK
            + response.usage.output_tokens / 1_000_000 * OUTPUT_PRICE_PER_MTOK)
    total_cost_usd += cost
    return json.loads(text), cost


def update_confirmed(draft_id: str):
    """match된 1차 draft: needs_review=false, correction_note='confirmed'."""
    res = (
        supabase.table("law_rule_drafts")
        .select("ai_flags").eq("id", draft_id).execute()
    )
    if not res.data:
        return
    flags = res.data[0]["ai_flags"] or {}
    flags["needs_review"] = False
    flags["correction_note"] = "confirmed_by_fresh_round"
    flags["correction_at"] = datetime.now(timezone.utc).isoformat()
    supabase.table("law_rule_drafts").update({
        "ai_flags": flags,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", draft_id).execute()


def mark_over_extraction(draft_id: str):
    """1차에만 있고 fresh에 없음 → over_extraction 의심."""
    res = supabase.table("law_rule_drafts").select("ai_flags").eq("id", draft_id).execute()
    if not res.data:
        return
    flags = res.data[0]["ai_flags"] or {}
    flags["correction_note"] = "over_extraction_suspected"
    flags["needs_review"] = True  # 사람 검토 유지
    supabase.table("law_rule_drafts").update({
        "ai_flags": flags,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", draft_id).execute()


def insert_recall_gap(article_id: str, law_name: str, article_no: int,
                      article_text: str, fresh_ob: Dict[str, Any],
                      fresh_self_check: Dict[str, Any], set_id: str, cycle: int):
    """fresh에만 있고 1차에 없음 → 1차 누락 (recall gap)."""
    flags = {
        "extraction_set": set_id,
        "extraction_cycle": cycle,
        "prompt_version": "v3.0.1",
        "from_pipeline": "correction_round",
        "source": "fresh_round_recall_gap",
        "broken": False,
        "self_check": fresh_self_check,
        "needs_review": True,
        "review_reasons": ["recall_gap_from_correction"],
        "correction_at": datetime.now(timezone.utc).isoformat(),
    }
    row = {
        "law_name": law_name,
        "law_article": f"제{article_no}조",
        "article_id": article_id,
        "article_text": article_text,
        "obligation_summary": fresh_ob["obligation_summary"],
        "appointment_target": fresh_ob["appointment_target"],
        "obligation_type": fresh_ob["obligation_type"],
        "sector": fresh_ob["sector"],
        "ai_reasoning": fresh_ob.get("ai_reasoning", "fresh round 신규 발견"),
        "ai_confidence": fresh_ob.get("ai_confidence", 70),
        "ai_flags": flags,
        "status": "draft",
        "diagnosis_stage": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    supabase.table("law_rule_drafts").insert([row]).execute()


# ============================================================
# 메인
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="TAI 법령엔진 정정 (fresh round)")
    parser.add_argument("--set", dest="set_id", required=True)
    parser.add_argument("--cycle", type=int, default=1)
    parser.add_argument("--limit", type=int, default=0, help="article 수 제한 (0=전체)")
    parser.add_argument("--dry-run", action="store_true",
                        help="DB 변경 없이 비교만 출력")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="match overlap 임계 (기본 0.5)")
    args = parser.parse_args()

    print(f"=== {args.set_id} cycle={args.cycle} 정정 라운드 시작 ===")
    print(f"[INFO] model={MODEL} cost_limit=${COST_LIMIT_USD} threshold={args.threshold}")
    if args.dry_run:
        print("[INFO] dry-run: DB 변경 없음")

    grouped = fetch_review_articles(args.set_id, args.cycle, args.limit)
    print(f"[INFO] 정정 대상 articles: {len(grouped)}")

    summary = {
        "articles": len(grouped),
        "matched_drafts": 0,
        "over_extraction": 0,
        "recall_gaps": 0,
        "patterns": [],
    }

    for i, (article_id, drafts) in enumerate(grouped.items(), 1):
        first = drafts[0]
        law_name = first["law_name"]
        article_no_str = first["law_article"]  # 예: "제96조"
        article_no = int(re.search(r"\d+", article_no_str).group()) if article_no_str else 0

        meta = fetch_article_meta(article_id)
        if not meta:
            print(f"[{i}/{len(grouped)}] {law_name} {article_no_str} - article 없음, skip")
            continue
        article_text = meta["article_text"]
        article_title = meta.get("article_title") or ""

        # 1차 obligations (비교용 — fresh prompt에는 안 보냄)
        orig_obs = [{
            "obligation_summary": d["obligation_summary"],
            "appointment_target": d["appointment_target"],
            "obligation_type": d["obligation_type"],
            "_id": d["id"],
        } for d in drafts]

        # Fresh 호출
        try:
            result, cost = call_fresh_llm(law_name, article_no, article_title, article_text)
            fresh_obs = result.get("obligations", [])
            fresh_self_check = result.get("self_check", {})
        except Exception as e:
            print(f"[{i}/{len(grouped)}] {law_name} {article_no_str} - fresh ERROR {e}", file=sys.stderr)
            continue

        # 비교
        m = match_obligations(orig_obs, fresh_obs, threshold=args.threshold)
        n_match = len(m["match"])
        n_over = len(m["orig_only"])
        n_recall = len(m["fresh_only"])

        marker = "✓" if (n_over == 0 and n_recall == 0) else "⚠️"
        print(f"[{i}/{len(grouped)}] {marker} {law_name} {article_no_str} "
              f"(orig={len(orig_obs)} fresh={len(fresh_obs)}) "
              f"match={n_match} over={n_over} recall_gap={n_recall} (${cost:.4f})")

        # 패턴 누적 (출력용)
        if n_over > 0 or n_recall > 0:
            summary["patterns"].append({
                "article_id": article_id,
                "law_name": law_name,
                "article": article_no_str,
                "orig_count": len(orig_obs),
                "fresh_count": len(fresh_obs),
                "match_count": n_match,
                "over_extraction_indices": m["orig_only"],
                "recall_gap_indices": m["fresh_only"],
                "over_extraction_summaries": [orig_obs[k]["obligation_summary"] for k in m["orig_only"]],
                "recall_gap_summaries": [fresh_obs[k]["obligation_summary"] for k in m["fresh_only"]],
            })

        # DB UPDATE
        if not args.dry_run:
            for o_idx, _, _ in m["match"]:
                update_confirmed(orig_obs[o_idx]["_id"])
            for o_idx in m["orig_only"]:
                mark_over_extraction(orig_obs[o_idx]["_id"])
            for f_idx in m["fresh_only"]:
                insert_recall_gap(article_id, law_name, article_no, article_text,
                                  fresh_obs[f_idx], fresh_self_check, args.set_id, args.cycle)

        summary["matched_drafts"] += n_match
        summary["over_extraction"] += n_over
        summary["recall_gaps"] += n_recall

        time.sleep(0.5)

    # 패턴 파일 출력
    out_path = Path(__file__).parent / f"patterns_{args.set_id}_{args.cycle}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n=== 정정 라운드 완료 ===")
    print(f"[RESULT] articles 처리:    {summary['articles']}")
    print(f"[RESULT] matched (확정):   {summary['matched_drafts']}")
    print(f"[RESULT] over_extraction:  {summary['over_extraction']}")
    print(f"[RESULT] recall_gap:       {summary['recall_gaps']} ⭐ (가장 위험 — 1차 누락)")
    print(f"[RESULT] 패턴 파일:        {out_path}")
    print(f"[RESULT] 총 비용:          ${total_cost_usd:.2f}")
    print(f"\n다음: patterns_{args.set_id}_{args.cycle}.json 검토 -> rule_patterns.yaml 수동 갱신")


if __name__ == "__main__":
    main()
