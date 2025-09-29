import QtQuick
import QtQuick.Controls.Basic

import "."

Rectangle {
    id: tbx;
    width: 400;
    height: 50;
    anchors.horizontalCenter: parent.horizontalCenter;
    color: "transparent";

    property string key: "TestKey";
    property string value: "TestValue";
    property bool crypt: false;

    Row {
        anchors.fill: parent;
        width: parent.width;
        height: parent.height;
        Label {
            text: tbx.key;
            color: "#79CEED";
            height: parent.height;
            width: parent.width * 0.3;
            font.pixelSize: 20;
            font.bold: true;
            verticalAlignment: Text.AlignVCenter;
            horizontalAlignment: Text.AlignHCenter;
            background: Rectangle {
                border.color: "#79CEED";
                color: "transparent";
            }
        }

        Rectangle {
            width: parent.width * 0.5;
            height: parent.height;
            border.color: "#79CEED";
            color: "transparent";
            Rectangle {
                anchors.centerIn: parent;
                width: height; height: parent.height * 0.5;
                radius: width / 2;
                border.color: "#79CEED";
                color: "transparent";
            }


            Rectangle {
                anchors.centerIn: parent;
                width: height; height: parent.height * 0.3;
                radius: width / 2;
                color: "#79CEED";
                
            }
        }
        
    }
    
}