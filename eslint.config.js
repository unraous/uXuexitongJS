import js from "@eslint/js";
import ts from "typescript-eslint";
import pluginVue from "eslint-plugin-vue";
import globals from "globals";
import eslintConfigPrettier from "eslint-config-prettier";

export default [
  js.configs.recommended,
  ...ts.configs.recommended,
  ...pluginVue.configs["flat/recommended"],
  eslintConfigPrettier,
  {
    files: ["**/*.vue", "**/*.ts", "**/*.js"],
    languageOptions: {
      globals: {
        ...globals.browser,
      },
    },
  },
  {
    files: ["**/*.vue"],
    languageOptions: {
      parserOptions: {
        parser: ts.parser,
      },
    },
  },
  {
    rules: {
      // 允许控制台打印
      "no-console": "off",
      // 避免出现未使用的变量
      "@typescript-eslint/no-unused-vars": "warn",
      // 与 Prettier 保持一致，允许 HTML 空元素自闭合 (<input />)
      "vue/html-self-closing": [
        "error",
        {
          html: {
            void: "always",
            normal: "any",
            component: "always",
          },
          svg: "always",
          math: "always",
        },
      ],
    },
  },
  {
    // 忽略生成文件与依赖目录
    ignores: ["dist/**", "src-tauri/target/**", "node_modules/**", "src/services/cmds.ts"],
  },
];
