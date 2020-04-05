import pytest
from guang_toolkit.plot import China
import warnings

warnings.filterwarnings('ignore')


@pytest.fixture(scope='module')
def china():
    return China()


def test_amap_data(china):
    # 测试有数据
    assert len(china.dict_adcode) > 0
    assert len(china.dict_name) > 0
    assert len(china.districts) > 0


def test_matched_adcode(china):
    # 测试匹配到的adcode
    assert china._get_matched_adcode(3101000) is None
    assert china._get_matched_adcode(310100) == '310100'
    assert china._get_matched_adcode('310100') == '310100'
    assert china._get_matched_adcode('xxxxxxxx') is None
    assert china._get_matched_adcode('上海市啦啦啦啦') == '310000'


def test_all_subdistrict_adcode(china):
    # 测试获取所有的下N级行政区划数量是否正确

    # 全国
    assert china._get_matched_adcode(100000) == '100000'
    assert len(china._get_all_subdistrict_adcode('100000', subdistrict=0)) == 1
    assert len(china._get_all_subdistrict_adcode('100000', subdistrict=1)) > 1
    assert len(china._get_all_subdistrict_adcode('100000', subdistrict=2)) > 1
    assert len(china._get_all_subdistrict_adcode('100000', subdistrict=3)) > 1

    # 浙江省
    assert china._get_matched_adcode(330000) == '330000'
    assert len(china._get_all_subdistrict_adcode('330000', subdistrict=0)) == 1
    assert len(china._get_all_subdistrict_adcode('330000', subdistrict=1)) > 1
    assert len(china._get_all_subdistrict_adcode('330000', subdistrict=2)) > 1
    assert len(china._get_all_subdistrict_adcode('330000', subdistrict=3)) == 0  # 因为没有下一级行政区划

    # 杭州市
    assert china._get_matched_adcode(330100) == '330100'
    assert len(china._get_all_subdistrict_adcode('330100', subdistrict=0)) == 1
    assert len(china._get_all_subdistrict_adcode('330100', subdistrict=1)) > 1
    assert len(china._get_all_subdistrict_adcode('330100', subdistrict=2)) == 0  # 因为没有下一级行政区划
    assert len(china._get_all_subdistrict_adcode('330100', subdistrict=3)) == 0  # 因为没有下一级行政区划

    # 西湖区
    assert china._get_matched_adcode(330106) == '330106'
    assert len(china._get_all_subdistrict_adcode('330106', subdistrict=0)) == 1
    assert len(china._get_all_subdistrict_adcode('330106', subdistrict=1)) == 0  # 因为没有下一级行政区划
    assert len(china._get_all_subdistrict_adcode('330106', subdistrict=2)) == 0  # 因为没有下一级行政区划
    assert len(china._get_all_subdistrict_adcode('330106', subdistrict=3)) == 0  # 因为没有下一级行政区划


def test_polylines(china):
    # 测试边界坐标数量是否正确

    assert len(china._get_polylines('100000')) > 100  # 全国，一般是上千个
    assert len(china._get_polylines('330000')) > 10  # 浙江省，一般是几百个
    assert len(china._get_polylines('330100')) > 0  # 杭州市，1个
    assert len(china._get_polylines('330106')) > 0  # 西湖区，1个


def test_all_polylines(china):
    # 测试下N级边界坐标数量是否正确

    # 全国
    assert len(china.get_all_polylines('100000', subdistrict=0)) > 10  # 全国，一般是上千个
    # 不测试全国下1/2/3级了，太多了

    # 浙江省
    assert len(china.get_all_polylines('330000', subdistrict=0)) > 10  # 浙江省，一般是几百个
    assert len(china.get_all_polylines('330000', subdistrict=1)) > 10  # 浙江省下1级，一般是几百个
    # 不测试浙江省下2级了，太多了
    assert len(china.get_all_polylines('330000', subdistrict=3)) == 0  # 因为没有下3级行政区划

    # 杭州市
    assert len(china.get_all_polylines('330100', subdistrict=0)) > 0  # 杭州市，1个
    assert len(china.get_all_polylines('330100', subdistrict=1)) > 0  # 杭州市下1级，一般是十几个
    assert len(china.get_all_polylines('330100', subdistrict=2)) == 0  # 因为没有下2级行政区划
    assert len(china.get_all_polylines('330100', subdistrict=3)) == 0  # 因为没有下3级行政区划

    # 西湖区
    assert len(china.get_all_polylines('330106', subdistrict=0)) > 0  # 西湖区，1个
    assert len(china.get_all_polylines('330106', subdistrict=1)) == 0  # 西湖区下1级，一般是十几个
    assert len(china.get_all_polylines('330106', subdistrict=2)) == 0  # 因为没有下2级行政区划
    assert len(china.get_all_polylines('330106', subdistrict=3)) == 0  # 因为没有下3级行政区划
