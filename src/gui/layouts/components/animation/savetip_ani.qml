import QtQuick

import "../theme_manager"

Item {
    id: saveTip;
    x: parent.width / 2 - width / 2;
    y: parent.height / 2 - height / 2; 
    width: parent.width * 0.5;
    height: parent.height * 0.5;
    visible: tipAnim.running;

    property real pWidth: parent.width;
    property real pHeight: parent.height;
    property string fontFamily;
    property alias tipAnim: tipAnim;

    
    Text {
        anchors.centerIn: parent;
        text: "succeed!";
        color: Theme.color[0];
        font.family: saveTip.fontFamily;
        font.pixelSize: 15;
        font.bold: true;
    }

    // 动画
    SequentialAnimation {
        id: tipAnim;
        running: false;
        ParallelAnimation {
            PropertyAnimation {
                target: saveTip;
                property: "y";
                from: saveTip.pHeight / 2 - saveTip.height / 2;
                to: saveTip.pHeight / 2 - saveTip.height / 2 - 50;
                duration: 400;
                easing.type: Easing.OutSine;
            }
            PropertyAnimation {
                target: saveTip;
                property: "opacity";
                from: 0;
                to: 1;
                duration: 200;
            }
        }
        ParallelAnimation {
            PropertyAnimation {
                target: saveTip;
                property: "y";
                from: saveTip.pHeight / 2 - saveTip.height / 2 - 50;
                to: saveTip.pHeight / 2 - saveTip.height / 2 - 60;
                duration: 150;
            }
            PropertyAnimation {
                target: saveTip;
                property: "opacity";
                from: 1;
                to: 0;
                duration: 150;
            }
        }
    }
    
}