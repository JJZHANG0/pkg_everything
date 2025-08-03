# 🚀 PACKAGE_CRUISER 校园快递配送系统

## 📋 项目简介

PACKAGE_CRUISER 是一个完整的校园快递配送系统，包含以下组件：

- **前端**: React + TypeScript 用户界面
- **后端**: Django REST Framework API
- **数据库**: MySQL 8.0
- **机器人客户端**: Python 机器人控制程序
- **Docker**: 容器化部署

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React前端     │    │   Django后端    │    │   MySQL数据库   │
│   (端口3000)    │◄──►│   (端口8000)    │◄──►│   (端口3306)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   机器人客户端   │
                       │   (Python)      │
                       └─────────────────┘
```

## 🚀 快速启动

### 方式1：Docker一键启动（推荐）

```bash
# 1. 进入Docker部署目录
cd docker_deploy

# 2. 配置环境变量
cp env.example .env

# 3. 启动所有服务
docker-compose up -d

# 4. 查看服务状态
docker-compose ps
```

### 方式2：本地开发环境

#### 后端启动
```bash
cd campus_delivery
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### 前端启动
```bash
cd package_frontend
npm install
npm start
```

#### 机器人客户端
```bash
cd robot_client
pip install -r requirements.txt
python main.py
```

## 🌐 访问地址

启动成功后，可以通过以下地址访问：

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000/api/
- **管理后台**: http://localhost:8000/admin/

## 📁 项目结构

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
├── robot_client/           # 机器人客户端
│   ├── main.py            # 主程序
│   ├── hardware/          # 硬件控制
│   └── network/           # 网络通信
├── docker_deploy/          # Docker部署配置
│   ├── docker-compose.yml  # 服务编排
│   ├── env.example        # 环境变量示例
│   └── README.md          # 部署指南
├── logs/                   # 日志文件
└── DEPLOYMENT_GUIDE.md    # 详细部署指南
```

## 🔧 配置说明

### 环境变量
主要配置在 `docker_deploy/.env` 文件中：
- `DB_NAME`: 数据库名称
- `DB_USER`: 数据库用户名
- `DB_PASSWORD`: 数据库密码
- `DB_HOST`: 数据库主机

### 端口配置
- 前端: 3000
- 后端: 8000
- 数据库: 3306

## 🛠️ 常用命令

### Docker管理
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart
```

### 数据库管理
```bash
# 进入数据库
docker-compose exec mysql mysql -u root -p

# 备份数据库
docker-compose exec mysql mysqldump -u root -p package > backup.sql
```

## 🐛 故障排除

### 常见问题
1. **端口被占用**: 修改 `docker-compose.yml` 中的端口映射
2. **数据库连接失败**: 检查环境变量配置
3. **权限问题**: 确保Docker权限正确

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📚 相关文档

- [详细部署指南](DEPLOYMENT_GUIDE.md)
- [API文档](docker_deploy/API_DOCUMENTATION.md)
- [机器人API文档](ROBOT_API_DOCUMENTATION.md)
- [机器人模拟器指南](ROBOT_SIMULATOR_GUIDE.md)

## 🤝 技术支持

如果遇到问题，请：
1. 检查Docker服务是否正常运行
2. 查看系统日志进行调试
3. 确认端口未被占用
4. 验证环境变量配置正确

---

**祝您使用愉快！** 🚀 