# -*- coding: utf-8 -*-
# @Time    : 2019/5/17 1:33 PM
# @Author  : 章光辉
# @FileName: plot.py
# @Software: PyCharm

import logging
from collections import defaultdict

import pandas as pd
import requests
import numpy as np

logger = logging.getLogger(__name__)

dict_map = defaultdict(dict)


def donut(data, title='', **kwargs):
    """
    画环装饼图来查看数据的分布
    :param data:
    :param title:
    :param kwargs:
    :return:
    """
    import matplotlib.pyplot as plt

    params = {
        'wedgeprops': {'linewidth': 7, 'edgecolor': 'white'},
        'autopct': '%1.0f%%'
    }
    if kwargs:
        params.update(kwargs)

    # 设置ax
    ax = kwargs.get('ax')
    if ax is None:
        fig, ax = plt.subplots(figsize=(4, 4), dpi=100)

    my_circle = plt.Circle((0, 0), 0.7, color='white')
    _data = pd.Series(data).value_counts().sort_values(ascending=False)
    ax.pie(_data.values, labels=_data.index, **params)
    p = plt.gcf()
    p.gca().add_artist(my_circle)
    plt.title(title)
    plt.axis('equal')
    return ax


def plot_china(show_province_name=False, **kwargs):
    """
    可视化全国
    :param show_province_name: 是否显示省名称，默认不显示
    :param kwargs: plt.line 参数
    :return:
    """

    dict_map_china = dict_map.get('china')

    if dict_map_china is None:
        dict_map_china = {}
        url = f'http://10.128.242.75:8007/api/geo/provinces'
        result = requests.get(url).json()

        for data in result['data']:
            adcode = data['adcode']
            try:
                dict_map_china[adcode] = {
                    'name': data['name'],
                    'polylines': [
                        np.array([
                            [float(x) for x in xy.split(',')]
                            for xy in polylines.split(';')
                        ])
                        for polylines in data['polyline'].split('|')
                    ]
                }
            except Exception as err:
                logger.warning(err)

        dict_map['china'] = dict_map_china

    # 设置ax
    ax = kwargs.pop('ax', None)
    if ax is None:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.set_aspect(1)

    for adcode, info in dict_map_china.items():
        if show_province_name:
            ax.text(*list(sorted(info['polylines'], key=lambda x: len(x))[-1].mean(axis=0)), info['name'], fontsize=8)
        # 画边界
        for border in info['polylines']:
            ax.plot(border[:, 0], border[:, 1], **kwargs)

    return ax


def plot_province(province_name=None, province_adcode=None, show_city_name=False, **kwargs):
    """
    可视化省份
    :param province_name: 省份名称
    :param province_adcode: 省份adcode
    :param show_city_name: 是否显示城市名称，默认不显示
    :param kwargs: plt.line 参数
    :return:
    """

    # 判断数据是否有效
    if province_name is None and province_adcode is None:
        logger.error('请指定省份名称或adcode!')
        return

    # 获取各城市边界
    def get_dict_city_info(cities):
        dict_city_info = {}
        for city in cities:
            _r = requests.get(f'http://10.128.242.75:8007/api/geo/city?name={city}').json()
            dict_city_info[city] = _r['data'][0]
            dict_city_info[city]['polylines'] = [
                np.array([
                    [float(x) for x in xy.split(',')]
                    for xy in polylines.split(';')
                ])
                for polylines in dict_city_info[city]['polyline'].split('|')
            ]
        return dict_city_info

    # 获取数据
    dict_province = dict_map['province'].get(province_adcode, dict_map['province'].get(province_name))
    if dict_province is None:
        if province_name is not None:
            r = requests.get(f'http://10.128.242.75:8007/api/geo/province?name={province_name}').json()
        else:
            r = requests.get(f'http://10.128.242.75:8007/api/geo/province?adcode={province_adcode}').json()
        if r['data']:
            df_province = pd.DataFrame(r['data'][0]['subdistricts'])
            province_name = r['data'][0]['name']
            province_adcode = r['data'][0]['adcode']
            list_city = list(df_province['city_name'].unique())

            # 获取边界
            dict_province = get_dict_city_info(list_city)

            # 保存数据
            dict_map['province'][province_adcode] = dict_map['province'][province_name] = dict_province
        else:
            logger.warning('找不到省份数据')
            dict_province = {}

    # 画城市边界
    if dict_province:
        # 设置ax
        ax = kwargs.pop('ax', None)
        if ax is None:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
        ax.set_aspect(1)

        for d_city in dict_province.values():
            # 显示城市名字
            if show_city_name:
                # 所有多边形的坐标的均值
                # center_lng, center_lat = np.concatenate(d_city['polylines']).mean(axis=0)
                # ax.text(center_lng, center_lat, d_city['name'], fontsize=8)
                # 最大多边形的坐标的均值
                ax.text(*list(sorted(d_city['polylines'], key=lambda x: len(x))[-1].mean(axis=0)), d_city['name'],
                        fontsize=8)
            # 画边界
            for border in d_city['polylines']:
                ax.plot(border[:, 0], border[:, 1], **kwargs)

        return ax


def plot_city(city_name=None, city_adcode=None, show_district_name=False, **kwargs):
    """
    可视化城市
    :param city_name: 城市名称
    :param city_adcode: 城市adcode
    :param show_district_name: 是否显示县区名称，默认不显示
    :param kwargs: plt.line 参数
    :return:
    """

    # 判断数据是否有效
    if city_name is None and city_adcode is None:
        logger.error('请指定城市名称或adcode!')
        return

    # 获取各城市边界
    def get_dict_district_info(district_adcodes):
        dict_district_info = {}
        for adcode in district_adcodes:
            url = f'http://10.128.242.75:8007/api/geo/district?adcode={adcode}'
            _r = requests.get(url).json()
            if _r['data']:
                dict_district_info[adcode] = _r['data'][0]
                dict_district_info[adcode]['polylines'] = [
                    np.array([
                        [float(x) for x in xy.split(',')]
                        for xy in polylines.split(';')
                    ])
                    for polylines in dict_district_info[adcode]['polyline'].split('|')
                ]
        return dict_district_info

    # 获取省份的各城市
    dict_city = dict_map['city'].get(city_name, dict_map['city'].get(city_adcode))
    if dict_city is None:
        if city_name is not None:
            r = requests.get(f'http://10.128.242.75:8007/api/geo/city?name={city_name}').json()
        else:
            r = requests.get(f'http://10.128.242.75:8007/api/geo/city?adcode={city_adcode}').json()

        if r['data']:
            df_city = pd.DataFrame(r['data'][0]['subdistricts'])
            city_name = r['data'][0]['name']
            city_adcode = r['data'][0]['adcode']
            list_district = list(df_city['district_adcode'].unique())

            # 获取边界
            dict_city = get_dict_district_info(list_district)

            # 保存数据
            dict_map['city'][city_name] = dict_map['city'][city_adcode] = dict_city
        else:
            logger.warning('找不到城市数据')
            dict_city = {}

    # 画城市边界
    if dict_city:
        # 设置ax
        ax = kwargs.pop('ax', None)
        if ax is None:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
        ax.set_aspect(1)

        # 画县区边界
        for d_district in dict_city.values():
            # 显示县区名字
            if show_district_name:
                # 所有多边形的坐标的均值
                # center_lng, center_lat = np.concatenate(d_district['polylines']).mean(axis=0)
                # ax.text(center_lng, center_lat, d_district['name'], fontsize=8)
                # 最大多边形的坐标的均值
                ax.text(*list(sorted(d_district['polylines'], key=lambda x: len(x))[-1].mean(axis=0)),
                        d_district['name'], fontsize=8)
            # 画边界
            for border in d_district['polylines']:
                ax.plot(border[:, 0], border[:, 1], **kwargs)

        return ax
