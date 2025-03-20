import React, { useState, useEffect } from 'react';
import { Timeline, Spin, Empty, Pagination, Tag, Typography, Tooltip } from 'antd';
import axios from 'axios';
import styled from 'styled-components';
import { ExportOutlined, ClockCircleOutlined } from '@ant-design/icons';

const { Link } = Typography;
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
  
  .post-title {
    font-size: 16px;
    font-weight: 500;
    margin-right: 12px;
    display: block;
    margin-bottom: 4px;
  }
  
  .time-label {
    color: #666;
    font-size: 14px;
  }
  
  .post-status {
    margin-left: 8px;
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
  
  .post-title {
    margin-right: 8px;
    font-size: 14px !important;
    font-weight: 500;
    color: #222;
    display: block;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 250px;
  }
  
  .time-label {
    color: #555;
    font-size: 14px !important;
  }
  
  .post-status {
    margin-left: 8px;
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

// 格式化日期函数
const formatDate = (timestamp) => {
  if (!timestamp) return '未知';
  
  try {
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) return '无效日期';
    
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  } catch (error) {
    console.error('日期格式化错误:', error);
    return '格式错误';
  }
};

// 完整发帖历史组件
const PostHistoryLogs = ({ author }) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });

  const fetchData = async (page = 1, pageSize = 10) => {
    setLoading(true);
    try {
      if (!author) {
        setData([]);
        setLoading(false);
        return;
      }

      console.log('请求参数:', { author, page, limit: pageSize });
      const response = await axios.get(`${API_BASE_URL}/author-post-history`, { 
        params: { 
          author,
          page,
          limit: pageSize
        } 
      });
      
      // 添加响应数据日志
      console.log('API响应数据:', response.data);
      
      // 处理数据 - 确保response.data和response.data.data存在
      if (response.data && Array.isArray(response.data.data)) {
        setData(response.data.data);
        setPagination({
          current: page,
          pageSize: pageSize,
          total: response.data.total || 0
        });
        
        // 输出调试统计信息
        if (response.data.debug) {
          console.log('调试统计信息:', response.data.debug);
          console.log(`总帖子数: ${response.data.debug.total_posts}, 活跃帖子: ${response.data.debug.active_posts}, 不活跃帖子: ${response.data.debug.inactive_posts}`);
        }
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
      console.error('获取发帖历史失败:', error);
      // 不向用户显示错误消息，只在控制台记录
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(pagination.current, pagination.pageSize);
  }, [author]);

  const handlePageChange = (page, pageSize) => {
    fetchData(page, pageSize);
  };

  const getPostColor = (isActive) => {
    return isActive ? 'blue' : 'red';
  };

  return (
    <Spin spinning={loading}>
      {data.length > 0 ? (
        <>
          <StyledTimeline
            items={data.map(item => ({
              color: getPostColor(item.is_active),
              children: (
                <div>
                  <Link 
                    className="post-title" 
                    href={item.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                  >
                    {item.title || '无标题'}
                    <ExportOutlined style={{ fontSize: '14px', marginLeft: '4px' }} />
                  </Link>
                  <span className="time-label">
                    {formatDate(item.post_time)}
                  </span>
                  {!item.is_active && (
                    <Tag className="post-status" color="red">找不到</Tag>
                  )}
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
        <StyledEmpty description="暂无发帖记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      )}
    </Spin>
  );
};

// 悬停预览组件
export const HoverPostHistoryLogs = ({ author, onViewMore }) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (!author) {
        setData([]);
        setLoading(false);
        return;
      }

      console.log('请求参数:', { author, limit: 10, page: 1 });
      const response = await axios.get(`${API_BASE_URL}/author-post-history`, { 
        params: { 
          author,
          limit: 10,
          page: 1
        } 
      });
      
      // 添加响应数据日志
      console.log('API响应数据:', response.data);
      
      // 处理数据 - 确保response.data和response.data.data存在
      if (response.data && Array.isArray(response.data.data)) {
        setData(response.data.data);
        setTotal(response.data.total || 0);
      } else {
        // 如果返回数据结构不正确，使用空数组
        console.warn('API返回的数据格式不正确:', response.data);
        setData([]);
        setTotal(0);
      }
    } catch (error) {
      console.error('获取发帖历史失败:', error);
      // 不向用户显示错误消息，只在控制台记录
      setData([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [author]);

  const getPostColor = (isActive) => {
    return isActive ? 'blue' : 'red';
  };

  return (
    <div>
      <Spin spinning={loading}>
        {data.length > 0 ? (
          <>
            <HoverTimeline
              size="small"
              items={data.map(item => ({
                color: getPostColor(item.is_active),
                children: (
                  <div>
                    <Tooltip title={item.title || '无标题'} destroyTooltipOnHide={true}>
                      <span>
                        <Link 
                          className="post-title" 
                          href={item.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                        >
                          {item.title || '无标题'}
                          <ExportOutlined style={{ fontSize: '12px', marginLeft: '4px' }} />
                        </Link>
                      </span>
                    </Tooltip>
                    <span className="time-label">
                      {formatDate(item.post_time)}
                    </span>
                    {!item.is_active && (
                      <Tag className="post-status" color="red" style={{ fontSize: '12px' }}>找不到</Tag>
                    )}
                  </div>
                )
              }))}
            />
            {total > 10 && (
              <ViewMoreButton onClick={onViewMore}>
                查看全部{total}条发帖历史
              </ViewMoreButton>
            )}
          </>
        ) : (
          <Empty description="暂无发帖记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        )}
      </Spin>
    </div>
  );
};

export default PostHistoryLogs; 