# 🚀 PACKAGE_CRUISER 快速启动指南

## 📋 系统要求
- Docker Desktop (Windows/Mac) 或 Docker Engine (Linux)
- 至少 4GB 可用内存
- 至少 2GB 可用磁盘空间

## 🚀 快速启动

### 1. 配置环境变量
```bash
# 复制环境变量文件
cp env.example .env
```

### 2. 启动所有服务
```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 或者前台运行（查看日志）
docker-compose up
```

### 3. 等待服务启动完成
```bash
# 查看服务状态
docker-compose ps

# 查看启动日志
docker-compose logs -f
```

### 4. 访问应用
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000/api/
- **管理后台**: http://localhost:8000/admin/

## 🛠️ 常用命令

### 服务管理
```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f
```

### 进入容器
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库
docker-compose exec mysql mysql -u root -p
```

## 🔧 故障排除

### 端口被占用
如果3000、8000或3306端口被占用，请修改 `docker-compose.yml` 中的端口映射。

### 数据库连接问题
```bash
# 重启数据库
docker-compose restart mysql
```

### 权限问题 (Linux/Mac)
```bash
sudo usermod -aG docker $USER
# 重新登录系统
```

## 📞 技术支持
如果遇到问题，请检查：
1. Docker服务是否正常运行
2. 端口是否被占用
3. 系统资源是否充足 