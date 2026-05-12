# HANDOFF_20260503_S10_PART2 — PDF 변환 보류 + KEC 전체 본문 별도 트랙 결정

> 본 파일은 `HANDOFF_20260503_S10.md` 의 마지막 추가본.  
> S10 세션 종료 직전 PDF 변환 작업 시작 직전에 발견한 결정적 이슈와 사용자 결정을 기록.

---

## 1. PDF 변환 작업 시작 직전 발견 — 첨부 6건 정체 재검증

PDF 변환·저장 작업 시작 직전, 의무 추출 대상 5 master 의 첨부 6건의 제목을 자세히 분석한 결과 **5/6건이 의무 본문이 아니라 행정 메타 문서**임을 발견.

| # | 법령 | 첨부 제목 | 정체 | 의무 추출 |
|---|---|---|---|:---:|
| 1 | 가스기술기준 (상세) | (양식)조문별제개정이유서_행정규칙 | 🔴 **양식** | ❌ |
| 2 | 가스기술기준 (상세) | 200417-(관보) 가스 상세기준 제·개정안 승인 공고 | 🔴 **공고문** | ❌ |
| 3 | 가스기술기준 (액석/도시) | KGS Code 일부 개정안 항목별 **개정사유** | 🔴 **개정사유서** | ❌ |
| 4 | 열사용기자재 검사 | (양식)조문별제**개정이유서**_열사용기자재 | 🔴 **양식** | ❌ |
| 5 | 전기통신사업용 무선설비 | 조문별제**개정이유서**(전기통신사업용 무선설비) | 🔴 **개정이유서** | ❌ |
| 6 | **KEC** | [전문] 2026년 한국전기설비규정 **일부개정 전문** | ⚠️ "**일부개정**"분만, 전체 본문 아님 | 부분 본문만 |

**사용자 정정 #1과 같은 패턴** — 첨부 제목만 보고 "본체"라 가정한 게 잘못. 내용 검증 없이 진행하면 LLM 비용만 낭비.

---

## 2. 메타 컬럼 NULL 분포 분석

사용자 추정("공고문에 번호들이 있을 거다") 검증 결과:

| 컬럼 | 5건 상태 | 공고문 파싱 가치 |
|---|---|---|
| `law_number` | ✅ 모두 채워짐 (raw_xml에서 추출됨) | 없음 |
| `announcement_date` | ✅ 모두 채워짐 | 없음 |
| `enforcement_date` | ✅ 모두 채워짐 | 없음 |
| `law_name_short` | ❌ 모두 빈 문자열 | 가능 (KEC, KGS Code 등) |
| `domain_code` | ⚠️ 2건 NULL | 가능 (열사용기자재, KEC) |
| `revision_type_code` | ⚠️ 3건 빈 문자열 | 가능 (가스 2건, 무선설비) |
| `source_url` (master/version) | ❌ 모두 NULL | 가능 |
| `remarks` | ❌ 모두 NULL | 가능 |

→ **핵심 메타(법령번호/일자/부처)는 이미 collect 단계에서 raw_xml로 추출됨**. 공고문 파싱으로 새로 얻을 메타는 적음.

---

## 3. 첨부 본체 트랙 가치 재정의

| 트랙 | 가치 |
|---|---|
| 첨부 본체 회복 116건 (450+ 첨부) | KEC 외에는 거의 행정 메타. 의무 추출 가치 낮음 |
| KEC 21MB "일부개정 전문" | 부분 본문 + 개정사유 + 신구대비표 → 의무 추출 가능 |
| **KEC 전체 본문** (통칙·접지·저압·고압·특고압·신재생·전기차) | ❌ **이번 트랙에 없음**. 별도 자료실 (kemc.or.kr 등) |
| 일반 752 master 중 article_text 있는 ~636건 | ✅ **진짜 의무 추출 본 미션**. 가치 압도적 |

**결정적 결론**: 첨부 본체 116건 회복은 유용했지만, 의무 추출 본 미션은 첨부 본체가 아니라 일반 752 master 트랙에서 진행해야 함.

---

## 4. 사용자 결정 — KEC 전체 본문 별도 수집 트랙 추가 (2번)

사용자 명시 결정 (4가지 옵션 중 2번):

> **2. KEC 전체 본문 별도 수집 트랙 추가**

근거:
- KEC는 한국 전기 안전의 핵심 기술기준
- 21MB "일부개정 전문"으로는 통칙·접지·저압·고압·특고압·신재생·전기자동차 등 전체 의무 미수집
- 사용자 기준: "수백 현장이 해야 할 일을 모르고 있는" 정확한 케이스

### 출처 후보 (다음 세션 1차 조사)

1. **한국전기기술인협회 (KEC 공식 자료실)**: `https://www.kecic.or.kr/`
2. **한국전기설비기술기준위원회**: `https://www.kemc.or.kr/`
3. **대한전기협회 KEC**: `https://www.kea.kr/`
4. 또는 산업통상자원부/한국에너지공단 자료실

### 처리 방향 (잠정)

1. 출처 사이트 식별 → 다운로드 URL 수집 (자동 또는 수동)
2. PDF 다운로드 → Supabase Storage `law-attachments/{KEC_master_id}/full_body/` 경로
3. `law_attachment` 신규 row 추가 (`attachment_type_code = 'OFFICIAL_FULL_BODY'` 신규 코드)
4. 텍스트 추출 → `law_article` 채우기 (장/절/조 구조 파싱)
5. 의무 추출 (Gemini Pro + Sonnet 검증)

### 우선순위 영향

- **PDF 변환 작업 (HWP→PDF) 보류** — KEC 전체 본문 확보가 선행
- **5 master 메타 정정** (law_name_short, domain_code, revision_type_code 등) — 짧은 작업이라 다음 세션 곁다리로 처리 가능
- **일반 752 master 트랙 의무 추출** — 첨부 본체 트랙과 병행 또는 후속

---

## 5. 다음 세션 진입점 (수정·최종)

### 5.1 다음 세션 첫 메시지 권장 흐름

```
1. 본 PART2 (HANDOFF_20260503_S10_PART2.md) 학습
2. 본체 (HANDOFF_20260503_S10.md) 학습
3. (선택) 이전 핸드오프들 (S1~S9) 도 빠르게 훑기
4. KEC 전체 본문 출처 조사 (kemc.or.kr / kecic.or.kr / kea.kr 등)
5. 출처 확정 후 수집 스크립트 설계 (또는 사용자 수동 다운로드 → upload_local_attachments 재활용)
6. KEC 전체 본문 → law_article 채우기 (장/절/조 구조 파싱)
7. KEC 의무 추출 PoC (Gemini 2.5 Pro + Sonnet 4.6 검증)
8. (병행 가능) 5 master 메타 컬럼 정정 (law_name_short, domain_code, revision_type_code)
9. 다음 분기: 일반 752 master 의무 추출 본 미션 진입할지 결정
```

### 5.2 다음 세션이 먼저 읽을 핸드오프 위치

**GitHub repo: `taiengineering/tai-admin`, branch: `main`**

```
docs/HANDOFF_20260503_S10_PART2.md    ← 본 PART2 (가장 먼저)
docs/HANDOFF_20260503_S10.md          ← S10 본체 (PART2 다음)
docs/S9_HANDOFF.md                    ← S9 (D_MAPPED 180건 정합성 시작)
docs/HANDOFF_20260503_S8.md           ← S8 (collect_v2 파이프라인 + raw_xml 정착)
docs/HANDOFF_20260503_S7.md           ← S7
docs/HANDOFF_20260503_S6.md           ← S6
docs/HANDOFF_20260502_S5.md           ← S5
docs/HANDOFF_20260502_S4.md           ← S4
docs/HANDOFF_20260502_S3.md           ← S3
docs/HANDOFF_20260502_S2.md           ← S2
docs/HANDOFF_20260502_S1.md           ← S1
```

→ 다음 세션 시작 시 위 경로를 `github-tai-admin:get_file_contents` 로 읽어서 학습. **PART2 → 본체 → S9 순으로 읽으면 가장 효율적**.

### 5.3 스크립트 위치 (`taiengineering/tai-api`, branch: `main`)

```
scripts/diagnose_orphan_rules.py            ← 진단 (read-only)
scripts/judge_orphan_rules.py               ← 의무 패턴 16종 판정
scripts/collect_law_attachments.py          ← 첨부 자동 다운로드 v2 (ASCII-safe path)
scripts/expand_law_zip_attachments.py       ← zip 압축 해제 자동 (사용 안 함, 보존)
scripts/upload_local_attachments.py         ← 로컬 디렉토리 → Storage (KEC 전체 본문 수집 시 재활용 예정)
docs/PRICING_FINAL.md                       ← 가격 정책
docs/DIAGNOSIS_TIER_FINAL.md                ← 진단 등급
docs/DEV_RULES_SERVICE_LAYER.md             ← 개발 규칙
docs/INSPECTION_PRINCIPLES.md               ← 모니터링 원칙
```

### 5.4 다음 세션 첫 SQL (즉시 상태 확인용)

```sql
-- 의무 추출 대상 ATTACHMENT_BODY 6건 (KEC + 4건 행정메타)
SELECT lm.law_name, lat.attachment_title, lat.file_format, lat.file_size_bytes
FROM law_master lm
JOIN law_attachment lat ON lat.law_version_id = lm.current_version_id
WHERE lat.attachment_type_code = 'ATTACHMENT_BODY'
  AND lat.download_status = 'SUCCESS'
ORDER BY lat.file_size_bytes DESC;

-- KEC master 정보
SELECT * FROM law_master WHERE id = '64209405-1a40-4f0a-aa8a-6f3e55917001';

-- 전체 분류 상태
SELECT attachment_type_code, COUNT(*),
       ROUND(SUM(file_size_bytes)::numeric/1024/1024, 1) as mb
FROM law_attachment
WHERE download_status IN ('SUCCESS', 'EXPANDED')
GROUP BY attachment_type_code
ORDER BY mb DESC;
```

### 5.5 다음 세션이 즉시 사용할 핵심 ID/값

- **KEC master_id**: `64209405-1a40-4f0a-aa8a-6f3e55917001`
- **KEC 일부개정 첨부 storage_path**: `64209405-1a40-4f0a-aa8a-6f3e55917001/160132559.pdf` (21.6MB)
- **Supabase project**: `vwlahtguyggrhvslabax` (서울)
- **Supabase Storage 버킷**: `law-attachments` (private)
- **API 키**: GEMINI_API_KEY, ANTHROPIC_API_KEY 모두 Railway 환경변수 등록 확인됨

---

**PART2 끝. 다음 세션은 KEC 전체 본문 수집 트랙부터.**
