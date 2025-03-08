import React, { useState, useEffect, useCallback } from 'react';
import { Table, Avatar, Input, App } from 'antd';
import { fetchUserActivity } from '../services/api';

// 备用模拟数据，仅在 API 调用失败时使用
const mockData = Array.from({ length: 20 }, (_, i) => ({
  id: `user_${i + 1}`,
  username: `用户${i + 1}`,
  userUrl: `https://example.com/user/${i + 1}`,
  totalPosts: Math.floor(Math.random() * 200) + 10,
  repostCount: Math.floor(Math.random() * 100) + 5,
  lastActiveTime: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
  avatar: `https://randomuser.me/api/portraits/men/${i + 1}.jpg`,
  rank: i + 1,
  userLevel: Math.min(10, 1 + Math.floor(Math.random() * 10))
}));

const UserRankingTable = () => {
  const [tableData, setTableData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [searchText, setSearchText] = useState('');
  const { message: messageApi } = App.useApp();
  
  const fetchData = useCallback(async (page = 1, pageSize = 10, search = '') => {
    if (loading) return; // 防止重复请求
    
    setLoading(true);
    try {
      const data = await fetchUserActivity();
      const realData = data && Array.isArray(data) && data.length > 0 ? data : mockData;
      const filteredData = search 
        ? realData.filter(item => 
            item.username && item.username.toLowerCase().includes(search.toLowerCase())
          )
        : realData;
      
      setTableData(filteredData);
      setPagination(prev => ({
        ...prev,
        current: page,
        pageSize,
        total: filteredData.length
      }));
    } catch (error) {
      console.error('加载用户排行榜失败:', error);
      messageApi.error('加载用户排行榜失败，使用模拟数据');
      setTableData(mockData);
      setPagination(prev => ({
        ...prev,
        current: page,
        pageSize,
        total: mockData.length
      }));
    } finally {
      setLoading(false);
    }
  }, [messageApi]); // 只依赖messageApi
  
  useEffect(() => {
    fetchData(pagination.current, pagination.pageSize, searchText);
  }, []); // 只在组件挂载时执行一次
  
  const handleTableChange = (paginationInfo) => {
    setPagination(paginationInfo);
  };
  
  const handleSearch = (value) => {
    setSearchText(value);
    fetchData(1, pagination.pageSize, value);
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
    { title: '发帖数', dataIndex: 'totalPosts', key: 'totalPosts', sorter: true },
    { title: '重发次数', dataIndex: 'repostCount', key: 'repostCount', sorter: true },
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
        rowKey="id"
      />
    </div>
  );
};

export default UserRankingTable; 