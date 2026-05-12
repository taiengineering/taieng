# 작업지시서: for-expert.html 히어로 섹션 교체

> **작업자:** Cursor / Claude Code
> **대상 파일:** `taieng` 레포 → `nexas/for-expert.html` (20KB)
> **작업 유형:** 히어로 섹션(§1) CSS + HTML 교체
> **주의:** 20KB+ 파일이므로 반드시 로컬 편집 후 git push

---

## 1. 변경 범위

`<!-- §1 히어로 [A] -->` 섹션의 **CSS와 HTML만** 교체.
§2~§5 섹션, 스크립트, 헤더/푸터는 건드리지 않는다.

---

## 2. 배경 이미지

Supabase Storage에 업로드된 텍스트 없는 버전 사용:
```
https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/company.png
```

- `background-size: cover`
- `background-position: center right` (인물이 오른쪽에 위치)
- 왼쪽에서 오른쪽으로 그라데이션 오버레이 (텍스트 가독성 확보)

---

## 3. 교체할 히어로 HTML

기존 `<section class="fe2-sec fe2-a" id="fe2-top">` 전체를 아래로 교체:

```html
<!-- §1 히어로 [A] -->
<section class="fe2-sec fe2-a" id="fe2-top">
  <!-- 배경 이미지 레이어 -->
  <div class="fe2-a-bg"></div>
  <!-- 그라데이션 오버레이 -->
  <div class="fe2-a-overlay"></div>

  <div class="fe2-inner fe2-a-layout">
    <!-- 왼쪽: 텍스트 -->
    <div class="fe2-a-text">
      <p class="fe2-a-eyebrow">대행기관 · 수선업체 · 컨설턴트</p>
      <h1>실력은 있는데,<br><span class="fe2-a-accent">찾는 곳이 없습니다.</span></h1>
      <p class="sub">TAI는 법적 의무를 인지한 사업장과 검증된 전문가를 연결하는 플랫폼을 준비하고 있습니다.</p>
      <p class="micro">사업장이 법령진단을 하면 의무가 감지되고, 그 의무를 이행할 전문가가 필요해집니다.<br>영업하지 않아도, 일감이 만들어지는 구조입니다.</p>
      <div class="fe2-a-cta">
        <a class="fe2-btn fe2-btn-pri" href="fix-request.html?from=for-expert&type=general&interest=partner">파트너 사전등록 →</a>
        <a class="fe2-btn fe2-btn-sec" href="fix-request.html?from=for-expert&type=general&interest=brochure">서비스 소개서 요청</a>
      </div>
    </div>

    <!-- 오른쪽: 고민 버블 -->
    <div class="fe2-a-bubbles">
      <div class="fe2-bubble fe2-bubble-1">
        <span class="fe2-bubble-x">✕</span>
        <span class="fe2-bubble-txt">견적은 넣는데<br><strong>선정이 안 됩니다</strong></span>
      </div>
      <div class="fe2-bubble fe2-bubble-2">
        <span class="fe2-bubble-x">✕</span>
        <span class="fe2-bubble-txt">실적 증빙이 안 되니<br><strong>신뢰를 못 얻습니다</strong></span>
      </div>
      <div class="fe2-bubble fe2-bubble-3">
        <span class="fe2-bubble-x">✕</span>
        <span class="fe2-bubble-txt">블로그 써도<br><strong>전화가 안 옵니다</strong></span>
      </div>
      <div class="fe2-bubble fe2-bubble-4">
        <span class="fe2-bubble-x">✕</span>
        <span class="fe2-bubble-txt">같은 거래처만 반복<br><strong>신규가 없습니다</strong></span>
      </div>
    </div>
  </div>
</section>
```

---

## 4. 교체/추가할 CSS

기존 `#fe2 .fe2-a` 관련 CSS를 아래로 교체.
**기존 `.fe2-a` 스타일 블록 전체를 삭제하고** 아래를 삽입:

```css
/* ===== §1 히어로 (이미지 배경 + 버블) ===== */
#fe2 .fe2-a {
  position: relative;
  overflow: hidden;
  background: #0a0f1a;
}

#fe2 .fe2-a-bg {
  position: absolute;
  inset: 0;
  background-image: url('https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/company.png');
  background-size: cover;
  background-position: center right;
  opacity: 0.55;
}

#fe2 .fe2-a-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    #0a0f1a 0%,
    rgba(10,15,26,0.95) 35%,
    rgba(10,15,26,0.45) 65%,
    rgba(10,15,26,0.2) 100%
  );
}

#fe2 .fe2-a .fe2-inner.fe2-a-layout {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  min-height: 420px;
  padding-top: 56px;
  padding-bottom: 56px;
  gap: 40px;
}

/* 왼쪽 텍스트 영역 */
#fe2 .fe2-a-text {
  flex: 1;
  max-width: 520px;
}

#fe2 .fe2-a-eyebrow {
  font-size: 12px;
  font-weight: 700;
  color: #60a5fa;
  letter-spacing: 0.08em;
  margin: 0 0 14px;
}

#fe2 .fe2-a h1 {
  font-size: clamp(1.65rem, 4.6vw, 2.5rem);
  font-weight: 900;
  line-height: 1.2;
  margin: 0 0 20px;
  color: #fff;
  letter-spacing: -0.02em;
}

#fe2 .fe2-a-accent {
  color: #60a5fa;
}

#fe2 .fe2-a .sub {
  font-size: clamp(0.95rem, 2.1vw, 1.05rem);
  font-weight: 700;
  color: rgba(255,255,255,0.82);
  line-height: 1.65;
  max-width: 40ch;
  margin: 0 0 18px;
  border-left: 3px solid #60a5fa;
  padding-left: 16px;
}

#fe2 .fe2-a .micro {
  font-size: 0.85rem;
  color: rgba(255,255,255,0.4);
  max-width: 44ch;
  line-height: 1.65;
  margin: 0 0 24px;
}

#fe2 .fe2-a-cta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* 오른쪽 버블 영역 */
#fe2 .fe2-a-bubbles {
  flex: 1;
  position: relative;
  min-height: 360px;
}

#fe2 .fe2-bubble {
  position: absolute;
  background: rgba(15,23,42,0.72);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(96,165,250,0.2);
  border-radius: 12px;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
}

#fe2 .fe2-bubble-x {
  font-size: 13px;
  color: #ef4444;
  opacity: 0.6;
  flex-shrink: 0;
}

#fe2 .fe2-bubble-txt {
  font-size: 12.5px;
  color: rgba(255,255,255,0.7);
  line-height: 1.45;
}

#fe2 .fe2-bubble-txt strong {
  color: #fff;
  font-weight: 700;
}

/* 버블 위치 */
#fe2 .fe2-bubble-1 { right: 30px; top: 10px; animation: fe2Float 3s ease-in-out infinite; }
#fe2 .fe2-bubble-2 { right: 0;    top: 100px; animation: fe2Float 3s ease-in-out infinite 0.6s; }
#fe2 .fe2-bubble-3 { right: 40px; top: 190px; animation: fe2Float 3s ease-in-out infinite 1.2s; }
#fe2 .fe2-bubble-4 { right: 10px; top: 280px; animation: fe2Float 3s ease-in-out infinite 1.8s; }

@keyframes fe2Float {
  0%, 100% { opacity: 0.65; transform: translateY(0); }
  50%      { opacity: 1;    transform: translateY(-5px); }
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  #fe2 .fe2-a .fe2-inner.fe2-a-layout {
    flex-direction: column;
    min-height: auto;
    padding-top: 44px;
    padding-bottom: 36px;
  }

  #fe2 .fe2-a-text { max-width: 100%; }

  #fe2 .fe2-a-bubbles {
    position: relative;
    min-height: auto;
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 24px;
  }

  #fe2 .fe2-bubble {
    position: static;
    animation: none !important;
    opacity: 0.85;
  }

  #fe2 .fe2-a-bg {
    background-position: top center;
    opacity: 0.3;
  }

  #fe2 .fe2-a-overlay {
    background: linear-gradient(
      180deg,
      rgba(10,15,26,0.92) 0%,
      rgba(10,15,26,0.85) 100%
    );
  }
}
```

---

## 5. 삭제해야 할 기존 CSS (충돌 방지)

아래 기존 규칙들은 **삭제** 또는 위 코드로 **대체**:

```
#fe2 .fe2-a::before { ... }               ← 삭제 (radial-gradient 배경)
#fe2 .fe2-a .fe2-inner { ... }            ← fe2-a-layout으로 대체
#fe2 .fe2-scroll { ... }                  ← 삭제 (스크롤 힌트 제거)
@keyframes fe2b { ... }                   ← 삭제
```

기존 `.fe2-a h1`, `.fe2-a .sub`, `.fe2-a .micro` 등은 위의 새 CSS가 덮어쓰므로 별도 삭제 불필요.

---

## 6. 주의사항

1. **body 클래스 `home-2` 제거 필수** — Vuexy 테마 클래스가 `tai-brand.css` 변수를 덮어씀
2. `tai-brand.css` 링크가 없으면 `<head>`에 추가: `<link rel="stylesheet" href="assets/css/tai-brand.css">`
3. `.fe2-identity-line`, `.fe2-release-line`, `.fe2-scroll`, `.hint` 관련 HTML은 히어로에서 삭제 (§2 이하에서 표시)
4. §2~§5 섹션은 변경 없음
5. 기존 스크립트(카운터 애니메이션 등)는 변경 없음

---

## 7. 검증 체크리스트

- [ ] 데스크톱(1280px): 왼쪽 텍스트 + 오른쪽 이미지·버블 레이아웃
- [ ] 모바일(375px): 텍스트 → 버블 수직 스택, 이미지 어둡게 처리
- [ ] 버블 4개 부유 애니메이션 동작
- [ ] CTA 버튼 2개 링크 정상 작동
- [ ] 히어로 최소 높이 420px 유지
- [ ] body에 `home-2` 클래스 없음 확인
- [ ] 보라색 안 나오는지 확인 (tai-brand.css 적용 여부)

---

## 8. 서비스 계층 분리 규칙 (참고)

- 20KB+ 파일이므로 MCP 수정 금지 → Cursor 로컬 편집 후 git push
- Router/Service/Schema 분리 대상 아님 (프론트엔드 HTML 파일)
