# 🚀 PACKAGE_CRUISER 部署指南

## 📋 系统要求

- **Docker Desktop** (Windows/Mac) 或 **Docker Engine** (Linux)
- **Git** (可选，用于版本控制)
- **至少 4GB 可用内存**
- **至少 2GB 可用磁盘空间**

## 🛠️ 快速部署步骤

### 1. 解压项目文件
```bash
# 解压项目文件
tar -xzf PACKAGE_CRUISER.tar.gz
cd PACKAGE_CRUISER
```

### 2. 启动服务
```bash
# 进入docker部署目录
cd docker_deploy

# 启动所有服务
docker-compose up -d
```

### 3. 等待服务启动
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 访问应用
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000/api/
- **管理后台**: http://localhost:8000/admin/

## 🔧 详细配置

### 环境变量配置
项目使用默认配置，如需修改请编辑 `docker_deploy/.env` 文件：

```env
DB_NAME=package
DB_USER=root
DB_PASSWORD=Aa123456
DB_HOST=mysql
```

### 端口配置
- **前端**: 3000
- **后端**: 8000
- **数据库**: 3306

如需修改端口，请编辑 `docker_deploy/docker-compose.yml` 文件。

## 🐛 常见问题

### 1. 端口被占用
```bash
# 查看端口占用
lsof -i :3000
lsof -i :8000
lsof -i :3306

# 停止占用端口的进程或修改docker-compose.yml中的端口映射
```

### 2. 数据库连接失败
```bash
# 重启数据库服务
docker-compose restart mysql

# 查看数据库日志
docker-compose logs mysql
```

### 3. 前端无法访问后端
```bash
# 检查后端服务状态
docker-compose logs backend

# 重启后端服务
docker-compose restart backend
```

### 4. 权限问题 (Linux/Mac)
```bash
# 确保当前用户有docker权限
sudo usermod -aG docker $USER

# 重新登录或重启系统
```

## 📊 服务管理

### 启动服务
```bash
docker-compose up -d
```

### 停止服务
```bash
docker-compose down
```

### 重启服务
```bash
docker-compose restart
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql
```

### 进入容器
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec mysql mysql -u root -p
```

## 🔄 更新项目

### 1. 停止服务
```bash
docker-compose down
```

### 2. 拉取最新代码
```bash
git pull origin main  # 如果使用git
# 或者重新解压新的项目文件
```

### 3. 重新构建并启动
```bash
docker-compose build --no-cache
docker-compose up -d
```

## 📝 开发模式

### 本地开发
```bash
# 启动服务
docker-compose up -d

# 查看实时日志
docker-compose logs -f
```

### 调试模式
```bash
# 进入后端容器调试
docker-compose exec backend bash
python manage.py shell

# 查看数据库
docker-compose exec mysql mysql -u root -p package
```

## 🗂️ 项目结构

```
PACKAGE_CRUISER/
├── campus_delivery/          # Django后端项目
│   ├── core/                # 核心应用
│   ├── campus_delivery/     # 项目配置
│   └── manage.py           # Django管理脚本
├── package_frontend/        # React前端项目
│   ├── src/                # 源代码
│   ├── public/             # 静态文件
│   └── package.json        # 依赖配置
├── docker_deploy/          # Docker部署配置
│   ├── docker-compose.yml  # 服务编排
│   ├── .env               # 环境变量
│   └── Dockerfile         # 镜像构建
├── logs/                   # 日志文件
└── README.md              # 项目说明
```

## 📞 技术支持

如果遇到问题，请检查：
1. Docker服务是否正常运行
2. 端口是否被占用
3. 系统资源是否充足
4. 网络连接是否正常

## 🎉 部署完成

恭喜！你的PACKAGE_CRUISER项目已经成功部署。

现在你可以：
- 访问前端界面进行测试
- 使用API进行开发
- 查看系统日志进行调试

祝你使用愉快！🚀 