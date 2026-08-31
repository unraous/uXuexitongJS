<script setup lang="ts">
import { ref, onMounted, useId } from "vue";
import VLabel from "./VLabel.vue";

const {
  modelValue,
  label,
  options = ["undefined", "option1", "option2", "option3"],
  id = useId(),
} = defineProps<{
  modelValue: number;
  label: string;
  options?: string[];
  id?: string;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: number): void;
}>();

const isOpen = ref(false);
const dropdownRef = ref<HTMLElement | null>(null);

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false;
  }
};

onMounted(() => document.addEventListener("click", handleClickOutside));
</script>

<template>
  <div class="base-config-select">
    <VLabel
      :label="label"
      :for="id"
    />

    <div
      ref="dropdownRef"
      class="input-section"
    >
      <div
        :id="id"
        class="select-trigger"
        :class="{ 'is-open': isOpen }"
        @click="isOpen = !isOpen"
        @keydown.space.prevent="isOpen = !isOpen"
        @keydown.enter.prevent="isOpen = !isOpen"
        @keydown.escape.prevent="isOpen = false"
      >
        <span class="selected-text">{{ options?.[modelValue] ?? "" }}</span>
        <span
          class="select-arrow"
          :class="{ 'is-open': isOpen }"
        >
          <svg
            viewBox="0 -960 960 960"
            width="24"
            height="24"
            fill="currentColor"
          >
            <path d="m256-424-56-56 280-280 280 280-56 56-224-223-224 223Z" />
          </svg>
        </span>
      </div>

      <Transition name="dropdown">
        <div
          v-show="isOpen"
          class="select-dropdown-wrapper"
        >
          <div class="select-dropdown">
            <div
              v-for="(opt, index) in options"
              :key="index"
              class="select-option"
              :class="{ 'is-selected': index === modelValue }"
              @click="
                emit('update:modelValue', index);
                isOpen = false;
              "
            >
              {{ opt }}
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.base-config-select {
  display: flex;
  align-items: center;
  width: 100%;
}

.input-section {
  flex-grow: 1;
  position: relative;
}

.select-trigger,
.select-option {
  height: 48px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.select-trigger {
  width: 100%;
  font-size: 1rem;
  border: 2px solid #0d58a4;
  background-color: #ebe2cf;
  justify-content: space-between;
  transition: border-color 0.2s;
}

.select-trigger:hover {
  border-color: #0b4c8d;
}

.selected-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.select-arrow {
  display: flex;
  transition: transform 0.2s;
  color: #0d58a4;
  transform: rotate(180deg);
}

.select-arrow.is-open {
  transform: rotate(0deg);
}

.select-dropdown-wrapper {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 10;
  overflow: hidden;
}

.select-dropdown {
  background-color: #ebe2cf;
  border: 2px solid #0d58a4;
  border-top: none;
  max-height: 192px;
  overflow-y: auto;
  box-shadow: 0 6px 16px rgba(13, 88, 164, 0.15);
}

.select-option {
  transition:
    background-color 0.15s ease-in-out,
    color 0.15s ease-in-out;
}

.select-option:hover {
  background-color: rgba(0, 0, 0, 0.08);
}

.select-option.is-selected {
  background-color: #0d58a4;
  color: #ffffff;
}

.select-dropdown::-webkit-scrollbar {
  width: 5px;
}

.select-dropdown::-webkit-scrollbar-track {
  background: transparent;
}

.select-dropdown::-webkit-scrollbar-thumb {
  background-color: #0b4c8d;
  border-radius: 0px;
}

/* 下拉菜单缓动动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: max-height 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.dropdown-enter-from,
.dropdown-leave-to {
  max-height: 0 !important;
}

.dropdown-enter-to,
.dropdown-leave-from {
  max-height: 194px !important;
}
</style>
