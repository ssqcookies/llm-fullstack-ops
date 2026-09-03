# llm-fullstack-ops

V1.0版本————轻量化LLMOps全栈工程化落地脚手架 | Python3.12 + Flask + LangChain 0.2.1
License: MIT

## 一、项目定位

对标LLMOps完整生命周期规范，解决AI应用从模型接入、对话交互、知识库检索、Agent开发、工作流编排到运维成本统计全链路重复开发工作，大幅降低企业AI应用落地成本。

## 二、核心解决的9大AI开发痛点

### 1. 多模型统一网关层

1. **Prompt工程适配**：支持多模型Prompt测评、差异化提示词模板管理；
2. **异构接口对齐**：智谱GLM、Moonshot等模型统一封装为OpenAI兼容协议，配置化切换，业务代码零改动；
3. **Token消耗计量**：全链路记录输入/输出Token用量，自动核算调用成本，实现用量可观测。

### 2. 对话与知识库能力层

1. **长短对话记忆**：Redis缓存短期会话上下文，向量库存储对话摘要实现长期记忆；
2. **RAG分层检索优化**：支持关键词检索、向量相似度检索、结果重排三级方案，按需控制成本与精度；
3. **需求到Agent闭环**：支持自定义工具开发、Agent编排、测试、一键部署完整流程。

### 3. 交互与任务编排层

1. **全场景流式响应**：SSE流式输出优化前端体验，兼容流式/非流式两种返回格式；
2. **复杂任务工作流编排**：大任务拆分子节点，不同子任务指派不同模型执行，性能与成本最优平衡。

## 三、架构与工程规范

1. 依赖注入分层架构，代码解耦易扩展；
2. 环境变量隔离配置，敏感密钥统一管理；
3. 统一异常捕获、标准化API返回体；
4. 文档遵循Diátaxis四分法规范维护。

## 四、项目结构

```tree
llm-fullstack-ops/
├──app                      // 应用入口集合
|	├──__init__.py
|   └──http
|	|	├──__init__.py
|	|	├──app.py           // 主入口
|	|	└──module.py        //扩展模块导入
├─config                    // 应用配置文件
|	├──__init__.py
|	├──config.py
|	└──default_config.py    //应用默认配置
├──internal                 // 应用所有内部文件夹
|   ├──core                 // LLM核心文件，集成LangChain、LLM、Embedding等非逻辑的代码
|	|	|──agent
|	|	├──chain
|	|	├──prompt
|	|	├──model_runtime
|	|	├──moderation
|	|	├──tools            //插件工具
|	|	├──vector_store
|	|	└──...
|   ├──exception            // 通用公共异常目录
|	|	├──__init__.py
|	|	├──exception.py
|	|	└──...
|   ├──extension            // Flask扩展文件目录
|	|	├──__init__.py
|	|	├──database_extension.py
|	|	└──migrate_extension.py
|   ├──handler              // 控制器/路由层（只写接口接收、参数校验、调用service）
|	|	├──__init__.py
|	|	├──account_handler.py
|	|	└──app.handler.py   //应用控制器
|   ├──middleware           // 应用中间件目录，包含校验是否登录
|	|	├──__init__.py
|	|	└──middleware.py
|	|	└──...
|   ├──migration            // 数据库迁移文件目录，自动生成
|	|	├──versions         //  迁移版本
|	|	└──...
|   ├──model                // 数据库模型文件目录
|	|	├──__init__.py
|	|	├──account.py
|	|	└──app.py           // # App ORM模型
|   ├──router               // 应用路由文件夹
|	|	├──__init__.py
|	|	├──router.py
|	|	└──...
|   ├──schedule             // 调度任务、定时任务文件夹
|	|	├──__init__.py
|	|	└──...
|   ├──schema               // 请求和响应的结构体
|	|	├──__init__.py
|	|	└──app.schema.py    //基础聊天接口验证
|   ├──server               // 构建的应用，与app文件夹对应
|	|	├──__init__.py
|	|	└──http.py          //http服务引擎
|   ├──service              // 服务层文件夹。业务逻辑层（LangChain调用、向量库操作、复杂计算）
|	|	├──__init__.py
|	|	├──oauth_service.py
|	|	└──app.service.py   //应用服务逻辑层：封装App相关数据库业务CRUD
|   ├──task                 // 任务文件夹，支持即时任务+延迟任务
|	|	├──__init__.py
|	|	└──...
├──pkg                      // 扩展包文件夹
|	├──__init__.py
|	|──oauth
|	|	├──__init__.py
|	|	├──github_oauth.py
|	|	└──...
|	|──response
|	|	├──__init__.py
|	|	├──http_code.py
|	|	└──response.py
|	|──sqlalchemy
|	|	├──__init__.py
|	|	└──sqlalchemy.py
|	└──...
├──storage              // 本地存储文件夹
├──test             // 测试目录
|	├──__init__.py
|	├──conftest.py
|	|──internal
|	|	├──handler
|	|	├──__init__.py
|	|	└──test_app_handler.py
|	└──...
├──venv  // 虚拟环境
├──.env  // 应用配置文件
├──.gitignore  // 配置git忽略文件
├──requirements.txt  // 第三方包依赖管理
└──README.md  // 项目说明文件
```