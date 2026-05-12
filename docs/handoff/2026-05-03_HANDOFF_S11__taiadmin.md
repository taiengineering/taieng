# HANDOFF_20260503_S11 — KEC 출처 + PART2 § 1 정정 + PoC 시도 (실행 미완)

> 본 세션 = S10 PART2 → S11. KEC 전체 본문 별도 수집 트랙 진입 → 검증 결과 PART2 § 1 결론 정정 → PoC 즉시 진입 → Gemini 1M 토큰 초과 → v2 청크 분할 패치 → v2 적용 미확인 → 세션 마무리.

---

## 0. 세션 메타

- 일시: 2026-05-03
- 시작: HANDOFF_20260503_S10_PART2 학습 (KEC 전체 본문 별도 수집 트랙)
- 종료: PoC v2 패치 적용 미확인 상태에서 사용자 세션 마무리 요청
- 진행자: 사용자(심태왕) + Claude (기획창)

---

## 1. 핵심 발견 — PART2 § 1 정정 (매우 중요)

### 1.1 KEC 출처 확정

- **`kec.kea.kr`** (대한전기산업연합회 운영) → "KEC 공고" 게시판 Total 37건
- 최신 #37: 기후에너지환경부 공고 제2025-227호 (시행 2026.01.05, 전기자동차 충전시설)
- 각 공고 첨부 패턴: `[공고문]...74KB.hwp` + `[전문]...수십MB.hwp`
- 다운로드 URL 패턴: `https://kec.kea.kr/bbs_sun/download.v2.php?b_name=report2&bd_number={번호}&seq={첨부순번}`

### 1.2 우리 21.6MB 검증 결과

PART2 § 1이 첨부 제목 패턴만 보고 "[전문] ... 일부개정 전문" → "부분만"이라고 결론 → **잘못된 추정**.

사용자 직접 PDF 검증:
- 첫 페이지: **개정이력**
- 둘째 페이지: **목차**
- **총 1234페이지**, 목차 뒤 본문 시작

→ **개정 후 KEC 전체 본문 확정** ✅

### 1.3 시점 매칭

| 우리 DB | kec.kea.kr #37 |
|---|---|
| `law_number = 2025-227` | 제2025-227호 ✅ |
| `enforcement_date = 2026-01-05` | 시행 2026.01.05 ✅ |
| `attachment_title` 포함 "(전기자동차 충전시설)" | 개정 항목 = 안 241.17.3 + 241.17.5 ✅ |

→ **이미 가장 최신 KEC 전체 본문 보유**. 추가 수집 불필요.

### 1.4 PART2 정정 사항

| 항목 | PART2 결론 | S11 정정 |
|---|---|---|
| § 1 표 6번 KEC 첨부 | ⚠️ "일부개정분만, 전체 본문 아님" | ✅ "전체 본문 1234p (개정이력+목차+본문)" |
| § 4 KEC 전체 본문 별도 수집 트랙 | 추가 진행 | **폐기** |
| § 6 PoC 계획 (KEC PDF 21MB) | 보류 | **부활, 즉시 진입 가능** |
| § 6 "Gemini Pro 200만 토큰" | 단일 호출 가능 | **잘못됨** (1.5 Pro와 혼동, 2.5 Pro = 1M tokens) |

> **S10 § 8 #1 원칙 재확인**: "DELETE/비활성화 등 비가역 작업 전 본문 대조". 첨부 분류도 동일하게 본문 검증 필요. 제목 패턴만 보고 단정 금지.

---

## 2. PoC 시도 — Gemini 토큰 한도 초과로 실행 미완

### 2.1 결정 사항 (사용자)

- 1차 추출: **Gemini 2.5 Pro** (텍스트 입력)
- 2차 검증: **Sonnet 4.6**
- 입력: pdfplumber 텍스트 추출 후 Gemini 호출
- 실행 위치: 사용자 Mac `~/dev/tai-poc-kec`, `railway run`으로 환경변수 주입
- Cursor 작업지시서 폐기 — 사용자 직접 실행 (PoC 단계 빠른 반복)

### 2.2 v1 스크립트 실행 결과

- ✅ Step 1: master + attachment 메타 조회
- ✅ Step 2: PDF 다운로드 (21.6MB, Storage `law-attachments/{master_id}/160132559.pdf`)
- ✅ Step 3: pdfplumber 텍스트 추출
  - **1234 페이지** / **1,555,175 chars** / failed pages (<50 chars) **19/1234** (1.5%)
  - 추출 시간 약 1분 22초
- ❌ Step 4: Gemini 2.5 Pro 호출 **실패**
  ```
  google.api_core.exceptions.InvalidArgument: 400
  The input token count exceeds the maximum number of tokens allowed 1048576.
  ```
  - 원인: **Gemini 2.5 Pro 입력 한도 = 1M 토큰**
  - 우리 입력: 1.55M chars → 한국어 char당 ~1 token이라 1M+ tokens

### 2.3 v2 청크 분할 패치 시도

- 350K chars per chunk → 5 청크 분할 → 청크별 Gemini 호출 → 통합 + (law_article, summary) dedup
- 사용자가 v2 파일 다운로드 → `mv ~/Downloads → ~/dev/tai-poc-kec/` 실행
- **v2 적용 안 됨** — 동일 에러 반복 (트레이스백 line 237, 로그 메시지 v1)
- 원인 추정 (다음 세션 1차 진단):
  1. macOS Downloads `extract_obligations_poc (1).py` 같은 suffix 처리 미스
  2. Python `__pycache__` 잔존
  3. `mv` 실패 또는 다른 파일 위치
- sed 임시 패치 안내 (`{full_text}` → `{full_text[:350000]}`) → 결과 미확인

---

## 3. 다음 세션 진입점 — GitHub raw URL로 v2 즉시 적용

본 핸드오프와 함께 v2 스크립트를 `tai-admin/docs/SCRIPTS/extract_obligations_poc_v2.py`에 보관.

### 3.1 다음 세션 첫 명령 (복사 실행)

```bash
cd ~/dev/tai-poc-kec
source venv/bin/activate

# GitHub raw URL로 v2 직접 다운로드 (Downloads 우회)
curl -fsSL -o extract_obligations_poc.py \
  https://raw.githubusercontent.com/taiengineering/tai-admin/main/docs/SCRIPTS/extract_obligations_poc_v2.py

# v2 적용 검증 (3 이상 출력)
grep -c "split_text_for_gemini\|GEMINI_CHUNK_MAX_CHARS\|chunked" extract_obligations_poc.py

# Python cache 제거
find ~/dev/tai-poc-kec -name __pycache__ -exec rm -rf {} + 2>/dev/null

# 재실행
railway run python3 extract_obligations_poc.py --max-obligations 5 --dry-run
```

### 3.2 v2 정상 작동 시 첫 로그 (확인용)

```
[INFO] Step 4: Gemini extract obligations (chunked)
[INFO] Split into 5 chunks (max_chars=350,000)
[INFO]   Gemini chunk 1/5 — input ~350,500 chars ...
```

이 3줄이 안 나오면 v2 적용 실패. 다음 단계: `head -3 extract_obligations_poc.py`로 v1/v2 직접 확인.

### 3.3 PoC 후속 흐름 (성공 가정)

1. 5건 dry-run → SUMMARY + CSV 검토
2. 품질 OK → `--max-obligations` 제거, 전체 추출 dry-run (~5~10분, ~$2~3)
3. 전체 결과 CSV 검토 → 사용자 결정 → INSERT 실행 (`--dry-run` 제거)
4. 의무 추출 5 master 확대:
   - 가스기술기준 (상세) 30KB
   - 가스기술기준 (액석/도시) 335KB
   - 열사용기자재 100KB
   - 무선설비 80KB
5. 5 master 완료 후 일반 752 master 본 미션 진입 결정

### 3.4 환경 상태 (변동 없음, 내일 그대로 사용 가능)

- 작업 디렉토리: `~/dev/tai-poc-kec` (venv + railway link 완료)
- Railway 환경변수: SUPABASE_URL, SUPABASE_SERVICE_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY ✅
- **KEC PDF 캐시**: `~/dev/tai-poc-kec/tmp_extracts/64209405-1a40-4f0a-aa8a-6f3e55917001.pdf` (이미 다운로드됨, 21.6MB)
  - 다음 세션은 Step 1, 2 즉시 스킵, Step 3 텍스트 추출부터
- 의존성: pdfplumber, google-generativeai, anthropic, supabase, python-dotenv

---

## 4. 본 세션 변경 사항

### 4.1 Supabase

- **임시 (즉시 복원 완료)**:
  - `storage.buckets.public = true` (law-attachments) → 즉시 `false` 복원
  - 임시 RLS 정책 `temp_kec_inspect_20260503` 추가 → 즉시 DROP
- **영구 변경 없음**: 본 세션은 검증 + 출처 조사 위주, DB schema 변경 없음

### 4.2 GitHub

- `tai-admin/docs/HANDOFF_20260503_S11.md` — 본 핸드오프
- `tai-admin/docs/SCRIPTS/extract_obligations_poc_v2.py` — PoC 스크립트 v2 (청크 분할)

### 4.3 KEC PDF 메타 (참조용)

```sql
-- KEC master
id:                 64209405-1a40-4f0a-aa8a-6f3e55917001
law_name:           한국전기설비규정
law_number:         2025-227
announcement_date:  2026-01-05
enforcement_date:   2026-01-05

-- attachment
attachment_type_code: ATTACHMENT_BODY
file_size_bytes:      21,566,439
storage_path:         64209405-1a40-4f0a-aa8a-6f3e55917001/160132559.pdf
attachment_title:     [전문] 2026년 한국전기설비규정 일부개정 전문_제2025-227호(전기자동차 충전시설).pdf
```

---

## 5. 미해결 / 보류 (S10에서 이어짐)

- D_MAPPED 180건 정합성 작업 (의무 추출 본 미션 후 자연 대체 예정)
- 3단계(파싱) 검증 미진입
- 기후위기 탄소중립 시행규칙 누락
- 백업 테이블 11개 정리
- HWP 처리 (가스기술기준 일부 가능성)
- 첨부 본체 회복 외 386건 누락

---

## 6. 작업 원칙 추가 (S10 § 8 + S11)

1~10. (S10 § 8 그대로)

11. **(S11 추가) 첨부 분류도 제목만 보고 단정 금지** — 본문 검증 (첫 페이지/목차) 반드시 수행. 정정 #1 (DELETE 본문 대조)과 동일 패턴.

12. **(S11 추가) 외부 API 토큰 한도는 공식 문서 직접 확인** — PART2의 "Gemini 2.5 Pro 200만 토큰"은 1.5 Pro와 혼동된 잘못된 추정. 실제 2.5 Pro = 1M tokens. 청크 분할 전제로 코드 작성.

---

## 7. 다음 세션 첫 메시지 권장 흐름

```
1. 본 핸드오프 (S11) 학습
2. (선택) PART2 § 1 정정 사항 확인
3. § 3.1 명령 실행: GitHub raw URL로 v2 다운로드 + grep 검증
4. 5건 dry-run 실행
5. SUMMARY + CSV 표본 검토
6. 품질 OK → 전체 추출 / 오추출 다수 → 프롬프트 튜닝
```

**최단 진입**:
> "S11 봤음. § 3.1 명령 실행하고 v2 dry-run."

---

**핸드오프 끝. 다음 세션은 v2 GitHub raw URL 다운로드 + 5건 dry-run부터.**
