# HistAgent Frontend

这是 HistAgent 项目的现代化 React + TypeScript 前端实现，基于原始的静态 HTML 页面重构而成。

## 🚀 功能特性

- **现代化技术栈**: React 18 + TypeScript + Vite
- **响应式设计**: 支持桌面端和移动端
- **实时通信**: WebSocket 连接，支持断线重连
- **文件上传**: 支持拖拽上传，多种文件格式
- **状态管理**: 使用 Zustand 进行状态管理
- **组件化设计**: 模块化的组件架构
- **工具调用**: 实时显示 AI 工具调用状态
- **会话管理**: 支持多会话切换和管理

## 📦 安装依赖

```bash
cd fronted
npm install
```

## 🛠️ 开发环境

启动开发服务器:

```bash
npm run dev
```

访问 http://localhost:3000

## 🏗️ 构建生产版本

```bash
npm run build
```

构建文件将输出到 `dist/` 目录。

## 📁 项目结构

```
fronted/
├── src/
│   ├── components/          # React 组件
│   │   ├── Sidebar.tsx     # 侧边栏组件
│   │   ├── MainContent.tsx # 主内容区组件
│   │   ├── ChatArea.tsx    # 聊天区域组件
│   │   ├── MessageInput.tsx# 消息输入组件
│   │   ├── MessageItem.tsx # 消息项组件
│   │   ├── ToolPanel.tsx   # 工具面板组件
│   │   └── WelcomeScreen.tsx# 欢迎页面组件
│   ├── services/           # 服务层
│   │   ├── websocket.ts    # WebSocket 服务
│   │   └── fileUpload.ts   # 文件上传服务
│   ├── store/              # 状态管理
│   │   └── index.ts        # Zustand store
│   ├── styles/             # 样式文件
│   │   ├── index.css       # 主样式文件
│   │   ├── base.css        # 基础样式
│   │   ├── layout.css      # 布局样式
│   │   ├── components.css  # 组件样式
│   │   ├── theme.css       # 主题样式
│   │   └── responsive.css  # 响应式样式
│   ├── types/              # TypeScript 类型定义
│   │   └── index.ts        # 全局类型
│   ├── App.tsx             # 主应用组件
│   └── main.tsx            # 应用入口
├── public/                 # 静态资源
├── package.json            # 项目配置
├── vite.config.ts         # Vite 配置
├── tailwind.config.js     # Tailwind 配置
├── tsconfig.json          # TypeScript 配置
└── README.md              # 项目说明
```

## 🔧 技术栈

- **React 18**: 用户界面库
- **TypeScript**: 类型安全的 JavaScript
- **Vite**: 现代化构建工具
- **Tailwind CSS**: 原子化 CSS 框架
- **Zustand**: 轻量级状态管理
- **Material Icons**: 图标库

## 🌐 API 集成

### WebSocket 连接

默认连接到 `ws://localhost:8000/ws`，支持：

- 自动重连机制
- 心跳检测
- 连接状态管理

### 文件上传

支持上传到 `/api/upload` 端点：

- 最大文件大小: 50MB
- 支持的文件类型: 图片、文档、音视频等
- 上传进度显示

## 🎨 样式系统

### CSS 模块化

- `base.css`: 基础样式和重置
- `layout.css`: 布局相关样式
- `components.css`: 组件样式
- `theme.css`: 主题和颜色变量
- `responsive.css`: 响应式样式

### 主题支持

支持浅色和深色主题切换（通过 `data-theme` 属性）。

## 📱 响应式设计

- **移动端**: < 768px
- **平板端**: 768px - 1024px
- **桌面端**: > 1024px
- **大屏幕**: > 1440px

## 🔌 后端集成

确保后端服务运行在正确的端口：

- API 服务: `http://localhost:8000`
- WebSocket 服务: `ws://localhost:8000/ws`

## 🛠️ 开发脚本

```bash
# 开发环境
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 类型检查
npm run type-check

# 代码检查
npm run lint
```

## 🔍 故障排除

### 常见问题

1. **WebSocket 连接失败**

   - 检查后端服务是否启动
   - 确认端口配置正确
2. **文件上传失败**

   - 检查文件大小是否超限
   - 确认文件类型是否支持
3. **样式显示异常**

   - 清除浏览器缓存
   - 重新安装依赖

### 调试模式

开启浏览器开发者工具查看控制台输出，所有重要操作都有相应的日志记录。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**注意**: 这是一个动态化的现代前端实现，保持了原始设计的 UI 风格，同时增加了完整的交互功能。
