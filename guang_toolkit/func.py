# -*- coding: utf-8 -*-
# @Time    : 2019/3/31 11:27 AM
# @Author  : 章光辉
# @FileName: func.py.py
# @Software: PyCharm
# 一些小功能

import json
import sys
from pathlib import Path
import hashlib
from functools import wraps
import logging
from shutil import rmtree, copy2, copytree, move

logger = logging.getLogger(__name__)


def load_config(path_config, config_type='json'):
    """
    加载配置文件。
    如果不是绝对路径，则必须是在config目录下。
    必须是json文件，可以不指定后缀。
    :param path_config: Path变量或者是字符串。
    :param config_type: 配置文件类型，值为'json'时，返回字典；为'txt'时，返回字符串列表
    :return:
    """
    assert config_type in ('json', 'txt')

    # 转变类型
    if isinstance(path_config, str):
        path_config = Path(path_config)

    # 文件是否存在
    if not path_config.exists():
        raise FileNotFoundError(f'找不到配置文件: {str(path_config)}')

    # 读取配置文件
    if config_type == 'json':
        with open(path_config, 'rb') as f:
            params = json.load(f)
    else:
        with open(path_config, 'r') as f:
            params = [key.strip() for key in f.readlines()]
    return params


def desensitize_id(id_str):
    """
    对ID进行脱敏处理
    :param id_str:ID字符串
    :return:
    """
    # 左右部分互换后，替换两类字符，再md5加密
    name = (id_str[-10:] + id_str[:-10]).replace('a', 'z').replace('z', 'a')
    return hashlib.md5(name.encode('utf-8')).hexdigest()


def show_df_size(head_str=''):
    """
    打印df大小的装饰器
    :param head_str: 头部信息文字
    :return:
    """

    def new_fun(func):
        @wraps(func)
        def describe(*args, **kwargs):
            df = func(*args, **kwargs)
            size_mb = sys.getsizeof(df) / 2 ** 20
            logger.info(head_str + f'{len(df)}行，{size_mb:.1f}MB')
            return df

        return describe

    return new_fun


def copy(src, dst, cover=False, delete=False):
    """
    拷贝对象
    :param src:
    :param dst:
    :param cover: 是否覆盖
    :param delete: 当设为True的时候，拷贝模式改为move，即拷贝完以后删除原对象
    :return:
    """
    src = Path(src)
    dst = Path(dst)

    # 检查
    if not src.exists():
        logger.error('拷贝对象不存在')
        return

    same_name = src.name == dst.name
    if same_name:
        if dst.exists():
            # 是否强制覆盖
            if not cover:
                logger.error('目标对象已存在，若要强制覆盖，请将cover设为True')
                return
            else:
                if dst.is_file():
                    dst.unlink()
                else:
                    rmtree(dst)
    else:
        # 当不同名时，代表目标对象为文件夹，则需要先递归创建
        dst.mkdir(parents=True, exist_ok=True)

    # 拷贝或移动
    if delete:
        move(src, dst)
    else:
        if src.is_file():
            copy2(src, dst)
        else:
            copytree(src, dst)
