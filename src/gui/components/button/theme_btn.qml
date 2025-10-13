// 最主要的按钮样式
import QtQuick
import QtQuick.Controls.Basic

import "../theme_manager"
import "../interface.js" as Interface

Button {
    id: btn;


    property int pixelSize: 48;
    property real gradientPos: btn.hovered ? (
        btn.pressed ? 0.0 : 2.5
    ) : 1.0;
    property var color : Theme.color;

    function saveGetColor(idx) {
        return btn.color[idx] ?? Theme.color[idx] ?? "transparent";
    }

    contentItem: Text {
        id: textItem;
        text: btn.text;
        anchors.fill: parent;
        font.family: btn.font.family;
        font.pixelSize: btn.pixelSize;
        font.bold: true;
        horizontalAlignment: Text.AlignHCenter;
        verticalAlignment: Text.AlignVCenter;
        scale: btn.hovered ? (btn.pressed ? 0.9 : 1.1) : 1.0;
        color: {
            if (!btn.color || btn.color.length < 10) return "transparent";
            return btn.hovered ? btn.saveGetColor(4) : btn.saveGetColor(0);
        }
        Behavior on scale { SpringAnimation { spring: 3; damping: 0.3; duration: 200; } }
        Behavior on color { ColorAnimation { duration: 200; } }
    }

    background: Rectangle { 
        gradient: Gradient {
            id: gradient
            orientation: Gradient.Horizontal;
            GradientStop {
                position: 0.0; color: "transparent"; 
                Behavior on color { ColorAnimation { duration: 200; } }
            }
            GradientStop {
                position: 0.4; color: btn.saveGetColor(6);
                Behavior on color { ColorAnimation { duration: 200; } }
            }
            GradientStop {
                position: 0.5; color: btn.saveGetColor(7);
                Behavior on color { ColorAnimation { duration: 200; } }
            }
            GradientStop {
                position: 0.6; color: btn.saveGetColor(8);
                Behavior on color { ColorAnimation { duration: 200; } }
            }
            GradientStop {
                position: 1.0; color: "transparent";
                Behavior on color { ColorAnimation { duration: 200; } }
            }
        }
        opacity: btn.hovered ? 0.5 : 0.0;
        Behavior on opacity { NumberAnimation { duration: 200; } }
    }

    function calPos(base: real, offset: real): real {
        return (base * offset);
    }

    Behavior on gradientPos { NumberAnimation { duration: 200; easing.type: Easing.InOutQuad; } }

    onClicked: {
        Theme.switchTo(btn.text);
        console.log(`切换到主题 ${btn.text}`);
        Interface.dispatch("set_config", [["metadata", "theme"], btn.text]);
        Interface.dispatch("commit_config", []);
    }
}