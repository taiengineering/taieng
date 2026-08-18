# HANDOFF — safe 결함 §32·§66·§67 통지 (→ 헬프센터 창)

> 작성 2026-08-18 · **갱신 2026-08-18(§66 병합·§67 표시수정 반영)** · 수신 **헬프센터 창**(LEDGER `tai-helpcenter_LEDGER_safe-defects.md` 소유)
> 성격 **통지** — LEDGER 미해결 재점검 중 처리/발견한 결함 3건. 이 문서로 LEDGER 갱신 판단을 요청한다.
> ⚠ LEDGER 규칙 준수: **danger·warn 은 배포 SUCCESS(코드) + 라이브 확인** 둘 다일 때만 지운다. 아래 §2 라이브 확인 후 반영할 것.
> 앞선 통지 `2026-08-18_HANDOFF_worker-app-defects-75-76-77-79-처리결과.md` 와 별개 건이다(75·76·77·79 는 그 문서 참조).

---

## 0. 한눈에

| 결함 | 상태 | 근거 | 조치 |
|---|---|---|---|
| **§32** 알럿 관리 라우터 미등록 | **이미 해소(코드·배포)** | `router_registry/saas_core.py` 에 `routers.alert_messages` 등록됨(주석 "LEDGER §32") | 라이브 확인 후 danger 삭제 |
| **§67** 작업중지 기준 카드 | **해소(코드·배포)** — 서버 v1.3.2 + 화면 PR #31 병합 | weather.py v1.3.2(data 키) + tai-admin **PR #31**(threshold JSON→condition) | 라이브 확인 후 warn 삭제 |
| **§66** 날씨 작업중지 배지 항상 「정상」 | **수정 PR #30 병합(배포)** | tai-admin **PR #30** merged `0324e12` | 라이브 확인 후 danger 삭제 |

---

## 1. 결함별 상세

### §32 — 알럿 관리 라우터 미등록 【이미 해소 · 재점검 발견】
- LEDGER 스냅샷은 미해결(높음)로 표시 중이나, **실측 결과 이미 등록돼 있다.** `router_registry/saas_core.py` 의 `ROUTERS` 에 `notifications` 다음 줄로 `{"module": "routers.alert_messages"}` 가 들어 있고, 주석에 "LEDGER §32" 로 사유까지 적혀 있다. main 반영됨 = 이미 배포됨.
- 권한: `alert_messages.py` 의 변경 엔드포인트(목록·생성·수정·삭제·토글)는 전부 `role_code=="001"`(최고관리자) 게이팅. `/alert-messages/codes` 만 무인증(코드→메시지 딕셔너리, 민감정보 아님). "등록 즉시 살아나니 권한 검증" 우려는 이미 충족.
- **라이브 확인**: 최고관리자 계정으로 `/alert-messages` 목록이 200 으로 뜨는지(과거 404). 확인되면 §32 danger 삭제.

### §67 — 작업중지 기준 카드 「기준 정보 없음」 【해소 · 서버+화면 2단】
- **서버(이미 해소)**: `routers/weather.py` v1.3.2(2026-08-18)에서 `GET /weather/work-stop-criteria` 응답에 표준 봉투 `data` 키를 병기. 화면이 값을 읽어 제37조 4개 항목(강풍·강우·강설·뇌전)이 뜬다. **라이브 스크린샷으로 항목 표시 확인됨.**
- **화면(PR #31 병합)**: 항목은 떴으나 설명 자리에 `threshold` dict 가 raw JSON(`{ "type":"wind_speed","value":10,"unit":"m/s" }`)으로 노출됐다. 서버 `WORK_STOP_CRITERIA` 필드는 `name`·`condition`·`threshold(dict)` 인데 화면이 `{{ c.description || c.threshold }}` 로 렌더 — `description` 부재 시 dict 출력. `{{ c.condition || c.description }}` 로 교체(자연어 "순간풍속 초당 10m 이상" 표시). 카드 1줄 변경.
- **라이브 확인**: 카드에 JSON 대신 "순간풍속 초당 10m 이상" 등 자연어 4항목이 뜨는지. 확인되면 §67 warn 삭제.

### §66 — 날씨 작업중지 배지 항상 「정상」 【PR #30 병합 · safe 대장 소유】
- **원인**: `safety-dashboard` 의 `loadWeather()` 가 서버에 없는 `stop.level` 을 읽어 `|| 'normal'` 로 항상 초록 「정상」. 서버 계약(`routers/weather.py`)은 `work_stop.required`(bool)·`reasons`(배열)다. 강풍·강우·강설·뇌전이 제37조 기준을 넘어도 「정상」이라 표시한 **안전 직결 오안내**.
- **수정 (tai-admin PR #30 merged `0324e12`)**: `useSafetyDashboard.ts` 가 `work_stop.required` 로 배지 도출 — true→빨강 「작업중지」+사유, 정보 있고 false→초록 「정상」, **정보 없으면 회색 「판정 불가」(초록 정상으로 단정 안 함)**. `weatherLevelLabel()` 로 한국어 라벨. `index.vue` 배지 텍스트 1줄 교체.
- **미확인**: `work_stop` 실제 구조는 Supabase Edge Function(리포 밖) 산물이라 확인 못 함. 서버 코드가 `required`/`reasons` 로 읽는 것이 계약 근거.
- **라이브 확인**(danger 삭제 전제, 안전 직결이라 필수):
  1. 실제 `/weather/now` 응답에 `work_stop.required` 가 오는지(개발자도구 네트워크)
  2. **기준 초과 상황에서 배지가 빨강 「작업중지」로 뜨는지**
  3. 정보 없을 때 회색 「판정 불가」(초록 아님)
  - 확인되면 §66 danger 삭제 + "작업중지 표시가 기상 기준을 반영한다" 로 문구 전환.

---

## 2. 라이브 확인 체크리스트 (danger/warn 삭제 전제)

- [ ] **§32**: 최고관리자(role 001)로 `/alert-messages` 목록 200 (과거 404)
- [x] **§67-서버**: 대시보드 「작업중지 기준」 카드에 제37조 4개 항목 표시 (스크린샷 확인)
- [ ] **§67-화면**: (PR #31 배포 후) 항목 설명이 JSON 아닌 자연어("순간풍속 초당 10m 이상" 등)
- [ ] **§66**: (PR #30 배포 후) 기준 초과 시 빨강 「작업중지」 / 정상 시 초록 / 정보 없을 시 회색 「판정 불가」

---

## 3. 검증 한계 (정직 고지)

- §32: 코드·배포는 실측 확인. HTTP 실동작 미확인(네트워크 차단 환경).
- §67: 서버 v1.3.2·화면 PR #31 모두 배포. 서버측 항목 표시는 라이브 스크린샷 확인, 화면 자연어 표시는 PR #31 배포 후 확인 대기.
- §66: `tsc` 구문 통과 + 로컬 재현 후 최소 수정. 브라우저 동작·`work_stop` 실제 구조 미확인. PR #30 병합·배포됨.
- 세 건 모두 §2 잔여 체크가 통과되어야 LEDGER 반영 가능.

---

## 4. 요청

1. §2 체크리스트 잔여 항목 라이브 확인.
2. 확인된 건만 LEDGER 갱신(§32 danger·§67 warn·§66 danger).
3. §66 은 **safe 대장 §66 소유** — PR #30 병합·배포 완료. 라이브 확인만 남음.
