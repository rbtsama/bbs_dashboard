import React from 'react';
import { Typography } from 'antd';
import customTheme from '../../theme';

const { Title } = Typography;

const PageTitle = ({ 
  title, 
  icon, 
  level = 4, 
  style = {} 
}) => {
  return (
    <div 
      style={{ 
        display: 'flex', 
        alignItems: 'center',
        position: 'relative',
        ...style
      }}
    >
      {icon && (
        <span 
          style={{ 
            marginRight: 12, 
            fontSize: level === 4 ? 20 : level === 3 ? 24 : 28,
            color: customTheme.token.colorPrimary,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: `rgba(24, 144, 255, 0.1)`,
            width: level === 4 ? 36 : level === 3 ? 40 : 48,
            height: level === 4 ? 36 : level === 3 ? 40 : 48,
            borderRadius: '50%',
            transition: 'all 0.3s',
          }}
        >
          {icon}
        </span>
      )}
      <Title 
        level={level} 
        style={{ 
          margin: 0,
          position: 'relative',
          display: 'inline-block',
        }}
      >
        {title}
        <div 
          style={{
            position: 'absolute',
            bottom: '-2px',
            left: '0',
            width: '40%',
            height: '3px',
            background: customTheme.token.colorPrimary,
            borderRadius: '2px',
          }}
        />
      </Title>
    </div>
  );
};

export default PageTitle; 