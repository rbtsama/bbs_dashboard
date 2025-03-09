import React, { useState, useEffect } from 'react';
import { Card, Table, Spin, Typography } from 'antd';
import axios from 'axios';

const { Link } = Typography;

const API_BASE_URL = '/api';

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

  useEffect(() => {
    fetchData();
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
      
      // 适应新的API返回格式
      const responseData = response.data;
      
      // 处理数据，确保字段名称正确
      const processedData = responseData.data.map(item => ({
        ...item,
        // 确保字段名称一致，将Days_Old映射到days_old
        days_old: item.Days_Old || item.days_old || 0,
        // 确保其他可能的字段也正确映射
        last_active: item.Last_Active || item.last_active || 0,
        repost_count: item.Repost_Count || item.repost_count || 0,
        reply_count: item.Reply_Count || item.reply_count || 0,
        delete_count: item.Delete_Count || item.delete_count || 0,
        read_count: item.read_count || 0
      }));
      
      console.log('处理后的帖子排行榜数据:', processedData);
      
      setData(processedData);
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
    }
  ];

  return (
    <Card title="帖子排行榜" style={{ marginTop: 16 }}>
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

export default ThreadRankingTable; 