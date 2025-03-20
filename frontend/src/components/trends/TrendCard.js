import React from 'react';
import { Card, Spin, Empty } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import styled from 'styled-components';
import { RiseOutlined, FallOutlined } from '@ant-design/icons';

// 样式化卡片组件
const StyledCard = styled(Card)`
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
    background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 100%);
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
`;

// 标题样式
const TitleWrapper = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  
  .trend-icon {
    font-size: 24px;
    
    &.up {
      color: #52c41a;
    }
    
    &.down {
      color: #ff4d4f;
    }
  }
  
  .title-text {
    font-size: 18px;
    font-weight: 600;
  }
  
  .trend-value {
    margin-left: auto;
    font-size: 16px;
    font-weight: 500;
    
    &.up {
      color: #52c41a;
    }
    
    &.down {
      color: #ff4d4f;
    }
  }
`;

// 图表容器样式
const ChartContainer = styled.div`
  height: 300px;
  padding: 16px;
  
  .recharts-default-tooltip {
    background-color: rgba(255, 255, 255, 0.95) !important;
    border: none !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
    padding: 12px !important;
  }
`;

// 自定义工具提示
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ 
        background: 'rgba(255, 255, 255, 0.95)',
        padding: '12px',
        border: 'none',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
      }}>
        <p style={{ margin: 0, fontWeight: 600 }}>{label}</p>
        <p style={{ margin: '8px 0 0', color: '#1890ff' }}>
          {payload[0].value}
        </p>
      </div>
    );
  }
  return null;
};

const TrendCard = ({ 
  title, 
  data, 
  loading, 
  trendValue, 
  trendType = 'value', // 'value' | 'percentage'
  dataKey = 'value',
  color = '#1890ff'
}) => {
  const getTrendIcon = () => {
    if (trendValue > 0) {
      return <RiseOutlined className="trend-icon up" />;
    } else if (trendValue < 0) {
      return <FallOutlined className="trend-icon down" />;
    }
    return null;
  };

  const formatTrendValue = () => {
    const prefix = trendValue > 0 ? '+' : '';
    const suffix = trendType === 'percentage' ? '%' : '';
    return `${prefix}${trendValue}${suffix}`;
  };

  const cardTitle = (
    <TitleWrapper>
      {getTrendIcon()}
      <span className="title-text">{title}</span>
      <span className={`trend-value ${trendValue > 0 ? 'up' : 'down'}`}>
        {formatTrendValue()}
      </span>
    </TitleWrapper>
  );

  return (
    <StyledCard title={cardTitle}>
      <Spin spinning={loading}>
        {data && data.length > 0 ? (
          <ChartContainer>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  stroke="#666"
                  tick={{ fontSize: 12 }}
                />
                <YAxis 
                  stroke="#666"
                  tick={{ fontSize: 12 }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey={dataKey}
                  stroke={color}
                  strokeWidth={2}
                  dot={{ fill: color, strokeWidth: 2 }}
                  activeDot={{ r: 6, strokeWidth: 0 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartContainer>
        ) : (
          <Empty 
            image={Empty.PRESENTED_IMAGE_SIMPLE} 
            description="暂无趋势数据"
          />
        )}
      </Spin>
    </StyledCard>
  );
};

export default TrendCard; 