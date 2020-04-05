#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.command.clean import clean
import subprocess
import os
import shutil
import re

from setuptools.command.install import install
from setuptools.command.test import test
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


def get_version():
    with open('guang_toolkit/__init__.py', 'r') as file:
        version = '0.0.0'
        for line in file.readlines():
            results = re.findall("__version__ = '(.*)'", line.replace("\"", '\''))
            if results:
                version = results[0]
                break
    return version


class ActionOnInstall(install):
    def run(self):
        install.run(self)


class ActionOnTest(test):
    def run(self):
        test.run(self)


class CleanHook(clean):
    def run(self):
        clean.run(self)

        def maybe_rm(path):
            if os.path.exists(path):
                shutil.rmtree(path)

        maybe_rm('guang_toolkit.egg-info')
        maybe_rm('.pytest_cache')
        maybe_rm('build')
        maybe_rm('dist')
        maybe_rm('.eggs')
        maybe_rm('htmlcov')
        subprocess.call('rm -rf .coverage', shell=True)
        subprocess.call('rm -rf *.egg', shell=True)
        subprocess.call('rm -f datastore.db', shell=True)
        subprocess.call(r'find . -name "*.pyc" -exec rm -rf {} \;',
                        shell=True)


setup(
    name="guang_toolkit",  # 应用名
    version=get_version(),  # 版本号
    packages=find_packages(),  # 指定子目录的python包
    install_requires=[  # 依赖列表
        'pandas >= 0.24.2',
        'openpyxl >= 2.5.12',
        'numpy >= 1.16.3',
        'geopy >= 1.14.0',
        'urllib3 >= 1.21.1',
        'jinja2 >= 2.10.1',
        'pymysql >= 0.9.3',
        'redis >= 3.2.1',
        'SQLAlchemy >= 1.3.3',
        'requests >= 2.19.1',
        'cryptography >= 2.6.1',
        'python-dateutil >= 2.6',
        'xlrd >= 1.2.0',
        'pathlib >= 1.0.1',
        'shapely >= 1.6.4.post2',
        'flake8 >= 3.7.7',
        'mysql-connector-python >= 8.0.16',
        'matplotlib >= 3.0.3',
        'boto3 >= 1.9.137',
        'bs4 >= 0.0.1',
        'pypinyin >= 0.36.0',
        'pyarrow >= 0.16.0'
    ],
    tests_require=[
        'pytest >= 4.4.1',
        'pytest-cov >= 2.7.1',
        'pytest-pep8 >= 1.0.6',
        'pytest-flakes >= 4.0.0',
    ],
    include_package_data=True,  # 启用清单文件MANIFEST.in
    cmdclass={
        'clean': CleanHook,  # python setup.py clean 清理工作区
        'test': ActionOnTest,  # python setup.py test 测试
        'install': ActionOnInstall  # python setup.py install 安装
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: MacOS X",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Chinese (Simplified)",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
    ],
    # 其他描述信息
    author='guanghui.zhang',
    author_email='415558663@qq.com',
    description="python toolkit",
    keywords=['toolkit', 'mail', 'geohash', 'mysql', 'pickle', 's3', 'weather', 'china', 'amap', 'crawler'],
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    python_requires='>=3',
    license="MIT",
    url='https://github.com/uncleguanghui/guang_toolkit'
)
