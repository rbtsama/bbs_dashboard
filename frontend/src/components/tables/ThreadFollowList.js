import React, { useState, useEffect } from 'react';
import { Card, Table, Spin, Typography, Timeline, message, Button, Modal, Tabs, Space, Popover, App, Badge } from 'antd';
import axios from 'axios';
import ActionLogs, { HoverActionLogs } from '../ActionLogs';
import styled from 'styled-components';
import { FireOutlined, HeartOutlined, HeartFilled, StarOutlined, StarFilled, HistoryOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { UpdateHistoryButton } from '../HistoryButton';
import { UpdateHistoryModal } from '../HistoryModal';
import { HistoryModalTitle } from '../HistoryButton';
import { API_BASE_URL } from '../../config';
import { deleteThreadFollow } from '../../services/api';

const { Link } = Typography;

// 样式化链接
const StyledLink = styled(Link)`
  font-size: 15px;
  font-weight: 500;
  color: #1890ff;
  transition: all 0.3s;
  
  &:hover {
    color: #40a9ff;
    text-decoration: underline;
  }
  
  @media (max-width: 768px) {
    font-size: 14px;
  }
`;

// 添加容器样式
const Container = styled.div`
  padding: 24px;
  background: linear-gradient(135deg, #f6f8fc 0%, #f0f4f9 100%);
  min-height: 100vh;
  
  @media (max-width: 768px) {
    padding: 16px;
  }

  .ant-pagination {
    display: flex;
    justify-content: center;
    margin-top: 16px;
  }

  .ant-tabs-nav {
    margin-bottom: 24px;
  }

  .ant-tabs-tab {
    font-size: 16px;
    padding: 12px 16px;
  }
`;

// 样式化卡片组件
const RankingCard = styled(Card)`
  margin-bottom: 24px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(24, 144, 255, 0.08);
  transition: all 0.3s;
  border: none;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
  width: 100%;
  
  &:hover {
    box-shadow: 0 10px 28px rgba(24, 144, 255, 0.15);
  }
  
  &:before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 5px;
    background: linear-gradient(90deg, #1890ff, #73d1ff);
    z-index: 2;
  }
  
  .ant-card-head {
    background: linear-gradient(135deg, #f8faff 0%, #ffffff 100%);
    border-bottom: 1px solid rgba(24, 144, 255, 0.1);
    padding: 0;
    min-height: 64px;
  }
  
  .ant-card-head-title {
    padding: 16px 24px;
    font-size: 18px;
    font-weight: 600;
  }
  
  .ant-card-head-wrapper {
    width: 100%;
  }
  
  .ant-card-extra {
    padding-right: 24px;
  }

  .ant-table {
    font-size: 14px;
    background: transparent;
  }
  
  .ant-table-thead > tr > th {
    background: rgba(240, 245, 255, 0.6);
    font-weight: 600;
    font-size: 14px;
    padding: 14px 16px;
    color: #1f1f1f;
    border-bottom: 1px solid rgba(24, 144, 255, 0.1);
    transition: background 0.3s;
  }
  
  .ant-table-tbody > tr > td {
    padding: 14px 16px;
    transition: background-color 0.3s;
    border-bottom: 1px solid rgba(24, 144, 255, 0.05);
  }
  
  .ant-table-tbody > tr:hover > td {
    background-color: rgba(240, 245, 255, 0.4);
  }
  
  .ant-table-row {
    transition: background-color 0.3s;
    cursor: pointer;
  }
  
  .ant-table-pagination {
    margin: 16px;
  }
  
  @media (max-width: 768px) {
    .ant-card-head-title {
      padding: 14px 16px;
      font-size: 16px;
    }
    
    .ant-table-thead > tr > th,
    .ant-table-tbody > tr > td {
      padding: 12px 12px;
      font-size: 13px;
    }
  }
`;

// 表格标题样式
const TableTitle = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  
  .left-section {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .right-section {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .icon {
    font-size: 22px;
    color: #1890ff;
    background: linear-gradient(135deg, #e6f7ff, #bae7ff);
    padding: 10px;
    border-radius: 12px;
    transition: all 0.3s;
    box-shadow: 0 2px 6px rgba(24, 144, 255, 0.15);
  }
  
  .title-text {
    font-size: 18px;
    font-weight: 600;
    color: #1f1f1f;
    background: linear-gradient(90deg, #1890ff, #69c0ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }
`;

// 操作按钮样式
const ActionButton = styled(Button)`
  margin: 0 4px;
  min-width: 100px;
  
  &.active {
    background-color: #1890ff;
    color: #fff;
    border-color: #1890ff;
    
    &:hover {
      background-color: #40a9ff;
      border-color: #40a9ff;
    }
  }
`;

// 放大悬停显示的文字样式
const HoverPopoverContent = styled.div`
  width: 350px;
  padding: 12px;
  
  .ant-timeline {
    font-size: 15px !important;
  }
  
  .ant-timeline-item-content {
    font-size: 16px !important;
    line-height: 1.5 !important;
    margin-left: 20px;
  }
  
  .action-name {
    font-size: 17px !important;
    font-weight: 600 !important;
    margin-right: 10px !important;
  }
  
  .action-time {
    font-size: 15px !important;
  }
  
  .view-more {
    font-size: 15px !important;
    font-weight: 500 !important;
    margin-top: 12px !important;
    padding-top: 8px !important;
  }
`;

const ThreadFollowList = () => {
  const [loading, setLoading] = useState(true);
  const [followedThreads, setFollowedThreads] = useState([]);
  const [myThreads, setMyThreads] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    showSizeChanger: true,
    pageSizeOptions: ['10', '20', '50'],
  });
  const { message } = App.useApp();
  const [actionLogsVisible, setActionLogsVisible] = useState(false);
  const [currentThreadId, setCurrentThreadId] = useState(null);
  const [currentThreadTitle, setCurrentThreadTitle] = useState('');

  useEffect(() => {
    fetchFollowedThreads();
    fetchMyThreads();
  }, []);

  const fetchFollowedThreads = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/thread-follows`, {
        params: { type: 'my_follow' }
      });
      setFollowedThreads(response.data.data || []);
    } catch (error) {
      console.error('获取关注帖子失败:', error);
      message.error('获取关注帖子失败');
    }
  };

  const fetchMyThreads = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/thread-follows`, {
        params: { type: 'my_thread' }
      });
      setMyThreads(response.data.data || []);
    } catch (error) {
      console.error('获取我的帖子失败:', error);
      message.error('获取我的帖子失败');
    } finally {
      setLoading(false);
    }
  };

  const handleUnfollow = async (record, type) => {
    try {
      if (!record) {
        console.error('帖子信息不存在');
        message.error('操作失败，帖子信息不存在');
        return;
      }

      // 准备请求参数
      const params = {
        type: type
      };
      
      // 根据不同类型的record构建不同的参数
      if (typeof record === 'object') {
        params.thread_id = record.thread_id;
        params.title = record.title;
        params.url = record.url;
      } else {
        // 如果只传入了字符串（可能是ID或URL）
        params.thread_id = record;
      }

      // 立即更新UI，在请求发送前先移除该项
      if (type === 'my_follow') {
        setFollowedThreads(prev => prev.filter(item => 
          !(item.thread_id === params.thread_id || 
            item.url === params.url || 
            (typeof params.url === 'string' && item.url && item.url.includes(params.url)) ||
            (typeof params.thread_id === 'string' && item.thread_id && item.thread_id.includes(params.thread_id)))
        ));
      } else {
        setMyThreads(prev => prev.filter(item => 
          !(item.thread_id === params.thread_id || 
            item.url === params.url || 
            (typeof params.url === 'string' && item.url && item.url.includes(params.url)) ||
            (typeof params.thread_id === 'string' && item.thread_id && item.thread_id.includes(params.thread_id)))
        ));
      }

      // 发送DELETE请求
      await deleteThreadFollow(params);
      
      message.success(type === 'my_follow' ? '已取消关注' : '已取消标记');
      
      // 延迟获取最新数据
      setTimeout(() => {
        // 刷新数据以确保UI与服务器状态同步
        if (type === 'my_follow') {
          fetchFollowedThreads();
        } else {
          fetchMyThreads();
        }
      }, 500);
    } catch (error) {
      console.error('取消关注/标记失败:', error);
      if (error.response && error.response.status === 404) {
        message.warning('找不到关注记录，可能已被删除');
        // 刷新数据以更新UI
        if (type === 'my_follow') {
          fetchFollowedThreads();
        } else {
          fetchMyThreads();
        }
      } else {
        message.error('操作失败，请稍后重试');
        // 恢复UI状态
        if (type === 'my_follow') {
          fetchFollowedThreads();
        } else {
          fetchMyThreads();
        }
      }
    }
  };

  // 获取徽章颜色
  const getBadgeColor = (value, field) => {
    if (value <= 0) return '#d9d9d9';
    
    switch (field) {
      case 'post_count':
        return '#555555';
      case 'repost_count':
        return '#2980B9';
      case 'reply_count':
        return '#27AE60';
      case 'delete_reply_count':
        return '#E74C3C';
      default:
        return '#1890ff';
    }
  };

  // 处理查看更新历史
  const handleViewActionLogs = (threadId, title) => {
    setCurrentThreadId(threadId);
    setCurrentThreadTitle(title);
    setActionLogsVisible(true);
  };

  // 定义基础列
  const getBaseColumns = (type) => [
    {
      title: '更新历史',
      dataIndex: 'action',
      key: 'action',
      width: 80,
      align: 'center',
      render: (_, record) => (
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <Popover
            content={
              <HoverPopoverContent>
                <HoverActionLogs 
                  url={record.url || record.thread_id} 
                  onViewMore={() => handleViewActionLogs(record.url || record.thread_id, record.title)}
                  threadId={record.thread_id}
                  title={record.title}
                  author={record.author}
                  authorLink={record.author_link}
                  repostCount={record.repost_count}
                  replyCount={record.reply_count}
                  deleteReplyCount={record.delete_reply_count}
                  daysOld={record.days_old}
                  lastActive={record.last_active}
                />
              </HoverPopoverContent>
            }
            title={<span style={{ fontSize: '18px', fontWeight: 'bold' }}>更新历史</span>}
            trigger="hover"
            placement="right"
            overlayStyle={{ 
              maxWidth: '400px',
              padding: '0'
            }}
            mouseEnterDelay={0.5}
            mouseLeaveDelay={0.2}
          >
            <div onClick={(e) => {
              e.stopPropagation();
              handleViewActionLogs(record.url || record.thread_id, record.title);
            }}>
              <UpdateHistoryButton />
            </div>
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
      render: (text, record) => (
        <StyledLink href={record.thread_id} target="_blank" rel="noopener noreferrer">
          {text}
        </StyledLink>
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
      render: (text) => (
        <Badge 
          count={text} 
          showZero 
          overflowCount={999} 
          style={{ 
            backgroundColor: getBadgeColor(text, 'repost_count'),
            fontSize: '14px',
            fontWeight: 'bold',
            padding: '0 8px'
          }} 
        />
      )
    },
    {
      title: '回帖',
      dataIndex: 'reply_count',
      key: 'reply_count',
      width: 90,
      align: 'center',
      responsive: ['sm'],
      render: (text) => (
        <Badge 
          count={text} 
          showZero 
          overflowCount={999} 
          style={{ 
            backgroundColor: getBadgeColor(text, 'reply_count'),
            fontSize: '14px',
            fontWeight: 'bold',
            padding: '0 8px'
          }} 
        />
      )
    },
    {
      title: '删回帖',
      dataIndex: 'delete_reply_count',
      key: 'delete_reply_count',
      width: 90,
      align: 'center',
      responsive: ['md'],
      render: (text) => (
        <Badge 
          count={text} 
          showZero 
          overflowCount={999} 
          style={{ 
            backgroundColor: getBadgeColor(text, 'delete_reply_count'),
            fontSize: '14px',
            fontWeight: 'bold',
            padding: '0 8px'
          }} 
        />
      )
    },
    {
      title: '帖龄',
      dataIndex: 'days_old',
      key: 'days_old',
      width: 90,
      align: 'center',
      responsive: ['lg'],
      render: (text) => <span style={{ fontSize: '14px' }}>{text}天</span>
    },
    {
      title: '活跃',
      dataIndex: 'last_active',
      key: 'last_active',
      width: 90,
      align: 'center',
      responsive: ['lg'],
      render: (text) => <span style={{ fontSize: '14px' }}>{text}天前</span>
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      align: 'center',
      fixed: 'right',
      render: (_, record) => (
        <Button 
          type="default"
          icon={type === 'my_follow' ? <HeartFilled /> : <StarFilled />}
          onClick={() => handleUnfollow(record, type)}
          style={{
            color: '#fff',
            backgroundColor: type === 'my_follow' ? '#E67E22' : '#FAAD14',
            borderColor: type === 'my_follow' ? '#E67E22' : '#FAAD14',
            margin: '0 4px',
            minWidth: '100px'
          }}
        >
          {type === 'my_follow' ? '取消关注' : '取消标记'}
        </Button>
      )
    }
  ];

  // 我的关注表格的列
  const followColumns = getBaseColumns('my_follow');
  
  // 我的帖子表格的列
  const myThreadColumns = getBaseColumns('my_thread');

  return (
    <Container>
      <RankingCard
        title={
          <TableTitle>
            <div className="left-section">
              <FireOutlined className="icon" />
              <span className="title-text">我的关注</span>
            </div>
          </TableTitle>
        }
        styles={{
          body: { padding: '0' }
        }}
      >
        <Spin spinning={loading}>
          <Table
            columns={followColumns}
            dataSource={followedThreads}
            rowKey="thread_id"
            pagination={{
              ...pagination,
              total: followedThreads.length,
              position: ['bottomCenter']
            }}
            scroll={{ x: 'max-content' }}
            size="middle"
          />
        </Spin>
      </RankingCard>

      <RankingCard
        title={
          <TableTitle>
            <div className="left-section">
              <StarOutlined className="icon" />
              <span className="title-text">我的帖子</span>
            </div>
          </TableTitle>
        }
        styles={{
          body: { padding: '0' }
        }}
      >
        <Spin spinning={loading}>
          <Table
            columns={myThreadColumns}
            dataSource={myThreads}
            rowKey="thread_id"
            pagination={{
              ...pagination,
              total: myThreads.length,
              position: ['bottomCenter']
            }}
            scroll={{ x: 'max-content' }}
            size="middle"
          />
        </Spin>
      </RankingCard>

      <Modal
        title={
          <HistoryModalTitle>
            <HistoryOutlined className="icon" />
            <span className="text">{currentThreadTitle}</span>
          </HistoryModalTitle>
        }
        open={actionLogsVisible}
        onCancel={() => setActionLogsVisible(false)}
        footer={null}
        width={800}
        styles={{
          body: {
            padding: '0',
            maxHeight: '70vh',
            overflow: 'auto'
          }
        }}
      >
        {currentThreadId && <ActionLogs url={currentThreadId} />}
      </Modal>
    </Container>
  );
};

export default ThreadFollowList; 