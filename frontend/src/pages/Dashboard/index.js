import React, { useState, useEffect } from 'react';
import { Row, Col, Typography, Spin, App } from 'antd';
import PostTrendChart from '../../components/charts/PostTrendChart';
import UpdateTrendChart from '../../components/charts/UpdateTrendChart';
import ViewTrendChart from '../../components/charts/ViewTrendChart';
import NewPostsTable from '../../components/tables/NewPostsTable';
import WordCloud from '../../components/charts/WordCloud';
import { fetchNewPostsYesterday } from '../../services/api';

const { Title } = Typography;

const Dashboard = () => {
  const [loading, setLoading] = useState(false);
  const { message } = App.useApp();
  
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // 获取数据
        await fetchNewPostsYesterday();
      } catch (error) {
        console.error('加载数据失败:', error);
        message.error('加载数据失败');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [message]);
  
  return (
    <div>
      <div className="dashboard-header">
        <Title level={2}>论坛数据大盘</Title>
      </div>
      
      <Spin spinning={loading}>
        {/* 按照要求调整模块顺序 */}
        
        {/* 1. 更新趋势 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col span={24}>
            <UpdateTrendChart />
          </Col>
        </Row>
        
        {/* 2. 发帖趋势 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col span={24}>
            <PostTrendChart />
          </Col>
        </Row>
        
        {/* 3. 昨日新帖 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col span={24}>
            <NewPostsTable />
          </Col>
        </Row>
        
        {/* 4. 阅读趋势 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col span={24}>
            <ViewTrendChart />
          </Col>
        </Row>
        
        {/* 5. 热门词汇 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col span={24}>
            <WordCloud />
          </Col>
        </Row>
      </Spin>
    </div>
  );
};

export default Dashboard; 