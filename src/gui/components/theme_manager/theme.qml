pragma Singleton
import QtQuick

import "../interface.js" as Interface

QtObject {
    id: theme
    property int colorId: Interface.dispatch("get_config", ["theme"]);
    property int changeId: Interface.dispatch("get_config", ["metadata", "theme"]);
    property string name: "ocean"
    property var color: [
        "#60EFDB", "#BEF2E5", "#C5E7F1", "#79CEED", "#6F89A2",
        "#18324A", "#204060", "#274A60", "#1B3A4D", "#101A26"
    ]
    property var font : FontLoader {
        id: fontFamily;
        source: "../../resources/ttf/mixture.ttf";
    }
    property var colorFamily : {}

    // 正则表达式解析 Python 字典
    function parsePythonDict(pythonStr) {
        const result = {};
        
        const themeRegex = /'(\w+)':\s*\[(.*?)\]/g;
        let match;
        
        while ((match = themeRegex.exec(pythonStr)) !== null) {
            const themeName = match[1];
            const colorsStr = match[2];
            const colorRegex = /'(#[0-9a-fA-F]{6})'/g;
            const colors = [];
            let colorMatch;  
            while ((colorMatch = colorRegex.exec(colorsStr)) !== null) {
                colors.push(colorMatch[1]);
            }        
            result[themeName] = colors;
        }
        
        return result;
    }

    function switchTo(name) {
        if (theme.colorFamily.hasOwnProperty(name)) {
            theme.name = name;
            theme.color = theme.colorFamily[name];
            console.log(`已切换至主题: ${name}`);
        } else {
            console.warn(`主题 ${name} 不存在`);
        }
    }

    function getColor(name) {
        if (theme.colorFamily?.hasOwnProperty(name)) {
            return [...theme.colorFamily[name]];
        } else {
            console.warn(`主题 ${name} 不存在`);
            return [];
        }
    }

    property Connections backendConnections: Connections {
        target: backend; // qmllint disable unqualified
        function onFinished(finishedJobId) {
            if (theme.colorId === finishedJobId) {
                console.log(`主题加载任务 ${finishedJobId} 已完成'!`);
                const resultStr = Interface.getResult(theme.colorId);
                try {
                    const result = theme.parsePythonDict(resultStr);  // 使用正则表达式解析
                    
                    if (Object.keys(result).length > 0) {
                        theme.colorFamily = result;
                        console.log(`主题加载成功: ${JSON.stringify(theme.colorFamily)}`);
                        
                    } else {
                        console.warn(`主题加载失败: 解析结果为空`);
                    }
                } catch (e) {
                    console.error(`正则解析失败: ${e.message}`);
                }
            } else if (theme.changeId === finishedJobId) {
                console.log(`主题切换任务 ${finishedJobId} 已完成'!`);
                theme.switchTo(Interface.getResult(theme.changeId));
            }
        }
    }

}