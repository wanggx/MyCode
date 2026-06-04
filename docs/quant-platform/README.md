# 轻量量化投研平台技术方案

本目录保存轻量量化投研平台的技术设计文档，供后续 Agent 继续拆分任务和落地实现。

## 前提

这是个人项目，不按商业量化平台的重型架构设计。当前目标是：

- 单体服务
- 单机部署
- MySQL 主存储
- Flask 后端
- Vue 前端
- 数据任务串行或低并发执行
- 不引入 Redis、Kafka、Airflow、Celery、ClickHouse、Kubernetes 等组件

## 文档

- `architecture.md`: 总体架构方案。
- `modules.md`: 各功能模块技术方案。
- `data-health.md`: 数据健康诊断与修复闭环方案。
- `database-draft.md`: 数据库表设计草案。
- `implementation-roadmap.md`: 分阶段落地路线。

## 推荐实现顺序

1. 数据健康中心
2. 任务中心
3. 策略参数化与信号解释
4. 日频回测
5. 模拟组合与风控
6. 因子实验室增强

## UI 原型

推荐原型入口：

```text
prototype/quant-prototype-v2.html
```

该原型对应完整导航：

1. 总览
2. 数据中心
3. 因子实验室
4. 策略工作台
5. 回测中心
6. 选股信号
7. 组合风控
8. 任务中心
9. 系统设置
