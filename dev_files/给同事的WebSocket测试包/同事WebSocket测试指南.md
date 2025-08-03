# 🤖 同事WebSocket测试指南

## 📋 概述

由于Django后端WebSocket服务暂时有配置问题，我们提供了一个简化的WebSocket服务器供同事测试使用。这个服务器实现了所有必要的WebSocket通信功能。

## 🚀 快速开始

### 1. 服务器端（我们这边）

我们已经启动了一个简化的WebSocket服务器：

```bash
# 服务器地址
ws://你的服务器IP:8001/robot/{robot_id}

# 示例
ws://192.168.1.100:8001/robot/1
```

### 2. 客户端（同事那边）

#### 安装依赖

```bash
pip install websockets
```

#### 运行测试客户端

```bash
python robot_test_client.py
```

## 📡 连接配置

### 修改连接地址

在 `robot_test_client.py` 中修改服务器地址：

```python
# 将这行修改为你的实际服务器地址
server_url = "ws://你的服务器IP:8001/robot/1"
```

### 支持的机器人ID

- 机器人1: `ws://服务器IP:8001/robot/1`
- 机器人2: `ws://服务器IP:8001/robot/2`
- 机器人3: `ws://服务器IP:8001/robot/3`

## 🔄 消息格式

### 1. 心跳消息

**发送（客户端 → 服务器）**
```json
{
    "type": "heartbeat",
    "robot_id": "1",
    "timestamp": 1640995200.0,
    "status": "online"
}
```

**接收（服务器 → 客户端）**
```json
{
    "type": "heartbeat_ack",
    "robot_id": "1",
    "timestamp": 1640995200.0
}
```

### 2. 状态更新

**发送（客户端 → 服务器）**
```json
{
    "type": "status_update",
    "robot_id": "1",
    "data": {
        "battery": 85,
        "location": "Building A",
        "door_status": "closed",
        "speed": 2,
        "temperature": 25.5
    },
    "timestamp": 1640995200.0
}
```

**接收（服务器 → 客户端）**
```json
{
    "type": "status_ack",
    "robot_id": "1",
    "timestamp": 1640995200.0
}
```

### 3. 命令执行

**接收（服务器 → 客户端）**
```json
{
    "type": "command",
    "command": "open_door",
    "command_id": "cmd_1640995200",
    "data": {},
    "timestamp": 1640995200.0
}
```

**发送（客户端 → 服务器）**
```json
{
    "type": "command_result",
    "robot_id": "1",
    "command_id": "cmd_1640995200",
    "result": "success",
    "message": "门已打开",
    "timestamp": 1640995200.0
}
```

### 4. 二维码扫描

**发送（客户端 → 服务器）**
```json
{
    "type": "qr_scanned",
    "robot_id": "1",
    "qr_data": {
        "order_id": "order_1234",
        "qr_content": "qr_content_567",
        "scan_time": "2024-01-01T12:00:00"
    },
    "timestamp": 1640995200.0
}
```

**接收（服务器 → 客户端）**
```json
{
    "type": "qr_scan_ack",
    "robot_id": "1",
    "timestamp": 1640995200.0
}
```

## 🔧 支持的命令

| 命令 | 描述 | 示例 |
|------|------|------|
| `open_door` | 开门 | 打开机器人舱门 |
| `close_door` | 关门 | 关闭机器人舱门 |
| `start_delivery` | 开始配送 | 开始配送任务 |
| `stop_robot` | 停止机器人 | 停止机器人移动 |
| `emergency_open_door` | 紧急开门 | 紧急情况下开门 |

## 📊 状态字段说明

| 字段 | 类型 | 描述 | 示例值 |
|------|------|------|--------|
| `battery` | int | 电池电量（0-100） | 85 |
| `location` | string | 当前位置 | "Building A" |
| `door_status` | string | 门状态 | "open", "closed" |
| `speed` | int | 移动速度（0-5） | 2 |
| `temperature` | float | 温度 | 25.5 |

## 🧪 测试步骤

### 1. 基础连接测试

```python
import asyncio
import websockets
import json

async def test_connection():
    uri = "ws://你的服务器IP:8001/robot/1"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ 连接成功")
            
            # 发送心跳
            heartbeat = {
                "type": "heartbeat",
                "robot_id": "1",
                "timestamp": time.time(),
                "status": "online"
            }
            await websocket.send(json.dumps(heartbeat))
            
            # 接收响应
            response = await websocket.recv()
            print(f"📥 收到响应: {response}")
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")

asyncio.run(test_connection())
```

### 2. 完整功能测试

运行提供的测试客户端：

```bash
python robot_test_client.py
```

这个客户端会自动：
- 建立WebSocket连接
- 每30秒发送心跳
- 每60秒发送状态更新
- 处理接收到的命令
- 模拟命令执行并返回结果

### 3. 手动命令测试

你可以通过修改服务器代码来发送测试命令：

```python
# 在服务器端添加测试命令发送
await server_instance.send_command("1", "open_door")
```

## 🔍 调试信息

### 客户端日志

客户端会输出详细的连接和通信日志：

```
🤖 机器人WebSocket测试客户端
==================================================
📡 服务器地址: ws://localhost:8001/robot/1
🤖 机器人ID: 1
==================================================
🔌 连接到服务器: ws://localhost:8001/robot/1
✅ 连接成功
🤖 机器人客户端启动
💓 发送心跳: 1
📊 发送状态更新: {'battery': 96, 'location': 'Building A', ...}
📥 收到消息: heartbeat_ack
📥 收到消息: command
🔧 收到命令: open_door
🔧 发送命令结果: success - 门已打开
```

### 服务器日志

服务器会记录所有连接和消息：

```
🚀 启动简化WebSocket服务器...
📡 监听端口: 8001
🔗 机器人连接地址: ws://localhost:8001/robot/{robot_id}
==================================================
✅ WebSocket服务器启动成功
⏳ 等待机器人连接...
🤖 机器人 1 尝试连接
✅ 机器人 1 连接成功
📥 收到机器人 1 的消息: heartbeat
📤 向机器人 1 发送消息: heartbeat_ack
```

## ❗ 常见问题

### 1. 连接被拒绝

**问题**: `ConnectionRefusedError`
**解决**: 
- 检查服务器IP和端口是否正确
- 确认服务器是否已启动
- 检查防火墙设置

### 2. 连接超时

**问题**: `TimeoutError`
**解决**:
- 检查网络连接
- 增加超时时间
- 确认服务器响应正常

### 3. JSON格式错误

**问题**: `JSONDecodeError`
**解决**:
- 检查消息格式是否符合规范
- 确保所有必需字段都存在
- 验证数据类型正确

### 4. 机器人ID冲突

**问题**: 多个机器人使用相同ID
**解决**:
- 确保每个机器人使用唯一的ID
- 检查机器人ID配置

## 📞 技术支持

如果遇到问题，请提供以下信息：

1. **错误信息**: 完整的错误日志
2. **连接信息**: 服务器地址、机器人ID
3. **网络环境**: 网络配置、防火墙设置
4. **测试代码**: 使用的测试代码片段

## 🔄 后续计划

等Django WebSocket服务修复后，我们将：

1. 迁移到完整的Django WebSocket服务
2. 提供更丰富的API功能
3. 支持数据库持久化
4. 添加用户认证和权限控制
5. 提供WebSocket监控界面

---

**注意**: 这是一个临时测试方案，用于验证WebSocket通信功能。等Django服务修复后，将提供完整的生产环境WebSocket API。 