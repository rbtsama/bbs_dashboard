import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Spin, Typography, Button, Tooltip, App, Checkbox, Space } from 'antd';
import { HeartOutlined, HeartFilled, StarOutlined, StarFilled } from '@ant-design/icons';
import axios from 'axios';

const { Link } = Typography;

const API_BASE_URL = '/api';

const ThreadRankingTable = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);
  const [hideMyThreads, setHideMyThreads] = useState(false);
  const [rawData, setRawData] = useState([]);
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

  useEffect(() => {
    fetchData();
    fetchFollowStatus();
  }, []);

  const fetchData = async (page = 1, pageSize = 10, sortField = sorter.field, sortOrder = sorter.order) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/thread-ranking`, {
        params: { 
          page, 
          limit: pageSize,
          sort_field: sortField,
          sort_order: sortOrder === 'descend' ? 'desc' : 'asc'
        }
      });
      
      const responseData = response.data;
      const processedData = responseData.data.map(item => ({
        ...item,
        thread_id: item.thread_id || item.url,
        days_old: item.Days_Old || item.days_old || 0,
        last_active: item.Last_Active || item.last_active || 0,
        repost_count: item.Repost_Count || item.repost_count || 0,
        reply_count: item.Reply_Count || item.reply_count || 0,
        delete_count: item.Delete_Count || item.delete_count || 0,
        read_count: item.read_count || 0
      }));
      
      setRawData(processedData);
      
      // 修正过滤逻辑
      const filteredData = hideMyThreads 
        ? processedData.filter(item => followStatus[item.thread_id] !== 'my_thread')
        : processedData;
      
      setData(filteredData);
      setPagination({
        ...pagination,
        current: responseData.page || page,
        pageSize: responseData.limit || pageSize,
        total: responseData.total || 0
      });
    } catch (error) {
      console.error('获取帖子排行榜数据失败:', error);
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
          if (item && item.thread_id) {
            statusMap[item.thread_id] = 'my_follow';
          }
        });
      }
      
      // 处理 my_thread 类型的数据
      if (myThreadResponse.data.data && Array.isArray(myThreadResponse.data.data)) {
        myThreadResponse.data.data.forEach(item => {
          if (item && item.thread_id) {
            statusMap[item.thread_id] = 'my_thread';
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
      message.error('获取关注状态失败，请稍后重试');
    }
  };

  // 处理关注/取消关注
  const handleFollow = async (threadId, followType) => {
    try {
      // 检查是否已经有相同类型的关注
      const existingFollow = await axios.get(`${API_BASE_URL}/thread-follows`, {
        params: { type: followType }
      });

      const hasFollow = existingFollow.data.data && existingFollow.data.data.some(
        follow => follow.thread_id === threadId || follow.url === threadId
      );

      if (hasFollow) {
        message.info('已经关注过这个帖子了');
        return;
      }

      // 获取当前帖子的基础信息
      const currentThread = data.find(item => item.thread_id === threadId || item.url === threadId);
      if (!currentThread) {
        message.error('获取帖子信息失败');
        return;
      }

      // 获取帖子的异动日志
      let threadHistory;
      try {
        const encodedThreadId = encodeURIComponent(threadId);
        const historyResponse = await axios.get(`${API_BASE_URL}/thread-history/${encodedThreadId}`);
        threadHistory = historyResponse.data;
        console.log('获取到的帖子异动日志:', threadHistory);
      } catch (error) {
        console.error('获取帖子异动日志失败:', error);
        message.warning('获取帖子异动日志失败');
        threadHistory = [];
      }

      // 发送添加关注请求
      const response = await axios.post(`${API_BASE_URL}/thread-follows`, {
        thread_id: threadId,
        follow_type: followType,
        thread_info: {
          ...currentThread,
          url: threadId, // 确保 url 字段存在
          history: threadHistory
        }
      });
      
      if (response.data.success) {
        setFollowStatus(prev => ({
          ...prev,
          [threadId]: followType
        }));
        message.success(followType === 'my_follow' ? '已添加关注' : '已添加标记');
        // 刷新关注状态
        await fetchFollowStatus();
      } else {
        throw new Error('添加关注失败');
      }
    } catch (error) {
      console.error('关注操作失败:', error);
      message.error('关注操作失败，请稍后重试');
    }
  };

  const handleTableChange = (newPagination, filters, newSorter) => {
    // 如果排序发生变化
    if (newSorter && newSorter.field) {
      setSorter({
        field: newSorter.field,
        order: newSorter.order || 'descend'
      });
      fetchData(
        newPagination.current, 
        newPagination.pageSize, 
        newSorter.field, 
        newSorter.order || 'descend'
      );
    } else {
      // 只有分页变化
      fetchData(
        newPagination.current, 
        newPagination.pageSize, 
        sorter.field, 
        sorter.order
      );
    }
  };

  // 修改处理勾选框变化的函数
  const handleHideMyThreads = (checked) => {
    setHideMyThreads(checked);
    
    // 修正过滤逻辑
    const filteredData = checked 
      ? rawData.filter(item => followStatus[item.thread_id] !== 'my_thread')
      : rawData;
      
    setData(filteredData);
    
    // 重新获取数据，让服务器处理分页
    fetchData(1, pagination.pageSize, sorter.field, sorter.order);
  };

  const columns = [
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      width: 80,
      render: (_, __, index) => (pagination.current - 1) * pagination.pageSize + index + 1
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (text, record) => (
        <Link href={record.url} target="_blank" ellipsis>
          {text}
        </Link>
      )
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: 120,
      render: (text, record) => (
        <Link href={record.author_link} target="_blank">
          {text}
        </Link>
      )
    },
    {
      title: '阅读量',
      dataIndex: 'read_count',
      key: 'read_count',
      width: 100,
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'read_count' ? sorter.order : null
    },
    {
      title: '重发',
      dataIndex: 'repost_count',
      key: 'repost_count',
      width: 80,
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'repost_count' ? sorter.order : 'descend'
    },
    {
      title: '回帖',
      dataIndex: 'reply_count',
      key: 'reply_count',
      width: 80,
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'reply_count' ? sorter.order : null
    },
    {
      title: '删回帖',
      dataIndex: 'delete_count',
      key: 'delete_count',
      width: 80,
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'delete_count' ? sorter.order : null
    },
    {
      title: '发帖天数',
      dataIndex: 'days_old',
      key: 'days_old',
      width: 100,
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'days_old' ? sorter.order : null,
      render: (text) => text === 0 ? '未知' : `${text}天` // 当值为0时显示为"未知"
    },
    {
      title: '最近活跃',
      dataIndex: 'last_active',
      key: 'last_active',
      width: 100,
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'last_active' ? sorter.order : null,
      render: (text) => `${text || 0}天` // 添加默认值0
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record) => {
        const threadId = record.thread_id;
        if (!threadId) {
          console.warn('记录缺少 thread_id:', record);
        }
        const isMyFollow = followStatus[threadId] === 'my_follow';
        const isMyThread = followStatus[threadId] === 'my_thread';
        
        return (
          <div style={{ display: 'flex', gap: '8px' }}>
            <Tooltip title={isMyFollow ? '取消关注' : '添加关注'}>
              <Button
                type={isMyFollow ? 'primary' : 'default'}
                icon={isMyFollow ? <HeartFilled /> : <HeartOutlined />}
                onClick={() => handleFollow(threadId, 'my_follow')}
                disabled={!threadId}
                style={{
                  width: '88px',
                  backgroundColor: isMyFollow ? '#52c41a' : 'transparent',
                  borderColor: isMyFollow ? '#52c41a' : '#d9d9d9',
                  color: isMyFollow ? 'white' : 'rgba(0, 0, 0, 0.45)',
                }}
                className="follow-button"
              >
                {isMyFollow ? '已关注' : '添加关注'}
              </Button>
            </Tooltip>
            <Tooltip title={isMyThread ? '取消标记' : '添加到我的帖子'}>
              <Button
                type={isMyThread ? 'primary' : 'default'}
                icon={isMyThread ? <StarFilled /> : <StarOutlined />}
                onClick={() => handleFollow(threadId, 'my_thread')}
                disabled={!threadId}
                style={{
                  width: '88px',
                  backgroundColor: isMyThread ? '#fa8c16' : 'transparent',
                  borderColor: isMyThread ? '#fa8c16' : '#d9d9d9',
                  color: isMyThread ? 'white' : 'rgba(0, 0, 0, 0.45)',
                }}
                className="follow-button"
              >
                {isMyThread ? '已标记' : '我的帖子'}
              </Button>
            </Tooltip>
          </div>
        );
      }
    }
  ];

  return (
    <>
      <Card 
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>帖子排行榜</span>
            <Checkbox 
              checked={hideMyThreads}
              onChange={(e) => handleHideMyThreads(e.target.checked)}
              style={{ color: '#1890ff' }}
              className="blue-checkbox"
            >
              不看我的帖子
            </Checkbox>
          </div>
        } 
        style={{ marginTop: 16 }}
      >
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={data}
            rowKey="id"
            pagination={pagination}
            onChange={handleTableChange}
            scroll={{ x: 'max-content' }}
          />
        </Spin>
      </Card>
      <style>{`
        .follow-button:hover {
          opacity: 0.85;
        }
        .follow-button:hover:not(.ant-btn-primary) {
          color: rgba(0, 0, 0, 0.85);
        }
        .blue-checkbox .ant-checkbox-checked .ant-checkbox-inner {
          background-color: #1890ff;
          border-color: #1890ff;
        }
        .blue-checkbox .ant-checkbox-wrapper:hover .ant-checkbox-inner,
        .blue-checkbox .ant-checkbox:hover .ant-checkbox-inner {
          border-color: #1890ff;
        }
      `}</style>
    </>
  );
};

export default ThreadRankingTable; 