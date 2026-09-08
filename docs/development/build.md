# 构建指南

## 前置条件

项目使用 pnpm、Node.js、Rust 和 Tauri 2。请安装 Node.js LTS、Rust 稳定版，并按 [Tauri 前置条件文档](https://v2.tauri.app/start/prerequisites/) 配置当前平台的系统依赖。

Windows 开发环境通常还需要 Microsoft C++ Build Tools 和 WebView2 Runtime；以 Tauri 官方文档的当前要求为准。

## 安装依赖

```sh
pnpm install
```

如果 Node.js 没有提供 pnpm，可先启用 Corepack：

```sh
corepack enable
```

## 本地开发

启动 Tauri 桌面端和 Vite 开发服务器：

```sh
pnpm tauri dev
```

仅启动前端开发服务器：

```sh
pnpm run dev
```

## 检查与构建

前端类型检查和生产构建：

```sh
pnpm run build
```

Rust 测试：

```sh
cargo test --manifest-path src-tauri/Cargo.toml
```

构建桌面端发行包：

```sh
pnpm tauri build
```

## 本地数据

运行时会在应用工作目录的 `uxs-data` 下保存配置和日志。该目录已被 Git 忽略；提交日志前请删除可能包含的敏感信息。
