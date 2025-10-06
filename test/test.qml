import QtQuick 2.15
import QtQuick.Controls 2.15

import "test.js" as Test
import "c"

ApplicationWindow {
    visible: true
    width: 800
    height: 600

    FontLoader {
        id: fontLoader
        source: "../src/gui/resources/ttf/mixture.ttf"
    }

    font.family: fontLoader.name

    Row {
        anchors.fill: parent
        width: parent.width
        height: parent.height

        L {
            id: leftPanel
            width: parent.width * 0.3;
            height: parent.height
        }

        Item {
            id: rightPanel
            width: parent.width * 0.7
            height: parent.height
            
            Rectangle {
                anchors.fill: parent
                color: "#444444"
                opacity: 0.3
                z: -1  // 放在底层
            }

            Column {
                id : col
                anchors.fill: parent
                padding: 40
                R1 {
                    font: fontLoader
                    width: col.width - col.padding * 2
                    height: col.height - col.padding * 2
                }
            }
        }

    }
}