# WORKORDER — §66 safety-dashboard `triggered` 키 정합

> 발행: 기획창 2026-08-20. 실행: Cursor(로컬 str_replace). 사유: 대상 파일 22KB(>20KB) + 한국어 주석 다수 → MCP 전체 재작성 금지 대상.

## 대상
- repo: `tai-admin`
- file: `vue3/src/pages/safety-dashboard/useSafetyDashboard.ts`
- function: `loadWeather()`
- 착수 시점 sha(참고): `3eb8730a` — 편집 직전 로컬 최신으로 재확인할 것

## 문제 (검증된 사실)
서버 `routers/weather.py` v1.3.3 와 엣지 `kma-weather` v1.7.0 **양쪽 모두** 작업중지 사유 배열 키가 `triggered` 다.
- 엣지 `action:now` → `work_stop: { required, level, triggered:[{code,name,value,threshold}], message }`
- 서버는 `weather_data` 를 손대지 않고 통과시킴 → 화면에 `work_stop.triggered` 그대로 도달

그런데 화면 `loadWeather()` 는 `stop.reasons` 를 읽는다. `reasons` 키는 존재하지 않으므로 항상 `[]` → 강풍/강우/강설 구체 사유가 유실되고 배지에 "작업중지 기준 초과"만 뜬다. (파일 내 주석 `work_stop = { required, reasons:[...] }` 도 옛 계약이라 오기.)

이것이 §66 의 마지막 미연결 선. 서버 PR#167 은 전구를 끼웠을 뿐, 화면이 옛 자리(`reasons`)에서 스위치를 찾고 있었다.

## 변경 ① — 사유 배열 키 (str_replace 1곳)
old:
```ts
        const reasons = (hasStop && Array.isArray(stop.reasons)) ? stop.reasons : []
```
new:
```ts
        const reasons = (hasStop && Array.isArray(stop.triggered)) ? stop.triggered
          : (hasStop && Array.isArray(stop.reasons)) ? stop.reasons : []
```
- 이후 `.map((r) => ... r.name || r.code || r.msg ...)` 및 `reasonText` 로직 **불변**. 엣지 `triggered[]` 가 `{code,name,...}` 라 `name`(한국어)이 그대로 렌더된다.

## 변경 ② — 오기 주석 정정 (같은 함수, 서버 계약 설명 주석)
`// 서버 계약(routers/weather.py): 작업중지 판정은 work_stop = { required: bool, reasons: [...] } 로 온다.`
→ `// 서버 계약(weather.py v1.3.3 / kma-weather v1.7.0): work_stop = { required, level, triggered:[{code,name,value,threshold}], message }. triggered 우선, reasons 는 하위호환 fallback.`

## 하지 말 것 (회귀 금지)
- `reasons` fallback 제거 금지 (하위호환 유지).
- `level` 도출 로직 불변: `!hasStop ? '' : (stopRequired ? 'stop' : 'normal')`. 정보 없음은 '정상'이 아니라 '판정 불가'(빈 level) 유지.
- `loadWeather()` 외 다른 함수/파일 변경 금지.

## 검증 (확인 한 줄 · 라이브)
safety-dashboard → 사업장 선택 → 풍속 10m/s↑ 또는 1시간 강수 1mm↑ 재현 시, 날씨 배지에 **"작업중지 기준 초과: 강풍"** 등 **구체 사유**가 뜨면 통과. 기준 이내면 "정상", 판정 정보 없으면 "판정 불가". (기준 초과 재현은 D — 실악천후 또는 엣지 주입 필요.)
push → Cloudflare Pages `taieng-tadmin` 자동배포.

## 맥락
§66 3끝단: 엣지 `triggered` ✅ · 서버 `triggered`(PR#167) ✅ · 화면 ← 이 변경으로 정합. 이후 기획창이 tai-admin main GET 으로 반영 검증.

## 별건 (이 지시서 범위 밖 — 통지 후보)
- ⓐ 엣지 `judgeWorkStop` 이 강풍·강우·강설 3종만 판정, **뇌전(THUNDER) 미판정**. criteria 카드는 4종. `now` 경로로 뇌전 미발동.
- ⓑ 서버 `_alert_type_from_work_stop` 이 `code`(영문) 우선 → 알림 title 영문화. raw `triggered` 엔 한국어 `name` 있음.
