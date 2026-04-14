/**
 * TAI 공통 Footer — assets/js/footer.js
 * 모든 페이지에서 <div id="tai-footer"></div> + <script src="...assets/js/footer.js"> 로 사용
 * v2.2.0 (2026-04-14): 특허 카운터 6→7건 (외 6건)
 */
(function () {
  'use strict';

  /* ── 경로 기준점 자동 감지 ── */
  var path  = window.location.pathname;
  var inSub = /\/(service|target|mypage)\//.test(path);
  var b     = inSub ? '../' : '';

  /* ── Footer HTML (Nexas 원본 footer-area style-1 구조) ── */
  var html = '<footer class="footer-area style-1">' +

    /* 특허 안내 바 */
    '<div class="footer-patent-bar" style="background:rgba(255,255,255,.05);padding:10px 0;text-align:center;">' +
    '  <div class="container">' +
    '    <p style="margin:0;font-size:.8rem;color:rgba(255,255,255,.55);">' +
    '      특허 출원 중 (Patent Pending) &nbsp;·&nbsp; 제10-2026-0056330 외 6건 &nbsp;·&nbsp; 상표출원 중' +
    '      <a href="' + b + 'patents.html" style="color:rgba(255,255,255,.45);margin-left:10px;">\uae30\uc220 \ud601\uc2e0 \ubcf4\uae30 \u2192</a>' +
    '    </p>' +
    '  </div>' +
    '</div>' +

    /* 푸터 바디 */
    '<div class="footer-inner">' +
    '  <div class="container">' +
    '    <div class="row">' +

    /* 회사 정보 */
    '      <div class="col-xl-4 col-lg-4 col-sm-6">' +
    '        <div class="footer-widget widget">' +
    '          <a class="logo" href="' + b + 'index.html"><img src="' + b + 'assets/img/tai-logo.png" alt="TAI 엔지니어링" style="height:36px;"></a>' +
    '          <div class="footer-company-info" style="margin-top:16px;">' +
    '            <p style="margin-bottom:4px;"><span class="footer-company-name" style="font-weight:700;">TAI 엔지니어링</span>&nbsp;&nbsp;<span style="font-size:.85rem;">대표 심태왕</span></p>' +
    '            <p style="margin-bottom:3px;font-size:.85rem;">서울특별시 강남구 테헤란로79길 6 JS타워 3층</p>' +
    '            <p style="margin-bottom:3px;font-size:.85rem;">TEL: 070-8080-1858 &nbsp;·&nbsp; FAX: 0504-845-8888</p>' +
    '            <p style="margin-bottom:3px;font-size:.85rem;">EMAIL: <a href="mailto:tai@taieng.co.kr">tai@taieng.co.kr</a></p>' +
    '            <p style="margin-bottom:3px;font-size:.85rem;">사업자등록번호: 723-39-01422</p>' +
    '            <p style="font-size:.85rem;">통신판매업 신고번호: 제2026-서울강남-02132호</p>' +
    '          </div>' +
    '        </div>' +
    '      </div>' +

    /* 서비스 */
    '      <div class="col-xl-2 col-lg-2 col-6">' +
    '        <div class="footer-widget widget widget_link">' +
    '          <h6 class="widget-title">서비스</h6>' +
    '          <ul>' +
    '            <li><a href="' + b + 'service/education.html"><i class="fas fa-angle-right"></i>교육사업</a></li>' +
    '            <li><a href="' + b + 'service/inapp.html"><i class="fas fa-angle-right"></i>인앱 서비스</a></li>' +
    '            <li><a href="' + b + 'service/repair.html"><i class="fas fa-angle-right"></i>수선 연결</a></li>' +
    '            <li><a href="' + b + 'service/consulting.html"><i class="fas fa-angle-right"></i>컨설팅</a></li>' +
    '            <li><a href="' + b + 'service/appointment.html"><i class="fas fa-angle-right"></i>선임 연결</a></li>' +
    '            <li><a href="' + b + 'service/saas.html"><i class="fas fa-angle-right"></i>SaaS 구독</a></li>' +
    '            <li><a href="' + b + 'service/diagnosis.html"><i class="fas fa-angle-right"></i>법령진단</a></li>' +
    '          </ul>' +
    '        </div>' +
    '      </div>' +

    /* 대상별 */
    '      <div class="col-xl-2 col-lg-2 col-6">' +
    '        <div class="footer-widget widget widget_link">' +
    '          <h6 class="widget-title">대상별</h6>' +
    '          <ul>' +
    '            <li><a href="' + b + 'target/building.html"><i class="fas fa-angle-right"></i>건물·시설</a></li>' +
    '            <li><a href="' + b + 'target/factory.html"><i class="fas fa-angle-right"></i>제조공장</a></li>' +
    '            <li><a href="' + b + 'target/construction.html"><i class="fas fa-angle-right"></i>건설현장</a></li>' +
    '          </ul>' +
    '          <h6 class="widget-title" style="margin-top:20px;">역할별</h6>' +
    '          <ul>' +
    '            <li><a href="' + b + 'for-safety-manager.html"><i class="fas fa-angle-right"></i>안전관리자</a></li>' +
    '            <li><a href="' + b + 'for-business-owner.html"><i class="fas fa-angle-right"></i>사업주·현장소장</a></li>' +
    '          </ul>' +
    '        </div>' +
    '      </div>' +

    /* 지원 */
    '      <div class="col-xl-2 col-lg-2 col-6">' +
    '        <div class="footer-widget widget widget_link">' +
    '          <h6 class="widget-title">시작하기</h6>' +
    '          <ul>' +
    '            <li><a href="' + b + 'free-diagnosis.html"><i class="fas fa-angle-right"></i>무료 법령진단</a></li>' +
    '            <li><a href="' + b + 'pricing.html"><i class="fas fa-angle-right"></i>요금제</a></li>' +
    '            <li><a href="' + b + 'contact.html"><i class="fas fa-angle-right"></i>도입 문의</a></li>' +
    '            <li><a href="' + b + 'faq.html"><i class="fas fa-angle-right"></i>FAQ</a></li>' +
    '            <li><a href="' + b + 'safety-news.html"><i class="fas fa-angle-right"></i>안전정보</a></li>' +
    '          </ul>' +
    '        </div>' +
    '      </div>' +

    /* 회사 */
    '      <div class="col-xl-2 col-lg-2 col-6">' +
    '        <div class="footer-widget widget widget_link">' +
    '          <h6 class="widget-title">회사</h6>' +
    '          <ul>' +
    '            <li><a href="' + b + 'about.html"><i class="fas fa-angle-right"></i>회사소개</a></li>' +
    '            <li><a href="' + b + 'patents.html"><i class="fas fa-angle-right"></i>특허 출원 중</a></li>' +
    '            <li><a href="' + b + 'terms.html"><i class="fas fa-angle-right"></i>이용약관</a></li>' +
    '            <li><a href="' + b + 'privacy.html"><i class="fas fa-angle-right"></i>개인정보처리방침</a></li>' +
    '          </ul>' +
    '        </div>' +
    '      </div>' +

    '    </div>' +
    '  </div>' +
    '</div>' +

    /* 푸터 하단 */
    '<div class="footer-bottom">' +
    '  <div class="container">' +
    '    <div class="row">' +
    '      <div class="col-md-6 align-self-center">' +
    '        <div class="copyright-area">' +
    '          <p class="mb-0">&copy; 2026 TAI Engineering. All rights reserved.</p>' +
    '        </div>' +
    '      </div>' +
    '      <div class="col-md-6 align-self-center text-md-end">' +
    '        <div class="author-area">' +
    '          <p class="mb-0" style="font-size:.82rem;">' +
    '            특허 출원 중 (Patent Pending) &nbsp;·&nbsp;' +
    '            <a href="' + b + 'site-map.html" style="opacity:.5;">사이트맵</a>' +
    '          </p>' +
    '        </div>' +
    '      </div>' +
    '    </div>' +
    '  </div>' +
    '</div>' +

    '</footer>';

  /* ── 삽입 ── */
  function inject() {
    var el = document.getElementById('tai-footer');
    if (el) {
      el.outerHTML = html;
    } else {
      var existing = document.querySelector('footer.footer-area');
      if (existing) {
        existing.outerHTML = html;
      } else {
        document.body.insertAdjacentHTML('beforeend', html);
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
