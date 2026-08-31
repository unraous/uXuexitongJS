<script setup lang="ts">
const { label, for: htmlFor } = defineProps<{
  label: string;
  for: string;
}>();
</script>

<template>
  <label
    :for="htmlFor"
    class="label-text"
  >
    {{ label }}
  </label>
</template>

<style scoped>
.label-text {
  flex-shrink: 0;
  width: 35%; /* 固定的标签宽度 */
  text-align: center;

  font-size: 1.25rem;
  color: #0d58a4;
  letter-spacing: 1px;
}
</style>
