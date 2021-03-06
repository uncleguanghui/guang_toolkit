## v3.0.13 (2020-04-04)
* 修改了地理绘图模块，能够基于最新的行政区划绘图
* 增加可视化部分的单元测试

## v3.0.10 (2020-03-02)
* 修改了S3类的get函数返回结果：当为空时返回None，否则返回DataFrame
* 增加了对S3上的parquet文件的读取支持
* 增加了将DataFrame保存为S3上的parquet或csv文件的功能
* 增加了S3文件的上传与下载功能

## v3.0.10 (2020-03-02)
* 修改了S3类的get函数返回结果：当为空时返回None，否则返回DataFrame
* 增加了对S3上的parquet文件的读取支持
* 增加了将DataFrame保存为S3上的parquet或csv文件的功能
* 增加了S3文件的上传与下载功能

## v3.0.4 (2019-11-20)
* 增加了历史天气搜索函数

## v3.0.3 (2019-11-19)
* 增加了天气爬虫模块
* 优化了地理解析与逆解析模块：支持传递非字符串形式的坐标
* 修改了邮箱模块的相关参数（不兼容之前），并增加了对163邮箱的支持

## v2.0.14 (2019-10-23)
* 完善mysql模块的to_sql功能：支持自定义原生参数

## v2.0.10 (2019-06-04)
* 还是mysql模块的问题，修复了select返回值为空时的报错。

## v2.0.9 (2019-06-03)
* 返回mysql执行结果
* 优化mysql返回的值：当只有一列时，取每行第一个值；当只有一次select时，直接取该select的结果。

## v2.0.8 (2019-05-31)
* 修复了mysql执行多条语句时的commit问题（忽略异常）

### v2.0.7 (2019-05-31)
* 将import matplotlib隐藏在函数里，避免在命令行导入模块时无法成功导入
* 修复了初始化S3类时没有默认项的问题
* 增加了S3下载数据前的检查功能
* 优化S3下载数据体验：url为文件时，返回一个DataFrame；url为路径时，返回一个DataFrame构成的list

### v2.0.6 (2019-05-21)
* 在__init__.py中添加新库
* 修复了donut绘图时的bug（缺少了value_counts）

### v2.0.5 (2019-05-20)
* 修复了可视化库matplotlib版本的错误问题（指定为3.0.3）

### v2.0.4 (2019-05-20)
* 增加了读取AWS S3数据的类
* 增加了可视化函数（环形图、中国可视化、省份可视化、城市可视化）

### v2.0.3 (2019-05-17)
* 修复了mysql的没有正确执行的bug（cnx.commit())

### v2.0.2 (2019-05-16)
* 修复了mysql的Unread result found错误: con.cursor(buffered=True)

### v2.0.1 (2019-05-16)
* 删除了连接mysql的warning

### v2.0.0 (2019-05-15)
* 重构项目，更加扁平化
* 取消了mysql执行时对错误的捕捉

### v1.0.8 (2019-05-15)
* 尝试修复import mysql的错误

### v1.0.7 (2019-05-15)
* 允许一次执行多条sql

### v1.0.6 (2019-05-12)
* 修正了读取redis数据(非pickle序列化数据)的bug

### v1.0.5 (2019-05-08)
* 初始化`AMAPCrawler`实例时，在支持以列表形式传入keys的基础上，增加一个默认的AMap key，因此用户可以直接使用AMAPCrawler类
* 支持修改`AMAPCrawler`的`batch_process_regeocode`方法和`batch_process_geocode`方法的`pool_size`参数，来手动适应key的数量，满足海量爬虫需求

### v1.0.4 (2019-05-08)
* 修复了mysql读取配置文件时读不到db_name的bug

### v1.0.3 (2019-05-07)
* 取消读取版本号时open函数的errors参数
* 修复了python setup.py install 时的安装bug

### v1.0.1 (2019-05-06)
* 修复了邮件群发的bug

### v1.0.0 (2019-05-05)
* 提供初始版guang_toolkit