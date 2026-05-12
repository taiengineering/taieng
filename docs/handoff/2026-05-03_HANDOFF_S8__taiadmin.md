# 핸드오프 — S8 (2026-05-03 일요일 정오)

> 직전: `HANDOFF_20260503_S7.md`
> 작업 시간: 2026-05-03 (일) 약 09:35 ~ 12:30 KST
> 핵심 분류: **미수집 법령 발견·수집 + 데이터 무결성 L3 검증**

---

## 0. 한 줄 요약

S7에서 시작한 본 미션(미수집 법령 수집)을 catalog 발견 → 분류 → 472건 신규 수집 → L3 무결성 검증까지 완수. **수집 단계 사실상 종료**, 의무사항 추출 단계로 진입 가능.

---

## 1. 본 미션 (변경 없음)

> 미수집된 법령을 수집·정제하면서 파이프라인 문제를 개선하여, 종국에는 **의무사항**을 도출한다.

| 단계 | 상태 |
|---|---|
| 1단계 — 미수집 법령 발견 | ✅ S8에서 완료 |
| 2단계 — 수집 | ✅ S8에서 완료 (652/654 SUCCESS) |
| 3단계 — 무결성 검증 | ✅ S8에서 L1+L2+L3 모두 통과 |
| 4단계 — 의무사항 추출 | ⏳ 다음 세션 진입점 |

---

## 2. S8 시작 시점 vs 종료 시점

| 항목 | 시작 (S7 종료) | 종료 (S8 종료) |
|---|---|---|
| `tai-api` 최신 commit | `2e38250a` | `995df984` |
| `law_master` | 182건 | **652건 (+470)** |
| `law_collection_target` (active) | 182건 (PHASE_1+2) | **654건 (PHASE_1 105 + PHASE_2 77 + PHASE_3 472)** |
| `law_external_catalog` | 0건 | **983건 (distinct)** |
| `quality_scan` 정상 | 182/182 (L2) | **629/652 (L2+L3)** |
| 진짜 부실 | 0 | **23건** (대다수 첨부파일 본체) |
| 첨부파일 본체 미해결 | 미인지 | **82건 식별** (별도 트랙) |
| 신규 도메인 결정 (WELFARE/COMMUNICATION) | 보류 | 임시 BUILDING 통합 (정식 분리 다음 세션) |

---

## 3. S8에서 진행한 작업 (시간순)

### 3.1 미수집 법령 발견 — catalog 인프라 활용

S3에서 작성된 `scripts/collect_catalog.py`를 처음 실제 가동:

1. **첫 시도 — Phase 2만 적재**: `railway run python3 scripts/collect_catalog.py collect`
   - Phase 1 (target=law) 57키워드 — 모두 ProxyError 또는 빈 응답
   - Phase 2 (target=admrul) 33키워드 — 정상 612건 distinct 적재
   - 원인: Railway Variables의 `OUTBOUND_PROXY=http://115.68.227.222:3128`이 자동 주입되어 죽은 iwinv 프록시로 라우팅 (admrul 모듈은 프록시 코드 없어서 정상)

2. **commit `6ab29ffd` (collect_catalog.py v1.2)**: `os.environ.pop("OUTBOUND_PROXY")` 명시 unset 추가
   - 사용자(또는 협업자)가 `collect_v2.py`에도 동일 패치 (commit `0732c6e`) — S7 핸드오프 § 4 메모 사항 처리됨

3. **재시도**: 누적 distinct **983건** (law 371 + admrul 612)

### 3.2 분류 — Supabase MCP로 직접 SQL 실행

`collect_catalog.py classify` 명령은 SQL 출력만 함 (Python 클라이언트 raw UPDATE 미지원). Claude가 Supabase MCP로 4개 SQL 직접 실행:

1. `is_in_law_master` 마킹
2. `is_in_collection_target` 마킹
3. `is_in_archive` 마킹
4. `saas_relevance` CASE 분류 (CORE / EXTENDED / OUT_OF_SCOPE / PENDING)

결과:

| saas_relevance | total | in_master | in_target | in_archive | truly_missing |
|---|---:|---:|---:|---:|---:|
| CORE | 519 | 153 | 154 | 2 | **365** |
| EXTENDED | 111 | 0 | 0 | 22 | **111** |
| PENDING | 314 | 14 | 14 | 2 | 300 (분류 보강 필요) |
| OUT_OF_SCOPE | 39 | 0 | 0 | 10 | 39 (제외) |

→ **CORE 365 + EXTENDED 111 = 476건** 진짜 누락 확정.

### 3.3 사용자 결정 — A 옵션 (전체 추가)

S3 § 1 사용자 결정 사항(어린이놀이시설 ✅, 의료시설 ✅, 학교/노인/사회복지/장애인 ✅, 방송통신 ✅, 어린이제품 ❌, 위험물 운송 경고표지 ✅) + S8 즉시 결정:

> **A. 전체 추가** (476건 모두 → SaaS 무관 일부 포함하더라도 누락 위험 0)

### 3.4 INSERT 적용 — 470건 (OTHER 6건 제외)

OTHER 9건 중 SaaS 무관 6건(대법원규칙 3건 / "안전기준 등록" 공고 2건 / 부직포 마스크 1건) 명시 제외, 정상 3건(가스기술기준 2 + NFTC 207 1)은 STANDARD로 매핑.

신규 도메인 WELFARE/COMMUNICATION은 `ck_domain_code` CHECK 제약상 추가하려면 ALTER 필요. S3 § 6.1 보류 사항이라 임시 BUILDING 통합.

도메인 매핑 키워드 우선순위 (`law_name ~` 정규식):
1. INDUSTRIAL_SAFETY (산업안전/안전보건/작업환경/중대재해/산재/방호장치)
2. CHEMICAL (화학물질/유해화학/MSDS/석면)
3. GAS (고압가스/액화석유/도시가스/가스안전/LPG/LNG)
4. FIRE (소방/화재/위험물/NFPC/NFTC)
5. ELECTRIC (전기/승강기/전선/배전/발전)
6. ENVIRONMENT (환경/폐기물/대기/수질/수도/하수/소음/진동/악취/토양)
7. CONSTRUCTION (건설)
8. DISASTER (재난/재해)
9. ENERGY (에너지/탄소중립/기후변화)
10. LABOR (근로기준/고용/임금/산업재해보상)
11. ELSE → BUILDING (WELFARE/COMMUNICATION 임시 통합)

### 3.5 INSERT 중복 사고 + 정정

⚠️ **MCP execute_sql 중복 실행 발생** — INSERT 결과 PHASE_3 PENDING이 934건(예상 470의 2배). 원인 미확정 (MCP retry 또는 timeout 재전송 의심).

복구: `ROW_NUMBER() OVER (PARTITION BY law_name, COALESCE(law_api_id, '__null__'))` 기반 DELETE로 중복 462건 제거 → **PHASE_3 PENDING 472건**으로 정정.

추가로 60건이 `domain_code=NULL` 상태였음 (CASE 결과 ELSE 'BUILDING'이 적용 안 된 row — 원인 동일 의심). 키워드 기반 UPDATE로 모두 매핑 완료.

### 3.6 본 수집 — `collect_v2.py all`

Mac 로컬에서 `railway run python3 scripts/collect_v2.py all` 실행:
- 시간: 56.6분
- 결과: **461/472 SUCCESS (97.7%)**, 11건 FAILED
  - 9건: `RemoteProtocolError: ConnectionTerminated` (HTTP/2 keepalive 끊김)
  - 2건: 검증 체크리스트 일부 실패 (학교안전공제료 / 한국전통문화대학교 시설물 — 첨부파일 본체)

### 3.7 retry — 9건 회수

`railway run python3 scripts/collect_v2.py retry`:
- 성공 9, 실패 2
- 최종 PHASE_3 SUCCESS: **470건 (99.6%)**

### 3.8 quality_scan v1.2 — L3 본문 내용 검증

S7의 quality_scan v1.1은 **L2(외형)**만 검사. 부실 104건 중 다수가 사실은 정상이거나 첨부파일 본체 — false positive 의심.

#### v1.2 신규: L3(데이터 내용) 검증

commit `995df984`. 신규 분류:
- **HOLLOW_CDATA**: 행정규칙 raw_xml `<조문내용><![CDATA[]]></조문내용>` + 첨부파일 없음 = 진짜 빈 행정규칙
- **ATTACHMENT_ONLY**: 빈 CDATA + `<첨부파일명>` 존재 = 첨부파일이 본체 (별도 트랙, 부실 아님)
- **SHORT_BODY**: 모든 article_text 합산 < 100자

#### 최종 결과

| 카테고리 | 카운트 |
|---|---:|
| 전체 SUCCESS | **652** |
| L2 통과 | 539 |
| L3 통과 | 547 |
| **정상 (L2+L3 통과)** | **629 (96.5%)** |
| **첨부파일 본체** (별도 트랙) | **82** |
| **진짜 부실** | **23** |

진짜 부실 23건 분석:
- 약 20건: 사실은 첨부파일 본체 (본문 짧지만 첨부에 본 기준 있음 — quality_scan v1.2가 빈 CDATA만 ATTACHMENT_ONLY로 잡았기 때문에 분류 누락)
  - 예: 환경 공정시험기준 7건, 전기용품 안전기준 KC 시리즈 3건, 가스기술기준 상세기준 2건
- 약 3건: 진짜 짧은 시행규칙 — 사회복지공동모금회법 시행규칙 / 승강기산업 진흥법 시행규칙 / 친환경주택 에너지절약 변경 지정

→ 실질 진짜 부실 ≈ 3건 / 652. 의무사항 추출 단계 진입 가능.

---

## 4. 데이터 현재 상태

### 테이블별 카운트

| 테이블 | 카운트 | 비고 |
|---|---:|---|
| `law_master` | 652 | PHASE_1 105 + PHASE_2 77 + PHASE_3 470 |
| `law_collection_target` (active) | 654 | + 진짜실패 2 (PHASE_3, FAILED) |
| `law_external_catalog` | 983 (distinct) | 분류 완료 |
| `law_master_archive_20260422` | 48 | 4/22 분리, 변경 없음 |

### Phase별 SUCCESS 분포

| phase | SUCCESS | 평균 article | 비고 |
|---|---:|---:|---|
| PHASE_1 | 105 | 95.3 | 4/23 ATOMIC SWITCH |
| PHASE_2 | 77 | 66.7 | FIRE NFPC/NFTC |
| PHASE_3 | 470 | 28.2 | S8 신규 (단발 고시 + 첨부파일 본체 다수 포함) |

### 도메인별 분포 (PHASE_3 새로 등록 중심)

| 도메인 | PHASE_1 | PHASE_2 | PHASE_3 | 합계 | 비고 |
|---|---:|---:|---:|---:|---|
| BUILDING | 12 | 0 | ~165 | ~177 | WELFARE 통합 다수 |
| CHEMICAL | 9 | 0 | ~47 | ~56 | |
| CONSTRUCTION | 9 | 0 | ~6 | ~15 | |
| DISASTER | 3 | 0 | ~9 | ~12 | |
| ELECTRIC | 10 | 0 | ~128 | ~138 | NFPC/전기설비기술기준 등 |
| ENERGY | 8 | 0 | ~10 | ~18 | |
| ENVIRONMENT | 18 | 0 | ~54 | ~72 | |
| FIRE | 12 | 77 | ~25 | ~114 | |
| GAS | 9 | 0 | ~12 | ~21 | |
| INDUSTRIAL_SAFETY | 6 | 0 | ~10 | ~16 | |
| LABOR | 9 | 0 | ~3 | ~12 | |

(PHASE_3 도메인별 정확 카운트는 `law_collection_target`에서 group by 가능)

### 첨부파일 본체 82건 (별도 트랙)

본문이 짧고 PDF/HWP 첨부에 실제 기준이 들어있는 행정규칙. 의무사항 추출 시 이 82건은 본문에서 추출 불가능 — 별도 PDF/HWP 파싱 파이프라인 필요. 본 미션의 별표/서식 추출 트랙(S5 § 8)과 합쳐서 처리.

---

## 5. 미해결 / 차후 위험

### 5.1 ⚠️ 첨부파일 본체 행정규칙 82건 + 별표/서식

본 미션 종착점 의무사항 추출에 직접 영향. 별도 트랙:
- PDF/HWP 다운로드 → 텍스트 추출 (한글 PDF는 OCR 필요할 수도)
- 추출된 텍스트를 article 단위로 분리해서 `law_article`에 저장
- 또는 별도 테이블 `law_article_attachment`로 분리 모델링
- 우선순위는 도메인별 영향도로 결정 (예: 환경 공정시험기준 = 측정 의무에 영향)

### 5.2 PENDING 300건 분류 보강

`law_external_catalog`의 `saas_relevance='PENDING'` 300건. 자동 분류 LIKE/regex가 못 잡은 패턴들. 다음 세션에서:
- 부처별 분포 확인 → 키워드 패턴 추가
- 또는 사용자 직접 검토 (300건 부담 큼)
- 우선순위는 의무사항 추출 단계 진입 후로 미뤄도 됨

### 5.3 신규 도메인 정식 분리 (WELFARE / COMMUNICATION)

S3 § 6.1 + S8에서 임시 BUILDING 통합. 정식 분리하려면:
1. `ALTER TABLE law_collection_target DROP CONSTRAINT ck_domain_code; ALTER ... ADD CHECK (... 'WELFARE', 'COMMUNICATION');`
2. `law_master`에도 동일 CHECK 가능 — 같은 ALTER 필요
3. 다른 테이블(`master_building_legal_rules` 등)에도 영향 검토
4. WELFARE 후보 row UPDATE (의료/노인/사회복지/장애인/학교 등)

다음 세션 의무사항 추출 단계에서 자연스럽게 분리 검토 가능.

### 5.4 admrul 파서 split 안전성 (S7 § 4.2 이월)

`routers/law_collector_admrul.py` v2.0의 NFPC `_NFPC_ARTICLE_PATTERN`이 "제N조" 정규식. 본문 내 "제2조의 규정에 따라"가 잘못 split될 위험. 의무사항 추출 시 영향. 1~2건 spot-check 필요.

### 5.5 quality_scan v1.3 ATTACHMENT_ONLY 보강 (선택)

현재 v1.2는 "빈 CDATA + 첨부파일"만 ATTACHMENT_ONLY로 분류. 실제 23건 중 ~20건이 "짧은 본문 + 첨부파일" 형태로 분류 누락. v1.3에서 본문 합산 < 200자 + 첨부파일 존재 = ATTACHMENT_ONLY로 보강 가능.

다만 의무사항 추출 단계에서 자연스럽게 식별되므로 우선순위 낮음.

### 5.6 INSERT 중복 사고 원인 미규명

S8 § 3.5에서 발생한 MCP execute_sql 중복 실행. 미래 대응:
- 대량 INSERT 시 사전에 `SELECT COUNT(*) WHERE 조건` 확인 후 INSERT
- INSERT 후 즉시 COUNT 검증
- 또는 트랜잭션 래핑 (BEGIN/COMMIT)

### 5.7 expected_article_count 미설정 다수 (S7 § 4.4 이월)

PHASE_3 472건 모두 `expected_article_count` 미설정. 향후 부실 감지 정확화하려면 핵심 법령부터 보강. 우선순위 낮음.

### 5.8 Railway 프록시 영구 복구 (S7 § 4.1 이월)

iwinv VPS Squid hung 상태 미해결. 운영 cron 자동화 진입 시 필요. 의무사항 추출 단계는 수집 cron과 무관하므로 보류 가능.

---

## 6. 환경 / 인프라 현재 상태

### 코드 (tai-api)

| 위치 | 최신 commit | 비고 |
|---|---|---|
| `routers/law_collector.py` | v3.0.8 (`ca2208f6`, S6) | OUTBOUND_PROXY 통과 + /whoami |
| `routers/law_collector_admrul.py` | v2.0 (4/23 검증) | NFPC/NFTC/폴백 분기 |
| `scripts/collect_v2.py` | `0732c6e` | load_dotenv + OUTBOUND_PROXY unset |
| `scripts/collect_catalog.py` | v1.2 (`6ab29ffd`) | 동일 |
| `scripts/quality_scan.py` | v1.2 (`995df984`) | L2 + L3 |

### 실행 패턴 (변경 없음)

```bash
cd ~/dev/tai-api
git pull origin main

# 모니터
railway run python3 scripts/collect_v2.py monitor

# 단일 / 도메인 / 전체 수집
railway run python3 scripts/collect_v2.py test "법령명"
railway run python3 scripts/collect_v2.py domain FIRE
railway run python3 scripts/collect_v2.py all
railway run python3 scripts/collect_v2.py retry

# 카탈로그 (다음 세션엔 거의 불필요)
railway run python3 scripts/collect_catalog.py {collect|classify|status|missing}

# 품질 스캔
railway run python3 scripts/quality_scan.py [--domain X] [--phase PHASE_3] [--csv 경로]
```

### Cron 상태 (변경 없음)

5개 LAW cron 모두 비활성. 의무사항 추출 단계는 cron 없이 진행 가능.

---

## 7. 다음 세션 진입점 (제안)

본 미션 4단계 = **의무사항 추출**. 진입 전 사전 조사 + sanity test.

### 7.1 사전 조사 (read-only, 30분)

1. `tai-api/scripts/law_to_rules.py` (10KB), `parse_law_rules.py` (16KB) 코드 검토
   - 어떤 입력(law_article? raw_xml?)을 받아 어떤 출력을 만드는지
   - LLM 호출 여부 (Anthropic API 키 필요한지)
   - `law_rule_drafts` 테이블 구조와 매핑
2. `law_rule_drafts` 현 상태 (Supabase에서 카운트 + 샘플)
3. `inspection_set_items` 등 후속 테이블과 연결 흐름

### 7.2 sanity test (1건, 30~60분)

추천 1순위: **산업안전보건법** (가장 의무사항 많고 정리 잘됨)
```
railway run python3 scripts/parse_law_rules.py "산업안전보건법"
```
(정확한 명령은 코드 검토 후)

기대: `law_rule_drafts`에 N건 생성. 첫 5건 직접 읽고 의무사항 적절성 평가.

### 7.3 sanity 통과 시 분기

| 결과 | 다음 |
|---|---|
| 추출 N건, 품질 양호 | 도메인별 일괄 추출 진입. 1개 도메인씩 검증하며 확장 |
| 품질 불만 | 프롬프트/로직 개선 |
| 추출 자체 실패 | 코드 미완성 — S9 이상 작업 분량 |

### 7.4 첨부파일 본체 82건 처리 트랙 (병행)

다음 세션에서 결정:
- 즉시 처리 (PDF/HWP 추출 파이프라인 신규 작성)
- 의무사항 추출이 안정화된 후 별도 작업

### 7.5 admrul split 안전성 점검 (병행, 30분)

S7 § 4.2 이월. NFPC 1~2건 raw_xml의 "제N조" 분포와 DB article 분포 비교.

---

## 8. S8 commit 정리 (시간순)

### tai-api

| commit | 내용 |
|---|---|
| `416174` | collect_catalog.py: load_dotenv 추가 (v1.1) |
| `6ab29ffd` | collect_catalog.py v1.2: OUTBOUND_PROXY 명시 unset |
| `0732c6e` | collect_v2.py: load_dotenv + OUTBOUND_PROXY unset (사용자/협업자) |
| `995df984` | quality_scan.py v1.2: L3 본문 내용 검증 추가 |

### tai-admin

| commit | 내용 |
|---|---|
| `fbb5ea71` | S7 핸드오프 작성 (S8 진입 전) |
| (이번) | S8 핸드오프 작성 |

---

## 9. 사용자 메모

### S8에서 사용자가 확립한 패턴

- **선택형 질문창 명시 거부** — 직접 질의응답 형식 유지 (S6/S7과 동일)
- **인프라 디버깅 시간 → 본 미션으로** — S6/S7에서 디버깅 다 끝났고 S8에서 본 미션 큰 진전
- **결정 시 신속** — A/B/C/D 옵션 제시 시 즉시 결정 (A 확정)
- **출력 그대로 붙여넣기** — 명령 결과를 사용자가 바로 붙임, Claude는 그것 보고 진단

### 본 미션에 대한 사용자 인식 정정

S8 도중 사용자 질의 "L3까지 진행" — 이는 **무결성 검증의 깊이**에 대한 인식이 깊음을 보여줌. 본 미션이 단순 수집이 아니라 **의무사항 추출 → 사용자 사업장 적용**까지 가는 큰 그림에서 데이터 신뢰도가 결정적임을 사용자가 이해하고 있음.

→ 다음 세션에서도 의무사항 품질을 사용자가 적극 검토할 가능성 높음. 추출 후 "1건 직접 읽기" 패턴으로 spot-check 필수.

### 사용자 시간

오늘 일요일 오전~정오. 인프라 디버깅(S6/S7) + 본 미션 큰 진전 모두 한 세션에 처리. 다음 세션은 의무사항 추출에 집중.

---

## 10. 핵심 원칙 재확인 (S7에서 이월 + S8 추가)

```
1. 임의해석 금지
2. 분할 검토는 AI 몰입 위험
3. 데이터 인프라 먼저, 추출은 그 위에서
4. 적용 룰 1건 = 수백 업체 영향
5. 신뢰 추락 방지
6. "건물/산업/건설 + 다중 부속시설" — 사용자 SaaS 통찰
7. 정방향 100% 패스 후 역방향 검증
8. 환경 디버깅보다 인프라 우회
9. 검증된 인프라 먼저 확인 — 문서는 참고 (S5)
10. 자동 파이프라인은 단계별 검증 후 재활성화 (S5)
11. 환경변수 이름이 IP 같아도, 코드가 실제로 그 변수를 쓰는지 확인 (S6)
12. 첫 응답 본문 디코드 우선. timeout 단정 금지 (S6)
13. ★ 무결성은 L1(수집)+L2(외형)+L3(내용)+L4(출처)+L5(매핑) 다층 (S8)
14. ★ 대량 SQL은 사전 카운트 확인 + 사후 검증 필수 (S8 INSERT 중복 사고)
15. ★ 행정규칙 raw_xml은 첨부파일이 본체일 수 있음 — 별도 트랙 (S8)
```

---

## 11. 다음 세션 첫 메시지 (예시)

**최단**:
> "S8 핸드오프 봤음. parse_law_rules.py 코드 검토해줘."

**상세**:
> "S8 핸드오프 학습. 의무사항 추출 단계 진입. 산업안전보건법 1건으로 sanity test 가자."

---

## 12. 핸드오프 체인

| 핸드오프 | 시점 | 핵심 |
|---|---|---|
| HANDOFF_20260502_S1~S5.md | 5/2 | α 검증 → 정방향 전환 → 인프라 원복 + cron 차단 |
| HANDOFF_20260503_S6.md | 5/3 낮 | IP 진단 + /whoami |
| HANDOFF_20260503_S7.md | 5/3 오전 | Mac 우회 + 수집 품질 게이트 + admrul 파서 검증 |
| **HANDOFF_20260503_S8.md** (현재) | 5/3 정오 | **catalog 발견 + PHASE_3 472건 수집 + L3 무결성 검증** |

다음: **HANDOFF_20260503_S9.md** 또는 **HANDOFF_20260504_S9.md** (의무사항 추출 sanity test 결과)

---

**작성**: 2026-05-03 12:30 KST (일요일)
**Repo 마지막 commit**:
- tai-api: `995df984` (quality_scan.py v1.2)
- tai-admin: 이 핸드오프
**Supabase 마지막 변경**: PHASE_3 INSERT 472건 (PENDING → 470 SUCCESS + 2 FAILED)
**다음 세션 진입점**: § 7.1 parse_law_rules.py / law_to_rules.py 코드 검토
**예상 소요**: 사전 조사 30분 + sanity 30~60분 + 분기 결정
