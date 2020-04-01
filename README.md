# Guang-Toolkit 工具包

本项目为平时写的一些小工具，用于实现特定需求

## 目录

- [贡献指南](#贡献指南)
- [上手指南](#上手指南)
    * [环境要求](#环境要求)
    * [安装](#安装)
- [教程](#教程)
  * [天气爬虫](#天气爬虫)
  * [地址解析与逆解析](#地址解析与逆解析)
  * [地理哈希](#地理哈希)
  * [邮箱](#邮箱)
  * [MySQL数据库](#mysq数据库l)
  * [Redis数据库](#redis数据库)
  * [Pickle序列化](#pickle序列化)
  * [AWS S3](#aws-s3)
  * [可视化](#可视化)
- [License](#license)

## 贡献指南

欢迎一起来扩充本模块，请联系 415558663@qq.com 来加入开发者，并参照[贡献指南](https://github.com/uncleguanghui/guang_toolkit/blob/master/CONTRIBUTING.md)

## 上手指南

### 环境要求

python版本：3.6+


### 安装

```
pip install guang_toolkit
```

## 教程

首先，导入模块

```
import guang_toolkit as pdt
```

### 天气爬虫

首先初始化爬虫实例，

```
weather = pdt.WeatherCrawler()  # 初始化爬虫实例
```

实时天气

```
weather.get_real_time_weather('上海市')
>>>
{
    "24h降水": "0", 
    "aqi_pm25": "114", 
    "城市": "上海", 
    "城市编码": "101020100", 
    "天气": "晴", 
    "日期": "11月19日(星期二)", 
    "更新时间": "10:07", 
    "温度（华氏）": "50", 
    "温度（摄氏）": "10", 
    "湿度": "44%", 
    "风向": "东风", 
    "风速": "<12km/h"
}
```


未来一小段时间的天气预报（逐小时）

```
weather.get_hours_weather('上海市')
>>>
{
    "城市": "上海市", 
    "城市编码": "101020100", 
    "数据": [
        {
            "天气": "晴", 
            "日期": "2019111908", 
            "温度": "8", 
            "风向": "北风", 
            "风速": "3~4级"
        }, 
        ......
        {
            "天气": "晴", 
            "日期": "2019112007", 
            "温度": "10", 
            "风向": "北风", 
            "风速": "<3级"
        }
    ], 
    "更新时间": "07:30"
}
```

近7天天气预报（实际返回8天的结果，包括昨天）

```
weather.get_7d_weather('上海市')
>>>
{
    "城市": "上海市", 
    "城市编码": "101020100", 
    "数据": [
        {
            "天气": "小雨转多云", 
            "日期": "18日", 
            "日期标识": "昨天", 
            "最低温度": "6", 
            "最高温度": "12", 
            "风向": "西北风",
            "风速": "<3级"
        }, 
        ......
        {
            "天气": "阴转多云", 
            "日期": "25日", 
            "日期标识": "周一", 
            "最低温度": "12", 
            "最高温度": "15", 
            "风向": "东北风",
            "风速": "3-4级"
        }
    ], 
    "更新时间": "07:30"
}
```

近15天天气预报（实际返回16天的结果，包括昨天）

```
weather.get_15d_weather('上海市')
>>>
{
    "城市": "上海市", 
    "城市编码": "101020100", 
    "数据": [
        {
            "天气": "小雨转多云", 
            "日期": "18日", 
            "日期标识": "昨天", 
            "最低温度": "6", 
            "最高温度": "12", 
            "风向": "西北风",
            "风速": "<3级"
        }, 
        ......
        {
            "天气": "多云", 
            "日期": "3日", 
            "日期标识": "周二", 
            "最低温度": "7", 
            "最高温度": "11", 
            "风向": "北风",
            "风速": "3-4级转<3级"
        }
    ], 
    "更新时间": "07:30"
}
```

历史天气

```
weather.get_history_weather('上海市', '20190101')
>>>
{
    "url": "http://www.tianqihoubao.com/lishi/shanghai/20190101.html", 
    "城市": "上海市", 
    "天气": "阴/多云", 
    "日期": "20190101", 
    "温度": "6℃/2℃", 
    "风向风力": "北风 1-2级/北风 1-2级"
}
```

### 地址解析与逆解析

本模块用于POI的地址解析与逆解析（基于高德地图）

首先初始化地图实例，

```
crawler = pdt.AMAPCrawler() # 初始化地图实例
```

解析单个坐标（逆地理编码）
```
crawler.regeocode(121, 31)
>>>
{
    "adcode": "310118", 
    "address": "上海市青浦区练塘镇岳荡", 
    "city": "上海市", 
    "district": "青浦区", 
    "lat": 31, 
    "lng": 121, 
    "location": [
        121, 
        31
    ], 
    "province": "上海市"
}
```

解析单个地址（地理编码）
```
crawler.geocode('上海市嘉定区汽车创新港')
>>>
{
    "address": "上海市嘉定区汽车创新港", 
    "city": "上海市", 
    "count": 1, 
    "district": "嘉定区", 
    "lat": 31.27914, 
    "lng": 121.195122, 
    "location": [
        121.195122, 
        31.27914
    ], 
    "province": "上海市"
}
```

批量解析坐标
```
crawler.batch_process_regeocode([(121, 31), (116, 39)])
>>>
{
    "adcodes": [
        "310118", 
        "130632"
    ], 
    "addresses": [
        "上海市青浦区练塘镇岳荡", 
        "河北省保定市安新县大王镇334省道"
    ], 
    "cities": [
        "上海市", 
        "保定市"
    ], 
    "districts": [
        "青浦区", 
        "安新县"
    ], 
    "provinces": [
        "上海市", 
        "河北省"
    ]
}
```


批量解析地址
```
crawler.batch_process_geocode(['上海市嘉定区汽车创新港', '北京市故宫博物院'])
>>>
{
    "adcodes": [
        "310114", 
        "110101"
    ], 
    "cities": [
        "上海市", 
        "北京市"
    ], 
    "districts": [
        "嘉定区", 
        "东城区"
    ], 
    "locations": [
        "121.195122,31.279140", 
        "116.397026,39.918058"
    ], 
    "provinces": [
        "上海市", 
        "北京市"
    ]
}
```

### 地理哈希

地理哈希，简单的理解就是把地球表面切割成了一个个网格，精度越大，网格越小。

一个有效的坐标，在确定了精度的情况下，总能映射到某个确定的网格中，这个网格的编号就是哈希值。

PS：精度为7时，网格边长约150米（纬度不同，边长会有差异），已经可以满足大部分的分析需要。

初始化经度、纬度

```
lng = 121
lat = 31
```

查看地理哈希的精度及其误差范围

```
help(encode)
>>>
            precision |  longitude  |  latitude
               1      |  5009.4km   |  4992.6km
               2      |  1252.3km   |   624.1km
               3      |   156.5km   |     156km
               4      |    39.1km   |    19.5km
               5      |     4.9km   |     4.9km
               6      |     1.2km   |    609.4m
               7      |    152.9m   |    152.4m
               8      |     38.2m   |       19m
               9      |      4.8m   |      4.8m
               10     |      1.2m   |    59.5cm
               11     |    14.9cm   |    14.9cm
               12     |     3.7cm   |     1.9cm
                      |             |
            precision |  delta_lng  |  delta_lat
               1      |  360/2**3   |  180/2**2
               2      |  360/2**5   |  180/2**5
               3      |  360/2**8   |  180/2**7
               4      |  360/2**10  |  180/2**10
               5      |  360/2**13  |  180/2**12
               6      |  360/2**15  |  180/2**15
               7      |  360/2**18  |  180/2**17
               8      |  360/2**20  |  180/2**20
               9      |  360/2**23  |  180/2**22
               10     |  360/2**25  |  180/2**25
               11     |  360/2**28  |  180/2**27
               12     |  360/2**30  |  180/2**30
```

对坐标进行哈希编码，精确到7位（最大误差约150m）

```
pdt.encode(lat, lng, 7)
>>> 'wtw037m'
```

逆解析哈希值，返回（纬度，经度）

```
pdt.decode('wtw037m')
>>> (30.999984741210938, 120.99998474121094)
```

逆解析哈希值，并返回网格的边长（纬度，经度，纬度跨度，经度跨度）

```
pdt.decode_exactly('wtw037m')
>>> (30.999984741210938, 120.99998474121094, 0.0006866455078125, 0.0006866455078125)
```

查看哈希值的边界

```
pdt.bbox('wtw037m')
>>>
{
    "e": 121.00067138671875,  # 最大经度
    "n": 31.00067138671875,  # 最大纬度
    "s": 30.999298095703125,  # 最小纬度
    "w": 120.99929809570312  # 最小经度
}
```

查看周围相邻的8个哈希值

```
pdt.neighbors('wtw037m')
>>> ['wtw037k', 'wtw037q', 'wtw037s', 'wtw037t', 'wtw037w', 'wtw037h', 'wtw037j', 'wtw037n']
```

查找半径500米内、指定精度的所有哈希值

```
pdt.hash_neighbors_radius(lat, lng, radius_m=500, precision=7)
>>> 'wtw037q,wtw037g,wtw0376,wtw037y,wtw0374,wtw03e8,wtw037z,wtw03kh,wtw037n,wtw037t,wtw036v,wtw037x,wtw036w,wtw036y,wtw03e2,wtw03kj,wtw036s,wtw037p,wtw037w,wtw037h,wtw037e,wtw036z,wtw037r,wtw037u,wtw037f,wtw037d,wtw037v,wtw036t,wtw03kn,wtw0377,wtw037m,wtw03eb,wtw036g,wtw036f,wtw037j,wtw036u,wtw0375,wtw03db,wtw037s,wtw03e0,wtw037k'
```


### 邮箱

本模块用于发送邮件

首先初始化邮箱实例，

```
mail = pdt.Mail() # 初始化邮箱实例
```

设置签名（可选）
```
mail.set_signature(
    chinese_name='XXX',
    english_name='XX X',
    position='XXX',
    department='XXX',
    phone_number=XXXXX,
    english_company='XXX',
    chinese_company='XXX',
    chinese_address='XXX',
    english_address='XXX',
)
```

写邮件

```
mail.write_mail(
    receivers='邮箱地址',  # 若给多人发送则用list
    subject='主题', 
    text='内容',
    pathes_attachment=['附件的路径']
)
```

发邮件

```
mail.send_mail()
```

### MySQL数据库

本模块用于操作MySQL数据库，操作更加简单

首先初始化MySQL实例（通过账密），

```
mysql = pdt.MySQL(
    user_name='xxxx', 
    password='xxxx', 
    host='xxx', 
    port=3306, 
    db_name='xxxx'
) # 初始化MySQL实例
```

或者通过配置文件初始化，

```
mysql = pdt.MySQL(path_config='配置文件地址')
```

执行SQL并返回结果

```
mysql.execute_sql('show tables;')
```

执行SQL并将返回值转成DataFrame

```
df = mysql.read_sql_to_df('show tables;')
```

将DataFrame存到mysql里

```
mysql.to_sql(df, table_name)  # 支持传递更多参数，见pandas的df.to_sql函数
```

### Redis数据库

本模块用于操作Redis数据库，特点是：
* 继承自redis.StrictRedis，保留了redis的所有方法
* 利用连接池来分配、管理和释放数据库连接，提高操作性能
* 优化了大数据的set、get和delete方法

首先本地已经起了一个Redis服务，然后初始化Redis实例

```
redis = pdt.Redis(db=0)  # 初始化Redis实例
```

或者连接远程Redis，

```
redis = pdt.Redis(
    host=远程host, 
    port=远程port, 
    db=0
)
```

保存一个值，key为's'

```
redis.set('s', 1)
```

查看key为's'的数据

```
redis.get('s')
>>> 1
```

删除key为's'的数据

```
redis.delete('s')
```

### Pickle序列化

本模块用于磁盘存储数据，特点是：
* 基于pickle模块，默认用最高的协议（pickle.HIGHEST_PROTOCOL）
* 取消了pickle对于单个文件大小的限制，优化特大数据的存储


保存数据
```
pdt.pickle_dump(666, 'test.pkl')
```

读取数据

```
pdt.pickle_load('test.pkl')
>>> 666
```

### AWS S3

从S3上拉数据，get方法支持批量拉取数据和拉取特定数据

初始化S3实例，

```
s3 = pdt.S3(
    access_key_id='xxx', 
    secret_access_key='xxx', 
    region='xxx', 
    bucket_name='xxx', 
    endpoint_url='xxx'
)
```

或者通过配置文件初始化

```
s3 = pdt.S3(path_config='配置文件地址')
```

拉取某个文件（目前仅支持csv和parquet格式）

```
s3.get('aaa/bbb/ccc.csv')
s3.get('aaa/bbb/ccc.parquet')
```


拉取某个目录下的所有文件（目前仅支持csv和parquet格式）

```
s3.get('aaa/bbb/ccc', suffix='.csv')
s3.get('aaa/bbb/ccc', suffix='.parquet')
```

保存数据到S3上（目前仅支持csv和parquet格式）

```
s3.set(df, 'aaa/bbb/ccc.csv')
s3.set(df, 'aaa/bbb/ccc.parquet')
```

上传文件到S3上

```
s3.upload_file('local_path', 'remote_path')
```

下载文件到S3上

```
s3.download_file('remote_path', 'local_path')
```

### 可视化

提供了一些可视化的方法。同时也支持一些高级方法：
1. 自定义地图样式：通过在函数里传入plt.plot所需的参数，如`plot_province('浙江省', color='#00BCBC')`；
1. 支持传入ax参数，如`plot_province('浙江省', ax=ax)`，方便控制图层；
1. 函数本身也返回了ax，方便控制图层

环状分布图

```
pdt.donut([1, 1, 2, 1])
```

可视化中国

```
pdt.plot_china()
```

可视化某个省份

```
pdt.plot_province('浙江省')
```

可视化某个城市

```
pdt.plot_city('苏州市')
```

## License

[MIT](http://opensource.org/licenses/MIT)