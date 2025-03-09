import React, { useState, useEffect } from 'react';
import { Card, Spin, Radio, Empty } from 'antd';
import { Column } from '@ant-design/charts';
import axios from 'axios';
import { Link } from 'react-router-dom';

const API_BASE_URL = '/api';

const PostTrendChart = () => {
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState([]);
  const [timeType, setTimeType] = useState('daily');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`/api/data-trends?type=post&time_type=${timeType}`);
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
              datetime: new Date(dateValue)
            };
          });
          
          // 按日期排序（降序）并只取最新的60条数据
          formattedData = formattedData
            .sort((a, b) => b.datetime - a.datetime)
            .slice(0, 60)
            .reverse(); // 反转回来，让图表从左到右是时间顺序
            
          setChartData(formattedData);
        }
      } catch (error) {
        console.error('获取帖子数据失败:', error);
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
      const date = new Date(dateTimeStr);
      // 返回"日/小时+点"格式，如"03/7点"
      return `${date.getDate().toString().padStart(2, '0')}/${date.getHours()}点`;
    } catch (e) {
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

  // 图表配置
  const chartConfig = {
    data: chartData,
    isGroup: true,
    xField: timeField,
    yField: 'count',
    seriesField: 'type',
    height: 300,
    columnStyle: {
      radius: [4, 4, 0, 0],
    },
    label: {
      position: 'top',
      style: {
        fill: '#FFFFFF',
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
      formattedTime: {
        alias: '日期',
        type: 'cat',
        formatter: (text) => text,
        range: [0, 1]
      },
      count: {
        alias: '帖子数',
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
    }
  };

  const columns = [
    {
        title: '标题',
        dataIndex: 'title',
        key: 'title',
        render: (text, record) => (
            <Link to={record.url} target="_blank">
                {text}
            </Link>
        )
    },
    {
        title: '作者',
        dataIndex: 'author',
        key: 'author',
        render: (text, record) => (
            <Link to={record.author_link} target="_blank">
                {text}
            </Link>
        )
    },
    {
        title: '发帖时间',
        dataIndex: 'post_time',
        key: 'post_time',
        render: (text) => formatDateTime(text)
    },
    {
        title: '阅读量',
        dataIndex: 'views',
        key: 'views'
    }
];

  return (
    <Card 
      title="发帖趋势" 
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

export default PostTrendChart; 