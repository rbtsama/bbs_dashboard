import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Spin, Typography, Button, Tooltip, App, Space, Badge, ConfigProvider, Popover, Modal } from 'antd';
import { HeartOutlined, HeartFilled, StarOutlined, StarFilled, FireOutlined, HistoryOutlined } from '@ant-design/icons';
import axios from 'axios';
import styled from 'styled-components';
import ActionLogs, { HoverActionLogs } from '../ActionLogs';
import { UpdateHistoryButton } from '../HistoryButton';
import { UpdateHistoryModal } from '../HistoryModal';
import { HistoryModalTitle } from '../HistoryButton';
import { API_BASE_URL } from '../../config';
import { deleteThreadFollow } from '../../services/api';

const { Link } = Typography;

// 复用ThreadRankingTable的样式组件
const Container = styled.div`
  padding: 0;
  
  .ant-pagination {
    display: flex;
    justify-content: center;
    margin-top: 12px;
  }
`;

const RankingCard = styled(Card)`
  margin: 0;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  border: none;
  background: #fff;
  
  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  }
  
  .ant-card-head {
    background: linear-gradient(135deg, #f8faff 0%, #ffffff 100%);
    border-bottom: 1px solid #f0f0f0;
    padding: 0;
    min-height: 60px;
  }
  
  .ant-card-head-title {
    padding: 14px 20px;
    font-size: 16px;
    font-weight: 600;
  }
`;

const TableTitle = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  
  .left-section {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .icon {
    font-size: 20px;
    color: #1890ff;
    background: #e6f4ff;
    padding: 8px;
    border-radius: 8px;
    transition: all 0.3s;
    
    &:hover {
      transform: scale(1.05);
      background: #d9edff;
    }
  }
  
  .title-text {
    font-size: 16px;
    font-weight: 600;
    color: #1f1f1f;
  }
`;

const StyledLink = styled(Link)`
  font-size: 14px;
  font-weight: 500;
  color: #1890ff;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  
  &:hover {
    color: #40a9ff;
    text-decoration: none;
    transform: translateX(2px);
  }
  
  &::after {
    content: '→';
    font-size: 14px;
    margin-left: 2px;
    transition: transform 0.3s;
  }
  
  &:hover::after {
    transform: translateX(2px);
  }
`;

const HoverPopoverContent = styled.div`
  width: 350px;
  padding: 12px;
`;

const globalStyles = `
  .thread-follow-table .even-row {
    background-color: #ffffff;
  }
  
  .thread-follow-table .odd-row {
    background-color: #fafafa;
  }
  
  .thread-follow-table .ant-table-cell {
    transition: all 0.3s;
  }

  .thread-follow-table .ant-table-row:hover .ant-table-cell {
    background-color: #e6f7ff !important;
  }

  .thread-follow-table .ant-table-thead > tr > th {
    background: #fafafa;
    font-weight: 600;
  }

  .thread-follow-table .ant-table-tbody > tr > td {
    padding: 12px 8px;
  }
`;

const ThreadFollowTable = ({ type = 'my_follow' }) => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    showSizeChanger: true
  });
  const { message } = App.useApp();

  // 操作日志状态
  const [actionLogsVisible, setActionLogsVisible] = useState(false);
  const [currentThreadId, setCurrentThreadId] = useState(null);
  const [currentUrl, setCurrentUrl] = useState(null);
  const [currentThread, setCurrentThread] = useState(null);

  useEffect(() => {
    fetchData();
  }, [type]);

  // 获取关注列表数据
  const fetchData = async () => {
    setLoading(true);
    try {
      // 获取关注列表
      const response = await axios.get(`${API_BASE_URL}/thread-follows`, {
        params: { type }
      });

      if (response.data && response.data.data) {
        // 处理数据，确保数值字段有默认值
        const processedData = response.data.data.map(item => ({
          ...item,
          repost_count: item.repost_count || 0,
          reply_count: item.reply_count || 0,
          delete_reply_count: item.delete_reply_count || 0,
          daysold: item.daysold || 0,
          last_active: item.last_active || 0
        }));
        
        setData(processedData);
        setPagination(prev => ({
          ...prev,
          total: response.data.total
        }));
      } else {
        setData([]);
      }
    } catch (error) {
      console.error('获取关注列表数据失败:', error);
      message.error('获取数据失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 处理取消关注
  const handleUnfollow = async (record) => {
    try {
      if (!record) {
        console.error('帖子信息不存在');
        message.error('操作失败，帖子信息不存在');
        return;
      }

      // 立即从本地数据中移除该项，提前更新UI
      setData(prevData => prevData.filter(item => 
        item.id !== record.id && 
        item.thread_id !== record.thread_id && 
        item.url !== record.url
      ));

      const params = {
        thread_id: record.thread_id,
        title: record.title,
        url: record.url,
        type
      };

      // 调用API
      await deleteThreadFollow(params);
      
      message.success(type === 'my_follow' ? '已取消关注' : '已取消标记');
      
      // 延迟一秒后刷新数据，确保后端操作完成
      setTimeout(() => {
        fetchData(); // 刷新数据
      }, 500);
    } catch (error) {
      console.error('取消关注失败:', error);
      if (error.response && error.response.status === 404) {
        message.warning('找不到关注记录，可能已被删除');
        fetchData(); // 刷新数据以更新UI
      } else {
        message.error('操作失败，请稍后重试');
        // 重新获取数据，恢复UI状态
        fetchData();
      }
    }
  };

  // 查看操作日志
  const handleViewActionLogs = useCallback((record) => {
    setCurrentThreadId(record.thread_id);
    setCurrentUrl(record.url);
    setCurrentThread(record);
    setActionLogsVisible(true);
  }, []);

  // 渲染数值徽章
  const renderNumberBadge = (value, fieldName) => {
    const numValue = parseInt(value, 10) || 0;
    const colors = {
      repost_count: '#2980B9',
      reply_count: '#27AE60',
      delete_reply_count: '#E74C3C'
    };
    
    return (
      <span 
        style={{ 
          backgroundColor: colors[fieldName] || '#1890ff',
          fontSize: '14px',
          fontWeight: 'bold',
          padding: '4px 8px',
          borderRadius: '10px',
          color: 'white',
          display: 'inline-block',
          minWidth: '30px',
          textAlign: 'center'
        }} 
      >
        {numValue}
      </span>
    );
  };

  const columns = [
    {
      title: '更新历史',
      key: 'action_logs',
      width: 80,
      align: 'center',
      fixed: 'left',
      render: (_, record) => (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '4px 0' }}>
          <Popover
            content={
              <HoverPopoverContent>
                <HoverActionLogs 
                  threadId={record.thread_id} 
                  url={record.url} 
                  onViewMore={() => handleViewActionLogs(record)}
                />
              </HoverPopoverContent>
            }
            title={<span style={{ fontSize: '18px', fontWeight: 'bold', padding: '16px 20px', display: 'block', borderBottom: '1px solid #f0f0f0' }}>更新历史</span>}
            trigger="hover"
            placement="right"
            overlayStyle={{ maxWidth: '400px' }}
            mouseEnterDelay={0.1}
            mouseLeaveDelay={0.3}
            destroyTooltipOnHide={true}
          >
            <span>
              <UpdateHistoryButton onClick={(e) => {
                e.stopPropagation();
                handleViewActionLogs(record);
              }} />
            </span>
          </Popover>
        </div>
      )
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: '35%',
      ellipsis: true,
      fixed: 'left',
      render: (text, record) => (
        <a href={record.url} target="_blank" rel="noopener noreferrer">
          {text}
        </a>
      )
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: '12%',
      ellipsis: true,
      responsive: ['md'],
      render: (text, record) => (
        <StyledLink href={record.author_link} target="_blank" rel="noopener noreferrer">
          {text}
        </StyledLink>
      )
    },
    {
      title: '重发',
      dataIndex: 'repost_count',
      key: 'repost_count',
      width: 90,
      align: 'center',
      responsive: ['sm'],
      render: (text) => renderNumberBadge(text, 'repost_count')
    },
    {
      title: '回帖',
      dataIndex: 'reply_count',
      key: 'reply_count',
      width: 90,
      align: 'center',
      responsive: ['sm'],
      render: (text) => renderNumberBadge(text, 'reply_count')
    },
    {
      title: '删回帖',
      dataIndex: 'delete_reply_count',
      key: 'delete_reply_count',
      width: 90,
      align: 'center',
      responsive: ['md'],
      render: (text) => renderNumberBadge(text, 'delete_reply_count')
    },
    {
      title: '帖龄',
      dataIndex: 'daysold',
      key: 'daysold',
      width: 90,
      align: 'center',
      responsive: ['lg'],
      render: (text) => <span style={{ fontSize: '14px' }}>{text || 0}天</span>
    },
    {
      title: '活跃',
      dataIndex: 'last_active',
      key: 'last_active',
      width: 90,
      align: 'center',
      responsive: ['lg'],
      render: (text) => <span style={{ fontSize: '14px' }}>{text || 0}天前</span>
    },
    {
      title: '操作',
      key: 'action',
      width: 90,
      align: 'center',
      render: (_, record) => (
        <Button
          type="text"
          danger
          icon={type === 'my_follow' ? <HeartFilled /> : <StarFilled />}
          onClick={() => handleUnfollow(record)}
        >
          取消{type === 'my_follow' ? '关注' : '标记'}
        </Button>
      )
    }
  ];

  const title = (
    <TableTitle>
      <div className="left-section">
        {type === 'my_follow' ? (
          <HeartFilled className="icon" style={{ color: '#ff4d4f', background: '#fff1f0' }} />
        ) : (
          <StarFilled className="icon" style={{ color: '#faad14', background: '#fffbe6' }} />
        )}
        <span className="title-text">
          {type === 'my_follow' ? '我的关注' : '我的帖子'}
        </span>
      </div>
    </TableTitle>
  );

  return (
    <ConfigProvider>
      <Container>
        <style>{globalStyles}</style>
        <RankingCard
          title={title}
          bodyStyle={{ padding: 0 }}
        >
          <Table
            className="thread-follow-table"
            columns={columns}
            dataSource={data}
            loading={loading}
            pagination={pagination}
            rowKey={record => record.thread_id || record.url}
            rowClassName={(_, index) => index % 2 === 0 ? 'even-row' : 'odd-row'}
            size="middle"
            scroll={{ x: 'max-content' }}
          />
        </RankingCard>

        <UpdateHistoryModal
          visible={actionLogsVisible}
          onCancel={() => setActionLogsVisible(false)}
          title={
            <HistoryModalTitle>
              <HistoryOutlined className="icon" />
              <span className="text">更新历史</span>
            </HistoryModalTitle>
          }
          width={800}
          destroyOnClose
        >
          <ActionLogs threadId={currentThreadId} url={currentUrl} />
        </UpdateHistoryModal>
      </Container>
    </ConfigProvider>
  );
};

export default ThreadFollowTable; 