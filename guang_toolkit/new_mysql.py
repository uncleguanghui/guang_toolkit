# -*- coding: utf-8 -*-
# @Time    : 2019/3/30 4:05 PM
# @Author  : 章光辉
# @FileName: models.py
# @Software: PyCharm

import logging
import math

import mysql.connector
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, event
from sqlalchemy.exc import DisconnectionError
from sqlalchemy import Integer, VARCHAR, TEXT, DATETIME
from sqlalchemy.dialects.mysql import DOUBLE

try:
    from .basic import Basic
except (ImportError, ValueError):
    from guang_toolkit.basic import Basic

logger = logging.getLogger(__name__)


def checkout_listener(dbapi_con, con_record, con_proxy):
    """
    监听数据库连接
    :param dbapi_con:
    :param con_record:
    :param con_proxy:
    :return:
    """
    try:
        try:
            dbapi_con.ping(False)
        except TypeError:
            dbapi_con.ping()
    except dbapi_con.OperationalError as exc:
        if exc.args[0] in (2006, 2013, 2014, 2045, 2055):
            raise DisconnectionError()
        else:
            logger.error(con_record)
            logger.error(con_proxy)
            raise


class MySQL(Basic):
    def __init__(self,
                 path_config=None,
                 user_name=None,
                 password=None,
                 host=None,
                 port=None,
                 db_name=None):
        """
        初始化MySQL连接
        :param path_config: 数据库连接配置文件
        :param user_name: user_name
        :param password: password
        :param host: host
        :param port: port
        :param db_name: db_name
        """
        self.user_name = None
        self.password = None
        self.host = None
        self.port = None
        self.db_name = None
        self.set_input(keys=['user_name', 'password', 'host', 'port', 'db_name'],
                       values=[user_name, password, host, port, db_name],
                       path_config=path_config)

        self.url = f'mysql+pymysql://{self.user_name}:{self.password}@{self.host}:{self.port}/{self.db_name}'
        self.engine = create_engine(self.url, pool_size=10, pool_recycle=300, echo=False, max_overflow=5)
        event.listen(self.engine, 'checkout', checkout_listener)

    def execute_sql(self, sql):
        """
        支持一条sql语句里包括多条请求。多条请求之间用;分开。
        :param sql:
        :return:
        """
        cnx = mysql.connector.connect(host=self.host,
                                      user=self.user_name,
                                      password=self.password,
                                      database=self.db_name)
        cursor = cnx.cursor(buffered=True)

        # 虽然设置了multi为True，但是可能只包含一条select请求（只有一个返回）
        # 因此当只有一条返回结果时，取第一条。
        # 当某个请求只有一列返回结果时，对每行数据取第一个值
        results = []
        rows = 0
        for result in cursor.execute(sql, multi=True):
            if result.with_rows:
                rows += 1
                r = result.fetchall()
                if r and len(r[0]) == 1:
                    r = [i[0] for i in r]
                results.append(r)
        if rows == 1:
            results = results[0]

        try:
            cnx.commit()
        except:
            cnx.rollback()
        cursor.close()
        cnx.close()
        return results

    def read_sql_to_df(self, sql):
        """
        将sql语句的返回值转化为DataFrame
        :param sql:
        :return:
        """
        with self.engine.connect() as conn, conn.begin():
            return pd.read_sql(sql, con=conn)

    def truncate_table(self, table_name):
        """
        清空表
        :param table_name:
        :return:
        """
        with self.engine.connect() as conn, conn.begin():
            return conn.execute(f'truncate table {table_name}')

    def add_primary_key(self, table_name, primary_key):
        """
        设置主键
        :param table_name:
        :param primary_key:
        :return:
        """
        with self.engine.connect() as conn, conn.begin():
            return conn.execute(f'alter table {table_name} add primary key ({primary_key})')

    def to_sql(self, df, table_name, **kwargs):
        """
        将DataFrame保存到数据库中
        :param df:
        :param table_name:
        :return:
        """
        # 将object列的内容转换为字符串
        for c in df.select_dtypes(object).columns:
            df[c] = df[c].astype(str).replace('None', np.nan).replace('nan', np.nan)

        kwargs = kwargs.copy()
        dtype = kwargs.pop('dtype', None)
        if dtype is None:
            # 定义数据类型为这4者其一：Integer、DOUBLE、VARCHAR（TEXT）、DATETIME
            # 其中DOUBLE不指定精度时，会尽可能地保留全部
            # 当字符串最大长度超过1000时，会被保存为TEXT
            dtype = {}
            for c in df.columns:
                if str(df[c].dtype) == 'int64':
                    dtype[c] = Integer
                elif str(df[c].dtype) == 'float64':
                    dtype[c] = DOUBLE
                elif str(df[c].dtype) == 'datetime64[ns]':
                    dtype[c] = DATETIME
                elif str(df[c].dtype) == 'object':
                    max_len = df[c].astype(str).apply(len).max()
                    if max_len > 1024:
                        dtype[c] = TEXT
                    else:
                        max_len = 2 ** math.ceil(np.log2(max_len))
                        dtype[c] = VARCHAR(max_len)
                else:
                    logger.debug(f'未知数据类型: {c}:{type(str(df[c].dtype))}')

        with self.engine.connect() as conn, conn.begin():
            if_exists = kwargs.pop('if_exists', 'append')
            chunksize = kwargs.pop('chunksize', 100000)
            index = kwargs.pop('index', False)
            df.to_sql(table_name, con=conn, index=index, if_exists=if_exists,
                      chunksize=chunksize, dtype=dtype, **kwargs)
