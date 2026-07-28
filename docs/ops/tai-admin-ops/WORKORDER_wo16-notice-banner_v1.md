---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-16 통합 공지 배너
version: 1
status: ACTIVE
owner: taiwang
---

# WO-16 — 통합 공지 배너 (NoticeBanner)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P2 WO-16
- **오브젝트:** notice_banner(신설) + 어드민 CRUD + 채널별 공개 조회
- **닫는 시나리오:** S16(한 곳에서 등록한 공지를 marketing·safe 두 채널에 노출)

---

## 1. 현황 (실측 — 범위 판정)

- `posts`(25컬럼): category·title·content·prec_id/prec_link·is_pinned·view_count. → **콘텐츠/블로그/판례 게시물**(산재판례 등). 노출기간·채널타깃·배너위치 없음.
- **운영 공지 배너와 성격 다름** → posts 재사용 부적합. 전용 테이블 신설.

**요구(사용자 확정):** taieng.co.kr(마케팅)·safe.taieng.co.kr(SaaS) **두 채널 공지를 한 곳에서 관리**. 공지 하나를 한쪽/양쪽에 노출.

## 2. 설계 — 채널 타깃 통합 공지

**채널 타깃은 ARRAY 방식**(메모리 원칙: COMMON 섹터 없음, 다중 적용은 ARRAY). `channels TEXT[]` = MARKETING·SAFE 조합.

**테이블(신설, RLS off):**
- `notice_banner`: id, title, body, channels(text[] — MARKETING|SAFE), banner_type(INFO|WARNING|MAINTENANCE|EVENT), link_url, link_label, starts_at, ends_at, priority(int), enabled(bool), created_by, created_at, updated_at.

**`services/notice_svc.py`(신설):**
- `list_admin(channel?, enabled?)`: 어드민 목록(필터).
- `create/update/delete/toggle`: CRUD.
- `active_for_channel(channel)`: 공개용 — 해당 채널 포함(channels @> [channel]) + enabled + 기간 내(starts_at≤now≤ends_at, null 허용). priority desc 정렬.

## 3. 엔드포인트

**어드민:**
- `GET/POST /notices` — 목록·생성.
- `PATCH /notices/{id}` — 수정.
- `PATCH /notices/{id}/toggle` — 활성 토글.
- `DELETE /notices/{id}` — 삭제.

**공개(marketing·safe가 호출):**
- `GET /notices/active?channel=MARKETING|SAFE` — 채널 현재 노출 공지.

## 4. 완료 판정 (IMPLEMENTED)

- notice_banner, notice_svc, 라우터, 등록.
- 채널 ARRAY 타깃 + 기간·priority 필터. active_for_channel 정확.
- `/health` 200, 배포 SUCCESS. 목업 공지 삽입→채널 조회→롤백 검증.

## 5. 산출물

1. 마이그레이션: notice_banner
2. `services/notice_svc.py`
3. `routers/notice.py`
4. router_registry 등록(external)
