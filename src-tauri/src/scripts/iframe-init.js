(() => {
  if (window === window.top) {
    window.addEventListener("message", (e) => {
      if (e.data && e.data.__uxue_navigate) {
        window.location.href = e.data.__uxue_navigate;
      }
    });
  }

  const safeNavigate = (url) => {
    if (!url || url.startsWith("javascript:")) return;
    try {
      window.top.location.href = url;
    } catch {
      window.top.postMessage({ __uxue_navigate: url }, "*");
    }
  };

  window.open = function (url) {
    if (url && typeof url === "string") {
      safeNavigate(url);
    }
    return window;
  };

  document.addEventListener(
    "click",
    (e) => {
      const anchor = e.target?.closest?.("a[href]");
      if (!anchor) return;

      const href = anchor.getAttribute("href");
      if (!href || href.startsWith("#") || href.startsWith("javascript:"))
        return;

      const target = anchor.getAttribute("target") || anchor.target;
      if (target === "_blank" || target === "_top" || target === "_parent") {
        e.preventDefault();
        e.stopPropagation();
        safeNavigate(anchor.href);
      }
    },
    true,
  );
})();
