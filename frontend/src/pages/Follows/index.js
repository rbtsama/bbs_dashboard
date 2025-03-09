import React from 'react';
import { Typography } from 'antd';
import ThreadFollowList from '../../components/tables/ThreadFollowList';

const { Title } = Typography;

const FollowsPage = () => {
  return (
    <div>
      <div className="follows-header">
        <Title level={2}>我的关注</Title>
      </div>
      <ThreadFollowList />
    </div>
  );
};

export default FollowsPage; 