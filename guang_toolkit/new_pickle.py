# -*- coding: utf-8 -*-
# @Time    : 2019/4/8 12:54 PM
# @Author  : 章光辉
# @FileName: my_pickle.py
# @Software: PyCharm

import pickle
import logging

logger = logging.getLogger(__name__)


def pickle_dump(obj, file_path):
    with open(file_path, "wb") as f:
        return pickle.dump(obj, PickleFile(f), protocol=pickle.HIGHEST_PROTOCOL)


def pickle_load(file_path):
    with open(file_path, "rb") as f:
        return pickle.load(PickleFile(f))


class PickleFile:
    """
    针对pickle存在单个文件存储上限的问题，进一步优化和封装
    """

    def __init__(self, f):
        self.f = f

    def __getattr__(self, item):
        return getattr(self.f, item)

    def read(self, n):
        # logger.debug("reading total_bytes=%s" % n, flush=True)
        if n >= (1 << 31):
            buffer = bytearray(n)
            idx = 0
            while idx < n:
                batch_size = min(n - idx, 1 << 31 - 1)
                # logger.debug("reading bytes [%s,%s)..." % (idx, idx + batch_size),
                #       end="", flush=True)
                buffer[idx:idx + batch_size] = self.f.read(batch_size)
                # logger.debug("done.", flush=True)
                idx += batch_size
            return buffer
        return self.f.read(n)

    def write(self, buffer):
        n = len(buffer)
        logger.debug("writing total_bytes=%s..." % n, flush=True)
        idx = 0
        while idx < n:
            batch_size = min(n - idx, 1 << 31 - 1)
            logger.debug("writing bytes [%s, %s)... " % (idx, idx + batch_size), end="", flush=True)
            self.f.write(buffer[idx:idx + batch_size])
            logger.debug("done.", flush=True)
            idx += batch_size
