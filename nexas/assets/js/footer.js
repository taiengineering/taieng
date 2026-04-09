/**
 * TAI 공통 Footer — 이 파일 하나만 수정하세요
 * 모든 페이지에서 <div id="tai-footer"></div> + <script src="assets/js/footer.js"> 로 사용
 */
(function () {
  const FOOTER_HTML = `
<footer class="tai-footer">
  <div class="footer-patent">
    본 서비스는 산업안전 법령 진단 및 관리 자동화 기술에 대해 특허 출원을 진행한 기술을 기반으로 합니다.
    (출원번호: 10-2026-0056330)
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
          <li><a href="index-5.html">안전정보</a></li>
          <li><a href="faq.html">FAQ</a></li>
          <li><a href="about.html">회사소개</a></li>
          <li><a href="contact.html">이용문의</a></li>
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
    <span>© 2026 TAI Engineering. All rights reserved.</span>
    <span>이걸 왜 몰랐지?</span>
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
