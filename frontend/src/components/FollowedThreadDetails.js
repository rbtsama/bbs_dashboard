import React, { useState, useEffect, useCallback } from 'react';
import { Card, Tabs, Table, Timeline, Statistic, Row, Col, Typography, Spin, Empty, Button, App } from 'antd';
import { Line } from '@ant-design/plots';
import { useSelector, useDispatch } from 'react-redux';
import { unfollowThread } from '../redux/actions';
import { fetchThreadHistory } from '../services/api';
import { deleteThreadFollow } from '../services/api';

const { Text } = Typography;

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
      // 使用真实API调用而不是模拟数据
      const response = await fetchThreadHistory(threadId);
      if (response && response.data) {
        setThreadHistory(response.data);
      } else {
        setThreadHistory([]);
      }
    } catch (error) {
      console.error('加载帖子历史记录失败:', error);
      message.error('加载帖子历史记录失败，请稍后再试');
      setThreadHistory([]);
    } finally {
      setLoading(false);
    }
  }, [message]);
  
  useEffect(() => {
    if (activeThreadId) {
      fetchThreadHistoryData(activeThreadId);
    }
  }, [activeThreadId, fetchThreadHistoryData]);
  
  const handleUnfollow = (thread) => {
    try {
      if (!thread) {
        message.error('无法取消关注，帖子信息不存在');
        return;
      }
      
      // 提前更新状态，使UI立即反应
      dispatch(unfollowThread(thread.thread_id));
      
      // 调用API删除关注
      deleteThreadFollow({
        thread_id: thread.thread_id,
        title: thread.title,
        url: thread.url,
        type: 'my_follow'
      }).then(() => {
        message.success('已取消关注');
        // 这里不需要重复调用dispatch，因为前面已经调用过了
      }).catch(error => {
        console.error('取消关注失败:', error);
        if (error.response && error.response.status === 404) {
          message.warning('找不到关注记录，可能已被删除');
        } else {
          message.error('取消关注失败，请稍后再试');
          // 如果API调用失败，需要恢复状态
          // 这里需要添加恢复状态的逻辑
        }
      });
    } catch (error) {
      console.error('取消关注时发生错误:', error);
      message.error('取消关注失败，请稍后再试');
    }
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
      style: {
        fill: '#2980B9',
        stroke: '#2980B9',
        lineWidth: 2,
      }
    },
    line: {
      style: {
        stroke: '#2980B9',
        lineWidth: 3,
      }
    },
    area: {
      style: {
        fill: 'l(270) 0:#2980B9 1:rgba(41, 128, 185, 0.1)',
      }
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
                onClick={() => handleUnfollow(thread)}
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
                      rowKey={record => `${record.id || record.scraping_time || ''}_${Math.random().toString(36).substr(2, 9)}`}
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
                        color: record.update_reason === '重发' ? '#E67E22' : 
                               record.update_reason === '回帖' ? '#27AE60' : '#3498DB',
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