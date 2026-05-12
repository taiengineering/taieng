# TAI Frontend MEMORY — 2026-04-01 야간 마감

> 작성: Claude (CTO/Architect 창)
> 커밋 범위: e5c90c7 → b50751d

---

## 1. Railway 502 오류 — legal_engine.py f-string 백슬래시 SyntaxError

**원인**: Python 3.11에서 f-string 내부 백슬래시(`\uXXXX`) 사용 불가 (3.12부터 허용)

**수정 대상 2곳 (백엔드 창 작업 필요)**
```python
# 수정 1 — _get_construction_summary() 약 891번 라인
# 현재 (오류)
basis_parts = [f"{site_label} {int(threshold/100_000_000)}억원 {'\uc774\uc0c1' if amount >= threshold else '\ubbf8\ub9cc'}"]
# 수정
_cmp_label = "이상" if amount >= threshold else "미만"
basis_parts = [f"{site_label} {int(threshold/100_000_000)}억원 {_cmp_label}"]

# 수정 2 — create_inspection_sets_from_legal() cycle_base_guide 라인
# 현재 (오류)
f"마지막 점검일로부터 {cycle_value}{'\\ub144' if cycle_unit == 'year' else '\\uac1c\\uc6d4'}마다"
# 수정
f"마지막 점검일로부터 {cycle_value}{'년' if cycle_unit == 'year' else '개월'}마다"
```
→ **API 현재 502 상태. 백엔드 창에서 수정 후 push 필수**

---

## 2. 로그인 구조 재정비 완료 (F-AUTH-001)

### 확정 접근 권한 정책

| role | 이름 | admin | tadmin | 앱 |
|------|------|:-----:|:------:|:--:|
| 001 | 최고관리자 | ✅ | ❌ admin 안내 | - |
| 002 | 관리자 | ✅ | ❌ admin 안내 | - |
| 003,005,007~013,015~016,020~021,GRP_* | 안전관리자 등 | ❌ | ✅ | - |
| **004,006,014,022** | **작업자류** | **❌** | **❌ 앱 안내** | **✅** |

### 수정 파일 (커밋 b50751d)
- `admin/full-version/html/horizontal-menu-template/auth-login-cover.html`
  - `ADMIN_ALLOWED_ROLES = ['001', '002']`
  - role 불일치 시: 빨간 alert + tadmin 링크 안내
  - cross-domain 자동 이동 완전 제거
  - 로그인 성공 → `/html/horizontal-menu-template/index.html` (절대경로)

- `tadmin/full-version/html/horizontal-menu-template/auth-login-cover.html`
  - `ADMIN_ONLY_ROLES = ['001', '002']` → 노란 alert + admin 링크
  - `APP_ONLY_ROLES = ['004', '006', '014', '022']` → 파란 alert + 앱 안내
  - 나머지 role → 정상 로그인 → tadmin index
  - cross-domain 자동 이동 완전 제거

### 무한루프 제거 원인
- **기존 문제**: `tadmin` 로그인 후 `admin.taieng.co.kr`로 cross-domain 이동 → admin localStorage에 token 없음 → auth-guard → login → 루프
- **해결**: 각 도메인은 자기 localStorage만 사용. 다른 도메인으로 자동 이동 없음.

---

## 3. _redirects 수정 (커밋 e5c90c7)

`/site/nexas-template/*` 경로를 리다이렉트 제외 (200 passthrough)

```
/site/nexas-template/* /site/nexas-template/:splat 200
/ /home/ 302
/tadmin  /tadmin/full-version/html/horizontal-menu-template/index.html 302
/tadmin/ /tadmin/full-version/html/horizontal-menu-template/index.html 302
```

**미해결**: `taieng.co.kr/site/nexas-template/nexas/index.html` 접속 시 여전히 `/home/`으로 리다이렉트됨
→ Cloudflare 대시보드 다른 규칙 또는 Worker가 원인으로 추정. 내일 확인 필요.

---

## 4. Nexas 템플릿 업로드 완료

**저장 위치**: `site/nexas-template/nexas/` (HTML), `site/nexas-template/documentation/` (assets)

**파일 구조 확인**: index-1~6.html, service.html, contact.html 등 정상 push됨

**접근 문제**: Cloudflare가 모든 URL을 `/home/`으로 리다이렉트 중 → 내일 Cloudflare 설정 확인 필요

---

## 5. DB 점검 결과 (모두 정상)

| 항목 | 상태 |
|------|------|
| construction_work_type 정비 | 건축1/토목1/공통98, NULL 0개 ✅ |
| law_master 미연결 | 0개 ✅ |
| factory_features | 28개 feature 정상 ✅ |
| system_codes plan_code | STARTER~CUSTOM 4개 ✅ |
| system_codes sector | BUILDING~SPECIAL 4개 ✅ |
| factories.sector | INDUSTRY 매핑 완료 ✅ |

---

## 6. 커밋 요약

| 커밋 | 내용 |
|------|------|
| `e5c90c7` | _redirects nexas-template passthrough 추가 |
| `c1db1d7` | auth 로그인 구조 재정비 1차 (cross-domain 제거) |
| `b50751d` | auth 접근 권한 확정 (admin 001+002, 앱전용 004+006+014+022) |

---

## 7. 내일 작업 목록

### 🔴 긴급 (오늘 미완료)
1. **Railway 502 수정** — legal_engine.py f-string 2곳 수정 (백엔드 창)
   - `_get_construction_summary()` 891번 라인
   - `create_inspection_sets_from_legal()` cycle_base_guide 라인

2. **Cloudflare 리다이렉트 문제 해결**
   - `taieng.co.kr/site/nexas-template/nexas/` 접근 시 `/home/`으로 리다이렉트되는 문제
   - `dash.cloudflare.com` → taieng.co.kr → Rules → Redirect Rules 확인
   - Worker 존재 여부 확인

### 🟠 우선 작업
3. **Nexas 커스터마이징 착수**
   - 포지션별 페이지 기획 확정 (제조/건설/건물/중대재해/가격)
   - index-1~6 중 TAI에 맞는 베이스 템플릿 선정
   - 스토리텔링 구조 설계

4. **admin index.html auth-guard 추가**
   - 현재 token 없으면 auth-login으로 이동하는 로직은 있으나
   - role 001, 002 아닌 token이 있을 경우 처리 누락 확인

### 🟡 예정 작업
5. **공지예외주장 제출 (2026-04-28 필수)**
   - patent.go.kr 접속
   - 참조번호: 110-2026-0056330

6. **Cloudflare Zero Trust Access 설정**
   - taieng.co.kr → hetto@kakao.com Only
   - dash.cloudflare.com → Zero Trust → Access → Self-hosted

7. **12개 법령 수집** (data.go.kr API)
   - 근로기준법, 소음진동관리법, 악취방지법 등

8. **feature-flags API 백엔드 구현**
   - `/feature-flags/?sector=&plan=` 엔드포인트 (Railway 502 해결 후)

9. **construction_work_type NULL 정비** (B-CON-002)
   - 공통 98개 룰에 적절한 work_type 매핑
