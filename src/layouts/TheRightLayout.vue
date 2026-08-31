<script setup lang="ts">
import TheChaoxingWebviewController from "@/components/TheChaoxingWebviewController.vue";
import TheCourseDashboard from "@/components/panels/TheCourseDashboard.vue";

defineProps<{
  version: string;
  author: string;
}>();
</script>

<template>
  <div class="right-container">
    <TheCourseDashboard />
    <!--
          Placeholder element for the Chaoxing WebView container.
          Note: This element remains empty because Tauri's native child WebView window
          is dynamically positioned and overlayed according to the layout bounds and
          geometry of this placeholder (styled by .chaoxing-webview).

          Scale-Invariant Proportional Layout Transformation Formulas:
          - Position X = Window.width  * (0.50 + 0.01) = 0.51 * W
          - Position Y = Window.height * (0.04 + 0.96 * 0.4375) = 0.46 * H
          - Width      = Window.width  * 0.50 * 0.96 = 0.48 * W
        -->
    <div class="chaoxing-webview">
      <TheChaoxingWebviewController />
    </div>
    <div class="version-info">
      <p>by {{ author }} v{{ version }}</p>
    </div>
  </div>
</template>

<style scoped>
.right-container {
  width: 50%;
  display: flex;
  align-items: center;
  flex-direction: column;
  background-color: transparent;
}

.chaoxing-webview {
  position: relative;
  width: 96%;
  height: 55%;
}

.chaoxing-webview::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: calc(100% + 6px);
  height: calc(100% + 6px);
  background: #0d58a4;
  pointer-events: none;
  z-index: 1;

  --t: 6px;
  clip-path: polygon(
    calc(100% - var(--t)) 0,
    100% var(--t),
    100% 100%,
    var(--t) 100%,
    0 calc(100% - var(--t)),
    calc(100% - var(--t)) calc(100% - var(--t))
  );
}

.version-info {
  padding-right: 40px;
  height: 6.25%;
  width: 100%;
  background-color: transparent;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
</style>
