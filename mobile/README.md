# React Native移动端开发指南

## 初始化项目

```bash
cd mobile

# 安装依赖（使用pnpm）
pnpm install

# iOS（需要Mac）
cd ios
pod install
cd ..
pnpm ios

# Android
pnpm android
```

## 开发计划

### Phase 1: 基础UI（1-2周）
- [ ] 登录/注册界面
- [ ] 主界面导航
- [ ] AI角色列表
- [ ] 基础聊天界面

### Phase 2: 核心功能（2-3周）
- [ ] AI对话功能
- [ ] 好感度显示
- [ ] 角色创建/编辑
- [ ] API Key配置

### Phase 3: 高级功能（2-3周）
- [ ] 实时流式回复
- [ ] 推送通知
- [ ] 主动消息提醒
- [ ] 多语言切换

## 项目结构（计划）

```
src/
├── screens/          # 页面
│   ├── Auth/
│   │   ├── Login.tsx
│   │   └── Register.tsx
│   ├── CharacterList.tsx
│   ├── ChatScreen.tsx
│   └── Profile.tsx
├── components/       # 组件
│   ├── MessageBubble.tsx
│   ├── CharacterCard.tsx
│   └── AffectionBar.tsx
├── services/         # API服务
│   ├── api.ts
│   └── auth.ts
├── stores/           # Zustand状态
│   ├── authStore.ts
│   └── chatStore.ts
├── types/            # TypeScript类型
└── locales/          # 国际化
    ├── en.json
    └── zh.json
```

## 技术栈

- **框架**：React Native 0.72+
- **语言**：TypeScript
- **导航**：React Navigation
- **状态管理**：Zustand
- **数据请求**：React Query + Axios
- **聊天UI**：react-native-gifted-chat
- **国际化**：i18next

## API集成示例

```typescript
// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

export const login = async (username: string, password: string) => {
  const response = await api.post('/auth/login', { username, password });
  return response.data;
};

export const sendMessage = async (conversationId: number, content: string, token: string) => {
  const response = await api.post(
    `/conversations/${conversationId}/messages`,
    { content },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return response.data;
};
```

## 下一步

运行以下命令初始化React Native项目：

```bash
npx react-native init AIChatApp --template react-native-template-typescript
```

然后将配置文件复制到新创建的项目中。
