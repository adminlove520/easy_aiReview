from ..base import KnowledgeCategory, KnowledgeDocument

react_knowledge = [
    KnowledgeDocument(
        id="react-1",
        title="React 安全最佳实践",
        content="""# React 安全最佳实践

## 核心安全原则

### 1. 防止 XSS 攻击
React 默认会转义 HTML，但是在某些情况下仍然需要注意。

```jsx
// 安全的做法：React 会自动转义
const userInput = '<script>alert("XSS")</script>';
function App() {
  return <div>{userInput}</div>; // 会被转义为 &lt;script&gt;alert("XSS")&lt;/script&gt;
}

// 不安全的做法：使用 dangerouslySetInnerHTML
function UnsafeComponent() {
  return <div dangerouslySetInnerHTML={{ __html: userInput }} />; // 直接渲染 HTML
}

// 安全使用 dangerouslySetInnerHTML
import DOMPurify from 'dompurify';

function SafeComponent() {
  const sanitizedHtml = DOMPurify.sanitize(userInput);
  return <div dangerouslySetInnerHTML={{ __html: sanitizedHtml }} />;
}
```

### 2. 保护敏感信息

```jsx
// 错误示例：硬编码敏感信息
const API_KEY = 'sk-1234567890abcdef';

// 正确做法：使用环境变量
const API_KEY = process.env.REACT_APP_API_KEY;

// 或者使用服务器端代理
async function fetchData() {
  const response = await fetch('/api/data');
  const data = await response.json();
  return data;
}
```

### 3. 防止 CSRF 攻击

```jsx
// 使用 CSRF 令牌
function submitForm() {
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  
  fetch('/api/submit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken
    },
    body: JSON.stringify({ data: formData })
  });
}
```

## 组件安全

### 1. 安全的 props 传递

```jsx
// 错误示例：直接传递函数引用
function Parent() {
  const handleClick = () => {
    console.log('Clicked');
  };
  return <Child onClick={handleClick} />;
}

// 正确做法：使用 useCallback
import { useCallback } from 'react';

function Parent() {
  const handleClick = useCallback(() => {
    console.log('Clicked');
  }, []);
  return <Child onClick={handleClick} />;
}
```

### 2. 防止组件注入

```jsx
// 错误示例：直接渲染用户提供的组件
function DynamicComponent({ component }) {
  return <component />; // 危险：用户可以注入任意组件
}

// 正确做法：使用组件白名单
const allowedComponents = {
  Button: Button,
  Card: Card
};

function SafeDynamicComponent({ componentName }) {
  const Component = allowedComponents[componentName];
  if (!Component) return null;
  return <Component />;
}
```

## 状态管理安全

### 1. Redux 安全

```jsx
// 错误示例：在 reducer 中执行副作用
function counterReducer(state = 0, action) {
  switch (action.type) {
    case 'INCREMENT':
      // 危险：在 reducer 中执行 API 调用
      fetch('/api/log', {
        method: 'POST',
        body: JSON.stringify({ action: 'increment' })
      });
      return state + 1;
    default:
      return state;
  }
}

// 正确做法：使用 middleware 处理副作用
const loggerMiddleware = store => next => action => {
  console.log('dispatching', action);
  const result = next(action);
  console.log('next state', store.getState());
  return result;
};
```

### 2. 保护状态中的敏感数据

```jsx
// 错误示例：在 localStorage 中存储敏感信息
function saveUser(user) {
  localStorage.setItem('user', JSON.stringify(user)); // 危险：包含密码等敏感信息
}

// 正确做法：只存储必要的信息
function saveUserSession(user) {
  const { id, username, email } = user;
  localStorage.setItem('userSession', JSON.stringify({ id, username, email }));
}
```

## API 调用安全

### 1. 安全的 API 请求

```jsx
// 错误示例：直接拼接 URL
function fetchUser(id) {
  return fetch(`/api/users/${id}`); // 可能导致路径遍历攻击
}

// 正确做法：使用参数化 URL
function fetchUser(id) {
  return fetch('/api/users/' + encodeURIComponent(id));
}

// 或者使用查询参数
function searchUsers(query) {
  const params = new URLSearchParams({ q: query });
  return fetch(`/api/users?${params.toString()}`);
}
```

### 2. 处理 API 错误

```jsx
async function fetchData() {
  try {
    const response = await fetch('/api/data');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Fetch error:', error);
    // 显示用户友好的错误信息
    return { error: 'Failed to fetch data. Please try again later.' };
  }
}
```

## 依赖管理

### 1. 定期更新依赖

```bash
# 检查过时的依赖
npm outdated

# 更新依赖
npm update

# 检查安全漏洞
npm audit
npm audit fix
```

### 2. 安全的依赖安装

```bash
# 安装特定版本
npm install package@version

# 安装带有安全修复的版本
npm install package@^version
```

## 构建和部署安全

### 1. 生产环境优化

```json
// package.json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}

// 构建生产版本
npm run build
```

### 2. 环境变量配置

```env
# .env.local
REACT_APP_API_URL=https://api.example.com
REACT_APP_ENVIRONMENT=production

# .env.development.local
REACT_APP_API_URL=http://localhost:3001
REACT_APP_ENVIRONMENT=development
```

### 3. 使用 HTTPS
在生产环境中，始终使用 HTTPS。

## 第三方库安全

### 1. 验证第三方库

```bash
# 检查库的安全状态
npm audit package-name

# 查看库的依赖树
npm ls package-name
```

### 2. 安全使用第三方库

```jsx
// 错误示例：使用已废弃的库
import moment from 'moment'; // 已废弃，建议使用 date-fns 或 dayjs

// 正确做法：使用活跃维护的库
import { format } from 'date-fns';

// 检查库的权限
// package.json 中的 permissions 字段
```

## 代码分割和性能

### 1. 实现代码分割

```jsx
// 使用 React.lazy 和 Suspense
import React, { lazy, Suspense } from 'react';

const LazyComponent = lazy(() => import('./LazyComponent'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LazyComponent />
    </Suspense>
  );
}

// 基于路由的代码分割
import { BrowserRouter, Routes, Route } from 'react-router-dom';

const Home = lazy(() => import('./Home'));
const About = lazy(() => import('./About'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

### 2. 优化渲染性能

```jsx
// 使用 memo 减少不必要的渲染
import { memo } from 'react';

const ExpensiveComponent = memo(({ prop1, prop2 }) => {
  // 昂贵的计算
  return <div>{prop1 + prop2}</div>;
});

// 使用 useMemo 缓存计算结果
import { useMemo } from 'react';

function App({ items }) {
  const sortedItems = useMemo(() => {
    return items.sort((a, b) => a.name.localeCompare(b.name));
  }, [items]);
  
  return (
    <ul>
      {sortedItems.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}
```

## 测试安全

### 1. 单元测试

```jsx
// 使用 Jest 和 React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});

test('handles form submission', () => {
  render(<App />);
  const input = screen.getByLabelText(/name/i);
  const button = screen.getByText(/submit/i);
  
  fireEvent.change(input, { target: { value: 'Test User' } });
  fireEvent.click(button);
  
  expect(screen.getByText(/Hello, Test User!/i)).toBeInTheDocument();
});
```

### 2. 安全测试

```jsx
// 测试 XSS 防护
import { render } from '@testing-library/react';
import SafeComponent from './SafeComponent';

test('sanitizes user input', () => {
  const userInput = '<script>alert("XSS")</script>';
  const { container } = render(<SafeComponent input={userInput} />);
  
  expect(container.innerHTML).not.toContain('<script>');
  expect(container.innerHTML).toContain('&lt;script&gt;');
});
```

## 总结

React 应用程序的安全需要多层防御策略，包括：

1. **防止 XSS 攻击**：使用 React 的自动转义，安全使用 dangerouslySetInnerHTML
2. **保护敏感信息**：使用环境变量，不在客户端存储敏感数据
3. **防止 CSRF 攻击**：使用 CSRF 令牌
4. **组件安全**：安全的 props 传递，防止组件注入
5. **状态管理安全**：在 reducer 中不执行副作用，保护状态中的敏感数据
6. **API 调用安全**：使用参数化 URL，处理 API 错误
7. **依赖管理**：定期更新依赖，检查安全漏洞
8. **构建和部署安全**：生产环境优化，使用 HTTPS
9. **第三方库安全**：验证第三方库，安全使用
10. **代码分割和性能**：实现代码分割，优化渲染性能
11. **测试安全**：单元测试，安全测试

通过实施这些最佳实践，可以显著提高 React 应用程序的安全性。""",
        category=KnowledgeCategory.FRAMEWORK,
        tags=["react", "javascript", "security", "best-practice"],
        severity="medium",
        cwe_ids=["CWE-79", "CWE-352", "CWE-614"],
        owasp_ids=["A1", "A2", "A3"]
    ),
    KnowledgeDocument(
        id="react-2",
        title="React 性能优化",
        content="""# React 性能优化

## 核心优化原则

### 1. 减少不必要的渲染

```jsx
// 使用 React.memo 缓存组件
import React, { memo } from 'react';

const ExpensiveComponent = memo(({ data }) => {
  console.log('Rendering ExpensiveComponent');
  // 昂贵的计算
  return <div>{data.value}</div>;
});

// 只有当 data 变化时才会重新渲染
function Parent() {
  const [count, setCount] = useState(0);
  const [data] = useState({ value: 'Hello' });
  
  return (
    <div>
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <ExpensiveComponent data={data} />
    </div>
  );
}
```

### 2. 使用 useMemo 缓存计算结果

```jsx
import React, { useMemo } from 'react';

function ListComponent({ items, filter }) {
  // 只有当 items 或 filter 变化时才会重新计算
  const filteredItems = useMemo(() => {
    console.log('Filtering items');
    return items.filter(item => item.includes(filter));
  }, [items, filter]);
  
  return (
    <ul>
      {filteredItems.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ul>
  );
}
```

### 3. 使用 useCallback 缓存函数

```jsx
import React, { useCallback } from 'react';

function Button({ onClick, children }) {
  return <button onClick={onClick}>{children}</button>;
}

function Parent() {
  const [count, setCount] = useState(0);
  
  // 只有当 count 变化时才会重新创建这个函数
  const handleClick = useCallback(() => {
    console.log('Button clicked', count);
  }, [count]);
  
  return (
    <div>
      <Button onClick={handleClick}>Click me</Button>
      <p>Count: {count}</p>
    </div>
  );
}
```

## 代码分割

### 1. 基于路由的代码分割

```jsx
import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

// 懒加载组件
const Home = lazy(() => import('./Home'));
const About = lazy(() => import('./About'));
const Contact = lazy(() => import('./Contact'));

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
        <Link to="/contact">Contact</Link>
      </nav>
      
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

### 2. 基于条件的代码分割

```jsx
import React, { lazy, Suspense, useState } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  const [showHeavyComponent, setShowHeavyComponent] = useState(false);
  
  return (
    <div>
      <button onClick={() => setShowHeavyComponent(true)}>
        Load Heavy Component
      </button>
      
      {showHeavyComponent && (
        <Suspense fallback={<div>Loading heavy component...</div>}>
          <HeavyComponent />
        </Suspense>
      )}
    </div>
  );
}
```

## 状态管理优化

### 1. 优化 Context 使用

```jsx
import React, { createContext, useContext, useState, useMemo } from 'react';

const UserContext = createContext();

function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('light');
  
  // 只有当 user 或 theme 变化时才会重新创建 value
  const contextValue = useMemo(() => ({
    user,
    setUser,
    theme,
    setTheme
  }), [user, theme]);
  
  return (
    <UserContext.Provider value={contextValue}>
      {children}
    </UserContext.Provider>
  );
}

function useUser() {
  return useContext(UserContext);
}
```

### 2. 状态拆分

```jsx
// 不好的做法：单个大状态对象
function App() {
  const [state, setState] = useState({
    user: null,
    posts: [],
    comments: [],
    notifications: []
  });
  
  // 更新任何一个字段都会导致整个组件重新渲染
  const updateUser = (user) => {
    setState(prev => ({ ...prev, user }));
  };
  
  return (
    <div>
      {/* 组件内容 */}
    </div>
  );
}

// 好的做法：拆分状态
function App() {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [comments, setComments] = useState([]);
  const [notifications, setNotifications] = useState([]);
  
  // 只有使用对应状态的组件才会重新渲染
  return (
    <div>
      {/* 组件内容 */}
    </div>
  );
}
```

## 虚拟滚动

### 1. 使用 react-window 实现虚拟滚动

```jsx
import React from 'react';
import { FixedSizeList as List } from 'react-window';

function VirtualizedList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      {items[index]}
    </div>
  );
  
  return (
    <List
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {Row}
    </List>
  );
}

// 使用示例
function App() {
  const [items] = useState(Array.from({ length: 10000 }, (_, i) => `Item ${i}`));
  
  return (
    <div>
      <h1>Virtualized List</h1>
      <VirtualizedList items={items} />
    </div>
  );
}
```

## 图片优化

### 1. 懒加载图片

```jsx
// 使用 React.lazy 或原生 loading 属性
function ImageComponent({ src, alt }) {
  return (
    <img 
      src={src} 
      alt={alt} 
      loading="lazy" 
      width="300" 
      height="200"
    />
  );
}

// 使用第三方库
import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';

function OptimizedImage({ src, alt }) {
  return (
    <LazyLoadImage
      src={src}
      alt={alt}
      effect="blur"
      width={300}
      height={200}
    />
  );
}
```

### 2. 使用适当的图片格式

```jsx
function ImageGallery() {
  return (
    <div>
      {/* 使用 WebP 格式，带 fallback */}
      <picture>
        <source srcSet="image.webp" type="image/webp" />
        <source srcSet="image.jpg" type="image/jpeg" />
        <img src="image.jpg" alt="Description" />
      </picture>
    </div>
  );
}
```

## 网络请求优化

### 1. 缓存 API 请求

```jsx
import { useQuery } from 'react-query';

function DataComponent({ id }) {
  const { data, isLoading, error } = useQuery(
    ['user', id], // 缓存键
    () => fetch(`/api/users/${id}`).then(res => res.json()),
    {
      staleTime: 5 * 60 * 1000, // 5分钟内视为新鲜
      cacheTime: 10 * 60 * 1000, // 10分钟后从缓存中移除
    }
  );
  
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return <div>{data.name}</div>;
}
```

### 2. 批量请求

```jsx
import { useQueries } from 'react-query';

function MultipleDataComponent({ ids }) {
  const queries = useQueries(
    ids.map(id => ({
      queryKey: ['user', id],
      queryFn: () => fetch(`/api/users/${id}`).then(res => res.json()),
    }))
  );
  
  return (
    <div>
      {queries.map((query, index) => {
        if (query.isLoading) return <div key={index}>Loading...</div>;
        if (query.error) return <div key={index}>Error</div>;
        return <div key={index}>{query.data.name}</div>;
      })}
    </div>
  );
}
```

## 构建优化

### 1. 代码分割

```jsx
// 动态导入组件
import React, { lazy, Suspense } from 'react';

const AdminPanel = lazy(() => import('./AdminPanel'));
const UserDashboard = lazy(() => import('./UserDashboard'));

function App() {
  const [isAdmin, setIsAdmin] = useState(false);
  
  return (
    <div>
      <Suspense fallback={<div>Loading...</div>}>
        {isAdmin ? <AdminPanel /> : <UserDashboard />}
      </Suspense>
    </div>
  );
}
```

### 2. 生产环境构建

```bash
# 构建生产版本
npm run build

# 分析构建包大小
npm install --save-dev webpack-bundle-analyzer

# 在 package.json 中添加脚本
"scripts": {
  "analyze": "npm run build && npx webpack-bundle-analyzer build/static/js/*.js"
}

# 运行分析
npm run analyze
```

### 3. Tree Shaking

```jsx
// 只导入需要的函数
import { debounce } from 'lodash/debounce';
// 而不是
import _ from 'lodash';

// 使用 ES6 模块
import { format } from 'date-fns';
```

## 渲染优化

### 1. 使用 key 属性

```jsx
// 不好的做法：使用索引作为 key
function List({ items }) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={index}>{item.name}</li> // 当 items 顺序变化时会导致性能问题
      ))}
    </ul>
  );
}

// 好的做法：使用唯一标识符作为 key
function List({ items }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{item.name}</li> // 稳定的 key
      ))}
    </ul>
  );
}
```

### 2. 避免内联样式

```jsx
// 不好的做法：内联样式
function Component() {
  return (
    <div style={{ 
      backgroundColor: 'red', 
      padding: '10px',
      margin: '10px'
    }}>
      Content
    </div>
  );
}

// 好的做法：使用 CSS 类
function Component() {
  return <div className="container">Content</div>;
}

// 或者使用 CSS-in-JS
import styled from 'styled-components';

const Container = styled.div`
  background-color: red;
  padding: 10px;
  margin: 10px;
`;

function Component() {
  return <Container>Content</Container>;
}
```

## 总结

React 性能优化的关键策略包括：

1. **减少不必要的渲染**：使用 React.memo, useMemo, useCallback
2. **代码分割**：基于路由和条件的代码分割
3. **状态管理优化**：Context 优化，状态拆分
4. **虚拟滚动**：处理大型列表
5. **图片优化**：懒加载，适当的图片格式
6. **网络请求优化**：缓存 API 请求，批量请求
7. **构建优化**：代码分割，生产环境构建，Tree Shaking
8. **渲染优化**：使用 key 属性，避免内联样式

通过实施这些优化策略，可以显著提高 React 应用程序的性能和用户体验。""",
        category=KnowledgeCategory.FRAMEWORK,
        tags=["react", "javascript", "performance", "optimization"],
        severity="low",
        cwe_ids=[],
        owasp_ids=[]
    ),
    KnowledgeDocument(
        id="react-3",
        title="React 错误处理",
        content="""# React 错误处理

## 基础错误处理

### 1. 使用 try-catch

```jsx
function FetchComponent() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch('/api/data');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err.message);
        setData(null);
      } finally {
        setLoading(false);
      }
    }
    
    fetchData();
  }, []);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return <div>Data: {data}</div>;
}
```

### 2. 错误边界

```jsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  
  static getDerivedStateFromError(error) {
    // 更新状态，下次渲染时显示错误界面
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    // 记录错误信息
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      // 自定义错误界面
      return (
        <div>
          <h2>Something went wrong.</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}

// 使用错误边界
function App() {
  return (
    <ErrorBoundary>
      <ComponentThatMightError />
    </ErrorBoundary>
  );
}
```

## 高级错误处理

### 1. 全局错误处理

```jsx
// 在 index.js 中设置全局错误处理
import { ErrorBoundary } from 'react-error-boundary';

function errorHandler(error, errorInfo) {
  // 记录错误到监控服务
  console.error('Global error:', error, errorInfo);
  // 可以发送错误到 Sentry 等服务
}

function fallbackComponent({ error, resetErrorBoundary }) {
  return (
    <div>
      <h1>An error occurred</h1>
      <p>{error.message}</p>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

ReactDOM.render(
  <ErrorBoundary
    onError={errorHandler}
    FallbackComponent={fallbackComponent}
  >
    <App />
  </ErrorBoundary>,
  document.getElementById('root')
);
```

### 2. 异步错误处理

```jsx
function AsyncComponent() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  
  const fetchData = async () => {
    try {
      const response = await fetch('/api/data');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err);
    }
  };
  
  return (
    <div>
      <button onClick={fetchData}>Fetch Data</button>
      {error && <div>Error: {error.message}</div>}
      {data && <div>Data: {data}</div>}
    </div>
  );
}
```

## 表单错误处理

### 1. 表单验证错误

```jsx
import { useState } from 'react';

function LoginForm() {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      // 提交表单
      console.log('Form submitted:', formData);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Email</label>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        />
        {errors.email && <div style={{ color: 'red' }}>{errors.email}</div>}
      </div>
      <div>
        <label>Password</label>
        <input
          type="password"
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
        />
        {errors.password && <div style={{ color: 'red' }}>{errors.password}</div>}
      </div>
      <button type="submit">Submit</button>
    </form>
  );
}
```

### 2. 使用 Formik 进行表单错误处理

```jsx
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';

const LoginSchema = Yup.object().shape({
  email: Yup.string()
    .email('Invalid email')
    .required('Email is required'),
  password: Yup.string()
    .min(6, 'Password must be at least 6 characters')
    .required('Password is required'),
});

function LoginForm() {
  return (
    <Formik
      initialValues={{ email: '', password: '' }}
      validationSchema={LoginSchema}
      onSubmit={(values) => {
        console.log('Form submitted:', values);
      }}
    >
      {({ errors, touched }) => (
        <Form>
          <div>
            <label>Email</label>
            <Field type="email" name="email" />
            <ErrorMessage name="email" component="div" style={{ color: 'red' }} />
          </div>
          <div>
            <label>Password</label>
            <Field type="password" name="password" />
            <ErrorMessage name="password" component="div" style={{ color: 'red' }} />
          </div>
          <button type="submit">Submit</button>
        </Form>
      )}
    </Formik>
  );
}
```

## API 错误处理

### 1. 统一 API 错误处理

```jsx
class ApiService {
  async request(url, options = {}) {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }
  
  async get(url) {
    return this.request(url);
  }
  
  async post(url, data) {
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

const api = new ApiService();

// 使用
async function fetchUsers() {
  try {
    const users = await api.get('/api/users');
    return users;
  } catch (error) {
    console.error('Failed to fetch users:', error);
    throw error;
  }
}
```

### 2. 错误重试机制

```jsx
async function fetchWithRetry(url, options = {}, retries = 3, delay = 1000) {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    if (retries > 0) {
      console.log(`Retrying... (${retries} attempts left)`);
      await new Promise(resolve => setTimeout(resolve, delay));
      return fetchWithRetry(url, options, retries - 1, delay * 2);
    }
    throw error;
  }
}

// 使用
async function fetchData() {
  try {
    const data = await fetchWithRetry('/api/data');
    return data;
  } catch (error) {
    console.error('Failed to fetch data after retries:', error);
    throw error;
  }
}
```

## 测试错误处理

### 1. 单元测试中的错误处理

```jsx
import { render, screen, fireEvent } from '@testing-library/react';
import ErrorComponent from './ErrorComponent';

test('renders error message when error occurs', () => {
  render(<ErrorComponent />);
  
  // 触发错误
  fireEvent.click(screen.getByText('Trigger Error'));
  
  // 验证错误信息是否显示
  expect(screen.getByText('Something went wrong')).toBeInTheDocument();
});

test('resets error when try again is clicked', () => {
  render(<ErrorComponent />);
  
  // 触发错误
  fireEvent.click(screen.getByText('Trigger Error'));
  expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  
  // 点击重试
  fireEvent.click(screen.getByText('Try again'));
  expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument();
});
```

### 2. 模拟 API 错误

```jsx
import { render, screen, waitFor } from '@testing-library/react';
import FetchComponent from './FetchComponent';

// 模拟 fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

test('displays error when API call fails', async () => {
  // 模拟错误响应
  mockFetch.mockRejectedValueOnce(new Error('Network error'));
  
  render(<FetchComponent />);
  
  // 验证错误信息是否显示
  await waitFor(() => {
    expect(screen.getByText('Error: Network error')).toBeInTheDocument();
  });
});
```

## 总结

React 错误处理的最佳实践包括：

1. **基础错误处理**：使用 try-catch，错误边界
2. **高级错误处理**：全局错误处理，异步错误处理
3. **表单错误处理**：表单验证错误，使用 Formik
4. **API 错误处理**：统一 API 错误处理，错误重试机制
5. **测试错误处理**：单元测试中的错误处理，模拟 API 错误

通过实施这些最佳实践，可以构建更健壮、更可靠的 React 应用程序。""",
        category=KnowledgeCategory.FRAMEWORK,
        tags=["react", "javascript", "error-handling", "best-practice"],
        severity="low",
        cwe_ids=[],
        owasp_ids=[]
    ),
    KnowledgeDocument(
        id="react-4",
        title="React 代码风格最佳实践",
        content="""# React 代码风格最佳实践

## 核心风格原则

### 1. 组件命名

```jsx
// 好的做法：使用 PascalCase 命名组件
function UserProfile() {
  return <div>User Profile</div>;
}

// 好的做法：使用 PascalCase 命名文件
// UserProfile.jsx

// 不好的做法：使用 camelCase 命名组件
function userProfile() {
  return <div>User Profile</div>;
}
```

### 2. 变量和函数命名

```jsx
// 好的做法：使用 camelCase 命名变量和函数
const userName = 'John';
function getUserData() {
  return { name: userName };
}

// 好的做法：使用 UPPER_SNAKE_CASE 命名常量
const API_URL = 'https://api.example.com';

// 不好的做法：使用 PascalCase 命名变量
const UserName = 'John';
```

### 3. 组件结构

```jsx
// 好的做法：使用函数组件
import React from 'react';

function Component() {
  return <div>Component</div>;
}

// 好的做法：使用箭头函数
const Component = () => {
  return <div>Component</div>;
};

// 好的做法：简洁的组件
const SimpleComponent = () => <div>Simple Component</div>;
```

## JSX 风格

### 1. 缩进和换行

```jsx
// 好的做法：适当的缩进和换行
function Component() {
  return (
    <div className="container">
      <h1>Hello World</h1>
      <p>This is a paragraph</p>
    </div>
  );
}

// 不好的做法：不适当的缩进
function Component() {
return <div className="container"><h1>Hello World</h1><p>This is a paragraph</p></div>;
}
```

### 2. 属性顺序

```jsx
// 好的做法：一致的属性顺序
function Component() {
  return (
    <div
      id="container"
      className="flex"
      style={{ backgroundColor: 'red' }}
      onClick={() => console.log('Clicked')}
    >
      Content
    </div>
  );
}

// 建议的属性顺序：
// 1. ID 和 className
// 2. 样式属性
// 3. 事件处理程序
// 4. 其他属性
```

### 3. 引号使用

```jsx
// 好的做法：JSX 属性使用双引号
function Component() {
  return <div className="container">Content</div>;
}

// 好的做法：JavaScript 字符串使用单引号
const message = 'Hello';

// 不好的做法：JSX 属性使用单引号
function Component() {
  return <div className='container'>Content</div>;
}
```

## 代码组织

### 1. 文件结构

```
// 好的做法：按功能组织文件
/src
  /components
    /Button
      Button.jsx
      Button.css
    /UserProfile
      UserProfile.jsx
      UserProfile.css
  /pages
    /Home
      Home.jsx
    /About
      About.jsx
  /utils
    api.js
    helpers.js
  /hooks
    useAuth.js
    useLocalStorage.js
  App.jsx
  index.jsx
```

### 2. 导入顺序

```jsx
// 好的做法：一致的导入顺序
import React from 'react';
import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import Button from './components/Button';
import { getUserData } from './utils/api';

// 建议的导入顺序：
// 1. React 和 React 相关库
// 2. 第三方库
// 3. 本地组件
// 4. 本地工具函数
```

### 3. 注释

```jsx
// 好的做法：使用注释解释复杂逻辑
function ComplexComponent() {
  // 计算用户分数
  // 公式：基础分数 + 奖励分数 - 惩罚分数
  const calculateScore = (user) => {
    return user.baseScore + user.bonusScore - user.penaltyScore;
  };
  
  return <div>Component</div>;
}

// 好的做法：使用 JSDoc 注释函数
/**
 * 获取用户数据
 * @param {string} userId - 用户 ID
 * @returns {Promise<Object>} 用户数据
 */
async function getUserData(userId) {
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
}
```

## 性能和可读性

### 1. 避免内联函数

```jsx
// 不好的做法：内联函数
function Component() {
  return (
    <button onClick={() => console.log('Clicked')}>
      Click me
    </button>
  );
}

// 好的做法：提取函数
function Component() {
  const handleClick = () => {
    console.log('Clicked');
  };
  
  return (
    <button onClick={handleClick}>
      Click me
    </button>
  );
}
```

### 2. 避免复杂的条件渲染

```jsx
// 不好的做法：复杂的条件渲染
function Component({ user }) {
  return (
    <div>
      {user ? (
        user.isAdmin ? (
          <AdminPanel />
        ) : (
          <UserPanel />
        )
      ) : (
        <GuestPanel />
      )}
    </div>
  );
}

// 好的做法：提取条件渲染逻辑
function Component({ user }) {
  const renderPanel = () => {
    if (!user) return <GuestPanel />;
    if (user.isAdmin) return <AdminPanel />;
    return <UserPanel />;
  };
  
  return (
    <div>
      {renderPanel()}
    </div>
  );
}
```

### 3. 使用解构赋值

```jsx
// 好的做法：使用解构赋值
function UserComponent({ user: { name, email, age } }) {
  return (
    <div>
      <h2>{name}</h2>
      <p>{email}</p>
      <p>{age}</p>
    </div>
  );
}

// 好的做法：使用默认值
function Component({ title = 'Default Title', items = [] }) {
  return (
    <div>
      <h1>{title}</h1>
      <ul>
        {items.map(item => <li key={item.id}>{item.name}</li>)}
      </ul>
    </div>
  );
}
```

## 最佳实践总结

### 1. 使用 ESLint 和 Prettier

```bash
# 安装 ESLint 和 Prettier
npm install --save-dev eslint prettier eslint-plugin-react eslint-config-prettier eslint-plugin-prettier

# 创建 .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "prettier"
  ],
  "plugins": ["react", "prettier"],
  "rules": {
    "prettier/prettier": "error"
  }
}

# 创建 .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5"
}

# 在 package.json 中添加脚本
"scripts": {
  "lint": "eslint src",
  "format": "prettier --write src"
}
```

### 2. 使用 TypeScript

```bash
# 创建 TypeScript 项目
npx create-react-app my-app --template typescript

# 或者在现有项目中添加 TypeScript
npm install --save-dev typescript @types/react @types/react-dom
```

### 3. 测试

```bash
# 安装测试库
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event

# 运行测试
npm test
```

## 总结

React 代码风格的最佳实践包括：

1. **核心风格原则**：组件命名，变量和函数命名，组件结构
2. **JSX 风格**：缩进和换行，属性顺序，引号使用
3. **代码组织**：文件结构，导入顺序，注释
4. **性能和可读性**：避免内联函数，避免复杂的条件渲染，使用解构赋值
5. **工具使用**：使用 ESLint 和 Prettier，使用 TypeScript，测试

通过实施这些最佳实践，可以编写更清晰、更可维护的 React 代码。""",
        category=KnowledgeCategory.FRAMEWORK,
        tags=["react", "javascript", "code-style", "best-practice"],
        severity="low",
        cwe_ids=[],
        owasp_ids=[]
    )
]
