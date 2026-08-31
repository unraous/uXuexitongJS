<script setup lang="ts">
import VButton from "@/components/base/VButton.vue";
import TheAPIPanel from "@/components/panels/TheAPIPanel.vue";
import TheCourseConfigPanel from "@/components/panels/TheCourseConfigPanel.vue";
import { commands } from "@/services/cmds";
import { ref } from "vue";

const apiPanelRef = ref<InstanceType<typeof TheAPIPanel> | null>(null);
const courseConfigPanelRef = ref<InstanceType<
  typeof TheCourseConfigPanel
> | null>(null);

const saveConfig = async () => {
  await Promise.all([
    apiPanelRef.value?.setKey(),
    courseConfigPanelRef.value?.setOptions(),
  ]).catch((e) => console.error("设置配置失败: ", e));
  await commands.saveConfig().catch((e) => console.error("保存配置失败: ", e));
};
</script>

<template>
  <div class="setting-panel">
    <h1 class="title">Configuration</h1>
    <div class="info-panel">
      <TheAPIPanel ref="apiPanelRef" />
      <TheCourseConfigPanel ref="courseConfigPanelRef" />
    </div>
    <div
      class="save-button"
      @click="saveConfig"
    >
      <VButton
        label="Save"
        style="width: 35%; height: 60%; font-size: 1.5rem"
      />
    </div>
  </div>
</template>

<style scoped>
.setting-panel {
  flex: 1;
  flex-direction: column;
}

.title {
  height: 10%;
  width: 100%;
  font-size: 2rem;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.info-panel {
  height: 55%;
  flex: 1;
  display: flex;
  gap: 16px;
  flex-direction: row;
}

.save-button {
  height: 20%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
