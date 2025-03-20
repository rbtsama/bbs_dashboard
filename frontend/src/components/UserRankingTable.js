import React, { useState, useEffect, useCallback } from 'react';
import { Table, Avatar, Input, App, Popover, Modal } from 'antd';
import { ClockCircleOutlined } from '@ant-design/icons';
import { fetchAuthorRank } from '../services/api';
import styled from 'styled-components';
import { HoverActionLogs } from './ActionLogs';

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

// 科技感时光机按钮 - 红色版本
const TimeMachineButton = styled.div`
  width: 48px;
  height: 48px;
  position: relative;
  cursor: pointer;
  transition: all 0.5s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    transform: scale(1.1);
  }
  
  &:active {
    transform: scale(0.95);
  }
  
  .outer-ring {
    position: absolute;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    border: 2px solid #F43F5E;
    box-shadow: 0 0 15px #F43F5E, inset 0 0 8px #F43F5E;
    animation: rotate 10s linear infinite;
  }
  
  .middle-ring {
    position: absolute;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    border: 1px dashed rgba(255, 99, 99, 0.8);
    animation: rotate 7s linear infinite reverse;
  }
  
  .inner-circle {
    position: absolute;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #F43F5E, #FF5757);
    box-shadow: 0 0 10px rgba(255, 87, 87, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }
  
  .inner-circle::before {
    content: '';
    position: absolute;
    width: 150%;
    height: 150%;
    background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.5), transparent);
    transform: rotate(45deg) translate(-50%, -50%);
    animation: shine 3s linear infinite;
  }
  
  .time-icon {
    font-size: 18px;
    color: white;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
    position: relative;
    z-index: 2;
  }
  
  .particles {
    position: absolute;
    width: 100%;
    height: 100%;
    pointer-events: none;
  }
  
  .particle {
    position: absolute;
    width: 3px;
    height: 3px;
    background: white;
    border-radius: 50%;
    opacity: 0;
    animation: particle 2s cubic-bezier(0.175, 0.885, 0.32, 1.275) infinite;
  }
  
  .particle:nth-child(1) {
    top: 20%;
    left: 60%;
    animation-delay: 0s;
  }
  
  .particle:nth-child(2) {
    top: 60%;
    left: 20%;
    animation-delay: 0.3s;
  }
  
  .particle:nth-child(3) {
    top: 40%;
    left: 70%;
    animation-delay: 0.6s;
  }
  
  .particle:nth-child(4) {
    top: 70%;
    left: 40%;
    animation-delay: 0.9s;
  }
  
  .particle:nth-child(5) {
    top: 30%;
    left: 30%;
    animation-delay: 1.2s;
  }
  
  @keyframes shine {
    0% {
      transform: rotate(45deg) translate(-50%, -50%);
    }
    100% {
      transform: rotate(45deg) translate(150%, 150%);
    }
  }
  
  @keyframes rotate {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
  
  @keyframes particle {
    0% {
      transform: scale(0);
      opacity: 0;
    }
    20% {
      opacity: 1;
    }
    80% {
      transform: scale(2);
      opacity: 0;
    }
    100% {
      transform: scale(3);
      opacity: 0;
    }
  }
`;

const UserRankingTable = () => {
  const [tableData, setTableData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [searchText, setSearchText] = useState('');
  const [actionLogsVisible, setActionLogsVisible] = useState(false);
  const [currentUsername, setCurrentUsername] = useState('');
  const { message: messageApi } = App.useApp();
  
  const fetchData = useCallback(async (page = 1, pageSize = 10, search = '') => {
    if (loading) return; // 防止重复请求
    
    setLoading(true);
    try {
      const response = await fetchAuthorRank(page, pageSize);
      
      if (response && response.data && Array.isArray(response.data) && response.data.length > 0) {
        // 处理从import表获取的数据
        const formattedData = response.data.map((item, index) => ({
          id: item.id || item.author_id || `user_${index}_${new Date().getTime()}`,
          username: item.author || '未知用户',
          userUrl: item.author_id ? `https://example.com/user/${item.author_id}` : '#',
          totalPosts: item.post_count || 0,
          repostCount: item.repost_count || 0,
          activePosts: item.active_posts || 0,
          lastActiveTime: item.datetime || '',
          avatar: `https://randomuser.me/api/portraits/men/${index % 30 + 1}.jpg`,
          rank: index + 1 + (page - 1) * pageSize,
          userLevel: Math.min(10, 1 + Math.floor(Math.random() * 10))
        }));
        
        const filteredData = search 
          ? formattedData.filter(item => 
              item.username && item.username.toLowerCase().includes(search.toLowerCase())
            )
          : formattedData;
        
        setTableData(filteredData);
        setPagination(prev => ({
          ...prev,
          current: page,
          pageSize,
          total: response.total || filteredData.length
        }));
      } else {
        setTableData([]);
        setPagination(prev => ({
          ...prev,
          current: page,
          pageSize,
          total: 0
        }));
      }
    } catch (error) {
      console.error('获取用户排行榜失败:', error);
      messageApi.error('获取用户排行榜失败');
      setTableData([]);
      setPagination(prev => ({
        ...prev, 
        current: page,
        pageSize,
        total: 0
      }));
    } finally {
      setLoading(false);
    }
  }, [loading, messageApi]);
  
  useEffect(() => {
    fetchData(pagination.current, pagination.pageSize, searchText);
  }, []); // 只在组件挂载时执行一次
  
  const handleTableChange = (paginationInfo, filters, sorter) => {
    setPagination(paginationInfo);
    fetchData(
      paginationInfo.current, 
      paginationInfo.pageSize, 
      searchText
    );
  };
  
  const handleSearch = (value) => {
    setSearchText(value);
    fetchData(1, pagination.pageSize, value);
  };
  
  const handleViewActionLogs = (username) => {
    setCurrentUsername(username);
    setActionLogsVisible(true);
  };
  
  const columns = [
    { title: '排名', dataIndex: 'rank', key: 'rank', width: 80 },
    { 
      title: '用户', 
      key: 'user',
      render: (_, record) => (
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Avatar src={record.avatar} size="small" style={{ marginRight: 8 }} />
          <a href={record.userUrl} target="_blank" rel="noopener noreferrer">
            {record.username}
          </a>
        </div>
      )
    },
    { title: '等级', dataIndex: 'userLevel', key: 'userLevel' },
    { title: '发帖数', dataIndex: 'totalPosts', key: 'totalPosts' },
    { title: '活跃帖数', dataIndex: 'activePosts', key: 'activePosts' },
    {
      title: '发帖异动',
      key: 'postChanges',
      width: 120,
      align: 'center',
      render: (_, record) => {
        // 计算历史贴数与活跃贴数的差值
        const inactivePosts = record.totalPosts - record.activePosts;
        
        // 只有当差值大于0时才显示按钮
        if (inactivePosts > 0) {
          return (
            <div style={{ display: 'flex', justifyContent: 'center', paddingLeft: '16px' }}>
              <Popover
                content={
                  <HoverPopoverContent>
                    <div style={{ padding: '10px', textAlign: 'center' }}>
                      <p style={{ fontSize: '18px', fontWeight: 'bold' }}>
                        该用户有 {inactivePosts} 个帖子已不再活跃
                      </p>
                      <p>历史发帖: {record.totalPosts}</p>
                      <p>当前活跃: {record.activePosts}</p>
                    </div>
                  </HoverPopoverContent>
                }
                title={<span style={{ fontSize: '18px', fontWeight: 'bold' }}>发帖异动记录</span>}
                trigger="hover"
                placement="right"
                overlayStyle={{ maxWidth: '400px' }}
              >
                <TimeMachineButton onClick={() => handleViewActionLogs(record.username)}>
                  <div className="outer-ring"></div>
                  <div className="middle-ring"></div>
                  <div className="inner-circle">
                    <ClockCircleOutlined className="time-icon" />
                  </div>
                  <div className="particles">
                    <div className="particle"></div>
                    <div className="particle"></div>
                    <div className="particle"></div>
                    <div className="particle"></div>
                    <div className="particle"></div>
                  </div>
                </TimeMachineButton>
              </Popover>
            </div>
          );
        }
        
        // 如果差值不大于0，则不显示任何内容
        return null;
      }
    },
    { title: '重发次数', dataIndex: 'repostCount', key: 'repostCount' },
    { title: '最后活跃时间', dataIndex: 'lastActiveTime', key: 'lastActiveTime' }
  ];
  
  return (
    <div className="ranking-table">
      <h2>用户排行榜</h2>
      <Input.Search 
        placeholder="搜索用户" 
        onSearch={handleSearch}
        style={{ marginBottom: 16 }} 
      />
      <Table 
        columns={columns} 
        dataSource={tableData}
        loading={loading}
        pagination={pagination}
        onChange={handleTableChange}
        rowKey={record => record.id || record.username || String(record.rank)}
      />
      
      <Modal
        title={`${currentUsername} 的发帖异动记录`}
        open={actionLogsVisible}
        onCancel={() => setActionLogsVisible(false)}
        footer={null}
        width={700}
      >
        <div style={{ padding: '20px' }}>
          <p style={{ fontSize: '16px', marginBottom: '20px' }}>
            该功能展示用户帖子的异动情况，包括帖子不再活跃、被删除或被隐藏的情况。
          </p>
          {/* 这里可以添加更详细的异动记录展示 */}
          <div style={{ textAlign: 'center', padding: '30px' }}>
            <p style={{ fontSize: '18px', fontWeight: 'bold' }}>
              详细异动记录功能正在开发中...
            </p>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default UserRankingTable; 