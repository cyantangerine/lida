# LIDA API 接口文档

## 基础信息

- **Base URL**: `/api`
- **认证方式**: OAuth2 Bearer Token
- **内容类型**: `application/json`
- **跨域支持**: 允许 localhost:8000, localhost:8001

---

## 🔐 认证接口

### 1. 用户登录

**POST** `/token`

获取访问令牌（Access Token）

#### 请求参数

**Content-Type**: `application/x-www-form-urlencoded`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

#### 响应示例

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 错误响应

```json
{
  "status": false,
  "message": "Incorrect username or password"
}
```

---

### 2. 用户注册

**POST** `/register`

注册新用户账号

#### 请求参数

**Content-Type**: `application/json`

```json
{
  "username": "string",
  "password": "string"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名（唯一） |
| password | string | 是 | 密码 |

#### 响应示例

成功：
```json
{
  "status": true,
  "message": "Successfully registered user!"
}
```

失败：
```json
{
  "status": false,
  "message": "Username already registered"
}
```

---

## 📊 数据管理接口

### 3. 上传文件并生成摘要

**POST** `/summarize`

上传 CSV、Excel 或 JSON 文件，自动生成数据摘要

#### 请求参数

**Content-Type**: `multipart/form-data`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | UploadFile | 是 | 上传的文件（CSV/Excel/JSON） |
| data | string | 是 | JSON 字符串，包含数据描述 |
| chat_id | string | 是 | 聊天 ID（"new" 表示新建） |

**data 参数格式**:
```json
{
  "description": "数据描述",
  "fields": {
    "field1": "字段 1 说明",
    "field2": "字段 2 说明"
  }
}
```

#### 响应示例

```json
{
  "status": true,
  "summary": {
    "name": "dataset_name",
    "file_name": "data.csv",
    "dataset_description": "数据集描述信息",
    "fields": [
      {"name": "age", "type": "int", "description": "年龄"}
    ],
    "field_names": ["age", "income", "score"]
  },
  "data_filename": "data.csv",
  "chat_id": "1234567890123456789",
  "warning": {
    "message": "某些字段描述不匹配",
    "data": ["unmatched_field"]
  }
}
```

#### 支持的文件类型

- CSV (`text/csv`)
- Excel (`application/vnd.ms-excel`, `.xls`, `.xlsx`)
- JSON (`application/json`)

---

### 4. 通过 URL 上传文件

**POST** `/summarize/url`

从远程 URL 下载文件并生成摘要

#### 请求参数

**Content-Type**: `application/json`

```json
{
  "url": "https://example.com/data.csv",
  "textgen_config": {
    "n": 1,
    "temperature": 0
  }
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 文件 URL 地址 |
| textgen_config | TextGenerationConfig | 否 | 文本生成配置 |

#### 响应示例

```json
{
  "status": true,
  "summary": {
    "name": "dataset_name",
    "file_name": "data.csv",
    "dataset_description": "...",
    "fields": [...],
    "field_names": [...]
  },
  "data_filename": "data.csv"
}
```

---

## 🎯 目标生成接口

### 5. 生成可视化目标

**POST** `/goal`

根据数据摘要生成可视化分析目标

#### 请求参数

**Content-Type**: `application/json`

```json
{
  "summary": {
    "name": "dataset",
    "file_name": "data.csv",
    "dataset_description": "描述",
    "field_names": ["field1", "field2"],
    "fields": [...]
  },
  "chat_id": "1234567890123456789",
  "n": 5,
  "extra_hint_interest": "额外提示",
  "textgen_config": {
    "n": 5,
    "temperature": 0.7
  }
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| summary | Summary | 是 | 数据摘要对象 |
| chat_id | string | 是 | 聊天 ID |
| n | int | 否 | 生成目标数量（默认 5） |
| extra_hint_interest | string | 否 | 额外的兴趣提示 |
| textgen_config | TextGenerationConfig | 否 | 文本生成配置 |

#### 响应示例

```json
{
  "status": true,
  "data": [
    {
      "index": 0,
      "question": "不同年龄段的收入分布如何？",
      "visualization": "bar chart",
      "rationale": "展示年龄与收入的关系"
    }
  ],
  "message": "Successfully generated 5 goals"
}
```

#### 错误处理

如果数据集列数过多导致上下文超限：
```json
{
  "status": false,
  "message": "The dataset you uploaded has too many columns. Please upload a dataset with fewer columns and try again."
}
```

---

## 📈 可视化接口

### 6. 生成可视化图表

**POST** `/visualize`

根据目标生成可视化图表

#### 请求参数

```json
{
  "summary": {},
  "goal": {
    "question": "问题描述",
    "visualization": "图表类型",
    "rationale": "理由",
    "index": 0
  },
  "chat_id": "1234567890123456789",
  "library": "seaborn",
  "textgen_config": {}
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| summary | Summary | 是 | 数据摘要 |
| goal | Goal | 是 | 可视化目标 |
| chat_id | string | 是 | 聊天 ID |
| library | string | 否 | 可视化库（默认 seaborn） |
| textgen_config | TextGenerationConfig | 否 | 文本生成配置 |

#### 响应示例

```json
{
  "status": true,
  "charts": [
    {
      "code": "import seaborn as sns\nsns.barplot(...)",
      "raster": "base64_encoded_image",
      "library": "seaborn"
    }
  ],
  "message": "Successfully generated charts.",
  "goal_id": "1234567890123456789"
}
```

---

### 7. 编辑可视化图表

**POST** `/visualize/edit`

根据编辑指令修改现有可视化代码

#### 请求参数

```json
{
  "chat_id": "1234567890123456789",
  "goal_id": "1234567890123456789",
  "summary": {},
  "code": "原始代码",
  "instructions": "将柱状图改为折线图",
  "library": "seaborn",
  "textgen_config": {}
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chat_id | string | 是 | 聊天 ID |
| goal_id | string | 是 | 目标 ID |
| summary | Summary | 是 | 数据摘要 |
| code | string | 是 | 原始可视化代码 |
| instructions | string \| string[] | 是 | 编辑指令（可以是字符串或数组） |
| library | string | 否 | 可视化库 |

#### 响应示例

```json
{
  "status": true,
  "charts": [
    {
      "code": "修改后的代码",
      "raster": "base64_encoded_image"
    }
  ],
  "message": "Successfully edited charts."
}
```

---

### 8. 修复可视化图表

**POST** `/visualize/repair`

根据反馈修复可视化代码问题

#### 请求参数

```json
{
  "feedback": "图表颜色不清晰",
  "code": "原始代码",
  "goal": {
    "question": "...",
    "visualization": "...",
    "rationale": "..."
  },
  "summary": {},
  "library": "seaborn",
  "textgen_config": {}
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| feedback | string \| string[] \| object[] | 是 | 反馈意见 |
| code | string | 是 | 原始代码 |
| goal | Goal | 是 | 可视化目标 |
| summary | Summary | 是 | 数据摘要 |
| library | string | 否 | 可视化库 |

#### 响应示例

```json
{
  "status": true,
  "charts": [
    {
      "code": "修复后的代码",
      "raster": "base64_encoded_image"
    }
  ],
  "message": "Successfully generated chart repairs"
}
```

---

### 9. 推荐可视化图表

**POST** `/visualize/recommend`

基于现有代码推荐改进的可视化方案

#### 请求参数

```json
{
  "summary": {},
  "code": "原始代码",
  "library": "seaborn",
  "textgen_config": {}
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| summary | Summary | 是 | 数据摘要 |
| code | string | 是 | 原始代码 |
| library | string | 否 | 可视化库 |
| textgen_config | TextGenerationConfig | 否 | 文本生成配置 |

#### 响应示例

```json
{
  "status": true,
  "charts": [
    {
      "code": "推荐的代码",
      "raster": "base64_encoded_image"
    }
  ],
  "message": "Successfully generated chart recommendation"
}
```

---

### 10. 生成可视化结论

**POST** `/visualize/conclusion`

基于可视化和提示生成分析结论

#### 请求参数

```json
{
  "summary": {},
  "goal": {
    "question": "...",
    "visualization": "...",
    "rationale": "..."
  },
  "code": "可视化代码",
  "hint": "额外提示",
  "library": "seaborn",
  "textgen_config": {}
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| summary | Summary | 是 | 数据摘要 |
| goal | Goal | 是 | 可视化目标 |
| code | string | 是 | 可视化代码 |
| hint | string | 否 | 额外提示 |
| library | string | 否 | 可视化库 |
| textgen_config | TextGenerationConfig | 否 | 文本生成配置 |

#### 响应示例

```json
{
  "status": true,
  "charts": [
    {
      "code": "结论代码",
      "raster": "base64_encoded_image"
    }
  ],
  "message": "Successfully generated chart conclusion"
}
```

---

## 🔍 解释与评估接口

### 11. 解释可视化代码

**POST** `/visualize/explain`

对可视化代码进行解释说明

#### 请求参数

```json
{
  "chat_id": "1234567890123456789",
  "goal_id": "1234567890123456789",
  "code": "可视化代码",
  "library": "seaborn",
  "textgen_config": {
    "n": 1,
    "temperature": 0
  }
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chat_id | string | 是 | 聊天 ID |
| goal_id | string | 是 | 目标 ID |
| code | string | 是 | 可视化代码 |
| library | string | 否 | 可视化库 |
| textgen_config | TextGenerationConfig | 否 | 文本生成配置 |

#### 响应示例

```json
{
  "status": true,
  "explanations": [
    {
      "explanation": "这段代码使用 seaborn 绘制柱状图...",
      "components": ["数据加载", "图表类型", "样式设置"]
    }
  ],
  "message": "Successfully generated explanations"
}
```

---

### 12. 评估可视化代码

**POST** `/visualize/evaluate`

对可视化代码进行评估打分

#### 请求参数

```json
{
  "chat_id": "1234567890123456789",
  "code": "可视化代码",
  "goal": {
    "question": "...",
    "visualization": "...",
    "rationale": "..."
  },
  "library": "seaborn",
  "textgen_config": {
    "n": 1,
    "temperature": 0
  }
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chat_id | string | 是 | 聊天 ID |
| code | string | 是 | 可视化代码 |
| goal | Goal | 是 | 可视化目标 |
| library | string | 否 | 可视化库 |
| textgen_config | TextGenerationConfig | 否 | 文本生成配置 |

#### 响应示例

```json
{
  "status": true,
  "evaluations": {
    "accuracy": 0.9,
    "clarity": 0.85,
    "aesthetics": 0.8,
    "comments": "图表清晰地展示了数据趋势"
  },
  "message": "Successfully generated evaluation"
}
```

---

## 💾 数据查询接口

### 13. 获取聊天列表

**GET** `/getChatList`

获取当前用户的聊天历史列表

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skip | int | 否 | 跳过数量（分页） |
| limit | int | 否 | 返回数量限制（默认 10） |

#### 响应示例

```json
{
  "status": true,
  "chats": [
    {
      "id": "1234567890123456789",
      "name": "数据分析聊天 1",
      "create_time": "2024-01-01T00:00:00",
      "update_time": "2024-01-02T00:00:00"
    }
  ],
  "message": "Successfully listed chats!"
}
```

---

### 14. 获取聊天详情

**GET** `/getChatInfo/{chat_id}`

获取指定聊天的详细信息

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chat_id | string | 是 | 聊天 ID（路径参数） |

#### 响应示例

```json
{
  "status": true,
  "summary": {
    "name": "数据集名称",
    "file_name": "data.csv",
    "dataset_description": "描述",
    "fields": [...],
    "field_names": [...]
  },
  "data": [
    {
      "index": 0,
      "question": "问题描述",
      "visualization": "bar chart",
      "rationale": "理由",
      "is_auto": 1,
      "id": "1234567890123456789"
    }
  ],
  "message": "Successfully get chatInfo!"
}
```

---

### 15. 获取目标详情

**POST** `/getGoalInfo`

获取指定目标的详细信息及可视化结果

#### 请求参数

```json
{
  "summary": {},
  "goal_id": "1234567890123456789"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| summary | Summary | 是 | 数据摘要 |
| goal_id | string | 是 | 目标 ID |

#### 响应示例

```json
{
  "status": true,
  "charts": [
    {
      "code": "可视化代码",
      "raster": "base64_encoded_image",
      "library": "seaborn"
    }
  ],
  "instructions": [
    {
      "index": 0,
      "edit": "编辑指令"
    }
  ],
  "explanations": [...],
  "evaluations": [...],
  "message": "Successfully get chatInfo!"
}
```

---

## 🧠 文本生成接口

### 16. 文本生成

**POST** `/text/generate`

使用配置的文本生成器生成文本

#### 请求参数

```json
{
  "prompt": "生成提示",
  "n": 1,
  "temperature": 0.7,
  "max_tokens": 100
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 生成提示 |
| n | int | 否 | 生成数量 |
| temperature | float | 否 | 温度参数 |
| max_tokens | int | 否 | 最大 token 数 |

#### 响应示例

```json
{
  "status": true,
  "completions": ["生成的文本内容"]
}
```

---

## 📷 信息图表接口

### 17. 生成信息图表

**POST** `/infographer`

使用 Peacasso 包生成信息图表

#### 请求参数

```json
{
  "visualization": "可视化描述",
  "n": 1,
  "style_prompt": "风格提示词"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| visualization | string | 是 | 可视化描述 |
| n | int | 否 | 生成数量（默认 1） |
| style_prompt | string \| string[] | 否 | 风格提示词 |

#### 响应示例

```json
{
  "status": true,
  "result": ["信息图表结果"],
  "message": "Successfully generated infographics"
}
```

---

## 🔧 系统接口

### 18. 获取支持的模型列表

**GET** `/models`

获取所有支持的文本生成模型

#### 响应示例

```json
{
  "status": true,
  "data": {
    "openai": ["gpt-3.5-turbo", "gpt-4"],
    "ollama": ["llama2", "mistral"]
  },
  "message": "Successfully listed models"
}
```

---

## 📝 数据模型定义

### Summary (数据摘要)

```typescript
{
  name: string,              // 数据集名称
  file_name: string,         // 文件名
  dataset_description: string, // 数据集描述
  field_names: string[],     // 字段名列表
  fields?: any[]             // 字段详细信息
}
```

### Goal (可视化目标)

```typescript
{
  question: string,          // 分析问题
  visualization: string,     // 推荐的可视化类型
  rationale: string,         // 推荐理由
  index?: number             // 索引编号
}
```

### TextGenerationConfig (文本生成配置)

```typescript
{
  n?: number,                // 生成数量
  temperature?: number,      // 温度参数 (0-1)
  max_tokens?: number,       // 最大 token 数
  top_p?: number,            // Top-p 采样
  frequency_penalty?: number,
  presence_penalty?: number
}
```

### Chart (图表响应)

```typescript
{
  spec?: string | object,    // Vega-Lite 规范
  status: boolean,           // 执行状态
  raster?: string,           // Base64 编码的图片
  code: string,              // 生成的代码
  library: string,           // 使用的库
  error?: object             // 错误信息
}
```

---

## 🔒 认证使用说明

### 获取 Token

```bash
curl -X POST http://localhost:8000/api/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_username&password=your_password"
```

### 使用 Token 访问受保护接口

```bash
curl -X GET http://localhost:8000/api/getChatList \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## ⚠️ 错误处理

所有接口统一返回格式：

### 成功响应

```json
{
  "status": true,
  "data": {...},
  "message": "操作成功"
}
```

### 失败响应

```json
{
  "status": false,
  "message": "错误描述信息"
}
```

### 常见错误码

- **401 Unauthorized**: 未授权访问（缺少或无效的 Token）
- **404 Not Found**: 资源不存在（如 Chat 或 Goal 未找到）
- **500 Internal Server Error**: 服务器内部错误

---

## 📋 使用示例

### 完整工作流程示例

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 1. 注册登录
requests.post(f"{BASE_URL}/register", json={
    "username": "user1",
    "password": "password123"
})

# 2. 获取 Token
token_resp = requests.post(f"{BASE_URL}/token", data={
    "username": "user1",
    "password": "password123"
})
access_token = token_resp.json()["access_token"]

headers = {"Authorization": f"Bearer {access_token}"}

# 3. 上传文件
with open("data.csv", "rb") as f:
    files = {"file": f}
    data = {
        "data": '{"description": "销售数据", "fields": {}}',
        "chat_id": "new"
    }
    resp = requests.post(f"{BASE_URL}/summarize", 
                        files=files, 
                        data=data, 
                        headers=headers)
    chat_id = resp.json()["chat_id"]
    summary = resp.json()["summary"]

# 4. 生成目标
goals_resp = requests.post(f"{BASE_URL}/goal", json={
    "summary": summary,
    "chat_id": chat_id,
    "n": 5
}, headers=headers)
goals = goals_resp.json()["data"]

# 5. 生成可视化
viz_resp = requests.post(f"{BASE_URL}/visualize", json={
    "summary": summary,
    "goal": goals[0],
    "chat_id": chat_id,
    "library": "seaborn"
}, headers=headers)
chart = viz_resp.json()["charts"][0]

print(f"生成的图表代码：{chart['code']}")
```

---

## 📞 技术支持

如需帮助或反馈问题，请访问项目仓库或联系开发团队。
