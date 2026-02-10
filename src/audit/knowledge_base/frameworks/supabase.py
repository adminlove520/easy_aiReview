from ..base import KnowledgeCategory, KnowledgeDocument

supabase_knowledge = [
    KnowledgeDocument(
        id="supabase-1",
        title="Supabase 安全最佳实践",
        content="""# Supabase 安全最佳实践

## 核心安全配置

### 1. 项目配置

```javascript
// 初始化 Supabase 客户端
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

### 2. 认证安全

```javascript
// 安全的认证流程
async function signIn(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  });
  
  if (error) {
    console.error('Sign in error:', error);
    return null;
  }
  
  return data.user;
}

// 退出登录
async function signOut() {
  const { error } = await supabase.auth.signOut();
  if (error) {
    console.error('Sign out error:', error);
  }
}
```

### 3. 行级安全 (RLS)

在 Supabase Dashboard 中配置行级安全策略：

```sql
-- 为 users 表启用 RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 创建策略：用户只能访问自己的数据
CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (auth.uid() = id);

-- 创建策略：用户只能更新自己的数据
CREATE POLICY "Users can update own profile" ON users
  FOR UPDATE USING (auth.uid() = id);
```

## API 安全

### 1. 安全的 API 调用

```javascript
// 安全的查询
async function getUserProfile() {
  const { data, error } = await supabase
    .from('users')
    .select('*')
    .eq('id', supabase.auth.user()?.id)
    .single();
  
  if (error) {
    console.error('Error fetching profile:', error);
    return null;
  }
  
  return data;
}

// 安全的插入
async function createPost(content) {
  const { data, error } = await supabase
    .from('posts')
    .insert({
      content,
      user_id: supabase.auth.user()?.id
    })
    .select()
    .single();
  
  if (error) {
    console.error('Error creating post:', error);
    return null;
  }
  
  return data;
}
```

### 2. 错误处理

```javascript
async function fetchData() {
  try {
    const { data, error } = await supabase
      .from('table')
      .select('*');
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Fetch error:', error);
    // 显示用户友好的错误信息
    return { error: 'Failed to fetch data. Please try again later.' };
  }
}
```

## 存储安全

### 1. 存储桶配置

在 Supabase Dashboard 中配置存储桶权限：

- **公开存储桶**：适合公开访问的文件，如图像
- **私有存储桶**：适合需要认证的文件，如用户文档

### 2. 安全的文件上传

```javascript
async function uploadFile(file) {
  const { data, error } = await supabase
    .storage
    .from('avatars')
    .upload(`public/${supabase.auth.user()?.id}/${file.name}`, file, {
      cacheControl: '3600',
      upsert: false
    });
  
  if (error) {
    console.error('Upload error:', error);
    return null;
  }
  
  // 获取文件 URL
  const { data: urlData } = supabase
    .storage
    .from('avatars')
    .getPublicUrl(`public/${supabase.auth.user()?.id}/${file.name}`);
  
  return urlData.publicUrl;
}
```

### 3. 访问控制

```sql
-- 为 storage.objects 表创建策略
CREATE POLICY "Users can view own avatars" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'avatars' AND
    auth.uid() = owner_id
  );
```

## 实时订阅安全

### 1. 安全的实时订阅

```javascript
// 订阅自己的帖子更新
const { data: subscription } = supabase
  .from(`posts:user_id=eq.${supabase.auth.user()?.id}`)
  .on('INSERT', payload => {
    console.log('New post:', payload.new);
  })
  .subscribe();

// 清理订阅
function cleanup() {
  subscription.unsubscribe();
}
```

### 2. 限制订阅范围

```javascript
// 只订阅需要的事件和列
const { data: subscription } = supabase
  .from('posts')
  .select('id, title, content')
  .eq('user_id', supabase.auth.user()?.id)
  .on('UPDATE', payload => {
    console.log('Updated post:', payload.new);
  })
  .subscribe();
```

## 环境变量管理

### 1. 安全的环境变量配置

```env
# .env.local
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key

# 服务端密钥（不要在客户端使用）
# SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### 2. 服务端密钥管理

服务端密钥应该只在服务器端使用，永远不要在客户端代码中暴露。

```javascript
// 服务器端代码（如 Next.js API route）
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseServiceKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
});

// 服务端操作
async function adminTask() {
  const { data, error } = await supabase
    .from('users')
    .select('*');
  
  return data;
}
```

## 数据验证

### 1. 客户端验证

```javascript
// 验证用户输入
function validateUserInput(userData) {
  const errors = {};
  
  if (!userData.email) {
    errors.email = 'Email is required';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(userData.email)) {
    errors.email = 'Email is invalid';
  }
  
  if (!userData.password) {
    errors.password = 'Password is required';
  } else if (userData.password.length < 6) {
    errors.password = 'Password must be at least 6 characters';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
}
```

### 2. 数据库验证

使用 PostgreSQL 的约束来验证数据：

```sql
-- 添加约束
ALTER TABLE users
  ADD CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- 添加唯一约束
ALTER TABLE users
  ADD CONSTRAINT users_email_unique UNIQUE (email);
```

## 最佳实践总结

1. **认证安全**：使用 Supabase 的内置认证，启用 2FA
2. **行级安全**：为所有表启用 RLS，创建适当的策略
3. **API 安全**：只查询需要的数据，验证用户输入
4. **存储安全**：使用适当的存储桶权限，限制文件访问
5. **实时订阅**：限制订阅范围，避免过度订阅
6. **环境变量**：安全管理环境变量，不暴露服务端密钥
7. **数据验证**：在客户端和数据库层面都进行验证
8. **错误处理**：适当处理错误，不暴露敏感信息

通过实施这些最佳实践，可以构建安全、可靠的 Supabase 应用程序。""",
        category=KnowledgeCategory.FRAMEWORK,
        tags=["supabase", "security", "best-practice"],
        severity="medium",
        cwe_ids=["CWE-614", "CWE-352", "CWE-79"],
        owasp_ids=["A1", "A2", "A3"]
    ),
    KnowledgeDocument(
        id="supabase-2",
        title="Supabase 性能优化",
        content="""# Supabase 性能优化

## 核心优化策略

### 1. 查询优化

```javascript
// 不好的做法：选择所有列
const { data, error } = await supabase
  .from('users')
  .select('*');

// 好的做法：只选择需要的列
const { data, error } = await supabase
  .from('users')
  .select('id, name, email');

// 使用过滤器减少返回数据
const { data, error } = await supabase
  .from('posts')
  .select('id, title, content')
  .eq('user_id', userId)
  .limit(10);
```

### 2. 索引优化

在 Supabase Dashboard 中为频繁查询的列添加索引：

```sql
-- 为 user_id 列添加索引
CREATE INDEX idx_posts_user_id ON posts(user_id);

-- 为 created_at 列添加索引
CREATE INDEX idx_posts_created_at ON posts(created_at);

-- 为复合查询添加索引
CREATE INDEX idx_posts_user_id_created_at ON posts(user_id, created_at);
```

### 3. 批量操作

```javascript
// 批量插入
const { data, error } = await supabase
  .from('posts')
  .insert([
    { title: 'Post 1', content: 'Content 1', user_id: userId },
    { title: 'Post 2', content: 'Content 2', user_id: userId }
  ]);

// 批量更新
const { data, error } = await supabase
  .from('posts')
  .update({ status: 'published' })
  .in('id', [1, 2, 3]);
```

## 缓存策略

### 1. 客户端缓存

```javascript
// 使用 localStorage 缓存数据
function cacheData(key, data, expirationMinutes = 60) {
  const item = {
    value: data,
    expiry: new Date().getTime() + expirationMinutes * 60 * 1000
  };
  localStorage.setItem(key, JSON.stringify(item));
}

// 从缓存获取数据
function getCachedData(key) {
  const itemStr = localStorage.getItem(key);
  if (!itemStr) return null;
  
  const item = JSON.parse(itemStr);
  if (new Date().getTime() > item.expiry) {
    localStorage.removeItem(key);
    return null;
  }
  
  return item.value;
}

// 缓存用户数据
async function getUserData() {
  const cachedData = getCachedData('userData');
  if (cachedData) {
    return cachedData;
  }
  
  const { data, error } = await supabase
    .from('users')
    .select('*')
    .eq('id', userId)
    .single();
  
  if (data) {
    cacheData('userData', data);
  }
  
  return data;
}
```

### 2. 使用 SWR 或 React Query

```javascript
// 使用 SWR
import useSWR from 'swr';

function useUserData() {
  const { data, error, mutate } = useSWR('userData', async () => {
    const { data } = await supabase
      .from('users')
      .select('*')
      .eq('id', userId)
      .single();
    return data;
  });
  
  return { data, error, mutate };
}

// 使用 React Query
import { useQuery } from 'react-query';

function usePosts() {
  return useQuery(['posts', userId], async () => {
    const { data } = await supabase
      .from('posts')
      .select('*')
      .eq('user_id', userId);
    return data;
  });
}
```

## 连接管理

### 1. 单一客户端实例

```javascript
// 创建单一实例
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseAnonKey);

export default supabase;

// 在其他文件中使用
import supabase from './supabaseClient';

async function fetchData() {
  const { data } = await supabase
    .from('table')
    .select('*');
  return data;
}
```

### 2. 优化连接池

在服务器端应用中，使用连接池来管理数据库连接：

```javascript
// Next.js API route
import supabase from '../../lib/supabase';

export default async function handler(req, res) {
  try {
    const { data, error } = await supabase
      .from('posts')
      .select('*');
    
    if (error) {
      throw error;
    }
    
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
```

## 实时订阅优化

### 1. 限制订阅数量

```javascript
// 不好的做法：多个单独的订阅
const postSubscription = supabase
  .from('posts')
  .on('INSERT', handlePostInsert)
  .subscribe();

const commentSubscription = supabase
  .from('comments')
  .on('INSERT', handleCommentInsert)
  .subscribe();

// 好的做法：合理管理订阅
class SubscriptionManager {
  constructor() {
    this.subscriptions = [];
  }
  
  subscribe(table, event, callback, filter = '') {
    const { data: subscription } = supabase
      .from(`${table}${filter}`)
      .on(event, callback)
      .subscribe();
    
    this.subscriptions.push(subscription);
    return subscription;
  }
  
  unsubscribeAll() {
    this.subscriptions.forEach(sub => sub.unsubscribe());
    this.subscriptions = [];
  }
}

const subscriptionManager = new SubscriptionManager();
```

### 2. 批量更新

```javascript
// 使用防抖减少实时更新频率
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

const debouncedUpdate = debounce((data) => {
  console.log('Updated data:', data);
  // 更新 UI
}, 300);

const { data: subscription } = supabase
  .from('posts')
  .on('UPDATE', payload => {
    debouncedUpdate(payload.new);
  })
  .subscribe();
```

## 存储优化

### 1. 文件压缩

```javascript
// 压缩图片后上传
async function compressAndUpload(file) {
  // 使用 canvas 压缩图片
  const compressedFile = await compressImage(file);
  
  const { data, error } = await supabase
    .storage
    .from('avatars')
    .upload(`public/${userId}/${file.name}`, compressedFile, {
      cacheControl: '3600',
      upsert: true
    });
  
  return data;
}
```

### 2. 合理使用存储桶

- **公开存储桶**：用于不需要认证的文件，如图像、CSS、JavaScript
- **私有存储桶**：用于需要认证的文件，如用户文档、敏感数据

## 服务器端优化

### 1. 使用 Edge Functions

```javascript
// supabase/functions/hello/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js';

const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;

const supabase = createClient(supabaseUrl, supabaseServiceKey);

serve(async (req) => {
  const { name } = await req.json();
  
  // 服务器端操作
  const { data, error } = await supabase
    .from('users')
    .insert({ name })
    .select()
    .single();
  
  if (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      headers: { 'Content-Type': 'application/json' },
      status: 400,
    });
  }
  
  return new Response(JSON.stringify({ data }), {
    headers: { 'Content-Type': 'application/json' },
  });
});
```

### 2. 数据库函数

```sql
-- 创建数据库函数
CREATE OR REPLACE FUNCTION get_user_posts(user_id UUID)
RETURNS SETOF posts AS $$
BEGIN
  RETURN QUERY SELECT * FROM posts WHERE posts.user_id = user_id ORDER BY created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- 调用函数
SELECT * FROM get_user_posts('123e4567-e89b-12d3-a456-426614174000');
```

## 总结

Supabase 性能优化的关键策略包括：

1. **查询优化**：只选择需要的列，使用过滤器，添加索引
2. **缓存策略**：使用客户端缓存，SWR 或 React Query
3. **连接管理**：使用单一客户端实例，优化连接池
4. **实时订阅**：限制订阅数量，批量更新
5. **存储优化**：文件压缩，合理使用存储桶
6. **服务器端优化**：使用 Edge Functions，数据库函数

通过实施这些优化策略，可以显著提高 Supabase 应用程序的性能和响应速度。""",
        category=KnowledgeCategory.FRAMEWORK,
        tags=["supabase", "performance", "optimization"],
        severity="low",
        cwe_ids=[],
        owasp_ids=[]
    )
]
