# -*- coding: utf-8 -*-
# @Time    : 2019/4/1 7:55 PM
# @Author  : 章光辉
# @FileName: logger.py
# @Software: PyCharm

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import inspect


class Logger(logging.Logger):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(self,
                 logger_file=None,
                 console_level='info',
                 logfile_level=None,
                 console_fmt='%(asctime)-15s | %(levelname)-8s | %(filename)-30s[line:%(lineno)3d] | %(message)s',
                 logfile_fmt='%(asctime)-15s | %(levelname)-8s | %(filename)-30s[line:%(lineno)3d] | %(message)s',
                 date_fmt='%Y-%m-%d %H:%M:%S'):
        """
        将日志同时输出到控制台和文件中，并按照时间自动分割日志文件。
        :param logger_file: 输出文件名，如果为None，则在引用文件所在目录的temp文件夹内，用引用文件名生成log
        :param console_level: 控制台日志级别，若为None，则不输出到控制台
        :param logfile_level: 文件日志级别，若为None，则不输出到文件
        :param console_fmt: 控制台的日志格式，若为None，则不设定格式
        :param logfile_fmt: 日志文件的日志格式，若为None，则不设定格式
        :param date_fmt: 时间格式
        """
        # self.logger = logging.getLogger(__name__)
        super().__init__(__name__)

        # 输出到控制台
        if console_level is not None:
            console_handler = logging.StreamHandler()
            if console_fmt is not None:
                format_str = logging.Formatter(console_fmt, date_fmt)
                console_handler.setFormatter(format_str)
            console_handler.setLevel(self.level_relations.get(console_level.lower()))
            self.addHandler(console_handler)

        # 输出到日志（按照天分割日志文件）,保留30份
        self.logger_file = None
        if logfile_level is not None:
            # log文件名为生成实例的脚本的文件名
            path = Path(inspect.stack()[1][1]).absolute()
            dir_log = path.parent / 'log'
            if not dir_log.exists():
                dir_log.mkdir()
            # 如果没有指定log路径，则在引用脚本的路径下的log文件夹内生成
            if logger_file is None:
                self.logger_file = dir_log / f'{path.stem}.log'
            else:
                self.logger_file = Path(logger_file).absolute()

            # when: 时间间隔：S 秒、M 分、H 小时、D 天、W 每星期（interval==0时代表星期一）、midnight 每天凌晨
            # backCount: 备份文件的个数，如果超过这个个数，就会自动删除，0不删
            file_handler = TimedRotatingFileHandler(filename=str(self.logger_file), when='D', interval=1,
                                                    backupCount=30, encoding='utf-8')
            if logfile_fmt is not None:
                format_str = logging.Formatter(logfile_fmt, date_fmt)
                file_handler.setFormatter(format_str)
            file_handler.setLevel(self.level_relations.get(logfile_level.lower()))
            self.addHandler(file_handler)
