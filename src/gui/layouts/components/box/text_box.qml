import QtQuick
import QtQuick.Controls.Basic

import "../theme_manager"

Rectangle {
    id: tbx;
    width: 400;
    height: 50;
    color: "transparent";

    property string key: "TestKey";
    property string value: tbx.num ? "0": "TestValue";
    property bool crypt: false;
    property bool num: false;
    property int jobId: -1;
    property real paddingcoe: 0.05;
    property real kpc: 0.3;
    property real vpc: 0.5;
    property real spc: 0.1;
    // border.color: "#8a1d73"

    Row {
        anchors.fill: parent;
        spacing: parent.width * tbx.spc;
        leftPadding: tbx.width * tbx.paddingcoe;
        rightPadding: tbx.width * tbx.paddingcoe;

        Label {
            text: tbx.key;
            color: Theme.color[3];
            height: parent.height;
            width: parent.width * tbx.kpc;
            font.pixelSize: 20;
            font.bold: true;
            verticalAlignment: Text.AlignVCenter;
            horizontalAlignment: Text.AlignHCenter;
            // background: Rectangle { border.color: "#5f18d9"; }
            
        }

        TextField {
            id: inputField;
            autoScroll: activeFocus;
            hoverEnabled: true;
            validator: tbx.num ? inputField.dVali : null;
            text: tbx.value;
            
            property DoubleValidator dVali: DoubleValidator {
                bottom: 0.0
                top: 20.0
                decimals: 1
                notation: DoubleValidator.StandardNotation
            }

            color: inputField.hovered ? Theme.color[2] : Theme.color[4];
            Behavior on color {
                ColorAnimation {
                    duration: 200;
                }
            }

            echoMode: {
                if (tbx.crypt) inputField.hovered ? TextInput.Normal : TextInput.Password;
                else TextInput.Normal;
            }

            // 当 echoMode 变化时，触发动画
            onEchoModeChanged: {
                // 先快速淡出
                opacity = 0;
                // 然后再平滑淡入
                fadeInAnimation.start();
            }

            onActiveFocusChanged: {
                if (!activeFocus) {
                    // 失去焦点时，强制显示文本左侧
                    cursorPosition = 0
                }
            }

            // 淡入动画
            NumberAnimation {
                id: fadeInAnimation;
                target: inputField;
                property: "opacity";
                to: 1;
                duration: 200;
            }

            height: parent.height;
            width: parent.width * tbx.vpc;
            font.pixelSize: 18;

            background: Rectangle {
                color: "transparent";
                // border.color: "#18d92b";
            }
            
            onTextChanged: tbx.value = text;

            verticalAlignment: Text.AlignVCenter;
            horizontalAlignment: tbx.num ? Text.AlignHCenter :Text.AlignLeft;
        }
    }
    
}