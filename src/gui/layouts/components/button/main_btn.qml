// 最主要的按钮样式
pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls.Basic

import "../animation"
import "../mask"
import "../theme_manager"

Button {
    id: btn;
    scale: btn.enabled ? (
        btn.hovered ? (btn.pressed ? 0.95 : 1.05) : 1.0
    ) : 1.0;
    property int pixelSize: 18;
    property real gradientPos: btn.finished ? 0.0 : (
        btn.hovered && !btn.loading ? (
            btn.pressed ? 0.0 : 2.5
        ) : 1.0
    );
    property bool loading: false;  // 添加加载状态属性
    property bool finished: false;
    property bool tip: false;
    property bool once: false;

    property int currentJobId: -1;

    signal task();
    signal after();

    Behavior on scale { SpringAnimation { spring: 3; damping: 0.3; duration: 150; } }

    // 使用Loader根据状态显示文本或加载动画
    contentItem: Loader {
        sourceComponent: btn.loading ? loadingComponent : textComponent;
    }

    // 文本组件
    Component {
        id: textComponent;
        Text {
            text: btn.finished ? "Completed" : btn.text;
            font.family: btn.font.family;
            font.pixelSize: btn.pixelSize;
            font.bold: true;
            horizontalAlignment: Text.AlignHCenter;
            verticalAlignment: Text.AlignVCenter;
            color: btn.finished ? Theme.color[3] : (btn.pressed ? Theme.color[2] : Theme.color[7]);
        }
    }

    // 加载动画组件
    Component {
        id: loadingComponent;
        Item {
            anchors.fill: parent;
            
            // 修正：使用正确的loading_ani组件
            LoadingAnimation {
                anchors.centerIn: parent;
                width: parent.height * 0.8;
                height: width;
                arcColor: Theme.color[6];
            }
        }
    }

    // 加载时禁用按钮交互
    enabled: !loading && !finished;

    background: Rectangle {
        radius: btn.height / 2;
        gradient: ButtonMask {
            orientation: Gradient.Horizontal
            btn: btn;
        }
    }

    // 保持原有函数
    function calPos(base: real, offset: real): real {
        return (base * offset > 0.75) ? 0.75 : (base * offset);
    }

    Behavior on gradientPos { NumberAnimation { duration: 150; easing.type: Easing.InOutQuad; } }

    // 保持原有动画组件
    SaveTipAnimation {
        id: saveTip;
        fontFamily: btn.font.family;
    }

    onClicked: {
        loading = true;
        btn.task();
        // 结束的状态处理位于main.qml
    }

    function completed() {  // 结束状态调用位于main.qml
        loading = false;
        if (tip) {
            saveTip.tipAnim.restart();
        }
        if (once) {
            finished = true;
        }
    }

    Connections {
        
        target: backend  // qmllint disable unqualified

        // 3. 监听 task_finished 信号
        function onFinished(finishedJobId) {
            // 4. 检查完成的票据是否是自己的
            if (btn.currentJobId === finishedJobId) {
                console.log("按钮 " + btn.text + " 确认任务 " + finishedJobId + " 已完成！");  
                btn.loading = false;
                if (btn.tip) {
                    saveTip.tipAnim.restart();
                }
                if (btn.once) {
                    btn.finished = true;
                }
                btn.after();
                btn.currentJobId = -1;  // 重置票据
            }
        }
    }
}