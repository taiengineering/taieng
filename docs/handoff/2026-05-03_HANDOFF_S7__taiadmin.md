# 핸드오프 — S7 (2026-05-03 일요일 오전)

> 직전: `HANDOFF_20260503_S6.md`
> 작업 시간: 2026-05-03 (일) 약 09:00 ~ 09:35 KST
> 핵심 분류: **인프라 디버깅 + 수집 품질 게이트 통과**

---

## 0. 한 줄 요약

법령 수집 인프라 4중 장애를 모두 짚어내고, 182건 수집·품질 검증을 100% 통과시켰다. **다음 세션은 의무사항(rule) 추출 단계로 진입할 수 있다**.

---

## 1. 본 미션 (변경 없음)

> 미수집된 법령을 수집·정제하면서 파이프라인 문제를 개선하여, 종국에는 **의무사항**을 도출한다.

S6에서 본 미션의 1·2단계(수집·정제)가 완료되었음이 확인됐다. 다음 세션은 3단계(의무사항 추출) 진입.

---

## 2. S6 시작 시점 vs 종료 시점

| 항목 | 시작 (S6 종료 시점) | 종료 (S7 시작 시점) |
|---|---|---|
| `tai-api` 최신 commit | `b6a5d4b5` (v3.0.6) | `2e38250a` (v3.0.8 + quality_scan v1.1) |
| Railway `/whoami` | 미구현 | 정상 (egress IP 확인 가능) |
| Railway egress IP | 미상 | `35.197.154.99` (GCP 동적) 확정 |
| 프록시 (iwinv 115.68.227.222) | "정상" 가정 | **hung 상태** (재부팅도 효과 없음) |
| Supabase 리전 | 싱가폴 (가정) | **한국 이전 완료** 확인 |
| Supabase 키 형식 | JWT (가정) | **`sb_secret_...` 새 형식** 확인 |
| `.env` 로드 방식 | `set -a; source .env` | **`load_dotenv()` 코드에 내장** |
| 법령 수집 (collection_status) | 182/182 SUCCESS | **변동 없음 (재수집 1건만 발생)** |
| 수집 품질 (quality_scan) | 미스캔 | **정상 182 / 부실 0** |

---

## 3. S6에서 확정·해결된 사실

### 3.1 Railway egress는 GCP 동적 IP (변경 불가)

`/whoami` 호출 결과 `35.197.154.99`. GCP us-west1 대역. Railway는 호스팅 OS가 아니라 GCP 위에서 떠 있고, 이 IP는 매 컨테이너 재시작마다 바뀔 수 있는 동적 IP. 따라서 **법제처 OC=taieng에 직접 등록 불가**(IP 등록은 고정 IP 전제).

### 3.2 프록시(`115.68.227.222`)는 iwinv VPS, Squid 3128 (4/20에 구축)

- 4/20 핸드오프(`tai-api/docs/session-handoff-20260420-v2.md`)에서 발견:
  - `OUTBOUND_PROXY=http://115.68.227.222:3128`
  - "iwinv VPS, 한국 고정 IP, SMS/결제 모듈에서 사용"
- 그러나 **현재 코드 어디서도 `OUTBOUND_PROXY`를 안 읽고 있었음** (Fly.io→Railway 이전 시 누락)
- v3.0.8에서 `routers/law_collector.py`에 추가했으나 **iwinv 프록시 자체가 hung 상태**:
  - TCP 연결은 됨 (포트 3128 listen 중)
  - GET 요청 송신 후 0 bytes 응답 = Squid가 응답하지 않음
  - **VPS 재부팅도 효과 없음** (Squid 자동 시작 + 외부 인터넷 자체 못 나가는 가능성)
- → **Railway 경로는 사실상 사용 불가**, Mac 로컬 직접 실행으로 우회 결정

### 3.3 Supabase 한국 리전 이전 (URL 변경)

- 옛 URL `xntdkrjhgcscmqctdzyo.supabase.co` (싱가폴) → DNS NXDOMAIN
- Mac `.env`에는 옛 URL이 그대로 남아있어 직접 실행 불가
- Railway Variables에는 새 URL이 등록되어 있음 → `railway run` CLI 패턴으로 우회

### 3.4 `sb_secret_...` 새 키 형식

- 41자, JWT(`eyJ...`) 아님. 2025년 출시된 새 Supabase API key 시스템.
- supabase-py 클라이언트가 인식 가능 (확인됨 — `railway run` 정상 작동)

### 3.5 `.env` 로드 zsh 호환성 문제

- `set -a; source .env`가 `.env` 내 특수문자(`^`, `$`)에 의해 부분 로드되는 버그
- 결과: `OUTBOUND_PROXY` 같은 단순 키는 로드되지만 `SUPABASE_URL` 같이 뒷줄에 있는 키는 빈 값
- → `scripts/collect_v2.py`에 `load_dotenv()` 내장 (commit `7f67a240`)

### 3.6 admrul 파서 v2.0 신뢰성 검증

- `quality_scan` v1.0이 부실 78건 식별 → 그 중 77건이 NFPC `NO_PARAGRAPHS`였으나, raw_xml 직접 확인 결과 **NFPC는 본래 평면 CDATA 구조**라 NO_PARAGRAPHS는 false positive
- 진짜 부실 1건(`전기설비기술기준`, AdmRul, 조문 1개)만 v2.0 파서로 강제 재수집 → **1 → 212건** 정상 분해
- `quality_scan` v1.1에서 행정규칙 분기 추가 → **부실 0/182**

---

## 4. 미해결 / 차후 위험 (다음 세션이 알아야 할 것)

### 4.1 ⚠️ 프록시 영구 복구 미완

- iwinv VPS의 Squid가 왜 hung 상태인지 **원인 미규명**
- 가능 원인:
  1. Squid 외부 outbound 차단 (DNS, 보안그룹)
  2. Squid 데몬 자체 hang (재부팅 후에도 재발)
  3. Squid ACL이 silent drop 모드
- 재진단 시 SSH 접속 후 다음 명령으로 시작:
  ```
  sudo systemctl status squid
  sudo ss -tlnp | grep 3128
  curl -m 10 http://api.ipify.org   # VPS 자체에서 외부 도달성
  sudo tail -50 /var/log/squid/access.log
  sudo tail -50 /var/log/squid/cache.log
  sudo grep -E "^(acl|http_access)" /etc/squid/squid.conf
  ```
- 영향 범위:
  - **법령 수집 cron은 가동 불가** (Railway에서 돌아도 죽은 프록시 거치므로 timeout)
  - 따라서 LAW_* cron 5종 비활성 상태 유지 적절. 활성화는 프록시 복구 후
  - SMS/결제: 4/20 이후 정말 작동하는지 별도 검증 필요할 수 있음 (`OUTBOUND_PROXY`를 안 보고 있을 가능성, 또는 다른 경로로 우회 중일 가능성)

### 4.2 admrul 파서 split 안전성 미검증

- v2.0 NFPC 파서: `<조문내용>` 여러 개를 순회하며 "제N조" 정규식 매칭
- 미확인: 조문 본문 안에 "제2조의 규정에 따라" 같은 문구가 있을 때 잘못 split 위험
- 의무사항 추출 단계에서 **조문 단위 신뢰성**에 직결되므로 1~2건 spot-check 필요

### 4.3 Mac 로컬 실행 의존

- 현재 수집은 **사용자 Mac에서 `railway run`으로만** 가능
- Mac IP가 OC=taieng에 등록되어 있어서 가능 (S7 시작 시점 검증)
- Mac IP가 변경되면(이사, ISP 변경, IP 갱신) 다시 등록 필요
- 자동화(cron) 불가 — 사용자가 직접 명령 실행 시점만 동작

### 4.4 expected_article_count 미설정 다수

- `law_collection_target.expected_article_count`가 0인 행이 다수
- → `BELOW_EXPECTED` 체크가 무용지물 (v1.1에서 면제 처리)
- 의무사항 추출 단계 진입 전, 핵심 법령들에 대한 expected 수치를 채우면 향후 부실 감지가 더 정확해짐

---

## 5. 환경 / 인프라 현재 상태

### 코드

| 위치 | 최신 commit | 비고 |
|---|---|---|
| `tai-api/routers/law_collector.py` | v3.0.8 (commit `ca2208f6`) | `OUTBOUND_PROXY` 통과 + `/whoami` |
| `tai-api/scripts/collect_v2.py` | commit `7f67a240` | `load_dotenv()` 내장 |
| `tai-api/scripts/quality_scan.py` | v1.1 (commit `2e38250a`) | 행정규칙 분기 |

### 실행 방법

**Mac 로컬에서만 가능** (Railway는 프록시 hung으로 사용 불가):

```
cd ~/dev/tai-api
git pull origin main

# 모니터
railway run python3 scripts/collect_v2.py monitor

# 단일 테스트
railway run python3 scripts/collect_v2.py test "법령명"

# 도메인별
railway run python3 scripts/collect_v2.py domain FIRE

# 품질 스캔
railway run python3 scripts/quality_scan.py --csv /tmp/q.csv

# 품질 스캔 (특정 도메인만)
railway run python3 scripts/quality_scan.py --domain FIRE
```

> **`railway` 접두사 누락 시 옛 .env가 로드되어 DNS 실패.** 항상 붙일 것.

### Cron 상태 (변동 없음)

- `RULE_REPARSE`, `LAW_COLLECT_MISSING`, `LAW_UPDATE_CHECK`, `LAW_RECOLLECT_15D`, `VALIDATE_MASTER` 5종 모두 **비활성**
- 활성화는 프록시 복구 후 (S6 § 4.1 참조)

---

## 6. 데이터 현재 상태

| 지표 | 값 |
|---|---|
| `law_master` | 182건 |
| `law_collection_target` (active) | 182건, 모두 SUCCESS |
| `quality_scan` 정상 | 182/182 (100.0%) |
| `quality_scan` 부실 | 0 |
| 행정규칙(AdmRul) 비중 | 약 77~78건 (FIRE 도메인 다수 + 전기설비기술기준) |

도메인별 분포:

```
BUILDING        12   |   ELECTRIC       10
CHEMICAL         9   |   ENERGY          8
CONSTRUCTION     9   |   ENVIRONMENT    18
DISASTER         3   |   FIRE           89
GAS              9   |   INDUSTRIAL_SAFETY 6
LABOR            9
                                    합계  182
```

---

## 7. 다음 세션 진입점 (제안)

본 미션의 3단계 = **의무사항 추출(rule extraction)**. 다음 세션은 다음 흐름을 권장:

### 7.1 사전 조사 (read-only, 30분)

1. `tai-api/scripts/law_to_rules.py` (10KB), `tai-api/scripts/parse_law_rules.py` (16KB) 검토
   - 어떤 입력(law_article 또는 raw_xml)을 받아 어떤 출력(`law_rule_drafts`?)을 만드는지
   - LLM 호출 여부 (Anthropic API 키 필요한지)
2. `law_rule_drafts` 테이블 현 상태 (Supabase에서 카운트)
3. `inspection_set_items` 등 후속 테이블과의 연결 흐름

### 7.2 sanity test (30~60분)

핵심 법령 1건으로 의무사항 추출 시도:

추천 1순위 — **산업안전보건법** (가장 의무사항이 많고 잘 정리된 법령):
```
railway run python3 scripts/parse_law_rules.py "산업안전보건법"   # 정확한 명령은 코드 검토 후
```

기대: `law_rule_drafts`에 N건의 의무사항 row 생성. 첫 5건 직접 읽어보고 의무사항으로 적절한지 평가.

### 7.3 sanity 통과 시 결정 분기

| 결과 | 다음 |
|---|---|
| 의무사항 N건 추출, 품질 양호 | 도메인별 일괄 추출 진입. 도메인 1개씩 검증하며 확장 |
| 추출은 되는데 품질 불만 | 프롬프트 개선 또는 후처리 룰 추가 |
| 추출 자체 실패 (코드 미완성) | 추출 파이프라인 신규 설계 — S7 이상의 작업 분량 |

### 7.4 행정규칙 split 안전성 검증 (병행)

S6 § 4.2. 1~2건 NFPC를 골라 raw_xml의 "제N조" 분포와 DB article 분포가 일치하는지 비교.

---

## 8. 사용자 요청 시 즉시 해야 할 명령들 (다음 세션 시작 직후)

```bash
# 1. 환경 검증
railway run python3 scripts/collect_v2.py monitor

# 2. 의무사항 파이프라인 코드 위치 확인
ls -la ~/dev/tai-api/scripts/*rule*.py ~/dev/tai-api/scripts/*to_rules*.py

# 3. 현재 law_rule_drafts 카운트
railway run python3 -c "
from dotenv import load_dotenv; load_dotenv()
from db.database import get_supabase
s = get_supabase()
r = s.table('law_rule_drafts').select('id', count='exact').execute()
print(f'law_rule_drafts: {r.count}건')
by_status = s.table('law_rule_drafts').select('status').execute().data
from collections import Counter
print(Counter(d.get('status') for d in by_status))
"
```

---

## 9. S6 commit 정리 (시간순)

| commit | repo | 내용 |
|---|---|---|
| `8d1df7d6` | tai-api | v3.0.7 — `/whoami` 진단 endpoint |
| `ca2208f6` | tai-api | v3.0.8 — `OUTBOUND_PROXY` 통과 |
| `7f67a240` | tai-api | `collect_v2.py`에 `load_dotenv()` 내장 |
| `0c2bd963` | tai-api | `quality_scan.py` v1.0 신규 |
| `2e38250a` | tai-api | `quality_scan.py` v1.1 — 행정규칙 분기 |

(tai-admin은 본 핸드오프 1건만 commit)

---

## 10. 사용자 메모 (S7 시작 시 참고)

- 사용자는 이번 세션에서 **선택형 질문창을 명시적으로 거부**함. 직접 질문/답변 형식으로 진행할 것.
- 사용자는 **인프라 디버깅에 시간을 많이 썼고**, 본 미션이 의무사항 도출임을 강조함. 다음 세션은 가능하면 본질(추출)에 시간을 쓸 것.
- 사용자 한국 시각 일요일 오전. 본인 페이스 고려.
