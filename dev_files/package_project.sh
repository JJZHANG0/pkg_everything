#!/bin/bash

# PACKAGE_CRUISER 项目打包脚本
# 用于将整个项目打包给同事

echo "🚀 开始打包 PACKAGE_CRUISER 项目..."

# 设置项目名称和版本
PROJECT_NAME="PACKAGE_CRUISER"
VERSION="1.0.0"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PACKAGE_NAME="${PROJECT_NAME}_v${VERSION}_${TIMESTAMP}"

echo "📦 打包名称: ${PACKAGE_NAME}"

# 创建临时打包目录
TEMP_DIR="temp_package"
mkdir -p $TEMP_DIR

echo "📁 复制项目文件..."

# 复制主要项目目录
cp -r campus_delivery $TEMP_DIR/
cp -r package_frontend $TEMP_DIR/
cp -r robot_client $TEMP_DIR/
cp -r docker_deploy $TEMP_DIR/
cp -r logs $TEMP_DIR/

# 复制文档文件
cp DEPLOYMENT_GUIDE.md $TEMP_DIR/
cp ROBOT_API_DOCUMENTATION.md $TEMP_DIR/
cp ROBOT_SIMULATOR_GUIDE.md $TEMP_DIR/
cp PACKAGE_CRUISER_README.md $TEMP_DIR/

# 复制机器人模拟器文件
cp robot_simulator_windows.py $TEMP_DIR/
cp robot_test_script_windows.py $TEMP_DIR/
cp test_connection.py $TEMP_DIR/

# 创建启动脚本
cat > $TEMP_DIR/start.sh << 'EOF'
#!/bin/bash

echo "🚀 启动 PACKAGE_CRUISER 系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未找到Docker，请先安装Docker Desktop"
    echo "下载地址: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# 检查Docker Compose是否可用
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: 未找到docker-compose，请确保Docker Desktop已正确安装"
    exit 1
fi

# 进入Docker部署目录
cd docker_deploy

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cp env.example .env
fi

# 启动服务
echo "🔧 启动Docker服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

echo ""
echo "🎉 系统启动完成！"
echo ""
echo "🌐 访问地址:"
echo "   前端界面: http://localhost:3000"
echo "   后端API:  http://localhost:8000/api/"
echo "   管理后台: http://localhost:8000/admin/"
echo ""
echo "📋 常用命令:"
echo "   查看日志: cd docker_deploy && docker-compose logs -f"
echo "   停止服务: cd docker_deploy && docker-compose down"
echo "   重启服务: cd docker_deploy && docker-compose restart"
echo ""
EOF

# 创建Windows启动脚本
cat > $TEMP_DIR/start.bat << 'EOF'
@echo off
chcp 65001 >nul
echo 🚀 启动 PACKAGE_CRUISER 系统...

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Docker，请先安装Docker Desktop
    echo 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM 检查Docker Compose是否可用
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到docker-compose，请确保Docker Desktop已正确安装
    pause
    exit /b 1
)

REM 进入Docker部署目录
cd docker_deploy

REM 检查环境变量文件
if not exist .env (
    echo 📝 创建环境变量文件...
    copy env.example .env
)

REM 启动服务
echo 🔧 启动Docker服务...
docker-compose up -d

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 📊 检查服务状态...
docker-compose ps

echo.
echo 🎉 系统启动完成！
echo.
echo 🌐 访问地址:
echo    前端界面: http://localhost:3000
echo    后端API:  http://localhost:8000/api/
echo    管理后台: http://localhost:8000/admin/
echo.
echo 📋 常用命令:
echo    查看日志: cd docker_deploy ^&^& docker-compose logs -f
echo    停止服务: cd docker_deploy ^&^& docker-compose down
echo    重启服务: cd docker_deploy ^&^& docker-compose restart
echo.
pause
EOF

# 设置脚本权限
chmod +x $TEMP_DIR/start.sh

# 创建压缩包
echo "🗜️ 创建压缩包..."
tar -czf "${PACKAGE_NAME}.tar.gz" -C $TEMP_DIR .

# 清理临时目录
rm -rf $TEMP_DIR

echo ""
echo "✅ 打包完成！"
echo "📦 文件名称: ${PACKAGE_NAME}.tar.gz"
echo "📏 文件大小: $(du -h "${PACKAGE_NAME}.tar.gz" | cut -f1)"
echo ""
echo "📋 给同事的使用说明:"
echo "1. 解压文件: tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "2. 进入目录: cd ${PROJECT_NAME}_v${VERSION}_${TIMESTAMP}"
echo "3. 启动系统: ./start.sh (Linux/Mac) 或 start.bat (Windows)"
echo ""
echo "🎉 打包完成！可以发送给同事了。" 