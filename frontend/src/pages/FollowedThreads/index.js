import React from 'react';
import { Typography, Empty } from 'antd';

const { Title } = Typography;

const FollowedThreads = () => {
  return (
    <div>
      <Title level={2}>关注列表</Title>
      
      <Empty 
        description="关注列表功能开发中，敬请期待..." 
        style={{ margin: '100px 0' }}
      />
    </div>
  );
};

export default FollowedThreads; 