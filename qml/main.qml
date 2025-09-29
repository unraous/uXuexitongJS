import QtQuick
import QtQuick.Shapes
import QtQuick.Controls
import QtQuick.Window

import "components"


ApplicationWindow {
    id: window;

    visible: true;
    width: 900;
    height: 600;
    maximumWidth: 900;
    maximumHeight: 600;
    flags: Qt.Window | Qt.FramelessWindowHint;
    color: "transparent";
    title: qsTr("XuexitongScript");
    opacity: 0;
    Behavior on opacity { NumberAnimation { duration: 300; easing.type: Easing.InOutQuad } }


    FontLoader {
        id: xFont;
        source: "../data/static/ttf/orbitron.ttf";
    }
    FontLoader {
        id: bFont;
        source: "../data/static/ttf/ChillRoundF.ttf"; // 替换为你的b字体路径
    }

    font.family: xFont.name;


    Shape {  // 主窗口布局
        id: mainWindow;
        anchors.fill: parent;
        antialiasing: true;
        
        ShapePath {
            strokeWidth: 0;
            fillGradient: RadialGradient {
                centerX: 0.25 * window.width;
                centerY: -0.35 * window.height;
                focalX: centerX;
                focalY: centerY;
                centerRadius: Math.max(window.width, window.height);
                GradientStop { position: 0.0; color: "#18324A"; }
                GradientStop { position: 0.25; color: "#204060"; }
                GradientStop { position: 0.5; color: "#274A60"; }
                GradientStop { position: 0.75; color: "#1B3A4D"; }
                GradientStop { position: 1.0; color: "#101A26"; }
            }
            PathRectangle {
                x: 0; y: 0;
                width: window.width;
                height: window.height;
                radius: 9;  //其实我想调大一点,但不知道为什么调大之后背后会有个原生title栏,所以只能卡到刚好覆盖的位置
            }
        }

        Column {
            id: mainLayout;
            anchors.fill: parent;
            width: parent.width;
            height: parent.height;
            spacing: 0;

            TitleBar {
                window: window;
                family: xFont.name;
                width: parent.width;
                height: 60;
            }

            Row {
                width: parent.width;
                height: window.height * 0.75;
                ConfigPanel {
                    id: configPanel;
                    width: window.width / 2 ; height: parent.height;
                    family: xFont.name;
                }
                ScriptPanel {
                    id: scriptPanel;
                    width: window.width / 2 ; height: parent.height;
                    family: xFont.name;
                }
            }

            BottomBar {
                family: xFont.name;
                width: parent.width;
                height: 90;
            }
            
        }


    }

    Component.onCompleted: {
        window.opacity = 1;
        
        // 存储初始Y位置，使用安全的相对坐标
        var initialY = window.y;
        window.y = initialY + 60; // 先向下移动20像素
        
        var startupAnimation = Qt.createQmlObject(`
            import QtQuick
            NumberAnimation {
                id: startupAnim;
                running: true;
                target: window;
                property: "y";
                to: ${initialY};
                duration: 500;
                easing.type: Easing.OutBack;
                easing.overshoot: 3;
                onFinished: startupAnim.destroy();
            }
        `, window, "startupAnimation");
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


