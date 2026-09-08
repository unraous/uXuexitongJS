<h1 align="center">uXueScript</h1>

<p align="center">
  <img src="src-tauri/icons/icon.png" width="160" alt="uXueScript Logo">
</p>

uXueScript 是学习通网页版课程辅助工具，使用 Tauri、Rust 与 Vue 开发，重构自 [history 分支中的 uXuexitongJS](https://github.com/unraous/uxuescript/tree/history)。桌面端集成课程控制、模型配置和进度展示，同时保留可在浏览器控制台执行的独立脚本。

> 本版本仍在持续完善。提交问题前，请先确认已更新至最新版本。

## 2.0.0 更新

- 大幅缩小桌面端产物体积，降低下载、安装与启动开销。
- 移除 Selenium 依赖，课程页面直接由内嵌 WebView 承载，程序更轻量。
- 修复测验页的特殊处理：此前单页只能处理一组题目，并可能在答题过程中直接跳转至其他任务点。

## 功能特性

- 读取课程章节与完成进度，自动切换待完成内容
- 支持视频、文档和阅读等课程任务的自动处理
- 支持倍速播放、静音、会话保持和后台播放
- 提取章节测验内容，并通过已配置的大模型生成参考答案
- 支持多个模型供应商、模型切换及 API Key 本地配置
- 桌面端自动向课程页面注入脚本；也可直接复制单文件脚本运行

## 注意事项

- 智能答题需自行配置模型供应商、模型和 API Key；密钥仅用于请求所选供应商的服务。
- 作者不是学习通长期用户，可用于测试的课程资源有限。特殊课程可能存在兼容性问题。
- 本项目仅供个人学习、自动化研究与技术交流。使用前请确认学校和平台规则，不得用于考试作弊或其他违法、违规用途。

## 使用方式

### 直接使用

从 [Release 页面](https://github.com/unraous/uxuescript/releases) 下载对应平台的最新发行包。启动应用后，请参阅[桌面端使用指南](docs/usage/desktop.md)。

### 自行构建

如需修改代码或自行打包，请参阅[构建指南](docs/development/build.md)。

## 运行方式

- **桌面端模式：** 从 [Release 页面](https://github.com/unraous/uxuescript/releases) 获取发行包。桌面端管理课程 WebView、保存配置并自动注入课程脚本。
- **无后端模式：** 将 `core.js` 复制到浏览器控制台执行。完整步骤见[无后端模式](docs/backend-free.md)。

## 文档

- [桌面端使用](docs/usage/desktop.md)：模型配置、课程操作和状态说明。
- [智能答题](docs/usage/ai.md)：模型配置与题目处理流程。
- [无后端模式](docs/backend-free.md)：浏览器控制台执行单文件脚本。
- [构建指南](docs/development/build.md)：开发环境、检查和打包。
- [架构概览](docs/architecture/overview.md)：前端、后端、课程 WebView 和独立脚本。
- [常见问题](docs/troubleshooting.md)：粘贴限制、模型请求和兼容性问题。

## 反馈与贡献

如问题在更新后仍未解决，请在 [GitHub Issues](https://github.com/unraous/uxuescript/issues) 提交复现步骤、课程类型和必要的错误信息，或发送邮件至 <unraous@qq.com>。

## 许可证

除第三方资源外，本仓库中的 uXueScript 源代码以 [GNU GPL v3.0 only](LICENSE) 发布。第三方字体、字形哈希表与依赖的归属和许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
