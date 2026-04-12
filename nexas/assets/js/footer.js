/**
 * TAI 공통 Footer — 이 파일 하나만 수정하세요
 * 모든 페이지에서 <div id="tai-footer"></div> + <script src="assets/js/footer.js"> 로 사용
 */
(function () {

  /* ── 파비콘 설정 ── */
  (function(){
    var link = document.querySelector("link[rel*='icon']") || document.createElement('link');
    link.type = 'image/svg+xml';
    link.rel  = 'icon';
    link.href = 'assets/img/favicon.svg';
    document.head.appendChild(link);
  })();

  /* ── Footer HTML ── */
  const FOOTER_HTML = `
<footer class="tai-footer">
  <div class="footer-patent" style="color:#fff;">
    본 서비스의 핵심 기술은 특허 출원 중입니다.
    특허출원: 제10-2026-0056330 외 4건 · 상표출원: 제40-2026-0061564
    <a href="patents.html" style="color:rgba(255,255,255,.6); margin-left:8px;">기술 혁신 보기 →</a>
  </div>
  <div class="footer-main">
    <div class="footer-grid">

      <!-- 회사 정보 -->
      <div>
        <a href="/" class="footer-logo">
          <img src="assets/img/tai-logo.png" alt="TAI 엔지니어링">
        </a>
        <div class="footer-info">
          <p><strong style="color:rgba(255,255,255,.65);">TAI엔지니어링</strong>&nbsp;&nbsp;대표: 심태왕</p>
          <p>서울특별시 강남구 테헤란로79길 6 JS타워 3층 브이1314</p>
          <p>TEL: 070-8080-1858 &nbsp;·&nbsp; FAX: 0504-845-8888</p>
          <p>EMAIL: <a href="mailto:tai@taieng.co.kr">tai@taieng.co.kr</a></p>
          <p>사업자등록번호: 723-39-01422</p>
          <p>통신판매신고번호: 제2011-강원춘천-0039호</p>
        </div>
      </div>

      <!-- 서비스 -->
      <div class="footer-col">
        <h6>서비스</h6>
        <ul>
          <li><a href="index-1.html">TAI Safe</a></li>
          <li><a href="index-2.html">TAI Manager</a></li>
          <li><a href="index-3.html">TAI Fix</a></li>
          <li><a href="index-4.html">TAI Care</a></li>
        </ul>
      </div>

      <!-- 이용안내 -->
      <div class="footer-col">
        <h6>이용안내</h6>
        <ul>
          <li><a href="safety-news.html">안전정보</a></li>
          <li><a href="faq.html">FAQ</a></li>
          <li><a href="about.html">회사소개</a></li>
          <li><a href="contact.html">이용문의</a></li>
          <li><a href="patents.html" style="color:#ff6b6b;">🔒 기술 혁신</a></li>
        </ul>
      </div>

      <!-- 법적 고지 -->
      <div class="footer-col">
        <h6>법적 고지</h6>
        <ul>
          <li><a href="terms.html">이용약관</a></li>
          <li><a href="privacy.html">개인정보처리방침</a></li>
          <li><a href="free-diagnosis.html">무료 법령 진단</a></li>
        </ul>
      </div>

    </div>
  </div>
  <div class="footer-bottom">
    <span>© TAI Engineering. All rights reserved.</span>
    <a href="site-map.html" style="color:rgba(255,255,255,.45); margin-left:14px; font-size:.78rem; text-decoration:none;">사이트맵 (점검)</a>
  </div>
</footer>
`;

  const el = document.getElementById('tai-footer');
  if (el) {
    el.outerHTML = FOOTER_HTML;
  } else {
    document.body.insertAdjacentHTML('beforeend', FOOTER_HTML);
  }

})();
