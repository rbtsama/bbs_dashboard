import React, { useState } from 'react';
import { Card } from 'antd';
import customTheme from '../../theme';

const EnhancedCard = ({ 
  children, 
  title, 
  style = {}, 
  bodyStyle = {},
  hoverable = true,
  ...props 
}) => {
  const [isHovered, setIsHovered] = useState(false);
  
  const handleMouseEnter = () => {
    if (hoverable) {
      setIsHovered(true);
    }
  };
  
  const handleMouseLeave = () => {
    if (hoverable) {
      setIsHovered(false);
    }
  };
  
  return (
    <Card
      title={title}
      style={{ 
        boxShadow: isHovered 
          ? '0 4px 16px rgba(0, 0, 0, 0.15)' 
          : customTheme.components.Card.boxShadow,
        borderRadius: customTheme.token.borderRadius,
        transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
        transform: isHovered ? 'translateY(-4px)' : 'translateY(0)',
        border: 'none',
        overflow: 'hidden',
        ...style
      }}
      styles={{
        body: {
          padding: '16px 24px',
          ...bodyStyle
        }
      }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      {...props}
    >
      {children}
    </Card>
  );
};

export default EnhancedCard; 