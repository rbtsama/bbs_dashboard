import React, { useState, useEffect } from 'react';
import { Card, Spin, Empty, Segmented, Row, Col, Statistic } from 'antd';
import { Column } from '@ant-design/plots';
import { EyeOutlined, RiseOutlined, ClockCircleOutlined, CalendarOutlined, FieldTimeOutlined, HistoryOutlined } from '@ant-design/icons';
import axios from 'axios';
import styled from 'styled-components';

const API_BASE_URL = '/api';

// 现代化卡片样式
const ModernCard = styled(Card)`
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
    background: linear-gradient(135deg, #ebf5fb 0%, #ffffff 100%);
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
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .ant-card-head-wrapper {
    width: 100%;
  }
  
  .ant-card-extra {
    padding: 16px 24px;
  }
`;

// 统计卡片样式
const StatisticCard = styled.div`
  background: ${props => props.background || 'linear-gradient(135deg, #ebf5fb 0%, #ffffff 100%)'};
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
  
  .ant-statistic-title {
    color: rgba(0, 0, 0, 0.65);
    font-size: 14px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .ant-statistic-content {
    color: #3498DB;
    font-size: 24px;
    font-weight: 600;
  }
`;

// 时间选择器样式
const TimeSegmented = styled(Segmented)`
  background: #f5f5f5;
  border-radius: 8px;
  padding: 4px;
  
  .ant-segmented-item {
    transition: all 0.3s;
    border-radius: 6px;
    
    &:hover:not(.ant-segmented-item-selected) {
      color: #3498DB;
      background: rgba(52, 152, 219, 0.1);
    }
  }
  
  .ant-segmented-item-selected {
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .ant-segmented-thumb {
    background: #ffffff;
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
`;

const ViewTrendChart = () => {
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState([]);
  const [timeType, setTimeType] = useState('daily');
  const [statistics, setStatistics] = useState({
    total: 0,
    average: 0,
    max: 0
  });

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API_BASE_URL}/view-trend`, {
          params: { type: timeType }
        });

        console.log('接收到的阅读趋势数据:', response.data);

        // 检查响应中是否含有data字段，并且是数组
        const responseData = response.data && response.data.data ? response.data.data : 
                           (Array.isArray(response.data) ? response.data : []);

        if (responseData.length > 0) {
          let formattedData = responseData.map(item => {
            // 检查日期时间是否已格式化
            const isAlreadyFormatted = typeof item.datetime === 'string' && 
                                      (item.datetime.includes('点') || item.datetime.includes('/'));
            
            let formattedTime;
            
            if (isAlreadyFormatted) {
              // 后端已经格式化的日期，直接使用
              formattedTime = item.datetime;
            } else {
              // 将原始日期时间保存用于排序
              const dateValue = new Date(item.datetime);
              
              if (timeType === 'hourly') {
                // 小时格式：dd/hh点
                const day = dateValue.getDate();
                const hour = dateValue.getHours();
                formattedTime = `${day}/${hour}点`;
              } else if (timeType === 'daily') {
                // 日格式：mm/dd
                const month = dateValue.getMonth() + 1;
                const day = dateValue.getDate();
                formattedTime = `${month}/${day}`;
              } else if (timeType === 'weekly') {
                // 周格式：mm/dd (周一)
                // 获取本周周一的日期
                const weekStart = new Date(dateValue);
                const day = dateValue.getDay() || 7; // 将0转为7，使周日为7
                weekStart.setDate(dateValue.getDate() - day + 1);
                
                const month = weekStart.getMonth() + 1;
                const date = weekStart.getDate();
                formattedTime = `${month}/${date}`;
              } else if (timeType === 'monthly') {
                // 月格式：yyyy/mm
                const year = dateValue.getFullYear();
                const month = dateValue.getMonth() + 1;
                formattedTime = `${year}/${month}`;
              }
            }
            
            return {
              ...item,
              datetime: formattedTime,
              count: Number(item.count || 0),
              originalDatetime: item.datetime // 使用原始datetime字符串而不是dateValue对象
            };
          });
          
          // 按日期正序排序
          formattedData = formattedData
            .sort((a, b) => {
              // 对于已格式化的日期，我们需要基于日期和小时进行比较
              if (timeType === 'hourly') {
                // 格式: "日/小时点"
                const getDateHour = (str) => {
                  const match = str.match(/(\d+)\/(\d+)点/);
                  if (match) {
                    return {
                      day: parseInt(match[1], 10),
                      hour: parseInt(match[2], 10)
                    };
                  }
                  return { day: 0, hour: 0 };
                };
                
                const dateA = getDateHour(a.datetime);
                const dateB = getDateHour(b.datetime);
                
                // 先比较日期，再比较小时
                if (dateA.day !== dateB.day) {
                  return dateA.day - dateB.day;
                }
                return dateA.hour - dateB.hour;
              } else {
                // 确保按照原始日期时间的顺序排序，而不是格式化后的显示文本
                return new Date(a.originalDatetime) - new Date(b.originalDatetime);
              }
            });
          
          // 计算统计数据
          const counts = formattedData.map(item => item.count);
          const total = counts.reduce((sum, count) => sum + count, 0);
          const average = counts.length > 0 ? Math.round(total / counts.length) : 0;
          const max = counts.length > 0 ? Math.max(...counts) : 0;
          
          setStatistics({
            total,
            average,
            max
          });
          
          setChartData(formattedData);
        }
      } catch (error) {
        console.error('获取阅读趋势数据失败:', error);
        setChartData([]);
        setStatistics({
          total: 0,
          average: 0,
          max: 0
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [timeType]);

  const handleTimeTypeChange = (value) => {
    setTimeType(value);
  };

  // 图表配置
  const config = {
    data: chartData,
    xField: 'datetime',
    yField: 'count',
    height: 300,
    columnStyle: {
      radius: [6, 6, 0, 0],
      fill: '#3498DB',
      fillOpacity: 0.85,
      shadowColor: 'rgba(52, 152, 219, 0.2)',
      shadowBlur: 10,
    },
    label: {
      position: 'top',
      style: {
        fill: '#FFFFFF',
        opacity: 1,
        fontSize: 12,
        fontWeight: 400,
      },
    },
    tooltip: {
      title: '时间',
      formatter: (datum) => {
        return { name: '阅读量', value: datum.count };
      },
      domStyles: {
        'g2-tooltip': {
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          borderRadius: '8px',
          padding: '12px 16px',
        },
        'g2-tooltip-title': {
          fontWeight: 600,
          marginBottom: '8px',
        },
        'g2-tooltip-list-item': {
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '4px',
        },
        'g2-tooltip-marker': {
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          marginRight: '8px',
        },
        'g2-tooltip-value': {
          fontWeight: 600,
          marginLeft: '16px',
        },
      },
    },
    meta: {
      datetime: {
        alias: '日期',
        type: 'cat',
        formatter: (text) => text,
        range: [0, 1]
      },
      count: {
        alias: '阅读量',
        formatter: (v) => `${v} 次`,
      },
    },
    xAxis: {
      label: {
        autoRotate: true,
        autoHide: false,
        autoEllipsis: false,
      },
      grid: {
        line: {
          style: {
            stroke: '#f5f5f5',
            lineWidth: 1,
            lineDash: [4, 4],
          },
        },
      },
    },
    yAxis: {
      title: {
        text: '阅读量',
        style: {
          fontSize: 14,
          fill: '#666',
        }
      },
      grid: {
        line: {
          style: {
            stroke: '#f5f5f5',
            lineWidth: 1,
            lineDash: [4, 4],
          },
        },
      },
    },
    // 交互配置
    interactions: [
      { type: 'element-active' },
    ],
    // 动画配置
    animation: {
      appear: {
        animation: 'wave-in',
        duration: 1000,
      },
    },
  };

  // 时间选择器选项
  const timeOptions = [
    {
      value: 'hourly',
      icon: <ClockCircleOutlined />,
      label: '小时',
    },
    {
      value: 'daily',
      icon: <CalendarOutlined />,
      label: '日',
    },
    {
      value: 'weekly',
      icon: <FieldTimeOutlined />,
      label: '周',
    },
    {
      value: 'monthly',
      icon: <HistoryOutlined />,
      label: '月',
    },
  ];

  return (
    <ModernCard 
      title={
        <>
          <EyeOutlined style={{ fontSize: 24, color: '#3498DB' }} />
          <span>阅读趋势</span>
        </>
      }
      extra={
        <TimeSegmented 
          value={timeType} 
          onChange={handleTimeTypeChange}
          options={timeOptions}
        />
      }
      styles={{
        body: {
          padding: '16px',
          minHeight: '400px'
        }
      }}
    >
      <Spin spinning={loading}>
        {/* 统计数据展示 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={8}>
            <StatisticCard background="linear-gradient(135deg, #ebf5fb 0%, #ffffff 100%)">
              <Statistic 
                title={<><EyeOutlined /> 总阅读量</>}
                value={statistics.total}
                valueStyle={{ color: '#3498DB' }}
                suffix="次"
              />
            </StatisticCard>
          </Col>
          <Col xs={24} sm={8}>
            <StatisticCard background="linear-gradient(135deg, #eafaf1 0%, #ffffff 100%)">
              <Statistic 
                title={<><RiseOutlined /> 平均阅读量</>}
                value={statistics.average}
                valueStyle={{ color: '#27AE60' }}
                suffix="次/天"
              />
            </StatisticCard>
          </Col>
          <Col xs={24} sm={8}>
            <StatisticCard background="linear-gradient(135deg, #fef5e7 0%, #ffffff 100%)">
              <Statistic 
                title={<><EyeOutlined /> 最高阅读量</>}
                value={statistics.max}
                valueStyle={{ color: '#E67E22' }}
                suffix="次"
              />
            </StatisticCard>
          </Col>
        </Row>
        
        {/* 图表展示 */}
        {chartData.length > 0 ? (
          <Column {...config} />
        ) : (
          <Empty 
            description="暂无数据" 
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            style={{ margin: '80px 0' }}
          />
        )}
      </Spin>
    </ModernCard>
  );
};

export default ViewTrendChart; 