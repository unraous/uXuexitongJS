import QtQuick
import QtQuick.Controls

import "components"


ApplicationWindow {
    id: window

    visible: true
    width: 900
    height: 600
    flags: Qt.Window | Qt.FramelessWindowHint
    color: "transparent"
    title: "XuexitongScript"

    FontLoader {
        id: orbitronFont
        source: "../data/static/ttf/orbitron.ttf"
    }
    
    font.family: orbitronFont.name

    Rectangle {  // 主窗口容器
        id: mainWindow
        anchors.fill: parent
        color: "#ffffff"
        radius: 15

        TitleBar {
            window: window
        }

    }

    MouseArea {
        anchors.fill: parent
        z: -1

        property real clickX: 0
        property real clickY: 0

        onPressed: (mouse) => {
            clickX = mouse.x
            clickY = mouse.y
        }
        
        onPositionChanged: (mouse) => {
            window.x += mouse.x - clickX
            window.y += mouse.y - clickY
        }
        
        acceptedButtons: Qt.LeftButton
    }
}


