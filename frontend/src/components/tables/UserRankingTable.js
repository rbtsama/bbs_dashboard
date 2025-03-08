import React, { useState, useEffect } from 'react';
import { Card, Table, Spin, Typography } from 'antd';
import axios from 'axios';

const { Link } = Typography;

const API_BASE_URL = '/api';

const UserRankingTable = () => {
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

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async (page = 1, pageSize = 10, sortField = sorter.field, sortOrder = sorter.order) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/user-ranking`, {
        params: { 
          page, 
          limit: pageSize,
          sort_field: sortField,
          sort_order: sortOrder === 'descend' ? 'desc' : 'asc'
        }
      });
      
      // 适应新的API返回格式
      const responseData = response.data;
      
      setData(responseData.data || []);
      setPagination({
        ...pagination,
        current: responseData.page || page,
        pageSize: responseData.limit || pageSize,
        total: responseData.total || 0
      });
    } catch (error) {
      console.error('获取用户排行榜数据失败:', error);
    } finally {
      setLoading(false);
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

  const columns = [
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      width: 80,
      render: (_, __, index) => (pagination.current - 1) * pagination.pageSize + index + 1
    },
    {
      title: '用户',
      dataIndex: 'author',
      key: 'author',
      ellipsis: true,
      render: (text, record) => (
        <Link href={record.author_link} target="_blank">
          {text}
        </Link>
      )
    },
    {
      title: '帖子数',
      dataIndex: 'post_count',
      key: 'post_count',
      width: 100,
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'post_count' ? sorter.order : null
    },
    {
      title: '重发',
      dataIndex: 'repost_count',
      key: 'repost_count',
      width: 100,
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'repost_count' ? sorter.order : 'descend'
    },
    {
      title: '回帖',
      dataIndex: 'reply_count',
      key: 'reply_count',
      width: 100,
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'reply_count' ? sorter.order : null
    },
    {
      title: '删回帖',
      dataIndex: 'delete_count',
      key: 'delete_count',
      width: 100,
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'delete_count' ? sorter.order : null
    },
    {
      title: '最近活跃',
      dataIndex: 'last_active',
      key: 'last_active',
      width: 120,
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'last_active' ? sorter.order : null,
      render: (text) => `${text}天`
    }
  ];

  return (
    <Card title="用户排行榜" style={{ marginTop: 16 }}>
      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="author"
          pagination={pagination}
          onChange={handleTableChange}
          scroll={{ x: 'max-content' }}
        />
      </Spin>
    </Card>
  );
};

export default UserRankingTable; 