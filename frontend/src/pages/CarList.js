import React, { useState, useEffect } from 'react';
import { Table, Input, Space, Tag, Typography, Button, Card, Row, Col, Radio, Spin, Select, Divider, Badge, Tooltip, Statistic } from 'antd';
import { SearchOutlined, CarOutlined, RocketOutlined, FilterOutlined, SortAscendingOutlined, ClockCircleOutlined, DollarOutlined } from '@ant-design/icons';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const { Title, Text } = Typography;
const { Search } = Input;
const { Option } = Select;

// 交易类型颜色映射
const tradeTypeColors = {
  '售车': 'blue',
  '卖车': 'blue',
  '求购': 'green',
  '出售': 'cyan',
  '交换': 'purple',
  '租赁': 'orange',
  '未知': 'blue', // 默认未知也显示为卖车
};

const CarListPage = () => {
  // 状态管理
  const [loading, setLoading] = useState(true);
  const [cars, setCars] = useState([]);
  const [filteredCars, setFilteredCars] = useState([]);
  const [searchText, setSearchText] = useState('');
  const [total, setTotal] = useState(0);
  const [tradeTypeFilter, setTradeTypeFilter] = useState('all');
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [sortField, setSortField] = useState('post_time');
  const [sortOrder, setSortOrder] = useState('asc');

  // 获取汽车数据
  const fetchCars = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/cars`, { 
        params: { 
          limit: 5000, // 增加数据获取上限，足够获取所有数据
          sort_field: sortField,
          sort_order: sortOrder
        } 
      });
      
      const carData = response.data.data || [];
      
      // 处理未知数据
      const processedData = carData.map(car => ({
        ...car,
        trade_type: car.trade_type && car.trade_type !== '-' ? car.trade_type : '卖车', // 未知交易类型默认为卖车
      }));
      
      setCars(processedData);
      filterCars(processedData, searchText, tradeTypeFilter);
    } catch (err) {
      console.error('获取汽车数据失败:', err);
      // 出错时显示空数据
      setCars([]);
      setFilteredCars([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  // 初始加载数据
  useEffect(() => {
    fetchCars();
  }, [sortField, sortOrder]);

  // 筛选数据的通用函数
  const filterCars = (data, text, tradeType) => {
    let filtered = [...data];
    
    // 搜索过滤
    if (text) {
      const searchValue = text.toLowerCase();
      filtered = filtered.filter(car => 
        (car.year && car.year.toString().toLowerCase().includes(searchValue)) ||
        (car.make && car.make.toLowerCase().includes(searchValue)) ||
        (car.model && car.model.toLowerCase().includes(searchValue)) ||
        (car.title && car.title.toLowerCase().includes(searchValue))
      );
    }
    
    // 交易类型过滤
    if (tradeType !== 'all') {
      filtered = filtered.filter(car => car.trade_type === tradeType);
    }
    
    setFilteredCars(filtered);
    setTotal(filtered.length);
  };

  // 计算距离现在的天数
  const getDaysFromNow = (dateStr) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  // 搜索处理
  const handleSearch = (value) => {
    setSearchText(value);
    filterCars(cars, value, tradeTypeFilter);
  };

  // 清除搜索
  const handleClearSearch = () => {
    setSearchText('');
    filterCars(cars, '', tradeTypeFilter);
  };
  
  // 交易类型筛选处理
  const handleTradeTypeChange = (e) => {
    const value = e.target.value;
    setTradeTypeFilter(value);
    filterCars(cars, searchText, value);
  };
  
  // 处理排序变化
  const handleSortChange = (field) => {
    const newOrder = field === sortField && sortOrder === 'asc' ? 'desc' : 'asc';
    setSortField(field);
    setSortOrder(newOrder);
  };

  // 获取所有唯一的交易类型
  const getUniqueTradeTypes = () => {
    const types = new Set(cars.map(car => car.trade_type).filter(type => type));
    return Array.from(types);
  };

  // 修复表格的onChange处理
  const handleTableChange = (pagination, filters, sorter) => {
    if (sorter && sorter.field) {
      const field = sorter.field === 'post_time' ? 'post_time' : 
                    sorter.field === 'scraping_time_R' ? 'scraping_time_R' : 
                    sorter.field;
      setSortField(field);
      setSortOrder(sorter.order === 'ascend' ? 'asc' : 'desc');
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '年份',
      dataIndex: 'year',
      key: 'year',
      sorter: (a, b) => {
        const yearA = parseInt(a.year) || 0;
        const yearB = parseInt(b.year) || 0;
        return yearA - yearB;
      },
      render: (text) => text && text !== '-' ? text : '-',
    },
    {
      title: '品牌',
      dataIndex: 'make',
      key: 'make',
      render: (text) => text && text !== '-' ? text : '-',
    },
    {
      title: '型号',
      dataIndex: 'model',
      key: 'model',
      render: (text) => text && text !== '-' ? text : '-',
    },
    {
      title: '里程',
      dataIndex: 'miles',
      key: 'miles',
      render: (text) => text && text !== '-' ? text : '-',
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (text) => {
        if (!text || text === '-') return '-';
        return text.includes('$') ? text : `$${text}`;
      },
    },
    {
      title: '交易类型',
      dataIndex: 'trade_type',
      key: 'trade_type',
      render: (text) => {
        if (!text || text === '-') return <Tag color={tradeTypeColors['卖车']}>卖车</Tag>;
        return <Tag color={tradeTypeColors[text] || 'blue'}>{text}</Tag>;
      },
      filters: getUniqueTradeTypes().map(type => ({ text: type, value: type })),
      onFilter: (value, record) => record.trade_type === value,
    },
    {
      title: '地点',
      dataIndex: 'location',
      key: 'location',
      render: (text) => text || '-',
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      render: (text, record) => (
        <a href={record.url} target="_blank" rel="noopener noreferrer" className="car-title-link">
          {text || '-'}
        </a>
      ),
      ellipsis: true,
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      render: (text, record) => (
        record.author_link ? 
          <a href={record.author_link} target="_blank" rel="noopener noreferrer">
            {text || '-'}
          </a> : 
          (text || '-')
      ),
    },
    {
      title: (
        <span 
          onClick={() => handleSortChange('post_time')}
          style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}
        >
          帖龄 {sortField === 'post_time' && <SortAscendingOutlined rotate={sortOrder === 'desc' ? 180 : 0} />}
        </span>
      ),
      dataIndex: 'post_time',
      key: 'post_time',
      render: (text) => {
        const days = getDaysFromNow(text);
        return days !== '-' ? `${days}天` : '-';
      },
      sorter: (a, b) => {
        const daysA = getDaysFromNow(a.post_time);
        const daysB = getDaysFromNow(b.post_time);
        if (daysA === '-' || daysB === '-') return 0;
        return daysA - daysB;
      },
      defaultSortOrder: 'ascend',
    },
    {
      title: '活跃',
      dataIndex: 'scraping_time_R',
      key: 'scraping_time_R',
      render: (text) => {
        const days = getDaysFromNow(text);
        return days !== '-' ? `${days}天前` : '-';
      },
      sorter: (a, b) => {
        const daysA = getDaysFromNow(a.scraping_time_R);
        const daysB = getDaysFromNow(b.scraping_time_R);
        if (daysA === '-' || daysB === '-') return 0;
        return daysA - daysB;
      },
    },
  ];

  return (
    <div style={{ padding: '24px', background: '#f0f2f5', minHeight: '100vh' }}>
      <div 
        style={{ 
          background: 'linear-gradient(135deg, #1a237e 0%, #2196f3 100%)',
          padding: '30px 24px',
          borderRadius: '12px',
          boxShadow: '0 10px 20px rgba(0,0,0,0.1)',
          marginBottom: '24px',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* 背景装饰元素 */}
        <div className="bg-circles" style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          opacity: 0.1,
          zIndex: 0,
          background: `
            radial-gradient(circle at 10% 20%, rgba(255,255,255,0.3) 0%, transparent 20%),
            radial-gradient(circle at 90% 80%, rgba(255,255,255,0.3) 0%, transparent 20%),
            radial-gradient(circle at 50% 50%, rgba(255,255,255,0.1) 0%, transparent 50%)
          `
        }}></div>
        
        <Row gutter={[24, 24]} align="middle" style={{ position: 'relative', zIndex: 1 }}>
          <Col xs={24} md={16}>
            <Title level={2} style={{ color: 'white', margin: 0, fontWeight: 'bold', textShadow: '0 2px 4px rgba(0,0,0,0.2)' }}>
              <CarOutlined style={{ marginRight: 12 }} /> 全美智能收车系统
            </Title>
            <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: '16px', display: 'block', marginTop: '8px' }}>
              人工智能为您筛选全美最佳车源 
              <Tag color="rgba(255,255,255,0.3)" style={{ 
                color: 'white', 
                marginLeft: '10px', 
                fontSize: '16px', 
                padding: '4px 12px',
                fontWeight: 'bold'
              }}>
                共计 {total} 辆车
              </Tag>
            </Text>
          </Col>
          
          <Col xs={24} md={8}>
            <div className={`search-container ${isSearchFocused ? 'focused' : ''}`} style={{ 
              transition: 'all 0.3s ease',
              transform: isSearchFocused ? 'scale(1.03)' : 'scale(1)',
              boxShadow: isSearchFocused 
                ? '0 0 0 3px rgba(24, 144, 255, 0.2), 0 15px 25px rgba(0,0,0,0.1)' 
                : '0 8px 16px rgba(0,0,0,0.1)',
              borderRadius: '8px',
              background: 'white',
              padding: '6px',
              position: 'relative'
            }}>
              <Search
                placeholder="搜索年份、品牌、型号或标题..."
                allowClear
                enterButton={<SearchOutlined style={{ fontSize: '20px' }} />}
                size="large"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onSearch={handleSearch}
                onFocus={() => setIsSearchFocused(true)}
                onBlur={() => setIsSearchFocused(false)}
                style={{ width: '100%' }}
              />
              
              {/* 搜索框发光效果 */}
              <div style={{
                position: 'absolute',
                bottom: '-8px',
                left: '50%',
                transform: 'translateX(-50%)',
                height: '5px',
                width: '50%', 
                background: 'linear-gradient(90deg, rgba(24,144,255,0) 0%, rgba(24,144,255,0.8) 50%, rgba(24,144,255,0) 100%)',
                borderRadius: '5px',
                filter: 'blur(4px)',
                opacity: isSearchFocused ? 0.8 : 0,
                transition: 'opacity 0.3s ease'
              }}></div>
            </div>
          </Col>
        </Row>
      </div>
      
      <Card 
        styles={{ 
          body: { padding: 0 }
        }}
        style={{ 
          borderRadius: '8px',
          overflow: 'hidden',
          boxShadow: '0 4px 12px rgba(0,0,0,0.05)'
        }}
      >
        <Table
          columns={columns}
          dataSource={filteredCars}
          rowKey="id"
          loading={loading}
          pagination={{ 
            pageSize: 20, 
            showSizeChanger: true, 
            pageSizeOptions: ['10', '20', '50', '100', '200', '500', '1000'],
            showTotal: (total) => `共 ${total} 条记录`,
            position: ['bottomCenter'],
            showQuickJumper: true,
            style: { marginBottom: '24px', marginTop: '24px' },
            itemRender: (page, type, originalElement) => {
              if (type === 'page') {
                return (
                  <div style={{ 
                    minWidth: '32px', 
                    height: '32px', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    fontWeight: 'bold',
                    color: '#1a237e'
                  }}>
                    {page}
                  </div>
                );
              }
              return originalElement;
            }
          }}
          scroll={{ x: 1300 }}
          onChange={handleTableChange}
          rowClassName={() => 'car-table-row'}
        />
      </Card>
      
      {/* 版权信息 */}
      <div style={{ 
        textAlign: 'center', 
        padding: '16px', 
        color: 'rgba(0,0,0,0.45)', 
        fontSize: '14px',
        marginTop: '16px'
      }}>
        数智罗盘 ©2025
      </div>
      
      {/* 添加CSS样式 */}
      <style jsx="true">{`
        .car-table-row {
          transition: all 0.3s;
        }
        .car-table-row:hover {
          background-color: rgba(24, 144, 255, 0.05) !important;
          transform: translateY(-2px);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
        }
        .car-title-link {
          transition: all 0.3s;
          position: relative;
          padding-bottom: 2px;
        }
        .car-title-link:hover {
          color: #1890ff;
        }
        .car-title-link:hover::after {
          content: '';
          position: absolute;
          left: 0;
          bottom: 0;
          width: 100%;
          height: 2px;
          background: linear-gradient(90deg, #1890ff, transparent);
        }
        .search-container {
          transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        .search-container:hover {
          transform: scale(1.01);
        }
        .search-container.focused {
          transform: scale(1.03);
        }
        
        /* 动画效果 */
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .ant-card {
          animation: fadeIn 0.5s ease-out;
        }
        
        .ant-input::placeholder {
          color: rgba(0, 0, 0, 0.5);
          font-weight: 500;
        }
        
        /* 分页组件样式 */
        .ant-pagination-item {
          border-radius: 6px;
          font-weight: bold;
          border-width: 2px;
        }
        
        .ant-pagination-item-active {
          background-color: #1890ff;
          border-color: #1890ff;
        }
        
        .ant-pagination-item-active a {
          color: white !important;
        }
        
        .ant-pagination-options {
          margin-left: 16px;
        }
        
        .ant-pagination-options-quick-jumper input {
          border-radius: 4px;
          border-width: 2px;
        }
      `}</style>
    </div>
  );
};

export default CarListPage; 