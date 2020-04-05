# -*- coding: utf-8 -*-
# @Time    : 2019/5/17 1:33 PM
# @Author  : 章光辉
# @FileName: plot.py
# @Software: PyCharm

import logging

import pandas as pd
import requests
import numpy as np
from shapely.geometry import Polygon

logger = logging.getLogger(__name__)


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


class China:
    def __init__(self):
        self.dict_adcode = {}  # {adcode：详情}
        self.dict_name = {}  # {名称：详情}
        self.districts = []  # 地区列表

        self.dict_polylines = {}  # 各地区的边界坐标（用于缓存数据）

        self.update_districts()  # 更新行政区划

    def update_districts(self):
        """
        更新行政区划
        :return:
        """
        url = f'https://restapi.amap.com/v3/config/district'
        data = {
            'keywords': '中国',
            'key': '87a08092f3e9c212e6f06e6327d9f385',
            'subdistrict': 3,  # 返回下级行政区
            'extensions': 'base',
            'offset': 1  # 只返回一条结果
        }
        country = requests.get(url, params=data).json()['districts'][0]
        self.dict_adcode[country['adcode']] = country
        self.dict_name[country['name']] = country
        self.dict_name['中国'] = country

        self.districts = country['districts']

        for province in self.districts:
            self.dict_adcode[province['adcode']] = province
            for city in province['districts']:
                self.dict_adcode[city['adcode']] = city
                for district in city['districts']:
                    self.dict_adcode[district['adcode']] = district

        for province in self.districts:
            self.dict_name[province['name']] = province
            for city in province['districts']:
                self.dict_name[city['name']] = city
                for district in city['districts']:
                    self.dict_name[district['name']] = district

    def _get_matched_adcode(self, adcode_or_name):
        """
        获取最匹配的adcode
        :param adcode_or_name:
        :return:
        """
        adcode_or_name = str(adcode_or_name)
        if adcode_or_name.isdigit():
            if adcode_or_name in self.dict_adcode:
                return adcode_or_name
        else:
            max_num = 0  # 所有名称里，从首字符开始的最长相同长度的最大值
            matched_adcode = None  # 最匹配的adcode
            for name, info in self.dict_name.items():
                # 找到从首字符开始的最长相同长度num
                num = 0
                for i, (s1, s2) in enumerate(zip(adcode_or_name, name)):
                    if s1 == s2:
                        num = i + 1
                    else:
                        break
                # 当前最长相同长度至少为2，且比之前找到的最长相同长度更长，则更新
                if num >= 2 and num > max_num:
                    max_num = num
                    matched_adcode = info['adcode']
            return matched_adcode

    def _get_all_subdistrict_adcode(self, adcode, subdistrict=0):
        """
        基于subdistrict的值，获取当前及所有下级行政区划的adcode
        :param adcode:
        :param subdistrict: 设置获取下级行政区级数的adcode，可选值为0/1/2/3，默认值为0，说明如下：
            0：不获取下级行政区；
            1：获取下一级行政区；
            2：获取下两级行政区；
            3：获取下三级行政区；
        :return:
        """
        adcode = str(adcode)

        list_adocde = []
        if subdistrict == 0:
            if self._get_matched_adcode(adcode) is not None:
                list_adocde.append(adcode)
        else:
            for p1 in self.dict_adcode[adcode]['districts']:
                if subdistrict == 1:
                    list_adocde.append(p1['adcode'])
                else:
                    for p2 in p1['districts']:
                        if subdistrict == 2:
                            list_adocde.append(p2['adcode'])
                        else:
                            for p3 in p2['districts']:
                                list_adocde.append(p3['adcode'])
        return list(set(list_adocde))

    def _get_polylines(self, adcode):
        """
        获取某个行政区划的边界坐标点
        :param adcode:
        :return:
        """
        adcode = str(adcode)

        # 先查询缓存
        polylines = self.dict_polylines.get(adcode)
        if polylines is None and self._get_matched_adcode(adcode) is not None:
            url = f'https://restapi.amap.com/v3/config/district'
            data = {
                'keywords': adcode,
                'key': '87a08092f3e9c212e6f06e6327d9f385',
                'subdistrict': 0,  # 返回下级行政区
                'extensions': 'all',
                'offset': 1  # 只返回一条结果
            }
            districts = requests.get(url, params=data).json()['districts']
            polylines = []
            if districts:
                for district in districts[0]['polyline'].split('|'):
                    borders = np.array([[float(i) for i in j.split(',')] for j in district.split(';')])
                    polylines.append(borders)
            self.dict_polylines[adcode] = polylines

        return polylines

    def get_all_polylines(self, adcode_or_name, subdistrict=0):
        """
        获取边境坐标点
        :param adcode_or_name:
        :param subdistrict: 设置获取下级行政区级数的边界，可选值为0/1/2/3，默认值为0，说明如下：
            0：不获取下级行政区；
            1：获取下一级行政区；
            2：获取下两级行政区；
            3：获取下三级行政区；
        :return:
        """
        adcode = self._get_matched_adcode(adcode_or_name)
        if adcode is None:
            print('找不到给定的行政区域')
            return []

        list_adcode = self._get_all_subdistrict_adcode(adcode, subdistrict)
        polylines = []
        for adcode in list_adcode:
            polylines += self._get_polylines(adcode)

        return polylines

    def plot(self, adcode_or_name, subdistrict=0, area_threshold=0.005):
        """
        可视化边境坐标点
        :param adcode_or_name:
        :param subdistrict: 设置绘制下级行政区级数，可选值为0/1/2/3，默认值为0，说明如下：
            0：不绘制下级行政区；
            1：绘制下一级行政区；
            2：绘制下两级行政区；
            3：绘制下三级行政区；
        :param area_threshold: 绘图阈值，面积小于该值的多边形将不再绘制在地图上，该参数用于加速绘图
        :return:
        """

        polylines = self.get_all_polylines(adcode_or_name, subdistrict)
        if polylines:
            import matplotlib.pyplot as plt

            plt.figure(figsize=(12, 12))
            for polyline in polylines:
                if Polygon(polyline).area > area_threshold:
                    plt.plot(polyline[:, 0], polyline[:, 1])
            plt.axis("equal")
            plt.show()
        else:
            print('找不到边界坐标，请确认 adcode 或名称是否正确，或者 subdistrict 设置过大')
