import QtQuick
import QtQuick.Controls.Basic
import Qt5Compat.GraphicalEffects

import "button"

Rectangle {
    id: scriptPanel;
    width: 450;
    height: 450;
    color: "transparent";
    property string family;
    property int process: 0; // 添加进度属性

    Image {
        id: setting
        source: "file:///" + "D:/Workspace/uXuexitongJS/data/static/svg/setting.svg"
        width: 48;
        height: 48;
        anchors.right: parent.right;
        anchors.top: parent.top;
        anchors.margins: 60;
        fillMode: Image.PreserveAspectCrop;
    }

    Column {
        anchors.fill: parent;
        anchors.topMargin: 80;
        anchors.bottomMargin: 80;
        spacing: 20;

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
                id: gradientRect;
                anchors.fill: parent;
                gradient: Gradient {
                    orientation: Gradient.Horizontal;
                    GradientStop { position: 0.0; color: "#60EFDB"; }   // 青绿色
                    GradientStop { position: 0.25; color: "#BEF2E5"; }  // 浅青绿色
                    GradientStop { position: 0.5; color: "#C5E7F1"; }   // 浅蓝色
                    GradientStop { position: 0.75; color: "#79CEED"; }  // 天蓝色
                    GradientStop { position: 1.0; color: "#6F89A2"; }   // 蓝灰色
                }
                visible: false;
            }
            
            OpacityMask {
                anchors.fill: titleText;
                source: gradientRect;
                maskSource: titleText;
            }
        }

        Row {
            leftPadding: 67;
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
                width: 300;
                spacing: 15;
                MainBtn {
                    id: runBtn;
                    text: "Run Script";
                    anchors.horizontalCenter: parent.horizontalCenter;
                    width: 200;
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
                    width: 200;
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
                    width: 200;
                    height: 50;  
                    // qmllint disable unqualified
                    onTask: { clearBtn.currentJobId = backend.execute("task_a", ["clear output"]); }
                    onAfter: { scriptPanel.process++; }
                    once: true;    
                }
            }
        }  
    }

      
}