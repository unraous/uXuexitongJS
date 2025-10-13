import QtQuick
import QtQuick.Controls.Basic
import Qt5Compat.GraphicalEffects


import "button"
import "box"
import "mask"
import "theme_manager"
import "interface.js" as Interface

Rectangle {
    id: script;
    width: 450;
    height: 450;
    color: "transparent";
    property string family;
    property int process: 0; // 添加进度属性
    property bool settingOpen: false;

    

    Item {

        id: settingCont;
        x: script.settingOpen ? 50 : parent.width - width - 60
        y: 40
        width: setting.width; height: setting.height;
        property bool hovered: false;
        property bool pressed: false;
        Behavior on x { NumberAnimation { duration: 500; easing.type: Easing.InOutCubic; } }
        transform: Rotation {
            origin.x: setting.width / 2
            origin.y: setting.height / 2
            angle: settingCont.hovered ? 240 : 0;   // 这里设置旋转角度
            Behavior on angle { NumberAnimation { duration: 1000; easing.type: Easing.OutBounce; } }
        }
        
        Image {
            id: setting;
            source: "../resources/svg/setting.svg";
            width: 50;
            height: 48;
            scale: settingCont.pressed ? 0.9 : (settingCont.hovered ? 1.1 : 1.0);

            Behavior on scale { SpringAnimation { spring: 3; damping: 0.3; duration: 150; } }
        }


        Rectangle {
            id: g1;
            scale: settingCont.pressed ? 0.9 : (settingCont.hovered ? 1.1 : 1.0);
            anchors.fill: parent;
            gradient: MainMask { orientation: Gradient.Horizontal; }
            visible: false;

            Behavior on scale { SpringAnimation { spring: 3; damping: 0.3; duration: 150; } }
        }
        
        OpacityMask {
            anchors.fill: setting;
            source: g1;
            maskSource: setting;
            scale: settingCont.pressed ? 0.9 : (settingCont.hovered ? 1.1 : 1.0);

            Behavior on scale { SpringAnimation { spring: 3; damping: 0.3; duration: 150; } }
        }

        MouseArea {
            anchors.fill: parent;
            cursorShape: Qt.PointingHandCursor;
            hoverEnabled: true
            onHoveredChanged: {
                settingCont.hovered = !settingCont.hovered;
            }
            onClicked: {
                script.settingOpen = !script.settingOpen;
            }
            onPressed: {
                settingCont.pressed = true;
            }
            onReleased: {
                settingCont.pressed = false;
            }
        }
    }

    Row {

        anchors.fill: parent;
        width: parent.width;
        height: parent.height;
        anchors.topMargin: 80;
        anchors.bottomMargin: 80;
      
        Column {  //主控部分
            id: step;
            width: script.settingOpen ? 0 : parent.width;
            opacity: script.settingOpen ? 0 : 1;
            height: parent.height;
            spacing: 25;

            Behavior on width { NumberAnimation { duration: 500; easing.type: Easing.InOutCubic; } }
            Behavior on opacity { NumberAnimation { duration: 500; easing.type: Easing.InOutBack; } }

            Item {
                width: parent.width;
                height: 30;
                
                Text {
                    id: titleText;
                    anchors.centerIn: parent;
                    font.family: script.family;
                    height: parent.height;    
                    text: "Script Panel";
                    font.pixelSize: 24;
                    font.bold: true;
                    visible: false;
                }

                Rectangle {
                    id: g2;
                    anchors.fill: parent;
                    gradient: MainMask { orientation: Gradient.Horizontal; }
                    visible: false;
                }
                
                OpacityMask {
                    anchors.fill: titleText;
                    source: g2;
                    maskSource: titleText;
                }
            }

            Row {

                leftPadding: step.width * 0.149;

                Rectangle {
                    width: 8;
                    height: {
                        switch (script.process) {
                            case 0: 1; break;
                            case 1: 255 * 0.33; break;
                            case 2: 255 * 0.67; break;
                            case 3: 255; break;
                            default: 255;
                        }
                    }
                    opacity: script.process === 0 ? 0 : 1;
                    gradient: MainMask { orientation: Gradient.Vertical; }
                    radius: width / 2;

                    Behavior on height { NumberAnimation { duration: 300; easing.type: Easing.InOutQuad; } }
                }

                Column {

                    width: step.width * 0.67;
                    spacing: 15;

                    MainButton {
                        id: btn1;
                        text: "启动浏览器";
                        anchors.horizontalCenter: parent.horizontalCenter;
                        width: step.width * 0.444;
                        height: 50;
                        onTask: { btn1.currentJobId = Interface.dispatch("launch_driver", []); }
                        onAfter: { script.process++; }
                        once: true;
                    }

                    Label {
                        text: "登录并切换到课程页面";
                        color: Theme.color[3];
                        anchors.horizontalCenter: parent.horizontalCenter;  
                        font.family: script.family;
                        font.pixelSize: 16;
                    }

                    MainButton {
                        id: btn2;
                        anchors.horizontalCenter: parent.horizontalCenter;
                        text: "注入脚本";
                        width: step.width * 0.444;
                        height: 50;
                        onTask: { btn2.currentJobId = Interface.dispatch("launch_script", []); }
                        onAfter: { script.process++; }
                        once: true;
                    }
                    Label {
                        text: "按弹窗提示操作";
                        color: Theme.color[3];
                        anchors.horizontalCenter: parent.horizontalCenter;
                        font.family: script.family;
                        font.pixelSize: 16;
                    }
                    MainButton {
                        id: btn3;
                        text: "开启鼠标模拟";
                        anchors.horizontalCenter: parent.horizontalCenter;
                        width: step.width * 0.444;
                        height: 50;  
                        onTask: { btn3.currentJobId = Interface.dispatch("pretend_active", []); }
                        onAfter: { script.process++; }
                        once: true;    
                    }
                }
            }  
        }

        Column {  //设置部分

            id: config;
            width: parent.width;
            height: parent.height;
            spacing: 20;

            opacity: script.settingOpen ? 1 : 0;
            Behavior on opacity { NumberAnimation { duration: 500; easing.type: Easing.InOutBack; } }

            Item {
                width: parent.width;
                height: 30;
                
                Text {
                    id: title;
                    anchors.centerIn: parent;
                    height: parent.height;   
                    font.family: script.family;    
                    text: "Script Settings";
                    font.pixelSize: 24;
                    font.bold: true;
                    visible: false;
                }

                Rectangle {
                    id: gradientRect;
                    anchors.fill: parent;
                    gradient: Gradient {
                        orientation: Gradient.Horizontal;
                        GradientStop { position: 0.0; color: Theme.color[0]; }
                        GradientStop { position: 0.25; color: Theme.color[1]; }
                        GradientStop { position: 0.5; color: Theme.color[2]; }
                        GradientStop { position: 0.75; color: Theme.color[3]; }
                        GradientStop { position: 1.0; color: Theme.color[4]; }
                    }
                    visible: false;
                }
                
                OpacityMask {
                    anchors.fill: title;
                    source: gradientRect;
                    maskSource: title;
                }
            }

            ScrollView {

                width: parent.width * 0.6;
                height: parent.height - 100;
                anchors.horizontalCenter: parent.horizontalCenter;
                clip: true;
                Column {
                    width: parent.width;
                    height: parent.height;
                    spacing: 20;
                    OptionBox {
                        id: log;
                        width: parent.width;
                        option: "Keep Login";
                        jobId: Interface.dispatch("get_config", ["auto_course", "restore_cookies"]);
                        Component.onCompleted: {
                            const chosen_text = Interface.getResult(jobId);
                            log.chosen = (chosen_text === "True") ? true : false;
                        }
                    }

                    OptionBox {
                        id: speed;
                        width: parent.width;
                        expand: true;
                        option: "Force Speed";
                        key: "Speed";
                        jobId: Interface.dispatch("get_config", ["auto_course", "force_speed"]);
                        jobId2: Interface.dispatch("get_config", ["auto_course", "speed"]);
                        Component.onCompleted: {
                            const chosen_text = Interface.getResult(jobId);
                            speed.chosen = (chosen_text === "True") ? true : false;
                            speed.value = Interface.getResult(jobId2);

                        }
                    }
                }
            }


            MainButton {
                id: saveBtn;
                text: "SAVE";
                tip: true;
                pixelSize: 20;
                width: parent.width * 0.5;
                height: 50;
                anchors.horizontalCenter: parent.horizontalCenter;
                onTask: {
                    Interface.dispatch("set_config", [["auto_course", "restore_cookies"], log.chosen]);
                    Interface.dispatch("set_config", [["auto_course", "force_speed"], speed.chosen]);
                    Interface.dispatch("set_config", [["auto_course", "speed"], Number(speed.value)]);
                    Interface.dispatch("refresh_settings", []);
                    saveBtn.currentJobId = Interface.dispatch("commit_config", []);
                } 
            }
        }
    }

      
}