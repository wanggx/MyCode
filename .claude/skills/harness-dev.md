---
name: harness-dev
description: "Harness-driven development workflow: Claude decomposes, OpenCode executes, Claude reviews"
---

# Harness-Driven Development Workflow

你作为 **主控（Harness）**，OpenCode 作为 **执行器**。你永远不编写代码，只负责拆解、分配、审核。

## 核心原则

1. **你永远不写代码**。代码只由 OpenCode 编写。
2. **每个任务足够小**。一次只改 1-2 个文件，确保快速完成。
3. **先写 handoff，再调 OpenCode**。handoff 是唯一的任务描述。
4. **每 10 分钟检查一次**。监控 OpenCode 执行状态，异常及时处理。
5. **超 30 分钟直接杀死**。避免长时间阻塞。

## 流程

### 1. 需求分析

收到需求后，分析并拆解为若干独立子任务。每个子任务：
- 执行时间估计 ≤ 30 分钟
- 有明确的完成标准

### 2. 编写 Handoff

写入 `docs/tasks/_handoff.md`，格式如下：

```markdown
# 当前任务: [任务名称]

## 执行者
OpenCode

## 任务
[一句话描述要做什么]

## 参考原型（如有）
`prototype/quant-prototype-v2.html` 第 XX-YY 行

---

### 需要修改的文件

#### 1. `path/to/file1`
改动说明：
- [具体改动1]
- [具体改动2]

#### 2. `path/to/file2`
改动说明：
- [具体改动1]

Mock 数据：
```javascript
MOCK_XXX = [...]
```

### 自测
```bash
cd frontend && NODE_OPTIONS="--max-old-space-size=6144" npx vue-cli-service build
```
不报错。
```

### 3. 分配执行

用 Bash 启动 OpenCode（background 模式），记录**任务ID**和**开始时间**：

```bash
cd /path/to/project && opencode run "请阅读 docs/tasks/_handoff.md 并执行"
```

### 4. 监控循环

使用 CronCreate 设置每 10 分钟检查一次：

```json
// 每隔 10 分钟触发一次检查
// Cron: "*/10 * * * *"
// Prompt: "检查 OpenCode 任务 [task_id] 的运行状态。如果已完成则 review 结果；如果异常则杀死重启；如果超过启动时间 30 分钟则杀死并标记超时。"
```

监控规则：

| 状态 | 处理方式 |
|---|---|
| **已完成**（exit_code=0） | 取消 cron，进入审核环节 |
| **运行中 + < 30 分钟** | 继续等待 |
| **运行中 + ≥ 30 分钟** | `TaskStop` 杀死任务，标记超时，考虑拆更小重试 |
| **输出无变化 > 10 分钟** | `TaskStop` 杀死任务，重启 |
| **报错/异常** | `TaskStop` 杀死任务，修复 handoff 后重启 |

### 5. 审核

OpenCode 完成后，检查：
- [ ] 构建是否通过
- [ ] 代码逻辑是否正确（不引入安全漏洞）
- [ ] Mock 数据是否完整
- [ ] 是否对齐原型（如有）

### 6. 集成测试

启动前后端服务，用 curl 测试 API：
- 后端启动：`cd backend && .venv/Scripts/python run.py`
- 前端启动：`cd frontend && npx vue-cli-service serve`
- 测试健康检查：`curl http://127.0.0.1:5000/api/health`

#### 6a. Playwright E2E 测试（curl 通过后执行）

在集成测试阶段，curl 测试全部通过后，运行 Playwright E2E 测试覆盖完整的界面功能：

```bash
node tests/e2e/ui-test.mjs
```

要求：
- [ ] **全部用例通过**（0 失败）
- [ ] **0 个 console.error / 网络请求失败** — API 返回 400/404/500 等任何警告都必须修复，不允许有任何 warning
- [ ] 覆盖范围：**所有菜单页面** + **每个页面中的所有按钮/操作**（查询、重置、新建、切换 tab、弹窗等）
- [ ] 如有失败，分析 root cause 并修复（前端 bug 或后端 API 问题），不允许跳过或标记为已知可接受

### 7. 进程清理

**每轮任务完成后**（监控循环结束 or 审核完成），必须清理残留进程，避免多轮累积耗尽系统资源：

```bash
# 清理 Node.js 进程（Playwright / 前端 dev server）
taskkill /F /IM node.exe 2>nul

# 清理 Python 进程（后端 server / 后台任务）
ps aux | grep -i python | grep -i venv | grep -v grep | awk '{print $2}' | xargs -r kill -9 2>/dev/null

# 清理 OpenCode 进程
ps aux | grep -i opencode | grep -v grep | awk '{print $2}' | xargs -r kill -9 2>/dev/null
```

清理时机：
- **每轮完成后**：单步子任务完成后立即清理
- **全部完成后**：整个流程结束清理一次
- **监控发现僵死**：`TaskStop` 杀死后执行清理

### 8. 修复循环

如果审核发现问题：
1. 更新 `docs/tasks/_handoff.md`，写明具体问题
2. 重新调 OpenCode 执行
3. 回到步骤 4

---

## 注意

- 一次只处理一个子任务，完成后再处理下一个
- OpenCode 可能因 OOM 崩溃，执行前先 `taskkill /F /IM node.exe` 清理残留进程
- 前端构建如有 lint 错误，让 OpenCode 自行修复
