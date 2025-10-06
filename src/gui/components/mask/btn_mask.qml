import QtQuick

import "../theme_manager"

Gradient {
    id: gradient
    required property var btn;

    GradientStop {
        position: gradient.btn.calPos(0.0, gradient.btn.gradientPos);
        color: gradient.btn.finished ? Theme.color[5] : Theme.color[0];
        // 添加颜色动画行为
        Behavior on color { ColorAnimation { duration: 200; easing.type: Easing.InOutQuad } }
    }
    GradientStop {
        position: gradient.btn.calPos(0.25, gradient.btn.gradientPos);
        color: gradient.btn.finished ? Theme.color[6] : Theme.color[1];
        // 添加颜色动画行为
        Behavior on color { ColorAnimation { duration: 200; easing.type: Easing.InOutQuad } }
    }
    GradientStop {
        position: gradient.btn.calPos(0.5, gradient.btn.gradientPos);
        color: gradient.btn.finished ? Theme.color[7] : Theme.color[2];
        // 添加颜色动画行为
        Behavior on color { ColorAnimation { duration: 200; easing.type: Easing.InOutQuad } }
    }
    GradientStop {
        position: gradient.btn.calPos(0.75, gradient.btn.gradientPos);
        color: gradient.btn.finished ? Theme.color[8] : Theme.color[3];
        // 添加颜色动画行为
        Behavior on color { ColorAnimation { duration: 200; easing.type: Easing.InOutQuad } }
    }
    GradientStop {
        position: 1.0;
        color: gradient.btn.finished ? Theme.color[9] : Theme.color[4];
        // 添加颜色动画行为
        Behavior on color { ColorAnimation { duration: 200; easing.type: Easing.InOutQuad } }
    }
}