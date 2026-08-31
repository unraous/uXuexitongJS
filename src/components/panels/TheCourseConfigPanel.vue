<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import VInput from "@/components/base/VInput.vue";
import VToggle from "@/components/base/VToggle.vue";
import { commands, OptionsConfig } from "@/services/cmds.ts";

const options = ref<OptionsConfig>();

const speedValue = computed<number>({
  get() {
    return options.value?.speedValue ?? 1;
  },
  set(val: number) {
    if (options.value) {
      options.value.speedValue = val;
    }
  },
});

const setOptions = async () => {
  if (!options.value) return;
  try {
    await commands.setOptions(options.value);
    console.log("设置课程配置成功:", options.value);
  } catch (err) {
    console.error("设置课程配置失败:", err);
  }
};

defineExpose({
  setOptions,
});

onMounted(async () => {
  try {
    const res = await commands.options();
    options.value = res;
  } catch (err) {
    console.error("获取配置失败:", err);
  }
});
</script>

<template>
  <div class="course-config-panel">
    <h2 class="title">Course</h2>
    <div
      v-if="options"
      class="settings-container"
    >
      <VToggle
        v-model="options.persistSession"
        label="Perisist Session"
      />
      <VToggle
        v-model="options.muteWebview"
        label="Mute Course Webview"
      />
      <VToggle
        v-model="options.speedLock"
        label="Lock Playing Speed"
      />
      <VInput
        id="playing-speed-input"
        v-model.number="speedValue"
        placeholder="input number here"
        label="Playing Speed"
        aria-label="Playing Speed"
        pattern="\d+(?:\.\d*)?"
        class="speed-input"
        @change="setOptions"
      />
    </div>
  </div>
</template>

<style scoped>
.course-config-panel {
  height: 100%;
  flex: 1;
  flex-direction: column;
  display: flex;
}

.settings-container {
  flex: 1;
  display: flex;
  gap: 16px;
  flex-direction: column;
}

.title {
  display: flex;
  height: 48px;
  font-size: 1.5rem;
  align-items: center;
  justify-content: center;
}

:deep(.base-config-select:first-child .select-dropdown-wrapper) {
  z-index: 20;
}

/* Model 下拉菜单 z-index 低一点 */
:deep(.base-config-select:nth-child(2) .select-dropdown-wrapper) {
  z-index: 19;
}

.speed-input :deep(.input-field) {
  text-align: center;
}
</style>
