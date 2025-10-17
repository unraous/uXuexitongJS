// 底部栏
import QtQuick
import Qt5Compat.GraphicalEffects

import "mask"
import "bridge.js" as BackendBridge

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
            font.pixelSize: 64;
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
        rightPadding: 60;
        bottomPadding: 12;
        property int contentWidth: 32;

            // 统一渐变
        Rectangle {
            id: rowGradient;
            width: 180; // 足够覆盖图标和文字
            height: 48;
            visible: false;
            gradient: MainMask { orientation: Gradient.Horizontal; }
        }

        Item {
            id: githubIcon;
            width: rowLayout.contentWidth;
            height: rowLayout.contentWidth;
            scale: githubIcon.hovered ? 1.3 : 1.0;

            property bool hovered: false;
            property real rotationAngle: 0;

            Behavior on scale { SpringAnimation { spring: 3; damping: 0.3; duration: 200; } }

            transform: Rotation {
                origin.x: githubIcon.width / 2
                origin.y: githubIcon.height / 2
                angle: githubIcon.rotationAngle
            }

            SequentialAnimation {
                id: swingAnim
                running: false
                NumberAnimation { target: githubIcon; property: "rotationAngle"; to: -6; duration: 200; easing.type: Easing.InOutQuad }
                NumberAnimation { target: githubIcon; property: "rotationAngle"; to: 6;  duration: 200; easing.type: Easing.InOutQuad }
                NumberAnimation { target: githubIcon; property: "rotationAngle"; to: 0;  duration: 200; easing.type: Easing.InOutQuad }
            }

            // 取消悬停时平滑回到 0 的动画（用于中断 swingAnim 后的平滑收尾）
            NumberAnimation {
                id: returnAnim
                target: githubIcon
                property: "rotationAngle"
                to: 0
                duration: 150
                easing.type: Easing.InOutQuad
            }

            OpacityMask {
                id: githubMask;
                anchors.fill: parent;
                source: rowGradient;
                maskSource: Image {
                    source: "../../resources/svg/github.svg";
                    fillMode: Image.PreserveAspectFit;
                }
            }

            MouseArea {
                anchors.fill: parent;
                cursorShape: Qt.PointingHandCursor;
                onClicked: Qt.openUrlExternally("https://github.com/unraous/uXuexitongJS");
                hoverEnabled: true;
                onHoveredChanged: {
                    githubIcon.hovered = !githubIcon.hovered; // 使用事件提供的 hovered 状态
                    if (githubIcon.hovered) {
                        returnAnim.stop();
                        swingAnim.start();
                    } else {
                        // 停止摆动并平滑回正
                        swingAnim.stop();
                        returnAnim.start();
                    }
                }
            }
        }

        OpacityMask {
            id: textMask;
            width: text.width; height: text.height;
            source: rowGradient;
            property int jobId: BackendBridge.dispatch("get_config", ["metadata", "version"]);
            maskSource: Text {
                id: text;
                text: "v0.0.0 by unraous";
                font.family: bottomBar.family;
                height: rowLayout.contentWidth;
                font.pixelSize: 14;
                color: "white";
                verticalAlignment: Text.AlignVCenter;
                horizontalAlignment: Text.AlignHCenter;

            }

        }
    }
    
    Component.onCompleted: {
        text.text = `v${BackendBridge.getResult(textMask.jobId)} by unraous`;
    }        
}