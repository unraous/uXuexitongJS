(() => {
  console.info(
    "[uXueScript] 开始全深度（穿透 iframe -> 强定向顶层 _top）窗口劫持...",
  );

  const hookDocument = (doc) => {
    if (!doc || doc._uxue_hooked) return;
    doc._uxue_hooked = true; // 标记防止重复绑定

    doc.addEventListener(
      "mouseover",
      function (e) {
        const anchor = e.target?.closest?.("a[href]");
        if (anchor) {
          const target = anchor.getAttribute("target") || anchor.target;
          if (target === "_blank") {
            anchor.setAttribute("target", "_top");
            anchor.target = "_top";
          }
        }
      },
      true,
    );

    doc.addEventListener(
      "click",
      function (e) {
        const anchor = e.target?.closest?.("a[href]");
        if (anchor) {
          const target = anchor.getAttribute("target") || anchor.target;
          if (target === "_blank" || target === "_top") {
            e.preventDefault();
            e.stopPropagation();
            anchor.setAttribute("target", "_top");
            anchor.target = "_top";
            window.top.location.href = anchor.href;
          }
        }
      },
      true,
    );
  };

  const scanAndHook = (rootDoc = document) => {
    hookDocument(rootDoc);
    const iframes = rootDoc.querySelectorAll("iframe");
    iframes.forEach((iframe) => {
      const innerDoc =
        iframe?.contentDocument || iframe?.contentWindow?.document;
      if (innerDoc) {
        hookDocument(innerDoc);
        scanAndHook(innerDoc);
      }
      iframe.addEventListener("load", () => {
        const loadedDoc =
          iframe?.contentDocument || iframe?.contentWindow?.document;
        if (loadedDoc) scanAndHook(loadedDoc);
      });
    });
  };

  scanAndHook();
  setInterval(scanAndHook, 1000);
})();
