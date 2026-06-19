# -*- coding: utf-8 -*-
"""Phase 0: 创建 qt_dev 数据库表 + 从 stock 库迁移数据"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import load_settings
import pymysql

settings = load_settings()

def get_conn(db=None):
    return pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=db or settings.DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def execute_ddl():
    """创建 qt_dev 所有表"""
    conn = get_conn()
    cursor = conn.cursor()

    ddl_statements = [
        # 1. users
        """CREATE TABLE IF NOT EXISTS users (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            username    VARCHAR(64)  NOT NULL UNIQUE COMMENT '用户名',
            password    VARCHAR(256) NOT NULL COMMENT '密码（bcrypt hash）',
            email       VARCHAR(128) DEFAULT NULL COMMENT '邮箱',
            role        VARCHAR(32)  DEFAULT 'user' COMMENT '角色：admin/user',
            status      VARCHAR(16)  DEFAULT 'active' COMMENT '状态：active/disabled',
            created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表'""",

        # 2. stock_basic
        """CREATE TABLE IF NOT EXISTS stock_basic (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            ts_code         VARCHAR(16)  NOT NULL UNIQUE COMMENT '代码（000001.SZ）',
            symbol          VARCHAR(8)   NOT NULL COMMENT '简写（000001）',
            name            VARCHAR(64)  NOT NULL COMMENT '名称（平安银行）',
            area            VARCHAR(32)  DEFAULT NULL COMMENT '地区',
            industry        VARCHAR(64)  DEFAULT NULL COMMENT '行业',
            market          VARCHAR(16)  NOT NULL COMMENT '市场（SZ/SE/HK）',
            list_date       DATE         DEFAULT NULL COMMENT '上市日期',
            delist_date     DATE         DEFAULT NULL COMMENT '退市日期',
            exchange        VARCHAR(16)  DEFAULT 'SZSE' COMMENT '交易所（SZSE/SSE）',
            board_type      VARCHAR(32)  DEFAULT 'MainBoard' COMMENT '板块（MainBoard/GEM/KSH）',
            status          VARCHAR(16)  DEFAULT 'active',
            created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
            updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_ts_code (ts_code),
            INDEX idx_market (market),
            INDEX idx_industry (industry)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票基础信息'""",

        # 3. stock_daily
        """CREATE TABLE IF NOT EXISTS stock_daily (
            id          BIGINT AUTO_INCREMENT PRIMARY KEY,
            ts_code     VARCHAR(16)  NOT NULL COMMENT '股票代码',
            trade_date  DATE         NOT NULL COMMENT '交易日期',
            open        DOUBLE       DEFAULT NULL,
            high        DOUBLE       DEFAULT NULL,
            low         DOUBLE       DEFAULT NULL,
            close       DOUBLE       DEFAULT NULL,
            pre_close   DOUBLE       DEFAULT NULL,
            change_pct  DOUBLE       DEFAULT NULL COMMENT '涨跌幅(%)',
            vol         DOUBLE       DEFAULT NULL COMMENT '成交量（手）',
            amount      DOUBLE       DEFAULT NULL COMMENT '成交额（千元）',
            turnover    DOUBLE       DEFAULT NULL COMMENT '换手率(%)',
            created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uk_code_date (ts_code, trade_date),
            INDEX idx_trade_date (trade_date),
            INDEX idx_ts_code (ts_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='A股日线行情'""",

        # 4. strategy
        """CREATE TABLE IF NOT EXISTS strategy (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            user_id         INT          NOT NULL COMMENT '创建用户',
            name            VARCHAR(128) NOT NULL COMMENT '策略名称',
            description     TEXT         DEFAULT NULL COMMENT '策略描述',
            strategy_type   VARCHAR(32)  DEFAULT 'stock' COMMENT '策略类型：stock/future/index',
            status          VARCHAR(16)  DEFAULT 'draft' COMMENT '状态：draft/active/archived',
            latest_version  INT          DEFAULT 0 COMMENT '最新版本号',
            default_config  JSON         DEFAULT NULL COMMENT '默认回测配置',
            tags            JSON         DEFAULT NULL COMMENT '标签',
            strategy_key    VARCHAR(64)  NOT NULL UNIQUE COMMENT '策略标识（用于日志目录等）',
            created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
            updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_user (user_id),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略主表'""",

        # 5. strategy_version
        """CREATE TABLE IF NOT EXISTS strategy_version (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            strategy_id     INT          NOT NULL COMMENT '策略ID',
            version         INT          NOT NULL COMMENT '版本号（自增）',
            source_code     MEDIUMTEXT   NOT NULL COMMENT '策略源码（Python）',
            config          JSON         DEFAULT NULL COMMENT '该版本的配置快照',
            change_log      TEXT         DEFAULT NULL COMMENT '变更说明',
            status          VARCHAR(16)  DEFAULT 'active' COMMENT '状态：active/archived',
            created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uk_strategy_version (strategy_id, version),
            INDEX idx_strategy (strategy_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略版本表'""",

        # 6. backtest_job
        """CREATE TABLE IF NOT EXISTS backtest_job (
            id                  INT AUTO_INCREMENT PRIMARY KEY,
            user_id             INT          NOT NULL COMMENT '用户ID',
            strategy_id         INT          NOT NULL COMMENT '策略ID',
            strategy_version    INT          NOT NULL COMMENT '策略版本号',
            strategy_name       VARCHAR(128) DEFAULT NULL COMMENT '策略名称（冗余）',
            strategy_key        VARCHAR(64)  DEFAULT NULL COMMENT '策略标识（冗余，用于日志路径）',
            status              VARCHAR(16)  DEFAULT 'pending' COMMENT 'pending/running/completed/failed/cancelled',
            config              JSON         NOT NULL COMMENT '回测配置快照',
            progress            DOUBLE       DEFAULT 0 COMMENT '进度 0-100',
            `current_date`      DATE         DEFAULT NULL COMMENT '当前运行日期',
            total_return        DOUBLE       DEFAULT NULL COMMENT '总收益率',
            annualized_return   DOUBLE       DEFAULT NULL COMMENT '年化收益率',
            max_drawdown        DOUBLE       DEFAULT NULL COMMENT '最大回撤',
            sharpe_ratio        DOUBLE       DEFAULT NULL COMMENT '夏普比率',
            sortino_ratio       DOUBLE       DEFAULT NULL COMMENT '索提诺比率',
            win_rate            DOUBLE       DEFAULT NULL COMMENT '胜率',
            profit_loss_ratio   DOUBLE       DEFAULT NULL COMMENT '盈亏比',
            annual_volatility   DOUBLE       DEFAULT NULL COMMENT '年化波动率',
            alpha               DOUBLE       DEFAULT NULL COMMENT 'Alpha',
            beta                DOUBLE       DEFAULT NULL COMMENT 'Beta',
            final_value         DOUBLE       DEFAULT NULL COMMENT '最终资产总值',
            total_trades        INT          DEFAULT 0 COMMENT '总交易笔数',
            benchmark_return    DOUBLE       DEFAULT NULL COMMENT '基准收益率',
            excess_return       DOUBLE       DEFAULT NULL COMMENT '超额收益',
            start_time          DATETIME     DEFAULT NULL COMMENT '开始时间',
            end_time            DATETIME     DEFAULT NULL COMMENT '结束时间',
            duration_ms         INT          DEFAULT NULL COMMENT '耗时（毫秒）',
            error_message       TEXT         DEFAULT NULL COMMENT '错误信息',
            log_path            VARCHAR(256) DEFAULT NULL COMMENT '日志文件路径',
            created_at          DATETIME     DEFAULT CURRENT_TIMESTAMP,
            updated_at          DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_user (user_id),
            INDEX idx_strategy (strategy_id),
            INDEX idx_status (status),
            INDEX idx_created (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测任务表'""",

        # 7. backtest_nav
        """CREATE TABLE IF NOT EXISTS backtest_nav (
            id                BIGINT AUTO_INCREMENT PRIMARY KEY,
            backtest_id       INT     NOT NULL COMMENT '回测任务ID',
            trade_date        DATE    NOT NULL COMMENT '交易日期',
            unit_net_value    DOUBLE  NOT NULL COMMENT '单位净值',
            daily_return      DOUBLE  DEFAULT NULL COMMENT '日收益率',
            cumulative_return DOUBLE DEFAULT NULL COMMENT '累计收益率',
            benchmark_nav     DOUBLE  DEFAULT NULL COMMENT '基准净值',
            excess_return     DOUBLE  DEFAULT NULL COMMENT '超额收益',
            UNIQUE KEY uk_bt_date (backtest_id, trade_date),
            INDEX idx_backtest (backtest_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测净值曲线'""",

        # 8. backtest_trade
        """CREATE TABLE IF NOT EXISTS backtest_trade (
            id              BIGINT AUTO_INCREMENT PRIMARY KEY,
            backtest_id     INT          NOT NULL COMMENT '回测任务ID',
            ts_code         VARCHAR(16)  NOT NULL COMMENT '股票代码',
            symbol          VARCHAR(8)   DEFAULT NULL COMMENT '股票简称',
            buy_date        DATE         NOT NULL COMMENT '买入日期',
            sell_date       DATE         DEFAULT NULL COMMENT '卖出日期',
            buy_price       DOUBLE       NOT NULL COMMENT '买入价',
            sell_price      DOUBLE       DEFAULT NULL COMMENT '卖出价',
            quantity        INT          NOT NULL COMMENT '交易数量（股）',
            buy_amount      DOUBLE       NOT NULL COMMENT '买入金额',
            sell_amount     DOUBLE       DEFAULT NULL COMMENT '卖出金额',
            pnl             DOUBLE       DEFAULT NULL COMMENT '盈亏金额',
            pnl_pct         DOUBLE       DEFAULT NULL COMMENT '盈亏百分比',
            holding_days    INT          DEFAULT NULL COMMENT '持仓天数',
            sell_reason     VARCHAR(64)  DEFAULT NULL COMMENT '卖出原因：signal/stop_loss/stop_profit/end',
            INDEX idx_backtest (backtest_id),
            INDEX idx_bt_code (backtest_id, ts_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测交易记录'""",

        # 9. backtest_position
        """CREATE TABLE IF NOT EXISTS backtest_position (
            id              BIGINT AUTO_INCREMENT PRIMARY KEY,
            backtest_id     INT          NOT NULL COMMENT '回测任务ID',
            trade_date      DATE         NOT NULL COMMENT '交易日期',
            ts_code         VARCHAR(16)  NOT NULL COMMENT '股票代码',
            symbol          VARCHAR(8)   DEFAULT NULL COMMENT '股票简称',
            quantity        INT          NOT NULL COMMENT '持仓数量',
            market_value    DOUBLE       NOT NULL COMMENT '市值',
            weight          DOUBLE       NOT NULL COMMENT '权重(%)',
            cost            DOUBLE       NOT NULL COMMENT '成本价',
            current_price   DOUBLE       NOT NULL COMMENT '当前价',
            pnl             DOUBLE       DEFAULT NULL COMMENT '浮动盈亏',
            pnl_pct         DOUBLE       DEFAULT NULL COMMENT '浮动盈亏百分比',
            INDEX idx_backtest (backtest_id),
            INDEX idx_bt_date (backtest_id, trade_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测持仓快照'""",

        # 10. backtest_daily_metrics
        """CREATE TABLE IF NOT EXISTS backtest_daily_metrics (
            id                BIGINT AUTO_INCREMENT PRIMARY KEY,
            backtest_id       INT     NOT NULL COMMENT '回测任务ID',
            trade_date        DATE    NOT NULL COMMENT '交易日期',
            daily_return      DOUBLE  DEFAULT NULL COMMENT '当日收益率',
            cumulative_return DOUBLE DEFAULT NULL COMMENT '累计收益率',
            drawdown          DOUBLE  DEFAULT NULL COMMENT '当日回撤(%)',
            portfolio_value   DOUBLE  DEFAULT NULL COMMENT '当日组合总值',
            cash              DOUBLE  DEFAULT NULL COMMENT '当日现金',
            leverage          DOUBLE  DEFAULT NULL COMMENT '当日杠杆',
            turnover          DOUBLE  DEFAULT NULL COMMENT '当日换手率',
            UNIQUE KEY uk_bt_date (backtest_id, trade_date),
            INDEX idx_backtest (backtest_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测日度指标'""",

        # 11. backtest_risk_metrics
        """CREATE TABLE IF NOT EXISTS backtest_risk_metrics (
            id                  INT AUTO_INCREMENT PRIMARY KEY,
            backtest_id         INT     NOT NULL UNIQUE COMMENT '回测任务ID',
            max_drawdown        DOUBLE  DEFAULT NULL COMMENT '最大回撤(%)',
            max_drawdown_start  DATE    DEFAULT NULL COMMENT '最大回撤开始日',
            max_drawdown_end    DATE    DEFAULT NULL COMMENT '最大回撤结束日',
            max_drawdown_recovery DATE  DEFAULT NULL COMMENT '最大回撤恢复日',
            max_drawdown_days   INT     DEFAULT NULL COMMENT '最大回撤持续天数',
            annual_volatility   DOUBLE  DEFAULT NULL COMMENT '年化波动率',
            downside_volatility DOUBLE  DEFAULT NULL COMMENT '下行波动率',
            var_95              DOUBLE  DEFAULT NULL COMMENT '95% VaR（日）',
            cvar_95             DOUBLE  DEFAULT NULL COMMENT '95% CVaR（日）',
            calmar_ratio        DOUBLE  DEFAULT NULL COMMENT 'Calmar比率',
            information_ratio   DOUBLE  DEFAULT NULL COMMENT '信息比率',
            tracking_error      DOUBLE  DEFAULT NULL COMMENT '跟踪误差',
            avg_holding_days    DOUBLE  DEFAULT NULL COMMENT '平均持仓天数',
            max_consecutive_win INT     DEFAULT NULL COMMENT '最大连续盈利次数',
            max_consecutive_lose INT    DEFAULT NULL COMMENT '最大连续亏损次数',
            INDEX idx_backtest (backtest_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测风险指标'""",

        # 12. data_source
        """CREATE TABLE IF NOT EXISTS data_source (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            name        VARCHAR(32)  NOT NULL UNIQUE COMMENT '数据源名称',
            display_name VARCHAR(64) NOT NULL COMMENT '显示名称',
            status      VARCHAR(16)  DEFAULT 'active' COMMENT 'active/disabled',
            config      JSON         DEFAULT NULL COMMENT '配置（token等）',
            priority    INT          DEFAULT 0 COMMENT '优先级',
            created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据源配置'""",

        # 13. data_sync_log
        """CREATE TABLE IF NOT EXISTS data_sync_log (
            id          BIGINT AUTO_INCREMENT PRIMARY KEY,
            source      VARCHAR(32)  NOT NULL COMMENT '数据源',
            data_type   VARCHAR(32)  NOT NULL COMMENT '数据类型',
            trade_date  DATE         DEFAULT NULL COMMENT '同步日期',
            status      VARCHAR(16)  DEFAULT 'pending' COMMENT 'pending/running/completed/failed',
            total_count INT          DEFAULT 0,
            success_count INT        DEFAULT 0,
            fail_count  INT          DEFAULT 0,
            error_msg   TEXT         DEFAULT NULL,
            started_at  DATETIME     DEFAULT NULL,
            finished_at DATETIME     DEFAULT NULL,
            created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_source (source),
            INDEX idx_date (trade_date),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据同步日志'""",

        # 14. factor_def
        """CREATE TABLE IF NOT EXISTS factor_def (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            factor_code VARCHAR(64)  NOT NULL UNIQUE COMMENT '因子编码',
            factor_name VARCHAR(128) NOT NULL COMMENT '因子名称',
            category    VARCHAR(32)  DEFAULT NULL COMMENT '分类',
            description TEXT         DEFAULT NULL,
            params      JSON         DEFAULT NULL,
            status      VARCHAR(16)  DEFAULT 'active',
            created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='因子定义'""",

        # 15. factor_value
        """CREATE TABLE IF NOT EXISTS factor_value (
            id          BIGINT AUTO_INCREMENT PRIMARY KEY,
            factor_code VARCHAR(64)  NOT NULL COMMENT '因子编码',
            ts_code     VARCHAR(16)  NOT NULL COMMENT '股票代码',
            trade_date  DATE         NOT NULL COMMENT '交易日期',
            value       DOUBLE       DEFAULT NULL COMMENT '因子值',
            UNIQUE KEY uk_factor_code_date (factor_code, ts_code, trade_date),
            INDEX idx_code (ts_code),
            INDEX idx_date (trade_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='因子值'""",

        # 16. task_job
        """CREATE TABLE IF NOT EXISTS task_job (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            task_type   VARCHAR(32)  NOT NULL COMMENT '任务类型',
            status      VARCHAR(16)  DEFAULT 'pending' COMMENT 'pending/running/completed/failed/cancelled',
            params      JSON         DEFAULT NULL COMMENT '任务参数',
            priority    INT          DEFAULT 0,
            progress    DOUBLE       DEFAULT 0 COMMENT '进度 0-100',
            result      JSON         DEFAULT NULL COMMENT '执行结果',
            error_msg   TEXT         DEFAULT NULL,
            created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
            started_at  DATETIME     DEFAULT NULL,
            finished_at DATETIME     DEFAULT NULL,
            INDEX idx_status (status),
            INDEX idx_type (task_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务队列表'""",

        # 17. task_step
        """CREATE TABLE IF NOT EXISTS task_step (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            job_id      INT          NOT NULL COMMENT '任务ID',
            step_name   VARCHAR(128) NOT NULL COMMENT '步骤名称',
            status      VARCHAR(16)  DEFAULT 'pending',
            started_at  DATETIME     DEFAULT NULL,
            finished_at DATETIME     DEFAULT NULL,
            error_msg   TEXT         DEFAULT NULL,
            INDEX idx_job (job_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务步骤表'""",

        # 18. rqalpha_config
        """CREATE TABLE IF NOT EXISTS rqalpha_config (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            config_key  VARCHAR(64)  NOT NULL UNIQUE COMMENT '配置键',
            config_value JSON        NOT NULL COMMENT '配置值',
            description VARCHAR(256) DEFAULT NULL,
            updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='rqalpha 系统配置'""",
    ]

    for i, ddl in enumerate(ddl_statements):
        try:
            cursor.execute(ddl)
            print(f'  [{i+1}/18] 表创建成功')
        except Exception as e:
            print(f'  [{i+1}/18] 表创建失败: {e}')

    conn.commit()
    cursor.close()
    conn.close()
    print('DDL 执行完成\n')


def migrate_data():
    """从 stock 库迁移数据到 qt_dev"""
    src_conn = pymysql.connect(
        host=settings.DB_HOST, port=settings.DB_PORT,
        user=settings.DB_USER, password=settings.DB_PASSWORD,
        database='stock', charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    dst_conn = get_conn()
    src = src_conn.cursor()
    dst = dst_conn.cursor()

    # 1. 迁移 stock → stock_basic（全量）
    print('迁移 stock → stock_basic (全量)...')
    src.execute('SELECT * FROM stock')
    rows = src.fetchall()
    if rows:
        # 旧表字段映射到新表
        col_map = {
            'ts_code': 'ts_code', 'symbol': 'symbol', 'name': 'name',
            'area': 'area', 'industry': 'industry', 'market': 'market'
        }
        for row in rows:
            try:
                # 从 ts_code 推导 exchange 和 board_type
                ts_code = row.get('ts_code', '')
                if '.SZ' in str(ts_code):
                    exchange = 'SZSE'
                elif '.SH' in str(ts_code):
                    exchange = 'SSE'
                elif '.HK' in str(ts_code):
                    exchange = 'HKEX'
                else:
                    exchange = 'SZSE'

                symbol = str(row.get('symbol', ''))
                if exchange == 'SSE' and symbol.startswith('688'):
                    board_type = 'KSH'
                elif exchange == 'SZSE' and (symbol.startswith('300') or symbol.startswith('301')):
                    board_type = 'GEM'
                else:
                    board_type = 'MainBoard'

                # list_date 是 TEXT 类型，需要转换
                list_date_str = str(row.get('list_date', '')).strip()
                list_date = list_date_str if list_date_str and list_date_str != 'None' else None

                dst.execute('''
                    INSERT INTO stock_basic (ts_code, symbol, name, area, industry, market,
                        list_date, exchange, board_type, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
                ''', (
                    row.get('ts_code'), row.get('symbol'), row.get('name'),
                    row.get('area'), row.get('industry'), row.get('market'),
                    list_date, exchange, board_type
                ))
            except Exception as e:
                pass  # skip duplicates
        dst_conn.commit()
        print(f'  迁移了 {len(rows)} 条 stock → stock_basic 记录')
    else:
        print('  stock 源表为空，跳过')

    # 2. 迁移 stock_daily（近 6 个月）
    print('迁移 stock_daily (近 6 个月)...')
    src.execute("""
        SELECT * FROM stock_daily
        WHERE trade_date >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 6 MONTH), '%Y%m%d')
        ORDER BY trade_date ASC
    """)
    rows = src.fetchall()
    if rows:
        batch_size = 5000
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            for row in batch:
                try:
                    # trade_date 是 VARCHAR 'YYYYMMDD' 格式，需转 DATE
                    td = str(row.get('trade_date', '')).strip()
                    trade_date = f'{td[:4]}-{td[4:6]}-{td[6:8]}' if len(td) == 8 else None
                    if not trade_date:
                        continue

                    dst.execute('''
                        INSERT INTO stock_daily (ts_code, trade_date, open, high, low, close,
                            pre_close, change_pct, vol, amount)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        row.get('ts_code'), trade_date,
                        row.get('open'), row.get('high'), row.get('low'), row.get('close'),
                        row.get('pre_close'), row.get('pct_chg'),
                        row.get('vol'), row.get('amount')
                    ))
                except Exception:
                    pass
            dst_conn.commit()
            print(f'  已迁移 {min(i+batch_size, len(rows))}/{len(rows)} 条 stock_daily 记录')
        print(f'  共迁移 {len(rows)} 条 stock_daily 记录')
    else:
        print('  stock_daily 源表为空（近6个月无数据），跳过')

    # 3. 迁移 users（全量）
    print('迁移 users (全量)...')
    src.execute('SELECT * FROM users')
    rows = src.fetchall()
    if rows:
        for row in rows:
            try:
                # 旧 status 是 tinyint，转换为 VARCHAR
                old_status = row.get('status', 1)
                new_status = 'active' if old_status == 1 else 'disabled'

                # 密码保持原样（MD5），后续首次登录时自动升级为 bcrypt
                dst.execute('''
                    INSERT INTO users (id, username, password, email, role, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    row.get('id'), row.get('username'), row.get('password'),
                    row.get('email'), row.get('role', 'user'), new_status,
                    row.get('created_at'), row.get('updated_at')
                ))
            except Exception:
                pass  # skip duplicates
        dst_conn.commit()
        print(f'  迁移了 {len(rows)} 条 users 记录')
    else:
        print('  users 源表为空，跳过')

    # 4. 插入默认 data_source 配置
    print('插入默认 data_source 配置...')
    dst.execute("SELECT COUNT(*) as cnt FROM data_source")
    if dst.fetchone()['cnt'] == 0:
        dst.execute("""
            INSERT INTO data_source (name, display_name, status, config, priority)
            VALUES ('tushare', 'Tushare Pro', 'active', '{}', 10)
        """)
        dst.execute("""
            INSERT INTO data_source (name, display_name, status, config, priority)
            VALUES ('akshare', 'AKShare', 'active', '{}', 5)
        """)
        dst_conn.commit()
        print('  已插入 Tushare + AKShare 数据源')
    else:
        print('  data_source 已有数据，跳过')

    # 5. 插入默认 rqalpha_config
    print('插入默认 rqalpha_config...')
    dst.execute("SELECT COUNT(*) as cnt FROM rqalpha_config")
    if dst.fetchone()['cnt'] == 0:
        defaults = [
            ('commission', '{"stock": 0.0003}', '股票交易手续费率'),
            ('slippage', '{"stock": 0.01}', '滑点'),
            ('matching_type', '"current_bar"', '成交匹配方式'),
            ('default_benchmark', '"000300.XSHG"', '默认基准指数'),
            ('default_frequency', '"1d"', '默认回测频率'),
        ]
        for key, val, desc in defaults:
            dst.execute(
                'INSERT INTO rqalpha_config (config_key, config_value, description) VALUES (%s, %s, %s)',
                (key, val, desc)
            )
        dst_conn.commit()
        print('  已插入 5 条 rqalpha 默认配置')
    else:
        print('  rqalpha_config 已有数据，跳过')

    src.close(); src_conn.close()
    dst.close(); dst_conn.close()
    print('数据迁移完成\n')


def verify():
    """验证表创建和数据迁移"""
    conn = get_conn()
    cursor = conn.cursor()

    expected_tables = [
        'users', 'stock_basic', 'stock_daily',
        'strategy', 'strategy_version',
        'backtest_job', 'backtest_nav', 'backtest_trade', 'backtest_position',
        'backtest_daily_metrics', 'backtest_risk_metrics',
        'data_source', 'data_sync_log',
        'factor_def', 'factor_value',
        'task_job', 'task_step', 'rqalpha_config'
    ]

    cursor.execute('SHOW TABLES')
    actual_tables = [row[list(row.keys())[0]] for row in cursor.fetchall()]

    print('=== 验证结果 ===')
    for t in expected_tables:
        status = '✓' if t in actual_tables else '✗ MISSING'
        print(f'  {t}: {status}')

    # 数据量检查
    for table in ['stock_basic', 'stock_daily', 'users', 'data_source', 'rqalpha_config']:
        cursor.execute(f'SELECT COUNT(*) as cnt FROM {table}')
        cnt = cursor.fetchone()['cnt']
        print(f'  {table} 记录数: {cnt}')

    cursor.close(); conn.close()


if __name__ == '__main__':
    print('=== Phase 0: qt_dev 数据库初始化 ===\n')
    execute_ddl()
    migrate_data()
    verify()
    print('\nPhase 0 完成!')
