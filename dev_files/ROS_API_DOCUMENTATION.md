# 🤖 ROS机器人API技术文档

## 📋 文档信息

- **版本**: v1.0.0
- **最后更新**: 2024年1月15日
- **作者**: 校园快递配送系统开发团队
- **适用对象**: ROS机器人开发工程师

---

## 🎯 概述

本文档描述了校园快递配送系统中ROS机器人端需要使用的所有API接口。系统采用RESTful API设计，支持完整的机器人控制、订单管理、状态同步和二维码扫描功能。

### 系统架构

```
ROS机器人 ←→ API网关 ←→ Django后端 ←→ MySQL数据库
    ↓           ↓           ↓           ↓
  硬件控制   认证授权    业务逻辑    数据存储
```

---

## 🔐 认证机制

### JWT Token认证

所有API请求都需要在请求头中包含有效的JWT访问令牌。

#### 获取访问令牌

```http
POST /api/token/
Content-Type: application/json

{
    "username": "root",
    "password": "test123456"
}
```

**响应示例**:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA1MzI0MDAwLCJqdGkiOiIxMjM0NTY3ODkwIiwidXNlcl9pZCI6MX0.abcdefghijklmnopqrstuvwxyz",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwNTQwNjQwMCwianRpIjoiMTIzNDU2Nzg5MCIsInVzZXJfaWQiOjF9.abcdefghijklmnopqrstuvwxyz"
}
```

#### 请求头格式

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## 📊 机器人状态管理

### 1. 获取机器人详细状态

获取机器人的完整状态信息，包括位置、电量、门状态和当前订单。

```http
GET /api/robots/{robot_id}/status/
Authorization: Bearer <token>
```

**路径参数**:
- `robot_id` (integer, required): 机器人ID

**响应示例**:
```json
{
    "id": 1,
    "name": "Robot-001",
    "status": "IDLE",
    "current_location": "Warehouse",
    "battery_level": 85,
    "door_status": "CLOSED",
    "current_orders": [
        {
            "order_id": 123,
            "status": "ASSIGNED",
            "delivery_location": "Building-A-101",
            "qr_is_valid": true,
            "qr_scanned_at": null
        }
    ],
    "last_update": "2024-01-15T10:30:00Z",
    "delivery_start_time": null,
    "qr_wait_start_time": null
}
```

**状态说明**:
- `status`: IDLE(空闲) | LOADING(装货中) | DELIVERING(配送中) | MAINTENANCE(维护中) | RETURNING(返航中)
- `door_status`: OPEN(开门) | CLOSED(关门)

### 2. 更新机器人状态

更新机器人的位置、电量、门状态等信息。

```http
POST /api/robots/{robot_id}/update_status/
Authorization: Bearer <token>
Content-Type: application/json

{
    "location": "Building-A",
    "battery": 85,
    "door_status": "OPEN",
    "status": "DELIVERING"
}
```

**请求参数**:
- `location` (string, optional): 当前位置
- `battery` (integer, optional): 电池电量 (0-100)
- `door_status` (string, optional): 门状态 ("OPEN" | "CLOSED")
- `status` (string, optional): 机器人状态

**响应示例**:
```json
{
    "message": "状态更新成功",
    "robot_id": 1,
    "status": "DELIVERING",
    "location": "Building-A",
    "battery": 85,
    "door_status": "OPEN"
}
```

---

## 📦 订单管理

### 1. 获取机器人当前订单

获取分配给机器人的所有订单的详细信息。

```http
GET /api/robots/{robot_id}/current_orders/
Authorization: Bearer <token>
```

**响应示例**:
```json
{
    "robot_id": 1,
    "robot_name": "Robot-001",
    "status": "LOADING",
    "current_orders": [
        {
            "order_id": 123,
            "status": "ASSIGNED",
            "student": {
                "id": 456,
                "name": "student1",
                "email": "student1@example.com",
                "first_name": "张",
                "last_name": "三"
            },
            "package_info": {
                "type": "包裹",
                "weight": "1kg",
                "fragile": false,
                "description": "书籍"
            },
            "pickup_location": {
                "building": "Warehouse",
                "instructions": "在仓库A区"
            },
            "delivery_location": {
                "building": "Building-A",
                "room": "101"
            },
            "qr_code_data": {
                "payload": "eyJvcmRlcl9pZCI6MTIzLCJzdHVkZW50X2lkIjo0NTZ9",
                "signature": "a1b2c3d4e5f6...",
                "qr_image_url": "http://example.com/qr/123.png"
            },
            "delivery_priority": "normal",
            "estimated_time": "15分钟"
        }
    ],
    "delivery_route": [
        {
            "sequence": 1,
            "order_id": 123,
            "location": "Building-A-101",
            "estimated_arrival": "10:30"
        }
    ],
    "summary": {
        "total_orders": 1,
        "loaded_orders": 0,
        "total_distance": "2.5km",
        "estimated_total_time": "15分钟"
    }
}
```

### 2. 接收订单分配

接收系统分配的订单，机器人状态自动更新为LOADING。

```http
POST /api/robots/{robot_id}/receive_orders/
Authorization: Bearer <token>
Content-Type: application/json

{
    "order_ids": [123, 124, 125]
}
```

**请求参数**:
- `order_ids` (array, required): 订单ID列表

**响应示例**:
```json
{
    "detail": "成功分配 3 个订单给机器人 Robot-001",
    "robot_id": 1,
    "robot_name": "Robot-001",
    "status": "LOADING",
    "assigned_orders": [123, 124, 125],
    "current_orders": [...],
    "delivery_route": [...],
    "summary": {
        "total_orders": 3,
        "loaded_orders": 0,
        "total_distance": "5.2km",
        "estimated_total_time": "45分钟"
    }
}
```

---

## 🎮 指令控制系统

### 1. 获取待执行指令

机器人定期轮询获取待执行的指令。

```http
GET /api/robots/{robot_id}/get_commands/
Authorization: Bearer <token>
```

**响应示例**:
```json
{
    "robot_id": 1,
    "robot_name": "Robot-001",
    "pending_commands": [
        {
            "command_id": 456,
            "command": "open_door",
            "command_display": "开门",
            "sent_at": "2024-01-15T10:30:00Z",
            "sent_by": "admin"
        },
        {
            "command_id": 457,
            "command": "start_delivery",
            "command_display": "开始配送",
            "sent_at": "2024-01-15T10:31:00Z",
            "sent_by": "admin"
        }
    ],
    "command_count": 2
}
```

**指令类型**:
- `open_door`: 开门
- `close_door`: 关门
- `start_delivery`: 开始配送
- `stop_robot`: 停止机器人
- `emergency_open_door`: 紧急开门

### 2. 执行指令并报告结果

机器人执行指令后报告执行结果。

```http
POST /api/robots/{robot_id}/execute_command/
Authorization: Bearer <token>
Content-Type: application/json

{
    "command_id": 456,
    "result": "门已成功打开"
}
```

**请求参数**:
- `command_id` (integer, required): 指令ID
- `result` (string, optional): 执行结果描述

**响应示例**:
```json
{
    "message": "指令执行成功",
    "command_id": 456,
    "status": "COMPLETED",
    "executed_at": "2024-01-15T10:31:00Z"
}
```

---

## 🚪 门控制系统

### 紧急按钮

紧急情况下立即开门，无需等待指令执行。

```http
POST /api/robots/{robot_id}/emergency_button/
Authorization: Bearer <token>
```

**响应示例**:
```json
{
    "message": "🚨 紧急按钮已触发！门已立即开启",
    "command_id": 789,
    "action": "emergency_open_door",
    "status": "COMPLETED",
    "door_status": "OPEN",
    "sent_at": "2024-01-15T10:30:00Z",
    "executed_at": "2024-01-15T10:30:00Z",
    "emergency": true
}
```

---

## 📱 二维码扫描系统

### 1. 开始等待二维码扫描

机器人到达目的地后开始等待用户扫描二维码。

```http
POST /api/robots/{robot_id}/start_qr_wait/
Authorization: Bearer <token>
Content-Type: application/json

{
    "order_id": 123
}
```

**请求参数**:
- `order_id` (integer, required): 订单ID

**响应示例**:
```json
{
    "message": "订单 123 开始等待二维码扫描",
    "qr_wait_start_time": "2024-01-15T10:30:00Z"
}
```

### 2. 二维码扫描处理

机器人扫描到二维码后处理扫描结果。

```http
POST /api/robots/{robot_id}/qr_scanned/
Authorization: Bearer <token>
Content-Type: application/json

{
    "order_id": 123,
    "qr_data": {
        "order_id": 123,
        "student_id": 456,
        "timestamp": "2024-01-15T10:30:00Z"
    }
}
```

**请求参数**:
- `order_id` (integer, required): 订单ID
- `qr_data` (object, required): 二维码扫描数据

**响应示例**:
```json
{
    "message": "订单 123 二维码扫描成功，包裹已取出",
    "order_id": 123,
    "status": "PICKED_UP",
    "qr_scanned_at": "2024-01-15T10:31:00Z"
}
```

---

## 🚚 配送流程管理

### 1. 到达目的地

机器人到达配送目的地时报告。

```http
POST /api/robots/{robot_id}/arrived_at_destination/
Authorization: Bearer <token>
Content-Type: application/json

{
    "order_id": 123
}
```

**响应示例**:
```json
{
    "message": "订单 123 已送达目的地",
    "order_id": 123,
    "status": "DELIVERED",
    "delivered_at": "2024-01-15T10:30:00Z"
}
```

### 2. 标记包裹已取出

确认包裹已被用户取出。

```http
POST /api/robots/{robot_id}/mark_picked_up/
Authorization: Bearer <token>
Content-Type: application/json

{
    "order_id": 123
}
```

**响应示例**:
```json
{
    "message": "订单 123 包裹已取出",
    "order_id": 123,
    "status": "PICKED_UP",
    "picked_up_at": "2024-01-15T10:31:00Z"
}
```

### 3. 开始配送

机器人开始配送流程。

```http
POST /api/robots/{robot_id}/start_delivery/
Authorization: Bearer <token>
Content-Type: application/json

{
    "action": "close_door_and_start"
}
```

**响应示例**:
```json
{
    "detail": "机器人已开始配送",
    "robot_id": 1,
    "status": "DELIVERING",
    "total_orders": 3
}
```

### 4. 自动返航

配送完成后自动返航到仓库。

```http
POST /api/robots/{robot_id}/auto_return/
Authorization: Bearer <token>
Content-Type: application/json

{
    "action": "return_to_warehouse"
}
```

**响应示例**:
```json
{
    "message": "机器人开始自动返航",
    "robot_id": 1,
    "status": "RETURNING",
    "return_start_time": "2024-01-15T10:35:00Z"
}
```

---

## 🔄 完整工作流程

### 典型配送流程

```mermaid
graph TD
    A[机器人启动] --> B[获取当前订单]
    B --> C[接收订单分配]
    C --> D[开始配送]
    D --> E[到达目的地]
    E --> F[等待二维码扫描]
    F --> G[扫描二维码]
    G --> H[开门取件]
    H --> I[标记包裹取出]
    I --> J{还有订单?}
    J -->|是| E
    J -->|否| K[自动返航]
    K --> L[返回仓库]
    L --> A
```

### 指令轮询流程

```mermaid
graph TD
    A[开始轮询] --> B[获取待执行指令]
    B --> C{有指令?}
    C -->|否| D[等待5秒]
    D --> B
    C -->|是| E[执行指令]
    E --> F[报告执行结果]
    F --> G[更新指令状态]
    G --> D
```

---

## ⚠️ 错误处理

### HTTP状态码

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 认证失败
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式

```json
{
    "detail": "错误描述信息",
    "error_code": 1001,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 常见错误码

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| 1001 | 未上传二维码图片 | 检查图片文件是否正确上传 |
| 1002 | 无法识别二维码 | 确保二维码清晰可见 |
| 1003 | 二维码数据解析失败 | 检查二维码格式是否正确 |
| 1004 | 二维码数据格式不完整 | 确保包含payload和signature |
| 1005 | payload解码失败 | 检查base64编码是否正确 |
| 1006 | 签名校验失败 | 验证二维码签名 |
| 1007 | payload内容解析失败 | 检查JSON格式是否正确 |
| 1008 | payload缺少必要字段 | 确保包含order_id和student_id |
| 1009 | 订单不存在或student_id不匹配 | 验证订单信息 |

---

## 🔧 最佳实践

### 1. 轮询策略

- **指令轮询**: 建议每5秒轮询一次
- **状态更新**: 建议每10秒更新一次状态
- **错误重试**: 网络错误时等待30秒后重试

### 2. 错误处理

```python
import requests
import time

def api_request_with_retry(url, headers, data=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            if data:
                response = requests.post(url, headers=headers, json=data, timeout=10)
            else:
                response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # 重新获取token
                refresh_token()
                continue
            else:
                print(f"API错误: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"网络错误: {e}")
            if attempt < max_retries - 1:
                time.sleep(30)
                continue
            else:
                raise
    
    return None
```

### 3. 状态同步

```python
def sync_robot_status(robot_id, token):
    """同步机器人状态"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 更新位置和电量
    status_data = {
        "location": get_current_location(),
        "battery": get_battery_level(),
        "door_status": get_door_status()
    }
    
    response = requests.post(
        f"/api/robots/{robot_id}/update_status/",
        headers=headers,
        json=status_data
    )
    
    return response.json()
```

### 4. 指令处理

```python
def handle_commands(robot_id, token):
    """处理待执行指令"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取待执行指令
    response = requests.get(
        f"/api/robots/{robot_id}/get_commands/",
        headers=headers
    )
    
    if response.status_code == 200:
        commands = response.json()["pending_commands"]
        
        for command in commands:
            command_id = command["command_id"]
            command_type = command["command"]
            
            # 执行指令
            result = execute_hardware_command(command_type)
            
            # 报告结果
            requests.post(
                f"/api/robots/{robot_id}/execute_command/",
                headers=headers,
                json={
                    "command_id": command_id,
                    "result": result
                }
            )
```

---

## 📞 技术支持

### 联系方式

- **技术支持邮箱**: support@example.com
- **技术文档**: https://docs.example.com
- **API状态**: https://status.example.com

### 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0.0 | 2024-01-15 | 初始版本发布 |
| v1.1.0 | 2024-01-20 | 新增紧急按钮功能 |
| v1.2.0 | 2024-01-25 | 优化二维码扫描流程 |

---

## 📄 许可证

本文档采用 MIT 许可证。详情请参阅 LICENSE 文件。

---

*最后更新时间: 2024年1月15日* 