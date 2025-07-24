# HistAgent 前端开发指南

## 概述

本指南详细介绍了 HistAgent 前端项目的开发环境搭建、开发流程、调试技巧、测试方法和部署流程。

## 环境要求

### 基础环境
- **Node.js**: 18.0.0 或更高版本
- **npm**: 8.0.0 或更高版本（推荐使用 npm 9.0+）
- **Git**: 2.30.0 或更高版本

### 推荐开发工具
- **VS Code**: 推荐的代码编辑器
- **Chrome/Edge**: 推荐的开发浏览器
- **React Developer Tools**: 浏览器扩展
- **Redux DevTools**: 状态调试工具

### VS Code 推荐插件
```json
{
  "recommendations": [
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-eslint",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense"
  ]
}
```

## 项目搭建

### 1. 克隆项目
```bash
git clone https://github.com/saltyfishtree/histagent.git
cd histagent/fronted
```

### 2. 安装依赖
```bash
npm install
```

### 3. 环境配置
创建环境配置文件 `.env.local`:
```bash
# 开发环境配置
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
VITE_UPLOAD_URL=http://localhost:8000/api/upload

# 功能开关
VITE_ENABLE_DEBUG=true
VITE_ENABLE_MOCK=false
VITE_ENABLE_ANALYTICS=false
```

### 4. 启动开发服务器
```bash
npm run dev
```

访问 `http://localhost:5173` 查看应用。

## 开发脚本

### 基础脚本
```bash
npm run dev          # 启动开发服务器
npm run build        # 构建生产版本
npm run preview      # 预览生产构建
npm run lint         # ESLint 代码检查
npm run lint:fix     # 自动修复 ESLint 问题
npm run type-check   # TypeScript 类型检查
```

### 高级脚本
```bash
npm run analyze      # 构建分析
npm run clean        # 清理构建缓存
npm run test         # 运行测试
npm run test:watch   # 监听模式运行测试
npm run storybook    # 启动 Storybook(如果配置)
```

## 项目结构说明

### 源码结构
```
src/
├── components/          # React 组件
│   ├── ui/             # 基础 UI 组件
│   ├── layout/         # 布局组件
│   └── features/       # 功能组件
├── services/           # 业务服务层
│   ├── api/           # API 服务
│   ├── websocket/     # WebSocket 服务
│   └── storage/       # 本地存储服务
├── store/             # 状态管理
│   ├── slices/        # 状态切片
│   └── selectors/     # 状态选择器
├── hooks/             # 自定义 Hooks
├── utils/             # 工具函数
├── types/             # TypeScript 类型定义
├── constants/         # 常量定义
├── styles/            # 全局样式
└── assets/            # 静态资源
```

### 组件组织原则
1. **按功能分组**: 相关组件放在同一目录
2. **单一职责**: 每个组件只负责一个功能
3. **可复用性**: 通用组件放在 `ui/` 目录
4. **类型安全**: 所有组件都有明确的 Props 类型

## 开发流程

### 1. 功能开发流程

#### 创建新功能
```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 创建组件目录
mkdir src/components/features/NewFeature

# 3. 创建组件文件
touch src/components/features/NewFeature/index.tsx
touch src/components/features/NewFeature/NewFeature.module.css
touch src/components/features/NewFeature/types.ts
```

#### 组件模板
```typescript
// src/components/features/NewFeature/index.tsx
import React from 'react';
import { NewFeatureProps } from './types';
import styles from './NewFeature.module.css';

const NewFeature: React.FC<NewFeatureProps> = ({ 
  prop1, 
  prop2,
  ...props 
}) => {
  return (
    <div className={styles.container} {...props}>
      {/* 组件内容 */}
    </div>
  );
};

export default NewFeature;
```

#### 类型定义
```typescript
// src/components/features/NewFeature/types.ts
export interface NewFeatureProps {
  prop1: string;
  prop2?: number;
  className?: string;
  children?: React.ReactNode;
}
```

### 2. 状态管理

#### 创建新的状态切片
```typescript
// src/store/slices/newFeatureSlice.ts
import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

interface NewFeatureState {
  data: any[];
  loading: boolean;
  error: string | null;
  
  // Actions
  setData: (data: any[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  fetchData: () => Promise<void>;
}

export const useNewFeatureStore = create<NewFeatureState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    data: [],
    loading: false,
    error: null,
    
    // Actions
    setData: (data) => set({ data }),
    setLoading: (loading) => set({ loading }),
    setError: (error) => set({ error }),
    
    fetchData: async () => {
      set({ loading: true, error: null });
      try {
        // API 调用逻辑
        const data = await fetchDataFromAPI();
        set({ data, loading: false });
      } catch (error) {
        set({ error: error.message, loading: false });
      }
    }
  }))
);
```

### 3. API 服务

#### 创建 API 服务
```typescript
// src/services/api/newFeatureApi.ts
import { ApiResponse } from '../../types';

export class NewFeatureAPI {
  private baseURL = import.meta.env.VITE_API_URL;
  
  async getData(): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${this.baseURL}/new-feature`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }
  
  async postData(data: any): Promise<ApiResponse<any>> {
    const response = await fetch(`${this.baseURL}/new-feature`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }
}

export const newFeatureAPI = new NewFeatureAPI();
```

## 调试技巧

### 1. React DevTools
```typescript
// 在组件中添加调试信息
const MyComponent = () => {
  const debugInfo = {
    props: { prop1, prop2 },
    state: { state1, state2 },
    timestamp: Date.now()
  };
  
  // 在开发环境中输出调试信息
  if (import.meta.env.DEV) {
    console.log('MyComponent Debug:', debugInfo);
  }
  
  return <div>Component Content</div>;
};
```

### 2. Zustand DevTools
```typescript
// 在 store 中启用 DevTools
import { devtools } from 'zustand/middleware';

export const useAppStore = create<AppState>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // store 定义
    })),
    {
      name: 'app-store', // DevTools 中的显示名称
    }
  )
);
```

### 3. 网络调试
```typescript
// 添加请求拦截器用于调试
const apiWithLogging = {
  async request(url: string, options?: RequestInit) {
    const startTime = Date.now();
    
    try {
      const response = await fetch(url, options);
      const endTime = Date.now();
      
      console.log(`API Request: ${url}`, {
        method: options?.method || 'GET',
        status: response.status,
        duration: endTime - startTime,
        headers: Object.fromEntries(response.headers.entries())
      });
      
      return response;
    } catch (error) {
      console.error(`API Error: ${url}`, error);
      throw error;
    }
  }
};
```

### 4. WebSocket 调试
```typescript
// WebSocket 连接调试
class DebugWebSocketService extends WebSocketService {
  connect(): Promise<void> {
    console.log('WebSocket: Attempting to connect...');
    
    return super.connect().then(() => {
      console.log('WebSocket: Connected successfully');
    }).catch((error) => {
      console.error('WebSocket: Connection failed', error);
      throw error;
    });
  }
  
  sendMessage(message: any): void {
    console.log('WebSocket: Sending message', message);
    super.sendMessage(message);
  }
  
  protected handleMessage(message: WebSocketMessage): void {
    console.log('WebSocket: Received message', message);
    super.handleMessage(message);
  }
}
```

## 样式开发

### 1. Tailwind CSS 使用
```typescript
// 使用 Tailwind 类名
const Button = ({ variant = 'primary', size = 'md', children }) => {
  const baseClasses = 'font-medium rounded-lg transition-colors';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700'
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };
  
  const className = clsx(
    baseClasses,
    variantClasses[variant],
    sizeClasses[size]
  );
  
  return (
    <button className={className}>
      {children}
    </button>
  );
};
```

### 2. 响应式设计
```css
/* 使用 Tailwind 响应式前缀 */
.container {
  @apply w-full px-4;
  @apply md:px-6;
  @apply lg:px-8;
  @apply xl:max-w-7xl xl:mx-auto;
}

/* 自定义断点 */
@media (min-width: 1440px) {
  .large-screen-layout {
    /* 大屏幕特定样式 */
  }
}
```

### 3. 主题系统
```typescript
// 主题变量定义
export const theme = {
  colors: {
    primary: {
      50: '#eff6ff',
      500: '#3b82f6',
      900: '#1e3a8a'
    },
    gray: {
      50: '#f9fafb',
      500: '#6b7280',
      900: '#111827'
    }
  },
  spacing: {
    xs: '0.5rem',
    sm: '1rem',
    md: '1.5rem',
    lg: '2rem',
    xl: '3rem'
  },
  borderRadius: {
    sm: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '1rem'
  }
};
```

## 性能优化

### 1. 组件优化
```typescript
// 使用 React.memo 优化组件
const ExpensiveComponent = React.memo<Props>(({ data, onUpdate }) => {
  // 组件逻辑
}, (prevProps, nextProps) => {
  // 自定义比较函数
  return prevProps.data.id === nextProps.data.id;
});

// 使用 useMemo 优化计算
const ProcessedData = ({ rawData }) => {
  const processedData = useMemo(() => {
    return rawData.map(item => ({
      ...item,
      processed: expensiveOperation(item)
    }));
  }, [rawData]);
  
  return <DataDisplay data={processedData} />;
};

// 使用 useCallback 优化函数
const ListComponent = ({ items }) => {
  const handleItemClick = useCallback((id: string) => {
    // 处理点击逻辑
  }, []);
  
  return (
    <div>
      {items.map(item => (
        <Item 
          key={item.id} 
          data={item} 
          onClick={handleItemClick}
        />
      ))}
    </div>
  );
};
```

### 2. 代码分割
```typescript
// 路由级别的代码分割
const HomePage = lazy(() => import('./pages/HomePage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

// 组件级别的代码分割
const HeavyComponent = lazy(() => import('./components/HeavyComponent'));

const App = () => (
  <Suspense fallback={<LoadingSpinner />}>
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/settings" element={<SettingsPage />} />
    </Routes>
  </Suspense>
);
```

### 3. 资源优化
```typescript
// 图片懒加载
const LazyImage = ({ src, alt, ...props }) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );
    
    if (imgRef.current) {
      observer.observe(imgRef.current);
    }
    
    return () => observer.disconnect();
  }, []);
  
  return (
    <div ref={imgRef} {...props}>
      {isInView && (
        <img
          src={src}
          alt={alt}
          onLoad={() => setIsLoaded(true)}
          style={{ 
            opacity: isLoaded ? 1 : 0,
            transition: 'opacity 0.3s'
          }}
        />
      )}
    </div>
  );
};
```

## 测试

### 1. 组件测试
```typescript
// 使用 React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import { expect, test } from 'vitest';
import Button from './Button';

test('Button renders with correct text', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByRole('button')).toHaveTextContent('Click me');
});

test('Button calls onClick when clicked', () => {
  const handleClick = vi.fn();
  render(<Button onClick={handleClick}>Click me</Button>);
  
  fireEvent.click(screen.getByRole('button'));
  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

### 2. Store 测试
```typescript
// 测试 Zustand store
import { renderHook, act } from '@testing-library/react';
import { useAppStore } from './store';

test('store updates state correctly', () => {
  const { result } = renderHook(() => useAppStore());
  
  act(() => {
    result.current.setUser({ id: '1', name: 'Test User' });
  });
  
  expect(result.current.user).toEqual({ id: '1', name: 'Test User' });
});
```

### 3. API 测试
```typescript
// Mock API 响应
import { vi } from 'vitest';
import { newFeatureAPI } from './newFeatureApi';

// Mock fetch
global.fetch = vi.fn();

test('API returns data correctly', async () => {
  const mockData = { success: true, data: [{ id: 1, name: 'Test' }] };
  
  (fetch as any).mockResolvedValueOnce({
    ok: true,
    json: async () => mockData
  });
  
  const result = await newFeatureAPI.getData();
  expect(result).toEqual(mockData);
});
```

## 构建和部署

### 1. 构建配置
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@headlessui/react', 'lucide-react'],
          utils: ['clsx', 'date-fns']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@services': resolve(__dirname, 'src/services'),
      '@utils': resolve(__dirname, 'src/utils')
    }
  }
});
```

### 2. 环境变量
```bash
# .env.production
VITE_API_URL=https://api.histagent.com
VITE_WS_URL=wss://api.histagent.com/ws
VITE_UPLOAD_URL=https://api.histagent.com/upload
VITE_ENABLE_DEBUG=false
VITE_ENABLE_ANALYTICS=true
```

### 3. 部署脚本
```bash
#!/bin/bash
# deploy.sh

# 构建项目
npm run build

# 检查构建是否成功
if [ $? -eq 0 ]; then
  echo "Build successful"
  
  # 部署到服务器
  rsync -avz --delete dist/ user@server:/var/www/histagent/
  
  echo "Deployment completed"
else
  echo "Build failed"
  exit 1
fi
```

### 4. Docker 部署
```dockerfile
# Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 常见问题解决

### 1. 开发环境问题

#### WebSocket 连接失败
```typescript
// 解决方案：添加重连逻辑和错误处理
const websocketService = new WebSocketService({
  url: 'ws://localhost:8000/ws/',
  maxReconnectAttempts: 10,
  reconnectDelay: 2000,
  onConnectionError: (error) => {
    console.error('WebSocket connection failed:', error);
    // 显示用户友好的错误信息
  }
});
```

#### 热重载不工作
```bash
# 清理缓存
rm -rf node_modules/.cache
rm -rf .vite

# 重新安装依赖
npm ci
npm run dev
```

#### TypeScript 类型错误
```typescript
// 创建类型声明文件
// src/types/global.d.ts
declare module '*.module.css' {
  const classes: { [key: string]: string };
  export default classes;
}

declare module '*.svg' {
  const content: string;
  export default content;
}
```

### 2. 性能问题

#### 大列表渲染卡顿
```typescript
// 使用虚拟化列表
import { FixedSizeList } from 'react-window';

const VirtualizedList = ({ items }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <ListItem data={items[index]} />
    </div>
  );
  
  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
    >
      {Row}
    </FixedSizeList>
  );
};
```

#### 状态更新频繁
```typescript
// 使用防抖优化
import { useDebouncedCallback } from 'use-debounce';

const SearchInput = () => {
  const [query, setQuery] = useState('');
  
  const debouncedSearch = useDebouncedCallback(
    (value: string) => {
      // 执行搜索
      performSearch(value);
    },
    300
  );
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    debouncedSearch(value);
  };
  
  return <input value={query} onChange={handleChange} />;
};
```

---

**更新时间**: 2024年
**版本**: v1.0.0
**维护者**: HistAgent 开发团队 