import { gsap } from "gsap";

export interface MagneticOptions {
  outerFactor?: number;
  innerFactor?: number;
  duration?: number;
  disabled?: () => boolean;
}

export function createMagnetic(
  outer: HTMLElement,
  inner: HTMLElement,
  options: MagneticOptions = {},
) {
  const {
    outerFactor = 0.1,
    innerFactor = 0.3,
    disabled = () => false,
  } = options;

  const pointerEnter = () => {
    if (disabled()) return;
    gsap.to(outer, {
      scale: 1.05,
      duration: 0.75,
      ease: "elastic.out",
    });
  };

  const pointerMove = (event: PointerEvent) => {
    if (disabled()) return;

    const rect = outer.getBoundingClientRect();
    const deltaX = event.clientX - rect.left - rect.width / 2;
    const deltaY = event.clientY - rect.top - rect.height / 2;

    gsap.to(outer, {
      x: deltaX * outerFactor,
      y: deltaY * outerFactor,
      duration: 0.25,
      ease: "power2.out",
    });

    gsap.to(inner, {
      x: deltaX * innerFactor,
      y: deltaY * innerFactor,
      duration: 0.25,
      ease: "power2.out",
      overwrite: "auto",
    });
  };

  const pointerDown = () => {
    if (disabled()) return;
    gsap.to(outer, {
      scale: 0.95,
      duration: 0.25,
      ease: "power1.out",
      overwrite: "auto",
    });
  };

  const pointerUp = () => {
    if (disabled()) return;
    gsap.to(outer, {
      scale: 1.05,
      duration: 0.75,
      ease: "elastic.out",
      overwrite: "auto",
    });
  };

  const pointerLeave = () => {
    gsap.to(outer, {
      x: 0,
      y: 0,
      scale: 1,
      duration: 0.5,
      ease: "back.out",
    });

    gsap.to(inner, {
      x: 0,
      y: 0,
      duration: 0.75,
      ease: "elastic.out",
      overwrite: "auto",
    });
  };

  return {
    pointerEnter,
    pointerMove,
    pointerLeave,
    pointerDown,
    pointerUp,
  };
}
