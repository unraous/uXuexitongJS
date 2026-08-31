import { ref, onScopeDispose } from "vue";

export function useClock() {
  const currentTime = ref("");

  const updateClock = () => {
    const now = new Date();
    currentTime.value = [now.getHours(), now.getMinutes(), now.getSeconds()]
      .map((v) => String(v).padStart(2, "0"))
      .join(":");
  };

  updateClock();
  const timer = setInterval(updateClock, 1000);

  onScopeDispose(() => {
    clearInterval(timer);
  });

  return {
    currentTime,
  };
}
