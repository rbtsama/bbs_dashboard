/**
 * 格式化数字为字符串，添加千位分隔符
 * @param {number} value - 要格式化的数字
 * @returns {string} 格式化后的字符串
 */
export const formatNumber = (value) => {
  if (value === null || value === undefined) return '0';
  
  // 如果已经是格式化的字符串，直接返回
  if (typeof value === 'string' && value.includes(',')) {
    return value;
  }
  
  // 转换为数字
  const num = parseFloat(String(value).replace(/[^\d.-]/g, ''));
  if (isNaN(num)) return '0';
  
  // 格式化数字，添加千位分隔符
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

/**
 * 格式化货币数字，保留最多两位小数
 * @param {number} value - 要格式化的数字
 * @returns {string} 格式化后的字符串
 */
export const formatCurrency = (value) => {
  if (value === null || value === undefined) return '0';
  
  // 如果已经是格式化的字符串，提取数字部分
  if (typeof value === 'string') {
    value = parseFloat(value.replace(/[^\d.-]/g, ''));
  }
  
  if (isNaN(value)) return '0';
  
  // 处理不同数量级的显示方式
  if (value >= 1000000) {
    return (value / 1000000).toFixed(2) + 'M';
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K';
  }
  
  // 一般情况，保留必要的小数位
  const decimalPlaces = value % 1 === 0 ? 0 : 2;
  return value.toFixed(decimalPlaces);
};

/**
 * 格式化日期为易读的字符串
 * @param {string|Date} date - 日期字符串或Date对象
 * @returns {string} 格式化后的日期字符串
 */
export const formatDate = (date) => {
  if (!date) return '';
  
  const d = new Date(date);
  if (isNaN(d.getTime())) return '';
  
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

/**
 * 根据天数计算相对时间描述
 * @param {number} days - 天数
 * @returns {string} 相对时间描述
 */
export const formatTimeAgo = (days) => {
  if (days === null || days === undefined) return '未知';
  
  if (days === 0) return '今天';
  if (days === 1) return '昨天';
  if (days < 7) return `${days}天前`;
  if (days < 30) return `${Math.floor(days / 7)}周前`;
  if (days < 365) return `${Math.floor(days / 30)}个月前`;
  
  return `${Math.floor(days / 365)}年前`;
}; 