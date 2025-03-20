import React from 'react';
import { Result, Button } from 'antd';
import { useNavigate, useRouteError } from 'react-router-dom';

const ErrorBoundary = () => {
  const error = useRouteError();
  const navigate = useNavigate();

  return (
    <Result
      status="error"
      title="发生错误"
      subTitle={error?.message || '抱歉，应用程序出现了错误。'}
      extra={[
        <Button type="primary" key="home" onClick={() => navigate('/')}>
          返回首页
        </Button>,
        <Button key="retry" onClick={() => window.location.reload()}>
          重试
        </Button>,
      ]}
    />
  );
};

export default ErrorBoundary; 