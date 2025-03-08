import React, { useState, useEffect } from 'react';
import { Card, Spin, Empty } from 'antd';
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
    // 清除旧的内容
    const container = document.getElementById('word-cloud-container');
    if (container) {
      container.innerHTML = '';
    }

    // 创建词云容器
    const cloudContainer = document.createElement('div');
    cloudContainer.style.position = 'relative';
    cloudContainer.style.width = '100%';
    cloudContainer.style.height = '400px';
    cloudContainer.style.display = 'flex';
    cloudContainer.style.alignItems = 'center';
    cloudContainer.style.justifyContent = 'center';

    // 添加每个词
    data.forEach(item => {
      const word = document.createElement('div');
      word.textContent = item.text;
      word.style.position = 'absolute';
      word.style.fontSize = `${item.size}px`;
      word.style.color = item.color;
      word.style.transform = `translate(${item.x}px, ${item.y}px) rotate(${item.rotate}deg)`;
      word.style.cursor = 'pointer';
      word.style.transition = 'all 0.3s';
      word.style.userSelect = 'none';
      word.style.whiteSpace = 'nowrap';

      // 添加悬停效果
      word.addEventListener('mouseover', () => {
        word.style.transform = `translate(${item.x}px, ${item.y}px) rotate(${item.rotate}deg) scale(1.2)`;
        word.style.zIndex = '1';
        // 显示词频提示
        const tooltip = document.createElement('div');
        tooltip.textContent = `${item.text}: ${item.count}次`;
        tooltip.style.position = 'fixed';
        tooltip.style.backgroundColor = 'rgba(0,0,0,0.75)';
        tooltip.style.color = 'white';
        tooltip.style.padding = '4px 8px';
        tooltip.style.borderRadius = '4px';
        tooltip.style.fontSize = '12px';
        tooltip.style.zIndex = '2';
        tooltip.className = 'word-cloud-tooltip';
        document.body.appendChild(tooltip);

        word.addEventListener('mousemove', (e) => {
          tooltip.style.left = `${e.pageX + 10}px`;
          tooltip.style.top = `${e.pageY + 10}px`;
        });

        word.addEventListener('mouseleave', () => {
          tooltip.remove();
          word.style.transform = `translate(${item.x}px, ${item.y}px) rotate(${item.rotate}deg)`;
          word.style.zIndex = 'auto';
        });
      });

      cloudContainer.appendChild(word);
    });

    container.appendChild(cloudContainer);
  };

  return (
    <Card title="热门词汇" style={{ marginTop: 16 }}>
      <Spin spinning={loading}>
        <div id="word-cloud-container" style={{ width: '100%', height: 400, overflow: 'hidden' }}>
          {!loading && !hasData && <Empty description="暂无数据" />}
        </div>
      </Spin>
    </Card>
  );
};

export default WordCloud; 