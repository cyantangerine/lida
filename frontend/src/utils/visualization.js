/**
 * 可视化工具函数
 */

/**
 * 将代码字符串转换为可执行的函数
 * @param {string} code - Python 或 JavaScript 代码
 * @returns {Function|null}
 */
export function parseCode(code) {
  if (!code) return null
  try {
    // 这里可以根据需要处理不同类型的代码
    // 如果是 Vega-Lite spec，直接返回 JSON
    if (code.trim().startsWith('{')) {
      return JSON.parse(code)
    }
    return code
  } catch (error) {
    console.error('解析代码失败:', error)
    return null
  }
}

/**
 * 渲染 Vega/Vega-Lite 图表
 * @param {HTMLElement} container - 容器元素
 * @param {Object} spec - Vega/Vega-Lite 规范
 * @param {Object} options - 配置选项
 */
export async function renderVegaChart(container, spec, options = {}) {
  const embed = await import('vega-embed')
  
  const defaultOptions = {
    mode: 'vega-lite',
    renderer: 'canvas',
    actions: {
      export: true,
      source: false,
      compiled: false,
      editor: false
    },
    ...options
  }
  
  try {
    const result = await embed.default(container, spec, defaultOptions)
    return result
  } catch (error) {
    console.error('渲染图表失败:', error)
    throw error
  }
}

/**
 * 显示 Base64 图片
 * @param {HTMLElement} container - 容器元素
 * @param {string} base64Data - Base64 编码的图片数据
 */
export function renderBase64Image(container, base64Data) {
  if (!container || !base64Data) return
  
  const img = document.createElement('img')
  img.src = `data:image/png;base64,${base64Data}`
  img.style.maxWidth = '100%'
  img.style.height = 'auto'
  
  container.innerHTML = ''
  container.appendChild(img)
}

/**
 * 格式化时间
 * @param {string|Date} date - 日期对象或字符串
 * @param {string} format - 格式模板
 * @returns {string}
 */
export function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return ''
  
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 生成随机颜色
 * @returns {string}
 */
export function getRandomColor() {
  const letters = '0123456789ABCDEF'
  let color = '#'
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)]
  }
  return color
}

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {number} wait - 等待时间 (毫秒)
 * @returns {Function}
 */
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * 节流函数
 * @param {Function} func - 要节流的函数
 * @param {number} limit - 时间限制 (毫秒)
 * @returns {Function}
 */
export function throttle(func, limit) {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}
