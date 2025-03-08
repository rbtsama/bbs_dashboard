import React, { useState, useEffect } from 'react';
import { Card, Spin, Radio, Empty } from 'antd';
import { Line } from '@ant-design/charts';
import axios from 'axios';

const API_BASE_URL = '/api';

const UpdateTrendChart = () => {
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState([]);
  const [timeType, setTimeType] = useState('daily');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        console.log(`请求更新分布数据，时间粒度: ${timeType}`);
        const response = await axios.get(`/api/update-distribution?time_type=${timeType}`);
        console.log('更新分布数据响应:', response.data);
        
        if (response.data && Array.isArray(response.data)) {
          // 根据时间类型格式化日期
          let formattedData = response.data.map(item => {
            let formattedTime;
            let dateValue = item.datetime || item.date_group || item.week_group || item.month_group;
            
            if (timeType === 'hourly') {
              formattedTime = formatDateTime(dateValue);
            } else if (timeType === 'daily') {
              formattedTime = formatDate(dateValue);
            } else if (timeType === 'weekly') {
              formattedTime = formatWeek(dateValue);
            } else {
              formattedTime = formatMonth(dateValue);
            }
            
            return {
              ...item,
              formattedTime,
              // 确保更新类型有中文显示
              updateType: item.updateType === '重发' ? '重发' : 
                          item.updateType === '回帖' ? '回帖' : 
                          item.updateType === '删回帖' ? '删回帖' : item.updateType,
              count: parseInt(item.count || 0)
            };
          });
          
          // 检查是否有数据
          if (formattedData.length === 0) {
            console.log('没有更新分布数据');
            setChartData([]);
            return;
          }
          
          console.log('格式化后的更新分布数据:', formattedData);
          console.log('数据点数量:', formattedData.length);
          
          setChartData(formattedData);
        } else {
          console.log('更新分布数据格式不正确:', response.data);
          setChartData([]);
        }
      } catch (error) {
        console.error('获取更新分布数据失败:', error);
        setChartData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [timeType]);

  // 格式化日期时间（小时维度）
  const formatDateTime = (dateTimeStr) => {
    if (!dateTimeStr) return '';
    try {
      console.log('格式化日期时间:', dateTimeStr);
      const date = new Date(dateTimeStr);
      if (isNaN(date.getTime())) {
        console.log('无效的日期时间:', dateTimeStr);
        return dateTimeStr;
      }
      // 返回"日/小时+点"格式，如"03/7点"
      return `${date.getDate().toString().padStart(2, '0')}/${date.getHours()}点`;
    } catch (e) {
      console.error('格式化日期时间错误:', e);
      return dateTimeStr;
    }
  };

  // 格式化日期
  const formatDate = (dateTimeStr) => {
    if (!dateTimeStr) return '';
    try {
      const date = new Date(dateTimeStr);
      // 返回"月/日"格式
      return `${date.getMonth() + 1}/${date.getDate()}`;
    } catch (e) {
      return dateTimeStr;
    }
  };

  // 格式化月份（年维度）
  const formatMonth = (dateTimeStr) => {
    if (!dateTimeStr) return '';
    try {
      const date = new Date(dateTimeStr);
      // 返回"年/月"格式
      return `${date.getFullYear()}/${(date.getMonth() + 1).toString().padStart(2, '0')}`;
    } catch (e) {
      return dateTimeStr;
    }
  };

  // 格式化周
  const formatWeek = (weekStr) => {
    if (!weekStr) return '';
    try {
      // 如果是YYYY-WW格式（如2025-07表示2025年第7周）
      if (weekStr.includes('-')) {
        const [year, week] = weekStr.split('-').map(Number);
        
        // 计算该年第一天是星期几
        const firstDayOfYear = new Date(year, 0, 1);
        const firstDayOfYearDay = firstDayOfYear.getDay() || 7; // 将0（周日）转换为7
        
        // 计算第一周的第一天（可能在上一年）
        // 如果1月1日是周一到周四，则第一周包含1月1日；如果是周五到周日，则第一周从下周一开始
        const daysToAdd = (firstDayOfYearDay <= 4) ? (1 - firstDayOfYearDay) : (8 - firstDayOfYearDay);
        const firstWeekStart = new Date(year, 0, 1 + daysToAdd);
        
        // 计算目标周的第一天
        const targetWeekStart = new Date(firstWeekStart);
        targetWeekStart.setDate(firstWeekStart.getDate() + (week - 1) * 7);
        
        // 返回"月/日"格式
        return `${targetWeekStart.getMonth() + 1}/${targetWeekStart.getDate()}`;
      } 
      // 如果是日期格式
      else {
        const date = new Date(weekStr);
        // 获取该日期所在周的第一天（周一）
        const day = date.getDay() || 7; // 将0（周日）转换为7
        const diff = date.getDate() - day + 1; // 计算周一的日期
        const weekStart = new Date(date);
        weekStart.setDate(diff);
        
        // 返回"月/日"格式
        return `${weekStart.getMonth() + 1}/${weekStart.getDate()}`;
      }
    } catch (e) {
      console.error('格式化周错误:', e, weekStr);
      return weekStr;
    }
  };

  const handleTimeTypeChange = (e) => {
    setTimeType(e.target.value);
  };

  // 根据时间类型确定X轴字段
  const timeField = 'formattedTime';

  // 曲线图配置
  const config = {
    data: chartData,
    xField: timeField,
    yField: 'count',
    seriesField: 'updateType',
    // 曲线图特有配置
    smooth: true, // 平滑曲线
    // 配置数据点
    point: {
      size: 5,
      shape: 'circle',
      // 确保数据点颜色与线条一致
      style: (datum) => {
        // 根据updateType设置不同的颜色
        let strokeColor = '#1890ff'; // 默认蓝色（重发）
        if (datum.updateType === '回帖') strokeColor = '#006400'; // 深绿色
        if (datum.updateType === '删回帖') strokeColor = '#FF69B4'; // 粉红色
        
        return {
          stroke: strokeColor,
          fill: 'white', // 白色填充
          lineWidth: 2,
        };
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
      formattedTime: {
        alias: '日期',
        type: 'cat',
        range: [0, 1]
      },
      count: {
        alias: '更新数量',
      },
    },
    xAxis: {
      label: {
        autoRotate: true,
        autoHide: false,
        autoEllipsis: false,
      },
      // 设置最小日期为2025年2月12日
      min: new Date('2025-02-12').getTime(),
    },
    // 使用明确的颜色映射
    colorField: 'updateType', // 指定颜色映射字段
    color: ['#1890ff', '#006400', '#FF69B4'], // 蓝色(重发), 深绿色(回帖), 粉红色(删回帖)
    // 交互配置
    interactions: [
      {
        type: 'marker-active',
      },
    ],
    // 提示框配置
    showCrosshairs: true,
    shared: true,
  };

  return (
    <Card 
      title="更新趋势" 
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
          <Line {...config} />
        ) : (
          <Empty description="暂无数据" />
        )}
      </Spin>
    </Card>
  );
};

export default UpdateTrendChart; 