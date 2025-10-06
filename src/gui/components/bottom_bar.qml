// 底部栏
import QtQuick
import Qt5Compat.GraphicalEffects

import "mask"
import "interface.js" as Interface

Rectangle {
    id: bottomBar;
    width: 450;
    height: 90;
    color: "transparent";
    property string family;

    

    Item {
        id: titleContainer;
        anchors.centerIn: parent;
        width: timeText.width;
        height: timeText.height;

        Text {
            id: timeText;
            text: Qt.formatTime(new Date(), "hh:mm:ss");
            font.family: bottomBar.family;
            font.pixelSize: 56;
            visible: false;
            bottomPadding: 30;

            // 用于对齐到整秒
            Timer {
                id: alignTimer;
                interval: {
                    let now = new Date();
                    return 1000 - now.getMilliseconds();
                }
                running: true;
                repeat: false;
                onTriggered: {
                    timeText.text = Qt.formatTime(new Date(), "hh:mm:ss");
                    syncTimer.start();
                }
            }

            // 每秒刷新
            Timer {
                id: syncTimer;
                interval: 1000;
                running: false;
                repeat: true;
                onTriggered: {
                    timeText.text = Qt.formatTime(new Date(), "hh:mm:ss");
                }
            }
        }
        
        Rectangle {
            id: gradientRect;
            anchors.fill: parent;
            gradient: MainMask { orientation: Gradient.Horizontal; }
            visible: false;
        }
        
        OpacityMask {
            anchors.fill: timeText;
            source: gradientRect;
            maskSource: timeText;
        }
    }

    Row {
        id: rowLayout;
        anchors.right: parent.right;
        anchors.verticalCenter: parent.verticalCenter;
        spacing: 12;
        rightPadding: 48;
        property int w: 32;

            // 统一渐变
        Rectangle {
            id: rowGradient;
            width: 180; // 足够覆盖图标和文字
            height: 48;
            visible: false;
            gradient: MainMask { orientation: Gradient.Horizontal; }
        }

        Item {
            width: rowLayout.w;
            height: rowLayout.w;

            OpacityMask {
                id: githubMask;
                anchors.fill: parent;
                source: rowGradient;
                maskSource: Image {
                    source: "../resources/svg/github.svg";
                    fillMode: Image.PreserveAspectFit;
                }
            }

            MouseArea {
                anchors.fill: parent;
                cursorShape: Qt.PointingHandCursor;
                onClicked: Qt.openUrlExternally("https://github.com/unraous/uXuexitongJS");
            }
        }

        OpacityMask {
            id: textMask;
            width: text.width; height: text.height;
            source: rowGradient;
            property int jobId: Interface.dispatch("get_config", ["metadata", "version"]);
            maskSource: Text {
                id: text;
                text: "v0.0.0 by unraous";
                font.family: bottomBar.family;
                height: rowLayout.w;
                font.pixelSize: 14;
                color: "white";
                verticalAlignment: Text.AlignVCenter;
                horizontalAlignment: Text.AlignHCenter;

            }

        }
    }
    
    Component.onCompleted: {
        text.text = `v${Interface.getResult(textMask.jobId)} by unraous`;
    }        
}