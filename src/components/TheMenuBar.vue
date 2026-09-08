<script setup lang="ts">
import CloseIcon from "@/assets/close.svg?component";
import MinimizeIcon from "@/assets/remove.svg?component";
import { commands } from "@/services/cmds";
import { ref } from "vue";

defineProps<{
  appTitle: string;
}>();

const minimizeLock = ref(false);
const closeLock = ref(false);

const minimizeApp = async () => {
  if (minimizeLock.value) return;
  minimizeLock.value = true;
  await commands.minimize();
  minimizeLock.value = false;
};

const closeApp = async () => {
  if (closeLock.value) return;
  closeLock.value = true;
  await commands.close();
  closeLock.value = false;
};
</script>

<template>
  <div class="menu-bar">
    <div class="title">
      {{ appTitle }}
    </div>
    <button
      type="button"
      @click="minimizeApp"
    >
      <MinimizeIcon class="icon" />
    </button>
    <button
      type="button"
      @click="closeApp"
    >
      <CloseIcon class="icon" />
    </button>
  </div>
</template>

<style scoped>
.menu-bar {
  height: 4%;
  background-color: transparent;
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  position: relative;
}

.title {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  color: #0d58a4;
  letter-spacing: 1px;
  -webkit-text-stroke: 1px currentColor;
  font-size: 2rem;
}

button {
  aspect-ratio: 1;
  border: none;
  border-radius: 0%;
  background-color: transparent;
  color: #0d58a4;
  height: 100%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s ease-out;
}

/* 悬停状态 */
button:hover {
  background-color: #0d58a4;
  color: #ede5d5;
}
</style>
