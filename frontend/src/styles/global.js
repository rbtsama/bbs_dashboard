import { createGlobalStyle } from 'styled-components';
import customTheme from '../theme';

// 引入现代字体
const GlobalStyle = createGlobalStyle`
  /* 引入字体 */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
  
  /* 重置样式 */
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  /* 根元素样式 */
  :root {
    font-size: 16px;
  }

  /* 基础样式 */
  body {
    margin: 0;
    padding: 0;
    font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: #f5f5f5;
    color: #434343;
  }

  /* 标题样式 */
  h1, h2, h3, h4, h5, h6 {
    margin: 0;
    font-weight: 600;
    line-height: 1.25;
    color: #1F2224;
    font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    letter-spacing: -0.01em;
  }

  h1 { font-size: 36px; }
  h2 { font-size: 30px; }
  h3 { font-size: 24px; }
  h4 { font-size: 20px; }
  h5 { font-size: 18px; }
  h6 { font-size: 16px; }

  /* 链接样式 */
  a {
    color: #1677FF;
    text-decoration: none;
    transition: color 0.3s ease;

    &:hover {
      color: #4096FF;
    }
  }

  /* 段落样式 */
  p {
    margin-bottom: 16px;
    line-height: 1.75;
  }

  /* 数据展示用等宽字体 */
  .number-data, .stat-value, .code-like, .ant-statistic-content-value {
    font-family: 'JetBrains Mono', 'Menlo', monospace;
  }

  /* 使所有数字使用等宽字体 */
  .ant-table td.column-numeric, 
  .ant-statistic-content-value,
  .ant-descriptions-item-content.numeric-value,
  .numeric {
    font-family: 'JetBrains Mono', 'Menlo', monospace;
    font-feature-settings: "tnum";
    letter-spacing: -0.02em;
  }

  /* 代码字体 */
  code, pre {
    font-family: 'JetBrains Mono', Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
  }

  /* Ant Design 组件全局样式覆盖 */
  .ant-btn {
    font-weight: 500;
    font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  }

  .ant-input {
    font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  }

  .ant-table {
    font-size: 14px;
    font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  }

  .ant-card-head-title {
    font-weight: 600;
    font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  }

  .ant-modal-title {
    font-weight: 600;
    font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  }

  .ant-tabs-tab {
    font-weight: 500;
    font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  }

  /* 自定义滚动条样式 */
  ::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }

  ::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
  }

  ::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
  }

  /* 文本选择样式 */
  ::selection {
    background: #40A9FF;
    color: white;
  }

  /* 技术相关菜单和标签 */
  .tech-menu, .tech-tags {
    font-family: 'JetBrains Mono', 'Menlo', monospace;
    font-size: 0.95em;
  }

  /* 表头使用半衬线字体增强科技感 */
  .ant-table-thead > tr > th {
    font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    font-weight: 600;
  }

  /* 欢迎页面背景 */
  .welcome-bg {
    position: relative;
    overflow: hidden;
  }

  .welcome-bg::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(24, 144, 255, 0.05) 0%, rgba(114, 46, 209, 0.05) 50%, rgba(0, 0, 0, 0) 100%);
    z-index: -1;
    animation: rotate 60s linear infinite;
  }

  @keyframes rotate {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
`;

export default GlobalStyle; 