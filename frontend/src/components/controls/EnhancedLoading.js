import React from 'react';
import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import styled, { keyframes } from 'styled-components';

// 旋转动画
const rotateAnimation = keyframes`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`;

// 基本样式类
const Styles = {
  container: {
    position: 'relative',
    width: '100%'
  },
  loadingWrapper: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'rgba(255, 255, 255, 0.85)',
    backdropFilter: 'blur(2px)',
    transition: 'all 0.3s',
    zIndex: 10
  },
  loadingText: {
    marginTop: 16,
    color: '#1890ff',
    fontSize: 14,
    textShadow: '0 0 8px rgba(24, 144, 255, 0.2)',
    opacity: 0.85,
    transition: 'all 0.3s'
  },
  content: {
    position: 'relative',
    transition: 'all 0.3s'
  }
};

// 仅为图标样式创建 styled 组件
const RotatingIcon = styled(LoadingOutlined)`
  font-size: ${props => props.size === 'large' ? '40px' : '24px'};
  color: #1890ff;
  animation: ${rotateAnimation} 1s linear infinite;
`;

// 自定义图标组件
const CustomLoadingIcon = ({ size }) => {
  return <RotatingIcon size={size} />;
};

// 样式化的容器
const SimpleLoadingWrapper = ({ visible, children }) => {
  return (
    <div 
      style={{
        ...Styles.loadingWrapper,
        opacity: visible ? 1 : 0,
        pointerEvents: visible ? 'auto' : 'none'
      }}
    >
      {children}
    </div>
  );
};

// 样式化的内容容器
const SimpleContentWrapper = ({ blurred, disabled, children }) => {
  return (
    <div 
      style={{
        ...Styles.content,
        filter: blurred ? 'blur(1px)' : 'none',
        pointerEvents: disabled ? 'none' : 'auto'
      }}
    >
      {children}
    </div>
  );
};

const EnhancedLoading = ({ 
  children, 
  spinning = false, 
  tip, 
  size = 'default',
  minHeight,
  style = {}
}) => {
  // 创建自定义图标
  const antIcon = <CustomLoadingIcon size={size} />;

  return (
    <div style={{
      ...Styles.container,
      minHeight: minHeight || '200px',
      ...style
    }}>
      <SimpleLoadingWrapper visible={spinning}>
        <Spin indicator={antIcon} />
        {tip && <div style={Styles.loadingText}>{tip}</div>}
      </SimpleLoadingWrapper>
      <SimpleContentWrapper blurred={spinning} disabled={spinning}>
        {children}
      </SimpleContentWrapper>
    </div>
  );
};

export default EnhancedLoading; 