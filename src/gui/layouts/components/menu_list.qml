import QtQuick

import "button"
import "theme_manager"

Rectangle {
    id: list;
    width: parent.width * 0.3;
    property var parentPanel: list.parent;
    property int padding: 0;

    color: "transparent"
    Column {
        id: bg;
        width: list.width
        spacing: 0;
        topPadding: list.padding;
        Rectangle {
            width: parent.width
            height: 80
            y: list.parentPanel.chosenIndex * 80 + list.padding
            color: Theme.color[2]
            opacity: 0.05
            Behavior on y {
                NumberAnimation { duration: 250; easing.type: Easing.OutBack; }
            }
        }
    }

    Column {
        width: list.width
        topPadding: list.padding;
        MenuButton {
            text: "Tutorial"
            width: list.width
            height: 80
            onClicked: {
                list.parentPanel.chosenIndex = 0;
            }
        }
        MenuButton {
            text: "Themes"
            width: list.width
            height: 80
            onClicked: {
                list.parentPanel.chosenIndex = 1;
            }
        }
    }
}
