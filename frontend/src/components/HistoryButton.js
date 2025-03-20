import React, { forwardRef } from 'react';
import styled from 'styled-components';
import { ClockCircleOutlined, HistoryOutlined } from '@ant-design/icons';

// 科技感时间机器按钮 - 统一样式
const StyledButton = styled.div`
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.3s ease-out;
  
  .outer-ring {
    position: absolute;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: 2px solid var(--ring-color, #4056F4);
    box-shadow: 0 0 8px var(--ring-color, #4056F4);
    animation: rotate 10s linear infinite;
    opacity: 0.7;
  }
  
  .middle-ring {
    position: absolute;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: 1px dashed rgba(64, 86, 244, 0.5);
    animation: rotate-reverse 7s linear infinite;
  }
  
  .inner-circle {
    position: absolute;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary-color, #4056F4), var(--secondary-color, #01CDFE));
    box-shadow: 0 0 10px rgba(1, 205, 254, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1;
    transition: all 0.3s ease;
  }
  
  .time-icon {
    color: white;
    font-size: 14px;
    z-index: 2;
    filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
  }
  
  .particles {
    position: absolute;
    width: 100%;
    height: 100%;
    z-index: 0;
  }
  
  .particle {
    position: absolute;
    width: 3px;
    height: 3px;
    border-radius: 50%;
    background: var(--primary-color, #4056F4);
    opacity: 0;
    transition: all 0.3s;
  }
  
  &:hover {
    transform: translateY(-2px);
    
    .outer-ring {
      opacity: 1;
      transform: scale(1.05);
    }
    
    .middle-ring {
      transform: scale(1.1) rotate(-30deg);
    }
    
    .inner-circle {
      transform: scale(1.1);
    }
    
    .particle {
      opacity: 0.8;
      animation: pulse 2s infinite;
    }
  }
  
  &:active {
    transform: translateY(1px) scale(0.95);
  }
  
  .particle:nth-child(1) { top: 0; left: 50%; transform: translateX(-50%); animation-delay: 0s; }
  .particle:nth-child(2) { top: 20%; right: 10%; animation-delay: 0.3s; }
  .particle:nth-child(3) { bottom: 0; left: 50%; transform: translateX(-50%); animation-delay: 0.6s; }
  .particle:nth-child(4) { top: 50%; left: 0; transform: translateY(-50%); animation-delay: 0.9s; }
  .particle:nth-child(5) { top: 70%; right: 20%; animation-delay: 1.2s; }
  .particle:nth-child(6) { top: 20%; left: 15%; animation-delay: 1.5s; }
  
  @keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  @keyframes rotate-reverse {
    from { transform: rotate(0deg); }
    to { transform: rotate(-360deg); }
  }
  
  @keyframes pulse {
    0% { transform: scale(1); opacity: 0.8; }
    50% { transform: scale(2.5); opacity: 0.4; }
    100% { transform: scale(4); opacity: 0; }
  }
`;

// 更新历史按钮 - 紫色主题，使用forwardRef解决findDOMNode警告
export const UpdateHistoryButton = forwardRef(({ onClick }, ref) => (
  <StyledButton 
    onClick={onClick}
    ref={ref}
    style={{ 
      '--primary-color': '#9B5DE5', 
      '--secondary-color': '#7209B7',
      '--ring-color': '#9B5DE5'
    }}
  >
    <div className="outer-ring"></div>
    <div className="middle-ring"></div>
    <div className="inner-circle">
      <HistoryOutlined className="time-icon" />
    </div>
    <div className="particles">
      <div className="particle"></div>
      <div className="particle"></div>
      <div className="particle"></div>
      <div className="particle"></div>
      <div className="particle"></div>
      <div className="particle"></div>
    </div>
  </StyledButton>
));

// 发帖历史按钮 - 红色主题，使用forwardRef解决findDOMNode警告
export const PostHistoryButton = forwardRef(({ onClick }, ref) => (
  <StyledButton 
    onClick={onClick}
    ref={ref}
    style={{ 
      '--primary-color': '#E74C3C', 
      '--secondary-color': '#C0392B',
      '--ring-color': '#E74C3C'
    }}
  >
    <div className="outer-ring"></div>
    <div className="middle-ring"></div>
    <div className="inner-circle">
      <ClockCircleOutlined className="time-icon" />
    </div>
    <div className="particles">
      <div className="particle"></div>
      <div className="particle"></div>
      <div className="particle"></div>
      <div className="particle"></div>
      <div className="particle"></div>
      <div className="particle"></div>
    </div>
  </StyledButton>
));

// 给按钮组件添加显示名称，方便调试
UpdateHistoryButton.displayName = 'UpdateHistoryButton';
PostHistoryButton.displayName = 'PostHistoryButton';

// 统一的模态框标题样式
export const HistoryModalTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  
  .icon {
    font-size: 18px;
  }
  
  .text {
    font-size: 18px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 650px;
  }
`;

export default {
  UpdateHistoryButton,
  PostHistoryButton,
  HistoryModalTitle
}; 