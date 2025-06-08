# Contributing to uXuexitong

感谢你对本项目的关注！欢迎提交 Issue、Pull Request 或提出建议。请遵循以下贡献指南，以便我们更高效地协作。

---

## 环境准备

1. **克隆仓库**

   ```sh
   git clone <your-repo-url>
   cd uXuexitongJS
   ```
2. **创建并激活虚拟环境**

   - Windows:
     ```sh
     python -m venv venv
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```sh
     python3 -m venv venv
     source venv/bin/activate
     ```
3. **安装依赖**

   ```sh
   pip install -r requirements.txt
   ```
4. **前端依赖（如有）**

   - 若涉及 JS 依赖，请在 `src/js/` 目录下说明。

---

## 代码规范

- **Python**

  - 遵循 [PEP8](https://pep8.org/) 代码风格。
  - 推荐使用 `black` 或 `autopep8` 格式化代码。
  - 文件编码统一为 UTF-8。
  - 资源文件路径请使用 `resource_path("data/xxx")` 形式，避免多级 `..`。
- **JavaScript**

  - 推荐使用 [StandardJS](https://standardjs.com/) 或 ESLint 检查代码风格。
  - 变量命名清晰，注释充分。
- **资源文件**

  - 新增图片、字体、JSON 等资源请放在 `data/static/` 或 `resource/image/` 等对应目录。
  - 临时/输出文件请写入 `data/temp/` 或用户目录，不要覆盖静态资源。

---

## 提交规范

- **分支管理**
  - 建议使用 `feature/xxx`、`bugfix/xxx`、`docs/xxx` 等分支命名。
- **Commit 信息**
  - 使用简明英文或中文描述，如：
    ```
    feat: 新增AI答题接口
    fix: 修复资源路径兼容问题
    docs: 完善打包教程
    ```
- **PR 说明**
  - 请详细描述变更内容、影响范围及测试方式。

---

## Issue 反馈

- 提交 Issue 前请先搜索是否已存在类似问题。
- 提供详细的复现步骤、环境信息（操作系统、Python/Node 版本等）、报错日志等。
- Bug 报告请尽量附带截图或日志。

---

## Pull Request 流程

1. Fork 本仓库并新建分支。
2. 按上述规范进行开发和提交。
3. 本地测试通过后提交 PR。
4. 等待维护者 Review 并合并。

---

## 资源文件管理

- 只读资源（如字体、图片、模板）请放在 `data/static/` 或 `resource/image/`。
- 可写文件（如运行时生成的 json/html）请写入 `data/temp/` 或用户主目录。
- 打包时请确保所有静态资源通过 `--add-data` 参数包含。

---

## 代码审查与合并

- 所有 PR 需通过基本测试和代码审查。
- 维护者有权根据项目需要进行修改或拒绝合并。

---

## 其他

- 遵守 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。
- 禁止任何商业用途，遵循 CC BY-NC 4.0 协议。

---

感谢你的贡献！
