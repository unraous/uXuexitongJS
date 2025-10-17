// 顶部按钮（最小化和关闭）
import QtQuick
import QtQuick.Controls

import "../theme_manager"

ToolButton {
    id: btn;
    width: 32;
    height: 32;

    required property string btnText;
    property color bgColor: Theme.color[8];
    property color textColor: Theme.color[4];
    property color bgHoverColor: textColor;

    contentItem: Text {
        text: btn.btnText;
        font.pixelSize: 20;
        font.bold: true;

        anchors.fill: parent;
        horizontalAlignment: Text.AlignHCenter;
        verticalAlignment: Text.AlignVCenter;

        color: btn.hovered ? btn.bgColor : btn.textColor;
    }

    background: Rectangle {
        color: btn.hovered ? btn.bgHoverColor : "transparent";

        Behavior on color {
            ColorAnimation { duration: 200; }  // 单位：ms
        }
    }
}
