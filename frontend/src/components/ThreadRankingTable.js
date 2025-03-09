import React, { useState, useEffect, useCallback } from 'react';
import { Table, Button, Input, App } from 'antd';
import { useDispatch } from 'react-redux';
import { followThread } from '../redux/actions';
import { fetchThreadRanking } from '../services/api';

// 备用模拟数据，仅在 API 调用失败时使用
const mockData = Array.from({ length: 20 }, (_, i) => ({
  id: `thread_${i + 1}`,
  thread_id: `${i + 1}`,
  title: `这是一个示例帖子标题 ${i + 1}`,
  author: `作者${i + 1}`,
  authorUrl: `https://example.com/user/${i + 1}`,
  forum: `板块${i % 5 + 1}`,
  viewCount: Math.floor(Math.random() * 10000) + 100,
  pageNum: Math.floor(Math.random() * 20) + 1,
  num: Math.floor(Math.random() * 100) + 1,
  repostCount: Math.floor(Math.random() * 50) + 1,
  lastUpdateTime: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
  threadUrl: `https://example.com/thread/${i + 1}`,
  rank: i + 1
}));

const ThreadRankingTable = () => {
  const [tableData, setTableData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [searchText, setSearchText] = useState('');
  const dispatch = useDispatch();
  const { message } = App.useApp();
  
  const fetchData = useCallback(async (page = 1, pageSize = 10, search = '') => {
    if (loading) return; // 防止重复请求
    
    setLoading(true);
    try {
      const data = await fetchThreadRanking();
      const realData = data && Array.isArray(data) && data.length > 0 ? data : mockData;
      const filteredData = search 
        ? realData.filter(item => 
            (item.title && item.title.toLowerCase().includes(search.toLowerCase())) || 
            (item.author && item.author.toLowerCase().includes(search.toLowerCase()))
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
      console.error('加载帖子排行榜失败:', error);
      message.error('加载帖子排行榜失败，使用模拟数据');
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
  }, [message]); // 只依赖message
  
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
  
  const handleFollow = (record) => {
    dispatch(followThread(record));
    message.success(`已关注帖子: ${record.title}`);
  };
  
  const columns = [
    { title: '排名', dataIndex: 'rank', key: 'rank', width: 80 },
    { 
      title: '帖子标题', 
      dataIndex: 'title', 
      key: 'title', 
      ellipsis: true,
      render: (text, record) => (
        <a href={record.threadUrl} target="_blank" rel="noopener noreferrer">{text}</a>
      )
    },
    { 
      title: '作者', 
      dataIndex: 'author', 
      key: 'author',
      render: (text, record) => (
        <a href={record.authorUrl} target="_blank" rel="noopener noreferrer">{text}</a>
      )
    },
    { title: '重发次数', dataIndex: 'repostCount', key: 'repostCount', sorter: true },
    { title: '最后更新时间', dataIndex: 'lastUpdateTime', key: 'lastUpdateTime' },
    { title: '阅读量', dataIndex: 'viewCount', key: 'viewCount' },
    { title: '页数', dataIndex: 'pageNum', key: 'pageNum' },
    { 
      title: '操作', 
      key: 'action',
      render: (_, record) => (
        <Button type="primary" size="small" onClick={() => handleFollow(record)}>
          关注
        </Button>
      )
    }
  ];
  
  return (
    <div className="ranking-table">
      <h2>帖子排行榜</h2>
      <Input.Search 
        placeholder="搜索帖子" 
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

export default ThreadRankingTable; 