# 快递系统API文档

## 🚀 新实现的API功能

### 1. 机器人当前订单查询
```
GET /api/robots/{robot_id}/current_orders/
```

**响应示例**：
```json
{
  "robot_id": 1,
  "robot_name": "Robot-001",
  "status": "LOADING",
  "current_orders": [
    {
      "order_id": 1,
      "status": "ASSIGNED",
      "student": {
        "id": 2,
        "name": "张三",
        "email": "zhangsan@example.com"
      },
      "package_info": {
        "type": "书籍",
        "weight": "2kg",
        "fragile": false
      },
      "delivery_location": {
        "building": "宿舍楼A",
        "room": "502"
      },
      "qr_code_data": {
        "payload": "{\"order_id\":1,\"student_id\":2}",
        "signature": "abc123...",
        "qr_image_url": "data:image/png;base64,..."
      }
    }
  ],
  "delivery_route": [
    {
      "sequence": 1,
      "order_id": 1,
      "location": "宿舍楼A-502"
    }
  ],
  "summary": {
    "total_orders": 4,
    "loaded_orders": 2,
    "estimated_total_time": "60分钟"
  }
}
```

### 2. 接收订单分配（批量分配）
```
POST /api/robots/{robot_id}/receive_orders/
```

**请求体**：
```json
{
  "order_ids": [1, 2, 3, 4]
}
```

**响应**：返回所有分配订单的完整信息

### 3. 单个订单状态更新（装货过程）
```
PATCH /api/dispatch/orders/{order_id}/
```

**请求体**：
```json
{
  "status": "DELIVERING"
}
```

**响应**（当状态更新为"配送中"时）：
```json
{
  "detail": "订单 1 状态已更新为 DELIVERING",
  "order_data": {
    "order_id": 1,
    "status": "DELIVERING",
    "student": {
      "id": 2,
      "name": "张三",
      "email": "zhangsan@example.com"
    },
    "package_info": {
      "type": "书籍",
      "weight": "2kg",
      "fragile": false
    },
    "delivery_location": {
      "building": "宿舍楼A",
      "room": "502"
    },
    "qr_code_data": {
      "payload": "{\"order_id\":1,\"student_id\":2}",
      "signature": "abc123...",
      "qr_image_url": "data:image/png;base64,..."
    },
    "action": "order_loaded",
    "timestamp": "2024-12-19T10:30:00Z"
  },
  "robot_id": 1,
  "robot_name": "Robot-001"
}
```

### 4. 开始配送
```
POST /api/robots/{robot_id}/start_delivery/
```

**请求体**：
```json
{
  "action": "close_door_and_start"
}
```

## 📊 数据库改进

### 新增字段
- `delivery_room`: 具体房间号
- `qr_payload_data`: 二维码payload数据
- `qr_signature`: 二维码签名
- `robot`: 机器人关联

### 二维码数据结构
```json
{
  "order_id": 1,
  "student_id": 2,
  "student_name": "张三",
  "delivery_building": "宿舍楼A",
  "delivery_room": "502",
  "package_type": "书籍"
}
```

## 🔄 正确的业务流程

### 1. **订单创建** 
- 学生创建订单
- 系统自动生成完整二维码数据

### 2. **订单分配** 
- 管理员选择多个订单
- 批量分配给指定机器人
- 机器人接收到所有订单的基本信息

### 3. **装货过程** ⭐ **关键步骤**
- **一个一个装货**：每装一个订单，就修改该订单状态
- **实时数据推送**：每修改一个订单状态为"配送中"，立即发送该订单的完整JSON数据给机器人
- **机器人实时接收**：机器人可以实时获取每个装货完成的订单详细信息

### 4. **装货完成**
- 所有订单都装完后，机器人开始自主巡航配送

### 5. **送达确认**
- 到达目的地后，扫描二维码验证用户身份

## 🎯 快递车监听方案

### 方式1：轮询查询
```javascript
setInterval(async () => {
  const response = await fetch('/api/robots/{robot_id}/current_orders/');
  const data = await response.json();
  
  if (data.status === 'LOADING') {
    displayOrders(data.current_orders);
  } else if (data.status === 'DELIVERING') {
    startAutonomousDelivery(data.current_orders);
  }
}, 5000);
```

### 方式2：监听状态更新API
```javascript
// 每次装货完成后，前端会调用状态更新API
// 机器人可以监听这个API的响应来获取订单数据
async function updateOrderStatus(orderId, newStatus) {
  const response = await fetch(`/api/dispatch/orders/${orderId}/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: newStatus })
  });
  
  const data = await response.json();
  if (data.order_data && data.order_data.action === 'order_loaded') {
    // 接收到装货完成的订单数据
    handleOrderLoaded(data.order_data);
  }
}
``` 