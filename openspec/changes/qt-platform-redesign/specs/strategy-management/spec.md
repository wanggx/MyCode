# Specification (Delta): Strategy Management — 策略管理

## ADDED Requirements

### Requirement: 策略 CRUD

系统 SHALL 支持策略的创建、查询、更新和删除。

#### Scenario: 创建策略
- **GIVEN** 已认证用户
- **WHEN** 客户端发送 POST `/api/strategies`，body 含 `name="双均线趋势跟踪", description="基于快速均线和慢速均线交叉生成买卖信号", strategy_type="stock"`
- **THEN** 系统 SHALL 自动生成 `strategy_key`（从 name 转换拼音："shuang_jun_xian_qu_shi_gen_zong"）
- **AND** 系统 SHALL 在 strategy 表创建记录（status=draft, latest_version=0）
- **AND** 系统 SHALL 响应 HTTP 201

#### Scenario: 创建策略缺少名称
- **WHEN** 客户端发送 POST `/api/strategies` 缺少 `name`
- **THEN** 系统 SHALL 响应 HTTP 400

#### Scenario: 查询策略列表
- **WHEN** 客户端发送 GET `/api/strategies?page=1&page_size=20&status=active&keyword=均线`
- **THEN** 系统 SHALL 响应 HTTP 200，返回分页列表，每项含 `id, name, strategy_type, status, latest_version, last_backtest_status, last_backtest_return, updated_at`

#### Scenario: 查询策略详情
- **WHEN** 客户端发送 GET `/api/strategies/1`
- **THEN** 系统 SHALL 响应 HTTP 200，含策略详情及最新版本号

#### Scenario: 更新策略信息
- **WHEN** 客户端发送 PUT `/api/strategies/1`，body 含 `name="新名称"`
- **THEN** 系统 SHALL 更新名称并响应 HTTP 200

#### Scenario: 删除无回测记录的策略
- **GIVEN** strategy_id=1 没有任何关联的 backtest_job
- **WHEN** 客户端发送 DELETE `/api/strategies/1`
- **THEN** 系统 SHALL 删除策略及其所有版本
- **AND** 系统 SHALL 响应 HTTP 200

#### Scenario: 删除有回测记录的策略
- **GIVEN** strategy_id=1 存在关联的 backtest_job 记录
- **WHEN** 客户端发送 DELETE `/api/strategies/1`
- **THEN** 系统 SHALL 响应 HTTP 409，提示需先删除所有回测记录

#### Scenario: 修改策略状态
- **WHEN** 客户端发送 PATCH `/api/strategies/1/status`，body 含 `status="archived"`
- **THEN** 系统 SHALL 更新策略状态并响应 HTTP 200

### Requirement: 策略版本管理

系统 SHALL 支持策略源码的多版本存储和查询。

#### Scenario: 创建策略版本
- **GIVEN** strategy_id=1 当前 latest_version=0
- **WHEN** 客户端发送 POST `/api/strategies/1/versions`，body 含 `source_code="def init(context):\n    ...", change_log="初始版本"`
- **THEN** 系统 SHALL 创建 version=1 的记录
- **AND** 系统 SHALL 更新 strategy.latest_version=1
- **AND** 系统 SHALL 响应 HTTP 201

#### Scenario: 版本号递增
- **GIVEN** strategy_id=1 latest_version=3
- **WHEN** 客户端再次 POST `/api/strategies/1/versions`
- **THEN** 系统 SHALL 创建 version=4 的记录

#### Scenario: 查询版本列表
- **WHEN** 客户端发送 GET `/api/strategies/1/versions`
- **THEN** 系统 SHALL 返回该策略所有版本的列表（version, change_log, status, created_at）

#### Scenario: 查询版本源码
- **WHEN** 客户端发送 GET `/api/strategies/1/versions/3`
- **THEN** 系统 SHALL 返回该版本的完整 source_code

#### Scenario: 策略 key 用于日志目录
- **GIVEN** strategy_key="double_ma"
- **WHEN** 回测引擎为 backtest_id=128 写入日志
- **THEN** 日志文件路径 SHALL 为 `logs/double_ma/128.log`

### Requirement: 策略代码在线编辑

前端 SHALL 提供 Monaco Editor 供用户在线编辑 Python 策略代码。

#### Scenario: 打开代码编辑器
- **GIVEN** 用户在策略研究页面
- **WHEN** 用户点击「编辑代码」按钮
- **THEN** Monaco Editor SHALL 进入编辑模式（可输入代码）
- **AND** 右侧配置面板 SHALL 显示策略参数

#### Scenario: 保存代码（Ctrl+S）
- **GIVEN** 用户在编辑模式中修改了代码
- **WHEN** 用户按下 Ctrl+S（或 Cmd+S）
- **THEN** 前端 SHALL 调用 `POST /api/strategies/:id/versions` 保存为新版本
- **AND** SHALL 提示「代码已保存」

#### Scenario: 代码语法高亮
- **GIVEN** Monaco Editor 已加载
- **WHEN** 用户输入 Python 代码
- **THEN** 编辑器 SHALL 显示 Python 语法高亮（关键字、字符串、注释、函数名）
