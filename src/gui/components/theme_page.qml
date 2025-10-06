import QtQuick
import QtQuick.Controls

import "button"
import "theme_manager"

ScrollView {
    id: scrollView
    clip: true
    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
    ScrollBar.vertical.policy: ScrollBar.AlwaysOff
    property int innerPadding: 20;
    background: Rectangle {
        color: "transparent"
    }
    Column {
        width: scrollView.width
        topPadding: scrollView.innerPadding;
        ThemeButton {
            text: "ocean"
            width: scrollView.width
            height: 120
            color: Theme.getColor(text);
        }
        ThemeButton {
            text: "ink"
            width: scrollView.width
            height: 120
            color: Theme.getColor(text);
        }
        ThemeButton {
            text: "silence"
            width: scrollView.width
            height: 120
            color: Theme.getColor(text);
        }
        ThemeButton {
            text: "vira"
            width: scrollView.width
            height: 120
            color: Theme.getColor(text);
        }
    }
}
