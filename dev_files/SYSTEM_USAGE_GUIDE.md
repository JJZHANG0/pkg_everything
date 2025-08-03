# 机器人配送系统使用指南

## 🎯 系统概述

这是一个完整的机器人配送系统，包含前端管理界面、后端API服务和机器人客户端。系统实现了从订单创建到配送完成的完整流程。

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端管理系统   │    │   Django后端    │    │   机器人客户端   │
│  (React + Nginx)│◄──►│  (DRF + MySQL)  │◄──►│  (Python + ROS) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 快速开始

### 1. 启动系统

```bash
# 启动Docker容器
cd docker_deploy
docker-compose up -d

# 访问前端
http://localhost:3000

# 访问后端API
http://localhost:8000
```

### 2. 创建管理员账户

```bash
# 进入Django容器
docker exec -it drf_backend bash

# 创建超级用户
python manage.py createsuperuser
# 用户名: root
# 密码: test123456
```

### 3. 启动机器人客户端

```bash
# 激活虚拟环境
source PACKAGE/bin/activate

# 启动增强版机器人客户端
cd robot_client
python main_enhanced.py
```

## 📋 完整工作流程

### 1. 订单管理流程

#### 1.1 创建订单
1. 学生/老师登录系统
2. 填写配送信息（取件地点、配送地点、包裹信息）
3. 系统自动生成二维码
4. 订单状态：`PENDING`

#### 1.2 订单分配
1. 管理员登录Dispatcher页面
2. 选择订单，状态改为`ASSIGNED`
3. 系统自动分配机器人
4. 机器人状态变为`LOADING`

#### 1.3 装货过程
1. 管理员将包裹装入机器人
2. 点击"关门"按钮
3. 点击"启动配送"按钮
4. 机器人状态变为`DELIVERING`

### 2. 配送流程

#### 2.1 自主配送
1. 机器人开始自主导航到配送点
2. 每5秒向服务器反馈位置和状态
3. 到达配送点后开始等待二维码扫描

#### 2.2 二维码验证
1. 用户扫描机器人上的二维码
2. 系统验证二维码有效性
3. 机器人自动开门
4. 用户取走包裹
5. 15秒后机器人自动关门
6. 订单状态更新为`PICKED_UP`

#### 2.3 超时处理
- 如果10分钟内无人扫描二维码
- 机器人自动开始返航
- 订单状态保持为`DELIVERING`

#### 2.4 返航流程
1. 机器人返回仓库
2. 状态变为`IDLE`
3. 管理员可以点击"开门"按钮
4. 取出剩余包裹或装入新包裹

## 🎮 前端界面操作

### Dispatcher控制面板

#### 机器人状态显示
- **状态**: IDLE/LOADING/DELIVERING/RETURNING
- **位置**: 当前所在位置
- **电池**: 电池电量百分比
- **门状态**: OPEN/CLOSED

#### 控制按钮
1. **🚪 开门**: 远程控制机器人开门
2. **🚪 关门**: 远程控制机器人关门
3. **🚀 启动配送**: 开始配送流程
4. **⏹️ 停止机器人**: 紧急停止

#### 订单管理
- 查看所有订单状态
- 修改订单状态（PENDING → ASSIGNED → DELIVERING → DELIVERED → PICKED_UP）
- 实时状态更新

#### 系统日志
- 实时显示系统操作日志
- 记录所有机器人操作和状态变化
- 错误和警告信息

## 🔧 机器人客户端功能

### 核心功能
1. **自动轮询**: 每3秒获取最新订单信息
2. **状态反馈**: 每5秒向服务器反馈位置和状态
3. **二维码扫描**: 自动扫描和验证二维码
4. **自主导航**: 模拟自主导航到配送点
5. **超时处理**: 10分钟无人取货自动返航

### 状态管理
- **IDLE**: 空闲状态，等待订单
- **LOADING**: 装货中，等待管理员操作
- **DELIVERING**: 配送中，正在前往配送点
- **RETURNING**: 返航中，返回仓库

### 硬件模拟
- **门控制**: 模拟开门/关门动作
- **蜂鸣器**: 新订单提醒
- **LED指示灯**: 状态指示
- **摄像头**: 二维码扫描

## 📊 系统监控

### 日志系统
- **操作日志**: 记录所有用户操作
- **机器人日志**: 记录机器人状态变化
- **错误日志**: 记录系统错误和异常
- **配送日志**: 记录配送过程

### 实时监控
- 机器人位置实时更新
- 电池电量监控
- 门状态监控
- 订单状态跟踪

## 🔒 安全机制

### 认证授权
- JWT Token认证
- 基于角色的权限控制
- API访问控制

### 数据安全
- 二维码签名验证
- 订单状态验证
- 操作日志记录

## 🧪 测试系统

### 功能测试
```bash
# 运行完整系统测试
python test_complete_system.py
```

### API测试
```bash
# 测试机器人控制API
curl -X POST http://localhost:8000/api/robots/1/control/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"action": "open_door"}'
```

## 📝 配置说明

### 环境变量
```bash
# 机器人配置
ROBOT_ID=1
ROBOT_NAME=Robot-001
SERVER_URL=http://localhost:8000

# 轮询配置
POLL_INTERVAL=3
STATUS_FEEDBACK_INTERVAL=5

# 超时配置
QR_WAIT_TIMEOUT=600  # 10分钟
```

### 数据库配置
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'robot_delivery',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'mysql',
        'PORT': '3306',
    }
}
```

## 🚨 故障排除

### 常见问题

#### 1. 机器人无法连接服务器
- 检查网络连接
- 验证服务器地址和端口
- 检查JWT Token是否有效

#### 2. 二维码扫描失败
- 检查摄像头权限
- 验证二维码数据格式
- 确认二维码是否已失效

#### 3. 订单状态不更新
- 检查数据库连接
- 验证API权限
- 查看系统日志

#### 4. 前端页面无法访问
- 检查Docker容器状态
- 验证端口映射
- 检查Nginx配置

### 日志查看
```bash
# 查看Django日志
docker logs drf_backend

# 查看前端日志
docker logs react_frontend

# 查看机器人客户端日志
tail -f robot_client/logs/robot.log
```

## 📞 技术支持

### 联系方式
- **技术支持**: tech-support@robot-delivery.com
- **文档更新**: 2025-07-30
- **系统版本**: v1.0

### 更新日志
- **v1.0**: 初始版本，包含完整的配送流程
- 支持机器人远程控制
- 实现二维码验证系统
- 添加完整的日志记录
- 支持自动返航功能

---

*本文档将根据系统更新持续维护，请关注最新版本。* 