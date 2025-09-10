import redis
import time
import json
from datetime import datetime
from colorama import init, Fore, Style
import sys

# 初始化colorama
init()

class RedisTester:
    def __init__(self):
        self.client = None
        self.test_results = {
            "start_time": None,
            "end_time": None,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
        self.redis_commands = {
            "string": ["set", "get", "append", "incr", "decr", "strlen"],
            "hash": ["hset", "hget", "hgetall", "hkeys", "hvals", "hdel"],
            "list": ["lpush", "rpush", "lpop", "rpop", "llen", "lrange"],
            "set": ["sadd", "smembers", "sismember", "scard", "srem"],
            "zset": ["zadd", "zrange", "zscore", "zcard", "zrem"],
            "keys": ["keys", "exists", "expire", "ttl", "del"],
            "transaction": ["multi", "exec", "discard"],
            "pubsub": ["publish", "subscribe"],
            "script": ["eval"]
        }
    
    def connect(self, host='localhost', port=6379, db=0, password=None):
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_timeout=5
            )
            # 测试连接
            self.client.ping()
            self.print_success(f"✅ 成功连接到Redis服务器: {host}:{port} (DB: {db})")
            return True
        except Exception as e:
            self.print_error(f"❌ 连接Redis服务器失败: {str(e)}")
            return False
    
    def run_all_tests(self):
        if not self.client:
            self.print_error("❌ 请先连接Redis服务器")
            return
        
        self.test_results["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.print_header("开始Redis功能测试")
        
        # 清空测试数据库，避免干扰
        try:
            self.client.flushdb()
            self.print_info("ℹ️  已清空测试数据库")
        except Exception as e:
            self.print_warning(f"⚠️  清空数据库失败: {str(e)}")
        
        # 测试各功能模块
        self.test_strings()
        self.test_hashes()
        self.test_lists()
        self.test_sets()
        self.test_zsets()
        self.test_keys()
        self.test_transactions()
        self.test_pubsub()
        self.test_lua_script()
        
        self.test_results["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.generate_report()
    
    def test_strings(self):
        self.print_section("字符串操作测试")
        test_key = "test:string"
        
        try:
            # SET/GET测试
            self.client.set(test_key, "Hello Redis")
            value = self.client.get(test_key)
            self.assert_test("SET/GET", value == "Hello Redis", f"期望值: Hello Redis, 实际值: {value}")
            
            # APPEND测试
            self.client.append(test_key, "! Testing...")
            value = self.client.get(test_key)
            self.assert_test("APPEND", value == "Hello Redis! Testing...", f"期望值: Hello Redis! Testing..., 实际值: {value}")
            
            # INCR/DECR测试
            incr_key = "test:counter"
            self.client.set(incr_key, 100)
            self.client.incr(incr_key)
            value = self.client.get(incr_key)
            self.assert_test("INCR", value == "101", f"期望值: 101, 实际值: {value}")
            
            self.client.decr(incr_key)
            value = self.client.get(incr_key)
            self.assert_test("DECR", value == "100", f"期望值: 100, 实际值: {value}")
            
            # STRLEN测试
            length = self.client.strlen(test_key)
            self.assert_test("STRLEN", length == 23, f"期望值: 23, 实际值: {length}")
            
            # 清理
            self.client.delete(test_key, incr_key)
        except Exception as e:
            self.assert_test("字符串操作", False, str(e))
    
    def test_hashes(self):
        self.print_section("哈希操作测试")
        test_key = "test:hash"
        
        try:
            # HSET/HGET测试
            self.client.hset(test_key, "name", "Redis")
            self.client.hset(test_key, "version", "7.0")
            name = self.client.hget(test_key, "name")
            self.assert_test("HSET/HGET", name == "Redis", f"期望值: Redis, 实际值: {name}")
            
            # HGETALL测试
            hash_all = self.client.hgetall(test_key)
            expected = {"name": "Redis", "version": "7.0"}
            self.assert_test("HGETALL", hash_all == expected, f"期望值: {expected}, 实际值: {hash_all}")
            
            # HKEYS/HVALS测试
            keys = sorted(self.client.hkeys(test_key))
            values = sorted(self.client.hvals(test_key))
            self.assert_test("HKEYS", keys == ["name", "version"], f"期望值: ['name', 'version'], 实际值: {keys}")
            self.assert_test("HVALS", values == ["7.0", "Redis"], f"期望值: ['7.0', 'Redis'], 实际值: {values}")
            
            # HDEL测试
            self.client.hdel(test_key, "version")
            hash_all = self.client.hgetall(test_key)
            self.assert_test("HDEL", hash_all == {"name": "Redis"}, f"期望值: {{'name': 'Redis'}}, 实际值: {hash_all}")
            
            # 清理
            self.client.delete(test_key)
        except Exception as e:
            self.assert_test("哈希操作", False, str(e))
    
    def test_lists(self):
        self.print_section("列表操作测试")
        test_key = "test:list"
        
        try:
            # LPUSH/RPUSH测试
            self.client.lpush(test_key, "item1")
            self.client.rpush(test_key, "item2")
            self.client.lpush(test_key, "item0")
            
            # LRANGE测试
            items = self.client.lrange(test_key, 0, -1)
            expected = ["item0", "item1", "item2"]
            self.assert_test("LPUSH/RPUSH/LRANGE", items == expected, f"期望值: {expected}, 实际值: {items}")
            
            # LLEN测试
            length = self.client.llen(test_key)
            self.assert_test("LLEN", length == 3, f"期望值: 3, 实际值: {length}")
            
            # LPOP/RPOP测试
            lpop = self.client.lpop(test_key)
            rpop = self.client.rpop(test_key)
            self.assert_test("LPOP", lpop == "item0", f"期望值: item0, 实际值: {lpop}")
            self.assert_test("RPOP", rpop == "item2", f"期望值: item2, 实际值: {rpop}")
            
            # 清理
            self.client.delete(test_key)
        except Exception as e:
            self.assert_test("列表操作", False, str(e))
    
    def test_sets(self):
        self.print_section("集合操作测试")
        test_key = "test:set"
        
        try:
            # SADD测试
            self.client.sadd(test_key, "member1", "member2", "member3")
            
            # SMEMBERS测试
            members = sorted(self.client.smembers(test_key))
            expected = ["member1", "member2", "member3"]
            self.assert_test("SADD/SMEMBERS", members == expected, f"期望值: {expected}, 实际值: {members}")
            
            # SISMEMBER测试
            is_member = self.client.sismember(test_key, "member2")
            not_member = self.client.sismember(test_key, "member4")
            self.assert_test("SISMEMBER", is_member and not not_member, f"member2应该存在，member4应该不存在")
            
            # SCARD测试
            count = self.client.scard(test_key)
            self.assert_test("SCARD", count == 3, f"期望值: 3, 实际值: {count}")
            
            # SREM测试
            self.client.srem(test_key, "member2")
            count = self.client.scard(test_key)
            self.assert_test("SREM", count == 2, f"期望值: 2, 实际值: {count}")
            
            # 清理
            self.client.delete(test_key)
        except Exception as e:
            self.assert_test("集合操作", False, str(e))
    
    def test_zsets(self):
        self.print_section("有序集合操作测试")
        test_key = "test:zset"
        
        try:
            # ZADD测试
            self.client.zadd(test_key, {"member1": 10, "member2": 5, "member3": 15})
            
            # ZRANGE测试
            members = self.client.zrange(test_key, 0, -1, withscores=True)
            expected = [("member2", 5.0), ("member1", 10.0), ("member3", 15.0)]
            self.assert_test("ZADD/ZRANGE", members == expected, f"期望值: {expected}, 实际值: {members}")
            
            # ZSCORE测试
            score = self.client.zscore(test_key, "member1")
            self.assert_test("ZSCORE", score == 10.0, f"期望值: 10.0, 实际值: {score}")
            
            # ZCARD测试
            count = self.client.zcard(test_key)
            self.assert_test("ZCARD", count == 3, f"期望值: 3, 实际值: {count}")
            
            # ZREM测试
            self.client.zrem(test_key, "member2")
            count = self.client.zcard(test_key)
            self.assert_test("ZREM", count == 2, f"期望值: 2, 实际值: {count}")
            
            # 清理
            self.client.delete(test_key)
        except Exception as e:
            self.assert_test("有序集合操作", False, str(e))
    
    def test_keys(self):
        self.print_section("键操作测试")
        test_key1 = "test:key1"
        test_key2 = "test:key2"
        
        try:
            # 确保测试环境干净，删除可能存在的测试键
            self.client.delete(test_key1, test_key2, "test:hash")
            # SET/KEYS测试
            self.client.set(test_key1, "value1")
            self.client.set(test_key2, "value2")
            keys = sorted(self.client.keys("test:*"))
            expected = sorted([test_key1, test_key2])
            self.assert_test("KEYS", keys == expected, f"期望值: {expected}, 实际值: {keys}")
            
            # EXISTS测试
            exists = self.client.exists(test_key1)
            not_exists = self.client.exists("non_existent_key")
            self.assert_test("EXISTS", exists and not not_exists, f"{test_key1}应该存在，non_existent_key应该不存在")
            
            # EXPIRE/TTL测试
            self.client.expire(test_key1, 5)
            ttl = self.client.ttl(test_key1)
            self.assert_test("EXPIRE/TTL", ttl > 0, f"TTL应该大于0，实际值: {ttl}")
            
            # DEL测试
            self.client.delete(test_key2)
            exists = self.client.exists(test_key2)
            self.assert_test("DEL", not exists, f"{test_key2}应该已被删除")
            
            # 清理剩余的键
            self.client.delete(test_key1)
        except Exception as e:
            self.assert_test("键操作", False, str(e))
    
    def test_transactions(self):
        self.print_section("事务操作测试")
        test_key = "test:transaction"
        
        try:
            # 开始事务
            pipe = self.client.pipeline()
            pipe.multi()
            
            # 添加事务操作
            pipe.set(test_key, "before")
            pipe.get(test_key)
            pipe.incr("test:counter", 10)
            pipe.get("test:counter")
            
            # 执行事务
            results = pipe.execute()
            
            # 验证结果
            value = self.client.get(test_key)
            self.assert_test("事务执行", value == "before" and len(results) == 4, f"事务执行结果不符合预期: {results}")
            
            # 测试放弃事务
            pipe = self.client.pipeline()
            pipe.multi()
            pipe.set(test_key, "discarded")
            pipe.discard()
            
            value = self.client.get(test_key)
            self.assert_test("事务放弃", value == "before", f"期望值: before, 实际值: {value}")
            
            # 清理
            self.client.delete(test_key, "test:counter")
        except Exception as e:
            self.assert_test("事务操作", False, str(e))
    
    def test_pubsub(self):
        self.print_section("发布订阅测试")
        channel = "test:channel"
        
        try:
            # 测试发布消息
            pubsub = self.client.pubsub()
            
            # 在新线程中订阅频道（简化版，不实际接收消息）
            pubsub.subscribe(channel)
            
            # 发布消息
            message_id = self.client.publish(channel, "Hello PubSub")
            
            # 对于简单测试，我们只检查发布是否成功（返回的是订阅者数量，这里可能为0，因为我们是异步订阅）
            self.assert_test("PUBLISH", isinstance(message_id, int), f"发布消息失败，返回值: {message_id}")
            
            # 清理
            pubsub.unsubscribe(channel)
            pubsub.close()
        except Exception as e:
            self.assert_test("发布订阅", False, str(e))
    
    def test_lua_script(self):
        self.print_section("Lua脚本测试")
        
        try:
            # 简单的Lua脚本：设置一个键值对并返回值
            script = """
            redis.call('SET', KEYS[1], ARGV[1])
            return redis.call('GET', KEYS[1])
            """
            test_key = "test:lua"
            
            # 执行Lua脚本
            result = self.client.eval(script, 1, test_key, "Lua Value")
            
            # 验证结果
            self.assert_test("Lua脚本执行", result == "Lua Value", f"期望值: Lua Value, 实际值: {result}")
            
            # 清理
            self.client.delete(test_key)
        except Exception as e:
            self.assert_test("Lua脚本", False, str(e))
    
    def assert_test(self, test_name, condition, message=None):
        self.test_results["total_tests"] += 1
        
        if condition:
            self.test_results["passed_tests"] += 1
            self.test_results["test_details"].append({
                "name": test_name,
                "status": "PASSED",
                "message": message or "测试通过"
            })
            self.print_success(f"✅ {test_name}: 测试通过")
        else:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append({
                "name": test_name,
                "status": "FAILED",
                "message": message or "测试失败"
            })
            self.print_error(f"❌ {test_name}: 测试失败 - {message}")
    
    def generate_report(self):
        self.print_header("Redis功能测试报告")
        
        # 输出到控制台
        print(f"测试开始时间: {self.test_results['start_time']}")
        print(f"测试结束时间: {self.test_results['end_time']}")
        print(f"总测试用例数: {self.test_results['total_tests']}")
        print(f"通过测试数: {self.test_results['passed_tests']}")
        print(f"失败测试数: {self.test_results['failed_tests']}")
        
        if self.test_results['failed_tests'] > 0:
            print(f"\n{Fore.RED}失败的测试:{Style.RESET_ALL}")
            for test in self.test_results['test_details']:
                if test['status'] == 'FAILED':
                    print(f"  - {test['name']}: {test['message']}")
        
        # 生成JSON报告
        report_file = f"redis_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        self.print_info(f"\n📊 测试报告已保存至: {report_file}")
        
        # 生成命令支持情况汇总
        supported_commands = {}
        for category, commands in self.redis_commands.items():
            supported_commands[category] = []
            for cmd in commands:
                # 检查命令是否在测试中被测试过（简化判断）
                is_supported = any(test['name'].upper() == cmd.upper() or cmd.upper() in test['name'].upper() for test in self.test_results['test_details'] if test['status'] == 'PASSED')
                supported_commands[category].append({"command": cmd, "supported": is_supported})
        
        # 保存命令支持情况
        commands_file = f"redis_commands_support_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(commands_file, 'w', encoding='utf-8') as f:
            json.dump(supported_commands, f, ensure_ascii=False, indent=2)
        
        self.print_info(f"📋 Redis命令支持情况已保存至: {commands_file}")
    
    # 辅助打印函数
    def print_header(self, text):
        print(f"\n{Fore.CYAN}======== {text} ========{Style.RESET_ALL}")
    
    def print_section(self, text):
        print(f"\n{Fore.GREEN}----- {text} -----{Style.RESET_ALL}")
    
    def print_success(self, text):
        print(f"{Fore.GREEN}{text}{Style.RESET_ALL}")
    
    def print_error(self, text):
        print(f"{Fore.RED}{text}{Style.RESET_ALL}")
    
    def print_warning(self, text):
        print(f"{Fore.YELLOW}{text}{Style.RESET_ALL}")
    
    def print_info(self, text):
        print(f"{Fore.BLUE}{text}{Style.RESET_ALL}")

if __name__ == "__main__":
    tester = RedisTester()
    
    # 获取命令行参数（如果有）
    host = '172.16.99.200'
    port = 6378
    db = 0
    password = 'redis_6xAzKX'
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        db = int(sys.argv[3])
    if len(sys.argv) > 4:
        password = sys.argv[4]
    
    # 连接Redis并运行测试
    if tester.connect(host, port, db, password):
        tester.run_all_tests()
    else:
        print("测试无法继续，退出程序。")