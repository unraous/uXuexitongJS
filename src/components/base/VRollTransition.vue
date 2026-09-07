<script setup lang="ts">
import { nextTick, onUnmounted, ref, watch } from "vue";

const props = defineProps<{ value: string | number }>();
defineSlots<{ default(props: { value: string | number }): unknown }>();

const current = ref(props.value);
const incoming = ref<string | number | null>(null);
const isRolling = ref(false);
const duration = 240;
let disposed = false;
let safetyTimer: ReturnType<typeof setTimeout> | null = null;

const cleanupTimer = () => {
  if (safetyTimer !== null) clearTimeout(safetyTimer);
  safetyTimer = null;
};

const startTransition = async () => {
  if (disposed || incoming.value !== null || props.value === current.value) return;
  incoming.value = props.value;
  // 先挂载待入场内容，再启动动画。
  await nextTick();
  if (disposed) return;
  isRolling.value = true;
  safetyTimer = setTimeout(commitTransition, duration + 40);
};

const commitTransition = async () => {
  if (disposed || incoming.value === null) return;
  cleanupTimer();
  current.value = incoming.value;
  incoming.value = null;
  isRolling.value = false;
  // 卸载上一轮入场节点，下一轮只取最新值。
  await nextTick();
  void startTransition();
};

const onAnimationEnd = (event: AnimationEvent) => {
  if (event.target !== event.currentTarget) return;
  const element = event.currentTarget as HTMLElement;
  if (event.animationName !== getComputedStyle(element).animationName) return;
  void commitTransition();
};

watch(() => props.value, startTransition);
onUnmounted(() => {
  disposed = true;
  cleanupTimer();
});
</script>

<template>
  <div class="roll-viewport" :style="{ '--roll-duration': `${duration}ms` }">
    <div class="roll-item" :class="{ 'roll-out': isRolling }">
      <slot :value="current" />
    </div>
    <div
      v-if="incoming !== null"
      class="roll-item roll-in"
      :class="{ 'roll-active': isRolling }"
      @animationend="onAnimationEnd"
    >
      <slot :value="incoming" />
    </div>
  </div>
</template>

<style scoped>
.roll-viewport {
  container-type: size;
  position: relative;
  overflow: hidden;
  min-width: 0;
  display: grid;
  grid-template-areas: "stack";
  grid-template-columns: minmax(0, 1fr);
  align-items: center;
}

.roll-item {
  grid-area: stack;
  width: 100%;
  min-width: 0;
  display: flex;
  align-items: center;
  text-align: inherit;
}

/* 位移覆盖容器高度与内容自身高度，适应不同字号和多行内容。 */
.roll-in {
  transform: translateY(calc(-100% - 100cqh));
}

.roll-out {
  animation: rollOut var(--roll-duration) cubic-bezier(0.25, 1, 0.5, 1) forwards;
}

.roll-in.roll-active {
  animation: rollIn var(--roll-duration) cubic-bezier(0.25, 1, 0.5, 1) forwards;
}

@keyframes rollOut {
  from { transform: translateY(0); }
  to { transform: translateY(calc(100% + 100cqh)); }
}

@keyframes rollIn {
  from { transform: translateY(calc(-100% - 100cqh)); }
  to { transform: translateY(0); }
}
</style>
