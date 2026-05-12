# 메뉴 축소 작업지시서
## 담당: Cursor
## 파일: `scripts/apply_menu_restructure.py`

---

## 문제

탑메뉴 10개 → 화면 너비 초과로 엔진설정 등 마지막 항목들이 잘려서 사라짐.

## 해결

문서관리 최상위 메뉴를 제거하고, 하부 메뉴 2개를 계약관리 하부로 이동.  
**9개 최상위 메뉴**로 축소 (대시보드 + 드롭다운 8개).

---

## 변경 후 MENU_SPEC (전체)

1. 대시보드 (`tabler-smart-home`)
2. 회원관리 (`tabler-users`)  
   → 회원관리 / 권한관리 / 알림설정 / 회사관리
3. 계약관리 (`tabler-file-invoice`)  
   → 계약관리 / 견적관리 / 문의관리 / **발행문서** / **요청문서** ← 문서관리에서 이동
4. 산업안전 (`tabler-building-factory`)
5. 건설안전 (`tabler-crane`)
6. 교육관리 (`tabler-school`)
7. 위험관리 (`tabler-alert-triangle`)
8. 업체연결 (`tabler-users-group`)
9. 엔진설정 (`tabler-cpu`)

문서관리 최상위는 완전히 제거.

---

## 파일별 active 변경

- `doc-submit.html` → 계약관리 + 발행문서
- `doc-report.html` → 계약관리 + 요청문서
- 나머지는 기존과 동일

---

## 작업

`MENU_SPEC` 수정 후:

```bash
python3 scripts/apply_menu_restructure.py
```

`admin/full-version/html/horizontal-menu-template/*.html` 의 `<ul class="menu-inner">` 일괄 갱신.
