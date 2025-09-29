pragma ComponentBehavior: Bound
// 最主要的按钮样式
import QtQuick
import QtQuick.Controls.Basic

import "animation"

Button {
    id: btn;

    property int pixelSize: 18;
    property real gradientPos: btn.finished ? 0.0 : (
        btn.hovered ? (
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
            color: btn.finished ? "#79CEED" : (btn.pressed ? "#C5E7F1" : "#274A60");
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
                arcColor: "#274A60";
            }
        }
    }

    // 加载时禁用按钮交互
    enabled: !loading && !finished;

    background: Rectangle {
        radius: btn.height / 2;
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop {
                position: btn.calPos(0.0, btn.gradientPos);
                color: btn.finished ? "#18324A" : "#60EFDB";
                // 添加颜色动画行为
                Behavior on color { ColorAnimation { duration: 200; easing.type: Easing.InOutQuad } }
            }
            GradientStop {
                position: btn.calPos(0.25, btn.gradientPos);
                color: btn.finished ? "#204060" : "#BEF2E5";
                // 添加颜色动画行为
                Behavior on color { ColorAnimation { duration: 200; easing.type: Easing.InOutQuad } }
            }
            GradientStop {
                position: btn.calPos(0.5, btn.gradientPos);
                color: btn.finished ? "#274A60" : "#C5E7F1";
                // 添加颜色动画行为
                Behavior on color { ColorAnimation { duration: 200; easing.type: Easing.InOutQuad } }
            }
            GradientStop {
                position: btn.calPos(0.75, btn.gradientPos);
                color: btn.finished ? "#1B3A4D" : "#79CEED";
                // 添加颜色动画行为
                Behavior on color { ColorAnimation { duration: 200; easing.type: Easing.InOutQuad } }
            }
            GradientStop {
                position: 1.0;
                color: btn.finished ? "#101A26" : "#6F89A2";
                // 添加颜色动画行为
                Behavior on color { ColorAnimation { duration: 200; easing.type: Easing.InOutQuad } }
            }
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
        // qmllint disable unqualified
        target: backend
        
        // 3. 监听 workFinished 信号
        function onWorkFinished(finishedJobId) {
            // 4. 检查完成的票据是否是自己的
            if (btn.currentJobId !== -1 && btn.currentJobId === finishedJobId) {
                console.log("按钮 " + btn.text + " 确认任务 " + finishedJobId + " 已完成！");  
                loading = false;
                if (tip) {
                    saveTip.tipAnim.restart();
                }
                if (once) {
                    finished = true;
                }
                btn.after();

                btn.currentJobId = -1;  // 重置票据
            }
        }
    }
}