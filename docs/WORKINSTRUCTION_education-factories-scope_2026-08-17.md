# 작업지시서 — /education·/factories 회사 스코프 (P13)

> 2026-08-17 · 스코프 클러스터 마지막 2건 · 대상 `tai-api`
> 처리: **Cursor / Claude Code** (보안 변경 · 라이브 테스트 필요)
> 근거: `DESIGN_safe-company-scope-p13_2026-08-17.md` + 정본 `routers/leader_scope.py`
> 공통 헬퍼(아래)는 contracts.py PR #150 에 이미 들어간 것과 동일. shared 모듈로 뽑아 재사용 권장.

## 공통 패턴
```python
from routers.auth import get_current_user
def _scope(sb, role_code):
    r = sb.table("role_data_scope").select("scope_type").eq("role_code", role_code).limit(1).execute()
    return (r.data[0]["scope_type"] if r.data and r.data[0].get("scope_type") else "TEAM")
def _is_admin(s): return s == "ALL"
```
규칙: `ALL`(총관리자) → 무제한 / 그 외 → 토큰 company_id 강제·소유권 404. **어드민 회귀 금지.** safe 어드민은 항상 토큰 전송(안전).

---

## 1. routers/factories.py (18.7KB, → v2.5.0)

12개 엔드포인트 전부 `current = Depends(get_current_user)` + 가드. 헬퍼:
```python
def _ensure_factory_own(sb, factory_id, current):
    if _is_admin(_scope(sb, current.get("role_code"))): return
    f = sb.table("factories").select("company_id").eq("id", factory_id).limit(1).execute()
    if not f.data or f.data[0].get("company_id") != current.get("company_id"):
        raise HTTPException(404, "시설을 찾을 수 없습니다")
```

| 엔드포인트 | 조치 |
|---|---|
| `GET /factories` (목록) | 비-ALL: `company_id = 토큰` 강제(클라 파라미터 덮어씀). **§patterns 핵심 — 타사 시설목록 차단.** |
| `POST /factories` (생성) | 비-ALL: `req.company_id = 토큰` 강제(남의 회사에 시설 생성 차단). |
| `GET/PATCH/DELETE /factories/{id}` | `_ensure_factory_own(id)` 먼저. |
| `GET /factories/{id}/users` · `/buildings` · `/contacts` | `_ensure_factory_own(id)` 먼저(중첩 자원도 타사 열람 차단). |
| `POST/PATCH/DELETE /factories/{id}/contacts[/{cid}]` | `_ensure_factory_own(id)` 먼저. |
| `POST /factories/{id}/legal` | `_ensure_factory_own(id)` 먼저. |

**같이 정리**: 기존 깨진 메시지 `등록뙀`→`등록됐`, `수정똥`→`수정됐`, `삭제똥`→`삭제됐`, `추가똥`→`추가됐`, `비활성화똥`→`비활성화됐`. (§16 계열)
이벤트 트리거·법령판정 로직 불변.

---

## 2. routers/education.py (29.7KB)

로컬 `get_supabase` 주입은 그대로 두고, 각 엔드포인트에 `current = Depends(get_current_user)` 추가. `education_history`·`education_setting` 은 **company_id 컬럼이 없어 factory 경유로 회사 판정**한다(위 `_ensure_factory_own` 재사용).

| 엔드포인트 | 조치 |
|---|---|
| `GET /education-master`·`/education-master/{code}` | 회사 무관 카탈로그 — **인증만** 추가(스코프 불필요). |
| `GET /education/company-effective-link` · `/company-settings` · `PUT/DELETE /company-settings/{id}` | 비-ALL: `company_id = 토큰` 강제(클라 파라미터 무시). |
| `GET /education-settings/{factory_id}[/{code}]` · `PATCH …/{code}` | 비-ALL: `_ensure_factory_own(factory_id)` 먼저. |
| `GET /education-history` · `/summary` | 비-ALL: `factory_id` 필수화하고 `_ensure_factory_own(factory_id)`. (factory 미지정 전사 조회는 ALL 만.) |
| `POST /education-history` · `/pending` | 비-ALL: `body.factory_id` 를 `_ensure_factory_own` 로 검증. |
| `GET/PATCH /education-history/{id}` · `/{id}/files`(GET/POST/DELETE) | 대상 이력의 `factory_id` 조회 → `_ensure_factory_own` 로 검증(타사 이력·증빙 차단). |

교육시간 검증·업로드·병합 로직 불변.

---

## 완료 판정 (라우터마다 라이브 2종, 둘 다)
1. **고객 토큰**: 목록·설정·이력이 자사(자사 시설)만. 남의 company_id/factory_id/이력 id → 404 또는 자사만.
2. **어드민(ALL) 토큰**: 전사 조회·생성·수정 종전대로(회귀 없음).
운영 로그: project 7c3ab53b… / tai-api-prod 4cf52678… / production 9dacb6f0….

## 착수 전 확인 (contracts 때와 동일)
두 라우터의 엔드포인트를 **사용자 토큰 없이** 부르는 비-사용자 호출자(웹훅·크론·내부 HTTP)가 없는지 점검. 내부는 대부분 테이블 직접 접근이라 무관하나, `/factories` 는 코어라 대시보드·진단·작업일정 등 여러 화면이 쓰므로 **토큰 전송 여부 확인 후** required-auth 적용.

## 헬프센터
반영·확인 후 교육·시설 관련 문서의 회사 스코프 관련 경고 정리 가능(별건).
