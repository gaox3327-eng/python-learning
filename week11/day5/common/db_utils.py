"""第 12 课：MySQL 工具（只给测试用）。

账号是只读+增删改的 tester，没有建表/删库权限。
"""
import pymysql

DB_CONF = dict(
    host="127.0.0.1",
    port=3306,
    user="tester",
    password="Test_2026",
    database="shop_test",
    charset="utf8mb4",
)


def connect():
    """autocommit=True 很关键。

    默认 autocommit=False 时，第一次 SELECT 会开启事务快照
    （MySQL 默认隔离级别 REPEATABLE READ），之后即使接口已经提交了改动，
    同一个连接也读不到 —— 表现为"接口改了库，但断言说没改"。
    """
    return pymysql.connect(autocommit=True, **DB_CONF)


def query(conn, sql, args=None):
    """查单个值：最常用的断言辅助。"""
    with conn.cursor() as cur:
        cur.execute(sql, args or ())
        row = cur.fetchone()
        return row[0] if row else None


def query_all(conn, sql, args=None):
    with conn.cursor() as cur:
        cur.execute(sql, args or ())
        return cur.fetchall()


def execute(conn, sql, args=None):
    """改数据用（造数/清理），记得提交。"""
    with conn.cursor() as cur:
        cur.execute(sql, args or ())
    conn.commit()
