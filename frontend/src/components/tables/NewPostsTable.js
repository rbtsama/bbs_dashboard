import React, { useState, useEffect } from 'react';
import { Card, Table, Spin, Typography, Badge, Tag, Space, Empty, DatePicker, Button, ConfigProvider } from 'antd';
import { ClockCircleOutlined, UserOutlined, RiseOutlined, LeftOutlined, RightOutlined, CalendarOutlined } from '@ant-design/icons';
import { getNewPosts } from '../../services/api';
import axios from 'axios';
import styled from 'styled-components';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';

dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

const { Link } = Typography;

const API_BASE_URL = '/api';

// 样式化卡片组件
const ModernCard = styled(Card)`
  margin-top: 24px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: none;
  
  &:hover {
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
    transform: translateY(-2px);
  }
  
  .ant-card-head {
    background: linear-gradient(135deg, #e6f7ff 0%, #ffffff 100%);
    border-bottom: 1px solid #f0f0f0;
    padding: 0;
    min-height: 64px;
    display: flex;
    align-items: center;
  }
  
  .ant-card-head-title {
    padding: 16px 24px;
    font-size: 18px;
    font-weight: 600;
  }

  .ant-table {
    font-size: 15px;
  }
  
  .ant-table-thead > tr > th {
    background-color: #fafafa;
    font-weight: 600;
    font-size: 16px;
    padding: 16px 24px;
    color: #333;
    border-bottom: 2px solid #f0f0f0;
  }
  
  .ant-table-tbody > tr > td {
    padding: 16px 24px;
    transition: all 0.3s;
  }
  
  .ant-table-tbody > tr:hover > td {
    background-color: #e6f7ff;
  }
  
  .ant-table-row {
    transition: all 0.2s;
  }
  
  .ant-table-row:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }
  
  .ant-table-pagination {
    margin: 16px 24px;
  }
  
  @media (max-width: 768px) {
    .ant-card-head-title {
      padding: 12px 16px;
      font-size: 16px;
    }
    
    .ant-table-thead > tr > th,
    .ant-table-tbody > tr > td {
      padding: 12px 16px;
      font-size: 14px;
    }
  }
`;

// 表格链接样式
const StyledLink = styled(Link)`
  font-size: 15px;
  font-weight: 500;
  color: #1890ff;
  transition: all 0.3s;
  
  &:hover {
    color: #40a9ff;
    text-decoration: underline;
  }
  
  @media (max-width: 768px) {
    font-size: 14px;
  }
`;

// 表格标题样式
const TableTitle = styled.div`
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  width: 100%;
  
  .left-section {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;
  }
  
  .icon {
    font-size: 24px;
    color: #1890ff;
  }
  
  .title-text {
    font-size: 18px;
    font-weight: 600;
    margin-right: 16px;
    white-space: nowrap;
  }
  
  .badge {
    margin-left: auto;
    flex-shrink: 0;
    
    .ant-badge-count {
      background: #1890ff;
      box-shadow: 0 4px 12px rgba(24, 144, 255, 0.2);
      font-size: 16px;
      font-weight: 600;
      padding: 0 12px;
      height: 28px;
      line-height: 28px;
      border-radius: 14px;
    }
  }
`;

// 日期选择器容器样式
const DatePickerContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  
  .ant-picker {
    border-radius: 8px;
    border: 1px solid #d9d9d9;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: all 0.3s;
    
    &:hover {
      border-color: #40a9ff;
      box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
    }
    
    &.ant-picker-focused {
      border-color: #1890ff;
      box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
    }
  }
  
  .date-nav-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: 1px solid #d9d9d9;
    background-color: white;
    color: #1890ff;
    transition: all 0.3s;
    
    &:hover {
      background-color: #e6f7ff;
      border-color: #1890ff;
    }
    
    &:active {
      background-color: #bae7ff;
    }
  }
`;

// 时间标签样式
const TimeTag = styled(Tag)`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
  background: #f0f5ff;
  border-color: #adc6ff;
  color: #1890ff;
  
  .anticon {
    font-size: 12px;
  }
`;

// 作者标签样式
const AuthorTag = styled(Tag)`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
  background: #f6ffed;
  border-color: #b7eb8f;
  color: #52c41a;
  
  .anticon {
    font-size: 12px;
  }
`;

const NewPostsTable = ({ selectedDate: propSelectedDate }) => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);
  const [totalPosts, setTotalPosts] = useState(0);
  const [currentDate, setCurrentDate] = useState(null);
  const [selectedDate, setSelectedDate] = useState(propSelectedDate || null);
  const [minDate, setMinDate] = useState(null);
  const [maxDate, setMaxDate] = useState(null);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true
  });

  // 获取数据库中的最早和最晚日期
  useEffect(() => {
    const fetchDateRange = async () => {
      try {
        // 调用API获取日期范围
        const response = await axios.get(`${API_BASE_URL}/post-date-range`);
        if (response.data) {
          console.log('获取到的日期范围:', response.data);
          setMinDate(response.data.min_date);
          setMaxDate(response.data.max_date);
          
          // 如果没有选择日期，默认使用最新日期
          if (!selectedDate && response.data.max_date) {
            setSelectedDate(response.data.max_date);
          }
        }
      } catch (error) {
        console.error('获取日期范围失败:', error);
        // 如果API调用失败，使用默认值
        setMinDate('2025-02-05');
        setMaxDate('2025-03-07');
      }
    };

    fetchDateRange();
  }, []);

  useEffect(() => {
    if (propSelectedDate !== selectedDate) {
      setSelectedDate(propSelectedDate);
    }
  }, [propSelectedDate]);

  useEffect(() => {
    fetchData();
  }, [selectedDate]);

  const fetchData = async (page = 1, pageSize = 10) => {
    setLoading(true);
    try {
      console.log('正在获取新帖数据，参数:', { page, pageSize, selectedDate });
      
      // 构建API请求参数
      const params = {
        page,
        limit: pageSize,
        get_total: true,
        sort_by: 'post_time',
        sort_order: 'desc'
      };
      
      // 如果有选定日期，添加到请求参数
      if (selectedDate) {
        params.date = selectedDate;
      }
      
      const response = await getNewPosts(params);
      console.log('接口返回的原始数据:', response);
      
      // 检查返回的数据格式
      if (response && typeof response === 'object') {
        let posts = [];
        let total = 0;
        let date = null;
        
        // 处理返回格式 {data: [], total: 0, date: ''}
        if (Array.isArray(response.data)) {
          posts = response.data;
          total = response.total || 0;
          date = response.date;
        } 
        // 处理旧的返回格式 []
        else if (Array.isArray(response)) {
          posts = response;
          total = posts.length;
        }
        
        console.log('处理后的数据:', {
          dataLength: posts.length,
          total,
          date
        });
        
        setData(posts);
        setTotalPosts(total);
        setCurrentDate(date);
        setPagination({
          ...pagination,
          current: page,
          pageSize,
          total
        });
      } else {
        console.error('接口返回的数据格式不正确:', response);
        setData([]);
        setTotalPosts(0);
      }
    } catch (error) {
      console.error('获取新帖数据出错:', error);
      setData([]);
      setTotalPosts(0);
    } finally {
      setLoading(false);
    }
  };

  const handleTableChange = (newPagination) => {
    fetchData(newPagination.current, newPagination.pageSize);
  };

  const formatDateTime = (dateTimeStr) => {
    if (!dateTimeStr) return '';
    const date = new Date(dateTimeStr);
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  };

  // 处理日期变更
  const handleDateChange = (date) => {
    if (date) {
      setSelectedDate(date.format('YYYY-MM-DD'));
    } else {
      setSelectedDate(null);
    }
  };

  // 前一天
  const handlePrevDay = () => {
    if (currentDate) {
      const prevDay = dayjs(currentDate).subtract(1, 'day');
      if (!minDate || prevDay.isAfter(minDate) || prevDay.isSame(minDate)) {
        setSelectedDate(prevDay.format('YYYY-MM-DD'));
      }
    }
  };

  // 后一天
  const handleNextDay = () => {
    if (currentDate) {
      const nextDay = dayjs(currentDate).add(1, 'day');
      if (!maxDate || nextDay.isBefore(maxDate) || nextDay.isSame(maxDate)) {
        setSelectedDate(nextDay.format('YYYY-MM-DD'));
      }
    }
  };

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      width: '50%',
      render: (text, record) => (
        <StyledLink href={record.url} target="_blank" ellipsis>
          {text}
        </StyledLink>
      )
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: '35%',
      render: (text, record) => (
        <StyledLink href={record.author_link} target="_blank">
          {text}
        </StyledLink>
      )
    },
    {
      title: '发帖时间',
      dataIndex: 'post_time',
      key: 'post_time',
      width: '15%',
      render: (text) => formatDateTime(text),
      sorter: true,
      defaultSortOrder: 'descend'
    }
  ];

  // 格式化标题日期
  const formatTitleDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  const title = (
    <TableTitle>
      <div className="left-section">
        <RiseOutlined className="icon" />
        <span className="title-text">新帖速递</span>
        <DatePickerContainer>
          <Button 
            className="date-nav-button" 
            icon={<LeftOutlined />} 
            onClick={handlePrevDay}
            disabled={minDate && currentDate && dayjs(currentDate).isSame(minDate)}
          />
          <DatePicker 
            value={currentDate ? dayjs(currentDate) : null}
            onChange={handleDateChange}
            format="YYYY-MM-DD"
            placeholder="选择日期"
            allowClear={false}
            disabledDate={(current) => {
              if (!current) return false;
              // 禁用范围外的日期
              if (minDate && current.isBefore(dayjs(minDate))) return true;
              if (maxDate && current.isAfter(dayjs(maxDate))) return true;
              return false;
            }}
            suffixIcon={<CalendarOutlined style={{ color: '#1890ff' }} />}
          />
          <Button 
            className="date-nav-button" 
            icon={<RightOutlined />} 
            onClick={handleNextDay}
            disabled={maxDate && currentDate && dayjs(currentDate).isSame(maxDate)}
          />
        </DatePickerContainer>
      </div>
      <Badge 
        count={`共${totalPosts}条`}
        className="badge" 
        overflowCount={9999}
      />
    </TableTitle>
  );

  return (
    <ModernCard 
      title={title} 
      styles={{
        body: { padding: '0' }
      }}
    >
      <ConfigProvider
        theme={{
          components: {
            Table: {
              borderColor: '#f0f0f0',
              headerBg: '#fafafa',
              headerColor: 'rgba(0, 0, 0, 0.85)',
              headerSplitColor: '#f0f0f0',
              rowHoverBg: '#e6f7ff',
              padding: 12,
              paddingXS: 8,
              paddingLG: 16,
            },
            Pagination: {
              colorBgContainer: '#ffffff',
              colorPrimary: '#1890ff',
              colorPrimaryHover: '#40a9ff',
              colorText: 'rgba(0, 0, 0, 0.88)',
              colorTextDisabled: 'rgba(0, 0, 0, 0.25)',
              controlHeight: 32,
              fontSizeSM: 14,
              itemActiveBg: '#1890ff',
              itemSize: 32,
              colorTextItemSelected: '#ffffff',
              colorBgTextHover: '#e6f4ff',
              colorBgTextActive: '#1890ff',
              colorTextActive: '#ffffff'
            },
          },
        }}
      >
        <Spin spinning={loading}>
          {data.length > 0 ? (
            <Table
              columns={columns}
              dataSource={data}
              rowKey="url"
              pagination={{
                ...pagination,
                showTotal: (total) => `共 ${total} 条记录`,
                style: { margin: '16px 0' },
                position: ['bottomCenter']
              }}
              onChange={handleTableChange}
              scroll={{ x: '100%' }}
            />
          ) : (
            <Empty 
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="暂无新帖数据"
            />
          )}
        </Spin>
      </ConfigProvider>
    </ModernCard>
  );
};

export default NewPostsTable;