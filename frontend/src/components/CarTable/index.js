import React from 'react';
import { Table, Empty, Tag } from 'antd';
import { CarOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import EnhancedLoading from '../controls/EnhancedLoading';

// 创建具有渐变边框的表格容器
const StyledTableContainer = styled.div`
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  background: white;
  
  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }
  
  .ant-table {
    background: transparent;
  }
  
  .ant-table-thead > tr > th {
    background: linear-gradient(to right, #f6f8fa, #ffffff);
    font-weight: 500;
    color: rgba(0, 0, 0, 0.7);
    font-size: 14px;
    transition: all 0.3s;
    padding: 12px 16px;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .ant-table-thead > tr > th:hover {
    background: linear-gradient(to right, #f0f2f5, #fafafa);
  }
  
  .ant-table-tbody > tr > td {
    color: rgba(0, 0, 0, 0.85);
    transition: all 0.3s;
    padding: 12px 16px;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .ant-table-tbody > tr:hover > td {
    background-color: #f5f7fa;
  }
  
  .ant-table-tbody > tr:last-child > td {
    border-bottom: none;
  }
  
  .ant-table-tbody > tr.ant-table-row:hover > td {
    background-color: rgba(240, 245, 255, 0.7);
  }
  
  .ant-table-row {
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .ant-table-row:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    z-index: 1;
  }
  
  .ant-empty {
    padding: 40px 0;
  }
  
  // 分页样式优化
  .ant-pagination {
    margin: 16px 0;
    padding: 0 16px;
  }
  
  .ant-pagination-item {
    border-radius: 6px;
    transition: all 0.3s;
    overflow: hidden;
    
    &:hover, &.ant-pagination-item-active {
      border-color: #1890ff;
      background: linear-gradient(to bottom, #e6f7ff, #ffffff);
    }
    
    &.ant-pagination-item-active a {
      color: #1890ff;
      font-weight: 500;
    }
  }
  
  .ant-pagination-options {
    .ant-select:hover .ant-select-selector {
      border-color: #1890ff;
    }
    
    .ant-select-selector {
      border-radius: 6px;
      transition: all 0.3s;
    }
  }
  
  .ant-pagination-options-quick-jumper {
    input {
      border-radius: 6px;
      transition: all 0.3s;
      
      &:hover, &:focus {
        border-color: #1890ff;
      }
    }
  }
`;

// 自定义无数据显示
const CustomEmpty = () => (
  <Empty
    image={<CarOutlined style={{ fontSize: 48, color: '#bfbfbf' }} />}
    imageStyle={{ height: 60, marginBottom: 20, opacity: 0.8 }}
    description={
      <div>
        <p style={{ fontSize: 16, marginBottom: 4, color: '#8c8c8c' }}>暂无车辆数据</p>
        <p style={{ fontSize: 14, color: '#bfbfbf' }}>尝试更改搜索条件查看其他结果</p>
      </div>
    }
  />
);

const CarTable = ({ dataSource, loading, pagination, onChange }) => {
  // 列定义，包含排序和筛选
  const columns = [
    {
      title: '车型',
      dataIndex: 'title',
      key: 'title',
      width: 300,
      ellipsis: true,
      render: (text, record) => {
        const hasUrl = record.url && record.url.startsWith('http');
        return hasUrl ? (
          <a 
            href={record.url} 
            target="_blank" 
            rel="noopener noreferrer"
            style={{ 
              color: '#1890ff',
              fontWeight: '500',
              transition: 'color 0.3s'
            }}
            onMouseEnter={(e) => e.target.style.color = '#40a9ff'}
            onMouseLeave={(e) => e.target.style.color = '#1890ff'}
          >
            {text}
          </a>
        ) : (
          <span>{text}</span>
        );
      }
    },
    {
      title: '品牌',
      dataIndex: 'make',
      key: 'make',
      width: 120,
      filters: [
        { text: '丰田', value: '丰田' },
        { text: '本田', value: '本田' },
        { text: '大众', value: '大众' },
        { text: '特斯拉', value: '特斯拉' },
        { text: '宝马', value: '宝马' },
        { text: '奔驰', value: '奔驰' },
        { text: '日产', value: '日产' },
      ],
      onFilter: (value, record) => record.make === value,
    },
    {
      title: '年份',
      dataIndex: 'year',
      key: 'year',
      sorter: (a, b) => a.year - b.year,
      width: 80,
    },
    {
      title: '里程',
      dataIndex: 'miles',
      key: 'miles',
      sorter: (a, b) => a.miles - b.miles,
      width: 100,
      render: (text) => `${text.toLocaleString()} 英里`
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      sorter: (a, b) => a.price - b.price,
      width: 100,
      render: (text) => `$${text.toLocaleString()}`
    },
    {
      title: '交易类型',
      dataIndex: 'trade_type',
      key: 'trade_type',
      width: 100,
      filters: [
        { text: '个人', value: '个人' },
        { text: '经销商', value: '经销商' },
      ],
      onFilter: (value, record) => record.trade_type === value,
      render: (text) => {
        let color = 'default';
        if (text === 'sale' || text === '出售') color = 'green';
        if (text === 'trade' || text === '交换') color = 'blue';
        if (text === 'buy' || text === '买车' || text === '求购') color = 'red';
        if (text === 'rent' || text === '租车') color = 'green';
        return <Tag color={color}>{text || '未知'}</Tag>;
      },
    },
    {
      title: '地点',
      dataIndex: 'location',
      key: 'location',
      width: 140,
      filters: [
        { text: '加州', value: 'California' },
        { text: '德州', value: 'Texas' },
        { text: '纽约', value: 'New York' },
        { text: '佛罗里达', value: 'Florida' },
      ],
      onFilter: (value, record) => record.location && record.location.includes(value),
    },
    {
      title: '上架天数',
      dataIndex: 'daysold',
      key: 'daysold',
      sorter: (a, b) => a.daysold - b.daysold,
      width: 100,
      render: (text) => `${text} 天`
    },
    {
      title: '最后活跃',
      dataIndex: 'last_active',
      key: 'last_active',
      sorter: (a, b) => new Date(a.last_active) - new Date(b.last_active),
      width: 160,
    }
  ];

  return (
    <EnhancedLoading spinning={loading} tip="加载车辆数据中...">
      <StyledTableContainer>
        <Table
          dataSource={dataSource}
          columns={columns}
          rowKey="id"
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            pageSizeOptions: ['10', '20', '50', '100'],
            showTotal: (total) => `共 ${total} 条数据`,
            position: ['bottomCenter'],
          }}
          onChange={onChange}
          loading={false} // 由于我们使用了EnhancedLoading，这里设为false
          locale={{ emptyText: <CustomEmpty /> }}
          scroll={{ x: 1200 }}
        />
      </StyledTableContainer>
    </EnhancedLoading>
  );
};

export default CarTable; 