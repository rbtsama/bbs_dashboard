import React from 'react';
import ThreadFollowList from '../../components/tables/ThreadFollowList';
import styled from 'styled-components';
import { Typography } from 'antd';

const { Title } = Typography;

// 页面容器样式
const FollowsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f6f8fc 0%, #f0f4f9 100%);
`;

// 页面标题样式
const PageHeader = styled.div`
  margin-bottom: 16px;
  position: relative;
  padding: 24px 24px 0;
  
  h2 {
    margin-bottom: 0;
  }
  
  @media (max-width: 768px) {
    padding: 16px 16px 0;
  }
`;

// 背景装饰元素
const BackgroundDecorator = styled.div`
  position: fixed;
  top: 0;
  right: 0;
  width: 40%;
  height: 40%;
  background: radial-gradient(circle at top right, rgba(24, 144, 255, 0.1), rgba(24, 144, 255, 0) 70%);
  z-index: 0;
  pointer-events: none;
`;

const FollowsPage = () => {
  return (
    <FollowsContainer>
      {/* 背景装饰元素 */}
      <BackgroundDecorator />
      
      {/* 页面标题 */}
      <PageHeader>
        <Title level={2}>我的关注</Title>
      </PageHeader>
      
      <ThreadFollowList />
      
      {/* 版权信息 */}
      <div style={{ 
        textAlign: 'center', 
        padding: '16px', 
        color: 'rgba(0,0,0,0.45)', 
        fontSize: '14px',
        marginTop: '8px'
      }}>
        数智罗盘 ©2025
      </div>
    </FollowsContainer>
  );
};

export default FollowsPage; 