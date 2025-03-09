import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { Layout, Menu, ConfigProvider, theme, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import './App.css';

const { Header, Content, Footer } = Layout;

const App = () => {
  const location = useLocation();
  const selectedKey = location.pathname === '/' ? '/dashboard' : location.pathname;

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <AntdApp>
        <Layout className="layout" style={{ minHeight: '100vh' }}>
          <Header>
            <div className="logo" />
            <Menu
              theme="dark"
              mode="horizontal"
              selectedKeys={[selectedKey]}
              items={[
                {
                  key: '/dashboard',
                  label: <Link to="/dashboard">数据大盘</Link>,
                },
                {
                  key: '/rankings',
                  label: <Link to="/rankings">排行榜</Link>,
                },
                {
                  key: '/follows',
                  label: <Link to="/follows">关注列表</Link>,
                },
              ]}
            />
          </Header>
          <Content style={{ padding: '0 50px', marginTop: 20 }}>
            <div className="site-layout-content" style={{ background: '#fff', padding: 24, minHeight: 280 }}>
              <Outlet />
            </div>
          </Content>
          <Footer style={{ textAlign: 'center' }}>论坛数据分析展示系统 ©2025</Footer>
        </Layout>
      </AntdApp>
    </ConfigProvider>
  );
};

export default App; 