# 快速启动指南

## 一键启动（推荐）

```bash
# 1. 进入项目目录
cd phoneapp

# 2. 复制环境变量文件
cd backend
cp .env.example .env

# 3. 生成加密密钥（在Python中执行）
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# 将输出的密钥复制到 .env 文件的 ENCRYPTION_KEY

# 4. 返回项目根目录
cd ..

# 5. 启动所有服务
docker-compose up -d

# 6. 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 7. 查看日志（可选）
docker-compose logs -f backend
```

## 访问应用

- **API文档（Swagger）**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health
- **数据库**：localhost:5432
- **Redis**：localhost:6379

## 停止服务

```bash
docker-compose down
```

## 重新构建

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## 测试API

### 1. 注册用户
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "email": "test@example.com",
    "password": "test123"
  }'
```

### 2. 登录
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=test123"
```

保存返回的`access_token`。

### 3. 配置API Key
```bash
curl -X POST "http://localhost:8000/api/auth/api-keys" \
  -H "Authorization: Bearer {你的access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "api_key": "sk-your-openai-key",
    "model": "gpt-3.5-turbo"
  }'
```

### 4. 创建AI角色
```bash
curl -X POST "http://localhost:8000/api/characters" \
  -H "Authorization: Bearer {你的access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "小助手",
    "personality": "友好、乐于助人",
    "background_story": "一个AI助手",
    "language": "zh",
    "llm_provider": "openai",
    "llm_model": "gpt-3.5-turbo"
  }'
```

## 故障排查

### 查看容器状态
```bash
docker-compose ps
```

### 查看日志
```bash
docker-compose logs backend
docker-compose logs celery_worker
docker-compose logs celery_beat
```

### 进入容器
```bash
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres -d ai_chat_app
```

## 下一步

1. 阅读 `README.md` 了解完整功能
2. 访问 http://localhost:8000/docs 查看API文档
3. 开始开发移动端应用
