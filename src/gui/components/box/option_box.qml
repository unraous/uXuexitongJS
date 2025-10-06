import QtQuick
import QtQuick.Controls.Basic

import "../theme_manager"
import "../mask"
import "."

Rectangle {
    id: obx;
    width: parent.width;
    height: initialHeight * (obx.expand && obx.chosen ? 2 : 1);
    color: "transparent";
    // border.color: "#b42727";

    property string option: "TestOption";
    property string key: "TestKey";
    property string value;
    property int jobId: -1;
    property int jobId2: -1;
    property real initialHeight: 50;
    property bool expand: false;
    property bool chosen: false;

    Behavior on height { NumberAnimation { duration: 300; easing.type: Easing.InOutCubic; } }
    
    Column {
        anchors.fill: parent;
        Row {
            width: obx.width;
            height: obx.initialHeight;
            Label {
                text: obx.option;
                color: Theme.color[3];
                height: parent.height;
                width: parent.width * 0.7;
                font.pixelSize: 20;
                font.bold: true;
                verticalAlignment: Text.AlignVCenter;
                horizontalAlignment: Text.AlignHCenter;
            }

            Rectangle {
                width: parent.width * 0.3;
                height: parent.height;
                color: "transparent";
                Rectangle {
                    anchors.centerIn: parent;
                    width: height; height: parent.height * 0.5;
                    radius: width / 2;
                    border.width: 2;
                    border.color: obx.chosen ? Theme.color[3] : Theme.color[4];
                    color: "transparent";

                    Behavior on border.color { ColorAnimation { duration: 200; } }
                }


                Rectangle {
                    anchors.centerIn: parent;
                    width: height; height: parent.height * 0.3;
                    radius: width / 2;
                    gradient: MainMask {
                        orientation: Gradient.Horizontal;
                    }
                    opacity: obx.chosen ? 1 : 0;

                    Behavior on opacity { NumberAnimation { duration: 200; } }

                    MouseArea {
                        anchors.fill: parent;
                        hoverEnabled: true;
                        cursorShape: Qt.PointingHandCursor;
                        onClicked: {
                            obx.chosen = !obx.chosen;
                        }
                    }
                }
            }
            
        }
        TextBox {
            id: tbx;
            width: obx.width;
            height: obx.expand && obx.chosen ? obx.initialHeight : 0;
            key: obx.key; value: obx.value;
            paddingcoe: 0;
            kpc: 0.7;
            vpc: 0.3;
            spc: 0;
            opacity: obx.chosen ? 1 : 0;
            num: true;
            onValueChanged: { obx.value = tbx.value; }
            Behavior on height { NumberAnimation { duration: 300; easing.type: Easing.InOutCubic; } }
            Behavior on opacity { NumberAnimation { duration: 300; easing.type: Easing.InOutCubic; } }
        }
    }
}