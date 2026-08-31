<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import VInput from "@/components/base/VInput.vue";
import VSelector from "@/components/base/VSelector.vue";
import { commands } from "@/services/cmds.ts";

const provider = ref(0);
const providers = ref<string[]>([]);
const model = ref(0);
const models = ref<string[]>([]);
const apiKey = ref("");

const loadProvider = async () => {
  if (providers.value.length === 0) {
    console.error("Provider 列表为空");
    return;
  }

  await commands.switchProvider(providers.value[provider.value]);
  const [fetchedModels, currentModel, fetchedApiKey] = await Promise.all([
    commands.models(),
    commands.currentModel(),
    commands.apiKey(),
  ]);
  models.value = fetchedModels;
  model.value = fetchedModels.includes(currentModel)
    ? fetchedModels.indexOf(currentModel)
    : 0;
  apiKey.value = fetchedApiKey;
};

const setKey = async () => {
  await commands.setKey(apiKey.value);
};

defineExpose({
  setKey,
});

onMounted(async () => {
  const [fetchedProviders, currentProvider] = await Promise.all([
    commands.providers(),
    commands.currentProvider(),
  ]);
  providers.value = fetchedProviders;

  const targetProviderIndex = fetchedProviders.includes(currentProvider)
    ? fetchedProviders.indexOf(currentProvider)
    : 0;
  if (provider.value === targetProviderIndex) {
    await loadProvider();
  } else {
    provider.value = targetProviderIndex;
  }
});

watch(provider, loadProvider);

watch(model, async () => {
  await commands.switchModel(models.value[model.value]);
});
</script>

<template>
  <div class="api-panel">
    <h2 class="title">API</h2>
    <div class="settings-container">
      <VSelector
        v-model="provider"
        label="Provider"
        :options="providers"
      />
      <VSelector
        v-model="model"
        label="Model"
        :options="models"
      />
      <VInput
        id="api-key-input"
        v-model="apiKey"
        label="API Key"
        aria-label="API Key"
        @change="setKey"
      />
    </div>
  </div>
</template>

<style scoped>
.api-panel {
  width: 50%;
  height: 100%;
  flex: 1;
  flex-direction: column;
  display: flex;
}

.settings-container {
  flex: 1;
  display: flex;
  gap: 48px;
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
</style>
