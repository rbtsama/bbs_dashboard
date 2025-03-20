import React from 'react';
import { Typography, Empty } from 'antd';
import styled from 'styled-components';

const { Title } = Typography;

const PageTitle = styled(Title)`
  margin-bottom: 24px;
`;

const FollowedThreads = () => {
  return (
    <div>
      <PageTitle level={2}>关注列表</PageTitle>
      
      <Empty 
        description="关注列表功能开发中，敬请期待..." 
        style={{ margin: '100px 0' }}
      />
    </div>
  );
};

export default FollowedThreads; 