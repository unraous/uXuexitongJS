// 顶部栏
import QtQuick

import "button"
import "theme_manager"

Rectangle {
    id: titleBar;
    width: Math.max(30, parent.width);
    height: 60;
    color: "transparent";

    property var window;
    property string family;
    property bool expand: false;



    MenuButton {
        id: titleContainer;
        text: "uXuexitongScript";
        anchors.centerIn: parent;
        font.family: titleBar.family;
        width: titleBar.width * 0.4;
        height: titleBar.height;
        pixelSize: 28;
        light: true;
        onAfter: titleBar.expand = !titleBar.expand;
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
        property int time: 250
        
        ParallelAnimation {
            NumberAnimation { 
                target: titleBar.window
                property: "height"
                to: 0
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

        TitleButton {
            btnText: "-";
            onClicked: titleBar.animatedMinimize();
        }
        
        TitleButton {
            btnText: "×";
            bgHoverColor: Theme.color[3];
            onClicked: titleBar.animatedClose();
        }

    }
        
}