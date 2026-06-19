# Specification (Delta): Stock Platform — 基础设施变更

## MODIFIED Requirements

### Requirement: 密码安全升级

系统 SHALL 使用 bcrypt 替代 MD5 进行密码哈希，并兼容旧密码的自动升级。

#### Scenario: 新用户注册使用 bcrypt
- **GIVEN** 系统配置 `PASSWORD_HASH=bcrypt`
- **WHEN** 新用户注册
- **THEN** 系统 SHALL 使用 bcrypt 哈希存储密码
- **AND** 密码 SHALL 不以 MD5 形式存储

#### Scenario: 旧 MD5 密码用户登录
- **GIVEN** 从旧系统迁移来的用户，密码字段为 MD5 哈希
- **WHEN** 用户使用正确密码登录
- **THEN** 系统 SHALL 先用 MD5 验证
- **AND** 验证通过后 SHALL 自动将密码升级为 bcrypt 哈希
- **AND** 系统 SHALL 更新数据库中该用户的密码字段

#### Scenario: 登录密码验证
- **GIVEN** 用户密码已为 bcrypt 哈希
- **WHEN** 用户登录
- **THEN** 系统 SHALL 使用 bcrypt 验证密码

### Requirement: 数据库切换

系统 SHALL 使用 `qt_dev` 数据库，通过 `.env` 的 `DB_NAME` 配置。

#### Scenario: 连接 qt_dev 数据库
- **GIVEN** `.env` 中 `DB_NAME=qt_dev`
- **WHEN** 系统启动
- **THEN** 所有数据库连接 SHALL 连接到 qt_dev 库
- **AND** 旧 `stock` 库 SHALL 不被修改

### Requirement: 健康检查增强

系统健康检查 SHALL 包含 rqalpha 和数据源状态。

#### Scenario: 健康检查返回增强信息
- **WHEN** 客户端发送 GET `/api/health`
- **THEN** 系统 SHALL 响应 HTTP 200
- **AND** body 含 `status="healthy"`, `rqalpha_version`, `data_source_status`

## REMOVED Requirements

### Requirement: 旧版回测模块

旧版 `/api/backtests` 路由（使用 mock 数据）SHALL 被移除，由新的 `backtest-center` 模块替代。

### Requirement: 旧版策略模块

旧版 `/api/strategies` 路由（使用 mock 数据）SHALL 被移除，由新的 `strategy-management` 模块替代。

### Requirement: 旧版信号模块

旧版 `/api/signals` 路由 SHALL 被移除（二期重新设计）。

### Requirement: 旧版组合模块

旧版 `/api/portfolio` 路由 SHALL 被移除（三期重新设计）。
