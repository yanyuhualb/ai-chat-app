# AI角色对话App - 完整项目

一个支持多AI平台、好感度系统和动态主动消息的移动端AI对话应用。

## 🌟 核心功能

- ✅ **多AI平台支持**：OpenAI GPT、Claude、通义千问、文心一言
- ✅ **自定义AI角色**：创建个性化AI角色（性格、背景、语言）
- ✅ **好感度系统**：-100~100分范围，7个等级（厌恶→恋人）
- ✅ **动态主动消息**：根据好感度自动调整发送频率（1-360分钟）
- ✅ **多轮对话**：独立对话历史，支持上下文记忆
- ✅ **用户自管API Key**：安全加密存储用户的AI平台密钥
- ✅ **国际化支持**：多语言、多时区

---

## 📁 项目结构

```
phoneapp/
├── backend/                  # FastAPI后端
│   ├── app/
│   │   ├── api/             # API路由
│   │   │   ├── auth.py      # 认证API
│   │   │   ├── characters.py # 角色管理API
│   │   │   ├── conversations.py # 对话API
│   │   │   └── affection.py # 好感度API
│   │   ├── models/          # SQLAlchemy模型
│   │   │   ├── user.py
│   │   │   ├── character.py
│   │   │   ├── conversation.py
│   │   │   ├── affection.py
│   │   │   └── proactive_message.py
│   │   ├── schemas/         # Pydantic Schema
│   │   ├── services/        # 业务逻辑
│   │   │   ├── llm_provider.py        # AI适配层
│   │   │   ├── affection_service.py   # 好感度服务
│   │   │   └── proactive_message_service.py
│   │   ├── core/            # 核心功能
│   │   │   ├── config.py    # 配置管理
│   │   │   ├── database.py  # 数据库连接
│   │   │   ├── redis.py     # Redis连接
│   │   │   └── security.py  # 安全（JWT、加密）
│   │   ├── tasks/           # Celery任务
│   │   │   ├── celery_app.py
│   │   │   └── proactive_tasks.py
│   │   └── main.py          # FastAPI应用入口
│   ├── alembic/             # 数据库迁移
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── mobile/                   # React Native前端（待实现）
├── docker-compose.yml       # Docker编排
└── README.md                # 项目文档
```

---

## 🚀 快速开始

### 方式一：使用Docker（推荐）

1. **复制环境变量文件**
```bash
cd backend
cp .env.example .env
```

2. **生成加密密钥**
```bash
# 在Python中生成32字节密钥
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
将生成的密钥复制到`.env`文件的`ENCRYPTION_KEY`字段。

3. **启动所有服务**
```bash
docker-compose up -d
```

4. **运行数据库迁移**
```bash
docker-compose exec backend alembic upgrade head
```

5. **访问应用**
- API文档：http://localhost:8000/docs
- API：http://localhost:8000

### 方式二：本地开发

#### 前置要求
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

#### 步骤

1. **安装Python依赖**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，填写数据库连接等信息
```

3. **运行数据库迁移**
```bash
alembic upgrade head
```

4. **启动FastAPI服务**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **启动Celery Worker（新终端）**
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

6. **启动Celery Beat（新终端）**
```bash
celery -A app.tasks.celery_app beat --loglevel=info
```

---

## 📖 API使用指南

### 1. 用户注册
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

### 2. 用户登录
```bash
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=testuser&password=password123
```

响应：
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### 3. 配置API Key
```bash
POST /api/auth/api-keys
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "provider": "openai",
  "api_key": "sk-proj-...",
  "model": "gpt-3.5-turbo"
}
```

### 4. 创建AI角色
```bash
POST /api/characters
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "小雪",
  "personality": "温柔体贴，善解人意",
  "background_story": "大学文学系学生，喜欢阅读和写作",
  "avatar_url": "https://example.com/avatar.jpg",
  "language": "zh",
  "llm_provider": "openai",
  "llm_model": "gpt-3.5-turbo",
  "config": {
    "temperature": 0.9
  }
}
```

### 5. 发送消息
```bash
POST /api/conversations/{conversation_id}/messages
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "content": "今天天气真好！",
  "stream": false
}
```

响应：
```json
{
  "id": 123,
  "conversation_id": 1,
  "role": "assistant",
  "content": "是呀！这样的好天气适合出去走走，你有什么计划吗？",
  "tokens_used": 28,
  "is_proactive": false,
  "created_at": "2025-12-07T10:30:00Z",
  "affection_change": 2
}
```

### 6. 查看好感度
```bash
GET /api/affection/{character_id}
Authorization: Bearer {access_token}
```

响应：
```json
{
  "character_id": 1,
  "current_score": 65,
  "level": "朋友",
  "next_level_score": 80,
  "total_interactions": 127,
  "last_interaction": "2025-12-07T10:30:00Z",
  "recent_changes": [
    {
      "id": 1,
      "score_change": 3,
      "reason": "用户分享积极情绪",
      "created_at": "2025-12-07T10:30:00Z"
    }
  ]
}
```

---

## 🎯 核心功能详解

### 好感度系统

**等级划分**（-100 ~ 100分）：
- **厌恶** (-100 ~ -60)：AI冷淡、距离感
- **陌生** (-60 ~ -20)：礼貌但疏远
- **普通** (-20 ~ 20)：中性态度
- **熟人** (20 ~ 50)：友好
- **朋友** (50 ~ 80)：亲近
- **挚友** (80 ~ 95)：深度信任
- **恋人** (95 ~ 100)：极度亲密

**好感度变化因素**：
- 积极对话：+2 ~ +5
- 中性对话：+1
- 消极对话：-1 ~ -3
- 长时间沉默：-2（每天）
- 深夜聊天：+2
- 分享秘密：+5

### 动态主动消息机制

**触发规则**（根据好感度）：

| 好感度 | 检测间隔 | 随机发送间隔 |
|--------|---------|-------------|
| 90-100分 | 用户3分钟无对话 | 1-10分钟 |
| 80-89分 | 用户10分钟无对话 | 10-30分钟 |
| 60-79分 | 用户30分钟无对话 | 30-120分钟 |
| 40-59分 | 用户2小时无对话 | 2-6小时 |
| <40分 | 不发送主动消息 | - |

**实现方式**：
- Celery Beat每分钟扫描一次
- 检查用户活跃状态表（`user_activity`）
- 根据好感度计算是否发送
- 调用AI生成自然的主动消息
- 发送推送通知（移动端待实现）

### AI平台适配

**支持的平台**：
1. **OpenAI**：GPT-3.5-turbo、GPT-4
2. **Claude**：Claude 3 Sonnet/Opus
3. **通义千问**：qwen-turbo、qwen-plus
4. **文心一言**：ernie-bot-turbo

**统一接口**：
```python
provider = get_llm_provider("openai")  # 或 "claude", "qwen", "ernie"
response = await provider.chat_completion(messages, api_key, model)
```

---

## 🔐 安全说明

1. **API Key加密**：使用Fernet对称加密存储用户的AI平台密钥
2. **密码加密**：使用bcrypt哈希存储密码
3. **JWT认证**：所有API需要Bearer Token
4. **HTTPS**：生产环境必须使用HTTPS
5. **环境变量**：敏感信息通过`.env`文件管理，不提交到Git

---

## 📱 移动端开发（待实现）

移动端将使用React Native开发，支持iOS和Android。

### 技术栈
- React Native 0.72+
- TypeScript
- React Navigation
- Zustand（状态管理）
- React Query（数据请求）
- react-native-gifted-chat（聊天UI）

### 计划功能
- [ ] 用户注册/登录界面
- [ ] AI角色列表和创建
- [ ] 对话界面（支持流式回复）
- [ ] 好感度可视化
- [ ] 主动消息推送通知
- [ ] 多语言切换

---

## 🛠️ 技术栈

### 后端
- **框架**：FastAPI 0.104+
- **ORM**：SQLAlchemy 2.0（异步）
- **数据库**：PostgreSQL 15
- **缓存**：Redis 7
- **任务队列**：Celery + Celery Beat
- **认证**：JWT
- **AI SDK**：openai、anthropic、dashscope、erniebot

### 前端（计划）
- React Native 0.72+
- TypeScript
- React Navigation
- Zustand

### 基础设施
- Docker & Docker Compose
- Nginx（反向代理）
- PostgreSQL（主数据库）
- Redis（缓存+队列）

---

## 📝 开发路线图

### ✅ 已完成
- [x] 后端项目搭建
- [x] 数据库模型设计
- [x] 用户认证系统
- [x] AI平台适配层
- [x] 好感度系统（支持负数）
- [x] 动态主动消息机制
- [x] Celery定时任务
- [x] 核心API接口
- [x] Docker配置

### 🚧 进行中
- [ ] WebSocket实时通信
- [ ] 流式对话回复
- [ ] 移动端UI开发

### 📅 计划中
- [ ] 推送通知集成
- [ ] 对话历史搜索
- [ ] 角色分享社区
- [ ] 多媒体消息支持
- [ ] 语音对话
- [ ] 数据分析仪表板

---

## 🐛 常见问题

### 1. 数据库连接失败
确保PostgreSQL已启动，检查`.env`文件中的`DATABASE_URL`配置。

### 2. Celery任务不执行
确保Redis已启动，检查`CELERY_BROKER_URL`配置。

### 3. AI调用失败
检查用户是否配置了API Key，确认API Key有效且有余额。

### 4. 加密密钥错误
确保`.env`文件中的`ENCRYPTION_KEY`是32字节的Fernet密钥。

---

## 📄 许可证

MIT License

---

## 👥 贡献

欢迎提交Issue和Pull Request！

---

## 📧 联系方式

如有问题，请提交Issue或联系开发者。

---

**祝你使用愉快！🎉**
