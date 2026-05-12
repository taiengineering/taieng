# 크론관리 메뉴 추가 작업 지시서
## 담당: Cursor
## 레포: tai-admin

---

## 작업 내용

`admin/full-version/html/horizontal-menu-template/` 아래 전체 HTML 파일에서
엔진설정 서브메뉴 마지막에 **크론관리** 메뉴를 추가한다.

---

## 찾아서 교체할 문자열

### 찾을 문자열 (before)
```html
<li class="menu-item"><a class="menu-link" href="engine-education.html"><div>교육</div></a></li></ul></li>
```

### 교체할 문자열 (after)
```html
<li class="menu-item"><a class="menu-link" href="engine-education.html"><div>교육</div></a></li><li class="menu-item"><a class="menu-link" href="cron-list.html"><div>크론관리</div></a></li></ul></li>
```

---

## 대상 파일

`admin/full-version/html/horizontal-menu-template/` 아래 `.html` 파일 **전체**

---

## 작업 명령

```bash
cd admin/full-version/html/horizontal-menu-template

# macOS/Linux
sed -i '' 's|<li class="menu-item"><a class="menu-link" href="engine-education.html"><div>교육<\/div><\/a><\/li><\/ul><\/li>|<li class="menu-item"><a class="menu-link" href="engine-education.html"><div>교육<\/div><\/a><\/li><li class="menu-item"><a class="menu-link" href="cron-list.html"><div>크론관리<\/div><\/a><\/li><\/ul><\/li>|g' *.html

# Windows (PowerShell)
Get-ChildItem *.html | ForEach-Object {
  $content = Get-Content $_.FullName -Raw -Encoding UTF8
  $content = $content -replace '<li class="menu-item"><a class="menu-link" href="engine-education.html"><div>교육</div></a></li></ul></li>', '<li class="menu-item"><a class="menu-link" href="engine-education.html"><div>교육</div></a></li><li class="menu-item"><a class="menu-link" href="cron-list.html"><div>크론관리</div></a></li></ul></li>'
  Set-Content $_.FullName $content -Encoding UTF8
}
```

---

## 확인

```bash
grep -l "cron-list.html" *.html | wc -l
# 전체 HTML 파일 수와 동일한 숫자가 나와야 함
```

---

## git push

```bash
git add admin/full-version/html/horizontal-menu-template/*.html
git commit -m "feat: 엔진설정 메뉴에 크론관리 추가"
git push origin main
```

---

## 완료 기준
- [ ] 전체 HTML 파일에 크론관리 메뉴 추가
- [ ] `cron-list.html` 클릭 시 크론 관리 페이지로 이동 확인
