import QtQuick

import "../theme_manager"

Gradient {
    GradientStop {
        position: 0.0; color: Theme.color[0]; 
        Behavior on color { ColorAnimation { duration: 200; } }
    }
    GradientStop {
        position: 0.25; color: Theme.color[1];
        Behavior on color { ColorAnimation { duration: 200; } }
    }
    GradientStop {
        position: 0.5; color: Theme.color[2];
        Behavior on color { ColorAnimation { duration: 200; } }
    }
    GradientStop {
        position: 0.75; color: Theme.color[3];
        Behavior on color { ColorAnimation { duration: 200; } }
    }
    GradientStop {
        position: 1.0; color: Theme.color[4];
        Behavior on color { ColorAnimation { duration: 200; } }
    }
}