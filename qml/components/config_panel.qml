import QtQuick
import Qt5Compat.GraphicalEffects

import "button"
import "box"

Rectangle {
    id: configPanel;
    width: 450;
    height: 450;
    color: "transparent";
    property string family;
    // border.color: "#79CEED";
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
                font.family: configPanel.family;    
                text: "API Configuration";
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

        TextBox {
            id: usernameBox;
            anchors.horizontalCenter: parent.horizontalCenter;
            width: parent.width - 100;
            key: "API KEY";
            value: "";
            crypt: true;
        }

        TextBox {
            id: passwordBox;
            anchors.horizontalCenter: parent.horizontalCenter;
            width: parent.width - 100;
            key: "BASE URL";
            value: "";
        }

        TextBox {
            id: schoolBox;
            anchors.horizontalCenter: parent.horizontalCenter;
            width: parent.width - 100;
            key: "MODEL";
            value: "";
            crypt: false;
        }

        MainBtn {
            id: saveBtn;
            text: "SAVE";
            pixelSize: 20;
            width: parent.width * 0.6;
            height: 50;
            anchors.horizontalCenter: parent.horizontalCenter;
            onTask: {
                // qmllint disable unqualified
                saveBtn.currentJobId = backend.execute("task_a", ["test!!"]);
            }
            
        }
    }
}