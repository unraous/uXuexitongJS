<script setup lang="ts">
import { getCurrentWebview } from "@tauri-apps/api/webview";
import { onMounted, onUnmounted, ref } from "vue";

const opacity = ref(0);
let unlistenCloseEvent: (() => void) | null = null;

onMounted(async () => {
  unlistenCloseEvent = await getCurrentWebview().listen("close-event", () => {
    console.debug("收到 close-event，开始关闭动画");
    opacity.value = 1;
  });
});

onUnmounted(() => {
  unlistenCloseEvent?.();
  unlistenCloseEvent = null;
});
</script>

<template>
  <div
    class="mask"
    :style="{ opacity }"
  ></div>
</template>

<style scoped>
.mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #000000;
  pointer-events: none;
  transition: opacity 500ms ease-in-out;
}
</style>
