import { watchEffect, toValue, type MaybeRefOrGetter } from "vue";
import { gsap } from "gsap";

export interface UseMagneticOptions {
  outerFactor?: number;
  innerFactor?: number;
  disabled?: MaybeRefOrGetter<boolean>;
}

export function useMagnetic(
  outerRef: MaybeRefOrGetter<HTMLElement | null | undefined>,
  innerRef?: MaybeRefOrGetter<HTMLElement | null | undefined>,
  options: UseMagneticOptions = {},
) {
  const { outerFactor = 0.1, innerFactor = 0.3, disabled = false } = options;

  watchEffect((onCleanup) => {
    const outer = toValue(outerRef);
    const inner = innerRef ? toValue(innerRef) : null;
    const isDisabled = toValue(disabled);

    if (!outer || isDisabled) {
      if (outer) {
        gsap.to(outer, { x: 0, y: 0, scale: 1, duration: 0.3, overwrite: "auto" });
      }
      if (inner) {
        gsap.to(inner, { x: 0, y: 0, duration: 0.3, overwrite: "auto" });
      }
      return;
    }

    const onPointerEnter = () => {
      gsap.to(outer, {
        scale: 1.05,
        duration: 0.75,
        ease: "elastic.out",
      });
    };

    const onPointerMove = (event: PointerEvent) => {
      const rect = outer.getBoundingClientRect();
      const deltaX = event.clientX - rect.left - rect.width / 2;
      const deltaY = event.clientY - rect.top - rect.height / 2;

      gsap.to(outer, {
        x: deltaX * outerFactor,
        y: deltaY * outerFactor,
        duration: 0.25,
        ease: "power2.out",
      });

      if (inner) {
        gsap.to(inner, {
          x: deltaX * innerFactor,
          y: deltaY * innerFactor,
          duration: 0.25,
          ease: "power2.out",
          overwrite: "auto",
        });
      }
    };

    const onPointerDown = () => {
      gsap.to(outer, {
        scale: 0.95,
        duration: 0.25,
        ease: "power1.out",
        overwrite: "auto",
      });
    };

    const onPointerUp = () => {
      gsap.to(outer, {
        scale: 1.05,
        duration: 0.75,
        ease: "elastic.out",
        overwrite: "auto",
      });
    };

    const onPointerLeave = () => {
      gsap.to(outer, {
        x: 0,
        y: 0,
        scale: 1,
        duration: 0.5,
        ease: "back.out",
      });

      if (inner) {
        gsap.to(inner, {
          x: 0,
          y: 0,
          duration: 0.75,
          ease: "elastic.out",
          overwrite: "auto",
        });
      }
    };

    outer.addEventListener("pointerenter", onPointerEnter);
    outer.addEventListener("pointermove", onPointerMove);
    outer.addEventListener("pointerdown", onPointerDown);
    outer.addEventListener("pointerup", onPointerUp);
    outer.addEventListener("pointerleave", onPointerLeave);

    onCleanup(() => {
      outer.removeEventListener("pointerenter", onPointerEnter);
      outer.removeEventListener("pointermove", onPointerMove);
      outer.removeEventListener("pointerdown", onPointerDown);
      outer.removeEventListener("pointerup", onPointerUp);
      outer.removeEventListener("pointerleave", onPointerLeave);
      gsap.killTweensOf([outer, inner].filter(Boolean));
    });
  });
}
