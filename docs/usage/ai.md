# 智能答题

智能答题仅在桌面端模式下可用。程序从课程页面提取章节测验内容；如检测到 `font-cxsecret` 加密字体，会先还原文字，再向所配置的模型供应商请求参考答案。

## 配置步骤

1. 打开 **Configuration**。
2. 选择 Provider 和 Model。
3. 输入对应供应商的 API Key。
4. 点击 **Save**。

本地默认配置包含 BigModel、DeepSeek、Google、Moonshot、OpenAI、OpenRouter 和 Ollama。具体可用模型以供应商当前文档和账户权限为准。

## 本地 Ollama

使用 Ollama 前，需在本机启动服务并安装模型。服务未启动或没有可用模型时，模型列表无法更新。

## 加密字体还原

部分题目以 `font-cxsecret` 显示混淆文字。程序从页面样式中提取字体，按字形路径匹配映射后处理题目内容。字形哈希表的 MIT 归属见 [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md)。

## 使用边界

- API Key 保存于本地配置文件，不要将配置文件或密钥提交到公开仓库。
- 模型输出仅供参考，不能保证适用于所有题型。
- 无后端模式不提供智能答题。需直接复制脚本时，请使用[无后端模式](../backend-free.md)。
