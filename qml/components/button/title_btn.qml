// 顶部按钮（最小化和关闭）
import QtQuick
import QtQuick.Controls

ToolButton {
    id: btn;
    width: 32;
    height: 32;

    property string btnText;
    property color bgColor: "#1B3A4D";
    property color textColor: "#6F89A2";

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
        color: btn.hovered ? btn.textColor : "transparent";

        Behavior on color {
            ColorAnimation { duration: 200; }  // 单位：ms
        }
    }
}
