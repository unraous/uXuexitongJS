import QtQuick
import QtQuick.Shapes

import "../theme_manager"

RadialGradient {
    id: rg;
    required property real width;
    required property real height;

    centerX: 0.25 * width;
    centerY: -0.35 * height;
    focalX: centerX;
    focalY: centerY;
    centerRadius: Math.max(width, height);
    GradientStop {
        position: 0.0; color: Theme.color[5];
        Behavior on color { ColorAnimation { duration: 200; } }    
    }
    GradientStop {
        position: 0.25; color: Theme.color[6];
        Behavior on color { ColorAnimation { duration: 200; } }
    }
    GradientStop {
        position: 0.5; color: Theme.color[7];
        Behavior on color { ColorAnimation { duration: 200; } }
    }
    GradientStop {
        position: 0.75; color: Theme.color[8];
        Behavior on color { ColorAnimation { duration: 200; } }
    }
    GradientStop {
        position: 1.0; color: Theme.color[9];
        Behavior on color { ColorAnimation { duration: 200; } }
    }
}