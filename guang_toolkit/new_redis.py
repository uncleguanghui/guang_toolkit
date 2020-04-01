# -*- coding: utf-8 -*-
# @Time    : 2019/4/3 1:00 AM
# @Author  : 章光辉
# @FileName: redis.py
# @Software: PyCharm

from time import sleep
import logging
import pickle

import redis

logger = logging.getLogger(__name__)


def check_connection(func, max_try_index=6, sleep_time=10):
    """
    检测数据库连接的装饰器
    :param func:
    :param max_try_index: 最大连接次数
    :param sleep_time: 连接等待时长（秒）
    :return:
    """

    def ping(self, *args, **kwargs):
        # 尝试连接
        try_index = 0
        while try_index < max_try_index:
            try:
                self.ping()
                break
            except redis.ConnectionError:
                logger.error(f'redis 失去连接，等待{sleep_time}秒')
                try_index += 1
                sleep(sleep_time)
        if try_index == max_try_index:
            # sys.exit('连接失败，退出')
            pass

        return func(self, *args, **kwargs)

    return ping


class Redis(redis.StrictRedis):
    """
    针对Redis存在单个数据存储上限的问题，进一步优化和封装
    单个数据的bytes大小最大约512MB
    注意：请勿随意清空数据库！！！尤其是在生产环境上运行的数据库！！！
    """
    max_bytes = 2 ** 29 - 1

    def __init__(self, *args, **kwargs):
        pool = redis.ConnectionPool(*args, **kwargs)
        super().__init__(connection_pool=pool)

    def set(self, key, value, **kwargs):
        """重写set函数"""
        # 因为key的大小可能会变（导致sub_key的数量发生变化），所以先都删掉
        self.delete(key)
        sub_keys, sub_bytes_values = self.generate_sub_keys_values(key, value)
        for sub_key, sub_bytes_value in zip(sub_keys, sub_bytes_values):
            super().set(sub_key, sub_bytes_value, **kwargs)
            logger.debug(f'成功保存变量 {sub_key}')

    def get(self, key):
        """重写get函数"""
        if self.exists(key):
            result = super().get(key)
            try:
                return pickle.loads(result)
            except pickle.UnpicklingError:
                return result
        else:
            sub_keys = self.sub_keys(key)
            if sub_keys:
                # 对找到的key做升序，再合并
                sub_keys = sorted(sub_keys, key=lambda x: int(x.decode('utf-8').split('__')[-1]))
                result = pickle.loads(b''.join(self.mget(sub_keys)))
                return result

    def delete(self, *keys, specific=False):
        """
        重写delete函数
        :param keys:
        :param specific: 是否只删除指定的keys，默认会删除所有子key
        :return:
        """
        if specific:
            super().delete(*keys)
        else:
            sub_keys = sum([self.sub_keys(key) for key in keys], [])
            for sub_key in sub_keys:
                super().delete(sub_key)
                logger.debug(f'成功删除变量 {sub_key}')

    @staticmethod
    def sub_key(head, tail=''):
        """
        子key的字符串
        :param head:
        :param tail:
        :return:
        """
        return f'{head}__sub__{tail}'

    @check_connection
    def sub_keys(self, key):
        """
        尝试获取所有子key（由于文件内容太大，导致无法一次储存）
        :param key:
        :return:
        """
        if self.exists(key):
            return [key]
        else:
            # 正则匹配子key的头部字符串，获取所有子key
            match_str = f'{self.sub_key(key)}*'
            keys = []

            # .keys() 优点是返回全部的keys，缺点是可能会阻塞服务
            # .scan() 优点是它是增量迭代的，每次只会返回少量key，不会阻塞服务，缺点是无法避免在迭代过程中可能出现的数据动态生成
            # 当cursor为0时，代表完成了一次完整的遍历，所以可以停止了
            while True:
                cursor, ks = self.scan(match=match_str, count=10000)
                keys += ks
                if cursor == 0:
                    # 结束一次完整的遍历
                    break
            return list(set(keys))

    @check_connection
    def generate_sub_keys_values(self, key, value):
        bytes_value = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        value_len = len(bytes_value)

        # chunk_size==1代表不拆分
        chunk_size = (value_len - 1) // self.max_bytes + 1
        if chunk_size == 1:
            sub_keys = [key]
            sub_values = [bytes_value]
        else:
            sub_keys, sub_values = [], []
            for i, idx in enumerate(range(0, value_len, self.max_bytes)):
                sub_keys.append(self.sub_key(key, str(i)))
                sub_values.append(bytes_value[idx:(idx + self.max_bytes)])

        return sub_keys, sub_values


if __name__ == '__main__':
    # 测试
    import pandas as pd

    r = Redis(db=1)
    r.set('s1', pd.DataFrame([1, 2]))
    print(r.get('s1'))

    r.set('s2', bytearray(2 ** 30))
    print(len(r.get('s2')))

    r.delete('s1', 's2')
