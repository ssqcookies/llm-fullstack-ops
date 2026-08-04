---
skill_name: LlmOps项目目录自动构建器
trigger_keywords:

- 读取README生成Python项目目录
- 根据readme搭建llmops工程目录
- 初始化python项目文件夹结构
- 按文档创建模块目录
  exclude_scenes:
- 不自动编写Python业务代码，仅创建目录+空占位文件
  version: 1.0
  scope: Python LlmOps工程

---

## 一、触发规则

1. 指令包含README、目录结构、创建文件夹、初始化工程、llmops架构时自动启用；
2. 优先解析项目根目录 README.md 中 ```tree 包裹的树形目录；
3. 只做文件系统创建，不冗余科普，采用渐进式回复。

## 二、强制约束（禁止项优先）

### 禁止行为

1. ❌ 绝不凭空脑补README不存在的目录，严格按文档结构还原；
2. ❌ 不覆盖已存在文件/文件夹，重复路径直接跳过并标注；
3. ❌ 不使用中文命名目录、文件名，全部小写蛇形命名；
4. ❌ 不深度嵌套超过5级目录，层级过深给出警告；
5. ❌ 不自动写入复杂逻辑代码，仅创建空占位文件。

### 强制执行规则

1. 第一步：解析README tree结构，先输出目录树给用户确认（第一层披露）；
2. 用户确认后批量创建物理文件夹；
3. Python模块规范：每个包目录自动生成 `__init__.py`；
4. 通用占位文件规则：
    - 模块目录：`__init__.py`
    - 配置目录：预留 `config.yaml` / `.env` 占位
    - 脚本目录：预留 `main.py` 入口
    - 测试目录：自动生成 `tests/` 及 `conftest.py`
5. 区分源码目录 `src/`、配置目录 `config/`、脚本 `scripts/`、日志 `logs/`、缓存 `.cache/`；
6. 创建完成输出报告：新建成功列表、已存在跳过列表。

## 三、交互渐进式流程

1. 首次回复：解析出完整目录树，询问是否确认创建；
2. 确认后执行磁盘创建；
3. 执行完毕输出结果，可按需补充生成 `.gitignore`、`requirements.txt`；
4. 可二次指令同步更新README与实际目录。

## 四、README标准可识别格式示例

```tree
src/
├── llm_client/        # 大模型调用封装
├── prompt/            # 提示词管理
├── pipeline/          # 工作流编排
├── utils/             # 工具函数
└── config_loader/     # 配置读取
config/
scripts/
tests/
logs/