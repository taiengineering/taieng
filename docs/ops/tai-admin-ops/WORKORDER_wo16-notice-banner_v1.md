---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-16 통합 공지 배너
version: 2
status: DONE
owner: taiwang
---

# WO-16 — 통합 공지 배너 (NoticeBanner)

- **작성일:** 2026-07-28 (v2: 검증 완료)
- **Goal:** G-ms4je4z3-33eada
- **최종:** VERIFIED. marketing·safe 두 채널 통합 관리.

---

## 1. 현황 (실측 — 범위 판정)

- `posts`(25컬럼): 콘텐츠/블로그/판례(prec_link·산재판례). 노출기간·채널타깃 없음 → 부적합.
- **요구(사용자 확정):** taieng.co.kr(마케팅)·safe.taieng.co.kr(SaaS) 두 채널 공지 한 곳 관리. → 전용 테이블 신설.

## 2. 구현 (완료)

**테이블(신설, RLS off, 적용됨):**
- `notice_banner`: title, body, **channels text[]**(MARKETING|SAFE), banner_type(INFO|WARNING|MAINTENANCE|EVENT), link_url/label, starts_at/ends_at, priority, enabled.
- GIN 인덱스(channels) + enabled + window 인덱스. 마이그레이션 `20260728174324_create_notice_banner.sql`.

**`services/notice_svc.py`** (커밋 860acc1):
- `list_admin(channel?, enabled?)`, `create/update/toggle/delete`.
- `active_for_channel(channel)`: channels @> [channel] + enabled + 기간 내(starts≤now≤ends, null 허용). priority desc.
- 채널·배너유형 검증.

**`routers/notice.py`** (커밋 9a2f978): 어드민 CRUD + `GET /notices/active?channel=`(공개). external 등록 34fe5ef.

## 3. 검증 결과 (롤백 테스트)

| 항목 | 상태 | 근거 |
|---|---|---|
| 채널 ARRAY 타깃 | VERIFIED | MARKETING 노출 2(전용+공통), SAFE 노출 2(전용+공통) |
| 노출기간 필터 | VERIFIED | ends_at 지난 공지(pri99) 제외 확인 |
| priority 정렬 | VERIFIED | MARKETING 최상단=전용(pri5) > 공통(pri1) |
| 무오염 | VERIFIED | residual 0 |
| 앱 기동·라우팅 | VERIFIED | 배포 SUCCESS(34fe5ef) + `/health` |

## 4. 채널 연동 (후속)

- marketing 사이트: `GET /notices/active?channel=MARKETING` 호출 → 상단 배너.
- safe 앱: `GET /notices/active?channel=SAFE` 호출 → 상단 배너.
- 프론트 배선은 WO-20(Vue3 이식) 또는 각 사이트 작업에서.

## 5. 산출물 (커밋)

1. `supabase/migrations/20260728174324_create_notice_banner.sql`
2. `services/notice_svc.py`
3. `routers/notice.py`
4. `router_registry/external.py` (notice 등록)
