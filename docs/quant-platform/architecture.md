# 总体架构方案

## 目标

建设一个个人使用的轻量量化投研平台，核心能力包括：

- 数据获取与补录
- 数据质量诊断与修复
- 因子和技术指标研究
- 策略参数化运行
- 日频回测
- 选股信号解释
- 模拟组合与风险监控
- 任务调度与运行日志

该平台不做实盘交易、不接券商下单、不管理真实资金账户。

## 设计原则

1. 单体优先：不拆微服务。
2. 数据可靠优先：先保证数据可信，再扩展复杂策略。
3. 任务可追踪：所有长任务都必须有任务记录和步骤日志。
4. 计算轻量：日频为主，不做分钟级和 tick 级回测。
5. 可恢复：失败任务可查看原因并手动重试。
6. 可追溯：策略、回测、信号都能追溯到参数版本和数据日期。

## 部署形态

推荐单机部署：

```text
Nginx
  - 托管前端静态文件
  - 反向代理 /api 到 Flask

Flask API 进程
  - 处理页面 API 请求
  - 创建任务
  - 查询任务状态
  - 查询数据、信号、回测结果

后台 Worker 进程
  - 扫描 MySQL 任务表
  - 串行或低并发执行任务
  - 执行数据同步、补录、质量检查、策略、回测

MySQL
  - 行情数据
  - 策略配置
  - 信号结果
  - 回测结果
  - 任务日志
  - 数据质量问题
```

## 进程模型

建议至少两个 Python 进程：

```text
1. Web 进程
   python backend/run.py

2. Worker 进程
   python backend/worker.py
```

Web 进程只提交任务，不直接执行耗时计算。

Worker 进程负责：

- 定时创建每日同步任务
- 执行 pending 任务
- 更新任务状态
- 写入步骤日志
- 捕获异常并落库

如果服务器资源非常有限，Worker 第一版可以只允许一个任务运行：

```text
max_running_jobs = 1
```

## 核心分层

```text
API Layer
  app/api/*

Service Layer
  app/services/*

Repository Layer
  app/repositories/*

Database
  MySQL
```

建议新增服务：

```text
data_provider_service.py
data_quality_service.py
data_repair_service.py
task_service.py
factor_service.py
strategy_service.py
backtest_service.py
signal_service.py
portfolio_service.py
```

现有服务可以保留：

```text
data_service.py
stock_service.py
select_service.py
```

后续迁移原则：

- 不一次性重构全部旧代码。
- 新功能优先走新服务。
- 旧选股逻辑逐步纳入策略服务。

## 数据流

### 每日自动流程

```text
定时触发
  -> 创建 sync_daily_data 任务
  -> 下载 A 股日线
  -> 下载港股日线
  -> 合并临时数据到正式表
  -> 聚合周线/月线
  -> 执行数据质量扫描
  -> 如果数据健康，运行启用策略
  -> 生成信号
  -> 更新模拟组合
  -> 发送通知
```

### 数据修复流程

```text
发现数据缺口
  -> 创建 data_quality_issue
  -> 用户查看影响范围
  -> 用户确认修复
  -> 创建 repair_missing_data 任务
  -> 补录缺失数据
  -> 重新聚合
  -> 自动复检
  -> 更新 issue 状态
  -> 可选重跑受影响策略
```

### 回测流程

```text
用户提交回测
  -> 创建 backtest_job
  -> 创建 task_job
  -> Worker 执行日频回测
  -> 保存净值、持仓、交易明细、指标
  -> 前端查询结果并展示
```

## API 设计原则

1. 所有长任务 API 只创建任务并返回 `job_id`。
2. 前端通过任务中心或轮询查询任务状态。
3. 查询类 API 必须分页。
4. 大结果不直接实时计算，优先读取已落库结果。
5. 接口返回结构统一：

```json
{
  "success": true,
  "data": {},
  "message": ""
}
```

## 不做的事情

第一阶段不引入：

- Redis
- Celery
- Kafka
- Airflow
- ClickHouse
- Spark
- Kubernetes
- 分布式任务
- 在线代码 IDE
- 实盘交易
- 券商下单

## 资源控制

为适应个人服务器：

- 后台任务串行执行。
- 回测默认限制区间，例如默认 3 年，最大 8 年。
- 单次数据补录限制日期范围。
- 大表查询必须分页。
- 日线、周线、月线表必须建复合索引。
- 日志和历史任务支持清理。
- 回测结果支持删除或归档。
