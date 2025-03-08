import React, { useState, useEffect } from 'react';
import { Card, Spin, Empty } from 'antd';
import { Chart } from '@antv/g2';
import axios from 'axios';

const WordCloud = () => {
  const [loading, setLoading] = useState(true);
  const [hasData, setHasData] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/title-wordcloud');
      if (response.data && response.data.length > 0) {
        setHasData(true);
        renderWordCloud(response.data);
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

  const renderWordCloud = (data) => {
    // 清除旧的图表
    const container = document.getElementById('word-cloud-container');
    if (container) {
      container.innerHTML = '';
    }

    // 创建图表实例
    const chart = new Chart({
      container: 'word-cloud-container',
      autoFit: true,
      height: 400,
      padding: [20, 20, 20, 20]
    });

    // 载入数据
    chart.data(data);

    // 设置比例尺
    chart.scale({
      x: { nice: true },
      y: { nice: true },
      size: { nice: true }
    });

    // 配置图形
    chart
      .interval()
      .adjust('stack')
      .position('x*y')
      .size('size')
      .shape('text')
      .label('text', {
        style: {
          fontFamily: 'PingFang SC',
          fontSize: (d) => d.size,
          fill: (d) => d.color || '#666',
          textAlign: 'center',
          textBaseline: 'middle',
          rotate: (d) => d.rotate || 0
        }
      });

    // 去除坐标轴
    chart.axis(false);

    // 去除图例
    chart.legend(false);

    // 配置tooltip
    chart.tooltip({
      showTitle: false,
      showCrosshairs: false,
      showMarkers: false,
      itemTpl: '<li class="g2-tooltip-list-item">{text}: {count}次</li>'
    });

    // 渲染图表
    chart.render();
  };

  return (
    <Card title="热门词汇" style={{ marginTop: 16 }}>
      <Spin spinning={loading}>
        <div id="word-cloud-container" style={{ width: '100%', height: 400 }}>
          {!loading && !hasData && <Empty description="暂无数据" />}
        </div>
      </Spin>
    </Card>
  );
};

export default WordCloud; 