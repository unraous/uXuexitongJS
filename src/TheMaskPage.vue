<script setup lang="ts">
import { getCurrentWebview } from "@tauri-apps/api/webview";
import { invoke } from "@tauri-apps/api/core";
import { onMounted, onUnmounted, ref } from "vue";
import appIcon from "../src-tauri/icons/icon.png";

type MaskPhase = "waiting" | "intro" | "revealing" | "closing";

const phase = ref<MaskPhase>("waiting");
let unlistenStartEvent: (() => void) | null = null;
let unlistenCloseEvent: (() => void) | null = null;

const startIntro = () => {
  phase.value = "intro";
};

const closeMask = () => {
  phase.value = "closing";
};

const revealMain = (event: AnimationEvent) => {
  if (event.animationName === "title-to-menu") {
    phase.value = "revealing";
  }
};

const hideAfterReveal = (event: TransitionEvent) => {
  if (phase.value === "revealing" && event.propertyName === "opacity") {
    void invoke("hide_mask");
  }
};

onMounted(async () => {
  const webview = getCurrentWebview();
  unlistenStartEvent = await webview.listen("start-event", startIntro);
  unlistenCloseEvent = await webview.listen("close-event", closeMask);
  await invoke("show_content");
  await invoke("start_mask");
});

onUnmounted(() => {
  unlistenStartEvent?.();
  unlistenCloseEvent?.();
});
</script>

<template>
  <main
    class="mask"
    :class="phase"
    @transitionend="hideAfterReveal"
  >
    <div
      class="logo"
      @animationend="revealMain"
    >
      <img
        :src="appIcon"
        alt=""
      />
    </div>
    <h1
      class="title"
      @animationend="revealMain"
    >
      uXueScript
    </h1>
  </main>
</template>

<style>
@font-face {
  font-family: "DefaultFont";
  src: url("@/assets/fonts/Mixture.woff2") format("woff2");
  font-weight: 400;
  font-style: normal;
}

html,
body,
#mask {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

body {
  margin: 0;
}

.mask {
  position: fixed;
  inset: 0;
  overflow: hidden;
  color: #0d58a4;
  background: #000;
  opacity: 0;
  pointer-events: none;
  transition: opacity 800ms ease-out;
}

.waiting,
.intro,
.revealing {
  background: linear-gradient(135deg, #e8dcc4 0%, #f0ebe0 100%);
}

.waiting,
.intro {
  opacity: 1;
}

.logo,
.title {
  position: absolute;
  left: 50%;
  opacity: 0;
}

.logo {
  top: calc(50% + min(2vmin, 24px));
  width: min(18vmin, 192px);
  height: min(18vmin, 192px);
  transform: translate(-50%, -50%);
}

.logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 10px 12px rgb(13 88 164 / 28%));
}

.title {
  top: calc(50% + min(13vmin, 140px));
  margin: 0;
  transform: translate(-50%, -50%);
  letter-spacing: 1px;
  -webkit-text-stroke: 1px currentColor;
  font-family: "DefaultFont", Inter, Avenir, Helvetica, Arial, sans-serif;
  font-size: 2rem;
  font-weight: 400;
}

.closing {
  opacity: 1;
  transition-duration: 500ms;
}

.intro .logo {
  animation:
    logo-enter 2s cubic-bezier(0.215, 0.61, 0.355, 1) forwards,
    logo-leave 500ms cubic-bezier(0.55, 0.055, 0.675, 0.19) 2s forwards;
}

.intro .title {
  animation:
    title-enter 2s cubic-bezier(0.215, 0.61, 0.355, 1) forwards,
    title-to-menu 1s cubic-bezier(0.215, 0.61, 0.355, 1) 2.5s forwards;
}

.revealing {
  opacity: 0;
}

.revealing .title {
  top: 2vh;
  opacity: 1;
  transform: translate(-50%, -50%) scale(1);
}

@keyframes logo-enter {
  to {
    top: calc(50% - min(6vmin, 64px));
    opacity: 1;
  }
}

@keyframes logo-leave {
  to {
    opacity: 0;
  }
}

@keyframes title-enter {
  to {
    top: calc(50% + min(5vmin, 54px));
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.25);
  }
}

@keyframes title-to-menu {
  to {
    top: 2vh;
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}
</style>
