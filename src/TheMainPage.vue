<script setup lang="ts">
import TheMainLayout from "@/layouts/TheMainLayout.vue";

const isDev = import.meta.env.DEV;
globalThis.addEventListener("keydown", (e) => {
  const key = e.key.toLowerCase();
  if ((e.ctrlKey || e.metaKey) && ["p", "s", "f"].includes(key)) {
    e.preventDefault();
    return;
  }
  if (!isDev && (((e.ctrlKey || e.metaKey) && key === "r") || key === "f5")) {
    e.preventDefault();
  }
});
</script>

<template>
<<<<<<< HEAD:src/TheMainPage.vue
  <TheMainLayout />
=======
  <div @contextmenu.prevent>
    <MainLayout />
  </div>
>>>>>>> origin/master:src/App.vue
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  width: 100%;
  height: 100%;
  overflow: hidden;
  overscroll-behavior: none;
}

@font-face {
  font-family: "DefaultFont";
  src: url("@/assets/fonts/Mixture.woff2") format("woff2");
  font-weight: 400;
  font-style: normal;
}

:root {
  user-select: none;
  font-family: "DefaultFont", Inter, Avenir, Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 24px;
  font-weight: 400;
  color: #0d58a4;
  background: linear-gradient(135deg, #e8dcc4 0%, #f0ebe0 100%);

  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: 100%;
}

button,
input,
select,
textarea {
  font-family: inherit;
  font-size: inherit;
}
</style>
