import React, { useState, useEffect } from 'react';
import { Timeline, Spin, message, Pagination, Empty } from 'antd';
import axios from 'axios';
import styled from 'styled-components';

const API_BASE_URL = '/api';

// 优化的时间线项目样式
const StyledTimeline = styled(Timeline)`
  padding: 16px 24px;
  max-height: 60vh;
  overflow-y: auto;
  
  .ant-timeline-item-content {
    font-size: 15px;
    line-height: 1.6;
  }
  
  .action-label {
    margin-right: 12px;
    font-size: 16px;
    font-weight: 500;
  }
  
  .time-label {
    color: #666;
  }
`;

// 悬停时间线样式
const HoverTimeline = styled(Timeline)`
  padding: 4px 0;
  
  .ant-timeline-item {
    padding-bottom: 12px;
  }
  
  .ant-timeline-item-content {
    font-size: 14px !important;
    line-height: 1.6;
  }
  
  .action-label {
    margin-right: 8px;
    font-size: 14px !important;
    font-weight: 600;
    color: #222;
  }
  
  .time-label {
    color: #555;
    font-size: 14px !important;
  }
`;

// 帖子信息容器样式
const ThreadInfoContainer = styled.div`
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 8px;
  background: #fafafa;
  border-radius: 4px;

  .title {
    font-size: 15px;
    font-weight: 600;
    color: #1890ff;
    margin-bottom: 8px;
    cursor: pointer;
    &:hover {
      color: #40a9ff;
    }
  }

  .meta {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    font-size: 13px;
    color: #666;

    .item {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .author {
      color: #1890ff;
      cursor: pointer;
      &:hover {
        color: #40a9ff;
      }
    }
  }
`;

// 查看更多按钮样式
const ViewMoreButton = styled.div`
  color: #4056F4;
  font-size: 15px;
  font-weight: 500;
  text-align: center;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    color: #01CDFE;
    text-decoration: underline;
  }
`;

// 分页容器样式
const PaginationContainer = styled.div`
  display: flex;
  justify-content: center;
  padding: 16px 0;
  margin-top: 8px;
  border-top: 1px solid #f0f0f0;
`;

// 空状态样式
const StyledEmpty = styled(Empty)`
  padding: 32px 0;
`;

// 完整历史记录组件
const ActionLogs = ({ threadId, url }) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });

  const fetchData = async (page = 1, pageSize = 10) => {
    if (!threadId && !url) {
      console.warn('ActionLogs: 没有提供threadId或url参数');
      return;
    }
    
    setLoading(true);
    try {
      const params = {};
      if (threadId) params.thread_id = threadId;
      if (url) params.url = url;
      params.limit = pageSize;
      params.page = page;

      console.log('请求参数:', params);
      const response = await axios.get(`${API_BASE_URL}/action-logs`, { params });
      
      // 添加响应数据日志
      console.log('API响应数据:', response.data);
      
      // 处理数据 - 确保response.data和response.data.data存在
      if (response.data && Array.isArray(response.data.data)) {
        const processedData = response.data.data
          .filter(item => item !== null) // 过滤掉null项
          .map(item => ({
            ...item,
            // 确保event_type和event_time字段存在
            event_type: item.event_type || item.action || '未知',
            event_time: item.event_time || item.action_time || new Date().toISOString()
          }));

        console.log('处理后的数据:', processedData);
        setData(processedData);
        setPagination({
          current: page,
          pageSize: pageSize,
          total: response.data.total || 0
        });
      } else {
        // 如果返回数据结构不正确，使用空数组
        console.warn('API返回的数据格式不正确:', response.data);
        setData([]);
        setPagination({
          current: 1,
          pageSize: 10,
          total: 0
        });
      }
    } catch (error) {
      console.error('获取更新历史失败:', error);
      // 不向用户显示错误消息，只在控制台记录
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (threadId || url) {
      console.log('ActionLogs组件参数变化，重新获取数据:', { threadId, url });
      fetchData(pagination.current, pagination.pageSize);
    }
  }, [threadId, url]);

  const handlePageChange = (page, pageSize) => {
    fetchData(page, pageSize);
  };

  const getActionColor = (eventType) => {
    switch (eventType) {
      case '重发': return 'blue';
      case '回帖': return 'green';
      case '删回帖': return 'red';
      case '发帖': case '新发布': return 'purple';
      default: return 'gray';
    }
  };

  return (
    <Spin spinning={loading}>
      {data.length > 0 ? (
        <>
          <StyledTimeline
            items={data.map(item => ({
              color: getActionColor(item.event_type),
              children: (
                <div>
                  <span className="action-label">{item.event_type}</span>
                  <span className="time-label">
                    {new Date(item.event_time).toLocaleString('zh-CN', {
                      year: 'numeric',
                      month: '2-digit',
                      day: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit',
                      hour12: false
                    })}
                  </span>
                </div>
              )
            }))}
          />
          {pagination.total > pagination.pageSize && (
            <PaginationContainer>
              <Pagination
                current={pagination.current}
                pageSize={pagination.pageSize}
                total={pagination.total}
                onChange={handlePageChange}
                showSizeChanger={false}
                showTotal={(total) => `共 ${total} 条记录`}
              />
            </PaginationContainer>
          )}
        </>
      ) : (
        <StyledEmpty description="暂无更新记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      )}
    </Spin>
  );
};

// 悬停预览组件
export const HoverActionLogs = ({ 
  threadId, 
  url, 
  onViewMore,
  title,
  author,
  authorLink,
  repostCount = 0,
  replyCount = 0,
  deleteReplyCount = 0,
  daysOld = 0,
  lastActive = 0
}) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);

  const fetchData = async () => {
    if (!threadId && !url) {
      console.warn('HoverActionLogs: 没有提供threadId或url参数');
      setData([]);
      return;
    }
    
    console.log('HoverActionLogs组件获取数据:', { threadId, url });
    setLoading(true);
    try {
      const params = {};
      if (threadId) params.thread_id = threadId;
      if (url) params.url = url;
      params.limit = 5;
      params.page = 1;
      
      const response = await axios.get(`${API_BASE_URL}/action-logs`, { params });
      console.log('HoverActionLogs API响应:', response.data);
      
      if (response.data && Array.isArray(response.data.data)) {
        const processedData = response.data.data
          .filter(item => item !== null)
          .map(item => ({
            ...item,
            // 确保event_type和event_time字段存在
            event_type: item.event_type || item.action || '未知',
            event_time: item.event_time || item.action_time || new Date().toISOString()
          }));
        
        console.log('处理后的悬停数据:', processedData);
        setData(processedData);
        setTotal(response.data.total || processedData.length);
      } else {
        console.warn('API返回的数据格式不正确:', response.data);
        setData([]);
        setTotal(0);
      }
    } catch (error) {
      console.error('获取操作日志失败:', error);
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (threadId || url) {
      fetchData();
    }
  }, [threadId, url]);

  const getActionColor = (eventType) => {
    switch (eventType) {
      case '重发': return 'blue';
      case '回帖': return 'green';
      case '删回帖': return 'red';
      case '发帖': case '新发布': return 'purple';
      default: return 'gray';
    }
  };

  return (
    <Spin spinning={loading}>
      {data.length > 0 ? (
        <>
          <HoverTimeline
            items={data.map(item => ({
              color: getActionColor(item.event_type),
              children: (
                <div>
                  <span className="action-label">{item.event_type}</span>
                  <span className="time-label">
                    {new Date(item.event_time).toLocaleString('zh-CN', {
                      year: 'numeric',
                      month: '2-digit',
                      day: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit',
                      hour12: false
                    })}
                  </span>
                </div>
              )
            }))}
          />
          {total > 5 && (
            <ViewMoreButton onClick={onViewMore}>
              查看全部{total}条更新记录
            </ViewMoreButton>
          )}
        </>
      ) : (
        <Empty description="暂无更新记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      )}
    </Spin>
  );
};

export default ActionLogs; 