import QtQuick
import QtQuick.Controls

import "button"
import "theme_manager"

ScrollView {
    id: view
    clip: true
    background: Rectangle {
        color: "transparent"
    }

    function init() {
        console.log("初始化主题页面");
        col.children.forEach(function(child) {
            if (child?.text) {
                child.color = Theme.getColor(child.text);
            }
        });
    }

    property int innerPadding: 20;

    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
    ScrollBar.vertical.policy: ScrollBar.AlwaysOff

    Column {
        id: col;
        width: view.width;
        topPadding: view.innerPadding;

        Repeater {
            model: [
                "aoguchi", "ink", "gummy", "prussian",
                "regal", "rosmarinus", "silence",
                "vandyke", "vira"
            ]
            ThemeButton {
                required property string modelData;
                text: modelData;
                width: parent.width;
                height: 120;
            }
        }
    }
}
