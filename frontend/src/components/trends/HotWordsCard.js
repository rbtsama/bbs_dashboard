import React, { useState } from 'react';
import { Card, Spin, Empty, Radio, List, Tag, Tooltip } from 'antd';
import { CloudOutlined, UnorderedListOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import ReactWordcloud from 'react-wordcloud';

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
  
  .ant-card-extra {
    padding-right: 24px;
  }
`;

// 标题样式
const TitleWrapper = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  
  .icon {
    font-size: 24px;
    color: #1890ff;
  }
  
  .title-text {
    font-size: 18px;
    font-weight: 600;
  }
`;

// 词云容器样式
const WordCloudContainer = styled.div`
  height: 400px;
  padding: 16px;
`;

// 列表样式
const StyledList = styled(List)`
  .ant-list-item {
    padding: 16px 24px;
    transition: all 0.3s;
    
    &:hover {
      background-color: #f0f7ff;
      transform: translateX(4px);
    }
  }
  
  .ant-tag {
    font-size: 14px;
    padding: 4px 8px;
    border-radius: 4px;
    margin-right: 8px;
    
    &.hot-1 { background-color: #fff1f0; color: #f5222d; border-color: #ffa39e; }
    &.hot-2 { background-color: #fff7e6; color: #fa8c16; border-color: #ffd591; }
    &.hot-3 { background-color: #fcffe6; color: #a0d911; border-color: #eaff8f; }
    &.hot-4 { background-color: #f0f5ff; color: #1890ff; border-color: #adc6ff; }
    &.hot-5 { background-color: #f9f0ff; color: #722ed1; border-color: #d3adf7; }
  }
`;

const HotWordsCard = ({ 
  title = '热门词汇',
  data = [], 
  loading = false 
}) => {
  const [viewMode, setViewMode] = useState('cloud'); // 'cloud' | 'list'

  // 词云配置
  const wordcloudOptions = {
    rotations: 2,
    rotationAngles: [-90, 0],
    fontSizes: [14, 48],
    padding: 2,
    colors: ['#f5222d', '#fa8c16', '#a0d911', '#1890ff', '#722ed1'],
  };

  // 获取热度标签样式
  const getHotTagClass = (index) => {
    if (index < 5) return `hot-${index + 1}`;
    return 'hot-5';
  };

  const cardTitle = (
    <TitleWrapper>
      <CloudOutlined className="icon" />
      <span className="title-text">{title}</span>
    </TitleWrapper>
  );

  const cardExtra = (
    <Radio.Group 
      value={viewMode} 
      onChange={(e) => setViewMode(e.target.value)}
      buttonStyle="solid"
    >
      <Radio.Button value="cloud">
        <Tooltip title="词云视图">
          <CloudOutlined />
        </Tooltip>
      </Radio.Button>
      <Radio.Button value="list">
        <Tooltip title="列表视图">
          <UnorderedListOutlined />
        </Tooltip>
      </Radio.Button>
    </Radio.Group>
  );

  const renderContent = () => {
    if (!data || data.length === 0) {
      return <Empty description="暂无热门词汇数据" />;
    }

    if (viewMode === 'cloud') {
      return (
        <WordCloudContainer>
          <ReactWordcloud 
            words={data.map(item => ({
              text: item.word,
              value: item.weight
            }))}
            options={wordcloudOptions}
          />
        </WordCloudContainer>
      );
    }

    return (
      <StyledList
        dataSource={data}
        renderItem={(item, index) => (
          <List.Item>
            <Tag className={getHotTagClass(index)}>
              {`#${index + 1}`}
            </Tag>
            <span style={{ fontSize: '15px' }}>{item.word}</span>
            <span style={{ marginLeft: 'auto', color: '#666' }}>
              {item.count}次
            </span>
          </List.Item>
        )}
      />
    );
  };

  return (
    <StyledCard title={cardTitle} extra={cardExtra}>
      <Spin spinning={loading}>
        {renderContent()}
      </Spin>
    </StyledCard>
  );
};

export default HotWordsCard; 