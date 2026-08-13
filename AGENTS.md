# AGENTS.md — taieng 라이브맵 (READ FIRST)

> ⚠️ 이 레포의 `nexas`(구 마케팅)는 **라이브가 아니다.** taieng.co.kr 라이브 마케팅은 별도 레포 `tai-www`(Astro)가 서빙한다. 혼동 주의.

## 라이브 매핑 (실측 2026-08-13)

| 라이브 도메인 | 실제 서빙 레포/브랜치/디렉터리 |
|---|---|
| `taieng.co.kr`, www | **`tai-www`** / main / (루트, Astro) ← 여기서 수정 |
| `old.taieng.co.kr` | 이 레포 과거 `nexas/` → CF `taieng-new` (자동배포 OFF, 동결) |

**taieng.co.kr 라이브 마케팅 수정은 이 레포가 아니라 `tai-www`에서 한다.**

## 이 레포에서 nexas가 사라진 이유

- `nexas/`는 `old.taieng.co.kr`만 서빙하던 구자산이고, CF `taieng-new`는 자동배포 OFF라 이 레포에 커밋해도 배포되지 않았다.
- 2026-08-13 `nexas/`·`nexas_sample/`·`legacy-taieng-public/`·`docs/`를 `legacy-archive` 브랜치(스냅샷 `692739d`)로 격리하고 main에서 제거했다.
- 구 마케팅 화면 육안 비교: `old.taieng.co.kr` (마지막 배포본 박제). 코드 비교: `git checkout legacy-archive`.
- 과거 프로젝트 문서 `docs/`(1,693개)는 `tai-www/docs`로 이관 완료.

## 이 레포에 남아있는 것 (활성)

`apps/`, `packages/`, `cloudflare-worker/`, `functions/`, `scripts/`, `documentation/`, `naver_monitor.py`(네이버 지식iN 모니터), `railway.toml` 등 — nexas 외 활성 자산. 이들은 격리 대상이 아니다.

## 절대 규칙

1. **taieng.co.kr 라이브 마케팅 = `tai-www` 레포.** 이 레포의 nexas(legacy-archive)를 고쳐 라이브 반영을 기대하지 말 것.
2. `taieng-new`(old.taieng.co.kr) 자동배포는 OFF 유지.
