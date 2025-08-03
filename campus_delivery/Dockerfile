FROM python:3.10-slim

WORKDIR /app

# 安装 zbar 共享库依赖
RUN apt-get update && apt-get install -y libzbar0 libffi-dev build-essential

# 单独复制 requirements.txt
COPY requirements.txt /app/

# 安装依赖
RUN pip install --upgrade pip
RUN pip install cryptography
RUN pip install -r requirements.txt

# 再复制所有项目代码
COPY . /app/

# 拷贝启动脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

CMD ["/entrypoint.sh"]
