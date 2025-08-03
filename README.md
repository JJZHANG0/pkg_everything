# 🤖 校园配送机器人系统

一个基于Django + React + Docker的智能校园配送机器人管理系统。

## 📋 系统架构

- **后端**: Django REST Framework + MySQL
- **前端**: React + TypeScript
- **数据库**: MySQL 8.0
- **部署**: Docker + Docker Compose
- **机器人通信**: HTTP轮询模式

## 🚀 快速部署

### 1. 环境要求

确保你的系统已安装：
- [Git](https://git-scm.com/) (版本 2.0+)
- [Docker](https://www.docker.com/) (版本 20.0+)
- [Docker Compose](https://docs.docker.com/compose/) (版本 2.0+)

### 2. 克隆项目

```bash
# 克隆项目到本地
git clone https://github.com/JJZHANG0/pkg_everything.git

# 进入项目目录
cd pkg_everything
```

### 3. 启动Docker服务

```bash
# 进入Docker部署目录
cd docker_deploy

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 4. 创建超级用户

```bash
# 创建超级用户（用于登录管理后台）
docker-compose exec backend python manage.py createsuperuser

# 按提示输入用户名和密码
# 例如：用户名: root, 密码: root
```

### 5. 访问系统

启动成功后，可以通过以下地址访问：

- **前端界面**: http://localhost:80
- **后端API**: http://localhost:8000
- **管理后台**: http://localhost:8000/admin

## 📱 系统功能

### 用户功能
- 用户注册/登录
- 创建配送订单
- 查看订单状态
- 个人中心管理

### 调度员功能
- 实时监控机器人状态
- 发送控制指令
- 紧急按钮处理
- 网络监控

### 机器人功能
- 二维码扫描识别
- 自动配送
- 状态上报
- 紧急处理

## 🔧 详细配置

### 环境变量配置

在 `docker_deploy/` 目录下创建 `.env` 文件（可选）：

```env
# 数据库配置
MYSQL_ROOT_PASSWORD=your_password
MYSQL_DATABASE=campus_delivery
MYSQL_USER=delivery_user
MYSQL_PASSWORD=delivery_pass

# Django配置
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 前端配置
REACT_APP_API_BASE_URL=http://localhost:8000
```

### 端口配置

默认端口配置：
- **前端**: 80
- **后端**: 8000
- **数据库**: 3306

如需修改端口，编辑 `docker_deploy/docker-compose.yml`：

```yaml
services:
  react_frontend:
    ports:
      - "8080:80"  # 修改为 8080:80
  drf_backend:
    ports:
      - "8001:8000"  # 修改为 8001:8000
```

## 🤖 机器人客户端

### 机器人通信接口

机器人通过HTTP轮询方式与服务器通信：

```bash
# 机器人客户端示例
cd robot_client
python robot_client_polling.py
```

### 主要API接口

| 接口 | 方法 | 功能 |
|------|------|------|
| `/api/robots/{id}/status/` | GET | 获取机器人状态 |
| `/api/robots/{id}/get_commands/` | GET | 获取待执行命令 |
| `/api/robots/{id}/execute_command/` | POST | 上报命令执行结果 |
| `/api/robots/{id}/upload_qr_image/` | POST | 上传二维码图片 |
| `/api/robots/{id}/emergency_button/` | POST | 紧急按钮处理 |

## 📊 监控和日志

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mysql

# 实时查看日志
docker-compose logs -f backend
```

### 系统监控

- **网络监控页面**: http://localhost:80/network-monitor
- **系统日志**: 通过管理后台查看
- **实时状态**: 调度员页面实时显示

## 🔍 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查看端口占用
lsof -i :80
lsof -i :8000

# 停止占用端口的进程
sudo kill -9 <PID>
```

#### 2. Docker服务启动失败
```bash
# 查看详细错误信息
docker-compose logs

# 重新构建镜像
docker-compose build --no-cache

# 清理Docker缓存
docker system prune -a
```

#### 3. 数据库连接失败
```bash
# 检查数据库服务状态
docker-compose ps mysql

# 重启数据库服务
docker-compose restart mysql

# 查看数据库日志
docker-compose logs mysql
```

#### 4. 前端无法访问后端API
```bash
# 检查CORS配置
docker-compose logs backend

# 检查网络连接
curl http://localhost:8000/api/

# 重启后端服务
docker-compose restart backend
```

### 重置系统

```bash
# 停止所有服务
docker-compose down

# 删除所有数据（谨慎操作）
docker-compose down -v
docker volume prune

# 重新启动
docker-compose up -d
```

## 📝 开发指南

### 本地开发环境

```bash
# 后端开发
cd campus_delivery
pip install -r requirements.txt
python manage.py runserver

# 前端开发
cd package_frontend
npm install
npm start
```

### 代码结构

```
ALANG/
├── campus_delivery/         # Django后端
│   ├── core/               # 核心应用
│   ├── campus_delivery/    # 项目配置
│   └── manage.py
├── package_frontend/        # React前端
│   ├── src/               # 源代码
│   ├── public/            # 静态文件
│   └── package.json
├── docker_deploy/          # Docker配置
│   └── docker-compose.yml
├── robot_client/           # 机器人客户端
└── README.md
```

## 🔐 安全说明

### 默认账户
- **超级用户**: root/root
- **数据库**: root/root

### 生产环境建议
1. 修改所有默认密码
2. 配置HTTPS
3. 设置防火墙规则
4. 定期备份数据
5. 监控系统日志

## 📞 技术支持

### 联系方式
- **项目地址**: https://github.com/JJZHANG0/pkg_everything
- **问题反馈**: 通过GitHub Issues提交

### 相关文档
- [API文档](ROBOT_API_DOCUMENTATION.md)
- [二维码上传API](二维码图片上传API说明.md)
- [Git子模块问题解决方案](Git子模块问题解决方案.md)

## 🎯 快速开始检查清单

- [ ] 安装Docker和Docker Compose
- [ ] 克隆项目代码
- [ ] 启动Docker服务
- [ ] 创建超级用户
- [ ] 访问前端界面
- [ ] 测试登录功能
- [ ] 检查机器人连接

## 📈 系统状态

- ✅ 用户认证系统
- ✅ 订单管理系统
- ✅ 机器人控制接口
- ✅ 二维码识别功能
- ✅ 实时监控系统
- ✅ Docker容器化部署
- ✅ 网络监控功能
- ✅ 紧急按钮处理

---

**注意**: 首次部署可能需要几分钟时间下载Docker镜像，请耐心等待。 