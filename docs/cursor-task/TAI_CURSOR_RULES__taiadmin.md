# TAI Cursor / Claude Code 운영 규칙

> 이 파일은 `.cursorrules` 또는 Claude Code 시작 프롬프트로 사용합니다.  
> 최종 업데이트: 2026-03-27

---

## 필수 선행 작업

작업 시작 전 반드시 아래 파일을 읽으세요:

1. **메인 컨텍스트**: `docs/TAI_MASTER_CONTEXT.md`
2. **비즈니스 기획서**: `docs/TAI_서비스_비즈니스_기획서_v1.md`

---

## 프로젝트 구조

```
tai-admin/          ← 프론트엔드 (HTML + Bootstrap)
  admin/full-version/html/horizontal-menu-template/  ← 어드민 페이지
  tadmin/full-version/html/horizontal-menu-template/ ← 고객 페이지
  assets/js/tai/    ← 공통 JS (api.js, toast.js, globals.js)
  docs/             ← 기획서/컨텍스트 문서
  logs/             ← 날짜별 작업일지

tai-api/            ← 백엔드 (FastAPI)
  routers/          ← API 라우터
  db/               ← Supabase 클라이언트
  main.py           ← 라우터 등록
```

---

## 백엔드 코딩 규칙

```python
# 1. DB 연결
from db.supabase_client import get_supabase
supabase = get_supabase()

# 2. 라우터 기본 구조
from fastapi import APIRouter, HTTPException, Query
router = APIRouter(prefix="/my-endpoint", tags=["태그명"])

# 3. 에러 처리
raise HTTPException(status_code=404, detail="설명")

# 4. 시간
from datetime import datetime, timezone
datetime.now(timezone.utc).isoformat()

# 5. main.py에 추가 필수
from routers.my_module import router as my_router
app.include_router(my_router)
```

---

## 프론트엔드 코딩 규칙

```javascript
// 1. 인증 체크 (모든 페이지 최상단)
var token = localStorage.getItem('access_token');
if (!token) location.replace('https://admin.taieng.co.kr/html/horizontal-menu-template/auth-login-cover.html');

// 2. API 호출
var data = await apiCall('GET', '/endpoint?param=value');
var data = await apiCall('POST', '/endpoint', { key: value });
var data = await apiCall('PATCH', '/endpoint/id', { key: value });
var data = await apiCall('DELETE', '/endpoint/id');

// 3. 알림
showToast('success', '성공 메시지');
showToast('error', '에러 메시지');
showToast('warning', '경고 메시지');

// 4. 페이지네이션
renderPagination(total, currentPage, pageSize, function(p) {
  currentPage = p;
  loadData();
});

// 5. 로그아웃
onclick="doLogout()"

// 6. XSS 방어
function esc(s) {
  if (s == null) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
}

// 7. URL 파라미터 인코딩 (특수문자 포함 가능한 값)
encodeURIComponent(value)
```

---

## 파일 생성 규칙

### 새 어드민 페이지 생성 시
1. 탑메뉴: `factory-list.html` 기준으로 복사
2. active 메뉴 설정
3. 슬라이드 패널: `.tai-side-panel` + `.open` 클래스
4. JS 파일 로드 순서:
```html
<script src="../../assets/js/tai/api.js"></script>
<script src="../../assets/js/tai/toast.js"></script>
<script src="../../assets/js/tai/globals.js"></script>
<script src="../../assets/js/utils.js"></script>
```

### 새 API 라우터 생성 시
1. `routers/` 폴더에 파일 생성
2. `main.py`에 import + include_router 추가
3. prefix는 `/케밥-케이스` 형식

---

## 커밋 메시지 규칙

```
feat(파일명): 기능 추가
fix(파일명): 버그 수정
refactor(파일명): 리팩토링
docs(파일명): 문서 수정
```

---

## 절대 하지 말 것

- ❌ 상대경로 URL (예: `../auth-login-cover.html`)
- ❌ 브라우저/Chrome으로 백엔드 테스트
- ❌ `location.href` 로 리다이렉트 (→ `location.replace()` 사용)
- ❌ `factory_process.py` / `factory_process_v2.py` 수정 (v3만 사용)
- ❌ 하드코딩 Mock 데이터
- ❌ API 기본 URL 직접 입력 (api.js에서 관리)
