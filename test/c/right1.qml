import QtQuick
import QtQuick.Controls

import "../test.js" as Test


ScrollView {
    id: scrollView
    clip: true
    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
    ScrollBar.vertical.policy: ScrollBar.AlwaysOff
    background: Rectangle {
        color: "transparent"
    }
    TextEdit {
        id: markdownText
        width: scrollView.width - scrollView.padding * 2
        textFormat: TextEdit.MarkdownText
        wrapMode: TextEdit.Wrap
        readOnly: true
        font.family: scrollView.font.family
        font.pixelSize: 16

        property bool isHoveringLink: false

        onLinkActivated: function(link) {
            console.log("点击了链接:", link)
            Qt.openUrlExternally(link)
        }

        onLinkHovered: function(link) {
            isHoveringLink = link !== ""
        }

        MouseArea {
            anchors.fill: markdownText
            acceptedButtons: Qt.NoButton
            cursorShape: markdownText.isHoveringLink ? Qt.PointingHandCursor : Qt.IBeamCursor
        }

        Component.onCompleted: {
            Test.readFile('../src/gui/resources/docs/tutorial.md').then((content) => {
                text = content;
            }).catch((err) => {
                console.error('读取失败:', err);
            });
        }
    }
}