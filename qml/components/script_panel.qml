import QtQuick
import QtQuick.Controls.Basic
import Qt5Compat.GraphicalEffects

import "button"
import "box"

Rectangle {
    id: scriptPanel;
    width: 450;
    height: 450;
    color: "transparent";
    property string family;
    property int process: 0; // 添加进度属性
    property bool settingOpen: false;

    

    Item {
        id: settingCont;
        x: scriptPanel.settingOpen ? 50 : parent.width - width - 60
        y: 40
        width: setting.width; height: setting.height;
        property bool hovered: false;
        Behavior on x { NumberAnimation { duration: 500; easing.type: Easing.InOutCubic } }
        transform: Rotation {
            origin.x: setting.width / 2
            origin.y: setting.height / 2
            angle: settingCont.hovered ? 240 : 0;   // 这里设置旋转角度
            Behavior on angle { NumberAnimation { duration: 300; easing.type: Easing.InOutCubic } }
        }
        
        Image {
            id: setting;
            source: "file:///" + "D:\\Workspace\\uXuexitongJS\\data\\static\\svg\\setting-2.svg";
            width: 50;
            height: 48;
        }


        Rectangle {
            id: g;
            anchors.fill: parent;
            gradient: Gradient {
                orientation: Gradient.Horizontal;
                GradientStop { position: 0.0; color: "#60EFDB"; }
                GradientStop { position: 0.25; color: "#BEF2E5"; }
                GradientStop { position: 0.5; color: "#C5E7F1"; }
                GradientStop { position: 0.75; color: "#79CEED"; }
                GradientStop { position: 1.0; color: "#6F89A2"; }
            }
            visible: false;
        }
        
        OpacityMask {
            anchors.fill: setting;
            source: g;
            maskSource: setting;
        }

        MouseArea {
            anchors.fill: parent;
            cursorShape: Qt.PointingHandCursor;
            hoverEnabled: true
            onHoveredChanged: {
                    settingCont.hovered = !settingCont.hovered;
            }
            onClicked: {
                scriptPanel.settingOpen = !scriptPanel.settingOpen;
            }
        }
    }

    Row {
        anchors.fill: parent;
        width: parent.width;
        height: parent.height;
        anchors.topMargin: 80;
        anchors.bottomMargin: 80;
        

        Column {
            id: step;
            width: scriptPanel.settingOpen ? 0 : parent.width;
            opacity: scriptPanel.settingOpen ? 0 : 1;
            height: parent.height;
            spacing: 25;

            Behavior on width { NumberAnimation { duration: 500; easing.type: Easing.InOutCubic; } }
            Behavior on opacity { NumberAnimation { duration: 500; easing.type: Easing.InOutBack; } }

            Item {
                width: parent.width;
                height: 30;
                
                Text {
                    id: titleText;
                    anchors.centerIn: parent;
                    font.family: scriptPanel.family;    
                    text: "Script Panel";
                    font.pixelSize: 24;
                    font.bold: true;
                    visible: false;
                }

                Rectangle {
                    id: gradientRect2;
                    anchors.fill: parent;
                    gradient: Gradient {
                        orientation: Gradient.Horizontal;
                        GradientStop { position: 0.0; color: "#60EFDB"; }
                        GradientStop { position: 0.25; color: "#BEF2E5"; }
                        GradientStop { position: 0.5; color: "#C5E7F1"; }
                        GradientStop { position: 0.75; color: "#79CEED"; }
                        GradientStop { position: 1.0; color: "#6F89A2"; }
                    }
                    visible: false;
                }
                
                OpacityMask {
                    anchors.fill: titleText;
                    source: gradientRect2;
                    maskSource: titleText;
                }
            }

            Row {
                leftPadding: step.width * 0.149;
                Rectangle {
                    width: 8;
                    height: {
                        switch (scriptPanel.process) {
                            case 0: 1; break;
                            case 1: 255 * 0.33; break;
                            case 2: 255 * 0.67; break;
                            case 3: 255; break;
                            default: 255;
                        }
                    }
                    opacity: scriptPanel.process === 0 ? 0 : 1;
                    gradient: Gradient {
                        orientation: Gradient.Vertical;
                        GradientStop { position: 0.0; color: "#60EFDB"; }   // 青绿色
                        GradientStop { position: 0.25; color: "#BEF2E5"; }  // 浅青绿色
                        GradientStop { position: 0.5; color: "#C5E7F1"; }   // 浅蓝色
                        GradientStop { position: 0.75; color: "#79CEED"; }  // 天蓝色
                        GradientStop { position: 1.0; color: "#6F89A2"; }   // 蓝灰色
                    }
                    radius: width / 2;

                    Behavior on height { NumberAnimation { duration: 300; easing.type: Easing.InOutQuad } }
                }
                Column {
                    width: step.width * 0.67;
                    spacing: 15;
                    MainBtn {
                        id: runBtn;
                        text: "Run Script";
                        anchors.horizontalCenter: parent.horizontalCenter;
                        width: step.width * 0.444;
                        height: 50;
                        // qmllint disable unqualified
                        onTask: { runBtn.currentJobId = backend.execute("task_a", ["run script"]); }
                        onAfter: { scriptPanel.process++; }
                        once: true;
                    }
                    Label {
                        text: "Status: Idle";
                        anchors.horizontalCenter: parent.horizontalCenter;  
                        font.family: scriptPanel.family;
                        font.pixelSize: 16;
                    }
                    MainBtn {
                        id: stopBtn;
                        anchors.horizontalCenter: parent.horizontalCenter;
                        text: "Stop Script";
                        width: step.width * 0.444;
                        height: 50;
                        // qmllint disable unqualified
                        onTask: { stopBtn.currentJobId = backend.execute("task_a", ["stop script"]); }
                        onAfter: { scriptPanel.process++; }
                        once: true;
                    }
                    Label {
                        text: "Progress: 0%";
                        anchors.horizontalCenter: parent.horizontalCenter;
                        font.family: scriptPanel.family;
                        font.pixelSize: 16;
                    }
                    MainBtn {   
                        id: clearBtn;
                        text: "Clear Output";
                        anchors.horizontalCenter: parent.horizontalCenter;
                        width: step.width * 0.444;
                        height: 50;  
                        // qmllint disable unqualified
                        onTask: { clearBtn.currentJobId = backend.execute("task_a", ["clear output"]); }
                        onAfter: { scriptPanel.process++; }
                        once: true;    
                    }
                }
            }  
        }

        Column {
            id: config;
            width: parent.width;
            height: parent.height;
            spacing: 20;

            onVisibleChanged: {
                config.opacity = 1 - config.opacity; // 重置进度
            }
            Behavior on opacity { NumberAnimation { duration: 500; easing.type: Easing.InOutQuad } }

            Item {
                width: parent.width;
                height: 30;
                
                Text {
                    id: title;
                    anchors.centerIn: parent;
                    font.family: scriptPanel.family;    
                    text: "Script Settings";
                    font.pixelSize: 24;
                    font.bold: true;
                    visible: false;
                }

                Rectangle {
                    id: gradientRect;
                    anchors.fill: parent;
                    gradient: Gradient {
                        orientation: Gradient.Horizontal;
                        GradientStop { position: 0.0; color: "#60EFDB"; }
                        GradientStop { position: 0.25; color: "#BEF2E5"; }
                        GradientStop { position: 0.5; color: "#C5E7F1"; }
                        GradientStop { position: 0.75; color: "#79CEED"; }
                        GradientStop { position: 1.0; color: "#6F89A2"; }
                    }
                    visible: false;
                }
                
                OpacityMask {
                    anchors.fill: title;
                    source: gradientRect;
                    maskSource: title;
                }
            }

            OptionBox {
                id: opt1;
                width: parent.width;
                key: "Log";
                value: "Yes";
                crypt: false;
            } 
        }
    }

      
}