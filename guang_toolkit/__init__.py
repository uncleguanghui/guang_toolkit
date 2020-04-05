from .func import load_config, desensitize_id, show_df_size, copy
from .amap import AMAPCrawler, in_china
from .mail import Mail, Mail163
from .new_mysql import MySQL
from .new_redis import Redis
from .logger import Logger
from .new_pickle import pickle_dump, pickle_load
from .geohash import (encode, decode, decode_exactly, bbox, neighbors, expand,
                      hash_neighbors_radius, neighbors_radius)
from .s3 import S3
from .weather import WeatherCrawler
from .plot import donut, China

__all__ = [
    'AMAPCrawler', 'in_china', 'Mail', 'Mail163', 'MySQL', 'Redis', 'Logger', 'pickle_dump', 'pickle_load',
    'encode', 'decode', 'decode_exactly', 'bbox', 'neighbors', 'expand', 'hash_neighbors_radius',
    'neighbors_radius', 'load_config', 'desensitize_id', 'show_df_size', 'copy',
    'donut', 'China',
    'S3', 'WeatherCrawler'
]
__version__ = '3.0.13'
__doc__ = """
github地址：https://github.com/uncleguanghui/guang_toolkit
"""
