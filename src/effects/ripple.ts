import { gsap } from "gsap";

export interface UseRippleOptions {
  /** 涟漪放大倍数（默认 2.0） */
  scale?: number;
  /** 动画消逝时间（秒，默认 0.6s） */
  duration?: number;
}

/**
 * 基于 GSAP 的高斯/波纹涟漪特效 Composable
 */
export function useRipple(options: UseRippleOptions = {}) {
  const { scale = 2.0, duration = 0.6 } = options;

  /**
   * 触发生成波纹并在动画结束后利用 GSAP 自动销毁 DOM
   * @param event 鼠标点击事件
   * @param disabled 是否处于禁用状态
   */
  const createRipple = (event: MouseEvent, disabled: boolean = false) => {
    if (disabled) return;

    const target = event.currentTarget as HTMLElement;
    if (!target) return;

    const rect = target.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height) * scale;
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    const circle = document.createElement("span");
    circle.className = "gsap-ripple";
    circle.style.position = "absolute";
    circle.style.borderRadius = "50%";
    circle.style.pointerEvents = "none";
    circle.style.background = "rgba(255, 255, 255, 0.75)";
    circle.style.left = `${x}px`;
    circle.style.top = `${y}px`;
    circle.style.width = `${size}px`;
    circle.style.height = `${size}px`;

    target.appendChild(circle);

    gsap.fromTo(
      circle,
      { scale: 0, opacity: 0.5 },
      {
        scale: 1,
        opacity: 0,
        duration: duration,
        ease: "power2.out",
        onComplete: () => {
          circle.remove();
        },
      },
    );
  };

  return {
    createRipple,
  };
}
