# HANDOFF — 2026-05-03 세션 6 (IP 미등록 진단 + /whoami endpoint 추가 필요)

> **작업명**: v3.0.6 검증 시도 → "사용자 정보 검증 실패" 응답으로 IP 미등록 의심 → 진단 endpoint 미추가 상태로 종료
> **상태**: v3.0.6 deploy + cron 비활성화는 그대로 유지. 검증은 IP 진단 후 진행.
> **다음 세션 진입점**: § 4. `/whoami` endpoint push → Railway egress IP 확인 → open.law.go.kr 비교

---

## 0. 세션 흐름 (S1~S6 통합)

```
S1 (5/2 17:53): α 검증 시도 → 표면 일치 한계 발견
   ↓
S2 (5/2 19:00): 4가지 매핑 오류 패턴 + 정방향 패러다임 전환
   ↓
S3 (5/2 19:50): 4/22 archive 발견 + 통합 마스터 80개 추출 + 외부 카탈로그 인프라 작성
   ↓
S4 (5/2 20:30): Railway 인프라 디버깅 + DATA_GO_KR 환경변수 fallback (v3.0.2)
   ↓
S5 (5/2 22:30): 검증된 인프라 원복(v3.0.6) + 자동 cron 5개 비활성화
   ↓
S6 (5/3 일요일 낮): debug/건축 검증 시도 → "사용자 정보 검증 실패" XML
   - 어제 timeout이 야간 불안정이 아니라 IP 인증 거부였음을 확정
   - INICIS_CLIENT_IP 변수 존재 발견 → 그러나 law_collector는 이를 참조하지 않음
   - 진짜 egress IP 확인용 /whoami endpoint 필요 → 사용자 결정 보류로 push 안 함
```

---

## 1. S6 작업 요약 (시간순)

### 1.1 v3.0.6 검증 재시도 (5/3 일요일 낮)

S5 핸드오프 § 5.1 "평일 주간" 조건 미충족이지만 시도. 4번의 호출:

| # | 호출 | 응답 | 의미 |
|---|---|---|---|
| 1 | `debug/건축` (첫 호출) | HTTP 200 + XML "사용자 정보 검증 실패" | **IP 미등록 확정** |
| 2 | `debug/소방` (직후) | ConnectTimeout 30s | 비인가 IP 반복 호출 후 일시 차단 |
| 3 | `status` | 정상 (Supabase만 호출) | v3.0.6 deploy 확인 |
| 4 | `debug/건축 -m 15` | timeout 15s | 일시 차단 지속 |

**1번 응답 XML 디코드** (결정적 단서):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <result>사용자 정보 검증에 실패하였습니다.</result>
    <msg>OPEN API 호출 시 사용자 검증을 위하여 
         정확한 서버장비의 IP주소 및 도메인을 등록해 주세요.</msg>
</Response>
```

→ 어제(S5)의 timeout은 야간/주말 서버 불안정이 아니라 **IP 차단의 결과**였음. S5 § 6 트러블슈팅 가이드의 **증상 2**(IP 미등록)에 정확히 매칭. S5 진단 일부 수정 필요.

### 1.2 `INICIS_CLIENT_IP` 발견과 사용자 핵심 지적

Railway 환경변수 목록에 `INICIS_CLIENT_IP`가 존재. INICIS 결제 IP 화이트리스트 인증 용도. 사용자가 이 변수의 존재로 "Railway에 고정 IP가 등록되어 있다"는 사실을 시사.

**Claude 초기 가정** (잘못됨): 그 IP가 Railway egress IP와 동일할 것.

**사용자 지적**:
> **"지금 수집프로그램에서 저 아이피를 쓰는지를 먼저확인"**

→ 정확. `INICIS_CLIENT_IP`는 **INICIS 통신용으로 저장된 값**일 뿐, 수집 프로그램이 이를 사용한다는 보장 없음.

### 1.3 코드 검증 결과

`routers/law_collector.py` v3.0.6 전수 검토:

```python
# fetch_law_list / fetch_law_content 의 호출 코드
def fetch_law_list(query, display=100, page=1):
    url = f"{LAW_API_BASE}/lawSearch.do"
    params = {"OC": LAW_API_OC, "target": "law", ...}
    resp = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=30)
    #      └── 평범한 requests.get().
```

확인 결과:
- `INICIS_CLIENT_IP` 환경변수 **참조 0건** (전체 파일)
- 커스텀 source IP / 인터페이스 바인딩 **없음**
- `requests.adapters` 커스터마이징 **없음**
- → **Railway 컨테이너의 OS 기본 egress IP**로 송신됨

### 1.4 추가 발견: debug 응답 형식 일부 누락

S5에서 v3.0.6 작성 시 `debug` 응답에 `oc` 필드 추가했으나, 5/3 응답에 `"oc"` 필드 없음. 코드 확인 결과 **현재 코드에는 `oc` 필드 포함됨** (`return {... "oc": LAW_API_OC, ...}`). 응답이 옛 형식인 이유 미확정. 가능성:
1. `/status`는 신 형식, `/debug`는 캐시된 옛 형식 (CDN 또는 Railway 응답 캐시)
2. 에러 분기에서 `oc` 누락 — 코드 재확인 시 정상

핵심 진단(IP 미등록)에는 영향 없음. 다음 세션에서 응답 분석 시 재확인.

### 1.5 진단 endpoint 제안 (push 보류)

```python
# 제안된 5줄 진단 코드 (현재 코드에 없음)
@router.get("/whoami")
async def whoami():
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=10)
        return {"egress_ip": r.json().get("ip"), "oc": LAW_API_OC}
    except Exception as e:
        return {"error": str(e)}
```

- 외부 echo 서비스(`api.ipify.org`)가 **호출 측 IP를 그대로 반환**
- 즉 법제처 호출에 사용되는 동일한 egress IP가 회신됨
- 호출 결과 → INICIS_CLIENT_IP / open.law.go.kr 등록 IP와 비교

**push 보류 사유**: 사용자가 핸드오프 작성 요청 → 다음 세션 첫 작업으로 미룸.

---

## 2. 현재 시점 상태 (S6 종료)

### 2.1 인프라 (S5에서 변경 없음)
- 마지막 commit: `b6a5d4b5` (v3.0.6) — `/status` 응답 정상
- 코드: law.go.kr/DRF + OC=taieng 단일 경로 (수정 없음)
- Railway 환경변수: `LAW_API_OC=taieng` ✅, `INICIS_CLIENT_IP` ✅ (수집과 무관)

### 2.2 자동 cron (S5에서 변경 없음, 모두 비활성)
- LAW 5개: `LAW_COLLECT_MISSING`, `LAW_UPDATE_CHECK`, `LAW_RECOLLECT_15D`, `RULE_REPARSE`, `VALIDATE_MASTER`
- + 사전 비활성: `AUTO_PARSE_NEW`

### 2.3 DB 상태 (S5와 동일)
- `law_master`: 182개
- `law_external_catalog`: 0건
- `law_master_archive_20260422`: 48개

### 2.4 신규 발견 (S6)
- **법제처 OC=taieng 등록 IP ≠ Railway egress IP** (강력 의심, 미확정)
- `INICIS_CLIENT_IP`는 수집 프로그램과 무관 (코드 검증 완료)

---

## 3. 환경 정보 (참고)

| 항목 | 값 |
|---|---|
| Supabase Project | 서울 `vwlahtguyggrhvslabax` |
| Railway URL | `https://api.taieng.co.kr` |
| Repo (admin) | `taiengineering/tai-admin` (docs/) |
| Repo (api) | `taiengineering/tai-api` (routers/, scripts/, docs/) |
| Railway 외부 IP | **미확정** (S6에서 의심 제기) |
| 4/23 핵심 문서 | `tai-api/docs/LAW_COLLECTION_COMPLETE_2026-04-23.md` |
| 사용자 환경 | Mac M2max, ~/dev/tai-api |

---

## 4. 🔴 다음 세션 — 즉시 실행 워크플로우

### 4.1 Step A: `/whoami` endpoint push (1차)

**파일**: `routers/law_collector.py` (현재 v3.0.6, commit `b6a5d4b5`)

**라우터 엔드포인트 섹션 끝(`@router.get("/status")` 위)에 추가**:

```python
@router.get("/whoami")
async def whoami():
    """진단용: Railway 컨테이너의 외부 egress IP 확인 (S6 IP 미등록 진단)"""
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=10)
        return {
            "egress_ip": r.json().get("ip"),
            "oc": LAW_API_OC,
            "purpose": "법제처 호출에 사용되는 IP를 확인 — open.law.go.kr 등록 IP와 비교"
        }
    except Exception as e:
        # 외부 ipify 실패 시 백업
        try:
            r2 = requests.get("https://ifconfig.me/ip", timeout=10)
            return {"egress_ip": r2.text.strip(), "oc": LAW_API_OC, "via": "ifconfig.me"}
        except Exception as e2:
            return {"error": f"{type(e).__name__}: {str(e)[:200]}", 
                    "fallback_error": f"{type(e2).__name__}: {str(e2)[:200]}"}
```

**버전 표기**: v3.0.7 (진단용 패치). `/status`의 `version` 필드도 동시 업데이트.

**Push 후 Railway deploy 1~2분 → 호출**:
```bash
curl https://api.taieng.co.kr/law-collector/whoami
```

**기대 응답**:
```json
{
  "egress_ip": "xxx.xxx.xxx.xxx",   ← Railway 실제 송신 IP
  "oc": "taieng",
  "purpose": "..."
}
```

### 4.2 Step B: 비교 — 사용자 작업

사용자가 `open.law.go.kr` 로그인 → 마이페이지 → 인증키 관리 → OC=taieng 등록 IP 목록 확인.

| 비교 결과 | 다음 액션 |
|---|---|
| `egress_ip`가 등록 목록에 **있음** | 다른 원인 (대역 차단? 헤더? 시간대?) → 추가 진단 |
| `egress_ip`가 등록 목록에 **없음** | 즉시 추가 등록 → 5분 후 `debug/건축` 재시도 → 정상이면 catalog 트리거 |
| 등록 목록이 **비어있음** | OC만 만들고 IP 등록 안 한 상태 → `egress_ip` 추가 등록 |
| `egress_ip`와 INICIS_CLIENT_IP **다름** | Railway가 동적 IP 사용 중 — 고정 IP 별도 구매했다면 그 IP 어디 사용되는지 재확인 필요 |

### 4.3 Step C: IP 등록 후 검증

```bash
curl -m 15 https://api.taieng.co.kr/law-collector/debug/건축
```

**기대 응답** (정상):
```json
{
  "api_source": "law.go.kr",
  "oc": "taieng",
  "law_count": 5,
  "first_law": {"법령ID": "...", "법령명한글": "건축법", ...}
}
```

→ 정상이면 S5 § 4.2 catalog 트리거로 진행.

---

## 5. ⚠️ 시나리오별 분기

### 시나리오 A: Railway egress IP가 OC에 없음 (가장 가능성 높음)
- 원인: 어제 S4의 진단(Railway IP 미등록)이 옳았음. S5에서 사용자가 "고정 IP 등록되어 있다"고 했으나, INICIS용일 가능성 높음.
- 해결: 그 IP를 OC에 추가 등록 → 5분 후 정상화

### 시나리오 B: Railway egress IP가 매번 바뀜
- 원인: Railway 무료/Hobby 플랜은 동적 egress IP. 고정 IP는 별도 추가 결제 필요.
- 확인: `/whoami`를 **여러 번 호출**해서 IP 일관성 확인
- 해결: Railway Static IP 추가 구매 OR 사용자 로컬에서 `scripts/collect_v2.py` 직접 실행 (4/23 검증된 방법)

### 시나리오 C: Railway 고정 IP는 있는데 다른 변수에 저장됨
- 가능성: INICIS_CLIENT_IP가 INICIS 측에 등록한 IP일 수도. Railway 측 실제 egress와 다를 수 있음.
- 확인: `/whoami` 결과를 INICIS_CLIENT_IP와 비교
- 해결: 시나리오 A 또는 B로 분기

### 시나리오 D: 등록 IP는 맞는데 거부됨 (드문 케이스)
- 원인: 헤더, User-Agent, 도메인 검증 등 다른 요인
- 해결: 4/23 작동 코드(`scripts/collect_v2.py`)와 현재 차이 비교

---

## 6. S5 핸드오프와의 차이점 (이번 세션 학습)

### S5에서 잘못 기록된 것
- "법제처가 야간에 연결이 불안" — **부분적으로만 사실**. 실제로는 IP 미등록으로 거부 → 일시 차단 → timeout 패턴 가능성 높음. 야간 timeout만으로 해석은 부족했음.

### S5 § 6 트러블슈팅에 추가할 항목
**증상 5**: 첫 호출 HTTP 200 + "사용자 정보 검증 실패" XML, 직후 호출은 timeout
- **원인**: IP 미등록 → 법제처가 비인가 IP를 일시 차단(rate limit)
- **확인**: `/whoami`로 egress IP 확인 → 등록 IP와 비교
- **해결**: IP 등록 추가 → 5~10분 대기 후 재시도

---

## 7. 미해결 결정 사항 (S5에서 이월 + S6 추가)

### 7.1 신규 도메인 추가 여부 (S5 § 7.1 이월)
WELFARE / COMMUNICATION 또는 BUILDING 통합. 수집 시작 후 결정 가능.

### 7.2 사업장 다중 타입 모델링 (S5 § 7.2 이월)
운영 단계 별도 설계.

### 7.3 추가 외부 발견 법령 (S5 § 7.3 이월)
catalog 수집 후 사용자 검토.

### 7.4 RULE_REPARSE 재활성화 시점 (S5 § 7.4 이월)
Phase 3+ 매핑 오류 정정 후.

### 7.5 ⭐ S6 신규: Railway 고정 IP 비용 vs 사용자 로컬 우회
- Railway Static IP는 추가 결제 (월 $5~10 정도)
- 사용자 로컬 우회: 4/23 검증된 `scripts/collect_v2.py`를 사용자 PC에서 직접 실행 (사용자 로컬 IP가 OC에 등록되어 있다고 가정)
- 운영 자동화에는 Railway 고정 IP가 안전하나, 일회성 catalog 수집은 로컬 우회로 충분
- 사용자 결정 필요

---

## 8. Phase 3+ 미해결 과제 (S5에서 이월)

| 과제 | 상태 |
|---|---|
| 별표/서식 수집 | 4/23부터 미해결 |
| NFTC/NFPC 세부 파싱 | 미해결 |
| 자동 업데이트 재가동 | cron 비활성화 — Step H에서 |
| 운영 13개 검증 불가 룰 정합화 | Step G에서 |
| 매핑 오류 4개 패턴 정정 | RULE_REPARSE 비활성 유지 |
| α 검증 작업 (S1) | 폐기 |
| 사용자 로컬 .env DNS 문제 | 보류 |
| data.go.kr 시도 (S5) | 폐기 |
| **Railway egress IP 미등록 (S6)** | **다음 세션 § 4** |

---

## 9. 핵심 원칙 재확인

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
11. ★ 환경변수 이름이 IP 같아도, 코드가 실제로 그 변수를 쓰는지 확인 후 추론 (S6)
12. ★ 첫 응답 본문 디코드 우선. timeout이라고 무조건 서버 문제 단정 금지 (S6)
```

---

## 10. 다음 세션 첫 메시지 (예시)

**최단**:
> "S6 핸드오프 봤음. /whoami push해줘."

**상세**:
> "S6 핸드오프 학습. v3.0.7로 /whoami endpoint 추가하고 push. deploy 끝나면 알려줘서 호출하겠음."

**병렬** (사용자가 IP 이미 알아냈을 때):
> "Railway egress IP는 X.X.X.X. open.law.go.kr 등록 IP는 Y.Y.Y.Y. 다음 단계 가자."

→ Claude가 분기 시나리오(§ 5)에 따라 즉시 결정.

---

## 11. 핸드오프 체인

| 핸드오프 | 시점 | 핵심 |
|---|---|---|
| HANDOFF_20260501.md | 5/1 | preserved 부분 일치 48건 분리 |
| HANDOFF_20260502_S1.md | 5/2 17:53 | α 검증 한계 |
| HANDOFF_20260502_S2.md | 5/2 19:00 | 4가지 매핑 오류 + 정방향 전환 |
| HANDOFF_20260502_S3.md | 5/2 19:50 | 통합 80개 + 외부 카탈로그 |
| HANDOFF_20260502_S4.md | 5/2 20:30 | Railway 인프라 + DATA_GO_KR (v3.0.2) |
| HANDOFF_20260502_S5.md | 5/2 22:30 | 검증 인프라 원복(v3.0.6) + cron 차단 |
| **HANDOFF_20260503_S6.md** (현재) | 5/3 낮 | **IP 미등록 진단 + /whoami 필요** |

다음: **HANDOFF_20260503_S7.md** 또는 **HANDOFF_20260504_S7.md**

---

## 12. Commit 이력 (S6)

| 시각 | 작업 | 상태 |
|---|---|---|
| 13:30~ | S5 핸드오프 학습 | ✅ |
| 13:35~ | v3.0.6 검증 시도 (4번 호출) | ✅ — IP 미등록 확정 |
| 13:45~ | 코드 전수 검토 (`INICIS_CLIENT_IP` 미참조 확인) | ✅ |
| — | `/whoami` endpoint push | ❌ **다음 세션** |
| — | 핸드오프 작성 | ✅ (이 문서) |

**Repo 마지막 commit**: tai-api `b6a5d4b5` (v3.0.6, 변경 없음)

---

## 13. S6 자기 점검

**이번 세션 잘못된 패턴**:
1. `INICIS_CLIENT_IP` 환경변수 발견 후 "Railway egress IP일 것"으로 추론 → 사용자 지적으로 정정
2. 어제 timeout을 "야간/주말 불안정"으로 단정 → 오늘 첫 응답 본문 디코드로 IP 미등록임이 드러남 → S5 진단 일부 오류

**다음 세션 적용**:
- 환경변수 이름이 시사하는 의미 ≠ 코드의 실제 사용. 항상 코드 검증 우선.
- HTTP 응답이 200이라도 본문 XML/JSON에 에러 메시지 있을 수 있음. timeout 직전 마지막 정상 응답 본문 우선 분석.
- 진단 endpoint를 코드 변경보다 먼저 추가 (5줄짜리 read-only) — 추측보다 측정.

---

**작성**: 2026-05-03 14:00 KST (일요일)
**Railway 마지막 commit**: `b6a5d4b5` (v3.0.6, 변경 없음)
**Supabase 마지막 변경**: 없음 (S5의 cron 5개 비활성화 그대로 유지)
**다음 세션 진입점**: § 4.1 `/whoami` endpoint push (v3.0.7)
**예상 소요**: push + deploy 3분 + 호출 1분 + 사용자 비교 5분 = 10분 내 IP 진단 완료
