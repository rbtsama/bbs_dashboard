import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { Layout, Menu, ConfigProvider, theme, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import Dashboard from './pages/Dashboard';
import Rankings from './pages/Rankings';
import FollowedThreads from './pages/FollowedThreads';
import './App.css';

const { Header, Content, Footer } = Layout;

const App = () => {
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
              defaultSelectedKeys={['1']}
              items={[
                {
                  key: '1',
                  label: <Link to="/">数据大盘</Link>,
                },
                {
                  key: '2',
                  label: <Link to="/rankings">排行榜</Link>,
                },
                {
                  key: '3',
                  label: <Link to="/followed">关注列表</Link>,
                },
              ]}
            />
          </Header>
          <Content style={{ padding: '0 50px', marginTop: 20 }}>
            <div className="site-layout-content" style={{ background: '#fff', padding: 24, minHeight: 280 }}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/rankings" element={<Rankings />} />
                <Route path="/followed" element={<FollowedThreads />} />
              </Routes>
            </div>
          </Content>
          <Footer style={{ textAlign: 'center' }}>论坛数据分析展示系统 ©2025</Footer>
        </Layout>
      </AntdApp>
    </ConfigProvider>
  );
};

export default App; 