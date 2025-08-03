# 📋 机器人配送系统 - 日志管理使用指南

## 🎯 概述

为了方便查看和管理机器人配送系统的所有日志，我们创建了一个统一的日志管理文件夹 `logs/`，包含三种不同类型的日志：

1. **🤖 机器人客户端日志** - 记录机器人运行状态
2. **🖥️ 后端系统日志** - 记录系统级事件
3. **🌐 前端操作日志** - 记录用户操作反馈

## 📁 日志文件夹结构

```
logs/
├── README.md              # 日志说明文档
├── robot_client.log       # 机器人客户端日志
├── system_backend.log     # 后端系统日志
├── frontend_operations.log # 前端操作日志模板
├── sync_logs.py          # 日志同步工具
├── view_all_logs.py      # 统一日志查看工具
├── clear_logs.py         # 日志清理工具
└── quick_view.sh         # 快速查看脚本
```

## 🚀 快速开始

### 方法1: 使用快速查看脚本 (推荐)

```bash
# 在项目根目录运行
./view_logs.sh
```

这会启动一个交互式菜单，让你选择要查看的日志类型。

### 方法2: 直接进入logs目录

```bash
cd logs
./quick_view.sh
```

### 方法3: 使用Python工具

```bash
cd logs
python view_all_logs.py
```

## 📊 日志类型详解

### 🤖 机器人客户端日志 (`robot_client.log`)

**来源**: 机器人客户端程序 (`robot_client/main_enhanced.py`)

**内容**:
- 机器人启动和初始化
- 网络连接状态
- 订单轮询结果
- 状态更新反馈
- 硬件操作模拟
- 错误和异常信息

**示例**:
```
[2025-07-31 16:28:23] INFO: 状态更新成功: 状态更新成功
[2025-07-31 16:28:23] INFO: 📍 位置: Warehouse, 🔋 电池: 100%
[2025-07-31 16:28:25] INFO: 获取订单成功，订单数量: 1
```

### 🖥️ 后端系统日志 (`system_backend.log`)

**来源**: Django后端数据库 (SystemLog表)

**内容**:
- API调用记录
- 用户操作事件
- 机器人控制命令
- 订单状态变更
- 系统错误和警告
- 业务逻辑事件

**示例**:
```
[2025-07-31 08:25:52] INFO - 机器人 Robot-001 状态更新: 位置=Warehouse, 电池=100%, 门=CLOSED
[2025-07-31 08:21:19] SUCCESS - 机器人 Robot-001 关门成功
[2025-07-31 08:21:19] SUCCESS - 机器人 Robot-001 开门成功
```

### 🌐 前端操作日志 (`frontend_operations.log`)

**来源**: 前端用户操作 (临时显示)

**内容**:
- 用户按钮点击
- API调用结果
- 操作成功/失败反馈
- 实时状态更新

**示例**:
```
[4:21:19 PM] ✅ 机器人控制成功: close_door - 机器人 Robot-001 关门成功
[4:21:19 PM] ✅ 机器人控制成功: open_door - 机器人 Robot-001 开门成功
[4:21:19 PM] ✅ 订单状态更新成功: 订单 #1 状态更新为 ASSIGNED
```

## 🔧 日志管理工具

### 1. 日志同步工具 (`sync_logs.py`)

```bash
cd logs
python sync_logs.py
```

**功能**:
- 同步机器人客户端日志
- 从数据库获取系统日志
- 创建前端日志模板

### 2. 统一日志查看工具 (`view_all_logs.py`)

```bash
cd logs
python view_all_logs.py [命令] [参数]
```

**命令选项**:
- `python view_all_logs.py` - 查看所有日志摘要
- `python view_all_logs.py robot [行数]` - 查看机器人日志
- `python view_all_logs.py system [行数]` - 查看系统日志
- `python view_all_logs.py frontend` - 查看前端日志说明
- `python view_all_logs.py summary` - 查看日志统计
- `python view_all_logs.py monitor` - 实时监控日志
- `python view_all_logs.py sync` - 同步日志文件

### 3. 日志清理工具 (`clear_logs.py`)

```bash
cd logs
python clear_logs.py [命令]
```

**命令选项**:
- `python clear_logs.py robot` - 清理机器人日志
- `python clear_logs.py system` - 清理系统日志
- `python clear_logs.py all` - 清理所有日志
- `python clear_logs.py backups` - 查看备份文件

## 📈 日志监控

### 实时监控

```bash
# 监控所有日志文件
tail -f logs/robot_client.log logs/system_backend.log

# 使用Python工具监控
cd logs
python view_all_logs.py monitor
```

### 日志统计

```bash
cd logs
python view_all_logs.py summary
```

输出示例:
```
📊 日志摘要
============================================================
🤖 机器人日志: 906 行
🖥️ 系统日志: 25 行
🌐 前端日志: 模板文件
📈 总日志行数: 931 行
```

## 🔍 常见使用场景

### 1. 调试机器人问题

```bash
# 查看机器人最新日志
cd logs
tail -n 50 robot_client.log

# 实时监控机器人状态
tail -f robot_client.log
```

### 2. 检查系统事件

```bash
# 查看系统日志
cd logs
python view_all_logs.py system 50

# 查看特定类型的日志
grep "SUCCESS" system_backend.log
```

### 3. 监控用户操作

```bash
# 查看前端操作日志模板
cd logs
cat frontend_operations.log

# 实时监控所有日志
python view_all_logs.py monitor
```

### 4. 日志维护

```bash
# 清理旧日志
cd logs
python clear_logs.py all

# 查看备份文件
python clear_logs.py backups
```

## ⚠️ 注意事项

1. **日志文件大小**: 机器人日志会持续增长，建议定期清理
2. **备份重要**: 清理前会自动备份，重要日志请及时保存
3. **权限问题**: 确保有读写logs目录的权限
4. **实时性**: 系统日志需要手动同步，机器人日志实时更新
5. **前端日志**: 前端日志是临时的，刷新页面后消失

## 🎯 最佳实践

1. **定期同步**: 每天运行一次 `sync_logs.py` 同步最新日志
2. **定期清理**: 每周清理一次旧日志，避免文件过大
3. **实时监控**: 调试时使用实时监控功能
4. **备份重要日志**: 重要事件后及时备份相关日志
5. **分类查看**: 根据问题类型选择对应的日志文件

## 🆘 故障排除

### 问题1: 日志文件不存在

```bash
cd logs
python sync_logs.py
```

### 问题2: 权限错误

```bash
chmod +x logs/quick_view.sh
chmod +x view_logs.sh
```

### 问题3: Python工具无法运行

```bash
# 确保在虚拟环境中
source ../PACKAGE/bin/activate
cd logs
python view_all_logs.py
```

### 问题4: 日志不同步

```bash
# 检查后端服务是否运行
docker-compose ps

# 手动同步日志
cd logs
python sync_logs.py
```

---

**📞 如有问题，请查看 `logs/README.md` 或联系技术支持。** 