import logging

try:
    from .func import load_config
except (ImportError, ValueError):
    from guang_toolkit import load_config

logger = logging.getLogger(__name__)


class Basic:
    def set_input(self, keys, values, path_config):
        """
        设置属性
        :param keys: 属性名称列表
        :param values: 属性值列表
        :param path_config:
        :return:
        """
        items = [(name, value) for (name, value) in zip(keys, values)]
        invalid_items = [(name, value) for (name, value) in items if value is None]  # 没有输入的属性

        if len(invalid_items) == 0:  # 如果属性全部都输入了
            for name, value in items:
                self.__setattr__(name, str(value))
        elif len(invalid_items) == len(keys):  # 如果属性都没输入
            if path_config is None:
                raise FileNotFoundError('请指定配置文件!')
            else:
                dict_params = load_config(path_config, config_type='json')
                for name in keys:
                    value = dict_params.get(name)
                    if value is None:
                        raise ValueError(f'配置文件缺少参数{name}')
                    else:
                        self.__setattr__(name, value)
        else:  # 部分属性输入了
            raise ValueError(f'缺少配置参数{[name for name, _ in invalid_items]}')
