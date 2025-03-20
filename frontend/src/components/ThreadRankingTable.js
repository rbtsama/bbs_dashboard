import React, { useState, useEffect, useCallback } from 'react';
import { Table, Button, Input, App } from 'antd';
import { useDispatch } from 'react-redux';
import { followThread } from '../redux/actions';
import { fetchPostRank } from '../services/api';

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
      const response = await fetchPostRank(page, pageSize);
      
      if (response && response.data && Array.isArray(response.data) && response.data.length > 0) {
        // 处理从import表获取的数据
        const formattedData = response.data.map((item, index) => ({
          id: item.id || `thread_${item.thread_id}` || `index_${index}`,
          thread_id: item.thread_id || '',
          title: item.title || '无标题',
          author: item.author || '未知作者',
          authorUrl: item.author_id ? `https://example.com/user/${item.author_id}` : '#',
          repostCount: item.count || 0,
          lastUpdateTime: item.datetime || '',
          threadUrl: item.url || '#',
          rank: index + 1 + (page - 1) * pageSize
        }));
        
        const filteredData = search 
          ? formattedData.filter(item => 
              (item.title && item.title.toLowerCase().includes(search.toLowerCase())) || 
              (item.author && item.author.toLowerCase().includes(search.toLowerCase()))
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
        // 没有数据时返回空数组，而不是抛出错误
        setTableData([]);
        setPagination(prev => ({
          ...prev,
          current: page,
          pageSize,
          total: 0
        }));
      }
    } catch (error) {
      console.error('获取帖子排行榜失败:', error);
      message.error('获取帖子排行榜失败');
      // 错误时返回空数组，而不是使用模拟数据
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
  }, [loading, message]); // 添加loading依赖
  
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
    { title: '重发次数', dataIndex: 'repostCount', key: 'repostCount' },
    { title: '最后更新时间', dataIndex: 'lastUpdateTime', key: 'lastUpdateTime' },
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
        rowKey={record => record.id || record.thread_id || record.url || String(record.rank)}
      />
    </div>
  );
};

export default ThreadRankingTable; 