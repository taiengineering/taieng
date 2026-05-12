# HANDOFF_20260504_S11 — KEC 의무 추출 PoC 완료 + 학습 사항

> 본 세션 = 2026-05-03 (S11 시작) → 2026-05-04 (PoC 종결).
> 핵심 결과: KEC 575건 추출, 375 verified, 시스템 검증 완료, 정식 코드 진입 준비됨.

---

## 1. 본 세션 미션 + 결과

### 1.1 시작 상태 (S10 PART2 끝)

- KEC PDF 21.6MB가 "일부개정 부분만"일 거라는 추정 (PART2 § 1)
- KEC 전체 본문 별도 수집 트랙 진입 (PART2 § 4)
- PoC 보류 (PART2 § 6)

### 1.2 S11 핵심 발견 — PART2 § 1 정정

**21.6MB는 사실 "개정 후 KEC 전체 본문" (1234p, 가장 최신).**

근거:
- 사용자 직접 PDF 검증: 첫 페이지 = 개정이력 / 둘째 = 목차 / 본문 시작
- 시점 매칭: `law_number = 2025-227`, `enforcement_date = 2026-01-05`, kec.kea.kr #37 일치
- attachment_title의 "(전기자동차 충전시설)"이 개정 항목 241.17.3, 241.17.5와 일치

→ KEC 전체 본문 별도 수집 트랙 **폐기**.
→ PoC 즉시 진입 가능 → 본 세션 후반 모든 작업.

---

## 2. PoC 진행 + 결과

### 2.1 시스템 작동 검증 ✅

- KEC PDF 1234p → pdfplumber 텍스트 추출 → Gemini 2.5 Pro 의무 추출 (5 청크) → Sonnet 4.6 검증 (38 batch) → CSV 생성
- **575건 의무 추출** (KEC 통칙·접지·고압설비·재생에너지 등 전 영역)
- **375건 verified=True** (Sonnet 명시 통과)
- 모든 단계 캐시화 (재실행 시 비용 0)

### 2.2 비용/시간 데이터

| 항목 | 값 |
|---|---|
| KEC PDF 1건 PoC 누적 비용 | ~$25 |
| 누적 시간 (시도 + 분석) | ~9시간 |
| Gemini 2.5 Pro (KEC 5 chunks) | $1.95 |
| Sonnet 4.6 (38 batch × 평균 2~3회 시도) | ~$23 |

### 2.3 본 미션 추정 (§ 8에서 정정됨, 아래 § 8 참조)

- KEC 1건 정식 코드 효율 가정: ~$5~7
- ~~752 master 평균 사이즈 (KEC의 ~1/100) 가정~~
- ~~추정 총 비용: $200~500~~
- ~~추정 총 시간: 2~3일~~

→ § 8 정정: 본 미션 입력은 **745 law_article + 5 attachment**로 분리됨. 비용 **$75~225**로 더 저렴.

---

## 3. PoC 핵심 학습 (정식 코드 진입 전 필독)

### 3.1 Sonnet broken JSON 문제 (가장 중요)

**현상**: Sonnet이 tool_use 응답에서 verification_note에 escape 안 된 큰따옴표/줄바꿈 → SDK가 string으로 fallback → broken JSON.

**측정**: 26 batch 캐시 / 13 batch 영구 실패. 동일 batch는 재호출해도 똑같이 실패.

**필수 해결책 (정식 코드)**:
```python
# 1) Sonnet 입력에서 obligation_detail 제거 (검증에는 summary + page_no만 필요)
# 2) verification_note 출력 길이 제한 (max 100자, 본문 인용 금지 명시)
# 3) json.loads 실패 시 json_repair.loads fallback
# 4) batch_size 작게 (5~10), 첫 호출 실패 시 batch=1로 자동 retry
# 5) Sonnet 검증 자체 우회 옵션 — Gemini 추출 결과 그대로 사용 + 사람 검토 단계로 위임
```

### 3.2 Gemini chunk 분할 (안정적)

- **Gemini 2.5 Pro 입력 한도 = 1M tokens** (PART2의 "200만"은 1.5 Pro와 혼동된 잘못된 추정)
- 한국어 char당 ~1 token → **350K chars/chunk가 안전**
- KEC 1234p → 5 chunks → 모두 첫 호출 성공
- chunk 1 (~280p)에서 ~100건 추출 → output 22K tokens (정상)

### 3.3 SDK string-wrapping 발견 (Anthropic Python SDK 동작)

- tool_use 응답이 max_tokens 한도 근처일 때 또는 schema validation 부분 실패 시 `block.input["obligations"]`이 list 대신 **string으로 wrap**됨
- string은 valid JSON일 수도, broken JSON일 수도 있음
- **모든 tool_use 응답에서 `isinstance(raw, str)` 체크 필수**

### 3.4 캐싱 패턴 (재사용 가능)

```python
# Gemini chunk: tmp_extracts/chunk_{N}_obligations.json
# Sonnet batch: tmp_extracts/verify_batch_{N}.json
# 재실행 시 자동 hit, 실패 batch만 재호출
```

본 미션에서는 master_id 디렉토리 구조로 확장:
```
cache/{master_id}/chunks/chunk_{N}.json
cache/{master_id}/verify/batch_{N}.json
```

### 3.5 DB schema 불일치 (해결 필수)

**PoC 스크립트가 INSERT하려던 컬럼 vs 실제 `law_rule_drafts` 테이블**:

| 스크립트 | 테이블 | 상태 |
|---|---|---|
| `obligation_summary`, `penalty_summary`, `law_article` | ✅ 존재 | OK |
| `law_id`, `law_version_id`, `source_doc_id`, `source_api`, `is_active`, `verified`, `verification_note`, `applicable_to`, `frequency` | ❌ **9개 컬럼 없음** | **추가 필요** |
| `law_name` (NOT NULL) | ✅ 존재, 스크립트 안 보냄 | **수정 필요** |
| `status` 기본값 | `'PENDING'` | 스크립트는 `'PENDING_REVIEW'` |

→ **본 미션 정식 코드 진입 전 DB migration 필수**:
- 9개 컬럼 추가 (UUID FK + boolean + text)
- `law_name` NOT NULL 제약 처리 (스크립트가 master에서 가져와서 채움)

### 3.6 비용 효율 — Sonnet 검증의 가치 재평가

PoC 결론: Sonnet 검증은 **broken JSON 문제로 신뢰성 낮고 비용 80% 차지**.

**대안 검토**:
1. Gemini만 사용 (검증 없이 모두 PENDING_REVIEW로 적재) — 비용 1/10
2. Sonnet 검증을 의무 N건씩만 샘플링 — 비용 절반
3. Gemini로 추출 + Gemini로 검증 (2-pass with different prompts) — Anthropic API 비용 0

본 미션 시작 시 옵션 검토 권장.

---

## 4. 보존된 자산

### 4.1 GitHub
- `tai-admin/docs/HANDOFF_20260504_S11.md` — 본 핸드오프
- `tai-admin/docs/SCRIPTS/extract_obligations_poc_v2.py` — v2.6 (json_repair 미적용 상태)
- 커밋 이력 8개 (v2.0 → v2.6)

### 4.2 사용자 Mac (`~/dev/tai-poc-kec/`)
- venv + 의존성 (pdfplumber, google-generativeai, anthropic, supabase, json_repair, python-dotenv)
- Railway link (환경변수 자동 주입)
- `extract_obligations_poc.py` (v2.6/v2.7 혼합 상태, 다음 세션에서 정식 재작성)
- `tmp_extracts/`:
  - `64209405-...-pdf` (KEC PDF 21.6MB, 캐시)
  - `chunk_{1..5}_obligations.json` (Gemini 결과 575건)
  - `verify_batch_{1..39}.json` (26개 캐시 — 13개는 broken JSON으로 미캐시)
  - `64209405-..._obligations.csv` (575건 최종 CSV, verified=True/False 혼합)

### 4.3 백업
- `~/Documents/tai_archives/tai_kec_poc_S11_20260504.tar.gz` (17MB)
  - `tmp_extracts/` 전체 + `extract_obligations_poc.py`

---

## 5. 다음 세션 권장 진입점

**S12: 정식 코드 진입 + DB migration**

### 5.1 우선순위

1. **DB schema migration** (Supabase MCP)
   - `law_rule_drafts`에 9개 컬럼 추가
   - `law_name` 기본값 처리 또는 INSERT 시 채우는 로직 결정
2. **PoC 코드 → 정식 코드 재작성** (Cursor)
   - `tai-api/scripts/extract_obligations.py` (정식 위치)
   - 학습 사항 § 3 모두 반영
   - 특히 § 3.1 (broken JSON 문제) 5가지 해결책 중 채택할 것 선택
   - **두 소스 병합 입력 처리** (§ 8 참조)
3. **KEC PoC 캐시 재활용 → 575건 INSERT**
   - 백업에서 verify_batch JSON 26개 + chunk JSON 5개 사용
   - 13건 미검증은 batch=1로 retry 또는 PENDING_REVIEW로 적재
4. **나머지 4 master 진입**: 가스기술기준 2건, 열사용기자재, 무선설비
5. **본 미션** 745 master (law_article 소스)

### 5.2 접근 방식 변경

**PoC에서 했던 sed 패치 + 즉흥 시도 패턴 폐기**.
정식 코드는:
- Cursor에서 처음부터 깔끔히 작성 (200줄+ 안전)
- DEV_RULES 서비스 계층 분리 (router/service/schema 분리)
- 단위 테스트 포함 (Sonnet broken JSON, Gemini chunk 경계 등 edge case)
- pytest로 검증 후 운영

---

## 6. 본 세션 종료 사유 (정직한 기록)

PoC 진행 중 7회 패치 사이클 (v1 → v2.7) 발생. 마지막 v2.7 sed 패치 시도 5회 모두 부분 실패 또는 위치 못 찾음.

근본 원인: **PoC 단계에서 즉흥 sed 패치는 한계.** 코드 상태가 추적 불가능해짐.

**판단**: 더 이상 같은 PoC를 다듬는 것보다 정식 코드로 깔끔히 재작성하는 게 효율적. 본 미션 진입 시점이 됨.

PoC 본 목적 = "추출 가능한가 + 비용/시간 추정 가능한가" → 둘 다 달성.

---

## 7. PART2 정정 + 작업 원칙 추가

### § 1 표 6번 (KEC) 최종 정정
~~"일부개정분만"~~ → **"개정 후 전체 본문 1234p (개정이력+목차+본문, 2026-01-05 시행)"**

### S10 § 8 작업 원칙 추가 (S11 학습)

13. **PoC 단계에서도 sed in-place 패치 5회 이상 누적되면 코드 상태 추적 불가.** 깨끗한 재작성으로 전환.

14. **외부 LLM tool_use 응답은 항상 string fallback 가능성 가정.** json.loads + json_repair.loads 2단계 fallback 필수.

15. **Sonnet broken JSON은 max_tokens 늘려도, batch 줄여도, prompt에 escape 강조해도 완전 해결 안 됨.** verification_note 길이 제한 + 본문 인용 금지 + json_repair fallback 조합이 정답.

16. **DB schema와 스크립트는 같은 PR로 함께 변경.** PoC에서 schema 무시하고 짠 INSERT 로직은 운영에서 100% 실패함.

---

## 8. 본 미션 입력 구조 정정 (세션 마무리 추가, 2026-05-04)

### 8.1 PoC 종료 후 데이터 검증 결과

세션 마지막에 사용자가 정확히 짚음:
> "본 수집이 끝나면 병합을 하고, 이상 있는 부분만 파싱을 다시 하면 되지 않나요?"

이 통찰이 정답이며, 데이터로 검증됨.

### 8.2 752 master 본문 분포 (Supabase 데이터)

```sql
-- 검증 쿼리 결과 (2026-05-04)
SELECT 
  COUNT(*) FILTER (WHERE has_articles AND has_body) AS both,        -- 5건
  COUNT(*) FILTER (WHERE has_articles AND NOT has_body) AS articles_only,  -- 745건
  COUNT(*) FILTER (WHERE NOT has_articles AND has_body) AS body_only,      -- 0건
  COUNT(*) FILTER (WHERE NOT has_articles AND NOT has_body) AS neither     -- 2건
```

| 분류 | 수 | 본문 위치 |
|---|---|---|
| **둘 다 있음** | **5건** | KEC, 가스기술기준 2건, 열사용기자재, 무선설비. `article_count=1` 메타 조항만 있고 진짜 본문은 첨부 PDF |
| **law_article만 있음** | **745건** | law.go.kr 조항이 본문. 32,808 조항 |
| **첨부만 있음** | **0건** | — |
| **둘 다 없음** | **2건** | 추후 확인 필요 |

### 8.3 본 미션 진짜 구조

**수집은 끝남.** 추가 외부 fetch 불필요. 모두 Supabase DB와 Storage에 보유 중.

**본 미션 = 두 소스 병합 → 의무 추출 → 이상 부분만 재파싱:**

```
[A] 본 수집 (병합)
    ├─ 745 master × law_article = 32,808 조항 (의무 추출 대상)
    └─ 5 master × ATTACHMENT_BODY PDF/HWP = 21MB (의무 추출 대상)
    → 통합 입력 큐로 만들기

[B] 1차 의무 추출 + 검증
    └─ 정식 코드 (Cursor) 한 번 돌리면 끝

[C] 이상 부분만 재파싱
    └─ verified=False / API 실패 / Sonnet broken JSON 발생한 master만 재시도
    └─ batch=1 또는 다른 모델로 fallback
    └─ 그래도 안 되면 사람 검토 큐로 보냄
```

### 8.4 비용 추정 정정

§ 2.3에서 "752 master 추정 $200~500"이라고 적었으나, 정확한 분리는:

| 소스 | master 수 | 평균 본문 크기 | 1건 비용 | 합계 |
|---|---|---|---|---|
| **A. law_article (745 master)** | 745 | ~50KB (KEC의 1/400) | ~$0.10~0.30 | **$75~225** |
| **B. attachment (5 master)** | 5 | KEC 21.6MB (1234p), 나머지 84KB~351KB | ~$3~7 | **$15~35** |
| **합계** | 750 | — | — | **$90~260** |

→ § 2.3의 추정 $200~500보다 저렴. KEC가 예외적으로 큰 master고, 나머지 745 law_article master는 모두 KEC의 1/400 수준.

### 8.5 PoC 학습의 적용 범위 명확화

**PoC에서 발견한 broken JSON 문제 (§ 3.1, § 3.3)는 attachment 본문 처리(5 master)에서 발생.**

745 law_article master 입력은:
- 더 작음 (~50KB)
- 이미 구조화된 조항 텍스트 (PDF 파싱 불필요)
- chunk 분할 거의 불필요 (1 chunk로 처리 가능)
- → **broken JSON 위험 낮음**

따라서 745 master 처리는 PoC보다 **훨씬 단순하고 빠름**. PoC는 5 master attachment 처리용 학습이었음.

### 8.6 정식 파이프라인 설계 권장 (S12)

본 미션 정식 코드는 두 입력 처리기가 분리되어야 함:

```python
# 입력 분기
def get_input_for_master(master_id):
    """745 master는 law_article에서, 5 master는 attachment에서 본문 추출."""
    body = get_attachment_body(master_id)
    if body:  # 5 master
        return extract_text_from_pdf_or_hwp(body)
    else:  # 745 master
        return concat_law_articles(master_id)  # 32,808 조항 중 해당 master 것만

# 통합 처리
for master_id in all_750_masters:
    text = get_input_for_master(master_id)
    if not text or text in cache:
        continue
    extract_obligations(text, master_id)  # 동일한 추출 + 검증 로직

# 이상만 재파싱
for master_id in failed_or_low_confidence:
    retry_with_fallback(master_id)  # batch=1, 다른 모델 등
```

---

**S11 완료. S12 진입점 = DB migration → 정식 코드 재작성 (두 소스 병합 처리).**
