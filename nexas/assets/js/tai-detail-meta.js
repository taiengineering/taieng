/**
 * 상세 페이지용 메타 태그 — title/description만 법적·가격 필터 적용 (본문 원문과 분리)
 */
(function (global) {
  function stripHtml(html) {
    if (html == null) return "";
    var d = document.createElement("div");
    d.innerHTML = String(html);
    return d.textContent || d.innerText || "";
  }

  function normalizeSpaces(s) {
    return String(s).replace(/\s+/g, " ").trim();
  }

  function removePriceLike(s) {
    return String(s)
      .replace(/\d{1,3}(,\d{3})+\s*원/g, "")
      .replace(/\d+\s*만\s*원/g, "")
      .replace(/\d+\s*원\s*\/\s*월/g, "")
      .replace(/\d+\s*원\/월/g, "")
      .replace(/\d+\s*원~/g, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function filterLegalCopy(s) {
    var t = String(s || "");
    t = t.replace(/법적\s*판단/g, "조건코드 기반 자동 판정");
    t = t.replace(/대행/g, "시스템 자동화·지원");
    return normalizeSpaces(removePriceLike(t));
  }

  function clip(s, max) {
    var t = String(s || "");
    if (t.length <= max) return t;
    return t.slice(0, max - 1) + "…";
  }

  function ensureMeta(name, content) {
    var sel = 'meta[name="' + name + '"]';
    var el = document.head.querySelector(sel);
    if (!el) {
      el = document.createElement("meta");
      el.setAttribute("name", name);
      document.head.appendChild(el);
    }
    el.setAttribute("content", content);
  }

  function ensureOg(property, content) {
    var el = document.head.querySelector('meta[property="' + property + '"]');
    if (!el) {
      el = document.createElement("meta");
      el.setAttribute("property", property);
      document.head.appendChild(el);
    }
    el.setAttribute("content", content);
  }

  /** 현재 페이지 절대 URL(해시 제외)을 canonical로 설정 — 상세 URL과 일치 */
  function setCanonicalAbsolute() {
    var u = window.location.href.split("#")[0];
    var el = document.head.querySelector('link[rel="canonical"]');
    if (!el) {
      el = document.createElement("link");
      el.setAttribute("rel", "canonical");
      document.head.appendChild(el);
    }
    el.setAttribute("href", u);
  }

  /**
   * @param {string} rawTitle
   * @param {string} [rawSummary] — 없으면 title 기반
   */
  function setDetailMeta(rawTitle, rawSummary) {
    var title = filterLegalCopy(stripHtml(rawTitle)) || "안전정보";
    var summarySource =
      rawSummary != null && String(rawSummary).trim()
        ? stripHtml(rawSummary)
        : title;
    var summaryFiltered = filterLegalCopy(summarySource);
    var body = clip(summaryFiltered, 140);
    var desc = body + " 3분 무료 법령진단 가능.";
    document.title = title + " | TAI Safe";
    ensureMeta("description", desc);
    ensureOg("og:title", title + " | TAI Safe");
    ensureOg("og:description", desc);
    setCanonicalAbsolute();
  }

  global.TAIDetailMeta = {
    setDetailMeta: setDetailMeta,
    setCanonicalAbsolute: setCanonicalAbsolute,
    filterLegalCopy: filterLegalCopy,
    stripHtml: stripHtml,
  };

  if (typeof document !== "undefined") {
    var runCanon = function () {
      setCanonicalAbsolute();
    };
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", runCanon);
    } else {
      runCanon();
    }
  }
})(typeof window !== "undefined" ? window : this);
