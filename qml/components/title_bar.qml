// 顶部栏
import QtQuick
import Qt5Compat.GraphicalEffects

import "button"

Rectangle {
    id: titleBar;
    width: Math.max(30, parent.width);
    height: 60;
    color: "transparent";

    property var window;
    property string family;



    Item {
        id: titleContainer;
        anchors.centerIn: parent;
        width: titleText.width;
        height: titleText.height;
        
        Text {
            id: titleText;
            text: "uXuexitongScript";
            font.family: titleBar.family;
            font.pixelSize: 26;
            font.bold: true;
            topPadding: 10;
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

    function animatedClose() {
        closeAnimation.start()
    }
    
    function animatedMinimize() {
        minimizeAnimation.start()
    }
    
    // 关闭动画
    SequentialAnimation {
        id: closeAnimation
        property int time: 350
        
        ParallelAnimation {
            NumberAnimation { 
                target: titleBar.window
                property: "width"
                to: 0
                duration: closeAnimation.time
                easing.type: Easing.InQuad
            }
            NumberAnimation { 
                target: titleBar.window
                property: "height"
                to: 0
                duration: closeAnimation.time
                easing.type: Easing.InQuad
            }
            NumberAnimation { 
                target: titleBar.window
                property: "x"
                to: titleBar.window.x + titleBar.window.width / 2
                duration: closeAnimation.time
                easing.type: Easing.InQuad
            }
            NumberAnimation { 
                target: titleBar.window
                property: "y"
                to: titleBar.window.y + titleBar.window.height / 2
                duration: closeAnimation.time
                easing.type: Easing.InQuad
            }
            NumberAnimation { 
                target: titleBar.window
                property: "opacity"
                to: 0
                duration: closeAnimation.time
                easing.type: Easing.InQuad
            }
        }
        
        ScriptAction {
            script: titleBar.window.close()
        }
    }
    
    // 最小化动画
    SequentialAnimation {
        id: minimizeAnimation
        
        ParallelAnimation {
            NumberAnimation { 
                target: titleBar.window
                property: "opacity"
                to: 0
                duration: 250
                easing.type: Easing.InQuad
            }
        }
        
        ScriptAction {
            script: {
                titleBar.window.showMinimized();
                titleBar.window.opacity = 1;
            }
        }
    }

    Row {
        anchors.right: parent.right;
        anchors.verticalCenter: parent.verticalCenter;
        rightPadding: 24;

        TitleBtn {
            btnText: "-";
            onClicked: titleBar.animatedMinimize();
        }
        
        TitleBtn {
            btnText: "×";
            onClicked: titleBar.animatedClose();
        }

    }
        
}