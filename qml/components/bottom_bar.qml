// 底部栏
import QtQuick
import Qt5Compat.GraphicalEffects

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
            id: timeText
            text: Qt.formatTime(new Date(), "hh:mm:ss")
            font.family: bottomBar.family
            font.pixelSize: 56
            visible: false
            bottomPadding: 30

            // 用于对齐到整秒
            Timer {
                id: alignTimer
                interval: {
                    var now = new Date()
                    return 1000 - now.getMilliseconds()
                }
                running: true
                repeat: false
                onTriggered: {
                    timeText.text = Qt.formatTime(new Date(), "hh:mm:ss")
                    syncTimer.start()
                }
            }

            // 每秒刷新
            Timer {
                id: syncTimer
                interval: 1000
                running: false
                repeat: true
                onTriggered: {
                    timeText.text = Qt.formatTime(new Date(), "hh:mm:ss")
                }
            }
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
            gradient: Gradient {
                orientation: Gradient.Horizontal;
                GradientStop { position: 0.0; color: "#60EFDB"; }
                GradientStop { position: 0.25; color: "#BEF2E5"; }
                GradientStop { position: 0.5; color: "#C5E7F1"; }
                GradientStop { position: 0.75; color: "#79CEED"; }
                GradientStop { position: 1.0; color: "#6F89A2"; }
            }
        }

        Item {
            width: rowLayout.w;
            height: rowLayout.w;

            OpacityMask {
                id: githubMask
                anchors.fill: parent
                source: rowGradient
                cached: true
                maskSource: Image {
                    source: "file:///D:\\Workspace\\uXuexitongJS\\data\\static\\svg\\github-142-svgrepo-com.svg"
                    fillMode: Image.PreserveAspectFit
                    antialiasing: true
                    smooth: true
                    mipmap: true
                }
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: Qt.openUrlExternally("https://github.com/unraous/uXuexitongJS")
            }
        }

        OpacityMask {
            width: textMask.width
            height: textMask.height
            source: rowGradient
            maskSource: Text {
                id: textMask
                text: "v1.0.0 by unraous";
                font.family: bottomBar.family;
                height: rowLayout.w;
                font.pixelSize: 14;
                color: "white";
                verticalAlignment: Text.AlignVCenter;
                horizontalAlignment: Text.AlignHCenter;
            }
        }
    }

    
        
}