import React, { useState, useEffect } from 'react';
import { Typography, Spin, Button } from 'antd';
import styled from 'styled-components';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import ReactWordcloud from 'react-wordcloud';

const { Title, Paragraph } = Typography;

// 样式化容器
const WelcomeContainer = styled.div`
  padding: 0;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  height: calc(100vh - 64px); /* 只减去header的高度 */
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at center, rgba(24, 144, 255, 0.03) 0%, rgba(0, 0, 0, 0) 70%);
    z-index: -1;
  }
  
  &::after {
    content: '';
    position: absolute;
    bottom: -30%;
    right: -30%;
    width: 80%;
    height: 80%;
    background: radial-gradient(circle at center, rgba(114, 46, 209, 0.02) 0%, rgba(0, 0, 0, 0) 70%);
    z-index: -1;
  }
`;

// 标题容器
const TitleContainer = styled.div`
  padding-top: 3vh; /* 增加顶部内边距，使标题向下移动 */
  margin-bottom: 1vh;
  
  .welcome-title {
    margin-bottom: 4px;
    background: linear-gradient(120deg, #1890ff, #722ed1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: min(40px, 4vw);
    font-weight: 700;
    letter-spacing: 1px;
    text-shadow: 0 2px 10px rgba(24, 144, 255, 0.2);
  }
  
  .welcome-subtitle {
    font-size: min(16px, 2vw);
    color: #666;
    margin-bottom: 0;
    max-width: 800px;
  }
`;

// 词云容器 - 简化样式
const WordCloudWrapper = styled.div`
  width: min(95%, 1600px);
  height: 55vh;
  margin: 0 auto;
  margin-top: 1vh;
  margin-bottom: 1vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 0;
  
  /* 保留装饰性圆圈，但简化样式 */
  .tech-circle {
    position: absolute;
    border-radius: 50%;
    opacity: 0.5;
    z-index: -1;
  }
  
  .tech-circle-1 {
    width: 360px;
    height: 360px;
    border: 1px solid rgba(24, 144, 255, 0.1);
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation: rotate 60s linear infinite;
  }
  
  .tech-circle-2 {
    width: 600px;
    height: 600px;
    border: 1px dashed rgba(114, 46, 209, 0.1);
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation: rotate 90s linear infinite reverse;
  }
  
  @keyframes rotate {
    from { transform: translate(-50%, -50%) rotate(0deg); }
    to { transform: translate(-50%, -50%) rotate(360deg); }
  }
  
  @media (max-height: 800px) {
    height: 50vh;
  }
  
  @media (max-height: 700px) {
    height: 45vh;
  }
`;

// 按钮容器 - 简化样式
const ButtonGroup = styled.div`
  margin-top: 0;
  margin-bottom: 1vh;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: min(25px, 2vw);
  width: 100%;
  max-width: 1200px;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    width: 80%;
    height: 1px;
    background: linear-gradient(90deg, 
      rgba(0,0,0,0), 
      rgba(24, 144, 255, 0.2), 
      rgba(114, 46, 209, 0.2), 
      rgba(24, 144, 255, 0.2), 
      rgba(0,0,0,0)
    );
    bottom: -8px;
  }
  
  .btn {
    position: relative;
    height: 50px;
    width: min(200px, 20vw);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    letter-spacing: 1px;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    transform: skewX(-10deg);
    
    span {
      transform: skewX(10deg);
      display: block;
      font-size: min(15px, 1.7vw);
    }
  }
  
  .main-btn {
    background: linear-gradient(135deg, #1890ff, #722ed1, #eb2f96);
    background-size: 300% 300%;
    color: white;
    border: none;
    box-shadow: 0 8px 16px rgba(24, 144, 255, 0.3);
    text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
    z-index: 2;
    
    span {
      font-size: min(18px, 1.9vw);
      font-weight: 700;
    }
    
    &:hover {
      transform: skewX(-10deg) translateY(-5px) scale(1.05);
      box-shadow: 0 12px 24px rgba(24, 144, 255, 0.4);
    }
  }
  
  .secondary-btn {
    height: 50px;
    width: min(180px, 18vw);
    background: rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(24, 144, 255, 0.2);
    color: rgba(0, 0, 0, 0.6);
    
    &:hover {
      color: rgba(24, 144, 255, 0.8);
      border-color: rgba(24, 144, 255, 0.3);
      transform: skewX(-10deg) translateY(-3px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
  }
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 15px;
    
    .btn {
      width: 80%;
      max-width: 280px;
    }
  }
`;

/**
 * 增强的词云组件，提供更好的视觉效果和交互
 * @param {Object} props - 组件属性
 * @param {Array} props.words - 词云数据
 * @param {Object} props.options - 词云配置选项
 * @param {Array} props.size - 词云尺寸
 * @returns {React.Component} - 词云组件
 */
const WordCloudComponent = ({ words, options, size }) => {
  const [selectedWord, setSelectedWord] = useState(null);
  
  // 回调函数 - 当词语被点击时触发
  const getCallback = callback => (word, event) => {
    if (callback) {
      callback(word, event);
    }
    setSelectedWord(word);
    setTimeout(() => setSelectedWord(null), 3000); // 3秒后清除选中状态
  };
  
  // 确保所有必要的属性都有默认值
  const defaultOptions = {
    // 外观设置
    colors: ['#1890ff', '#52c41a', '#722ed1', '#fa8c16', '#eb2f96', '#13c2c2', '#faad14', '#2f54eb', '#f5222d', '#a0d911'],
    enableTooltip: true,
    fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
    fontSizes: [18, 92],
    fontStyle: 'normal',
    fontWeight: 'bold',
    padding: 2,
    
    // 布局设置
    rotations: 3,              // 0-3次旋转
    rotationAngles: [-30, 30], // 旋转角度范围
    spiral: 'rectangular',     // 螺旋排布方式
    scale: 'sqrt',             // 缩放方式
    
    // 交互设置
    deterministic: false,      // 非确定性布局，每次刷新都有变化
    random: Math.random,       // 随机函数
    transitionDuration: 800,   // 过渡动画时间
    
    // 回调函数
    callbacks: {
      onWordClick: getCallback(),
      onWordMouseOver: getCallback(),
      getWordTooltip: word => `${word.text} (${word.value})`,
    },
    ...options
  };
  
  const defaultSize = size || [1200, 480];
  
  // 附加的样式
  const containerStyle = {
    position: 'relative',
    width: '100%',
    height: '100%',
  };
  
  // 如果有选中词语，显示信息
  const selectedWordStyle = {
    position: 'absolute',
    bottom: '10px',
    right: '10px',
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    color: 'white',
    padding: '6px 12px',
    borderRadius: '4px',
    transition: 'all 0.3s ease',
    opacity: selectedWord ? 1 : 0,
    pointerEvents: 'none',
    zIndex: 1000,
  };
  
  return (
    <div style={containerStyle}>
      <ReactWordcloud
        words={words}
        options={defaultOptions}
        size={defaultSize}
      />
      <div style={selectedWordStyle}>
        {selectedWord && `"${selectedWord.text}" - 出现次数: ${selectedWord.value}`}
      </div>
    </div>
  );
};

/**
 * 欢迎页组件
 * @returns {React.Component} - 欢迎页组件
 */
const Welcome = () => {
  const [wordCloudData, setWordCloudData] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  
  useEffect(() => {
    fetchWordCloudData();
  }, []);
  
  /**
   * 获取词云数据
   * @returns {Promise<void>}
   */
  const fetchWordCloudData = async () => {
    try {
      setLoading(true);
      console.log('开始请求词云数据...');
      const response = await axios.get('/api/title-wordcloud');
      console.log('词云API响应:', response);
      
      // 检查响应数据
      if (response.data && Array.isArray(response.data) && response.data.length > 0) {
        // API现在返回标准格式：[{text: "词语", value: 数值}, ...]
        console.log(`获取到 ${response.data.length} 个词云数据项`);
        console.log('数据示例:', response.data.slice(0, 3));
        
        // 验证是否有必要的字段
        if (response.data[0].text && response.data[0].value !== undefined) {
          setWordCloudData(response.data);
        } else {
          console.error('词云数据格式不正确, 缺少必要字段');
          setWordCloudData([]);
        }
      } else {
        console.error('未获取到有效的词云数据');
        setWordCloudData([]);
      }
    } catch (error) {
      console.error('获取词云数据失败:', error);
      setWordCloudData([]);
    } finally {
      setLoading(false);
    }
  };
  
  // 词云配置 - 简化配置
  const wordcloudOptions = {
    rotations: 0,
    fontSizes: [18, 96],
    fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
    fontWeight: 'bold',
    padding: 1,
    deterministic: true,
    enableTooltip: false,
    spiral: 'rectangular',
    transitionDuration: 1000,
    colors: ['#1890ff', '#52c41a', '#722ed1', '#fa8c16', '#eb2f96', '#13c2c2', '#faad14', '#2f54eb', '#f5222d', '#a0d911'],
  };
  
  return (
    <WelcomeContainer className="fade-in">
      <TitleContainer>
        <Title level={1} className="welcome-title">
          洛杉矶华人网论坛数据大盘
        </Title>
        <Paragraph className="welcome-subtitle">
          透视论坛数据，追踪兴趣主题，AI帮你找车
        </Paragraph>
      </TitleContainer>
      
      <WordCloudWrapper>
        <div className="tech-circle tech-circle-1"></div>
        <div className="tech-circle tech-circle-2"></div>
        <Spin spinning={loading} tip="加载词云数据中...">
          {wordCloudData.length > 0 && (
            <WordCloudComponent
              words={wordCloudData}
              options={wordcloudOptions}
              size={[1200, 480]}
            />
          )}
        </Spin>
      </WordCloudWrapper>
      
      <ButtonGroup>
        <Button className="btn secondary-btn" onClick={() => navigate('/rankings')}>
          <span>查看排行榜</span>
        </Button>
        <Button className="btn main-btn" onClick={() => navigate('/dashboard')}>
          <span>进入数据大盘</span>
        </Button>
        <Button className="btn secondary-btn" onClick={() => navigate('/cars')}>
          <span>查看全美收车</span>
        </Button>
      </ButtonGroup>
    </WelcomeContainer>
  );
};

export default Welcome; 