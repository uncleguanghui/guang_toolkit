# Contributing to Guang-Toolkit

如果你有兴趣为 Guang-Toolkit 做出贡献，你的贡献将分为两类：

1. 提出一个新功能并实现它
    - 发布你的预期功能，然后我们将讨论设计和实施。一旦我们同意该功能，请继续执行。
2. 希望为未解决的issue实现功能或修复bug
    - 查看[issue](https://github.com/uncleguanghui/guang_toolkit/issues)。
    - 选择一个issue，并评论你要实现的功能。
    - 如果你需要更多关于特定issue的背景信息，请询问我们来提供帮助。

如果条件允许，你还需要编写一些测试代码以确保代码能正常运作。我们用`pytest`用来编写测试：
  - 测试文件的命名规范：`test_*.py`，例如`test_precision.py`
  - 测试函数的命名规范`def test_*`，例如`def test_precision_on_random_data()`

新代码应与`Python 3.6+`版本兼容。完成功能或者修复bug和测试后，请运行lint检查（必须）和测试（如果有）：

#### 运行lint检查

```
flake8 guang_toolkit/ tests/
```

#### 运行测试

```
python -m pytest tests/
```

我们建议在`Python 3.6+`上运行测试。

#### 发送pull reqeust

如果一切正常，请发送一个pull reqeust到 https://github.com/uncleguanghui/guang_toolkit

如果你不熟悉创建pull reqeust，请参阅以下指南：

* [GitHub 的 Pull Request 是指什么意思？](https://www.zhihu.com/question/21682976)
* [how to do a github pull request](http://stackoverflow.com/questions/14680711/how-to-do-a-github-pull-request)
* [Creating a pull request](https://help.github.com/articles/creating-a-pull-request)


#  工具包上传

### 1、安装twine
 
```
pip install twine
```

### 2、修改本地配置

修改用户根目录的`.pypirc`文件为

```
[distutils]
index-servers =
    pypi

[nexus]
repository=https://upload.pypi.org/legacy/
username=用户名
password=密码
```

### 3、打包


```
python setup.py sdist bdist_wheel

```

### 4、上传

```
twine upload -r nexus dist/*   
```

### 5、清空

```
python setup.py clean   
```
