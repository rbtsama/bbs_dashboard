import React from 'react';
import { Typography, Divider } from 'antd';
import ThreadRankingTable from '../../components/tables/ThreadRankingTable';
import UserRankingTable from '../../components/tables/UserRankingTable';

const { Title } = Typography;

const Rankings = () => {
  return (
    <div>
      <Title level={2}>论坛排行榜</Title>
      
      {/* 帖子排行榜 */}
      <div style={{ marginBottom: 24 }}>
        <ThreadRankingTable />
      </div>
      
      <Divider />
      
      {/* 用户排行榜 */}
      <div style={{ marginBottom: 24 }}>
        <UserRankingTable />
      </div>
    </div>
  );
};

export default Rankings; 