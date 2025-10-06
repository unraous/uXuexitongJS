import QtQuick
import Qt5Compat.GraphicalEffects

import "button"
import "box"
import "mask"
import "interface.js" as Interface

Rectangle {
    id: configPanel;
    width: 450;
    height: 450;
    color: "transparent";
    property string family;
    // border.color: "#79CEED";
    Column {
        anchors.fill: parent;
        anchors.topMargin: 80;
        anchors.bottomMargin: 80;
        spacing: 20;

        Item {
            width: parent.width;
            height: 30;
            
            Text {
                id: titleText;
                anchors.centerIn: parent;
                font.family: configPanel.family;   
                height: parent.height; 
                text: "API Configuration";
                font.pixelSize: 24;
                font.bold: true;
                visible: false;
            }
            
            Rectangle {
                id: gradientRect;
                anchors.fill: parent;
                gradient: MainMask { orientation: Gradient.Horizontal; }
                visible: false;
            }
            
            OpacityMask {
                anchors.fill: titleText;
                source: gradientRect;
                maskSource: titleText;
            }
        }

        TextBox {
            id: apiKeyBox;
            anchors.horizontalCenter: parent.horizontalCenter;
            width: parent.width - 100;
            key: "API KEY";
            jobId: Interface.dispatch("get_config", ["openai", "api_key"]);
            crypt: true;
            Component.onCompleted: { value = String(Interface.getResult(jobId)); }
        }

        TextBox {
            id: baseUrlBox;
            anchors.horizontalCenter: parent.horizontalCenter;
            width: parent.width - 100;
            key: "BASE URL";
            jobId: Interface.dispatch("get_config", ["openai", "base_url"]);
            Component.onCompleted: { value = String(Interface.getResult(jobId)); }
        }

        TextBox {
            id: modelBox;
            anchors.horizontalCenter: parent.horizontalCenter;
            width: parent.width - 100;
            key: "MODEL";
            jobId: Interface.dispatch("get_config", ["openai", "model"]);
            crypt: false;
            Component.onCompleted: { value = String(Interface.getResult(jobId)); }
        }

        MainButton {
            id: saveBtn;
            text: "SAVE";
            tip: true;
            pixelSize: 20;
            width: parent.width * 0.6;
            height: 50;
            anchors.horizontalCenter: parent.horizontalCenter;
            onTask: {
                Interface.dispatch("set_config", [["openai", "api_key"], apiKeyBox.value]);
                Interface.dispatch("set_config", [["openai", "base_url"], baseUrlBox.value]);
                Interface.dispatch("set_config", [["openai", "model"], modelBox.value]);
                saveBtn.currentJobId = Interface.dispatch("commit_config", []);
            }
        }
    }
}