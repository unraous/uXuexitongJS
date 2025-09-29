import QtQuick
import QtQuick.Controls.Basic

Rectangle {
    id: tbx;
    width: 400;
    height: 50;
    color: "transparent";

    property string key: "TestKey";
    property string value: "TestValue";
    property bool crypt: false;

    Row {
        anchors.fill: parent;
        spacing: parent.width * 0.1;
        leftPadding: parent.width * 0.05;
        rightPadding: parent.width * 0.05;

        Label {
            text: tbx.key;
            color: "#79CEED";
            height: parent.height;
            width: parent.width * 0.3;
            font.pixelSize: 20;
            font.bold: true;
            verticalAlignment: Text.AlignVCenter;
            horizontalAlignment: Text.AlignHCenter;
        }

        TextField {
            id: inputField;
            hoverEnabled: true;
            
            text: tbx.value;

            color: inputField.hovered ? "#C5E7F1" : "#6F89A2";

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

            // 淡入动画
            NumberAnimation {
                id: fadeInAnimation;
                target: inputField;
                property: "opacity";
                to: 1;
                duration: 200;
            }

            height: parent.height;
            width: parent.width * 0.5;
            font.pixelSize: 18;
            background: Rectangle { color: "transparent"; }
            
            onTextChanged: tbx.value = text;

            verticalAlignment: Text.AlignVCenter;
            horizontalAlignment: Text.AlignHCenter;
        }
    }
    
}