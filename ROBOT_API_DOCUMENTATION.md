# 🤖 机器人API技术文档

## 📋 概述

本文档描述了校园快递配送系统的机器人控制API接口。系统支持完整的订单状态管理，从订单创建到包裹送达的完整流程。

## 🔄 订单状态流程

### 正常流程
```
PENDING → ASSIGNED → DELIVERING → DELIVERED → PICKED_UP
```

### 超时处理
```
DELIVERED → CANCELLED (超时未取)
```

### 状态说明
- **PENDING**: 待分配
- **ASSIGNED**: 已装入机器人
- **DELIVERING**: 配送中
- **DELIVERED**: 已送达
- **PICKED_UP**: 已取出
- **CANCELLED**: 已作废（超时未取）

## 🔐 认证

所有API请求都需要JWT认证。获取token：

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

在请求头中包含token：
```bash
Authorization: Bearer <your_token>
```

## 📦 订单管理API

### 创建订单
```http
POST /api/orders/
Content-Type: application/json
Authorization: Bearer <token>

{
  "student": 1,
  "package_description": "包裹描述",
  "pickup_location": "取件地点",
  "delivery_location": "配送地点",
  "status": "PENDING"
}
```

### 分配订单
```http
PATCH /api/dispatch/orders/{order_id}/
Content-Type: application/json
Authorization: Bearer <token>

{
  "status": "ASSIGNED"
}
```

**注意**: 当订单状态更新为`ASSIGNED`时，系统会自动：
- 分配空闲机器人给订单
- 将机器人状态设置为`LOADING`

## 🤖 机器人控制API

### 获取机器人状态
```http
GET /api/robots/{robot_id}/status/
Authorization: Bearer <token>
```

### 发送控制指令给机器人
```http
POST /api/robots/{robot_id}/control/
Content-Type: application/json
Authorization: Bearer <token>

{
  "action": "start_delivery" | "stop_robot" | "open_door" | "close_door"
}
```

**功能**:
- 服务器向机器人发送控制指令
- 指令存储在数据库中，状态为`PENDING`
- 机器人需要轮询获取指令并执行

**响应示例**:
```json
{
  "message": "控制指令已发送给机器人 Robot-001",
  "command_id": 123,
  "action": "start_delivery",
  "status": "PENDING",
  "sent_at": "2025-07-31T10:30:00Z"
}
```

### 机器人获取待执行指令
```http
GET /api/robots/{robot_id}/get_commands/
Authorization: Bearer <token>
```

**功能**:
- 机器人轮询获取待执行的指令
- 返回所有状态为`PENDING`的指令

**响应示例**:
```json
{
  "robot_id": 1,
  "robot_name": "Robot-001",
  "pending_commands": [
    {
      "command_id": 123,
      "command": "start_delivery",
      "command_display": "开始配送",
      "sent_at": "2025-07-31T10:30:00Z",
      "sent_by": "admin"
    }
  ],
  "command_count": 1
}
```

### 机器人执行指令并报告结果
```http
POST /api/robots/{robot_id}/execute_command/
Content-Type: application/json
Authorization: Bearer <token>

{
  "command_id": 123,
  "result": "执行成功"
}
```

**功能**:
- 机器人执行指令后向服务器报告结果
- 服务器更新指令状态为`COMPLETED`
- 根据指令类型执行相应的状态更新

### 机器人到达目的地
```http
POST /api/robots/{robot_id}/arrived_at_destination/
Content-Type: application/json
Authorization: Bearer <token>

{
  "order_id": 123
}
```

**功能**:
- 将指定订单状态从`DELIVERING`更新为`DELIVERED`
- 开始等待用户扫描二维码
- 设置机器人的`qr_wait_start_time`

### 扫描二维码
```http
POST /api/robots/{robot_id}/qr_scanned/
Content-Type: application/json
Authorization: Bearer <token>

{
  "qr_data": "order_123",
  "order_id": 123
}
```

**功能**:
- 验证二维码数据
- 将订单状态从`DELIVERED`更新为`PICKED_UP`
- 清除机器人的二维码等待状态

### 标记包裹已取出
```http
POST /api/robots/{robot_id}/mark_picked_up/
Content-Type: application/json
Authorization: Bearer <token>

{
  "order_id": 123
}
```

**功能**:
- 手动标记包裹已取出
- 要求订单状态为`DELIVERED`
- 将订单状态更新为`PICKED_UP`

### 自动返航（超时处理）
```http
POST /api/robots/{robot_id}/auto_return/
Content-Type: application/json
Authorization: Bearer <token>

{}
```

**功能**:
- 处理超时未取的包裹
- 将所有`DELIVERED`状态的订单更新为`CANCELLED`
- 将机器人状态设置为`RETURNING`
- 清除二维码等待状态

## 📊 系统日志API

### 获取系统日志
```http
GET /api/logs/
Authorization: Bearer <token>
```

### 获取日志摘要
```http
GET /api/logs/summary/
Authorization: Bearer <token>
```

## 🔍 完整工作流程示例

### 1. 创建订单
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "student": 1,
    "package_description": "测试包裹",
    "pickup_location": "图书馆",
    "delivery_location": "宿舍楼",
    "status": "PENDING"
  }'
```

### 2. 分配订单
```bash
curl -X PATCH http://localhost:8000/api/dispatch/orders/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"status": "ASSIGNED"}'
```

### 3. 发送开始配送指令
```bash
curl -X POST http://localhost:8000/api/robots/1/control/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"action": "start_delivery"}'
```

### 4. 机器人获取指令（机器人端）
```bash
curl -X GET http://localhost:8000/api/robots/1/get_commands/ \
  -H "Authorization: Bearer <token>"
```

### 5. 机器人执行指令并报告结果（机器人端）
```bash
curl -X POST http://localhost:8000/api/robots/1/execute_command/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "command_id": 123,
    "result": "开始配送成功"
  }'
```

### 6. 到达目的地
```bash
curl -X POST http://localhost:8000/api/robots/1/arrived_at_destination/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"order_id": 1}'
```

### 7. 扫描二维码
```bash
curl -X POST http://localhost:8000/api/robots/1/qr_scanned/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "qr_data": "order_1",
    "order_id": 1
  }'
```

## ⚠️ 错误处理

### 常见错误码
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 认证失败
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式
```json
{
  "detail": "错误描述信息"
}
```

## 🔧 开发环境

### 启动服务
```bash
cd docker_deploy
docker-compose up -d
```

### 访问地址
- 前端: http://localhost:3000
- 后端API: http://localhost:8000/api/
- 管理后台: http://localhost:8000/admin/

## 📝 更新日志

### v2.1.0 (2025-07-31)
- ✅ 重构机器人控制机制：服务器控制机器人
- ✅ 新增`RobotCommand`模型管理控制指令
- ✅ 新增`get_commands` API端点（机器人获取指令）
- ✅ 新增`execute_command` API端点（机器人执行指令）
- ✅ 优化指令状态管理（PENDING → EXECUTING → COMPLETED）
- ✅ 完善指令执行日志记录

### v2.0.0 (2025-07-31)
- ✅ 新增完整的订单状态流程
- ✅ 新增`arrived_at_destination` API端点
- ✅ 新增`mark_picked_up` API端点
- ✅ 新增`auto_return` API端点（超时处理）
- ✅ 新增`CANCELLED`订单状态
- ✅ 优化机器人状态与订单状态同步
- ✅ 完善系统日志记录

### v1.0.0 (2025-07-30)
- ✅ 基础机器人控制功能
- ✅ 订单管理系统
- ✅ 用户认证系统
- ✅ 系统日志记录 