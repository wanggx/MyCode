# -*- coding: utf-8 -*-
"""
通用数据访问基类：分页查询辅助
"""


def paginate_sql(base_sql, count_sql, params, page, page_size, cursor):
    """
    执行分页查询

    Args:
        base_sql: 数据查询 SQL（不含 LIMIT/OFFSET）
        count_sql: 计数 SQL
        params: 查询参数列表
        page: 页码（从 1 开始）
        page_size: 每页条数
        cursor: 数据库 cursor

    Returns:
        dict: {items, total, page, page_size, total_pages}
    """
    cursor.execute(count_sql, params)
    total_row = cursor.fetchone()
    total = total_row["total"] if total_row and "total" in total_row else 0
    if isinstance(total_row, dict) and "total" not in total_row:
        total = list(total_row.values())[0] if total_row else 0

    offset = (page - 1) * page_size
    cursor.execute(base_sql + " LIMIT %s OFFSET %s", params + [page_size, offset])
    items = cursor.fetchall()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
    }
