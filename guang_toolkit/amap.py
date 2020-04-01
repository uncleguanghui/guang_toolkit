# -*- coding: utf-8 -*-
# @Time    : 2019/3/30 9:57 PM
# @Author  : 章光辉
# @FileName: amap.py
# @Software: PyCharm

from multiprocessing import Manager
from multiprocessing.pool import ThreadPool
from time import sleep
import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.exceptions import HTTPError
import numpy as np
import pandas as pd

session = requests.session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

logger = logging.getLogger(__name__)


class AMAPCrawler:
    def __init__(self, keys: (list, tuple, str) = None):
        if keys is None:
            self.keys = ['87a08092f3e9c212e6f06e6327d9f385']
        else:
            if isinstance(keys, str):
                keys = [keys]
            self.keys = keys

    def geocode(self, address):
        """
        单个地址的地理编码
        :param address:地址，类型为字符串
        :return:坐标
        """
        result = {
            'location': None,
            'province': None,
            'city': None,
            'district': None,
            'count': 0,
            'address': address,
            'lng': None,
            'lat': None,
        }
        try:
            url = 'https://restapi.amap.com/v3/geocode/geo'
            params = {
                'address': address,
                'key': np.random.choice(self.keys),
            }
            res = _request(url, params)
            count = int(res.get('count'))
            if count:
                first_poi = res.get('geocodes')[0]
                location = tuple([float(i) for i in first_poi.get('location').split(',')])
                province = first_poi.get('province') or ''
                city = first_poi.get('city') or ''
                district = first_poi.get('district') or ''
                result.update({
                    'location': location,
                    'province': province,
                    'city': city,
                    'district': district,
                    'count': count,
                    'lng': location[0],
                    'lat': location[1],
                })
            else:
                logger.warning(f'geocode高德API没有返回结果: {address}')
        except Exception as e:
            logger.warning('geocode', address, e)

        return result

    def regeocode(self, location_or_lng: (tuple, list, str, float, int), lat: (float, int) = None):
        """
        单个坐标的逆地理编码
        :param location_or_lng:坐标，类型为字符串
        :param lat:坐标，类型为字符串
        :return:坐标
        """

        if lat is None:
            if isinstance(location_or_lng, (list, tuple)):
                location = location_or_lng
            elif isinstance(location_or_lng, str):
                location = tuple([float(i) for i in location_or_lng.split(',')])
            else:
                raise ValueError('坐标类型错误')
        else:
            location = (location_or_lng, lat)

        result = {
            'address': None,
            'province': None,
            'city': None,
            'district': None,
            'lng': None,
            'lat': None,
            'location': None,
            'adcode': None,
        }

        try:
            result.update({
                'lng': location[0],
                'lat': location[1],
                'location': location,
            })

            url = 'https://restapi.amap.com/v3/geocode/regeo'
            params = {
                'location': f'{location[0]},{location[1]}',
                'key': np.random.choice(self.keys),
            }
            res = _request(url, params)
            regeo_codes = res.get('regeocode')
            if regeo_codes:
                address = regeo_codes.get('formatted_address')
                addressComponent = regeo_codes.get('addressComponent', {})
                province = addressComponent.get('province')
                city = addressComponent.get('city') or province
                district = addressComponent.get('district')
                adcode = addressComponent.get('adcode')
                result.update({
                    'address': address,
                    'province': province,
                    'city': city,
                    'district': district,
                    'adcode': adcode,
                })
            else:
                logger.error(f'regeocode高德API没有返回结果: {location}')
        except Exception as e:
            logger.error(location, e)
        return result

    def __batch_geocode_new(self, location_list):
        """
        批量火星坐标(GCJ-02)逆解析为地址
        :param location_list: 坐标列表，每个元素的类型均为字符串
        :return:地址列表
        """
        address_list = run_thread_pool(location_list, self.regeocode, 10, split_params=False)
        columns_rename = {
            'province': 'provinces',
            'city': 'cities',
            'district': 'districts',
            'address': 'addresses',
            'adcode': 'adcodes',
        }
        results = pd.DataFrame(address_list).rename(columns=columns_rename).to_dict('list')
        return results

    def __batch_geocode_new_new(self, list_location_str, pool_size=10, step=400):
        """
        批量坐标逆解析（坐标一定要是有效的），每400个坐标合并成一组参数
        :param list_location_str: 坐标字符串构成的列表
        :param pool_size: 线程池大小
        :param step: 批量接口上限
        :return:
        """

        list_params = [list_location_str[i:(i + step)] for i in range(0, len(list_location_str), step)]
        results = run_thread_pool(list_params, self.__batch_400_regeocode, pool_size, split_params=False)
        adcodes, provinces, cities, districts, addresses = list(zip(*results))
        adcodes = sum(adcodes, [])
        provinces = sum(provinces, [])
        cities = sum(cities, [])
        districts = sum(districts, [])
        addresses = sum(addresses, [])
        return adcodes, provinces, cities, districts, addresses

    def __batch_400_regeocode(self, list_location_str, step=20):
        """
        调用高德的批量接口来解析坐标，最多解析20*20个坐标字符串
        :param list_location_str:
        :param step: 批量接口上限
        :return:
        """
        assert len(list_location_str) <= 400

        # 生成子请求的url
        def get_url(locs):
            return f'/v3/geocode/regeo?key={key}&batch=true&location=' + '|'.join(locs)

        # 整理出请求所需的url和params
        key = np.random.choice(self.keys)
        url_batch = f'https://restapi.amap.com/v3/batch&key={key}'
        locations = [list_location_str[i:(i + step)] for i in range(0, len(list_location_str), step)]
        params = {
            "ops": [{'url': get_url(ls)} for ls in locations]
        }

        def request_success(r, index, num):
            return sum([i['body']['infocode'] != '10000' for i in r]) == 0 or index > num

        # 有的时候，接口超时，但是会返回数据，这里要做校验，当infocode不为'10000'时再请求一次
        try_num = 5
        try_index = 0
        while True:
            results = _request(url_batch, params, 'post')
            try:
                if request_success(results, try_index, try_num):
                    break
            except (TypeError, KeyError) as e:
                logger.error(f'解析失败，再爬一次:{e}')
            try_index += 1
            sleep(1)

        # 从结果里提取数据
        def get_result(r, key1=None, key2=None):
            rs = sum([[j[key1] if key2 is None else j[key1][key2] for j in i['body']['regeocodes']] for i in r], [])
            return [r or None for r in rs]

        # 提取数据，如果有坐标落在国外，则会提取不到相应的数据，需要把这组数据都拆分。
        try:
            adcodes = get_result(results, 'addressComponent', 'adcode')
            provinces = get_result(results, 'addressComponent', 'province')
            cities = get_result(results, 'addressComponent', 'city')
            districts = get_result(results, 'addressComponent', 'district')
            addresses = get_result(results, 'formatted_address')
        except KeyError:
            dict_result = self.__batch_geocode_new(list_location_str)
            adcodes = [r or None for r in dict_result['adcodes']]
            provinces = [r or None for r in dict_result['provinces']]
            cities = [r or None for r in dict_result['cities']]
            districts = [r or None for r in dict_result['districts']]
            addresses = [r or None for r in dict_result['addresses']]
        return adcodes, provinces, cities, districts, addresses

    def batch_process_regeocode(self, list_location, pool_size=1):
        """
        批量坐标逆解析（包含对无效坐标的处理）
        :param list_location: 坐标字符串构成的列表
        :param pool_size: 线程池大小
        :return:
        """

        def get_location_str(lnglat):
            try:
                if isinstance(lnglat, str):
                    lng, lat = list(map(float, lnglat.split(',')))
                else:
                    lng, lat = lnglat
                if in_china(lng, lat):
                    location_str = f'{lng:.6f},{lat:.6f}'
                else:
                    location_str = None
            except (ValueError, TypeError):
                location_str = None
            return location_str

        list_location_str = [get_location_str(lnglat) for lnglat in list_location]
        df = pd.DataFrame(list_location_str, columns=['location_str'])
        rows = df['location_str'].notnull()
        adcodes, provinces, cities, districts, addresses = self.__batch_geocode_new_new(list(df[rows]['location_str']),
                                                                                        pool_size)
        df.loc[rows, 'adcodes'] = [i or np.nan for i in adcodes]
        df.loc[rows, 'provinces'] = [i or np.nan for i in provinces]
        df.loc[rows, 'cities'] = [i or np.nan for i in cities]
        df.loc[rows, 'districts'] = [i or np.nan for i in districts]
        df.loc[rows, 'addresses'] = [i or np.nan for i in addresses]

        # 修复直辖市（只有省名称，没有城市名称）：用省名称当做城市名称
        rows = df['provinces'].fillna('').str.endswith('市') & df['cities'].replace('nan', np.nan).isnull()
        df.loc[rows, 'cities'] = df.loc[rows, 'provinces']
        # 当省的最后一个字不为市时（省或其他情况），修复缺失值为区名称
        rows = ~df['provinces'].fillna('').str.endswith('市') & df['cities'].replace('nan', np.nan).isnull()
        df.loc[rows, 'cities'] = df.loc[rows, 'districts']

        # 处理数据，合并成一个字典
        df = df.drop(['location_str'], axis=1)
        dict_result = dict((k, [i if str(i) != 'nan' else None for i in v])
                           for k, v in df.to_dict('list').items())
        return dict_result

    def _batch_200_geocode(self, list_address_str, step=10):
        """
        调用高德的批量接口来解析坐标，最多解析20*10个地址
        :param list_address_str:
        :param step: 批量接口上限
        :return:
        """
        assert len(list_address_str) <= 200

        # 地址不能太长
        list_address_str = [add[:20] for add in list_address_str]

        # 生成子请求的url
        def get_url(adds):
            return f'/v3/geocode/geo?key={key}&batch=true&address=' + '|'.join(adds)

        # 整理出请求所需的url和params
        key = np.random.choice(self.keys)
        url_batch = f'https://restapi.amap.com/v3/batch&key={key}'
        addresses = [list_address_str[i:(i + step)] for i in range(0, len(list_address_str), step)]
        params = {
            "ops": [{'url': get_url(ls)} for ls in addresses]
        }

        # 有的时候，接口超时，但是会返回数据，这里要做校验，当infocode不为'10000'时再请求一次
        results = _request(url_batch, params, 'post')

        # 从结果里提取数据
        def get_result(r, key1=None, key2=None):
            rs = sum([[j[key1] if key2 is None else j[key1][key2] for j in i['body']['geocodes']] for i in r], [])
            return [r or None for r in rs]

        # 提取数据
        adcodes = get_result(results, 'adcode')
        provinces = get_result(results, 'province')
        cities = get_result(results, 'city')
        districts = get_result(results, 'district')
        locations = get_result(results, 'location')

        return adcodes, provinces, cities, districts, locations

    def _batch_geocode_new(self, list_address_str, pool_size=3, step=200):
        """
        批量地址解析（地址可以是无效的），每200个地址合并成一组参数
        :param list_address_str: 地址字符串构成的列表
        :param pool_size: 线程池大小
        :param step: 批量接口上限
        :return:
        """
        list_params = [list_address_str[i:(i + step)] for i in range(0, len(list_address_str), step)]
        results = run_thread_pool(list_params, self._batch_200_geocode, pool_size, split_params=False)
        adcodes, provinces, cities, districts, locations = list(zip(*results))
        adcodes = sum(adcodes, [])
        provinces = sum(provinces, [])
        cities = sum(cities, [])
        districts = sum(districts, [])
        locations = sum(locations, [])
        return adcodes, provinces, cities, districts, locations

    def batch_process_geocode(self, list_address_str, pool_size=1):
        """
        批量地址解析（包含对无效数据的处理）
        :param list_address_str: 坐标字符串构成的列表
        :param pool_size: 线程池大小
        :return:
        """

        def get_address_str(address_str):
            if isinstance(address_str, str):
                return address_str
            return None

        df = pd.DataFrame(list_address_str, columns=['address'])
        df['address_str'] = df['address'].apply(get_address_str)
        rows = df['address_str'].notnull()
        adcodes, provinces, cities, districts, locations = self._batch_geocode_new(list(df[rows]['address_str']),
                                                                                   pool_size)
        df.loc[rows, 'adcodes'] = adcodes
        df.loc[rows, 'provinces'] = provinces
        df.loc[rows, 'cities'] = cities
        df.loc[rows, 'districts'] = districts
        df.loc[rows, 'locations'] = locations

        # 修复城市名称：
        # 当省的最后一个字为市时（直辖市），修复缺失值为省名称
        rows = df['provinces'].fillna('').str.endswith('市') & df['cities'].isnull()
        df.loc[rows, 'cities'] = df.loc[rows, 'provinces']
        # 当省的最后一个字不为市时（省或其他情况），修复缺失值为区名称
        rows = ~df['provinces'].fillna('').str.endswith('市') & df['cities'].isnull()
        df.loc[rows, 'cities'] = df.loc[rows, 'districts']

        # 处理数据，合并成一个字典
        df = df.drop(['address', 'address_str'], axis=1)
        dict_result = dict((k, [i if str(i) != 'nan' else None for i in v])
                           for k, v in df.to_dict('list').items())
        return dict_result


def in_china(lng, lat):
    """
    粗略判断是否在中国
    :param lng: 经度
    :param lat: 纬度
    :return:
    """
    return (73 <= lng <= 136) & (18 <= lat <= 54)


def foo_process(p):
    param, job, key, return_dict, split_params, total_num = p
    if split_params:
        if isinstance(param, (list, tuple)) and len(param) > 0:
            r = job(*param)
        else:
            r = job()
    else:
        r = job(param)
    return_dict[key] = r


def run_thread_pool(params, job, pool_size=50, split_params=True):
    """
    多线程处理任务
    :param params: 每个线程的所需参数的的列表
    :param job: 任务函数
    :param pool_size: 线程池大小，默认50
    :param split_params: 是否拆分参数
    :return: 结果列表
    """
    manager = Manager()
    return_dict = manager.dict()
    total_num = len(params)

    def get_params(p):
        for key, param in enumerate(p):
            yield (param, job, key, return_dict, split_params, total_num)

    pool_size = min(pool_size, total_num)
    pool = ThreadPool(processes=pool_size)
    pool.map(foo_process, get_params(params))
    pool.close()

    list_result = [return_dict.get(i) for i in range(len(params))]

    return list_result


def _request(url, params=None, method='get', max_tries=10, **kwargs):
    """
    向服务器发送get或post请求
    :param url: 请求url，类型为字符串
    :param params: 参数，类型为字典
    :param method: 请求类型，'get' or 'post'
    :param max_tries: 最大请求次数
    :return: 字典格式的结果
    """

    try_num = 0
    while try_num < max_tries:
        try:
            headers = {
                'Content-Type': 'application/json',
            }

            if method == 'get':
                res = session.get(url, params=params, headers=headers, timeout=10, **kwargs).json()
            else:
                res = session.post(url, json=params, headers=headers, timeout=10, **kwargs).json()
            return res
        except HTTPError:
            try_num += 1
            logger.debug(f'尝试第{try_num}次')
            # sleep(1 * try_num)
    if try_num == max_tries:
        logger.debug(f'无法连接{url}')
        return {}
