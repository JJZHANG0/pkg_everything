# 🤖 ROS小车WebSocket API文档

## 概述

本文档描述了ROS小车与服务器之间的WebSocket通信协议，用于替代原有的轮询机制，实现实时双向通信。

## 连接信息

- **WebSocket URL**: `ws://localhost:8000/ws/robot/{robot_id}/`
- **认证方式**: JWT Token (通过URL参数传递)
- **连接参数**:
  - `token`: JWT认证token
  - `robot_id`: 机器人ID

### 连接示例

```javascript
// JavaScript示例
const ws = new WebSocket(`ws://localhost:8000/ws/robot/1/?token=${jwt_token}&robot_id=1`);
```

```python
# Python示例
import websockets
import asyncio

async def connect_robot():
    params = f"token={jwt_token}&robot_id=1"
    uri = f"ws://localhost:8000/ws/robot/1/?{params}"
    websocket = await websockets.connect(uri)
    return websocket
```

## 消息格式

所有消息都使用JSON格式，包含以下字段：

```json
{
    "type": "消息类型",
    "timestamp": "2024-01-01T12:00:00Z",
    "data": {}
}
```

## 服务器发送的消息类型

### 1. 连接确认 (connection_established)

```json
{
    "type": "connection_established",
    "message": "机器人 快递小车1 WebSocket连接成功",
    "robot_id": 1,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. 指令消息 (command)

```json
{
    "type": "command",
    "command_id": 123,
    "command": "open_door",
    "data": {
        "priority": "high"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**指令类型**:
- `open_door`: 开门指令
- `close_door`: 关门指令
- `start_delivery`: 开始配送
- `stop_robot`: 停止机器人
- `emergency_open_door`: 紧急开门

### 3. 通知消息 (notification)

```json
{
    "type": "notification",
    "message": "系统维护通知",
    "level": "info",
    "data": {
        "maintenance_time": "2024-01-01T14:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**通知级别**:
- `info`: 信息
- `warning`: 警告
- `error`: 错误

### 4. 错误消息 (error)

```json
{
    "type": "error",
    "message": "指令格式错误",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## ROS小车发送的消息类型

### 1. 状态更新 (status_update)

```json
{
    "type": "status_update",
    "status": "IDLE",
    "battery": 85,
    "door_status": "CLOSED",
    "location": {
        "x": 10.5,
        "y": 20.3
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**状态值**:
- `status`: `IDLE` | `LOADING` | `DELIVERING` | `MAINTENANCE` | `RETURNING`
- `door_status`: `OPEN` | `CLOSED`
- `battery`: 0-100的整数
- `location`: 包含x, y坐标的对象

### 2. 指令执行结果 (command_result)

```json
{
    "type": "command_result",
    "command_id": 123,
    "result": "door_open",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**结果值**:
- `door_open`: 门已打开
- `door_closed`: 门已关闭
- `delivery_started`: 配送已开始
- `robot_stopped`: 机器人已停止
- `error: 错误信息`: 执行失败

### 3. 二维码扫描结果 (qr_scanned)

```json
{
    "type": "qr_scanned",
    "order_id": 456,
    "qr_data": {
        "scanned_at": 1704110400,
        "location": {
            "x": 10.5,
            "y": 20.3
        }
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 4. 订单状态更新 (order_update)

```json
{
    "type": "order_update",
    "order_id": 456,
    "status": "PICKED_UP",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 5. 心跳消息 (heartbeat)

```json
{
    "type": "heartbeat",
    "timestamp": 1704110400
}
```

## 服务器响应消息

### 1. 状态更新确认 (status_update_ack)

```json
{
    "type": "status_update_ack",
    "message": "状态更新成功",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. 指令结果确认 (command_result_ack)

```json
{
    "type": "command_result_ack",
    "message": "指令结果接收成功",
    "command_id": 123,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 3. 二维码扫描确认 (qr_scanned_ack)

```json
{
    "type": "qr_scanned_ack",
    "message": "二维码扫描处理成功",
    "order_id": 456,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 4. 订单更新确认 (order_update_ack)

```json
{
    "type": "order_update_ack",
    "message": "订单状态更新成功",
    "order_id": 456,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 5. 心跳响应 (heartbeat_ack)

```json
{
    "type": "heartbeat_ack",
    "message": "心跳响应",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## 连接关闭代码

- `4000`: 连接失败
- `4001`: 缺少认证token
- `4002`: 认证失败
- `4003`: 缺少机器人ID
- `4004`: 机器人不存在

## 使用示例

### Python客户端示例

```python
import asyncio
import websockets
import json
import time

class RobotWebSocketClient:
    def __init__(self, server_url, robot_id, token):
        self.server_url = server_url
        self.robot_id = robot_id
        self.token = token
        self.websocket = None
        
    async def connect(self):
        params = f"token={self.token}&robot_id={self.robot_id}"
        uri = f"{self.server_url}/ws/robot/{self.robot_id}/?{params}"
        self.websocket = await websockets.connect(uri)
        
    async def send_status_update(self, status_data):
        message = {
            "type": "status_update",
            **status_data
        }
        await self.websocket.send(json.dumps(message))
        
    async def send_command_result(self, command_id, result):
        message = {
            "type": "command_result",
            "command_id": command_id,
            "result": result
        }
        await self.websocket.send(json.dumps(message))
        
    async def listen_for_commands(self):
        async for message in self.websocket:
            data = json.loads(message)
            if data["type"] == "command":
                await self.handle_command(data)
                
    async def handle_command(self, data):
        command_id = data["command_id"]
        command = data["command"]
        
        # 执行指令
        if command == "open_door":
            # 执行开门操作
            result = "door_open"
            await self.send_command_result(command_id, result)

# 使用示例
async def main():
    client = RobotWebSocketClient("ws://localhost:8000", 1, "your_jwt_token")
    await client.connect()
    
    # 发送初始状态
    await client.send_status_update({
        "status": "IDLE",
        "battery": 85,
        "door_status": "CLOSED",
        "location": {"x": 0, "y": 0}
    })
    
    # 监听指令
    await client.listen_for_commands()

asyncio.run(main())
```

### JavaScript客户端示例

```javascript
class RobotWebSocketClient {
    constructor(serverUrl, robotId, token) {
        this.serverUrl = serverUrl;
        this.robotId = robotId;
        this.token = token;
        this.ws = null;
    }
    
    connect() {
        const url = `${this.serverUrl}/ws/robot/${this.robotId}/?token=${this.token}&robot_id=${this.robotId}`;
        this.ws = new WebSocket(url);
        
        this.ws.onopen = () => {
            console.log('WebSocket连接已建立');
            this.sendStatusUpdate({
                status: 'IDLE',
                battery: 85,
                door_status: 'CLOSED',
                location: {x: 0, y: 0}
            });
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket连接已关闭');
        };
    }
    
    sendStatusUpdate(statusData) {
        const message = {
            type: 'status_update',
            ...statusData
        };
        this.ws.send(JSON.stringify(message));
    }
    
    sendCommandResult(commandId, result) {
        const message = {
            type: 'command_result',
            command_id: commandId,
            result: result
        };
        this.ws.send(JSON.stringify(message));
    }
    
    handleMessage(data) {
        if (data.type === 'command') {
            this.handleCommand(data);
        }
    }
    
    handleCommand(data) {
        const commandId = data.command_id;
        const command = data.command;
        
        if (command === 'open_door') {
            // 执行开门操作
            this.sendCommandResult(commandId, 'door_open');
        }
    }
}

// 使用示例
const client = new RobotWebSocketClient('ws://localhost:8000', 1, 'your_jwt_token');
client.connect();
```

## 最佳实践

1. **心跳机制**: 建议每30秒发送一次心跳消息
2. **错误处理**: 实现重连机制，处理连接断开情况
3. **状态同步**: 定期发送状态更新，保持服务器状态同步
4. **指令确认**: 收到指令后及时发送执行结果
5. **日志记录**: 记录所有WebSocket通信日志，便于调试

## 迁移指南

从轮询模式迁移到WebSocket模式：

1. **替换API调用**: 将轮询API调用替换为WebSocket消息
2. **状态管理**: 使用WebSocket实时更新状态，而不是定期查询
3. **指令处理**: 通过WebSocket接收指令，而不是轮询获取
4. **错误处理**: 实现WebSocket连接错误处理和重连机制

## 注意事项

1. **连接稳定性**: WebSocket连接可能因网络问题断开，需要实现重连机制
2. **消息顺序**: 确保消息按正确顺序处理
3. **认证安全**: JWT token需要定期刷新
4. **资源管理**: 及时关闭不需要的WebSocket连接 