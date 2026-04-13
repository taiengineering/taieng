/**
 * TAI 공통 Footer — 이 파일 하나만 수정하세요
 * 모든 페이지에서 <div id="tai-footer"></div> + <script src="assets/js/footer.js"> 로 사용
 * v2.0.0: 사이트맵 기준 전체 링크 갱신 (2026-04-13)
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

  /* ── 현재 페이지가 service/ 또는 target/ 하위인지 확인해 경로 보정 ── */
  const path   = window.location.pathname;
  const isSubDir = /\/(service|target)\//.test(path);
  const base   = isSubDir ? '../' : '';

  /* ── Footer HTML ── */
  const FOOTER_HTML = `
<footer class="tai-footer">
  <div class="footer-patent" style="color:#fff;">
    본 서비스의 핵심 기술은 특허 출원 중입니다.
    특허출원: 제10-2026-0056330 외 4건 · 상표출원: 제40-2026-0061564
    <a href="${base}patents.html" style="color:rgba(255,255,255,.6); margin-left:8px;">기술 혁신 보기 →</a>
  </div>
  <div class="footer-main">
    <div class="footer-grid" style="grid-template-columns: 1.6fr repeat(5, 1fr);">

      <!-- 회사 정보 -->
      <div>
        <a href="${base}index.html" class="footer-logo">
          <img src="${base}assets/img/tai-logo.png" alt="TAI 엔지니어링">
        </a>
        <div class="footer-info">
          <p><strong style="color:rgba(255,255,255,.65);">TAI엔지니어링</strong>&nbsp;&nbsp;대표: 심태왕</p>
          <p>서울특별시 강남구 테헤란로79길 6 JS타워 3층 브이1314</p>
          <p>TEL: 070-8080-1858 &nbsp;·&nbsp; FAX: 0504-845-8888</p>
          <p>EMAIL: <a href="mailto:tai@taieng.co.kr">tai@taieng.co.kr</a></p>
          <p>사업자등록번호: 723-39-01422</p>
          <p>통신판매업 신고번호: 제2026-서울강남-02132호</p>
        </div>
      </div>

      <!-- 서비스 -->
      <div class="footer-col">
        <h6>서비스</h6>
        <ul>
          <li><a href="${base}service/education.html">교육사업</a></li>
          <li><a href="${base}service/inapp.html">인앱 서비스</a></li>
          <li><a href="${base}service/repair.html">수선 연결</a></li>
          <li><a href="${base}service/consulting.html">컨설팅</a></li>
          <li><a href="${base}service/appointment.html">선임 연결</a></li>
          <li><a href="${base}service/saas.html">SaaS 구독</a></li>
          <li><a href="${base}service/diagnosis.html">법령진단</a></li>
        </ul>
      </div>

      <!-- 대상별 -->
      <div class="footer-col">
        <h6>대상별</h6>
        <ul>
          <li><a href="${base}target/building.html">건물·시설</a></li>
          <li><a href="${base}target/factory.html">제조공장</a></li>
          <li><a href="${base}target/construction.html">건설현장</a></li>
        </ul>
        <h6 style="margin-top:18px;">역할별</h6>
        <ul>
          <li><a href="${base}for-safety-manager.html">안전관리자</a></li>
          <li><a href="${base}for-business-owner.html">사업주·현장소장</a></li>
        </ul>
      </div>

      <!-- 요금·전환 -->
      <div class="footer-col">
        <h6>요금·시작</h6>
        <ul>
          <li><a href="${base}pricing.html">요금제</a></li>
          <li><a href="${base}free-diagnosis.html">무료 법령진단</a></li>
          <li><a href="${base}contact.html">도입 문의</a></li>
          <li><a href="${base}sign-up.html">회원가입</a></li>
          <li><a href="${base}log-in.html">로그인</a></li>
        </ul>
      </div>

      <!-- 신뢰·지원 -->
      <div class="footer-col">
        <h6>신뢰·지원</h6>
        <ul>
          <li><a href="${base}about.html">회사소개</a></li>
          <li><a href="${base}patents.html" style="color:#ff6b6b;">🔒 특허 출원 중</a></li>
          <li><a href="${base}faq.html">FAQ</a></li>
          <li><a href="${base}safety-news.html">안전정보</a></li>
        </ul>
      </div>

      <!-- 법적 고지 -->
      <div class="footer-col">
        <h6>법적 고지</h6>
        <ul>
          <li><a href="${base}terms.html">이용약관</a></li>
          <li><a href="${base}privacy.html">개인정보처리방침</a></li>
        </ul>
      </div>

    </div>
  </div>
  <div class="footer-bottom">
    <span>© TAI Engineering. All rights reserved.</span>
    <a href="${base}site-map.html" style="color:rgba(255,255,255,.45); margin-left:14px; font-size:.78rem; text-decoration:none;">사이트맵</a>
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
