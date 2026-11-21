/* Google Analytics 4, loaded only when Site Settings has a Google Analytics ID (data-ga on this script tag).
   Kept in a file because the Content-Security-Policy allows no inline scripts. */
(function () {
  "use strict";
  var id = document.currentScript && document.currentScript.getAttribute("data-ga");
  if (!id) return;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag("js", new Date());
  window.gtag("config", id);
  var tag = document.createElement("script");
  tag.async = true;
  tag.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(id);
  document.head.appendChild(tag);
})();
