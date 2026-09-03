(() => {
  const sideCon = document.querySelector(".sideCon");
  globalThis.__TAURI_INTERNALS__.invoke("insert_course_meta_map", {
    courseId: sideCon.querySelector("#courseid")?.value,
    metadata: {
      title: sideCon.querySelector(".classDl dd")?.innerText.trim(),
      cover: sideCon
        .querySelector(".classDl dt img")
        ?.src.replace(/\/star3\/.*?\//, "/star3/origin/"),
    },
  });
})();
