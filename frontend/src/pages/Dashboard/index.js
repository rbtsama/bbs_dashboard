import React, { useState, useEffect } from 'react';
import { Row, Col, Typography, Spin, App as AntdApp } from 'antd';
import PostTrendChart from '../../components/charts/PostTrendChart';
import UpdateTrendChart from '../../components/charts/UpdateTrendChart';
import ViewTrendChart from '../../components/charts/ViewTrendChart';
import NewPostsTable from '../../components/tables/NewPostsTable';
import { getNewPosts } from '../../services/api';
import styled from 'styled-components';

const { Title } = Typography;

// 模块间距
const ModuleWrapper = styled.div`
  margin-bottom: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const Dashboard = () => {
  const [loading, setLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState(null);
  const { message } = AntdApp.useApp();
  
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // 获取数据
        await getNewPosts();
      } catch (error) {
        console.error('加载数据失败:', error);
        message.error('加载数据失败');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [message]);
  
  // 处理日期选择
  const handleDateSelect = (date) => {
    console.log('选择了日期:', date);
    setSelectedDate(date);
  };
  
  return (
    <div>
      <Spin spinning={loading}>
        {/* 按照要求调整模块顺序 */}
        
        {/* 1. 更新趋势 */}
        <ModuleWrapper>
          <UpdateTrendChart />
        </ModuleWrapper>
        
        {/* 2. 发帖趋势 */}
        <ModuleWrapper>
          <PostTrendChart />
        </ModuleWrapper>
        
        {/* 3. 新帖列表 */}
        <ModuleWrapper>
          <NewPostsTable selectedDate={selectedDate} />
        </ModuleWrapper>
        
        {/* 4. 阅读趋势 */}
        <ModuleWrapper>
          <ViewTrendChart />
        </ModuleWrapper>
      </Spin>
    </div>
  );
};

export default Dashboard; 