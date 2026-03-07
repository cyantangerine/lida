import request from '@/utils/request'

// 用户登录
export function login(username, password) {
  const params = new URLSearchParams()
  params.append('username', username)
  params.append('password', password)
  return request({
    url: '/token',
    method: 'post',
    data: params
  })
}

// 用户注册
export function register(username, password) {
  return request({
    url: '/register',
    method: 'post',
    data: { username, password }
  })
}

// 上传文件
export function uploadFile(file, data, chatId) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('data', JSON.stringify(data))
  formData.append('chat_id', chatId)
  return request({
    url: '/summarize',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 生成目标
export function generateGoals(summary, chatId, n = 5, extraHintInterest = '') {
  return request({
    url: '/goal',
    method: 'post',
    data: {
      summary,
      chat_id: chatId,
      n,
      extra_hint_interest: extraHintInterest
    }
  })
}

// 生成可视化
export function visualize(summary, goal, chatId, library = 'seaborn') {
  return request({
    url: '/visualize',
    method: 'post',
    data: {
      summary,
      goal,
      chat_id: chatId,
      library
    }
  })
}

// 编辑可视化
export function editVisualize(chatId, goalId, summary, code, instructions, library = 'seaborn') {
  return request({
    url: '/visualize/edit',
    method: 'post',
    data: {
      chat_id: chatId,
      goal_id: goalId,
      summary,
      code,
      instructions,
      library
    }
  })
}

// 获取聊天列表
export function getChatList(skip = 0, limit = 10) {
  return request({
    url: `/getChatList?skip=${skip}&limit=${limit}`,
    method: 'get'
  })
}

// 获取聊天详情
export function getChatInfo(chatId) {
  return request({
    url: `/getChatInfo/${chatId}`,
    method: 'get'
  })
}

// 获取目标详情
export function getGoalInfo(summary, goalId) {
  return request({
    url: '/getGoalInfo',
    method: 'post',
    data: {
      summary,
      goal_id: goalId
    }
  })
}

// 解释可视化
export function explainVisualization(chatId, goalId, code, library = 'seaborn') {
  return request({
    url: '/visualize/explain',
    method: 'post',
    data: {
      chat_id: chatId,
      goal_id: goalId,
      code,
      library
    }
  })
}

// 评估可视化
export function evaluateVisualization(chatId, code, goal, library = 'seaborn') {
  return request({
    url: '/visualize/evaluate',
    method: 'post',
    data: {
      chat_id: chatId,
      code,
      goal,
      library
    }
  })
}

// 推荐可视化
export function recommendVisualization(summary, code, library = 'seaborn') {
  return request({
    url: '/visualize/recommend',
    method: 'post',
    data: {
      summary,
      code,
      library
    }
  })
}

// 修复可视化
export function repairVisualization(feedback, code, goal, summary, library = 'seaborn') {
  return request({
    url: '/visualize/repair',
    method: 'post',
    data: {
      feedback,
      code,
      goal,
      summary,
      library
    }
  })
}
