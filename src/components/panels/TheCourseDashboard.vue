<script setup lang="ts">
import { onMounted, ref } from "vue";
</script>

<template>
  <div class="dashboard">
    <div class="content">
      <div class="cover"></div>
      <div class="info">
        <div class="title"></div>
        <div class="chapter"></div>
        <div class="task"></div>
      </div>
    </div>
    <div class="progreass-bar"></div>
  </div>
</template>

<style scoped>
.dashboard {
  flex: 1;
  width: 96%;
  height: 38.75%;
  flex-direction: row;
  background-color: yellowgreen;
}

.content {
  height: 80%;
  background-color: bisque;
  flex-direction: column;
}

.cover {
  height: 100%;
  aspect-ratio: 1 / 1;
  background-color: pink;
}

.progress-bar {
  height: 20%;
}
</style>
