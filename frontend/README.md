# LIDA Vue 2 前端项目

基于 Vue 2 + Element UI 的 LIDA 数据可视化平台前端。

## 技术栈

- **Vue 2.6** - 渐进式 JavaScript 框架
- **Vue Router 3.5** - 官方路由管理器
- **Vuex 3.6** - 状态管理库
- **Element UI 2.15** - 基于 Vue 2.0 的桌面端组件库
- **Axios** - HTTP 客户端
- **Vega/Vega-Lite** - 可视化语法库

## 功能特性

### 已实现的核心功能

1. **用户认证**
   - ✅ 用户登录
   - ✅ 用户注册
   - ✅ Token 认证机制
   - ✅ 路由守卫

2. **数据管理**
   - ✅ 文件上传 (CSV/Excel/JSON)
   - ✅ 数据摘要生成
   - ✅ 聊天历史管理

3. **可视化功能**
   - ✅ 自动生成可视化目标
   - ✅ 图表生成 (支持多种库)
   - ✅ 图表编辑 (自然语言指令)
   - ✅ 图表解释
   - ✅ Vega-Embed 集成

4. **界面组件**
   - ✅ 响应式布局
   - ✅ 侧边栏导航
   - ✅ 卡片式界面
   - ✅ 交互式表格

## 项目结构

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── api/              # API 接口
│   │   └── index.js
│   ├── assets/           # 静态资源
│   │   └── styles/
│   │       └── global.scss
│   ├── components/       # 公共组件
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── store/            # Vuex 状态管理
│   │   └── index.js
│   ├── utils/            # 工具函数
│   │   └── request.js
│   ├── views/            # 页面视图
│   │   ├── Login.vue
│   │   ├── Register.vue
│   │   ├── Home.vue
│   │   ├── ChatDetail.vue
│   │   └── Demo.vue
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── package.json         # 依赖配置
├── vue.config.js        # Vue CLI 配置
└── README.md           # 项目说明
```

## 安装与运行

### 环境要求

- Node.js >= 14.0.0
- npm >= 6.0.0
- 后端服务运行在 http://localhost:8000

### 安装步骤

1. **进入项目目录**
```bash
cd frontend
```

2. **安装依赖**
```bash
npm install
```

3. **启动开发服务器**
```bash
npm run serve
```

应用将在 http://localhost:8080 启动

4. **构建生产版本**
```bash
npm run build
```

## API 代理配置

开发环境下，所有 `/api` 请求将代理到后端服务:

```javascript
// vue.config.js
devServer: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

## 主要页面路由

| 路径 | 名称 | 描述 |
|------|------|------|
| `/login` | Login | 用户登录 |
| `/register` | Register | 用户注册 |
| `/` | Home | 主页 (需要认证) |
| `/chat/:id` | ChatDetail | 聊天详情 (需要认证) |
| `/demo` | Demo | 在线演示 |

## 核心 API 调用

### 用户认证
```javascript
import { login, register } from '@/api'

// 登录
await login(username, password)

// 注册
await register(username, password)
```

### 数据上传
```javascript
import { uploadFile } from '@/api'

const formData = {
  description: '数据描述',
  fields: {}
}

await uploadFile(file, formData, chatId)
```

### 可视化生成
```javascript
import { visualize, generateGoals } from '@/api'

// 生成目标
await generateGoals(summary, chatId, n=5)

// 生成可视化
await visualize(summary, goal, chatId, library='seaborn')
```

## 样式规范

使用 SCSS 预处理器，全局样式定义在 `src/assets/styles/global.scss`

主题色:
- 主色：#67c23a (绿色)
- 文字：#333, #666, #999
- 背景：#f5f7fa

## 开发注意事项

1. **跨域问题**: 开发时通过代理解决，生产环境需配置 CORS
2. **Token 存储**: 使用 localStorage 存储访问令牌
3. **错误处理**: 统一在 axios 拦截器中处理
4. **响应式设计**: 使用 Element UI 的栅格系统

## 后续优化方向

- [ ] 添加更多图表类型支持
- [ ] 完善错误处理和用户反馈
- [ ] 增加数据预览功能
- [ ] 优化移动端适配
- [ ] 添加国际化支持
- [ ] 性能优化 (懒加载、代码分割)

## 浏览器支持

- Chrome >= 80
- Firefox >= 75
- Safari >= 13
- Edge >= 80

## 许可证

MIT License

## 联系方式

如有问题或建议，请查看项目文档或联系开发团队。
