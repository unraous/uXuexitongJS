import QtQuick

import "components"
import "components/theme_manager"

Column {
    id: mainLayout;
    anchors.fill: parent;
    width: parent.width;
    height: parent.height;
    spacing: 0;

    required property var window;

    TitleBar {
        id: titleBar;
        window: mainLayout.window;
        family: mainLayout.window.font.family;
        width: parent.width;
        height: 60;
        onExpandChanged: {
            if (!menuRow?.loaded) {
                console.log("初始化菜单页面");
                menuRow.loaded = true;
            }
        }
    }

    Row {
        id: menuRow;
        width: parent.width;
        height: titleBar.expand ? mainLayout.window.height - titleBar.height : 0;
        clip: true;
        opacity: titleBar.expand ? 1 : 0;
        property int chosenIndex: 0;
        property bool loaded: false;

        onLoadedChanged: {
            themePage.init();
        }            

        Behavior on opacity { NumberAnimation { duration: 500; easing.type: Easing.InOutQuad; } }
        Behavior on height { NumberAnimation { duration: 500; easing.type: Easing.InOutCubic; } }
        MenuList {
            id: menuList;
            width: menuRow.width * 0.3;
            height: mainLayout.window.height - titleBar.height;
            parentPanel: menuRow;
            padding: 80;
        }
        Item {
            id: rightPanel;
            width: parent.width * 0.7;
            height: mainLayout.window.height - titleBar.height;
            
            Rectangle {
                anchors.fill: parent;
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "transparent"; }
                    GradientStop { position: 0.1; color: Theme.color[2]; }
                    GradientStop { position: 0.9; color: Theme.color[2]; }
                    GradientStop { position: 1.0; color: "transparent"; }
                }
                opacity: 0.05;
                z: -1;  // 放在底层
            }

            Column {
                id : col;
                anchors.fill: parent
                padding: 40
                ThemePage {
                    id: themePage;
                    width: col.width - col.padding * 2;
                    height: menuRow.chosenIndex === 1 ? col.height - col.padding * 2 : 0;
                    Behavior on height { NumberAnimation { duration: 250; easing.type: Easing.InOutQuad; } }
                }
                TutorialPage {
                    font: Theme.font;
                    width: col.width - col.padding * 2;
                    height: menuRow.chosenIndex === 0 ? col.height - col.padding * 2 : 0;
                    Behavior on height { NumberAnimation { duration: 250; easing.type: Easing.InOutQuad; } }
                }
                
            }
        }
    }

    Row {
        width: parent.width;
        height: mainLayout.window.height * 0.75;
        ConfigPanel {
            id: configPanel;
            width: mainLayout.window.width / 2 ; height: parent.height;
            family: mainLayout.window.font.family;
        }
        ScriptPanel {
            id: scriptPanel;
            width: mainLayout.window.width / 2 ; height: parent.height;
            family: mainLayout.window.font.family;
        }
    }

    BottomBar {
        family: mainLayout.window.font.family;
        width: parent.width;
        height: 90;
    }
    
}