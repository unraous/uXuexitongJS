import QtQuick
import QtQuick.Controls

Rectangle {
    id: tbx
    width: 300
    height: 50
    color: "transparent"

    property string key: "TestKey"
    property string value: "TestValue"

    Row {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 12

        Label {
            text: tbx.key
            color: "#333"
            font.pixelSize: 16
            verticalAlignment: Label.AlignVCenter
            width: 80
        }

        TextField {
            id: inputField
            text: tbx.value
            placeholderText: "请输入内容"
            font.pixelSize: 16
            background: Rectangle { color: "transparent" }
            anchors.verticalCenter: parent.verticalCenter
            width: tbx.width - 100
            onTextChanged: tbx.value = text
        }
    }
    
}