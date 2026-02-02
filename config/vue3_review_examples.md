# Vue3代码审查示例和最佳实践

## 概述

本文档提供了Vue3代码审查的具体示例和最佳实践，帮助开发者理解如何编写高质量的Vue3代码。

## 1. Composition API使用审查

### 1.1 响应式数据使用

#### ❌ 问题示例
```vue
<template>
  <div>
    <p>{{ user.name }}</p>
    <button @click="updateUser">更新用户</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      user: {
        name: 'John',
        age: 30
      }
    }
  },
  methods: {
    updateUser() {
      this.user.name = 'Jane' // 直接修改对象属性
    }
  }
}
</script>
```

#### ✅ 优化建议
```vue
<template>
  <div>
    <p>{{ user.name }}</p>
    <button @click="updateUser">更新用户</button>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

// 使用reactive()创建响应式对象
const user = reactive({
  name: 'John',
  age: 30
})

const updateUser = () => {
  user.name = 'Jane' // 响应式更新
}
</script>
```

**修改说明**：
- 使用Composition API的`<script setup>`语法
- 使用`reactive()`创建响应式对象
- 避免使用Options API的`data()`和`methods`

### 1.2 计算属性优化

#### ❌ 问题示例
```vue
<template>
  <div>
    <p>全名: {{ firstName + ' ' + lastName }}</p>
    <p>年龄状态: {{ age > 18 ? '成年' : '未成年' }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const firstName = ref('John')
const lastName = ref('Doe')
const age = ref(25)
</script>
```

#### ✅ 优化建议
```vue
<template>
  <div>
    <p>全名: {{ fullName }}</p>
    <p>年龄状态: {{ ageStatus }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const firstName = ref('John')
const lastName = ref('Doe')
const age = ref(25)

// 使用computed()缓存计算结果
const fullName = computed(() => `${firstName.value} ${lastName.value}`)
const ageStatus = computed(() => age.value > 18 ? '成年' : '未成年')
</script>
```

**修改说明**：
- 使用`computed()`缓存计算结果，避免每次渲染都重新计算
- 提高性能和代码可读性

## 2. 组件设计审查

### 2.1 Props定义

#### ❌ 问题示例
```vue
<template>
  <div>
    <h1>{{ title }}</h1>
    <p>{{ content }}</p>
  </div>
</template>

<script setup>
// 没有定义props类型和默认值
const props = defineProps(['title', 'content'])
</script>
```

#### ✅ 优化建议
```vue
<template>
  <div>
    <h1>{{ title }}</h1>
    <p>{{ content }}</p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  content?: string
  count?: number
}

// 使用TypeScript定义props类型和默认值
const props = withDefaults(defineProps<Props>(), {
  content: '默认内容',
  count: 0
})
</script>
```

**修改说明**：
- 使用TypeScript定义props接口
- 使用`withDefaults()`设置默认值
- 提高类型安全性和代码可维护性

### 2.2 Emits定义

#### ❌ 问题示例
```vue
<template>
  <button @click="handleClick">点击</button>
</template>

<script setup>
// 没有定义emits事件
const emit = defineEmits(['click'])

const handleClick = () => {
  emit('click', { timestamp: Date.now() })
}
</script>
```

#### ✅ 优化建议
```vue
<template>
  <button @click="handleClick">点击</button>
</template>

<script setup lang="ts">
interface ClickEvent {
  timestamp: number
  buttonText: string
}

// 使用TypeScript定义emits事件类型
const emit = defineEmits<{
  click: [event: ClickEvent]
  submit: [data: any]
}>()

const handleClick = () => {
  emit('click', {
    timestamp: Date.now(),
    buttonText: '点击'
  })
}
</script>
```

**修改说明**：
- 使用TypeScript定义emits事件类型
- 提供更好的类型检查和IDE支持

## 3. 性能优化审查

### 3.1 响应式优化

#### ❌ 问题示例
```vue
<template>
  <div>
    <p>{{ expensiveCalculation() }}</p>
    <button @click="updateData">更新数据</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const data = ref(0)

// 每次渲染都会重新计算
const expensiveCalculation = () => {
  return data.value * 2 + Math.random()
}

const updateData = () => {
  data.value++
}
</script>
```

#### ✅ 优化建议
```vue
<template>
  <div>
    <p>{{ expensiveResult }}</p>
    <button @click="updateData">更新数据</button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const data = ref(0)

// 使用computed()缓存计算结果
const expensiveResult = computed(() => {
  return data.value * 2 + Math.random()
})

const updateData = () => {
  data.value++
}
</script>
```

**修改说明**：
- 使用`computed()`缓存计算结果
- 避免每次渲染都重新计算

### 3.2 异步组件优化

#### ❌ 问题示例
```vue
<template>
  <div>
    <HeavyComponent />
  </div>
</template>

<script setup>
import HeavyComponent from './HeavyComponent.vue'
</script>
```

#### ✅ 优化建议
```vue
<template>
  <div>
    <Suspense>
      <template #default>
        <HeavyComponent />
      </template>
      <template #fallback>
        <div>加载中...</div>
      </template>
    </Suspense>
  </div>
</template>

<script setup>
import { defineAsyncComponent } from 'vue'

// 使用异步组件进行代码分割
const HeavyComponent = defineAsyncComponent(() => import('./HeavyComponent.vue'))
</script>
```

**修改说明**：
- 使用`defineAsyncComponent()`进行代码分割
- 使用`<Suspense>`处理异步组件加载状态
- 减少初始包大小

## 4. 错误处理审查

### 4.1 错误边界

#### ❌ 问题示例
```vue
<template>
  <div>
    <ChildComponent />
  </div>
</template>

<script setup>
import ChildComponent from './ChildComponent.vue'
</script>
```

#### ✅ 优化建议
```vue
<template>
  <div>
    <ErrorBoundary>
      <template #default>
        <ChildComponent />
      </template>
      <template #error="{ error }">
        <div class="error">
          <h3>出错了！</h3>
          <p>{{ error.message }}</p>
        </div>
      </template>
    </ErrorBoundary>
  </div>
</template>

<script setup>
import { onErrorCaptured } from 'vue'
import ChildComponent from './ChildComponent.vue'

// 捕获子组件错误
onErrorCaptured((error, instance, info) => {
  console.error('组件错误:', error)
  console.error('错误信息:', info)
  return false // 阻止错误继续传播
})
</script>
```

**修改说明**：
- 使用`onErrorCaptured()`捕获子组件错误
- 提供友好的错误提示界面
- 记录错误日志用于调试

## 5. 状态管理审查

### 5.1 Pinia使用

#### ❌ 问题示例
```vue
<template>
  <div>
    <p>用户: {{ user.name }}</p>
    <button @click="updateUser">更新用户</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 直接在组件中管理状态
const user = ref({ name: 'John' })

const updateUser = () => {
  user.value.name = 'Jane'
}
</script>
```

#### ✅ 优化建议
```vue
<template>
  <div>
    <p>用户: {{ userStore.user.name }}</p>
    <button @click="userStore.updateUser">更新用户</button>
  </div>
</template>

<script setup>
import { useUserStore } from '@/stores/user'

// 使用Pinia进行状态管理
const userStore = useUserStore()
</script>
```

**store/user.ts**:
```typescript
import { defineStore } from 'pinia'

interface User {
  name: string
  email: string
}

export const useUserStore = defineStore('user', {
  state: () => ({
    user: {
      name: 'John',
      email: 'john@example.com'
    } as User
  }),
  
  actions: {
    updateUser(newName: string) {
      this.user.name = newName
    }
  },
  
  getters: {
    userName: (state) => state.user.name
  }
})
```

**修改说明**：
- 使用Pinia进行集中状态管理
- 将业务逻辑从组件中分离
- 提供更好的状态共享和持久化

## 6. 测试和文档审查

### 6.1 单元测试

#### ❌ 问题示例
```vue
<template>
  <div>
    <h1>{{ title }}</h1>
    <button @click="increment">{{ count }}</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const title = ref('计数器')
const count = ref(0)

const increment = () => {
  count.value++
}
</script>
```

#### ✅ 优化建议
```vue
<template>
  <div>
    <h1>{{ title }}</h1>
    <button @click="increment" data-testid="increment-btn">{{ count }}</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const title = ref('计数器')
const count = ref(0)

const increment = () => {
  count.value++
}

// 暴露方法用于测试
defineExpose({
  increment,
  count
})
</script>
```

**Counter.test.ts**:
```typescript
import { mount } from '@vue/test-utils'
import Counter from './Counter.vue'

describe('Counter', () => {
  it('should increment count when button is clicked', async () => {
    const wrapper = mount(Counter)
    
    expect(wrapper.text()).toContain('0')
    
    await wrapper.find('[data-testid="increment-btn"]').trigger('click')
    
    expect(wrapper.text()).toContain('1')
  })
  
  it('should expose increment method', () => {
    const wrapper = mount(Counter)
    
    expect(wrapper.vm.increment).toBeDefined()
    expect(wrapper.vm.count).toBe(0)
  })
})
```

**修改说明**：
- 添加`data-testid`属性便于测试
- 使用`defineExpose()`暴露组件方法
- 编写完整的单元测试

## 7. 样式和UI审查

### 7.1 CSS作用域

#### ❌ 问题示例
```vue
<template>
  <div class="container">
    <h1>标题</h1>
  </div>
</template>

<style>
/* 全局样式，可能影响其他组件 */
.container {
  background: red;
}
</style>
```

#### ✅ 优化建议
```vue
<template>
  <div class="container">
    <h1>标题</h1>
  </div>
</template>

<style scoped>
/* 使用scoped样式，避免样式污染 */
.container {
  background: red;
}
</style>
```

**修改说明**：
- 使用`scoped`样式避免样式污染
- 确保组件样式的独立性

## 总结

Vue3代码审查应该重点关注：

1. **Composition API的正确使用**
2. **TypeScript类型安全**
3. **性能优化**
4. **错误处理**
5. **状态管理**
6. **测试覆盖**
7. **代码规范**

通过遵循这些最佳实践，可以编写出高质量、可维护的Vue3代码。 