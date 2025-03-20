import React, { useState, useEffect } from 'react';
import { Card, Spin, Radio, Empty, Segmented, Tooltip, Statistic, Row, Col, Typography } from 'antd';
import { Line } from '@ant-design/plots';
import { LineChartOutlined, ClockCircleOutlined, CalendarOutlined, FieldTimeOutlined, HistoryOutlined, ArrowUpOutlined, InfoCircleOutlined } from '@ant-design/icons';
import axios from 'axios';
import styled from 'styled-components';

const { Title, Text } = Typography;

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
  background: ${props => props.$background || 'linear-gradient(135deg, #ebf5fb 0%, #ffffff 100%)'};
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

// 将英文类型映射为中文的辅助函数
const getChineseTypeName = (englishType) => {
  const typeMap = {
    'repost': '重发',
    'reply': '回帖',
    'delete_reply': '删回帖'
  };
  return typeMap[englishType] || englishType;
};

const UpdateTrendChart = () => {
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState([]);
  const [timeType, setTimeType] = useState('daily');
  const [statistics, setStatistics] = useState({
    total: 0,
    repost: 0,
    reply: 0,
    deleteReply: 0
  });

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API_BASE_URL}/update-trend`, {
          params: { type: timeType }
        });

        console.log('接收到的更新趋势数据:', response.data);

        // 检查响应中是否含有data字段，并且是数组
        const responseData = response.data && response.data.data ? response.data.data : 
                           (Array.isArray(response.data) ? response.data : []);

        console.log('处理前的数据:', responseData);
        
        if (responseData.length > 0) {
          // 处理时间格式
          const processedData = responseData.map(item => {
            console.log('处理单项数据:', item);
            
            // 检查日期时间是否已格式化
            const isAlreadyFormatted = typeof item.datetime === 'string' && 
                                      (item.datetime.includes('点') || item.datetime.includes('/'));
            
            // 解析日期对象(仅在需要时使用)
            let dateValue;
            if (!isAlreadyFormatted) {
              dateValue = new Date(item.datetime);
            }
            
            // 格式化显示时间
            let formattedDatetime;
            
            if (isAlreadyFormatted) {
              // 后端已经格式化的日期，直接使用
              formattedDatetime = item.datetime;
              console.log('使用后端已格式化的日期:', formattedDatetime);
            } else if (timeType === 'hourly') {
              // 小时格式：dd/hh点
              if (!isNaN(dateValue.getTime())) {
                const day = dateValue.getDate();
                const hour = dateValue.getHours();
                formattedDatetime = `${day}/${hour}点`;
              } else {
                formattedDatetime = '无效日期';
                console.error('无效日期:', item.datetime);
              }
            } else if (timeType === 'daily') {
              // 日格式：mm/dd
              const month = dateValue.getMonth() + 1; 
              const day = dateValue.getDate();
              formattedDatetime = `${month}/${day}`;
            } else if (timeType === 'weekly') {
              // 周格式：mm/dd (周一)
              // 获取本周周一的日期
              const weekStart = new Date(dateValue);
              const day = dateValue.getDay() || 7; // 将0转为7，使周日为7
              weekStart.setDate(dateValue.getDate() - day + 1);
              
              const month = weekStart.getMonth() + 1;
              const date = weekStart.getDate();
              formattedDatetime = `${month}/${date}`;
            } else if (timeType === 'monthly') {
              // 月格式：yyyy/mm
              const year = dateValue.getFullYear();
              const month = dateValue.getMonth() + 1;
              formattedDatetime = `${year}/${month}`;
            }
            
            // 将英文类型映射为中文显示
            const chineseType = getChineseTypeName(item.type);
            
            return {
              datetime: formattedDatetime,
              count: Number(item.count || 0),
              updateType: item.type, // 使用原始英文类型名作为分类字段
              originalType: item.type, // 保留原始英文类型
              displayType: chineseType, // 保存中文显示名称
              originalDatetime: item.datetime // 保留原始日期时间
            };
          });
          
          console.log('处理后的数据:', processedData);
          
          // 计算统计数据
          const stats = {
            total: 0,
            repost: 0,
            reply: 0,
            deleteReply: 0
          };
          
          processedData.forEach(item => {
            stats.total += item.count;
            if (item.updateType === 'repost') stats.repost += item.count;
            else if (item.updateType === 'reply') stats.reply += item.count;
            else if (item.updateType === 'delete_reply') stats.deleteReply += item.count;
          });
          
          setStatistics(stats);
          setChartData(processedData);
        } else {
          console.log('更新分布数据格式不正确:', response.data);
          setChartData([]);
          setStatistics({
            total: 0,
            repost: 0,
            reply: 0,
            deleteReply: 0
          });
        }
      } catch (error) {
        console.error('获取更新分布数据失败:', error);
        setChartData([]);
        setStatistics({
          total: 0,
          repost: 0,
          reply: 0,
          deleteReply: 0
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

  // 曲线图配置
  const config = {
    data: chartData.sort((a, b) => {
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
        const dateA = new Date(a.originalDatetime);
        const dateB = new Date(b.originalDatetime);
        return dateA - dateB;
      }
    }),
    xField: 'datetime',
    yField: 'count',
    seriesField: 'updateType', // 使用英文类型作为系列字段
    // 明确配置颜色映射关系
    colorField: 'updateType',
    // 曲线图特有配置
    smooth: true, // 平滑曲线
    // 配置数据点
    point: {
      size: 5,
      shape: 'circle',
    },
    // 使用静态颜色数组而非函数
    color: ({ updateType }) => {
      const colorMap = {
        'repost': '#3498DB',
        'reply': '#27AE60',
        'delete_reply': '#E67E22'
      };
      return colorMap[updateType] || '#999';
    },
    legend: {
      position: 'top',
      itemName: {
        formatter: (text) => {
          // 将英文类型映射为中文显示
          const typeMap = {
            'repost': '重发',
            'reply': '回帖',
            'delete_reply': '删回帖'
          };
          return typeMap[text] || text;
        },
        style: {
          fontSize: 16, // 默认字号+4px
          fontWeight: 500
        }
      }
    },
    tooltip: {
      title: '时间',
      formatter: (datum) => {
        // 显示中文类型
        const displayType = datum.displayType || getChineseTypeName(datum.updateType);
        return { name: displayType, value: datum.count };
      },
      showMarkers: true,
      domStyles: {
        'g2-tooltip': {
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          borderRadius: '8px',
          padding: '12px 16px',
        },
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
      label: {
        formatter: (v) => `${v}`,
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
      { type: 'marker-active' },
      { type: 'element-highlight' },
      { type: 'legend-highlight' },
    ],
    // 提示框配置
    showCrosshairs: true,
    crosshairs: {
      type: 'xy',
      line: {
        style: {
          stroke: '#3498DB',
          lineWidth: 1,
          lineDash: [4, 4],
        },
      },
    },
    animation: {
      appear: {
        animation: 'wave-in',
        duration: 1000,
      },
    },
    // 图表样式
    style: {
      height: 350,
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
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <LineChartOutlined style={{ fontSize: '24px', color: '#3498DB' }} />
          <span>更新趋势</span>
        </div>
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
          <Col xs={24} sm={12} md={6}>
            <StatisticCard $background="linear-gradient(135deg, #ebf5fb 0%, #ffffff 100%)">
              <Statistic 
                title={<><ArrowUpOutlined /> 总更新次数</>}
                value={statistics.total}
                suffix="次"
              />
            </StatisticCard>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <StatisticCard $background="linear-gradient(135deg, #fef5e7 0%, #ffffff 100%)">
              <Statistic 
                title={<><LineChartOutlined /> 重发次数</>}
                value={statistics.repost}
                valueStyle={{ color: '#E67E22' }}
                suffix="次"
              />
            </StatisticCard>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <StatisticCard $background="linear-gradient(135deg, #eafaf1 0%, #ffffff 100%)">
              <Statistic 
                title={<><LineChartOutlined /> 回帖次数</>}
                value={statistics.reply}
                valueStyle={{ color: '#27AE60' }}
                suffix="次"
              />
            </StatisticCard>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <StatisticCard $background="linear-gradient(135deg, #ebf5fb 0%, #ffffff 100%)">
              <Statistic 
                title={<><LineChartOutlined /> 删回帖次数</>}
                value={statistics.deleteReply}
                valueStyle={{ color: '#3498DB' }}
                suffix="次"
              />
            </StatisticCard>
          </Col>
        </Row>
        
        {/* 图表展示 */}
        {chartData.length > 0 ? (
          <div style={{ height: 350, marginTop: 16 }}>
            <Line {...config} />
          </div>
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

export default UpdateTrendChart; 