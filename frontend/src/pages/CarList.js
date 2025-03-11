import React, { useState, useEffect } from 'react';
import { Input, Table, Card, message, Button, Typography, Space } from 'antd';
import { fetchCarList, importCarInfo } from '../services/api';
import { SearchOutlined } from '@ant-design/icons';

const { Search } = Input;

const CarList = () => {
  const [loading, setLoading] = useState(false);
  const [carList, setCarList] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: false,
  });
  const [searchValue, setSearchValue] = useState('');

  // 获取车辆列表
  const getCarList = async (page = 1, search = searchValue) => {
    setLoading(true);
    try {
      const res = await fetchCarList(page, pagination.pageSize, search);
      if (res.success) {
        setCarList(res.data);
        setPagination({
          ...pagination,
          current: res.page,
          total: res.total,
        });
      } else {
        message.error(res.message || '获取车辆列表失败');
      }
    } catch (error) {
      console.error('获取车辆列表出错:', error);
      message.error('获取车辆列表出错');
    } finally {
      setLoading(false);
    }
  };

  // 表格分页变化
  const handleTableChange = (pagination) => {
    getCarList(pagination.current);
  };

  // 搜索
  const handleSearch = (value) => {
    setSearchValue(value);
    getCarList(1, value);
  };

  // 初始加载
  useEffect(() => {
    getCarList();
  }, []);

  // 通用渲染函数 - 处理空值和"找不到"
  const renderCommonField = (text) => {
    if (!text || text === '找不到' || text === 'undefined' || text === 'null') {
      return '-';
    }
    return text;
  };

  // 表格列定义
  const columns = [
    {
      title: '年份',
      dataIndex: 'year',
      key: 'year',
      width: 80,
      render: renderCommonField,
    },
    {
      title: '品牌',
      dataIndex: 'make',
      key: 'make',
      width: 120,
      render: renderCommonField,
    },
    {
      title: '型号',
      dataIndex: 'model',
      key: 'model',
      width: 120,
      render: renderCommonField,
    },
    {
      title: '里程',
      dataIndex: 'miles',
      key: 'miles',
      width: 120,
      render: renderCommonField,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: renderCommonField,
    },
    {
      title: '交易类型',
      dataIndex: 'trade_type',
      key: 'trade_type',
      width: 100,
      render: (text) => {
        if (!text || text === '找不到') {
          return '-';
        }
        if (text === '买车') {
          return <span style={{ color: 'red' }}>{text}</span>;
        }
        if (text === '租车') {
          return <span style={{ color: 'purple' }}>{text}</span>;
        }
        return text;
      },
    },
    {
      title: '地点',
      dataIndex: 'location',
      key: 'location',
      width: 120,
      render: renderCommonField,
    },
    {
      title: '帖子',
      dataIndex: 'url',
      key: 'url',
      width: 100,
      render: (text, record) => (
        <a href={text} target="_blank" rel="noopener noreferrer">
          {record.thread_id ? `#${record.thread_id}` : '-'}
        </a>
      ),
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: 100,
      render: (text) => {
        if (!text || text === '找不到') return '-';
        const authorUrl = `https://www.chineseinla.com/f/profile_${text}.html`;
        return <a href={authorUrl} target="_blank" rel="noopener noreferrer">{text}</a>;
      },
    },
    {
      title: '发帖天数',
      dataIndex: 'daysold',
      key: 'daysold',
      width: 90,
      render: (text) => {
        if (!text && text !== 0) return '-';
        return text;
      },
    },
    {
      title: '最近活跃',
      dataIndex: 'last_active',
      key: 'last_active',
      width: 150,
      render: (text) => {
        if (!text && text !== 0) return '-';
        return `${text}天前`;
      },
    },
  ];

  return (
    <div>
      <Card>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 24 }}>
          <Search
            placeholder="请输入感兴趣的车辆名称"
            enterButton={<Button type="primary" icon={<SearchOutlined />}>搜索</Button>}
            onSearch={handleSearch}
            style={{ 
              width: '320px', 
              height: 50, 
              fontSize: 18 
            }}
            size="large"
            allowClear
          />
        </div>
        <Table
          dataSource={carList}
          columns={columns}
          rowKey="id"
          pagination={pagination}
          onChange={handleTableChange}
          loading={loading}
          scroll={{ x: 1300 }}
        />
      </Card>
    </div>
  );
};

export default CarList; 