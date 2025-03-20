import React, { useState, useEffect } from 'react';
import { Table, Input, Select, Button, Space, Row, Col, Card, Tooltip, message } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import axios from 'axios';
import moment from 'moment';
import { API_BASE_URL } from '../config';

const { Option } = Select;

const CarListTable = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    showSizeChanger: true
  });
  const [sorter, setSorter] = useState({
    field: 'updated_at',
    order: 'descend'
  });
  const [filters, setFilters] = useState({});
  const [makes, setMakes] = useState([]);
  const [models, setModels] = useState([]);
  const [years, setYears] = useState([]);
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    fetchData();
    fetchFilters();
  }, []);

  const fetchFilters = async () => {
    try {
      // 获取品牌列表
      const makesResponse = await axios.get(`${API_BASE_URL}/car-makes`);
      setMakes(makesResponse.data || []);

      // 获取年份列表
      const yearsResponse = await axios.get(`${API_BASE_URL}/car-years`);
      setYears(yearsResponse.data || []);

      // 获取位置列表
      const locationsResponse = await axios.get(`${API_BASE_URL}/car-locations`);
      setLocations(locationsResponse.data || []);
    } catch (error) {
      console.error('获取过滤选项失败:', error);
      message.error('获取过滤选项失败');
    }
  };

  const fetchModels = async (make) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/car-models`, {
        params: { make }
      });
      setModels(response.data || []);
    } catch (error) {
      console.error('获取车型列表失败:', error);
      message.error('获取车型列表失败');
    }
  };

  const fetchData = async (page = pagination.current, pageSize = pagination.pageSize) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/car-info`, {
        params: {
          page,
          limit: pageSize,
          sort_field: sorter.field,
          sort_order: sorter.order === 'ascend' ? 'asc' : 'desc',
          ...filters
        }
      });

      const { data: responseData, total } = response.data;

      setData(responseData.map(item => ({
        ...item,
        key: item.id || item.url
      })));

      setPagination({
        ...pagination,
        current: page,
        pageSize,
        total
      });
    } catch (error) {
      console.error('获取车辆列表失败:', error);
      message.error('获取车辆列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleTableChange = (pagination, filters, sorter) => {
    setSorter({
      field: sorter.field || 'updated_at',
      order: sorter.order || 'descend'
    });
    fetchData(pagination.current, pagination.pageSize);
  };

  const handleSearch = () => {
    setPagination({
      ...pagination,
      current: 1
    });
    fetchData(1, pagination.pageSize);
  };

  const handleReset = () => {
    setFilters({});
    setSorter({
      field: 'updated_at',
      order: 'descend'
    });
    setPagination({
      ...pagination,
      current: 1
    });
    fetchData(1, pagination.pageSize);
  };

  const handleMakeChange = (value) => {
    setFilters({
      ...filters,
      make: value
    });
    if (value) {
      fetchModels(value);
    } else {
      setModels([]);
    }
  };

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      render: (text, record) => (
        <Tooltip title={text || record.model}>
          <a href={record.url} target="_blank" rel="noopener noreferrer">
            {text || `${record.year} ${record.make} ${record.model}`}
          </a>
        </Tooltip>
      ),
      width: 300,
      ellipsis: true
    },
    {
      title: '年份',
      dataIndex: 'year',
      key: 'year',
      sorter: true,
      width: 80
    },
    {
      title: '品牌',
      dataIndex: 'make',
      key: 'make',
      width: 100
    },
    {
      title: '型号',
      dataIndex: 'model',
      key: 'model',
      width: 120
    },
    {
      title: '里程',
      dataIndex: 'miles',
      key: 'miles',
      width: 100
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: text => text || '-'
    },
    {
      title: '交易类型',
      dataIndex: 'trade_type',
      key: 'trade_type',
      width: 100
    },
    {
      title: '位置',
      dataIndex: 'location',
      key: 'location',
      width: 100
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      render: (text, record) => (
        record.author_link ? (
          <a href={record.author_link} target="_blank" rel="noopener noreferrer">
            {text || '-'}
          </a>
        ) : (
          text || '-'
        )
      ),
      width: 100
    },
    {
      title: '发帖时间',
      dataIndex: 'post_time',
      key: 'post_time',
      render: text => text ? moment(text).format('YYYY-MM-DD HH:mm') : '-',
      sorter: true,
      width: 150
    },
    {
      title: '帖龄',
      dataIndex: 'daysold',
      key: 'daysold',
      render: text => text ? `${text}天` : '-',
      sorter: true,
      width: 80
    },
    {
      title: '最后活跃',
      dataIndex: 'last_active',
      key: 'last_active',
      render: text => text ? `${text}天前` : '-',
      sorter: true,
      width: 100
    },
    {
      title: '阅读',
      dataIndex: 'read_count',
      key: 'read_count',
      render: text => text || '0',
      sorter: true,
      width: 80
    },
    {
      title: '回复',
      dataIndex: 'reply_count',
      key: 'reply_count',
      render: text => text || '0',
      sorter: true,
      width: 80
    }
  ];

  return (
    <Card>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={4}>
          <Select
            placeholder="选择年份"
            allowClear
            style={{ width: '100%' }}
            value={filters.year}
            onChange={(value) => setFilters({ ...filters, year: value })}
          >
            {years.map(year => (
              <Option key={year} value={year}>{year}</Option>
            ))}
          </Select>
        </Col>
        <Col span={4}>
          <Select
            placeholder="选择品牌"
            allowClear
            style={{ width: '100%' }}
            value={filters.make}
            onChange={handleMakeChange}
          >
            {makes.map(make => (
              <Option key={make} value={make}>{make}</Option>
            ))}
          </Select>
        </Col>
        <Col span={4}>
          <Select
            placeholder="选择型号"
            allowClear
            style={{ width: '100%' }}
            value={filters.model}
            onChange={(value) => setFilters({ ...filters, model: value })}
            disabled={!filters.make}
          >
            {models.map(model => (
              <Option key={model} value={model}>{model}</Option>
            ))}
          </Select>
        </Col>
        <Col span={4}>
          <Select
            placeholder="选择位置"
            allowClear
            style={{ width: '100%' }}
            value={filters.location}
            onChange={(value) => setFilters({ ...filters, location: value })}
          >
            {locations.map(location => (
              <Option key={location} value={location}>{location}</Option>
            ))}
          </Select>
        </Col>
        <Col span={4}>
          <Input
            placeholder="最低价格"
            value={filters.price_min}
            onChange={(e) => setFilters({ ...filters, price_min: e.target.value })}
            style={{ width: '100%' }}
          />
        </Col>
        <Col span={4}>
          <Input
            placeholder="最高价格"
            value={filters.price_max}
            onChange={(e) => setFilters({ ...filters, price_max: e.target.value })}
            style={{ width: '100%' }}
          />
        </Col>
      </Row>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={4}>
          <Input
            placeholder="最低里程"
            value={filters.miles_min}
            onChange={(e) => setFilters({ ...filters, miles_min: e.target.value })}
            style={{ width: '100%' }}
          />
        </Col>
        <Col span={4}>
          <Input
            placeholder="最高里程"
            value={filters.miles_max}
            onChange={(e) => setFilters({ ...filters, miles_max: e.target.value })}
            style={{ width: '100%' }}
          />
        </Col>
        <Col span={16}>
          <Space>
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
              搜索
            </Button>
            <Button icon={<ReloadOutlined />} onClick={handleReset}>
              重置
            </Button>
          </Space>
        </Col>
      </Row>
      <Table
        columns={columns}
        dataSource={data}
        pagination={pagination}
        loading={loading}
        onChange={handleTableChange}
        scroll={{ x: 1500 }}
      />
    </Card>
  );
};

export default CarListTable; 