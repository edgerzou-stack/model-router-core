# model-router-core

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](#)

> **项目定位 (Project Positioning)**
> `model-router-core` 是一个面向 AI Agent 的本地运行时骨架，用来把“先计划、后审批、再执行、再复核”的工作流固化为一个可诊断、可配置、可运行的 CLI 工具。

**model-router-core** 专门用于把 `Plan -> Approval -> Execute -> Review` 这套流程，从提示词习惯升级成真正可执行的 agent runtime。它的目标不是“让 AI 自由发挥”，而是让 AI 在强约束下安全协作：先用强模型缩问题，再用便宜模型机械执行，并把配置缺失、审批边界、执行状态全部显式暴露出来。

---

## 核心特性 (Key Features)

- **先诊断后运行 (Diagnose Before Run)**：通过 `model-router doctor` 在执行前明确告诉用户：配置文件是否存在、字段是否完整、环境变量是否缺失。
- **本地配置 + 环境变量密钥 (Local Config + Env Secrets)**：结构化配置放在 `config/runtime.yaml`，敏感密钥仅放环境变量，避免泄漏到仓库。
- **角色与提供商解耦 (Role / Provider Decoupling)**：使用 `premium / cheap` 表示系统角色，使用 `openai / deepseek / mock` 表示底层模型提供商，方便未来替换。
- **强制审批闸门 (Mandatory Approval Gate)**：`plan` 完成后流程强制停止，必须显式批准后才能进入 `execute`。
- **可被 AI 阅读的仓库 (AI-Readable Repo)**：通过 `README`、`ARCHITECTURE`、`AI_SETUP_CONTRACT` 和 `doctor` 输出，让另一个 AI 能快速判断你还缺哪些配置。

---

## 架构哲学 (Architecture Philosophy)

- **工作流优先 (Workflow First)**：先固化阶段边界，再谈模型能力。
- **显式优先于隐式 (Explicit Over Implicit)**：缺什么就报什么，不做静默魔法配置。
- **角色优先于厂商 (Role Before Vendor)**：先定义 `premium/cheap` 的职责，再决定底层接 `openai/deepseek/mock`。
- **先跑通，再做聪明 (Make It Run Before Making It Smart)**：先用简单稳定规则和最小 API 调用跑通，再升级分类器、重试、并发和工具调用。

---

## 目录结构 (Directory Structure)

```text
model-router-core/
├── config/
│   └── runtime.example.yaml      # 本地配置模板
├── docs/
│   └── AI_SETUP_CONTRACT.md      # 给 AI 的设置契约
├── src/model_router/
│   ├── cli.py                    # 命令行入口
│   ├── config.py                 # 配置加载与校验
│   ├── diagnostics.py            # 运行前诊断
│   ├── registry.py               # provider 解析
│   ├── workflow.py               # Plan/Execute/Review 引擎
│   └── providers/                # OpenAI / DeepSeek / Mock provider
├── tests/                        # 核心测试
├── ARCHITECTURE.md               # 架构说明
└── README.md                     # 本说明文档
```

---

## 快速上手 (Quick Start)

### 1. 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. 初始化本地配置

```bash
model-router init
```

它会生成：

```text
config/runtime.yaml
```

### 3. 配置环境变量

```bash
export OPENAI_API_KEY="your-openai-key"
export DEEPSEEK_API_KEY="your-deepseek-key"
```

### 4. 诊断当前是否可运行

```bash
model-router doctor
```

### 5. 启动一个任务

```bash
model-router run --task "Refactor this module"
```

流程会在 `plan` 后停住，等待你人工批准。

---

## 配置原则 (Configuration Rules)

### 结构化配置放这里

- `config/runtime.yaml`

这里放：
- `premium / cheap` 角色绑定
- provider 名称
- model 名称
- env var 名称
- routing 默认规则

### 敏感密钥放环境变量

不要把以下内容写进仓库配置：
- `OPENAI_API_KEY`
- `DEEPSEEK_API_KEY`
- 其他 token / secret / access credential

---

## 命令参考 (Command Reference)

### `model-router init`
- 创建本地配置模板
- 不覆盖已有配置，除非加 `--force`

### `model-router doctor`
- 检查配置文件是否存在
- 检查配置是否完整
- 检查环境变量是否缺失
- 输出可执行性状态：`UNINITIALIZED / MISCONFIGURED / READY`

### `model-router run --task "..."`
- 读取配置
- 检查 readiness
- 如果未准备好，则拒绝执行并告诉你缺什么
- 如果准备好，则启动 `plan`
- 在 `plan` 后强制停住等待审批

### 低层命令
- `model-router approve`
- `model-router execute`
- `model-router review`
- `model-router show`

这些命令用于显式推进阶段，不做自动跳步。

---

## 测试 (Tests)

```bash
python3 -m unittest discover -s tests
```

---

## 当前边界 (Current Boundary)

当前版本已经支持：
- 本地 config
- env secret 约束
- doctor / init / run
- mock provider
- 第一版真实 `OpenAI` / `DeepSeek` 文本调用

当前版本暂不支持：
- streaming
- retries
- tool calling
- web UI
- 长时任务编排
- 自动审批

---

## 面向 AI 的使用方式 (How Another AI Should Use This Repo)

如果你让另一个 AI 来帮你使用这个仓库，推荐它遵守：

1. 先读 `README.md`
2. 再读 `docs/AI_SETUP_CONTRACT.md`
3. 先运行 `model-router doctor`
4. 如果缺配置，先引导用户补配置
5. 如果缺环境变量，明确要求用户提供 env var
6. 只有在 `READY` 时才允许 `run`
7. 在 `plan` 后停住，等待用户审批

这正是本仓库向 `ai-agent-playbook` 靠拢的地方：
- 不是追求模型自由执行
- 而是追求“可控、透明、可审计”的 agent workflow
