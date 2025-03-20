// 定义标准化颜色变量
const colors = {
  // 主要颜色
  primary: '#1677ff',           // 主色 - 蓝色
  primaryLight: '#4096ff',      // 主色亮色
  primaryDark: '#0958d9',       // 主色暗色
  secondary: '#722ed1',         // 次色 - 紫色
  
  // 功能色
  success: '#52c41a',           // 成功色
  warning: '#faad14',           // 警告色
  error: '#f5222d',             // 错误色
  info: '#1677ff',              // 信息色
  
  // 中性色
  neutral05: '#ffffff',         // 纯白
  neutral10: '#fafafa',         // 背景色
  neutral20: '#f5f5f5',         // 浅灰背景
  neutral30: '#f0f0f0',         // 分割线色
  neutral40: '#d9d9d9',         // 边框色
  neutral50: '#bfbfbf',         // 禁用色
  neutral60: '#8c8c8c',         // 次要文字
  neutral70: '#595959',         // 次要文字
  neutral80: '#434343',         // 主要文字
  neutral90: '#262626',         // 重要文字
  neutral100: '#000000',        // 纯黑
};

// 自定义主题配置
const theme = {
  token: {
    colorPrimary: colors.primary,
    colorSuccess: colors.success,
    colorWarning: colors.warning,
    colorError: colors.error,
    colorInfo: colors.info,
    
    colorTextBase: colors.neutral80,
    colorTextSecondary: colors.neutral70,
    colorTextTertiary: colors.neutral60,
    colorTextDisabled: colors.neutral50,
    
    colorBgContainer: colors.neutral05,
    colorBgElevated: colors.neutral05,
    colorBgLayout: colors.neutral20,
    
    borderRadius: 4,
    wireframe: false,
    
    colorBorder: colors.neutral40,
    colorSplit: colors.neutral30,
    
    boxShadow: '0 1px 4px rgba(0, 0, 0, 0.1)',
    boxShadowSecondary: '0 2px 8px rgba(0, 0, 0, 0.1)',
    
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    fontSize: 14,
  },
  components: {
    Menu: {
      itemBg: 'transparent',
      itemColor: colors.neutral05,
      itemHoverColor: colors.primaryLight,
      itemSelectedColor: colors.primaryLight,
      itemSelectedBg: 'rgba(255, 255, 255, 0.1)',
      fontSize: 15,
      itemHeight: 48,
      itemMarginInline: 8,
    },
    Layout: {
      headerBg: '#001529',
      headerHeight: 64,
      headerPadding: '0 30px',
      bodyBg: '#f5f5f5',
    },
    Table: {
      colorBgContainer: colors.neutral05,
      headerBg: colors.neutral10,
      headerColor: colors.neutral80,
      headerSplitColor: colors.neutral30,
      rowHoverBg: colors.neutral20,
      borderColor: colors.neutral30,
      fontSize: 14,
      headerBorderRadius: 4,
      cellPaddingBlock: 12,
      cellPaddingInline: 16,
    },
    Card: {
      colorBgContainer: colors.neutral05,
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)',
      borderRadius: 6,
      headerHeight: 54,
      headerFontSize: 16,
      headerFontSizeSM: 14,
      paddingLG: 24,
      paddingMD: 20,
      paddingSM: 16,
    },
    Button: {
      colorPrimary: colors.primary,
      colorPrimaryHover: colors.primaryLight,
      colorPrimaryActive: colors.primaryDark,
      borderRadius: 4,
      fontSize: 14,
      paddingContentHorizontal: 15,
      controlHeight: 32,
    },
    Pagination: {
      itemSize: 32,
      borderRadius: 4,
      colorPrimary: colors.primary,
      colorPrimaryHover: colors.primaryLight,
      colorBgContainer: '#fff',
      colorBgContainerDisabled: '#f5f5f5',
      colorPrimaryBg: '#e6f4ff',
      colorText: 'rgba(0, 0, 0, 0.88)',
      colorTextDisabled: 'rgba(0, 0, 0, 0.25)',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      fontSize: 14,
      lineHeight: 1.5714285714285714,
      itemActiveBg: '#e6f4ff',
      itemLinkBg: 'transparent',
      itemActiveBgDisabled: '#f5f5f5',
      itemActiveColorDisabled: 'rgba(0, 0, 0, 0.25)',
      itemInputBg: '#ffffff',
    },
    Input: {
      borderRadius: 4,
      controlHeight: 32,
    },
    Select: {
      borderRadius: 4,
      controlHeight: 32,
    },
    Divider: {
      marginLG: 24,
      colorSplit: colors.neutral30,
    },
    Tag: {
      borderRadius: 2,
      fontSize: 12,
    },
  },
};

export default theme;
export { colors }; 