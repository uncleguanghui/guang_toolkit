# -*- coding: utf-8 -*-
# @Time    : 2019/5/20 16:22 PM
# @Author  : 章光辉
# @FileName: s3.py
# @Software: PyCharm

import io
import socket
import logging
from pathlib import Path

import pandas as pd
import boto3

try:
    from .basic import Basic
except (ImportError, ValueError):
    from guang_toolkit.basic import Basic

logger = logging.getLogger(__name__)


class S3(Basic):
    """
    AWS S3连接类
    """

    def __init__(self,
                 path_config=None,
                 access_key_id=None,
                 secret_access_key=None,
                 region=None,
                 endpoint_url=None,
                 bucket_name=None):
        """
        初始化S3连接
        :param path_config: 连接配置文件
        :param access_key_id: access_key_id
        :param secret_access_key: secret_access_key
        :param region: region
        :param endpoint_url: endpoint_url
        :param bucket_name: bucket_name
        """
        self.access_key_id = None
        self.secret_access_key = None
        self.region = None
        self.endpoint_url = None
        self.bucket_name = None
        self.set_input(keys=['access_key_id', 'secret_access_key', 'region', 'endpoint_url', 'bucket_name'],
                       values=[access_key_id, secret_access_key, region, endpoint_url, bucket_name],
                       path_config=path_config)

        self.s3_resource = boto3.resource(
            service_name='s3',
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            endpoint_url=self.endpoint_url
        )
        self.s3_client = boto3.client(
            service_name='s3',
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            endpoint_url=self.endpoint_url
        )
        logger.info("Amazon S3连接成功")

    def get(self, url, suffix='.csv'):
        """
        拉取S3数据
        :param url:
        :param suffix: 文件名后缀
        :return:
        """
        suffix = Path(url).suffix or suffix
        assert suffix in ('.csv', '.parquet'), f'不支持{suffix}后缀'

        list_df = []
        files = self.get_valid_files(url, suffix=suffix)
        for file in files:
            try:
                obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=file)
                if suffix == '.csv':
                    df = pd.read_csv(io.BytesIO(obj['Body'].read()), error_bad_lines=False)
                else:
                    df = pd.read_parquet(io.BytesIO(obj['Body'].read()))
                list_df.append(df)
            except socket.timeout:
                logger.error("S3连接超时")
            except IOError as err:
                logger.error(f"读取文件失败{err}")
            except Exception as err:
                logger.error(str(err))

        # 如果后缀是.csv，则返回一个DataFrame，否则返回一个list
        if len(list_df):
            return pd.concat(list_df, sort=False)
        else:
            return None

    def get_valid_files(self, url, suffix='.csv'):
        """
        检查文件是否有效，有效的定义：
        1、有指定后缀的文件
        2、文件非空
        :param url:
        :param suffix: 文件名后缀
        :return:
        """
        suffix = Path(url).suffix or suffix
        assert suffix in ('.csv', '.parquet'), f'不支持{suffix}后缀'

        results = []
        for item in self.s3_resource.Bucket(self.bucket_name).objects.filter(Prefix=url):
            if item.key.endswith(suffix):
                results.append(item.key)

        if len(results) == 0:
            logger.warning(f'{url}不存在')

        files = []
        for result in results:
            obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=result)
            valid = obj['ContentLength'] != 0
            if valid:
                files.append(result)

        return files

    def set(self, df: pd.DataFrame, url):
        """
        写数据到S3
        """
        suffix = Path(url).suffix
        assert suffix != '', 'url为文件路径，需包含.csv或.parquet后缀'
        assert suffix in ('.csv', '.parquet'), f'不支持{suffix}后缀'
        if suffix == '.parquet':
            parquet_buffer = io.BytesIO()
            df.to_parquet(parquet_buffer, index=False)
            self.s3_resource.Object(self.bucket_name, url).put(Body=parquet_buffer.getvalue())
        else:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, header=True, index=False)
            self.s3_resource.Object(self.bucket_name, url).put(Body=csv_buffer.getvalue())

    def upload_file(self, local_path, url):
        """
        上传文件到S3
        :param local_path:
        :param url:
        :return:
        """
        try:
            self.s3_resource.meta.client.upload_file(local_path, self.bucket_name, url)
        except Exception as e:
            print(e)

    def download_file(self, url, local_path):
        """
        从S3上下载文件
        :param url:
        :param local_path:
        :return:
        """
        try:
            self.s3_resource.meta.client.download_file(self.bucket_name, url, local_path)
        except Exception as e:
            print(e)
