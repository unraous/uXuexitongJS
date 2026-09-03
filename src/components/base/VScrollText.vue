<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted } from "vue";

const props = defineProps<{
  text: string | number;
}>();

// 当前停留在视窗中央的文本
const current = ref<string | number>(props.text ?? "");
// 准备进场或正在进场的文本（静止时为 null，保持单节点洁净 DOM）
const incoming = ref<string | number | null>(null);
// 动画激活状态
const isRolling = ref(false);

let safetyTimer: ReturnType<typeof setTimeout> | null = null;

const cleanupTimer = () => {
  if (safetyTimer) {
    clearTimeout(safetyTimer);
    safetyTimer = null;
  }
};

const commitTransition = () => {
  cleanupTimer();
  if (incoming.value !== null) {
    current.value = incoming.value;
    incoming.value = null;
  }
  isRolling.value = false;
};

watch(
  () => props.text,
  async (newVal) => {
    const target = newVal ?? "";
    if (target === current.value) return;

    cleanupTimer();

    incoming.value = target;
    isRolling.value = false;

    // 等待挂载到待命位后启动动画
    await nextTick();
    isRolling.value = true;

    // 0.28s 兜底自动收尾（防止系统挂起或休眠中断 animationend 事件）
    safetyTimer = setTimeout(commitTransition, 280);
  },
);

onUnmounted(() => {
  cleanupTimer();
});
</script>

<template>
  <div class="roll-viewport">
    <!-- 当前元素：静止时居中，翻转时下移出框 -->
    <div
      class="roll-item"
      :class="{ 'roll-out': isRolling }"
    >
      <div class="roll-content">
        <slot :text="current">{{ current }}</slot>
      </div>
    </div>

    <!-- 进场元素：共享同一 Grid 槽位，自物理安全高位下沉进场 -->
    <div
      v-if="incoming !== null"
      class="roll-item roll-in"
      :class="{ 'roll-active': isRolling }"
      @animationend="commitTransition"
    >
      <div class="roll-content">
        <slot :text="incoming">{{ incoming }}</slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
/*
  使用 CSS Grid 单单元格堆叠布局 (Single-Cell Grid Stacking)
  - container-type: size 建立容器查询上下文，精确获取视窗高度 (100cqh)
  - 新旧节点在同一个 Grid 槽位自动对齐，彻底告别绝对定位破坏布局的问题
*/
.roll-viewport {
  container-type: size;
  position: relative;
  overflow: hidden;
  width: 100%;
  height: 100%;
  display: grid;
  grid-template-areas: "stack";
  align-items: center;
}

.roll-item {
  grid-area: stack;
  width: 100%;
  display: flex;
  align-items: center;
  text-align: inherit;
}

/* 支持自动折行与多行显示，继承父级对齐设定 */
.roll-content {
  max-width: 100%;
  white-space: normal;
  word-break: break-all;
  word-wrap: break-word;
  line-height: 1.25;
  text-align: inherit;
}

/*
  数学严格位移原理：
  当元素垂直居中时，将其彻底移出视窗顶/底所需的最小位移为 (H_container + H_element) / 2。
  此处位移量严格取 (100cqh [容器高] + 100% [文字自身高])，必然严格大于临界位移。
  因此，无论字号多大、文本折几行，进场前与离场后都绝对不可能露出任何边缘。
*/
.roll-in {
  transform: translateY(calc(-100% - 100cqh));
}

.roll-out {
  animation: rollOut 0.24s cubic-bezier(0.25, 1, 0.5, 1) forwards;
}

.roll-in.roll-active {
  animation: rollIn 0.24s cubic-bezier(0.25, 1, 0.5, 1) forwards;
}

@keyframes rollOut {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(calc(100% + 100cqh));
  }
}

@keyframes rollIn {
  from {
    transform: translateY(calc(-100% - 100cqh));
  }
  to {
    transform: translateY(0);
  }
}
</style>
