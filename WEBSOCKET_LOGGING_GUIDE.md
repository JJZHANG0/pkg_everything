# 🔌 WebSocket专业日志系统使用指南

## 概述

我们为WebSocket通信建立了一个全面、专业的日志系统，提供详细的连接、消息、性能和错误记录。

## 日志文件结构

### 📁 日志文件位置
```
/app/logs/
├── websocket_detailed.log    # 详细日志 (DEBUG级别)
├── websocket_events.log      # 重要事件日志 (INFO级别)
└── system_backend.log        # 系统后端日志
```

### 📊 日志级别说明
- **DEBUG**: 详细调试信息，包括所有消息收发
- **INFO**: 重要事件，如连接建立、断开、指令执行
- **WARNING**: 警告信息，如安全事件
- **ERROR**: 错误信息，如连接失败、指令执行失败

## 日志内容详解

### 🔗 连接事件日志

#### 连接尝试
```
[2024-01-01 12:00:00] INFO [WebSocket] [Robot-1:快递小车1] CONNECTION_ATTEMPT: WebSocket连接尝试 | IP: 192.168.1.100 | User-Agent: Python/3.8 websockets/11.0...
```

#### 连接建立
```
[2024-01-01 12:00:01] INFO [WebSocket] ✅ [Robot-1:快递小车1] CONNECTION_ESTABLISHED: WebSocket连接已建立 | IP: 192.168.1.100 | Connection-ID: robot_1!abc123
```

#### 连接断开
```
[2024-01-01 12:05:00] INFO [WebSocket] 🔌 [Robot-1:快递小车1] CONNECTION_CLOSED: WebSocket连接已关闭 | IP: 192.168.1.100 | Code: 1000 | Reason: 正常断开
```

#### 连接失败
```
[2024-01-01 12:00:00] ERROR [WebSocket] ❌ [Robot-1:快递小车1] CONNECTION_FAILED: WebSocket连接失败 | IP: 192.168.1.100 | Error: 认证失败 | Code: 4002
```

### 💬 消息事件日志

#### 接收消息
```
[2024-01-01 12:01:00] DEBUG [WebSocket] 📥 [Robot-1:快递小车1] MESSAGE_RECEIVED: 收到消息 | Type: status_update | IP: 192.168.1.100 | Data: {"status": "IDLE", "battery": 85}
```

#### 发送消息
```
[2024-01-01 12:01:05] DEBUG [WebSocket] 📤 [Robot-1:快递小车1] MESSAGE_SENT: 发送消息 | Type: command | IP: 192.168.1.100 | Data: {"command": "open_door", "command_id": 123}
```

### ⚡ 指令执行日志

#### 指令执行成功
```
[2024-01-01 12:02:00] INFO [WebSocket] ⚡ [Robot-1:快递小车1] COMMAND_EXECUTED: 指令执行完成 | Command: open_door | Result: door_open | Time: 0.125s
```

#### 指令执行失败
```
[2024-01-01 12:02:00] ERROR [WebSocket] 💥 [Robot-1:快递小车1] COMMAND_FAILED: 指令执行失败 | Command: open_door | Error: 硬件故障
```

### 💓 心跳日志
```
[2024-01-01 12:03:00] DEBUG [WebSocket] 💓 [Robot-1:快递小车1] HEARTBEAT: 收到心跳 | IP: 192.168.1.100
```

### 📊 性能指标日志
```
[2024-01-01 12:01:05] INFO [WebSocket] 📊 [Robot-1:快递小车1] PERFORMANCE: 性能指标 | command_send_time: 0.045s
```

### 🔒 安全事件日志
```
[2024-01-01 12:00:00] WARNING [WebSocket] 🔒 [Robot-1:快递小车1] SECURITY: 安全事件 | 无效token尝试 | Details: {"ip": "192.168.1.101", "token": "invalid_token"}
```

### 🚨 错误日志
```
[2024-01-01 12:00:00] ERROR [WebSocket] 🚨 [Robot-1:快递小车1] ERROR: 发生错误: 消息格式错误 | Context: {"client_ip": "192.168.1.100", "raw_data": "invalid json"}
```

## 日志查看工具

### 🔍 基本用法

#### 查看最近的事件日志
```bash
python view_websocket_logs.py --type events --lines 50
```

#### 查看详细日志
```bash
python view_websocket_logs.py --type detailed --lines 100
```

#### 按级别过滤
```bash
python view_websocket_logs.py --type events --level ERROR
```

#### 按机器人ID过滤
```bash
python view_websocket_logs.py --type events --robot-id 1
```

### 📊 统计功能

#### 显示连接统计
```bash
python view_websocket_logs.py --stats
```
输出示例：
```
📊 WebSocket连接统计
==================================================
🔗 总连接数: 15
🟢 活跃连接: 3
🔴 失败连接: 2
💬 总消息数: 1,247

🤖 机器人统计:
  Robot-1: 8 连接, 856 消息
  Robot-2: 7 连接, 391 消息
```

#### 显示性能指标
```bash
python view_websocket_logs.py --performance
```
输出示例：
```
⚡ WebSocket性能指标
==================================================
📤 平均指令发送时间: 0.045s
⚡ 平均指令执行时间: 0.125s

💬 消息类型统计:
  status_update: 456 条
  command: 123 条
  heartbeat: 668 条
```

#### 显示错误日志
```bash
python view_websocket_logs.py --errors 24
```

### 🔴 实时监控

#### 实时监控事件日志
```bash
python view_websocket_logs.py --live --type events
```

#### 实时监控特定机器人
```bash
python view_websocket_logs.py --live --type events --robot-id 1
```

## 数据库日志

除了文件日志，WebSocket事件也会记录到数据库的 `SystemLog` 表中：

### 📋 日志类型
- `WEBSOCKET_CONNECTION`: 连接相关事件
- `WEBSOCKET_MESSAGE`: 消息收发事件
- `WEBSOCKET_COMMAND`: 指令执行事件
- `WEBSOCKET_ERROR`: 错误事件
- `WEBSOCKET_SECURITY`: 安全事件

### 🔍 查询示例

#### 查看WebSocket连接日志
```sql
SELECT * FROM core_systemlog 
WHERE log_type LIKE 'WEBSOCKET%' 
ORDER BY timestamp DESC 
LIMIT 50;
```

#### 查看特定机器人的日志
```sql
SELECT * FROM core_systemlog 
WHERE log_type LIKE 'WEBSOCKET%' 
AND data->>'$.robot_id' = '1'
ORDER BY timestamp DESC;
```

## 日志分析技巧

### 🔍 故障排查

1. **连接问题**：
   ```bash
   # 查看连接失败日志
   python view_websocket_logs.py --type events --level ERROR | grep CONNECTION
   ```

2. **指令执行问题**：
   ```bash
   # 查看指令执行失败
   python view_websocket_logs.py --type events --level ERROR | grep COMMAND
   ```

3. **性能问题**：
   ```bash
   # 查看性能指标
   python view_websocket_logs.py --performance
   ```

### 📈 监控建议

1. **定期检查错误日志**：
   ```bash
   # 每小时检查一次错误
   python view_websocket_logs.py --errors 1
   ```

2. **监控连接状态**：
   ```bash
   # 实时监控连接事件
   python view_websocket_logs.py --live --type events
   ```

3. **性能监控**：
   ```bash
   # 定期检查性能指标
   python view_websocket_logs.py --performance
   ```

## 日志轮转

### 🔄 自动轮转配置

建议配置日志轮转以避免日志文件过大：

```bash
# 创建日志轮转配置
sudo nano /etc/logrotate.d/websocket-logs
```

配置内容：
```
/app/logs/websocket_*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        systemctl reload rsyslog
    endscript
}
```

### 🧹 手动清理

```bash
# 清理30天前的日志
find /app/logs -name "websocket_*.log.*" -mtime +30 -delete

# 压缩旧日志
gzip /app/logs/websocket_*.log.1
```

## 安全注意事项

### 🔐 敏感信息处理

- 自动脱敏：token、password等敏感字段会被自动脱敏
- 数据清理：只记录必要的信息，避免泄露敏感数据

### 📊 访问控制

- 日志文件权限：建议设置为644，只允许管理员访问
- 数据库日志：通过Django权限系统控制访问

## 最佳实践

1. **定期检查**：每天检查一次错误日志
2. **性能监控**：定期查看性能指标
3. **容量管理**：及时清理旧日志文件
4. **备份重要日志**：定期备份重要的日志数据
5. **告警设置**：为严重错误设置告警机制

## 故障排除

### 常见问题

1. **日志文件不存在**：
   - 检查Docker容器是否正常运行
   - 确认日志目录权限

2. **日志不更新**：
   - 检查WebSocket连接是否正常
   - 确认日志配置是否正确

3. **日志文件过大**：
   - 配置日志轮转
   - 清理旧日志文件

### 调试命令

```bash
# 检查日志文件状态
ls -la /app/logs/websocket_*.log

# 检查日志文件大小
du -h /app/logs/websocket_*.log

# 检查最新日志
tail -f /app/logs/websocket_events.log
```

这个专业的WebSocket日志系统为你提供了全面的监控和分析能力，帮助你更好地管理和调试WebSocket通信！ 