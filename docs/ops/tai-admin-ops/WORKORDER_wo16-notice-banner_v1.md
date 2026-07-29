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
- **최종:** VERIFIED. marketing·safe 두 채널 통합 공지.

---

## 1. 요구 (사용자 확정)

taieng.co.kr(마케팅)·safe.taieng.co.kr(SaaS) **두 채널 공지를 한 곳에서 관리**. 공지 하나를 한쪽/양쪽 노출. posts(콘텐츠/판례)는 성격 달라 전용 테이블 신설.

## 2. 구현 (완료)

**테이블(신설, RLS off, 적용됨):**
- `notice_banner`: title, body, **channels text[]**(MARKETING|SAFE), banner_type(INFO|WARNING|MAINTENANCE|EVENT), link_url, link_label, starts_at, ends_at, priority, enabled.
- 마이그레이션 `20260728174324_create_notice_banner.sql`. GIN 인덱스(channels).

**`services/notice_svc.py`** (커밋 860acc1):
- `list_admin(channel?, enabled?)`, `create/update/toggle/delete`.
- `active_for_channel(channel)`: channels @> [channel] + enabled + 노출기간 내(null 허용). priority desc.

**`routers/notice.py`** (커밋 9a2f978): 어드민 CRUD + `GET /notices/active?channel=`. external 등록 34fe5ef.

## 3. 검증 결과

DO block 롤백 테스트(4건 삽입 후 채널별 집계):

| 항목 | 상태 | 근거 |
|---|---|---|
| MARKETING 채널 노출 | VERIFIED | 마케팅전용+공통=2 (기대 2) |
| SAFE 채널 노출 | VERIFIED | safe전용+공통=2 (기대 2) |
| 만료 공지 제외 | VERIFIED | ends_at 과거 건 노출 0 (기대 0) |
| ARRAY 타깃(@>) | VERIFIED | channels @> [channel] 정확 |
| 무오염 | VERIFIED | residual 0 |
| 앱 기동·라우팅 | VERIFIED | 배포 SUCCESS + `/health` |

## 4. 채널 사용

- marketing 사이트: `GET /notices/active?channel=MARKETING`.
- safe 앱: `GET /notices/active?channel=SAFE`.
- 어드민에서 공지 1건 등록 시 channels=['MARKETING','SAFE']면 양쪽 동시 노출.

## 5. 산출물 (커밋)

1. `supabase/migrations/20260728174324_create_notice_banner.sql`
2. `services/notice_svc.py`
3. `routers/notice.py`
4. `router_registry/external.py` (notice 등록)
