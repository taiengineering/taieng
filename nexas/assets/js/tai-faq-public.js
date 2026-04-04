/**
 * 공개 FAQ — GET https://api.taieng.co.kr/faqs
 * #faqAccordion 에 Bootstrap 5 accordion 렌더
 */
(function () {
  'use strict';

  var API = 'https://api.taieng.co.kr/faqs';

  function esc(s) {
    if (s == null) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function fallbackItems() {
    return [
      {
        question: 'TAI 서비스를 선택해야 하는 이유는 무엇인가요?',
        answer:
          '산업안전 규정·점검·실무를 한곳에서 정리하는 TAI 플랫폼 안내입니다. 상세 내용은 각 서비스 페이지에서 확인하세요.'
      },
      {
        question: '무료 법령 진단은 어떻게 이용하나요?',
        answer:
          '진단 시작 페이지에서 안내에 따라 정보를 입력하시면 됩니다. 문의가 필요하면 <a href="contact.html">문의하기</a>로 연락해 주세요.'
      }
    ];
  }

  function render(items) {
    var root = document.getElementById('faqAccordion');
    if (!root) return;
    if (!items || !items.length) {
      items = fallbackItems();
    }
    var html = items
      .map(function (row, i) {
        var id = 'faqItem' + i;
        var collapseId = 'faqCollapse' + i;
        var headingId = 'faqHeading' + i;
        var show = i === 0;
        var ans = row.answer != null ? String(row.answer) : '';
        return (
          '<div class="accordion-item' +
          (i === items.length - 1 ? ' mb-0' : '') +
          '">' +
          '<h2 class="accordion-header" id="' +
          esc(headingId) +
          '">' +
          '<button class="accordion-button' +
          (show ? '' : ' collapsed') +
          '" type="button" data-bs-toggle="collapse" data-bs-target="#' +
          esc(collapseId) +
          '" aria-expanded="' +
          (show ? 'true' : 'false') +
          '" aria-controls="' +
          esc(collapseId) +
          '">' +
          esc(row.question) +
          '</button></h2>' +
          '<div id="' +
          esc(collapseId) +
          '" class="accordion-collapse collapse' +
          (show ? ' show' : '') +
          '" aria-labelledby="' +
          esc(headingId) +
          '" data-bs-parent="#faqAccordion">' +
          '<div class="accordion-body">' +
          ans +
          '</div></div></div>'
        );
      })
      .join('');
    root.innerHTML = html;
  }

  async function load() {
    var root = document.getElementById('faqAccordion');
    if (!root) return;
    root.innerHTML =
      '<p class="text-center py-4 mb-0"><span class="spinner-border text-light" role="status"></span></p>';
    try {
      var res = await fetch(API, { method: 'GET', headers: { Accept: 'application/json' } });
      var json = await res.json().catch(function () {
        return {};
      });
      var items =
        json.data && json.data.items && json.data.items.length
          ? json.data.items
          : null;
      render(items);
    } catch (e) {
      render(null);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
})();
