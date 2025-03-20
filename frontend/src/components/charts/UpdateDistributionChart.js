import React, { useState, useEffect } from 'react';
import { Card, Spin, Radio, Empty } from 'antd';
import { Column, Pie } from '@ant-design/plots';
import axios from 'axios';

const API_BASE_URL = '/api';

const UpdateDistributionChart = () => {
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState([]);
  const [timeType, setTimeType] = useState('daily');
  const [chartType, setChartType] = useState('column');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API_BASE_URL}/update-distribution`, {
          params: { time_type: timeType }
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
            count: parseInt(item.count),
            // 确保更新类型有中文显示
            updateType: item.updateType === '重发' ? '重发' : 
                        item.updateType === '回帖' ? '回帖' : 
                        item.updateType === '删回帖' ? '删回帖' : item.updateType
          };
        });
        
        setChartData(processedData);
      } catch (error) {
        console.error('获取更新分布数据失败:', error);
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

  const handleChartTypeChange = (e) => {
    setChartType(e.target.value);
  };

  // 柱状图配置
  const columnConfig = {
    data: chartData,
    xField: 'displayValue',
    yField: 'count',
    seriesField: 'updateType',
    isGroup: true,
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
        return { name: datum.updateType, value: datum.count };
      }
    },
    legend: {
      position: 'top',
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
        alias: '更新数量',
      },
    },
    xAxis: {
      label: {
        autoRotate: true,
        formatter: (text) => text
      }
    }
  };

  // 饼图配置
  const pieData = React.useMemo(() => {
    if (chartData.length === 0) return [];
    
    // 按更新类型汇总数据
    const summary = {};
    chartData.forEach(item => {
      if (!summary[item.updateType]) {
        summary[item.updateType] = 0;
      }
      summary[item.updateType] += item.count;
    });
    
    // 转换为饼图数据格式
    return Object.keys(summary).map(key => ({
      type: key,
      value: summary[key]
    }));
  }, [chartData]);

  const pieConfig = {
    data: pieData,
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    height: 300,
    label: {
      type: 'outer',
      content: '{name}: {value}',
    },
    tooltip: {
      formatter: (datum) => {
        return { name: datum.type, value: datum.value };
      }
    },
    interactions: [
      {
        type: 'element-active',
      },
    ],
  };

  return (
    <Card 
      title="更新类型分布" 
      extra={
        <div>
          <Radio.Group 
            value={timeType} 
            onChange={handleTimeTypeChange}
            style={{ marginRight: 16 }}
          >
            <Radio.Button value="hourly">小时</Radio.Button>
            <Radio.Button value="daily">日</Radio.Button>
            <Radio.Button value="weekly">周</Radio.Button>
            <Radio.Button value="monthly">月</Radio.Button>
          </Radio.Group>
          <Radio.Group 
            value={chartType} 
            onChange={handleChartTypeChange}
          >
            <Radio.Button value="column">柱状图</Radio.Button>
            <Radio.Button value="pie">饼图</Radio.Button>
          </Radio.Group>
        </div>
      }
      styles={{
        body: {
          padding: '16px',
          minHeight: '400px'
        }
      }}
    >
      <Spin spinning={loading}>
        {chartData.length > 0 ? (
          chartType === 'column' ? (
            <Column {...columnConfig} />
          ) : (
            <Pie {...pieConfig} />
          )
        ) : (
          <Empty description="暂无数据" />
        )}
      </Spin>
    </Card>
  );
};

export default UpdateDistributionChart; 