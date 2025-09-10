# Redis功能测试项目

这个项目用于全面测试Redis服务器的各项功能，并生成详细的测试报告。

## 功能特性

- 测试Redis的核心数据类型：字符串、哈希、列表、集合、有序集合
- 测试Redis的键操作、事务、发布订阅和Lua脚本功能
- 生成JSON格式的测试报告和命令支持情况汇总
- 彩色控制台输出，方便查看测试结果
- 支持自定义Redis连接参数（主机、端口、数据库、密码）

## 环境要求

- Python 3.6+（已测试3.12.2版本）
- Redis服务器（默认连接localhost:6379）

## 安装依赖

在项目目录下运行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 默认配置运行

如果Redis服务器运行在localhost:6379，没有设置密码，可以直接运行：

```bash
python redis_test.py
```

### 自定义连接参数

可以通过命令行参数指定Redis连接信息：

```bash
python redis_test.py [主机] [端口] [数据库] [密码]
```

例如：

```bash
python redis_test.py 192.168.1.100 6379 0 mypassword
```

## 测试内容

测试项目会对以下Redis功能进行全面测试：

1. **字符串操作**：SET, GET, APPEND, INCR, DECR, STRLEN
2. **哈希操作**：HSET, HGET, HGETALL, HKEYS, HVALS, HDEL
3. **列表操作**：LPUSH, RPUSH, LPOP, RPOP, LLEN, LRANGE
4. **集合操作**：SADD, SMEMBERS, SISMEMBER, SCARD, SREM
5. **有序集合操作**：ZADD, ZRANGE, ZSCORE, ZCARD, ZREM
6. **键操作**：KEYS, EXISTS, EXPIRE, TTL, DEL
7. **事务操作**：MULTI, EXEC, DISCARD
8. **发布订阅**：PUBLISH, SUBSCRIBE
9. **Lua脚本**：EVAL

## 测试报告

测试完成后，会在当前目录生成两个JSON格式的文件：

1. `redis_test_report_时间戳.json` - 包含详细的测试结果信息
2. `redis_commands_support_时间戳.json` - 包含Redis命令的支持情况汇总

同时，测试结果也会在控制台以彩色文本形式显示。

## 注意事项

- 测试过程中会清空指定的Redis数据库，请确保使用测试专用的数据库
- 如果Redis服务器配置了密码认证，请在命令行参数中提供密码
- 如需测试更多Redis功能，请修改`redis_test.py`文件中的相关测试方法