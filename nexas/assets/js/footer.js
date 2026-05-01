/**
 * TAI 공통 Footer — assets/js/footer.js
 * v3.3.0 (2026-04-29): 풋터 요금제 링크 삭제 (이니시스 요청)
 * v3.2.0 (2026-04-29): Supabase 신규 프로젝트(서울) URL로 교체
 * v3.1.0 (2026-04-26): 로고 텍스트 TAI → TAI Engineering
 * v3.0.0 (2026-04-26): 로고 아이콘+텍스트 방식 전환 + 특허 13건
 * v2.4.0: 풋터 다크 테마 (#0f172a) CSS 주입
 */
(function () {
  'use strict';

  var ICON_URL = 'https://vwlahtguyggrhvslabax.supabase.co/storage/v1/object/public/site-assets/tai-icon-96.png';

  function injectFooterDarkTheme() {
    if (document.getElementById('tai-footer-dark-theme')) return;
    var css = [
      '.footer-area.style-1 { background: #0f172a !important; }',
      '.footer-area.style-1 .footer-inner { background: transparent !important; }',
      '.footer-area.style-1 .footer-bottom { background: rgba(255,255,255,.04) !important; border-top: 1px solid rgba(255,255,255,.08) !important; }',
      '.footer-area.style-1 .footer-patent-bar { background: rgba(255,255,255,.05) !important; border-bottom: 1px solid rgba(255,255,255,.06) !important; }',
      '.footer-area.style-1 .footer-patent-bar p { color: rgba(255,255,255,.45) !important; }',
      '.footer-area.style-1 .footer-patent-bar a { color: rgba(255,255,255,.35) !important; }',
      '.footer-area.style-1 .footer-patent-bar a:hover { color: rgba(255,255,255,.65) !important; }',
      '.footer-area.style-1 .widget-title, .footer-area.style-1 h6.widget-title { color: #fff !important; font-size:.82rem !important; letter-spacing:.08em !important; }',
      '.footer-area.style-1 .footer-widget p, .footer-area.style-1 .footer-company-info p { color: rgba(255,255,255,.58) !important; }',
      '.footer-area.style-1 .footer-company-name { color: rgba(255,255,255,.9) !important; }',
      '.footer-area.style-1 .widget_link ul li a { color: rgba(255,255,255,.58) !important; transition: color .15s !important; }',
      '.footer-area.style-1 .widget_link ul li a:hover { color: #93c5fd !important; }',
      '.footer-area.style-1 .widget_link ul li a i { color: rgba(255,255,255,.3) !important; }',
      '.footer-area.style-1 .footer-company-info a { color: rgba(255,255,255,.58) !important; }',
      '.footer-area.style-1 .footer-company-info a:hover { color: #93c5fd !important; }',
      '.footer-area.style-1 .footer-bottom p { color: rgba(255,255,255,.38) !important; }',
      '.footer-area.style-1 .footer-bottom p a { color: rgba(255,255,255,.38) !important; }',
      '.footer-area.style-1 .footer-bottom p a:hover { color: rgba(255,255,255,.65) !important; }',
      '.tai-footer-logo { display:flex; align-items:center; gap:10px; text-decoration:none !important; }',
      '.tai-footer-logo:hover { text-decoration:none !important; }',
      '.tai-footer-logo img { width:36px; height:36px; border-radius:7px; object-fit:cover; box-shadow:0 2px 8px rgba(0,0,0,.3); }',
      '.tai-footer-logo span { font-family:"DM Sans","Arial Black",Arial,sans-serif; font-weight:900; font-size:1.1rem; color:#fff; letter-spacing:-.01em; white-space:nowrap; }',
    ].join('\n');
    var styleEl = document.createElement('style');
    styleEl.id = 'tai-footer-dark-theme';
    styleEl.textContent = css;
    document.head.appendChild(styleEl);
  }

  function nexasRelBase() {
    var path = window.location.pathname || '';
    var marker = '/nexas/';
    var i = path.indexOf(marker);
    if (i < 0) return '';
    var rest = path.slice(i + marker.length);
    var parts = rest.split('/').filter(Boolean);
    if (parts.length <= 1) return '';
    var depth = parts.length - 1;
    return new Array(depth + 1).join('../');
  }

  function legacyRelBase() {
    var path = window.location.pathname || '';
    if (/\/(service|target)\//.test(path)) return '../';
    var m = path.match(/\/mypage\/(.+)/);
    if (m) {
      var n = m[1].split('/').filter(Boolean).length;
      return n >= 2 ? '../../' : '../';
    }
    return '';
  }

  injectFooterDarkTheme();

  var b = nexasRelBase();
  if (!b) b = legacyRelBase();

  var html = '<footer class="footer-area style-1">' +
    '<div class="footer-patent-bar" style="padding:10px 0;text-align:center;">' +
    '  <div class="container">' +
    '    <p style="margin:0;font-size:.8rem;">' +
    '      특허 출원 (Patent Pending) &nbsp;·&nbsp; 제10-202*-***6330 외 12건' +
    '      <a href="' + b + 'patents.html" style="margin-left:16px;">기술 혁신 보기 →</a>' +
    '    </p>' +
    '  </div>' +
    '</div>' +
    '<div class="footer-inner">' +
    '  <div class="container">' +
    '    <div class="row">' +
    '      <div class="col-xl-4 col-lg-4 col-sm-6">' +
    '        <div class="footer-widget widget">' +
    '          <a class="tai-footer-logo" href="' + b + 'index.html">' +
    '            <img src="' + ICON_URL + '" alt="TAI Engineering">' +
    '            <span>TAI Engineering</span>' +
    '          </a>' +
    '          <div class="footer-company-info" style="margin-top:16px;">' +
    '            <p style="margin-bottom:4px;"><span class="footer-company-name" style="font-weight:700;">TAI 엔지니어링</span>&nbsp;&nbsp;<span style="font-size:.85rem;">대표 심태왕</span></p>' +
    '            <p style="margin-bottom:3px;font-size:.85rem;">서울특별시 강남구 테헤란로79길 6 JS타워 3층</p>' +
    '            <p style="margin-bottom:3px;font-size:.85rem;">TEL: 070-8080-1858 &nbsp;·&nbsp; FAX: 0504-845-8888</p>' +
    '            <p style="margin-bottom:3px;font-size:.85rem;">EMAIL: tai@taieng.co.kr</p>' +
    '            <p style="margin-bottom:3px;font-size:.85rem;">사업자등록번호: 723-39-01422</p>' +
    '            <p style="font-size:.85rem;">통신판매업 신고번호: 제2026-서울강남-02132호</p>' +
    '          </div>' +
    '        </div>' +
    '      </div>' +
    '      <div class="col-xl-2 col-lg-2 col-6">' +
    '        <div class="footer-widget widget widget_link">' +
    '          <h6 class="widget-title">서비스</h6>' +
    '          <ul>' +
    '            <li><a href="' + b + 'service/education.html"><i class="fas fa-angle-right"></i>교육사업</a></li>' +
    '            <li><a href="' + b + 'service/inapp.html"><i class="fas fa-angle-right"></i>인앱 서비스</a></li>' +
    '            <li><a href="' + b + 'fix-request.html?from=footer&type=repair"><i class="fas fa-angle-right"></i>수선 연결</a></li>' +
    '            <li><a href="' + b + 'fix-request.html?from=footer&type=consulting"><i class="fas fa-angle-right"></i>컨설팅</a></li>' +
    '            <li><a href="' + b + 'fix-request.html?from=footer&type=appointment"><i class="fas fa-angle-right"></i>선임 연결</a></li>' +
    '            <li><a href="' + b + 'service/saas.html"><i class="fas fa-angle-right"></i>SaaS 구독</a></li>' +
    '            <li><a href="' + b + 'service/diagnosis.html"><i class="fas fa-angle-right"></i>법령진단</a></li>' +
    '          </ul>' +
    '        </div>' +
    '      </div>' +
    '      <div class="col-xl-2 col-lg-2 col-6">' +
    '        <div class="footer-widget widget widget_link">' +
    '          <h6 class="widget-title">업종별</h6>' +
    '          <ul>' +
    '            <li><a href="' + b + 'target/building.html"><i class="fas fa-angle-right"></i>건물·시설</a></li>' +
    '            <li><a href="' + b + 'target/factory.html"><i class="fas fa-angle-right"></i>제조공장</a></li>' +
    '            <li><a href="' + b + 'target/construction.html"><i class="fas fa-angle-right"></i>건설현장</a></li>' +
    '          </ul>' +
    '          <h6 class="widget-title" style="margin-top:20px;">역할별</h6>' +
    '          <ul>' +
    '            <li><a href="' + b + 'for-safety-manager"><i class="fas fa-angle-right"></i>안전관리자</a></li>' +
    '            <li><a href="' + b + 'for-business-owner"><i class="fas fa-angle-right"></i>사업주</a></li>' +
    '            <li><a href="' + b + 'provider-register"><i class="fas fa-angle-right"></i>전문가</a></li>' +
    '          </ul>' +
    '        </div>' +
    '      </div>' +
    '      <div class="col-xl-2 col-lg-2 col-6">' +
    '        <div class="footer-widget widget widget_link">' +
    '          <h6 class="widget-title">시작하기</h6>' +
    '          <ul>' +
    '            <li><a href="' + b + 'free-diagnosis.html"><i class="fas fa-angle-right"></i>무료 법령진단</a></li>' +
    '            <li><a href="' + b + 'fix-request.html?from=footer&type=general"><i class="fas fa-angle-right"></i>도입 문의</a></li>' +
    '            <li><a href="' + b + 'faq.html"><i class="fas fa-angle-right"></i>FAQ</a></li>' +
    '          </ul>' +
    '          <h6 class="widget-title" style="margin-top:20px;">안전정보</h6>' +
    '          <ul>' +
    '            <li><a href="' + b + 'precedent-search.html"><i class="fas fa-angle-right"></i>판례 검색</a></li>' +
    '            <li><a href="' + b + 'safety-news.html"><i class="fas fa-angle-right"></i>안전정보</a></li>' +
    '          </ul>' +
    '        </div>' +
    '      </div>' +
    '      <div class="col-xl-2 col-lg-2 col-6">' +
    '        <div class="footer-widget widget widget_link">' +
    '          <h6 class="widget-title">회사</h6>' +
    '          <ul>' +
    '            <li><a href="' + b + 'about.html"><i class="fas fa-angle-right"></i>회사소개</a></li>' +
    '            <li><a href="' + b + 'patents.html"><i class="fas fa-angle-right"></i>TAI 기술력</a></li>' +
    '            <li><a href="' + b + 'terms.html"><i class="fas fa-angle-right"></i>이용약관</a></li>' +
    '            <li><a href="' + b + 'privacy.html"><i class="fas fa-angle-right"></i>개인정보처리방침</a></li>' +
    '          </ul>' +
    '        </div>' +
    '      </div>' +
    '    </div>' +
    '  </div>' +
    '</div>' +
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
    '            특허 출원 (Patent Pending) &nbsp;·&nbsp;' +
    '            <a href="' + b + 'site-map.html">사이트맵</a>' +
    '          </p>' +
    '        </div>' +
    '      </div>' +
    '    </div>' +
    '  </div>' +
    '</div>' +
    '</footer>';

  function inject() {
    var el = document.getElementById('tai-footer');
    if (el) { el.outerHTML = html; }
    else {
      var existing = document.querySelector('footer.footer-area');
      if (existing) { existing.outerHTML = html; }
      else { document.body.insertAdjacentHTML('beforeend', html); }
    }
  }
  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', inject); }
  else { inject(); }
})();
