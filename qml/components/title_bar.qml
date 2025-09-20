// 顶部栏
import QtQuick

import "button"

Rectangle {
    id: titleBar
    width: parent.width
    height: 50
    color: "transparent"
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right

    property var window

    

    Text {
        text: "uXuexitongScript"
        anchors.centerIn: parent
        font.family: titleBar.window.font.family
        font.pixelSize: 20
        color: "#2f3640"
    }

    Row {
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        rightPadding: 16

        TitleBtn {
            btnText: "-"
            bgColor: "#ffffff"
            textColor: "#000000"
            onClicked: titleBar.window.showMinimized()
        }
        
        TitleBtn {
            btnText: "×"
            bgColor: "#ffffff"
            textColor: "#000000"
            onClicked: titleBar.window.close()
        }

    }
        
}