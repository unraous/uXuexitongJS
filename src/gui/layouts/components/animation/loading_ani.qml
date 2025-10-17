import QtQuick
import QtQuick.Shapes

import "../theme_manager"

Item {
    id: root;
    width: 30;
    height: width;

    property real centerX: width / 2;
    property real centerY: height / 2;
    property real arcRadius: width * 0.4;
    property real arcWidth: width * 0.15;  // 弧的厚度
    property color arcColor: Theme.color[7];
    property real sweepAngleValue: 0.01;  // 弧度
    property real startAngle: -90;  // 相位
    property real dotRadius: width * 0.75;  // 点的半径
    
    
    // 弧形
    Shape {
        id: arcShape1;
        anchors.fill: parent;
        antialiasing: true;
        smooth: true;
        layer.enabled: true;
        layer.samples: 8;  // 增加采样率

        ShapePath {
            id: arcPath1
            fillColor: "transparent";  // 不填充
            strokeColor: root.arcColor;  // 使用纯色
            strokeWidth: root.arcWidth;
            capStyle: ShapePath.RoundCap;  // 圆形端点
            // 画弧（不是从中心点，而是直接画弧线）
            PathAngleArc {
                centerX: root.centerX;
                centerY: root.centerY;
                radiusX: root.arcRadius;
                radiusY: root.arcRadius;
                startAngle: root.startAngle;
                sweepAngle: root.sweepAngleValue;
            }
        }
    }
    
    Shape {
        id: arcShape2;
        anchors.fill: parent;
        antialiasing: true;
        smooth: true;
        layer.enabled: true;
        layer.samples: 8;  // 增加采样率
        
        ShapePath {
            id: arcPath2;
            fillColor: "transparent";  // 不填充
            strokeColor: root.arcColor;  // 使用纯色
            strokeWidth: root.arcWidth;
            capStyle: ShapePath.RoundCap;  // 圆形端点
            
            // 画弧（不是从中心点，而是直接画弧线）
            PathAngleArc {
                centerX: root.centerX;
                centerY: root.centerY;
                radiusX: root.arcRadius;
                radiusY: root.arcRadius;
                startAngle: root.startAngle + 180;
                sweepAngle: root.sweepAngleValue;
            }
        }
    }
    
    
    // 添加循环动画
    SequentialAnimation {
        running: true;
        loops: Animation.Infinite;

        NumberAnimation {
            target: root;
            property: "sweepAngleValue";
            from: 0.01;
            to: 180;
            duration: 1000;
            easing.type: Easing.InOutCubic;
        }

        NumberAnimation {
            target: root;
            property: "sweepAngleValue";
            from: 180;
            to: 0.01;
            duration: 1000;
            easing.type: Easing.InOutCubic;
        }
        
    }
    SequentialAnimation {
        running: true;
        loops: Animation.Infinite;

        NumberAnimation {
            target: root;
            property: "startAngle";
            from: -90;
            to: 270;
            duration: 1000;
            easing.type: Easing.InOutCubic;
        }
        
    }
}