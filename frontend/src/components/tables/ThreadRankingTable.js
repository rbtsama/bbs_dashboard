import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Spin, Typography, Button, Tooltip, App, Checkbox, Space, Badge, ConfigProvider, Popover, Modal } from 'antd';
import { HeartOutlined, HeartFilled, StarOutlined, StarFilled, FireOutlined, TrophyOutlined, HistoryOutlined, ClockCircleOutlined, UserOutlined, LinkOutlined, CrownOutlined, EyeOutlined, CommentOutlined, CalendarOutlined, UserSwitchOutlined } from '@ant-design/icons';
import axios from 'axios';
import styled from 'styled-components';
import ActionLogs, { HoverActionLogs } from '../ActionLogs';
import dayjs from 'dayjs';
import { UpdateHistoryButton } from '../HistoryButton';
import { UpdateHistoryModal } from '../HistoryModal';
import { HistoryModalTitle } from '../HistoryButton';
import { API_BASE_URL } from '../../config';
import { deleteThreadFollow } from '../../services/api';

const { Link } = Typography;

// 格式化日期函数
const formatDate = (timestamp) => {
  if (!timestamp) return '未知';
  
  // 如果是数字（天数），直接返回
  if (typeof timestamp === 'number') {
    return `${timestamp}天前`;
  }
  
  try {
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) return '无效日期';
    
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    console.error('日期格式化错误:', error);
    return '格式错误';
  }
};

// 添加容器样式
const Container = styled.div`
  padding: 0;
  width: 100%;
  
  .ant-pagination {
    display: flex;
    justify-content: center;
    margin-top: 12px;
  }
`;

// 样式化卡片组件
const RankingCard = styled(Card)`
  margin: 0;
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
    
    &:hover {
      transform: scale(1.08) rotate(5deg);
      background: linear-gradient(135deg, #bae7ff, #91d5ff);
    }
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

// 排名样式
const RankNumber = styled.div`
  font-size: 15px;
  font-weight: 600;
  padding: 0 10px;
  color: #262626;
  display: inline-flex;
  align-items: center;
  justify-content: center;
`;

// 样式化链接
const StyledLink = styled(Link)`
  font-size: 14px;
  font-weight: 500;
  color: #1890ff;
  transition: color 0.3s;
  
  &:hover {
    color: #40a9ff;
    text-decoration: underline;
  }
`;

// 操作按钮样式
const ActionButton = styled(Button)`
  margin: 0 4px;
  min-width: 90px;
  height: 32px;
  border-radius: 6px;
  font-size: 14px;
  
  &.follow-btn {
    background-color: ${props => props.followed ? '#f0f0f0' : '#1890ff'};
    color: ${props => props.followed ? '#666' : '#fff'};
    border-color: ${props => props.followed ? '#d9d9d9' : '#1890ff'};
    
    &:hover {
      background-color: ${props => props.followed ? '#e8e8e8' : '#40a9ff'};
      border-color: ${props => props.followed ? '#d9d9d9' : '#40a9ff'};
      color: ${props => props.followed ? '#666' : '#fff'};
    }
  }
  
  &.hide-btn {
    background-color: ${props => props.hidden ? '#fff1f0' : '#fff'};
    color: ${props => props.hidden ? '#ff4d4f' : '#666'};
    border-color: ${props => props.hidden ? '#ffa39e' : '#d9d9d9'};
    
    &:hover {
      background-color: ${props => props.hidden ? '#fff1f0' : '#fff'};
      color: ${props => props.hidden ? '#ff7875' : '#40a9ff'};
      border-color: ${props => props.hidden ? '#ff7875' : '#40a9ff'};
    }
  }

  &.active {
    background-color: ${props => props.type === 'my_posts' ? '#E67E22' : '#1890ff'};
    color: #fff;
    border-color: ${props => props.type === 'my_posts' ? '#E67E22' : '#1890ff'};
    
    &:hover {
      background-color: ${props => props.type === 'my_posts' ? '#F39C12' : '#40a9ff'};
      border-color: ${props => props.type === 'my_posts' ? '#F39C12' : '#40a9ff'};
    }
  }
  
  @media (max-width: 768px) {
    min-width: 80px;
    height: 28px;
    font-size: 13px;
  }
`;

// 过滤选项复选框
const FilterCheckbox = styled(Checkbox)`
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  
  .ant-checkbox-wrapper:hover .ant-checkbox-inner, 
  .ant-checkbox:hover .ant-checkbox-inner, 
  .ant-checkbox-input:focus + .ant-checkbox-inner {
    border-color: #1890ff;
  }
  
  .ant-checkbox-checked .ant-checkbox-inner {
    background-color: #1890ff;
    border-color: #1890ff;
  }
  
  @media (max-width: 768px) {
    font-size: 13px;
  }
`;

// 添加全局样式
const globalStyles = `
  .thread-ranking-table .even-row {
    background-color: #ffffff;
  }
  
  .thread-ranking-table .odd-row {
    background-color: #fafafa;
  }
  
  .thread-ranking-table .ant-table-cell {
    transition: all 0.3s;
  }
  
  @media (max-width: 576px) {
    .thread-ranking-table .ant-table-cell {
      padding: 8px 4px !important;
    }
  }
`;

// 悬停弹窗内容样式
const HoverPopoverContent = styled.div`
  width: 350px;
  padding: 12px;
`;

const ThreadRankingTable = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    showSizeChanger: true
  });
  const [sorter, setSorter] = useState({
    field: 'repost_count',
    order: 'descend'
  });
  const { message } = App.useApp();

  // 添加关注状态
  const [followStatus, setFollowStatus] = useState({});

  // 添加状态管理操作日志显示
  const [actionLogsVisible, setActionLogsVisible] = useState(false);
  const [currentThreadId, setCurrentThreadId] = useState(null);
  const [currentUrl, setCurrentUrl] = useState(null);
  const [currentThread, setCurrentThread] = useState(null);

  const [filteredData, setFilteredData] = useState([]);
  const [activeFilters, setActiveFilters] = useState([]);

  useEffect(() => {
    console.log('组件加载，获取数据...');
    fetchData();
    // 获取关注状态
    fetchFollowStatus();
  }, []);

  // 处理表格变化（分页、筛选、排序）
  const handleTableChange = (newPagination, filters, newSorter) => {
    console.log('表格变化:', { newPagination, filters, newSorter });
    
    // 更新排序状态
    if (newSorter && newSorter.field) {
        console.log(`排序变更为: ${newSorter.field} ${newSorter.order || 'descend'}`);
        
        // 确保排序字段与后端匹配
        const sortFieldMap = {
            'repost_count': 'repost_count',
            'reply_count': 'reply_count',
            'delete_reply_count': 'delete_reply_count',
            'daysold': 'daysold',
            'last_active': 'last_active',
            'author': 'author',
            'title': 'title'
        };
        
        const mappedField = sortFieldMap[newSorter.field] || 'repost_count';
        
        // 更新排序状态
        setSorter({
            field: mappedField,
            order: newSorter.order || 'descend'
        });
        
        // 重新请求数据
        fetchData(
            newPagination.current, 
            newPagination.pageSize, 
            mappedField, 
            newSorter.order || 'descend'
        );
        return;
    }
    
    // 如果页码或每页数量变化，重新请求数据
    if (newPagination.current !== pagination.current || 
        newPagination.pageSize !== pagination.pageSize) {
        console.log(`分页变更为: 页码=${newPagination.current}, 每页=${newPagination.pageSize}`);
        fetchData(
            newPagination.current, 
            newPagination.pageSize, 
            sorter.field, 
            sorter.order
        );
    }
  };

  // 优化fetchData函数，确保正确处理API响应
  const fetchData = async (page = 1, pageSize = 10, sortField = sorter.field, sortOrder = sorter.order) => {
    setLoading(true);
    try {
      console.log(`正在获取帖子排行榜数据: 页码=${page}, 每页=${pageSize}, 排序字段=${sortField}, 排序方式=${sortOrder}`);
      
      // 确保排序参数正确
      const apiSortOrder = sortOrder === 'descend' ? 'desc' : 
                          sortOrder === 'ascend' ? 'asc' : 'desc';
      
      const response = await axios.get(`${API_BASE_URL}/post-rank`, {
        params: { 
          page, 
          limit: pageSize,
          sort_field: sortField,
          sort_order: apiSortOrder
        }
      });
      
      const responseData = response.data;
      console.log('API返回原始数据:', responseData);
      
      // 检查返回的数据结构
      if (!responseData || !responseData.data || !Array.isArray(responseData.data)) {
        console.error('API返回格式错误:', responseData);
        setData([]);
        setFilteredData([]);
        setPagination(prev => ({
          ...prev,
          current: page,
          pageSize: pageSize,
          total: 0
        }));
        setLoading(false);
        return;
      }
      
      // 只添加key字段，确保每条记录都有唯一key
      const processedData = responseData.data.map(item => ({
        ...item,
        key: item.thread_id || item.url || `${Math.random()}`
      }));
      
      console.log('处理后的数据:', processedData);
      console.log(`返回的总记录数: ${responseData.total}`);
      console.log(`当前页码: ${responseData.page}`);
      console.log(`每页大小: ${responseData.limit}`);
      
      // 更新组件状态
      setData(processedData);
      setFilteredData(processedData);
      setPagination(prev => ({
        ...prev,
        current: parseInt(responseData.page) || page,
        pageSize: parseInt(responseData.limit) || pageSize,
        total: parseInt(responseData.total) || 0
      }));
    } catch (error) {
      console.error('获取帖子排行榜数据失败:', error);
      if (error.response) {
        console.error('错误响应:', error.response.data);
      }
      message.error('获取数据失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 获取关注状态
  const fetchFollowStatus = async () => {
    try {
      console.log('开始获取关注状态...');
      // 获取两种类型的关注状态
      const [myFollowResponse, myThreadResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/thread-follows`, { params: { type: 'my_follow' } }),
        axios.get(`${API_BASE_URL}/thread-follows`, { params: { type: 'my_thread' } })
      ]);
      
      console.log('获取到的关注数据:', {
        my_follow: myFollowResponse.data,
        my_thread: myThreadResponse.data
      });
      
      const statusMap = {};
      // 处理 my_follow 类型的数据
      if (myFollowResponse.data.data && Array.isArray(myFollowResponse.data.data)) {
        myFollowResponse.data.data.forEach(item => {
          if (item) {
            // 尝试多种可能的ID字段
            const threadId = item.thread_id || (item.thread_info && item.thread_info.url) || item.url;
            if (threadId) {
              statusMap[threadId] = 'my_follow';
              console.log(`设置关注状态: ${threadId} => my_follow`);
            }
          }
        });
      }
      
      // 处理 my_thread 类型的数据
      if (myThreadResponse.data.data && Array.isArray(myThreadResponse.data.data)) {
        myThreadResponse.data.data.forEach(item => {
          if (item) {
            // 尝试多种可能的ID字段
            const threadId = item.thread_id || (item.thread_info && item.thread_info.url) || item.url;
            if (threadId) {
              statusMap[threadId] = 'my_thread';
              console.log(`设置关注状态: ${threadId} => my_thread`);
            }
          }
        });
      }
      
      console.log('处理后的关注状态:', statusMap);
      setFollowStatus(statusMap);
    } catch (error) {
      console.error('获取关注状态失败:', error);
      if (error.response) {
        console.error('错误响应:', error.response.data);
      }
      message.error('获取关注状态失败');
    }
  };

  // 处理关注/取消关注
  const handleFollow = async (threadId, followType) => {
    try {
      // 直接使用本地状态检查是否已关注
      const currentStatus = followStatus[threadId];
      const isCurrentType = currentStatus === followType;

      if (isCurrentType) {
        // 如果当前已经是这个类型的关注，则执行取消关注操作
        await deleteThreadFollow({
          thread_id: threadId,
          type: followType
        });
        
        setFollowStatus(prev => {
          const newStatus = { ...prev };
          delete newStatus[threadId];
          return newStatus;
        });
        
        message.success(followType === 'my_follow' ? '已取消关注' : '已取消标记');
        return;
      }

      // 如果已经在另一个列表中
      const inOtherList = currentStatus && currentStatus !== followType;
      const otherType = followType === 'my_follow' ? 'my_thread' : 'my_follow';

      // 如果在另一个列表中，先删除
      if (inOtherList) {
        try {
          await deleteThreadFollow({
            thread_id: threadId,
            type: otherType
          });
          console.log(`已从${otherType}列表中移除`);
        } catch (error) {
          console.error(`从${otherType}列表中移除失败:`, error);
        }
      }

      // 发送添加关注请求
      await axios.post(`${API_BASE_URL}/thread-follows`, {
        thread_id: threadId,
        type: followType
      });
      
      // 更新关注状态
      setFollowStatus(prev => ({
        ...prev,
        [threadId]: followType
      }));
      
      message.success(followType === 'my_follow' ? '已关注' : '已标记');
    } catch (error) {
      console.error('关注操作失败:', error);
      message.error('操作失败，请稍后重试');
    }
  };

  // 查看操作日志的处理函数
  const handleViewActionLogs = useCallback((record) => {
    // 确保正确保存当前线程ID、URL和线程对象
    setCurrentThreadId(record.thread_id);
    setCurrentUrl(record.url || record.threadUrl);
    setCurrentThread(record);
    setActionLogsVisible(true);
  }, []);

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

  // 渲染数值徽章，确保正确显示数值
  const renderNumberBadge = (value, fieldName) => {
    // 确保值是数字
    const numValue = parseInt(value, 10) || 0;
    
    return (
      <span 
        style={{ 
          backgroundColor: getBadgeColor(numValue, fieldName),
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

  const renderRankColumn = (text, record, index) => {
    const rank = record.rank || index + 1;
    return <RankNumber>{rank}</RankNumber>;
  };

  const columns = [
    {
      title: '更新历史',
      key: 'action_logs',
      width: 100,
      align: 'center',
      render: (_, record) => (
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <Popover
            content={
              <HoverPopoverContent>
                <HoverActionLogs 
                  threadId={record.thread_id} 
                  url={record.url} 
                  title={record.title}
                  author={record.author}
                  authorLink={record.author_link}
                  repostCount={record.repost_count || 0}
                  replyCount={record.reply_count || 0}
                  deleteReplyCount={record.delete_reply_count || 0}
                  daysOld={record.daysold || 0}
                  lastActive={record.last_active || 0}
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
              <UpdateHistoryButton onClick={() => handleViewActionLogs(record)} />
            </span>
          </Popover>
        </div>
      )
    },
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      width: 80,
      align: 'center',
      fixed: 'left',
      render: renderRankColumn
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
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'repost_count' ? sorter.order : 'descend',
      render: (text) => renderNumberBadge(text, 'repost_count')
    },
    {
      title: '回帖',
      dataIndex: 'reply_count',
      key: 'reply_count',
      width: 90,
      align: 'center',
      responsive: ['sm'],
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'reply_count' ? sorter.order : null,
      render: (text) => renderNumberBadge(text, 'reply_count')
    },
    {
      title: '删回帖',
      dataIndex: 'delete_reply_count',
      key: 'delete_reply_count',
      width: 90,
      align: 'center',
      responsive: ['md'],
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'delete_reply_count' ? sorter.order : null,
      render: (text) => renderNumberBadge(text, 'delete_reply_count')
    },
    {
      title: '帖龄',
      dataIndex: 'daysold',
      key: 'daysold',
      width: 90,
      align: 'center',
      responsive: ['lg'],
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'daysold' ? sorter.order : null,
      render: (text) => <span style={{ fontSize: '14px' }}>{text}天</span>
    },
    {
      title: '活跃',
      dataIndex: 'last_active',
      key: 'last_active',
      width: 90,
      align: 'center',
      responsive: ['lg'],
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'last_active' ? sorter.order : null,
      render: (text) => <span style={{ fontSize: '14px' }}>{text}天前</span>
    },
    {
      title: '关注',
      key: 'follow_status',
      width: 90,
      align: 'center',
      filters: [
        { text: '关注中', value: 'my_follow' },
        { text: '我的', value: 'my_thread' },
        { text: '未关注', value: 'none' }
      ],
      filterMultiple: true,
      render: (_, record) => {
        const status = followStatus[record.thread_id];
        if (!status) return '';
        return (
          <span style={{ 
            color: status === 'my_follow' ? '#27AE60' : '#E67E22',
            fontWeight: 500
          }}>
            {status === 'my_follow' ? '关注中' : '我的'}
          </span>
        );
      }
    },
    {
      title: '操作',
      key: 'action',
      width: 220,
      align: 'center',
      fixed: 'right',
      render: (_, record) => {
        const threadId = record.thread_id;
        const isFollowed = followStatus[threadId] === 'my_follow';
        const isMine = followStatus[threadId] === 'my_thread';
        
        return (
          <Space size="small" style={{ whiteSpace: 'nowrap' }}>
            <Button
              type="default"
              icon={isFollowed ? <HeartFilled /> : <HeartOutlined />}
              onClick={() => handleFollow(threadId, 'my_follow')}
              style={{
                color: isFollowed ? '#fff' : '#2C3E50',
                backgroundColor: isFollowed ? '#27AE60' : '',
                borderColor: isFollowed ? '#27AE60' : '#2C3E50',
                margin: '0 4px',
                minWidth: '100px'
              }}
              size="middle"
            >
              {isFollowed ? '取消关注' : '关注'}
            </Button>
            <Button
              type="default"
              icon={isMine ? <StarFilled /> : <StarOutlined />}
              onClick={() => handleFollow(threadId, 'my_thread')}
              style={{
                color: isMine ? '#fff' : '#2C3E50',
                backgroundColor: isMine ? '#E67E22' : '',
                borderColor: isMine ? '#E67E22' : '#2C3E50',
                margin: '0 4px',
                minWidth: '100px'
              }}
              size="middle"
            >
              {isMine ? '取消' : '我的'}
            </Button>
          </Space>
        );
      }
    }
  ];

  // 自定义标题
  const title = (
    <TableTitle>
      <div className="left-section">
        <FireOutlined className="icon" />
        <span className="title-text">帖子排行榜</span>
      </div>
    </TableTitle>
  );

  return (
    <Container>
      <RankingCard 
        title={title} 
        styles={{
          body: { padding: '0' }
        }}
      >
        <ConfigProvider
          theme={{
            components: {
              Table: {
                borderColor: '#f0f0f0',
                headerBg: '#fafafa',
                headerColor: 'rgba(0, 0, 0, 0.85)',
                headerSplitColor: '#f0f0f0',
                rowHoverBg: '#e6f7ff',
                padding: 12,
                paddingXS: 8,
                paddingLG: 16,
              },
              Pagination: {
                colorBgContainer: '#ffffff',
                colorPrimary: '#1890ff',
                colorPrimaryHover: '#40a9ff',
                colorText: 'rgba(0, 0, 0, 0.88)',
                colorTextDisabled: 'rgba(0, 0, 0, 0.25)',
                controlHeight: 32,
                fontSizeSM: 14,
                itemActiveBg: '#1890ff',
                itemSize: 32,
                colorTextItemSelected: '#ffffff',
                colorBgTextHover: '#e6f4ff',
                colorBgTextActive: '#1890ff',
                colorTextActive: '#ffffff'
              },
            },
          }}
        >
          <style>{globalStyles}</style>
          <Spin spinning={loading}>
            <Table
              columns={columns}
              dataSource={filteredData}
              rowKey="thread_id"
              pagination={{
                ...pagination,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条记录`,
                position: ['bottomCenter'],
                responsive: true,
              }}
              onChange={handleTableChange}
              scroll={{ x: 'max-content' }}
              size="middle"
              rowClassName={(record, index) => index % 2 === 0 ? 'even-row' : 'odd-row'}
              tableLayout="fixed"
              className="thread-ranking-table"
            />
          </Spin>
        </ConfigProvider>
      </RankingCard>

      {/* 添加操作日志弹窗 */}
      <UpdateHistoryModal
        visible={actionLogsVisible}
        onCancel={() => setActionLogsVisible(false)}
        title={
          <HistoryModalTitle>
            <HistoryOutlined className="icon" />
            <span className="text">更新历史</span>
          </HistoryModalTitle>
        }
      >
        <ActionLogs threadId={currentThreadId} url={currentUrl} />
      </UpdateHistoryModal>
    </Container>
  );
};

export default ThreadRankingTable; 