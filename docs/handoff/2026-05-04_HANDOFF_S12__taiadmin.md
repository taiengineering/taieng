# S12 핸드오프 — KEC PoC 완료 + 다음 트랙 (4 master PDF 외부 수집)

**작성일**: 2026-05-04
**선행 세션**: S11 (PoC v2.6 — broken JSON 33% 실패) → S12 (PoC v2.7~v2.10 마무리 + drafts INSERT)
**컴팩션 시점**: KEC 575건 INSERT 완료 직후

---

## 1. S12 결과 요약

### 1.1 KEC 1 master 처리 완료
| 단계 | 결과 | 비용 |
|---|---|---|
| Gemini 추출 | 575건 의무 (chunk 5개) | (S11) |
| Sonnet 검증 v2.7 | 497 pass / 78 fail (86.4%) | $1.23 |
| 재검증 v2.8 (ctx prefix) | 542 pass / 33 fail (94.3%) | +$0.51 |
| 재검증 v2.9 (멀티 위치) | 566 pass / 9 fail (98.4%) | +$0.37 |
| 재검증 v2.10 (batch=1) | 570 pass / 5 fail (99.1%) | +$0.20 |
| **drafts INSERT** | **575/575 건 (570 PENDING + 5 NEEDS_REVIEW)** | $0 |
| **합계** | **99.1% verified, broken JSON 0%** | **$2.31** |

### 1.2 운영 적재 (active) 미완
- (가) 의도 = "원본 데이터 보존만 우선"
- 정규화 컬럼 (sector, condition_code, obligation_type 등) 모두 NULL
- 운영 active 진입은 별도 트랙 (자동 정규화 알고리즘 결정 후, § 6 참고)

---

## 2. PoC 학습 (v2.7~v2.10) — 4 master / 745 master에 재사용

### 2.1 v2.7: broken JSON 해결 (4가지 보강)
- Sonnet 입력에서 `obligation_detail`/`applicable_to`/`frequency`/`penalty_summary` 제거 (출력 길이 압박 해소)
- `verification_note` maxLength 100자 + 따옴표/줄바꿈/백슬래시 금지 (system + tool schema 양쪽)
- `json_repair` fallback
- batch 실패 시 batch=1 자동 retry
- **결과**: broken 33% → 0%

### 2.2 v2.8: ctx 추출 부정확 해결
- v2.7 page_no 기반 ctx → `law_article` prefix 기반 검색
- prefix 단계별 fallback (4단계 → 3단계 → 2단계)
- 발견 위치 ±5000 chars
- 의무별 ctx 분리
- **결과**: fail 78 → 33 (회복률 58%)

### 2.3 v2.9: 멀티 위치 ctx
- `find()` 첫 위치만 → 최대 3개 발견 위치 모두 (목차 + 본문 양쪽)
- 위치별 ±2000 chars, `=====` 구분자
- system prompt에 "목차/본문 양쪽 ctx 가능" 가이드
- **결과**: fail 33 → 9 (회복률 73%)

### 2.4 v2.10: batch=1 (ctx truncate 회피)
- v2.9 코드 import + `BATCH_SIZE=1` wrapper (5줄)
- 의무당 ctx 단독 확보 → 50KB truncate 우회
- **결과**: fail 9 → 5 (회복률 44%)

### 2.5 ★ 핵심 학습 — 다음 master에 반드시 적용

1. **Gemini의 page_no는 신뢰 금지** — KEC에서 page_no 16/16 부정확
2. **본문은 hierarchical 표기** (예: KEC `241.17.2` 헤더 + `가. ~~~` 항목)
3. **Gemini는 합성 점번호 생성** (`241.17.2.가`). 본문에 그 문자열 없어도 환각 아님
4. **점번호는 목차 + 본문 두 곳 등장**. find() 첫 위치만 쓰면 목차 잡힘
5. **system prompt 가이드 필수**:
   - "헤더만 있고 하위 항목(가/나/다) ctx 범위 밖이면 verified=True 유지"
   - "verification_note 100자, 따옴표/줄바꿈/백슬래시 금지"

### 2.6 PoC vs 본 미션 — 코드 작성 원칙
- v2.7~v2.10 단계별 새 파일이라 추적 가능 (sed in-place patch 누적이 아님)
- **그러나 4 master / 745 master 본 미션은 정식 코드(Cursor)로 처음부터 깔끔히** 작성 권장
- 본 PoC는 reference 자료. 본 코드는 v2.7~v2.10 학습 반영한 단일 파일.

---

## 3. 작업 파일 인벤토리

### 3.1 GitHub: `taiengineering/tai-admin/docs/SCRIPTS/`
| 파일 | 용도 | 4 master에 재사용? |
|---|---|---|
| `extract_obligations_poc_v2_7.py` | 전체 파이프라인 (download→extract→Gemini→Sonnet) | ✅ 베이스 |
| `verify_only_v2_7.py` | verify 단독 (chunk cache 활용) | △ 디버깅용 |
| `verify_fails_v2_8.py` | ctx prefix 기반 재검증 | ✅ 로직 통합 |
| `verify_fails_v2_9.py` | 멀티 위치 ctx 재검증 | ✅ 로직 통합 |
| `diagnose_fails_v2_7.py` | fail 환각 vs false negative 진단 | ✅ quality 점검용 |
| `diagnose_pdf_quality_v2_7.py` | PDF 추출 품질 + 점번호 표기 변형 진단 | ✅ master 진단 |
| `analyze_kec_cache.py` | cache 진단 | △ 디버깅용 |
| `insert_kec_to_drafts.py` | verified CSV → drafts INSERT | ✅ 마지막 단계 |

### 3.2 대표님 로컬 (`~/dev/tai-poc-kec/`)
| 파일/디렉토리 | 비고 |
|---|---|
| `venv/` | Python 3.14 + anthropic + supabase + pdfplumber + dotenv + json_repair |
| `*.py` (위 GitHub 동기화) | heredoc로 저장됨 |
| `tmp_extracts/` | KEC cache (PDF + chunks + verify_batch_*.json + CSV) |
| `tmp_verify/` | 4 master PDF 검증용 (S12 § 4.1 검증 결과) |

### 3.3 Cache 구조 (`tmp_extracts/`)
| 파일 패턴 | 용도 |
|---|---|
| `{master_id}.pdf` | PDF 원본 cache (재실행 시 다운로드 skip) |
| `chunk_{1~5}_obligations.json` | Gemini 추출 의무 chunk별 |
| `verify_batch_{1~N}.json` | Sonnet 검증 batch별 (cache hit으로 비용 절감) |
| `{master_id}_verified_v2_{7~10}.csv` | 단계별 통합 결과 |

### 3.4 환경 설정
- 환경변수 주입: **`railway run python3 ...`** (.env 없음, Railway link 활용)
- 작업 디렉토리: 반드시 `cd ~/dev/tai-poc-kec` 후 실행 (load_dotenv + cache 경로)

---

## 4. 다음 트랙 B — 4 master 외부 PDF 수집

### 4.1 4 master 정보 + ATTACHMENT_BODY 검증 결과 (DB 확정)

#### 4 master 메타
| Master | law_number | 부처 | master_id |
|---|---|---|---|
| **가스기술기준 #1** (고압+LP+도시) | 2020-271 | 산업통상자원부 | `93f3b603-9c17-4a3d-a5a8-fef0c7dd42be` |
| **가스기술기준 #2** (LP+도시) | 2020-168 | 산업통상자원부 | `4db2c77a-b32b-47ed-ad0b-8da867490878` |
| **열사용기자재 검사·면제 기준** | 2024-184 | 산업통상자원부 | `cf52bb1c-2bd8-46e1-87a1-ecabef5a5cb6` |
| **전기통신사업용 무선설비 기술기준** | 2023-22 | 국립전파연구원 | `a7b2021e-e211-423d-90ec-c1dfd633f5f6` |

각 master의 `article_count = 1` (메타 1건만, 본문 없음).

#### ATTACHMENT_BODY 5건 검증 (S12에서 직접 PDF 열람 확인)
**모두 다운로드 받았으나 본문 0건. 100% 개정공고/이유서.**

| Master | filename | 크기 | 페이지 | 첫 페이지 헤더 | source_url |
|---|---|---|---|---|---|
| 가스 #1 | `200417-(관보) 가스 상세기준 제·개정안 승인 공고.hwp` | 17KB | - | 관보 승인 공고 | http://law.go.kr/flDownload.do?flSeq=64744251 |
| 가스 #1 | `(양식)조문별제개정이유서_행정규칙(2020-271호).hwp` | 14KB | - | 개정이유서 | http://law.go.kr/flDownload.do?flSeq=64744253 |
| 가스 #2 | `KGS Code 일부 개정안 항목별 개정사유 (제2020-168호).pdf` | 351KB | 24p | "KGS Code 일부 개정안 항목별 개정사유" | http://law.go.kr/flDownload.do?flSeq=73776667 |
| 열사용 | `(양식)조문별제개정이유서_열사용기자재 검사 및 검사면제에 관한 기준.pdf` | 105KB | 1p | "조문별 제·개정이유서" + 주요내용 가~사 | http://law.go.kr/flDownload.do?flSeq=145961535 |
| 무선 | `조문별제개정이유서(전기통신사업용 무선설비의 기술기준).pdf` | 85KB | 1p | "조문별 제·개정이유서" + 5G 부합화 | http://law.go.kr/flDownload.do?flSeq=135252485 |

**비교 (KEC vs 4 master)**: KEC 1 ATTACHMENT_BODY = 21.6MB / 1234p (본문) vs 4 master 5건 합계 = 0.55MB / 4 master는 외부 별도 수집 필수.

source_url은 모두 `law.go.kr` 행정규칙 첨부파일 시스템(공고/이유서만 등록). 본문은 별도 시스템에 있음.

### 4.2 외부 PDF 수집 후보 URL

**가스 #1 (2020-271), 가스 #2 (2020-168)** (산업통상자원부 고시):
- 1순위: KGS 가스기술기준위원회 — https://www.kgscode.or.kr (가스 KGS Code 검색 → FU/FP/FS/FC/FD/FE/FT 등 전체 코드)
- 2순위: 법제처 국가법령정보센터 — https://www.law.go.kr (행정규칙 검색, 본문 게시 페이지)
- 3순위: 산업통상자원부 — https://www.motie.go.kr (고시 검색)

**열사용기자재** (2024-184):
- 1순위: 한국에너지공단 (KEA) — https://www.energy.or.kr
- 2순위: 산업통상자원부 — https://www.motie.go.kr
- 3순위: 법제처 — https://www.law.go.kr/LSW/admRulLsInfoP.do (본문 게시 페이지)

**무선설비 기술기준** (2023-22):
- 1순위: 국립전파연구원 — https://www.rra.go.kr (자료실 → 고시)
- 2순위: 과학기술정보통신부 — https://www.msit.go.kr
- 3순위: 법제처 — https://www.law.go.kr (본문 게시 페이지)

### 4.3 수집 절차 (각 master당)
1. 외부 사이트에서 PDF 수동 다운로드 (위 1순위 → 안 되면 2순위 → 3순위)
2. Supabase storage `law-attachments` 버킷에 업로드 (`{master_id}/body_{filename}.pdf`)
3. `law_attachment` 테이블에 메타 INSERT (`attachment_type_code='ATTACHMENT_BODY'`, `storage_path`, `file_size_bytes`, `attachment_title`)
4. PoC 파이프라인 적용 — `extract_obligations_poc_v2_7.py` 베이스 + v2.8/v2.9/v2.10 로직 통합한 새 단일 파일
5. CSV → drafts INSERT (`insert_kec_to_drafts.py` 응용, master_id/version_id/article_id/law_name 변경)

### 4.4 master별 점번호 형식 (system prompt 조정 필요)

| Master | 점번호 형식 예시 |
|---|---|
| KEC | hierarchical (`241.17.2.가`) |
| 가스 #1, #2 | KGS Code 형식 (예: `FU211 1.7.1.1`, `1.7.1.1` 등) |
| 열사용 | 별표 형식 (예: `[별표 1] 1.가`, `제3조 ②` 등) |
| 무선 | 조항 번호 (예: `제3조 제2항`, `제5조의2`) |

→ extract_obligations_poc 작성 시 master별 system prompt 가이드 추가 필요.
→ ctx 추출 함수 (`find_ctx_v2_9`)도 점번호 형식 따라 prefix 분할 로직 조정 가능.

### 4.5 작업 우선순위 (권장)
1. **무선설비** — 가장 단순, 분량 작음, 조항 번호 형식 익숙
2. **열사용기자재** — 별표 형식 학습 (745 master에 별표 패턴 다수)
3. **가스 #2** (LP+도시) — KGS Code 형식 첫 적용
4. **가스 #1** (고압+LP+도시) — 가스 #2 학습 후 (가장 큰 분량)

### 4.6 KEC quality 보장 (4 master 작업 시 동일 검증)
- broken JSON 0%
- false negative 5% 이하 (KEC = 0.9%)
- prefix 발견율 100% (진짜 환각 식별 가능)
- 비용 ≤ $3 / master

### 4.7 PoC 파일 → 4 master 적용 매핑

#### 단계별 사용 파일

| 단계 | KEC에서 사용한 파일 | 4 master에서 |
|---|---|---|
| 1. PDF 다운로드 + Gemini 추출 + Sonnet 검증 | `extract_obligations_poc_v2_7.py` | 새 단일 파일 작성 권장 (Cursor) |
| 2. PDF 추출 품질 진단 | `diagnose_pdf_quality_v2_7.py` | CSV path만 변경 후 재사용 |
| 3. fail 환각 진단 | `diagnose_fails_v2_7.py` | CSV path만 변경 후 재사용 |
| 4. ctx prefix 재검증 (v2.8) | `verify_fails_v2_8.py` | 새 파일에 로직 통합 권장 |
| 5. 멀티 위치 ctx (v2.9) | `verify_fails_v2_9.py` | 새 파일에 로직 통합 권장 |
| 6. batch=1 wrapper (v2.10) | (5줄 wrapper) | 동일 |
| 7. drafts INSERT | `insert_kec_to_drafts.py` | 상수 5개 변경 후 재사용 |

#### insert_*_to_drafts.py 상수 변경 가이드 (master당)

```python
# 무선설비 예시
KEC_MASTER_ID  → "a7b2021e-e211-423d-90ec-c1dfd633f5f6"
KEC_VERSION_ID → 외부 수집 후 DB 조회로 확인
KEC_ARTICLE_ID → 외부 수집 후 DB 조회로 확인
KEC_LAW_NAME   → "전기통신사업용 무선설비의 기술기준"
SOURCE_API     → "gemini_pro_poc_v2_10"  # 그대로 유지 가능
```

#### 새 단일 파일 (Cursor 작성) 작성 가이드

PoC v2.7~v2.10에서 분리된 4개 단계를 하나로 통합:

```
extract_master.py
├─ 1. PDF cache (storage 다운로드, file 캐시)
├─ 2. PDF 텍스트 추출 (pdfplumber, [PAGE N] 마커)
├─ 3. Gemini chunk 분할 추출 (master별 점번호 형식 system prompt)
├─ 4. Sonnet 검증 (v2.7 4가지 보강 + v2.8 ctx prefix + v2.9 멀티 위치)
└─ 5. 출력 CSV (page_no, law_article, summary, detail, applicable_to, 
                frequency, penalty_summary, verified, verification_note)
```

verify는 자동으로 batch=1 fallback 포함. 처음부터 batch=1로 가도 됨 (느리지만 안전).

#### 4 master 추출 후 INSERT 시 ai_flags 메타

KEC와 동일 패턴 + master별 식별:
```json
{
  "master_id": "<master_uuid>",
  "law_number": "2023-22",
  "page_no": <int>,
  "applicable_to": "...",
  "frequency": "...",
  "verified": <bool>,
  "verification_note": "...",
  "source_api": "gemini_pro_v2_10_4master",
  "extracted_at": "2026-05-04",
  "external_source": "rra.go.kr"
}
```

---

## 5. 참고: 다음 트랙 C — 745 master × 32,808 article

### 5.1 진짜 본 미션
- 4 master는 학습용 (점번호 형식 다양화, 외부 수집 경험)
- 745 master는 본 작업 (현재 추출 0%)

### 5.2 단순화 가능
- `article_text`에 이미 구조화 본문 존재 → PDF 다운로드 + pdfplumber 단계 불필요
- chunk 분할도 단순 (article 단위로 자연 분할)
- v2.7~v2.10 보강 그대로 적용 가능 + 단순화

### 5.3 추정
- 비용 $75~225, 시간 5~10시간
- 주요 비용은 Gemini 추출 (article 32,808 × 평균 길이) + Sonnet 검증

---

## 6. 미결정 사항 — 자동 정규화 알고리즘

(가) 의도로 drafts INSERT 575건 끝. 운영 active 적재까지 가려면 **자연어 → 코드값** 자동 정규화 필수.

후보 (사람 검수 불가 결정 후):
| # | 방식 | 핵심 |
|---|---|---|
| C1 | LLM 단독 | Sonnet으로 sector/condition_code/obligation_type 결정 |
| C2 | 규칙기반 + LLM 하이브리드 | 키워드 사전 + 모호한 부분만 LLM |
| C3 | few-shot from active 2,002건 | 운영 룰을 LLM 학습 자료로 |
| C4 | LLM-A 변환 + LLM-B 검증 | 셀프체크 (비용 2배) |
| C5 | 단계 분리 | drafts에 article 매칭만 자동, 정규화는 별도 cron |

**결정 시점**: KEC 575 + 4 master + 745 master 모두 추출/적재 끝난 후 한 번에 결정. 745 master에서 다시 결정하지 않게.

---

## 7. 환경 / 도구 / 한계 (다음 세션 진입용)

### 7.1 작업 환경
- macOS, Python 3.14 venv (~/dev/tai-poc-kec/venv)
- 환경변수: `railway run python3 ...`
- json_repair 0.59.5 설치됨

### 7.2 GitHub MCP 한계 (S12 학습)
- 대표님 Mac에 tai-admin clone 없음
- raw URL/curl/pbpaste 모두 실패 사례 있음 (private repo token 만료)
- **가장 안정**: heredoc 통째 (`cat > file <<'PYEOF' ... PYEOF`)
- 12KB 코드까지 답변 한 번에 가능, 31KB는 분할 또는 wrapper 패턴
- v2.10이 그 예시 (5줄짜리 import wrapper로 v2.9 재사용)

### 7.3 Supabase 정보
- project: `vwlahtguyggrhvslabax` (서울)
- 버킷: `law-attachments` (KEC 21.6MB 포함)
- KEC drafts 575건 적재 완료
  - status=PENDING: 570
  - status=NEEDS_REVIEW: 5

### 7.4 PoC 단계 누적의 ROI
- v2.6 → v2.7 → v2.8 → v2.9 → v2.10 = broken 33% → 0%, fail 78 → 5 (94% 회복)
- 누적 비용 $2.31, 시간 ~30분
- **ROI 매우 높음**. 단 누적 5단계가 한계 — 그 이상은 본 미션 진입이 늦어짐
- KEC 미해결 5건은 환각 의심 큐로 보존 (NEEDS_REVIEW). 향후 v2.11(PyMuPDF)로 시도 가능

---

## 8. 다음 세션 시작 시 결정 사항

### 8.1 즉시 결정
1. **다음 master 작업 시작**: 무선 / 열사용 / 가스 #2 / 가스 #1 중 어느 것부터?
2. **외부 PDF 다운로드 방식**: 수동 다운로드 후 Supabase 업로드 / 자동 스크립트 (URL 확정 후)
3. **추출 코드 작성 방식**:
   - (a) `extract_obligations_poc_v2_7.py` 응용 (PoC 누적 패턴 계속)
   - (b) **Cursor에서 정식 코드 처음부터 깔끔히** (권장 — § 2.6)
   - (c) Claude Code

### 8.2 작업 시 의식할 것
- 매 master에서 PDF 추출 품질 진단 먼저 (`diagnose_pdf_quality_v2_7.py` 응용)
- master별 점번호 형식에 맞는 system prompt 조정
- v2.7~v2.10의 4가지 보강은 기본 탑재
- "한 건 놓치면 점검 안 함" 원칙 — fail 진단 + ctx 보강은 끝까지

---

## 9. 참고 commit (S12 작업 history)

| Commit | 내용 |
|---|---|
| `5a6d76e` | extract_obligations_poc_v2_7.py |
| `c4491f5` | verify_only_v2_7.py |
| `b0ab53a` | diagnose_fails_v2_7.py |
| `8f906a5` | diagnose_pdf_quality_v2_7.py |
| `5e14aff` | verify_fails_v2_8.py |
| `6d0c352` | verify_fails_v2_9.py |
| `18b9181` | insert_kec_to_drafts.py |
| `9d93ade` | 핸드오프 v1 |
| (이번) | 핸드오프 v2 — § 4.1 PDF 검증 결과 + § 4.7 PoC 파일 매핑 |

모두 `taiengineering/tai-admin/docs/SCRIPTS/` 또는 `docs/HANDOFF_*` 경로.
