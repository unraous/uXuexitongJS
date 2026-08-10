<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";
import type { TaskStatus } from "@/services/cmds";

const chapterStatus = ref<TaskStatus | null>(null);
let unlisten: UnlistenFn | null = null;

onMounted(async () => {
  try {
    unlisten = await listen<TaskStatus>("chapter-status-update", (event) => {
      chapterStatus.value = event.payload;
    });
  } catch (err) {
    console.error("注册 chapter-status-update 监听失败:", err);
  }
});

onUnmounted(() => {
  if (unlisten) {
    unlisten();
    unlisten = null;
  }
});
</script>

<template>
  <div class="body">
    <div class="config">
      <h2>章节处理状态</h2>
      <div v-if="chapterStatus" class="status-card">
        <div class="status-item">
          <span class="label">当前章节：</span>
          <span class="value title">{{ chapterStatus.title || "未知章节" }}</span>
        </div>
        <div class="status-item">
          <span class="label">处理进度：</span>
          <span class="value">{{ chapterStatus.completed }} / {{ chapterStatus.total }}</span>
        </div>
        <div class="progress-bar-bg">
          <div
            class="progress-bar-fill"
            :style="{
              width: `${Math.min(100, Math.max(0, (chapterStatus.completed / chapterStatus.total) * 100))}%`,
            }"
          ></div>
        </div>
      </div>
      <p v-else class="placeholder">等待接收章节状态通知...</p>
    </div>
  </div>
</template>

<style scoped>
.body {
  padding: 20px;
  width: 100%;
  flex: 1;
  background-color: transparent;
  display: flex;
  align-items: center;
  flex-direction: column;
}

.config {
  padding: 20px;
  width: 100%;
  height: 100%;
}

.status-card {
  margin-top: 16px;
  padding: 16px;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
}

.label {
  opacity: 0.7;
}

.value {
  font-weight: bold;
}

.value.title {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.progress-bar-bg {
  width: 100%;
  height: 8px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background-color: #409eff;
  transition: width 0.3s ease;
}

.placeholder {
  margin-top: 16px;
  opacity: 0.5;
  font-size: 14px;
}
</style>
