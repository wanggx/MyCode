# 股票API使用指南

## 概述

股票API提供了从MySQL数据库中查询股票信息的功能，支持分页、搜索和筛选。

## 数据库表结构

```sql
CREATE TABLE `stock` (
  `ts_code` text COMMENT 'TS代码',
  `symbol` bigint DEFAULT NULL COMMENT '股票代码',
  `name` text COMMENT '股票名称',
  `area` text COMMENT '地域',
  `industry` text COMMENT '所属行业',
  `cnspell` text COMMENT '拼音缩写',
  `market` text COMMENT '市场类型（主板/创业板/科创板/CDR）',
  `list_date` bigint DEFAULT NULL COMMENT '上市日期',
  `act_name` text COMMENT '实控人名称',
  `act_ent_type` text COMMENT '实控人企业性质'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
```

## API接口

### 1. 获取股票列表

**接口地址**: `GET /api/stocks`

**请求参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认10，最大100）
- `keyword`: 搜索关键词（支持ts_code、symbol、name模糊搜索）
- `area`: 地域筛选
- `industry`: 行业筛选

**请求示例**:
```bash
curl -X GET "http://localhost:8080/api/stocks?page=1&page_size=10&keyword=银行" \
  -H "Authorization: Bearer <your_token>"
```

**响应示例**:
```json
{
  "message": "获取成功",
  "data": {
    "stocks": [
      {
        "ts_code": "000001.SZ",
        "symbol": "1",
        "name": "平安银行",
        "area": "深圳",
        "industry": "银行",
        "cnspell": "PAYH",
        "market": "主板",
        "list_date": "19910403",
        "act_name": "中国平安保险(集团)股份有限公司",
        "act_ent_type": "民营企业"
      }
    ],
    "total": 10,
    "page": 1,
    "page_size": 10,
    "total_pages": 1
  }
}
```

### 2. 获取地域列表

**接口地址**: `GET /api/stocks/areas`

**请求示例**:
```bash
curl -X GET "http://localhost:8080/api/stocks/areas" \
  -H "Authorization: Bearer <your_token>"
```

**响应示例**:
```json
{
  "message": "获取成功",
  "data": ["北京", "上海", "深圳", "浙江", "江苏", "四川", "贵州"]
}
```

### 3. 获取行业列表

**接口地址**: `GET /api/stocks/industries`

**请求示例**:
```bash
curl -X GET "http://localhost:8080/api/stocks/industries" \
  -H "Authorization: Bearer <your_token>"
```

**响应示例**:
```json
{
  "message": "获取成功",
  "data": ["银行", "房地产", "白酒", "科技", "汽车", "金融", "医药"]
}
```

## 使用场景

### 1. 基础查询
```bash
# 获取第一页数据，每页10条
curl -X GET "http://localhost:8080/api/stocks" \
  -H "Authorization: Bearer <your_token>"
```

### 2. 关键词搜索
```bash
# 搜索包含"银行"的股票
curl -X GET "http://localhost:8080/api/stocks?keyword=银行" \
  -H "Authorization: Bearer <your_token>"
```

### 3. 地域筛选
```bash
# 筛选深圳地区的股票
curl -X GET "http://localhost:8080/api/stocks?area=深圳" \
  -H "Authorization: Bearer <your_token>"
```

### 4. 行业筛选
```bash
# 筛选科技行业的股票
curl -X GET "http://localhost:8080/api/stocks?industry=科技" \
  -H "Authorization: Bearer <your_token>"
```

### 5. 组合查询
```bash
# 搜索深圳地区的科技股
curl -X GET "http://localhost:8080/api/stocks?area=深圳&industry=科技" \
  -H "Authorization: Bearer <your_token>"
```

### 6. 分页查询
```bash
# 获取第2页，每页5条数据
curl -X GET "http://localhost:8080/api/stocks?page=2&page_size=5" \
  -H "Authorization: Bearer <your_token>"
```

## 错误处理

### 常见错误码

- `401`: 未授权（token无效或过期）
- `500`: 服务器内部错误（数据库连接失败等）

### 错误响应示例
```json
{
  "error": "数据库连接失败"
}
```

## 性能优化

1. **分页查询**: 建议每页不超过100条数据
2. **索引优化**: 数据库已为常用查询字段创建索引
3. **连接池**: 使用数据库连接池提高性能

## 测试

运行测试脚本验证API功能：

```bash
cd stock/backend
python test_stock_api.py
```

## 注意事项

1. 所有接口都需要JWT认证
2. 关键词搜索支持模糊匹配
3. 地域和行业筛选支持精确匹配
4. 分页参数会自动验证和修正
5. 数据库连接失败时会返回错误信息 