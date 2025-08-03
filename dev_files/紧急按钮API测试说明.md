# 🚨 紧急按钮API测试说明

## 📋 概述

本文档提供了测试紧急按钮API的Python脚本和使用说明。

## 📁 文件说明

### 1. `smart_emergency_test.py` - 智能版测试脚本 ⭐ **推荐**
- **功能**：智能处理URL格式，自动添加协议和端口
- **特点**：用户友好，错误提示详细，自动连接测试
- **适用**：所有用户，特别是初学者

### 2. `test_emergency_button_api.py` - 完整测试脚本
- **功能**：全面的API测试，包括正常请求、异常处理、状态检查等
- **特点**：交互式配置，详细的测试报告
- **适用**：开发和调试阶段

### 3. `simple_emergency_test.py` - 简化测试脚本
- **功能**：快速测试紧急按钮API的基本功能
- **特点**：代码简洁，易于修改配置
- **适用**：日常测试和验证

## 🚀 使用方法

### 前置条件
1. 确保服务器正在运行
2. 确保网络连接正常
3. 安装Python和requests库：`pip install requests`

### 智能版测试（强烈推荐）

1. **运行智能测试**：
   ```bash
   python3 smart_emergency_test.py
   ```

2. **按提示输入**：
   - 服务器地址：直接输入IP或域名（如：`192.168.110.148`）
   - 机器人ID：默认为1
   - 用户名：默认为root
   - 密码：默认为root

3. **自动处理**：
   - 自动添加 `http://` 协议前缀
   - 自动添加 `:8000` 端口号
   - 自动测试服务器连接
   - 详细的错误提示和解决方案

### 快速测试

1. **修改配置**：
   打开 `simple_emergency_test.py`，修改以下参数：
   ```python
   SERVER_URL = "http://192.168.110.148:8000"  # 你的服务器地址（包含协议和端口）
   ROBOT_ID = 1                          # 你的机器人ID
   USERNAME = "root"                     # 你的用户名
   PASSWORD = "root"                     # 你的密码
   ```

2. **运行测试**：
   ```bash
   python3 simple_emergency_test.py
   ```

## 📡 API接口详情

### 请求信息
- **URL**：`POST /api/robots/{robot_id}/emergency_button/`
- **认证**：Bearer Token
- **Content-Type**：application/json

### 请求体
```json
{
    "action": "emergency_open_door"
}
```

### 响应示例
```json
{
    "message": "🚨 紧急按钮已触发！门已立即开启",
    "command_id": 79,
    "action": "emergency_open_door",
    "status": "COMPLETED",
    "door_status": "OPEN",
    "sent_at": "2025-08-03T06:45:15.643366+00:00",
    "executed_at": "2025-08-03T06:45:15.643253+00:00",
    "emergency": true
}
```

## 🔧 故障排除

### 常见问题

1. **URL格式错误**
   - ❌ 错误：`192.168.110.148`
   - ✅ 正确：`http://192.168.110.148:8000`
   - 💡 使用智能版脚本自动处理

2. **连接失败**
   - 检查服务器地址是否正确
   - 确认服务器是否正在运行
   - 检查网络连接

3. **认证失败**
   - 确认用户名和密码正确
   - 检查用户是否有权限

4. **API调用失败**
   - 检查机器人ID是否存在
   - 确认API路径正确

### 调试建议

1. **使用智能版脚本**：
   ```bash
   python3 smart_emergency_test.py
   ```

2. **查看服务器日志**：
   ```bash
   docker-compose logs backend
   ```

3. **检查网络连接**：
   ```bash
   curl -X GET http://your-server:8000/api/robots/1/status/
   ```

## 📞 技术支持

如果遇到问题，请提供以下信息：
1. 错误信息截图
2. 服务器日志
3. 网络配置信息
4. Python版本和依赖库版本

## 🆕 更新日志

- **v1.3** - 添加智能版测试脚本，自动处理URL格式
- **v1.2** - 优化错误提示和调试信息
- **v1.1** - 添加完整测试脚本和异常处理
- **v1.0** - 初始版本，支持基本API测试 