# 📋 机器人配送系统日志管理

这个文件夹包含了机器人配送系统的所有日志文件，方便统一管理和查看。

## 📁 日志文件说明

### 🤖 `robot_client.log`
- **来源**: 机器人客户端 (`robot_client/logs/robot.log`)
- **内容**: 机器人运行状态、硬件操作、网络通信
- **更新频率**: 实时更新
- **查看命令**: `tail -f logs/robot_client.log`

### 🖥️ `system_backend.log`
- **来源**: Django后端数据库 (SystemLog表)
- **内容**: 系统级事件、API调用、状态变更
- **更新频率**: 事件触发时更新
- **查看命令**: `tail -f logs/system_backend.log`

### 🌐 `frontend_operations.log`
- **来源**: 前端用户操作
- **内容**: 用户操作反馈、按钮点击、API调用结果
- **更新频率**: 用户操作时更新
- **查看命令**: `tail -f logs/frontend_operations.log`

## 🚀 快速查看命令

```bash
# 查看所有日志的最新内容
./view_all_logs.py

# 查看机器人日志
tail -f logs/robot_client.log

# 查看系统日志
tail -f logs/system_backend.log

# 查看前端操作日志
tail -f logs/frontend_operations.log

# 查看所有日志（实时）
tail -f logs/*.log
```

## 📊 日志格式说明

### 机器人日志格式
```
[时间戳] 级别: 消息内容
[2025-07-31 16:21:21] INFO: 状态更新成功
```

### 系统日志格式
```
[时间戳] 级别 - 消息内容
[2025-07-31 08:21:19] SUCCESS - 机器人 Robot-001 关门成功
```

### 前端日志格式
```
[时间] ✅/❌ 操作结果: 详细信息
[4:21:19 PM] ✅ 机器人控制成功: close_door - 机器人 Robot-001 关门成功
```

## 🔧 日志管理工具

- `view_all_logs.py`: 统一查看所有日志
- `clear_logs.py`: 清理旧日志文件
- `log_analyzer.py`: 日志分析工具

## 📈 日志统计

- 机器人日志: 实时记录，文件大小持续增长
- 系统日志: 存储在数据库中，可通过API查询
- 前端日志: 临时显示，刷新页面后消失

---

**注意**: 日志文件会持续增长，建议定期清理旧日志以节省磁盘空间。 