# uXueScript

uXueScript 是面向学习通网页版的桌面端课程辅助工具，使用 Tauri、Rust 与 Vue 重构自 [uXuexitongJS](https://github.com/unraous/uXuexitongJS)。它保留旧版的课程自动化与 AI 答题能力，并将配置、课程控制和状态展示整合到桌面应用中。

> 项目处于重构后的早期迭代阶段，版本更新会相对频繁。遇到问题前，请先确认自己正在使用最新版本。

## 功能

- 读取课程章节与完成进度，自动切换待完成内容
- 支持视频、文档和阅读等课程任务的自动处理
- 支持播放倍速、静音和后台播放
- 提取章节测验内容，并通过已配置的大模型生成参考答案
- 支持多个模型供应商、模型切换及 API Key 本地配置
- 保留可直接注入浏览器控制台的核心脚本，未连接桌面后端时仍可处理支持的非测验任务

## 使用方式

1. 在 **Configuration** 中选择合适的模型供应商和模型，并填写 API Key。
2. 在右下角的课程页面登录学习通，打开要处理的课程。
3. 根据弹窗提示启动课程任务。课程进度和当前状态会显示在应用内。

API Key 仅用于向你配置的模型供应商发起请求。请使用自己拥有且可安全使用的密钥。

## 兼容性与反馈

作者不是学习通长期用户，可用于测试的课程资源有限；部分特殊课程尚未充分验证，可能存在兼容性问题。若更新到最新版本后问题仍未解决，请在 [GitHub Issues](https://github.com/unraous/uxs-rs/issues) 提交复现步骤、课程类型和必要的错误信息，或发送邮件至 <unraous@qq.com>。

本项目以非盈利目的维护，仅供个人学习、自动化研究与技术交流。使用前请自行确认学校和平台的规则；作者不对使用本软件产生的后果承担责任。请勿将其用于考试作弊或其他违法、违规用途。

## 开发

前端使用 pnpm 管理依赖；运行桌面端还需要 Rust 的稳定版工具链和 Tauri 所需的系统依赖。

```sh
pnpm install
pnpm tauri dev
```

构建前端：

```sh
pnpm run build
```

构建桌面安装包：

```sh
pnpm tauri build
```

## 致谢与第三方资源

- 项目由旧版 [uXuexitongJS](https://github.com/unraous/uXuexitongJS) 重构而来。
- 加密字体字形哈希表 `src-tauri/src/core/quiz/table.json` 的内嵌元数据注明作者为 `wyn665817`，许可为 MIT。
- `ttf-parser` 使用 MIT 或 Apache-2.0 双许可；Typr.js 为 MIT 许可，其字形路径格式为当前兼容实现的参考来源。
- 界面字体 ChillRoundF（寒蝉全圆体）以 SIL Open Font License 1.1 发布；完整文本见 [licenses/OFL-1.1.txt](licenses/OFL-1.1.txt)。

## 许可证

除上述第三方资源外，本仓库中的 uXueScript 源代码以 [GNU GPL v3.0 only](LICENSE) 发布。GPL 保障复制、修改和再分发的自由，并要求衍生程序在发布时提供相同的自由；它不限制商业再分发。
