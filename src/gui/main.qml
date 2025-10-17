import QtQuick
import QtQuick.Shapes
import QtQuick.Controls
import QtQuick.Window

import "layouts"
import "layouts/components/mask"
import "layouts/components/theme_manager"


ApplicationWindow {
    id: window;

    visible: true;
    width: 900;
    height: 600;
    x : (Screen.width - window.width) / 2;
    y : (Screen.height - window.height) / 2;    
    maximumWidth: 900;
    maximumHeight: 600;
    flags: Qt.Window | Qt.FramelessWindowHint;
    color: "transparent";
    title: "XuexitongScript";
    opacity: 0;


    property bool startupAnimRunning: true

    Behavior on opacity { NumberAnimation { duration: 300; easing.type: Easing.InOutQuad; } }

    Shape {  // 主窗口布局
        id: mainWindow;
        anchors.fill: parent;
        antialiasing: true;
        
        ShapePath {
            strokeWidth: 0;
            fillGradient: BackgroundMask { width: window.width; height: window.height; }
            PathRectangle {
                x: 0; y: 0;
                width: window.width; height: window.height;
                radius: 9;  // 其实我想调大一点,但不知道为什么调大之后背后原生title栏会露出来,所以只能卡到刚好覆盖的位置
            }
        }

        MainLayout {
            id: mainLayout;
            anchors.fill: parent;
            window: window;
        }

    }

    PropertyAnimation {
        id: startupAnim
        target: window
        property: "y"
        from: (Screen.height - window.height) / 2 + 60
        to: (Screen.height - window.height) / 2
        duration: 500
        easing.type: Easing.OutBack
        easing.overshoot: 3
        running: window.startupAnimRunning
        onFinished: window.startupAnimRunning = false
    }

    Component.onCompleted: {

        window.font.family = Theme.font.name;
        window.opacity = 1;
        window.startupAnimRunning = true;
    }

    MouseArea {
        anchors.fill: parent;
        z: -1;

        property real clickX: 0;
        property real clickY: 0;

        onPressed: (mouse) => {
            clickX = mouse.x;
            clickY = mouse.y;
        }
        
        onPositionChanged: (mouse) => {
            window.x += mouse.x - clickX;
            window.y += mouse.y - clickY;
        }
        
        acceptedButtons: Qt.LeftButton;
    }
}


