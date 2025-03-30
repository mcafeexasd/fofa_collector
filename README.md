# FOFA API 信息收集工具

这是一个使用FOFA API进行信息收集的Python工具，可以通过FOFA搜索引擎收集域名、子域名、IP和URL信息。

## 功能特点

- 支持单条语句自定义查询
- 支持批量查询（从文件读取）
- 将查询结果分类保存到不同文件中
- 自动去重并保留历史结果
- 可配置查询间隔和重试次数

## 安装

1. 克隆本仓库或下载源代码
2. 安装依赖库：
```
pip install requests tldextract
```
或者使用requirements.txt安装：
```
pip install -r requirements.txt
```

## 配置

在使用前，请先编辑 `config.py` 文件，填入您的FOFA账号信息：

```python
FOFA_API_KEY = "your-api-key"  # 填写FOFA API KEY
```

您可以在FOFA个人中心页面获取您的API KEY：https://fofa.info/user/api

## 使用方法

### 单条查询

```
python main.py domain="example.com"
```

### 批量查询

创建一个文本文件（例如 `info.txt`），每行一个查询目标：

```
aaaa
bbbb
cccc
......
```

然后执行批量查询（注意不需要添加引号）：

```
python main.py org=info.txt
```

程序会自动读取文件中的每一行，并构造格式为 `org="aaaa"` 的查询语句发送给FOFA API。

## 结果文件

查询结果将保存在 `result` 目录下的四个文件中：

- `domain.txt`: 主域名结果（例如：example.com）
- `subdomain.txt`: 子域名结果（例如：sub.example.com）
- `ip.txt`: IP地址结果
- `url.txt`: URL地址结果（原始格式，直接来自FOFA返回的第一列）

每次查询后，结果会追加到现有文件中并自动去重。

## 注意事项

- 每个查询请求的时间间隔为2秒
- 查询失败会自动重试，最多2次
- 需要有效的FOFA会员账号才能使用API 