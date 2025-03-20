import React from 'react';
import ThreadRankingTable from '../../components/tables/ThreadRankingTable';
import UserRankingTable from '../../components/tables/UserRankingTable';
import styled from 'styled-components';
import { Typography } from 'antd';

const { Title } = Typography;

// 页面容器样式
const RankingsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 30px;  // 增加卡片间距
  padding: 24px;
  background: linear-gradient(135deg, #f6f8fc 0%, #f0f4f9 100%);
  min-height: 100vh;
  
  @media (max-width: 768px) {
    gap: 24px;
    padding: 16px;
  }
`;

// 页面标题样式
const PageHeader = styled.div`
  margin-bottom: 16px;
  position: relative;
  
  h2 {
    margin-bottom: 0;
  }
`;

// 增加背景装饰元素
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

const Rankings = () => {
  return (
    <RankingsContainer>
      {/* 背景装饰元素 */}
      <BackgroundDecorator />
      
      {/* 页面标题 */}
      <PageHeader>
        <Title level={2}>数据排行榜</Title>
      </PageHeader>
      
      {/* 帖子排行榜 */}
      <ThreadRankingTable />
      
      {/* 用户排行榜 */}
      <UserRankingTable />
      
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
    </RankingsContainer>
  );
};

export default Rankings; 