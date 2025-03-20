import React, { useState, useEffect, useRef } from 'react';
import { Card, Spin, Empty } from 'antd';
import { Chart } from '@antv/g2';
import axios from 'axios';

/**
 * 词云组件
 * 显示帖子标题中的热门词汇
 */
const WordCloud = () => {
  const [loading, setLoading] = useState(true);
  const [hasData, setHasData] = useState(false);
  const [data, setData] = useState([]);
  const chartRef = useRef(null);

  useEffect(() => {
    fetchData();
  }, []);

  // 当数据变化时重新渲染词云
  useEffect(() => {
    if (hasData && data.length > 0) {
      try {
        renderWordCloud();
      } catch (error) {
        console.error('词云渲染出错:', error);
      }
    }
  }, [data, hasData]);

  /**
   * 获取词云数据
   */
  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/title-wordcloud');
      
      // 处理数据
      const wordData = response.data || [];
      
      if (Array.isArray(wordData) && wordData.length > 0) {
        // 转换数据格式以适配词云图表要求
        const chartData = wordData.map((item, index) => {
          // 随机生成x和y坐标
          const x = Math.random() * 800 - 400;
          const y = Math.random() * 800 - 400;
          
          // 归一化词频值
          const maxValue = Math.max(...wordData.map(d => d.value));
          const normalizedValue = item.value / maxValue;
          
          // 根据归一化值计算文本大小
          const size = 12 + normalizedValue * 48;
          
          // 生成彩色系列
          const hue = (index * 10) % 360;
          const color = `hsl(${hue}, 70%, 50%)`;
          
          // 随机旋转角度
          const rotate = Math.random() > 0.5 ? Math.floor(Math.random() * 45) : Math.floor(Math.random() * -45);
          
          return {
            text: item.text,
            value: item.value,
            x,
            y,
            size,
            color,
            rotate
          };
        });
        
        setData(chartData);
        setHasData(true);
      } else {
        setHasData(false);
      }
    } catch (error) {
      console.error('获取词云数据失败:', error);
      setHasData(false);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 渲染词云图表
   */
  const renderWordCloud = () => {
    if (!chartRef.current || !hasData || !data.length) return;

    // 清除之前的图表
    chartRef.current.innerHTML = '';

    // 创建词云图表
    const chart = new Chart({
      container: chartRef.current,
      autoFit: true,
      height: 400,
      padding: [20, 20, 30, 20],
    });

    // 配置数据
    chart.data(data);

    // 配置坐标轴和比例尺
    chart.scale({
      x: { nice: true },
      y: { nice: true },
      size: { 
        type: 'linear',
        range: [12, 60],
      },
    });

    // 关闭图表动画效果以提高性能
    chart.animate(false);

    // 隐藏坐标轴
    chart.axis(false);
    chart.legend(false);
    chart.tooltip({
      showTitle: false,
      showMarkers: false,
      itemTpl: '<li class="g2-tooltip-list-item">'
        + '<span class="g2-tooltip-name">{text}</span>'
        + '<span class="g2-tooltip-value">频次: {value}</span>'
        + '</li>',
    });

    // 渲染文本点
    chart
      .point()
      .position('x*y')
      .size('size')
      .shape('text')
      .text('text')
      .color('color')
      .tooltip('text*value', (text, value) => ({ text, value }))
      .adjust('jitter')  // 添加抖动以避免文本重叠
      .style({
        fontFamily: 'Microsoft YaHei, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial',
        fontWeight: 'normal',
        shadowBlur: 2,
        shadowColor: 'rgba(0, 0, 0, 0.2)',
        rotate: (d) => d.rotate || 0,
      })
      .state({
        active: {
          style: {
            fontSize: (d) => Math.min(d.size * 1.2, 72),
            fontWeight: 'bold',
            shadowColor: '#aaa',
            shadowBlur: 10,
          },
        },
      });

    // 添加交互
    chart.interaction('element-active');

    // 绘制图表
    chart.render();
  };

  return (
    <Card
      title="热门词汇"
      bordered={false}
      bodyStyle={{ height: 450, overflow: 'hidden' }}
    >
      {loading ? (
        <div style={{ height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Spin size="large" />
        </div>
      ) : !hasData ? (
        <Empty description="暂无数据" style={{ marginTop: 150 }} />
      ) : (
        <div ref={chartRef} style={{ width: '100%', height: '100%' }} />
      )}
    </Card>
  );
};

export default WordCloud; 