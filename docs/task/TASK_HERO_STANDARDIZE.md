# 작업지시서: 표준 히어로 모듈 적용

**작업자:** Cursor  
**레포:** `taiengineering/taieng`  
**작업 디렉토리:** `nexas/`  
**작성일:** 2026-05-01  

---

## ██ 절대 규칙 ██

```
1. 히어로 섹션(페이지 최상단 첫 번째 <section>) 만 수정한다.
2. 히어로 아래의 모든 섹션은 단 한 줄도 건드리지 않는다.
3. 이 지시서에 적힌 것만 변경한다. 그 외는 전부 유지한다.
4. 임의 판단 금지. 판단이 필요한 상황이 오면 멈추고 보고한다.
5. 파일 1개 완료할 때마다 커밋한다.
```

---

## 히어로 섹션의 정의

각 파일에서 `<div id="tai-header"></div>` 바로 다음에 오는 **첫 번째 `<section>` 태그**가 히어로 섹션이다.  
히어로 섹션은 해당 `<section>`의 닫는 `</section>` 태그까지다.  
그 이후는 절대 건드리지 않는다.

---

## 표준 히어로 구조

작업 후 모든 히어로 섹션은 아래 구조를 사용한다.

### 타입 1: 배경 이미지형

```html
<section class="tai-hero tai-hero--image" id="[기존 id 유지]">
  <div class="tai-hero__bg" style="background-image:url('[이미지URL]')"></div>
  <div class="tai-hero__overlay tai-hero__overlay--left"></div>
  <div class="container">
    <div class="tai-hero__inner">
      <p class="tai-hero__eyebrow">[섹터명]</p>
      <h1 class="tai-hero__title">[제목줄1]<br><span class="accent">[강조부분]</span></h1>
      <p class="tai-hero__sub">[서브카피]</p>
      <div class="tai-hero__cta">
        <a class="tai-btn-pri" href="[경로]">[버튼1] →</a>
        <a class="tai-btn-sec" href="[경로]">[버튼2]</a>
      </div>
    </div>
  </div>
</section>
```

### 타입 2: 그라디언트형 (이미지 없음)

```html
<section class="tai-hero tai-hero--dark" id="[기존 id 유지]">
  <div class="container">
    <div class="tai-hero__inner">
      <p class="tai-hero__eyebrow">[섹터명]</p>
      <h1 class="tai-hero__title">[제목줄1]<br><span class="accent">[강조부분]</span></h1>
      <p class="tai-hero__sub">[서브카피]</p>
      <div class="tai-hero__cta">
        <a class="tai-btn-pri" href="[경로]">[버튼1] →</a>
        <a class="tai-btn-sec" href="[경로]">[버튼2]</a>
      </div>
    </div>
  </div>
</section>
```

---

## 표준 `<head>` CSS 링크

모든 파일의 `<head>` 안 CSS 링크 블록을 아래 순서로 맞춘다.  
상대경로는 파일 위치에 따라 `assets/` 또는 `../assets/`로 유지한다.

**있어야 하는 것 (없으면 추가):**
```html
<link rel="stylesheet" href="[경로]/assets/css/tai-brand.css">
<link rel="stylesheet" href="[경로]/assets/css/tai-main.css">
<link rel="stylesheet" href="[경로]/assets/css/tai-hero.css">
```
추가 위치: `responsive.css` 링크 바로 아래.

**제거해야 하는 것 (있으면 삭제):**
```html
<link rel="stylesheet" href="[경로]/assets/css/tai-hero-fix.css">
```

**나머지 CSS 링크는 순서 포함 그대로 유지한다.**

---

## 파일별 작업 지시

---

### 파일 1: `nexas/target/construction.html`

#### 현재 히어로 상태
Nexas 템플릿의 `.breadcrumb-area` 섹션 사용 중.

#### 작업 1-1: `<head>` CSS 링크 정리
위의 표준 `<head>` 규칙 적용.

#### 작업 1-2: 히어로 섹션 교체
`<div id="tai-header"></div>` 다음에 오는 첫 번째 `<section>` 전체를 찾아서 아래로 교체한다.

**삭제 대상** (이 패턴으로 시작하는 섹션 전체):
```
<section class="breadcrumb-area
```

**교체할 내용:**
```html
<section class="tai-hero tai-hero--image" id="construction-hero">
  <div class="tai-hero__bg" style="background-image:url('https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/build.png')"></div>
  <div class="tai-hero__overlay tai-hero__overlay--left"></div>
  <div class="container">
    <div class="tai-hero__inner">
      <p class="tai-hero__eyebrow">건설현장</p>
      <h1 class="tai-hero__title">
        오늘도 서류 먼저 쓰고,<br>
        <span class="accent">현장은 나중입니다.</span>
      </h1>
      <p class="tai-hero__sub">
        TBM, 위험성평가, 안전관리계획서, 일보...<br>
        서류에 묻혀 정작 현장을 못 봅니다.
      </p>
      <div class="tai-hero__cta">
        <a class="tai-btn-pri" href="../free-diagnosis.html">무료 법령진단 시작 →</a>
        <a class="tai-btn-sec" href="../fix-request.html?from=target-construction&type=general">도입 문의</a>
      </div>
    </div>
  </div>
</section>
```

#### 작업 1-3: `<style>` 블록 정리
`<head>` 안 `<style>` 블록에서 아래 클래스의 CSS 블록만 찾아 삭제한다.  
**그 외 CSS는 절대 건드리지 않는다.**

삭제 대상 클래스명 (이 이름으로 시작하는 CSS 선언 블록 전체):
- `.breadcrumb-area`
- `.tai-hero` (단, 다른 클래스 안에 중첩된 것 제외, 최상위 선택자만)
- `.tai-btn-pri`
- `.tai-btn-sec`
- `.hero-split`

`<style>` 블록이 완전히 비워지면 `<style></style>` 태그도 삭제한다.

#### 커밋
메시지: `feat(construction): 표준 히어로 적용 — breadcrumb-area 제거`

---

### 파일 2: `nexas/target/factory.html`

#### 현재 히어로 상태
`.tai-hero` 클래스 사용, 인라인 CSS 있음.

#### 작업 2-1: `<head>` CSS 링크 정리
위의 표준 `<head>` 규칙 적용.

#### 작업 2-2: 히어로 섹션 클래스/구조 수정
`<div id="tai-header"></div>` 다음 첫 번째 `<section>`을 찾는다.

**변경할 것: 클래스명만**

| 현재 | 변경 후 |
|---|---|
| `class="tai-hero"` (section) | `class="tai-hero tai-hero--image"` |
| `class="tai-hero-bg"` | `class="tai-hero__bg"` |
| `class="tai-hero-overlay"` | `class="tai-hero__overlay tai-hero__overlay--left"` |
| `class="tai-hero-eyebrow"` | `class="tai-hero__eyebrow"` |
| `class="tai-hero-title"` | `class="tai-hero__title"` |
| `class="tai-hero-accent"` (span) | `class="accent"` |
| `class="tai-hero-sub"` | `class="tai-hero__sub"` |
| `class="tai-hero-micro"` | `class="tai-hero__micro"` |
| `class="tai-hero-cta"` | `class="tai-hero__cta"` |

**변경할 것: container 구조**

현재:
```html
<div class="container" style="position:relative;z-index:2;">
  <div class="row align-items-center" style="min-height:420px;">
    <div class="col-lg-7 py-5">
      [콘텐츠]
    </div>
    <div class="col-lg-5 d-none d-lg-block">
    </div>
  </div>
</div>
```

변경 후:
```html
<div class="container">
  <div class="tai-hero__inner">
    [콘텐츠]
  </div>
</div>
```

※ `[콘텐츠]` = eyebrow, h1, sub, micro, cta 요소들을 그대로 유지한다. 텍스트, 경로, id 변경 금지.

#### 작업 2-3: `<style>` 블록 정리
파일 1과 동일한 기준으로 히어로 관련 CSS 블록만 삭제한다.

#### 커밋
메시지: `refactor(factory): 표준 히어로 모듈 적용`

---

### 파일 3: `nexas/target/building.html`

파일 2(`factory.html`)와 동일한 절차를 적용한다.

#### 커밋
메시지: `refactor(building): 표준 히어로 모듈 적용`

---

### 파일 4: `nexas/for-expert.html`

파일 2(`factory.html`)와 동일한 절차를 적용한다.  
단, 이 파일의 상대경로는 `assets/css/` (상위 폴더 없음).

#### 커밋
메시지: `refactor(for-expert): 표준 히어로 모듈 적용`

---

### 파일 5, 6, 7: `for-safety-manager.html`, `for-consultant.html`, `for-repair.html`

각 파일을 열어서 `<div id="tai-header"></div>` 다음 첫 번째 `<section>`의 클래스를 확인한다.

**확인 후 판단:**

| 첫 번째 `<section>`의 클래스 | 실행할 작업 |
|---|---|
| `breadcrumb-area`로 시작 | 즉시 멈추고 보고: "파일명: breadcrumb-area 발견 — 히어로 콘텐츠(제목, 서브카피, 버튼 경로) 확인 후 별도 지시 필요" |
| `tai-hero`로 시작 | 파일 2와 동일한 절차 적용 |
| `fa2-a` 또는 `fa2-sec`로 시작 | 히어로 섹션 수정하지 않음. `<head>` CSS 링크 정리만 적용 후 커밋 |
| 위 3가지에 해당하지 않는 경우 | 수정하지 않고 즉시 보고: "파일명: 알 수 없는 패턴 — [현재 클래스명]" |

---

## 작업 완료 조건

각 파일에 대해 아래 3가지가 모두 참이면 완료:

1. `<head>`에 `tai-brand.css`, `tai-main.css`, `tai-hero.css` 링크가 있고 `tai-hero-fix.css`가 없다
2. 첫 번째 `<section>`이 `tai-hero` 클래스를 사용한다 (단, `fa2-sec` 계열 제외)
3. 두 번째 `<section>` 이후는 작업 전과 완전히 동일하다

---

## 하지 말아야 할 것 (명시적 금지 목록)

- 히어로 아래 섹션의 HTML 수정
- 히어로 아래 섹션의 CSS 수정
- 버튼 텍스트, CTA 경로 변경
- 제목/서브카피 텍스트 변경
- `id` 속성 변경
- `<head>`의 `<title>`, `<meta>` 변경
- JS 파일 수정
- `footer.js`, `nav-auth.js` 관련 코드 수정
- `style.css`, `responsive.css` 수정
- 지시서에 없는 "개선" 추가
