<script setup lang="ts">
import MainLayout from "@/layouts/TheMainLayout.vue";

const isDev = import.meta.env.DEV;
globalThis.addEventListener("keydown", (e) => {
  const key = e.key.toLowerCase();
  // 1. 任何环境下都禁用的系统默认快捷键
  if ((e.ctrlKey || e.metaKey) && ["p", "s", "f"].includes(key)) {
    e.preventDefault();
    return;
  }
  // 2. 仅在生产打包构建模式下禁用刷新 (Ctrl+R / F5)
  if (!isDev && (((e.ctrlKey || e.metaKey) && key === "r") || key === "f5")) {
    e.preventDefault();
  }
});
</script>

<template>
  <div @contextmenu.prevent>
    <MainLayout />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
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
