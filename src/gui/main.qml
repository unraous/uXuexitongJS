import QtQuick
import QtQuick.Shapes
import QtQuick.Controls
import QtQuick.Window

import "components"
import "components/mask"
import "components/theme_manager"


ApplicationWindow {
    id: window;

    visible: true;
    width: 900;
    height: 600;
    maximumWidth: 900;
    maximumHeight: 600;
    flags: Qt.Window | Qt.FramelessWindowHint;
    color: "transparent";
    title: "XuexitongScript";
    opacity: 0;
    Behavior on opacity { NumberAnimation { duration: 300; easing.type: Easing.InOutQuad } }


    Shape {  // 主窗口布局
        id: mainWindow;
        anchors.fill: parent;
        antialiasing: true;
        
        ShapePath {
            strokeWidth: 0;
            fillGradient: BackgroundMask { width: window.width; height: window.height; }
            PathRectangle {
                x: 0; y: 0;
                width: window.width;
                height: window.height;
                radius: 9;  // 其实我想调大一点,但不知道为什么调大之后背后原生title栏会露出来,所以只能卡到刚好覆盖的位置
            }
        }

        Column {
            id: mainLayout;
            anchors.fill: parent;
            width: parent.width;
            height: parent.height;
            spacing: 0;

            TitleBar {
                id: titleBar;
                window: window;
                family: window.font.family;
                width: parent.width;
                height: 60;
            }

            Row {
                id: menuRow;
                width: parent.width;
                height: titleBar.expand ? window.height - titleBar.height : 0;
                clip: true;
                opacity: titleBar.expand ? 1 : 0;
                property int chosenIndex: 0;
                Behavior on opacity { NumberAnimation { duration: 500; easing.type: Easing.InOutQuad; } }
                Behavior on height { NumberAnimation { duration: 500; easing.type: Easing.InOutCubic; } }
                MenuList {
                    id: menuList;
                    width: menuRow.width * 0.3;
                    height: window.height - titleBar.height;
                    parentPanel: menuRow;
                    padding: 80;
                }
                Item {
                    id: rightPanel;
                    width: parent.width * 0.7;
                    height: window.height - titleBar.height;
                    
                    Rectangle {
                        anchors.fill: parent;
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "transparent"; }
                            GradientStop { position: 0.1; color: Theme.color[2]; }
                            GradientStop { position: 0.9; color: Theme.color[2]; }
                            GradientStop { position: 1.0; color: "transparent"; }
                        }
                        opacity: 0.05;
                        z: -1;  // 放在底层
                    }

                    Column {
                        id : col;
                        anchors.fill: parent
                        padding: 40
                        ThemePage {
                            width: col.width - col.padding * 2;
                            height: menuRow.chosenIndex === 1 ? col.height - col.padding * 2 : 0;
                            Behavior on height { NumberAnimation { duration: 250; easing.type: Easing.InOutQuad; } }
                        }
                        TutorialPage {
                            font: Theme.font;
                            width: col.width - col.padding * 2;
                            height: menuRow.chosenIndex === 0 ? col.height - col.padding * 2 : 0;
                            Behavior on height { NumberAnimation { duration: 250; easing.type: Easing.InOutQuad; } }
                        }
                        
                    }
                }
            }

            Row {
                width: parent.width;
                height: window.height * 0.75;
                ConfigPanel {
                    id: configPanel;
                    width: window.width / 2 ; height: parent.height;
                    family: window.font.family;
                }
                ScriptPanel {
                    id: scriptPanel;
                    width: window.width / 2 ; height: parent.height;
                    family: window.font.family;
                }
            }

            BottomBar {
                family: window.font.family;
                width: parent.width;
                height: 90;
            }
            
        }

    }

    Component.onCompleted: {
        window.font.family = Theme.font.name;
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


