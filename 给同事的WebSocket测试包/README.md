# 🤖 给同事的WebSocket测试包

## 📋 文件说明

这个包包含了完整的WebSocket通信测试系统，供同事测试机器人WebSocket连接使用。

## 📁 文件清单

### 核心文件
1. **`websocket_server_final.py`** - WebSocket服务器（你这边运行）
2. **`robot_test_client.py`** - 机器人测试客户端（同事运行）
3. **`start_websocket_test.sh`** - 快速启动脚本
4. **`requirements.txt`** - Python依赖库

### 文档文件
5. **`同事WebSocket测试指南.md`** - 详细使用指南
6. **`如何发送命令给机器人.md`** - 命令发送说明
7. **`README.md`** - 本说明文件

## 🚀 快速开始

### 服务器端（你这边）
1. **启动服务器**:
```bash
python3 websocket_server_final.py
```

2. **发送命令**:
在服务器终端中直接输入：
```
1 open_door          # 向机器人1发送开门命令
1 close_door         # 向机器人1发送关门命令
1 start_delivery     # 向机器人1发送开始配送命令
1 stop_robot         # 向机器人1发送停止命令
1 emergency_open_door # 向机器人1发送紧急开门命令
```

### 客户端（同事那边）
1. **安装依赖**:
```bash
pip install websockets
```

2. **修改服务器地址**:
在 `robot_test_client.py` 中修改服务器地址：
```python
server_url = "ws://你的服务器IP:8001/robot/1"
```

3. **启动客户端**:
```bash
python3 robot_test_client.py
```

或者使用快速启动脚本：
```bash
./start_websocket_test.sh
```

## 📡 连接信息

- **服务器地址**: `ws://你的服务器IP:8001/robot/{robot_id}`
- **机器人ID**: 1, 2, 3... (可自定义)
- **端口**: 8001

## 🔧 支持的功能

- ✅ WebSocket连接建立
- ✅ 心跳通信
- ✅ 状态更新
- ✅ 命令接收和执行
- ✅ 二维码扫描模拟
- ✅ 自动重连
- ✅ 实时命令发送

## 📞 联系我们

如果遇到问题，请提供：
1. 错误信息截图
2. 连接日志
3. 网络环境信息

---

**注意**: 这是临时测试方案，等Django WebSocket服务修复后，将提供完整的生产环境API。 