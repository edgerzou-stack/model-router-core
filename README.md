# model-router-core

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](#)

> **项目定位 (Project Positioning)**
> `model-router-core` 是一个面向 AI Agent 的本地运行时，用来把“先计划、后审批、再执行、再复核”的工作流固化为一个可诊断、可配置、可运行的 CLI 工具。

**model-router-core** 的目标不是让 AI 自由发挥，而是把一套严谨的 `Plan -> Approval -> Execute -> Review` 流程真正做成可运行 runtime：

- 强模型负责 `plan/review`
- 便宜模型负责 `execute`
- 所有关键边界显式可见
- 配置缺失可诊断
- 人工审批不可跳过
- 工作状态可落盘

这使它更像一个“可控的 agent workflow engine”，而不是单次 API 调用脚本。

---

## 核心特性 (Key Features)

- **先诊断后运行 (Diagnose Before Run)**：通过 `model-router doctor` 明确告诉用户：配置是否存在、字段是否完整、环境变量是否缺失。
- **本地配置 + 环境变量密钥 (Local Config + Env Secrets)**：结构化配置放在 `config/runtime.yaml`，敏感密钥仅放环境变量，避免泄漏到仓库。
- **角色与提供商解耦 (Role / Provider Decoupling)**：使用 `premium / cheap` 表示系统角色，使用 `openai / deepseek / mock` 表示底层模型提供商，便于未来替换。
- **强制审批闸门 (Mandatory Approval Gate)**：`plan` 完成后流程强制停住，必须显式批准后才能进入 `execute`。
- **真实状态落盘 (Stateful Workflow)**：每个任务都有本地状态文件，支持 `run -> approve -> execute -> review` 的明确阶段推进。
- **面向 AI 可读 (AI-Readable Repo)**：通过 `README`、`ARCHITECTURE`、`AI_SETUP_CONTRACT` 和 `doctor` 输出，让另一个 AI 能迅速判断还缺哪些配置。
- **Playbook 风格输出 (Playbook-like Output)**：CLI 成功路径包含 `✅ Completed / 🔄 Active / ➡️ Next` 阶段块，帮助用户和 AI 理解下一步操作。

---

## 架构哲学 (Architecture Philosophy)

- **工作流优先 (Workflow First)**：先固化阶段边界，再谈模型能力。
- **显式优先于隐式 (Explicit Over Implicit)**：缺什么就报什么，不做静默魔法配置。
- **角色优先于厂商 (Role Before Vendor)**：先定义 `premium/cheap` 的职责，再决定底层接 `openai/deepseek/mock`。
- **先跑通，再做聪明 (Make It Run Before Making It Smart)**：先用简单稳定规则与最小 provider 调用跑通，再升级分类器、重试、并发和工具调用。
- **人工审批不可省略 (Human Approval Is a Feature)**：人不是 fallback，而是这个系统设计中的正式决策节点。

---

## 目录结构 (Directory Structure)

```text
model-router-core/
├── config/
│   ├── runtime.example.yaml      # 本地配置模板
│   └── runtime.yaml              # 运行时本地配置（用户生成）
├── docs/
│   └── AI_SETUP_CONTRACT.md      # 给 AI 的设置契约
├── src/model_router/
│   ├── cli.py                    # 命令行入口
│   ├── cli_blocks.py             # 结构化输出块
│   ├── config.py                 # 配置加载与校验
│   ├── diagnostics.py            # 运行前诊断
│   ├── registry.py               # provider 解析
│   ├── state_store.py            # 状态文件持久化
│   ├── workflow.py               # Plan/Execute/Review 引擎
│   ├── exceptions.py             # 统一错误类型
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

### 6. 批准 / 执行 / 复核

```bash
model-router approve --state .runs/<task>.json --goal "..."
model-router execute --state .runs/<task>.json
model-router review --state .runs/<task>.json
model-router show --state .runs/<task>.json
```

---

## 配置原则 (Configuration Rules)

### 结构化配置放这里

- `config/runtime.yaml`

这里放：
- `premium / cheap` 角色绑定
- provider 名称
- model 名称
- env var 名称
- 可选 `base_url` 与 `api_style`
- routing 默认规则

### 敏感密钥放环境变量

不要把以下内容写进仓库配置：
- `OPENAI_API_KEY`
- `DEEPSEEK_API_KEY`
- 其他 token / secret / access credential

---

## OpenAI-Compatible Gateway 支持

当前版本已支持 `OpenAI-compatible` 网关配置，例如：

```yaml
roles:
  premium:
    provider: openai
    model: gpt-5-codex
    api_key_env: OPENAI_API_KEY
    base_url: https://vip.auto-code.net/v1
    api_style: responses
```

也就是说：
- `openai` provider 不一定非得直连官方 OpenAI
- 只要你的网关兼容 `responses` 或 `chat/completions`，就可以接入

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

### `model-router approve`
- 记录人工批准结果
- 写入 handoff packet
- 把任务切换到可执行状态

### `model-router execute`
- 调用 cheap 角色 provider 执行批准后的任务
- 保存执行输出到状态文件

### `model-router review`
- 调用 premium 角色 provider 审查执行结果
- 输出通过/拒绝/建议等 review 结果

### `model-router show`
- 查看当前状态文件中的完整信息

---

## 真实能力状态 (Current Real Capability)

当前版本已经完成了以下真实验证：

- `doctor` 可真实识别 readiness
- `premium` 已成功接入真实 OpenAI-compatible gateway
- `cheap` 已成功接入真实 DeepSeek
- `plan -> approve -> execute -> review` 整体链路已真实跑通
- 状态文件 `.runs/*.json` 可持续记录任务阶段状态

换句话说：
- 这已经不是概念验证
- 也不是纯 mock demo
- 而是一个 **可真实使用的 v1 runtime**

---

## 体验与鲁棒性增强 (UX & Robustness)

当前版本额外支持：

- 结构化成功输出块：`Completed / Active / Next`
- 结构化 provider 错误输出：
  - provider 名称
  - model 名称
  - HTTP 状态码
  - 响应摘要
- 更清晰的故障定位，适合调试：
  - 官方 API
  - OpenAI-compatible gateway
  - DeepSeek provider

---

## 测试 (Tests)

```bash
python3 -m unittest discover -s tests
```

当前测试覆盖：
- config 加载与校验
- diagnostics readiness
- provider registry
- CLI run gate
- workflow approval discipline
- provider 错误包装
- CLI 输出风格

---

## 当前边界 (Current Boundary)

当前版本已经支持：
- 本地 config
- env secret 约束
- doctor / init / run
- 状态文件流转
- 第一版真实 `OpenAI-compatible` / `DeepSeek` 文本调用
- playbook 风格成功/失败输出

当前版本暂不支持：
- streaming
- retries/backoff
- tool calling
- web UI
- 长时任务编排
- 自动审批
- 高级 memory 管理

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
8. 再按 `approve -> execute -> review` 推进

这正是本仓库向 `ai-agent-playbook` 靠拢的地方：
- 不是追求模型自由执行
- 而是追求“可控、透明、可审计”的 agent workflow
