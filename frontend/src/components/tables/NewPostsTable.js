import React, { useState, useEffect } from 'react';
import { Card, Table, Spin, Typography } from 'antd';
import axios from 'axios';

const { Link } = Typography;

const API_BASE_URL = '/api';

const NewPostsTable = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    showSizeChanger: false
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async (page = 1, pageSize = 10) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/new-posts-yesterday`, {
        params: { page, limit: pageSize }
      });
      
      setData(response.data);
      setPagination({
        ...pagination,
        current: page,
        total: response.data.length > pageSize ? response.data.length : response.data.length + pageSize
      });
    } catch (error) {
      console.error('获取昨日新帖数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTableChange = (pagination) => {
    fetchData(pagination.current, pagination.pageSize);
  };

  // 格式化日期时间
  const formatDateTime = (dateTimeStr) => {
    if (!dateTimeStr) return '';
    const date = new Date(dateTimeStr);
    return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  };

  const columns = [
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
      title: '发帖时间',
      dataIndex: 'post_time',
      key: 'post_time',
      width: 180,
      sorter: (a, b) => new Date(a.post_time) - new Date(b.post_time),
      defaultSortOrder: 'ascend',
      render: (text) => formatDateTime(text)
    }
  ];

  return (
    <Card title="昨日新帖" style={{ marginTop: 16 }}>
      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="url"
          pagination={pagination}
          onChange={handleTableChange}
          scroll={{ x: 'max-content' }}
        />
      </Spin>
    </Card>
  );
};

export default NewPostsTable; 