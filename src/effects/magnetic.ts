import { onUnmounted, type Ref } from "vue";
import { gsap } from "gsap";

export interface UseMagneticOptions {
  /** 外层容器 DOM 引用 */
  outerRef: Ref<HTMLElement | null>;
  /** 内层视差内容 DOM 引用（可选） */
  innerRef?: Ref<HTMLElement | null>;
  /** 外层磁吸拉力系数（默认 0.12，数值越小磁吸位移越小） */
  outerFactor?: number;
  /** 内层视差拉力系数（默认 0.22） */
  innerFactor?: number;
  /** 最大偏移像素阈值/半径限制（可选，如 25px，防止拉伸过大） */
  maxDistance?: number;
  /** 动画平滑响应时间（秒，默认 0.35s） */
  duration?: number;
  /** 是否处于禁用状态 */
  disabled?: () => boolean;
  /** 鼠标按下时的回调 */
  onMouseDown?: (event: MouseEvent) => void;
}

/**
 * 高性能双层视差磁吸动画 Composable
 */
export function useMagnetic(options: UseMagneticOptions) {
  const {
    outerRef,
    innerRef,
    outerFactor = 0.12,
    innerFactor = 0.22,
    maxDistance,
    duration = 0.35,
    disabled = () => false,
    onMouseDown,
  } = options;

  let btnXTo: ReturnType<typeof gsap.quickTo> | null = null;
  let btnYTo: ReturnType<typeof gsap.quickTo> | null = null;
  let contentXTo: ReturnType<typeof gsap.quickTo> | null = null;
  let contentYTo: ReturnType<typeof gsap.quickTo> | null = null;

  /** 懒加载初始化 GSAP quickTo 管道 */
  const initQuickTo = () => {
    if (!outerRef.value || btnXTo) return;

    btnXTo = gsap.quickTo(outerRef.value, "x", {
      duration,
      ease: "power3.out",
    });
    btnYTo = gsap.quickTo(outerRef.value, "y", {
      duration,
      ease: "power3.out",
    });

    if (innerRef?.value) {
      contentXTo = gsap.quickTo(innerRef.value, "x", {
        duration: duration * 0.75,
        ease: "power3.out",
      });
      contentYTo = gsap.quickTo(innerRef.value, "y", {
        duration: duration * 0.75,
        ease: "power3.out",
      });
    }
  };

  const handleMouseEnter = () => {
    if (disabled() || !outerRef.value) return;
    gsap.to(outerRef.value, {
      scale: 1.025,
      duration: 0.25,
      ease: "power2.out",
    });
  };

  const handleMouseMove = (event: MouseEvent) => {
    if (disabled() || !outerRef.value) return;
    initQuickTo();

    const rect = outerRef.value.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    let deltaX = event.clientX - centerX;
    let deltaY = event.clientY - centerY;

    if (maxDistance && maxDistance > 0) {
      const distance = Math.hypot(deltaX, deltaY);
      if (distance > maxDistance) {
        const angle = Math.atan2(deltaY, deltaX);
        deltaX = Math.cos(angle) * maxDistance;
        deltaY = Math.sin(angle) * maxDistance;
      }
    }

    if (btnXTo && btnYTo) {
      btnXTo(deltaX * outerFactor);
      btnYTo(deltaY * outerFactor);
    }

    if (contentXTo && contentYTo) {
      contentXTo(deltaX * innerFactor);
      contentYTo(deltaY * innerFactor);
    }
  };

  const handleMouseDown = (event: MouseEvent) => {
    if (onMouseDown) {
      onMouseDown(event);
    }
    if (disabled() || !outerRef.value) return;
    gsap.to(outerRef.value, {
      scale: 0.95,
      duration: 0.1,
      ease: "power1.out",
    });
  };

  const handleMouseUp = () => {
    if (disabled() || !outerRef.value) return;
    gsap.to(outerRef.value, {
      scale: 1.025,
      duration: 0.35,
      ease: "back.out(2)",
    });
  };

  const handleMouseLeave = () => {
    if (!outerRef.value) return;

    if (btnXTo && btnYTo) {
      btnXTo(0);
      btnYTo(0);
    }
    if (contentXTo && contentYTo) {
      contentXTo(0);
      contentYTo(0);
    }

    gsap.to(outerRef.value, {
      scale: 1,
      duration: 0.45,
      ease: "back.out(2.5)",
    });

    if (innerRef?.value) {
      gsap.to(innerRef.value, {
        x: 0,
        y: 0,
        duration: 0.45,
        ease: "power2.out",
      });
    }
  };

  onUnmounted(() => {
    btnXTo = null;
    btnYTo = null;
    contentXTo = null;
    contentYTo = null;
  });

  return {
    handleMouseEnter,
    handleMouseMove,
    handleMouseDown,
    handleMouseUp,
    handleMouseLeave,
  };
}
