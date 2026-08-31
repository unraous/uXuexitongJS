<script setup lang="ts">
import MenuBar from "@/components/TheMenuBar.vue";
import TheLeftLayout from "./TheLeftLayout.vue";
import TheRightLayout from "./TheRightLayout.vue";
import { onMounted, ref } from "vue";
import { commands, MetadataConfig } from "@/services/cmds.ts";

const metadata = ref<MetadataConfig>({
  title: "uxs",
  author: "unraous",
  version: "x.x.x",
});

onMounted(async () => {
  metadata.value = await commands.metadata();
});
</script>

<template>
  <main class="container">
    <MenuBar :app-title="metadata.title!" />
    <div class="main-layout">
      <TheLeftLayout />
      <TheRightLayout
        :author="metadata.author!"
        :version="metadata.version!"
      />
    </div>
  </main>
</template>

<style scoped>
.container {
  display: flex;
  height: 100vh;
  width: 100vw;
  flex-direction: column;
  position: relative;
  background: linear-gradient(135deg, #e8dcc4 0%, #f0ebe0 100%);
}

.main-layout {
  flex: 1;
  display: flex;
  flex-direction: row;
}
</style>
