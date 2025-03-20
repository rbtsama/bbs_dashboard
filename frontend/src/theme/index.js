import { theme } from 'antd';

// 调色板
export const palette = {
  primary: {
    light: '#3498DB',
    main: '#2980B9',
    dark: '#1F618D',
    gradient: 'linear-gradient(120deg, #2980B9 0%, #1F618D 100%)',
  },
  secondary: {
    light: '#2ECC71',
    main: '#27AE60',
    dark: '#1E8449',
    gradient: 'linear-gradient(120deg, #27AE60 0%, #1E8449 100%)',
  },
  tertiary: {
    light: '#F1948A',
    main: '#E74C3C',
    dark: '#B03A2E',
    gradient: 'linear-gradient(120deg, #E74C3C 0%, #B03A2E 100%)',
  },
  quaternary: {
    light: '#F5B041',
    main: '#E67E22',
    dark: '#B9770E',
    gradient: 'linear-gradient(120deg, #E67E22 0%, #B9770E 100%)',
  },
  dark: {
    light: '#34495E',
    main: '#2C3E50',
    dark: '#1C2833',
    gradient: 'linear-gradient(120deg, #2C3E50 0%, #1C2833 100%)',
  },
  success: {
    light: '#73D13D',
    main: '#52C41A',
    dark: '#389E0D',
    gradient: 'linear-gradient(120deg, #52C41A 0%, #389E0D 100%)',
  },
  warning: {
    light: '#FFA940',
    main: '#FA8C16',
    dark: '#D46B08',
    gradient: 'linear-gradient(120deg, #FA8C16 0%, #D46B08 100%)',
  },
  error: {
    light: '#FF7875',
    main: '#F5222D',
    dark: '#CF1322',
    gradient: 'linear-gradient(120deg, #F5222D 0%, #CF1322 100%)',
  },
  neutral: {
    0: '#FFFFFF',
    50: '#F8F9FA',
    100: '#F0F2F5',
    200: '#E6E8EB',
    300: '#D0D3D6',
    400: '#A3A6A9',
    500: '#808487',
    600: '#636669',
    700: '#484B4E',
    800: '#2E3133',
    900: '#1F2224',
  },
};

// 字体系统
export const typography = {
  fontFamily: {
    base: "'PingFang SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
    code: "'JetBrains Mono', Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace",
    number: "'DIN Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
  },
  fontSize: {
    xs: '12px',
    sm: '14px',
    base: '16px',
    lg: '18px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '30px',
    '4xl': '36px',
    '5xl': '48px',
  },
  fontWeight: {
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: 1.25,
    base: 1.5,
    relaxed: 1.75,
  },
};

// 阴影系统
export const shadows = {
  xs: '0 2px 8px rgba(0, 0, 0, 0.05)',
  sm: '0 4px 12px rgba(0, 0, 0, 0.08)',
  md: '0 8px 16px rgba(0, 0, 0, 0.12)',
  lg: '0 12px 24px rgba(0, 0, 0, 0.15)',
  xl: '0 20px 32px rgba(0, 0, 0, 0.18)',
};

// 圆角系统
export const borderRadius = {
  none: '0',
  xs: '2px',
  sm: '4px',
  md: '6px',
  lg: '8px',
  xl: '12px',
  '2xl': '16px',
  '3xl': '24px',
  full: '9999px',
};

// 间距系统
export const spacing = {
  0: '0',
  1: '4px',
  2: '8px',
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  8: '32px',
  10: '40px',
  12: '48px',
  16: '64px',
  20: '80px',
  24: '96px',
};

// 动画系统
export const animation = {
  duration: {
    fast: '0.2s',
    base: '0.3s',
    slow: '0.4s',
    slower: '0.6s',
  },
  easing: {
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
  },
};

// 自定义主题配置
const customTheme = {
  token: {
    colorPrimary: palette.primary.main,
    colorSuccess: palette.success.main,
    colorWarning: palette.warning.main,
    colorError: palette.error.main,
    colorTextBase: palette.neutral[800],
    colorBgBase: palette.neutral[0],
    fontFamily: typography.fontFamily.base,
    fontSize: parseInt(typography.fontSize.base),
    borderRadius: parseInt(borderRadius.md),
    wireframe: false,
  },
  components: {
    Button: {
      borderRadius: borderRadius.md,
      controlHeight: 40,
      controlHeightLG: 48,
      controlHeightSM: 32,
      paddingContentHorizontal: spacing[4],
    },
    Card: {
      borderRadius: borderRadius.lg,
      boxShadow: shadows.sm,
    },
    Table: {
      borderRadius: borderRadius.lg,
      headerBg: palette.neutral[50],
      headerColor: palette.neutral[800],
      rowHoverBg: palette.neutral[50],
    },
    Input: {
      borderRadius: borderRadius.md,
      controlHeight: 40,
      controlHeightLG: 48,
      controlHeightSM: 32,
    },
    Select: {
      borderRadius: borderRadius.md,
      controlHeight: 40,
      controlHeightLG: 48,
      controlHeightSM: 32,
    },
    Modal: {
      borderRadius: borderRadius.xl,
      headerBg: 'transparent',
      contentBg: palette.neutral[0],
    },
    Tabs: {
      inkBarColor: palette.primary.main,
      cardGutter: 0,
    },
  },
};

export default customTheme; 