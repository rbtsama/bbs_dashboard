import React, { useState, useEffect } from 'react';
import { Card, Spin, Radio, Empty } from 'antd';
import { Column } from '@ant-design/charts';
import axios from 'axios';

const API_BASE_URL = '/api';

const PostDataChart = () => {
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState([]);
  const [timeType, setTimeType] = useState('daily');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API_BASE_URL}/data-trends`, {
          params: { type: 'post', time_type: timeType }
        });
        
        // 处理数据
        const processedData = response.data.map(item => {
          let displayValue = '';
          
          if (timeType === 'hourly') {
            // 小时数据，使用datetime
            displayValue = item.datetime;
          } else if (timeType === 'daily') {
            // 日数据，格式化为"2月5日"
            if (item.date && /^\d{1,2}$/.test(item.date)) {
              displayValue = `2月${parseInt(item.date)}日`;
            } else {
              displayValue = item.date || item.datetime;
            }
          } else if (timeType === 'weekly') {
            // 周数据，使用week字段，格式化为"2月5日"
            if (item.week && /^(\d{2})(\d{2})$/.test(item.week)) {
              const matches = item.week.match(/^(\d{2})(\d{2})$/);
              displayValue = `${parseInt(matches[1])}月${parseInt(matches[2])}日`;
            } else {
              displayValue = item.week || item.datetime;
            }
          } else if (timeType === 'monthly') {
            // 月数据，格式化为"2025年2月"
            if (item.month && /^(\d{2})(\d{2})$/.test(item.month)) {
              const matches = item.month.match(/^(\d{2})(\d{2})$/);
              displayValue = `20${matches[1]}年${parseInt(matches[2])}月`;
            } else {
              displayValue = item.month || item.datetime;
            }
          }
          
          return {
            ...item,
            displayValue: displayValue,
            count: parseInt(item.count)
          };
        });
        
        setChartData(processedData);
      } catch (error) {
        console.error('获取帖子数据失败:', error);
        setChartData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [timeType]);

  const handleTimeTypeChange = (e) => {
    setTimeType(e.target.value);
  };

  // 图表配置
  const chartConfig = {
    data: chartData,
    xField: 'displayValue',
    yField: 'count',
    height: 300,
    columnStyle: {
      radius: [4, 4, 0, 0],
    },
    label: {
      position: 'top',
      style: {
        opacity: 0.6,
      },
    },
    tooltip: {
      title: '时间',
      formatter: (datum) => {
        return { name: '帖子数', value: datum.count };
      }
    },
    meta: {
      displayValue: {
        alias: '日期',
        type: 'cat',
        // 确保坐标轴标签按照数据顺序显示
        formatter: (text) => text,
        // 自定义坐标轴范围
        range: [0, 1]
      },
      count: {
        alias: '帖子数',
      },
    },
    xAxis: {
      label: {
        autoRotate: true,
        formatter: (text) => text
      }
    }
  };

  return (
    <Card 
      title="帖子数据统计" 
      extra={
        <Radio.Group 
          value={timeType} 
          onChange={handleTimeTypeChange}
        >
          <Radio.Button value="hourly">小时</Radio.Button>
          <Radio.Button value="daily">日</Radio.Button>
          <Radio.Button value="weekly">周</Radio.Button>
          <Radio.Button value="monthly">月</Radio.Button>
        </Radio.Group>
      }
    >
      <Spin spinning={loading}>
        {chartData.length > 0 ? (
          <Column {...chartConfig} />
        ) : (
          <Empty description="暂无数据" />
        )}
      </Spin>
    </Card>
  );
};

export default PostDataChart; 