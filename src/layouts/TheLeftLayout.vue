<script setup lang="ts">
import TheConfigLayout from "./TheConfigLayout.vue";
import TheInfoPanel from "@/components/panels/TheInfoPanel.vue";
</script>

<template>
  <div class="left-container">
    <TheInfoPanel class="info-panel" />
    <TheConfigLayout />
  </div>
</template>

<style scoped>
.left-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: transparent;
}

.info-panel {
  height: 45%;
  background-color: transparent;
}
</style>
