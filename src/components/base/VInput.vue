<script setup lang="ts">
import { useId } from "vue";
import VTextBox from "./VTextBox.vue";
import VLabel from "./VLabel.vue";

const {
  modelValue,
  label,
  placeholder = "",
  pattern = ".*",
  id = useId(),
} = defineProps<{
  modelValue: string | number;
  label: string;
  placeholder?: string;
  pattern?: string;
  id?: string;
}>();

const emit = defineEmits(["update:modelValue", "change"]);
</script>

<template>
  <div class="base-config-input">
    <!-- 仅保留文本标签，设定固定宽度以确保右侧输入框对齐 -->
    <VLabel
      :label="label"
      :for="id"
    />
    <VTextBox
      :id="id"
      :model-value="modelValue"
      :placeholder="placeholder"
      :pattern="pattern"
      class="input-section"
      @update:model-value="emit('update:modelValue', $event)"
      @change="emit('change', $event)"
    />
  </div>
</template>

<style scoped>
.base-config-input {
  display: flex;
  align-items: center;
  width: 100%;
}

.input-section {
  flex-grow: 1;
}
</style>
