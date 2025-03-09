import React, { useState, useEffect, useCallback } from 'react';
import { Card, Tabs, Table, Timeline, Statistic, Row, Col, Typography, Spin, Empty, Button, App } from 'antd';
import { Line } from '@ant-design/charts';
import { useSelector, useDispatch } from 'react-redux';
import { unfollowThread } from '../redux/actions';
import { fetchThreadHistory } from '../services/api';

const { Text } = Typography;

// 模拟线程历史数据
const generateMockThreadHistory = (threadId) => {
  return Array.from({ length: 20 }, (_, i) => ({
    id: `history_${threadId}_${i}`,
    thread_id: threadId,
    scraping_time: new Date(Date.now() - (20 - i) * 24 * 60 * 60 * 1000).toISOString(),
    update_reason: ['重发', '回帖', '其他'][Math.floor(Math.random() * 3)],
    view_count: Math.floor(Math.random() * 10000) + 100 * i,
    page_num: Math.floor(Math.random() * 20) + 1,
    num: Math.floor(Math.random() * 100) + 1
  }));
};

const FollowedThreadDetails = () => {
  const followedThreads = useSelector(state => state.follow.threads);
  const [activeThreadId, setActiveThreadId] = useState(null);
  const [threadHistory, setThreadHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();
  const { message } = App.useApp();
  
  useEffect(() => {
    if (followedThreads.length > 0 && !activeThreadId) {
      setActiveThreadId(followedThreads[0].thread_id);
    }
  }, [followedThreads, activeThreadId]);
  
  const fetchThreadHistoryData = useCallback(async (threadId) => {
    setLoading(true);
    try {
      // 使用模拟数据代替 API 调用
      // const data = await fetchThreadHistory(threadId);
      const data = generateMockThreadHistory(threadId);
      setThreadHistory(data);
    } catch (error) {
      console.error('加载帖子历史记录失败:', error);
      message.error('加载帖子历史记录失败，请稍后再试');
    } finally {
      setLoading(false);
    }
  }, [message]);
  
  useEffect(() => {
    if (activeThreadId) {
      fetchThreadHistoryData(activeThreadId);
    }
  }, [activeThreadId, fetchThreadHistoryData]);
  
  const handleUnfollow = (threadId) => {
    dispatch(unfollowThread(threadId));
    message.success('已取消关注');
  };
  
  // 操作历史数据列
  const operationHistoryColumns = [
    { title: '抓取时间', dataIndex: 'scraping_time', key: 'scraping_time' },
    { title: '更新原因', dataIndex: 'update_reason', key: 'update_reason' },
    { title: '页数', dataIndex: 'page_num', key: 'page_num' },
    { title: '编号', dataIndex: 'num', key: 'num' },
    { title: '阅读量', dataIndex: 'view_count', key: 'view_count' }
  ];
  
  // 阅读量趋势图配置
  const viewTrendConfig = {
    data: threadHistory.map(h => ({
      time: h.scraping_time,
      views: h.view_count
    })),
    xField: 'time',
    yField: 'views',
    smooth: true,
    point: {
      size: 5,
      shape: 'diamond',
    }
  };
  
  if (followedThreads.length === 0) {
    return <Empty description="暂无关注的帖子" />;
  }
  
  const getTabItems = () => {
    return followedThreads.map(thread => ({
      key: thread.thread_id,
      label: thread.title ? (thread.title.substring(0, 15) + '...') : '未知标题',
      children: (
        <Card 
          title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>{thread.title}</span>
              <Button 
                type="primary" 
                danger 
                size="small"
                onClick={() => handleUnfollow(thread.thread_id)}
              >
                取消关注
              </Button>
            </div>
          }
        >
          <Text type="secondary">
            作者: <a href={thread.authorUrl} target="_blank" rel="noopener noreferrer">{thread.author}</a> | 
            关注时间: {new Date(thread.followedAt).toLocaleString()}
          </Text>
          
          <Row gutter={16} style={{ marginTop: 16 }}>
            <Col span={6}>
              <Statistic title="当前阅读量" value={thread.viewCount || 0} />
            </Col>
            <Col span={6}>
              <Statistic title="当前页数" value={thread.pageNum || 0} />
            </Col>
            <Col span={6}>
              <Statistic title="重发次数" value={thread.repostCount || 0} />
            </Col>
            <Col span={6}>
              <Statistic title="编号" value={thread.num || 0} />
            </Col>
          </Row>
          
          <Spin spinning={loading}>
            <Tabs 
              defaultActiveKey="history" 
              style={{ marginTop: 24 }}
              items={[
                {
                  key: 'history',
                  label: '操作历史',
                  children: (
                    <Table 
                      columns={operationHistoryColumns}
                      dataSource={threadHistory}
                      pagination={{ pageSize: 5 }}
                      rowKey="id"
                    />
                  )
                },
                {
                  key: 'trends',
                  label: '阅读量趋势',
                  children: (
                    threadHistory.length > 0 ? (
                      <Line {...viewTrendConfig} />
                    ) : (
                      <Empty description="暂无趋势数据" />
                    )
                  )
                },
                {
                  key: 'timeline',
                  label: '更新时间线',
                  children: (
                    <Timeline 
                      mode="left" 
                      style={{ marginTop: 16 }}
                      items={threadHistory.map((record, index) => ({
                        key: index,
                        color: record.update_reason === '重发' ? 'blue' : 
                               record.update_reason === '回帖' ? 'green' : 'red',
                        children: (
                          <>
                            <p><strong>{record.scraping_time}</strong></p>
                            <p>更新原因: {record.update_reason}</p>
                            <p>阅读量: {record.view_count}</p>
                            <p>页数/编号: {record.page_num}/{record.num}</p>
                          </>
                        )
                      }))}
                    />
                  )
                }
              ]}
            />
          </Spin>
        </Card>
      )
    }));
  };
  
  return (
    <div className="followed-threads">
      <Tabs 
        type="card" 
        activeKey={activeThreadId} 
        onChange={setActiveThreadId}
        tabPosition="left"
        items={getTabItems()}
      />
    </div>
  );
};

export default FollowedThreadDetails; 