<h1 align="center">uXueScript</h1>

<p align="center">
  <img src="src-tauri/icons/icon.png" width="160" alt="uXueScript Logo">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Rust-1.97.1-DEA584?style=flat-square&logo=rust&logoColor=white" alt="Rust 1.97.1">
  <img src="https://img.shields.io/badge/Tauri-2.11-24C8DB?style=flat-square&logo=tauri&logoColor=white" alt="Tauri 2.11">
  <img src="https://img.shields.io/badge/Vue-3.5-42B883?style=flat-square&logo=vuedotjs&logoColor=white" alt="Vue 3.5">
  <img src="https://img.shields.io/badge/TypeScript-5.6-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript 5.6">
  <img src="https://img.shields.io/badge/pnpm-12.3.4-F69220?style=flat-square&logo=pnpm&logoColor=white" alt="pnpm 12.3.4">
</p>

uXueScript 是学习通网页版课程辅助工具，使用 Tauri、Rust 与 Vue 开发，重构自 [history 分支中的 uXuexitongJS](https://github.com/unraous/uxuescript/tree/history)。桌面端集成课程控制、模型配置和进度展示，同时保留可在浏览器控制台执行的独立脚本。

> 本版本仍在持续完善。提交问题前，请先确认已更新至最新版本。

## 2.0.1 更新

- **更小的安装包：** Windows 发行包从旧版约百 MB 降至约 `6–7 MB`，下载和安装更快。
- **更轻的桌面端：** 不再依赖 Selenium、浏览器驱动或 Python 运行环境。首次使用无需等待下载驱动，也不会因网络波动导致驱动下载失败，安装后即可登录并使用课程页面。
- **更稳定的测验处理：** 同一页面中的题目会完整处理；提交答案后，程序会等待当前任务点完成，再继续下一项，避免答题过程中错误跳转。
- **更准确的题目识别：** 旧版通过哈希比对还原混淆字体，误判率较高且可能丢失题目信息。2.0 改用成熟的字体解析方案，更完整地还原题目内容，提高答题准确性。

## 功能特性

- 读取课程章节与完成进度，自动切换待完成内容
- 支持视频、文档和阅读等课程任务的自动处理
- 支持倍速播放、静音、会话保持和后台播放
- 提取章节测验内容，并通过已配置的大模型生成参考答案
- 支持多个模型供应商、模型切换及 API Key 本地配置
- 桌面端自动向课程页面注入脚本；也可直接复制单文件脚本运行

## 后续计划

- 自动检测新版本，方便在修复兼容性问题后及时升级。
- 完善 macOS 和 Linux 的构建、图标与发行支持。
- 继续完善刷课核心脚本，恢复互动题自动处理能力。
- 在课程页面返回标准答案时，自动回填并修正已记录的答案。
- 持续适配特殊课程页面与任务类型，改善兼容性和错误提示。

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
