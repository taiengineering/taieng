# 작업지시서 — §54·§61 size 상한 재발 (진단/건설 선택기)

> 2026-08-18 · LEDGER §54[높음]·§61[높음] · 대상 `tai-api`
> 처리: **Cursor / Claude Code** (factories.py 는 P13 스코프 가드가 든 코어 보안 라우터 → 전체 재작성 금지, 외과적 1줄만)
> 근거: LEDGER 실측 인용 + size 상한 검색에서 두 라우터의 `le=100` 확인.
> 패턴: 화면이 `size=200` 을 보내는데 서버 상한이 `le=100` → 422 → ①(res.ok 미검사)로 빈 배열 → "없음". §68·§31 과 동일 계열.

## 1. §54 — 진단 1단계 시설 선택 불능 (factories)
- 화면 `diagnosis-step1`: `GET /factories?size=200`
- 서버 `routers/factories.py` 목록(get_factories): `size: int = Query(default=20, ge=1, le=100)`
- 결과: 422 → 시설 0개 → "시설이 선택되지 않았습니다" 상시(라이브 5,475건).

**수정(외과적, 1곳만)**: get_factories 의 `le=100` → **`le=500`** (§68 users 와 동일 상향).
- **P13 회사 스코프 가드(`_forced_company_id`·`_ensure_factory_own` 등)는 절대 건드리지 말 것.** size 파라미터 한 줄만.
- 비-ALL 은 이미 company_id 강제라 자사 시설만(테넌트당 유한), ALL 은 페이지네이션 유지.

## 2. §61 — 법령진단 2단계 연동 "등록된 공정이 없습니다" (processes)
- 화면 `construction-process-list`: 공정 목록을 `size=200` 로 요청(공정 6건 실재).
- 서버 공정 목록 라우터의 `size` 상한이 `le=100` 이면 동일하게 422 → 빈 목록.

**수정**: 해당 공정 목록 엔드포인트(`routers/*process*` 의 목록 GET)의 `size` 상한을 **`le=500`** 으로 상향(먼저 실제 상한을 직독해 확인 후, 100이면 상향).
- 공정은 시설/현장 단위라 유한 → 상한 상향 안전.

## 완료 판정 (라이브)
1. **§54**: 진단 1단계 진입 시 시설 목록이 채워지고, 배너가 사라지며 진단 실행이 첫 줄에서 되돌아가지 않음.
2. **§61**: 2단계 연동 화면에 공정 6건이 표시됨.
운영 로그: project 7c3ab53b… / tai-api-prod 4cf52678… / production 9dacb6f0….

## 배포
main push → Railway 자동배포, `railway_list_deployments` SUCCESS 확인, `/health` 200 유지.

## 참고 — size 상한 패턴 전수
이미 조치: §68 `/users`(500)·§31 `/equipment-assets`(1000)·㉙ `/work-schedules`(이미 500).
남음: §54 `/factories`·§61 공정 (이 지시서). 근본적으론 화면이 상한을 모른 채 큰 값을 보내는 계약 문제 —
장기적으로는 목록 계약(상한·페이지네이션)을 공통화하는 편이 낫다.
