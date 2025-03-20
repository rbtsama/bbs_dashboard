import React, { useState, useEffect } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { Layout, Menu, ConfigProvider, theme as antTheme, App as AntdApp, Typography, Space } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import customTheme, { colors } from './theme';
import GlobalStyle from './styles/global';
import './App.css';
import { ThemeProvider } from 'styled-components';
import { 
  HomeOutlined, 
  DashboardOutlined, 
  TrophyOutlined, 
  StarOutlined, 
  CarOutlined,
  CompassOutlined,
  RadarChartOutlined,
  PieChartOutlined,
  AreaChartOutlined,
  GlobalOutlined
} from '@ant-design/icons';
import styled from 'styled-components';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

// 样式化组件
const StyledHeader = styled(Header)`
  display: flex;
  align-items: center;
  padding: 0 30px;
  position: sticky;
  top: 0;
  z-index: 1000;
  width: 100%;
  transition: all 0.3s ease;
  background: #001529;
  box-shadow: ${props => props['data-scrolled'] ? 
    '0 2px 8px rgba(0, 0, 0, 0.15)' : 
    'none'};
`;

const LogoContainer = styled.div`
  display: flex;
  align-items: center;
  margin-right: 30px;
`;

const Logo = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 4px;
  background: #1677ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
`;

const LogoText = styled(Title)`
  margin: 0 !important;
  color: white !important;
  font-size: 18px !important;
  font-weight: 500 !important;
  letter-spacing: 0.5px;
`;

const StyledMenu = styled(Menu)`
  flex: 1;
  border-bottom: none;
  background: transparent;
  line-height: 64px;
  
  .ant-menu-item {
    padding: 0 18px;
    margin: 0 4px !important;
    border-radius: 4px;
    transition: all 0.3s ease;
    
    &:hover {
      background-color: rgba(255, 255, 255, 0.05);
    }
    
    &.ant-menu-item-selected {
      background-color: rgba(24, 144, 255, 0.2);
      
      &::after {
        display: none;
      }
    }
  }
  
  .ant-menu-title-content {
    font-size: 15px;
    
    a {
      color: rgba(255, 255, 255, 0.85);
      transition: all 0.3s;
      
      &:hover {
        color: white;
      }
    }
  }
  
  .ant-menu-item-selected .ant-menu-title-content a {
    color: white;
  }
  
  .ant-menu-item .anticon {
    margin-right: 8px;
    font-size: 16px;
  }
`;

const App = () => {
  const location = useLocation();
  const selectedKey = location.pathname === '/' ? '/' : location.pathname;
  
  // 添加滚动监听
  const [isScrolled, setIsScrolled] = useState(false);
  
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 0) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: antTheme.defaultAlgorithm,
        ...customTheme
      }}
    >
      <ThemeProvider theme={customTheme}>
        <GlobalStyle />
        <AntdApp>
          <Layout className="layout" style={{ minHeight: '100vh' }}>
            <StyledHeader data-scrolled={isScrolled}>
              <LogoContainer>
                <Logo>
                  <RadarChartOutlined style={{ color: 'white', fontSize: '18px' }} />
                </Logo>
                <LogoText level={4}>数智罗盘</LogoText>
              </LogoContainer>
              <StyledMenu
                theme="dark"
                mode="horizontal"
                selectedKeys={[selectedKey]}
                items={[
                  {
                    key: '/',
                    icon: <HomeOutlined />,
                    label: <Link to="/">首页</Link>,
                  },
                  {
                    key: '/dashboard',
                    icon: <DashboardOutlined />,
                    label: <Link to="/dashboard">数据大盘</Link>,
                  },
                  {
                    key: '/rankings',
                    icon: <TrophyOutlined />,
                    label: <Link to="/rankings">排行榜</Link>,
                  },
                  {
                    key: '/follows',
                    icon: <StarOutlined />,
                    label: <Link to="/follows">关注列表</Link>,
                  },
                  {
                    key: '/cars',
                    icon: <CarOutlined />,
                    label: <Link to="/cars">全美收车</Link>,
                  },
                ]}
              />
            </StyledHeader>
            <Content style={{ 
              padding: '0 50px', 
              paddingTop: isScrolled ? '84px' : '20px',
              background: '#f5f5f5', 
              minHeight: 'calc(100vh - 64px - 70px)',
              transition: 'padding-top 0.3s'
            }}>
              <Outlet />
            </Content>
            <Footer style={{ 
              textAlign: 'center', 
              fontSize: '14px', 
              padding: '16px 50px',
              background: '#fff',
              color: 'rgba(0, 0, 0, 0.45)'
            }}>
              数智罗盘 ©2024
            </Footer>
          </Layout>
        </AntdApp>
      </ThemeProvider>
    </ConfigProvider>
  );
};

export default App; 