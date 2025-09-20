// 最主要的按钮样式
import QtQuick
import QtQuick.Controls.Basic

Button {
    id: btn

    property int pixelSize: 18

    contentItem: Text {
        text: btn.enabled ? btn.text : "Done"
        font.pixelSize: btn.pixelSize

        anchors.fill: parent
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        color: btn.enabled ? (
            btn.hovered ? "#000000" : "#ffffff"
        ) : "#777777"
    }

    background: Rectangle {
        radius: btn.height / 2
        color: btn.enabled ? (
            btn.hovered ? "#ffffff" : "#000000"
        ) : "#444444"

        Behavior on color {
            ColorAnimation { duration: 150 }  // 单位：ms
        }
    }

    onPressed: console.log("按钮按下")
    onReleased: console.log("按钮释放")
}