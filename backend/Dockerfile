# 生命反射弧 · 后端（FastAPI + SQLite）
# 构建：docker build -t lifereflex-backend .
FROM python:3.12-slim

WORKDIR /app

# 依赖安装（利用构建缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用代码 + 健康检查脚本
COPY app ./app
COPY healthcheck.py .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_URL=sqlite:////app/data/lifereflex.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
