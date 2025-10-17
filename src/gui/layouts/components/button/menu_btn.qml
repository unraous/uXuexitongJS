// 主菜单按钮样式, 同时适用于侧边栏菜单按钮
pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls.Basic
import Qt5Compat.GraphicalEffects

import "../mask"
import "../theme_manager"

Button {
    id: btn;

    property int pixelSize: 24;
    property real gradientPos: btn.hovered ? (
        btn.pressed ? 0.0 : 2.5
    ) : 1.0;
    property bool finished: false;
    property bool light: false;
    property bool glow: false;
    signal after();

    contentItem: Item {
        scale: btn.hovered ? (btn.pressed ? 0.9 : 1.1) : 1.0;

        Behavior on scale { SpringAnimation { spring: 3; damping: 0.3; duration: 200; } }

        Text {
            id: textItem;
            text: btn.text;
            anchors.fill: parent;
            font.family: btn.font.family;
            font.pixelSize: btn.pixelSize;
            font.bold: true;
            horizontalAlignment: Text.AlignHCenter;
            verticalAlignment: Text.AlignVCenter;
            visible: false;
        }

        // 渐变背景
        Rectangle {
            id: g;
            anchors.fill: textItem;
            visible: false;  
            gradient: ButtonMask {
                orientation: Gradient.Horizontal;
                btn: btn;
            }
        }

        OpacityMask {
            id: maskedText
            anchors.fill: textItem
            source: g
            maskSource: textItem
        }

        Glow {
            anchors.fill: maskedText
            source: maskedText
            radius: btn.hovered || btn.glow ? 12 : 0
            samples: 25
            color: btn.light ? (
                btn.glow ? Theme.color[0] : Theme.color[2]
            ) : "transparent"
            spread: 0.3
            opacity: btn.hovered || btn.glow ? 0.7 : 0
            
            Behavior on color { ColorAnimation { duration: 200 } }
            Behavior on radius { NumberAnimation { duration: 200 } }
            Behavior on opacity { NumberAnimation { duration: 200 } }
        }
    }

    background: Rectangle { color: "transparent"; radius: 0; }

    // 保持原有函数
    function calPos(base: real, offset: real): real {
        return (base * offset > 0.75) ? 0.75 : (base * offset);
    }

    Behavior on gradientPos { NumberAnimation { duration: 200; easing.type: Easing.InOutQuad; } }

    onClicked: {
        btn.glow = !btn.glow;
        btn.after();
    }
    
}