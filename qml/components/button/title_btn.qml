// 顶部按钮（最小化和关闭）
import QtQuick
import QtQuick.Controls

ToolButton {
    id: btn
    width: 32
    height: 32

    property string btnText
    property color bgColor: "#ffffff"
    property color textColor: "#000000"

    contentItem: Text {
        text: btn.btnText
        font.pixelSize: 16

        anchors.fill: parent
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter

        color: btn.hovered ? btn.bgColor : btn.textColor
    }

    background: Rectangle {
        color: btn.hovered ? btn.textColor : btn.bgColor

        Behavior on color {
            ColorAnimation { duration: 150 }  // 单位：ms
        }
    }
}
