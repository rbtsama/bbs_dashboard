import React, { useState } from 'react';
import { Input } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import styled, { keyframes } from 'styled-components';

const rippleEffect = keyframes`
  0% {
    transform: scale(1);
    opacity: 0.4;
  }
  100% {
    transform: scale(2.5);
    opacity: 0;
  }
`;

const SearchContainer = styled.div`
  position: relative;
  width: ${props => props.width || '100%'};
  height: ${props => props.height || '40px'};
  overflow: hidden;
  border-radius: 8px;
  background: #fff;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  &:focus-within {
    box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
  }
`;

const StyledInput = styled(Input)`
  height: 100%;
  font-size: ${props => props.fontSize || '14px'};
  border: 1px solid rgba(24, 144, 255, 0.1);
  border-radius: 8px;
  padding: 0 16px;
  transition: all 0.3s;

  &:hover, &:focus {
    border-color: #1890ff;
  }

  .ant-input {
    font-size: ${props => props.fontSize || '14px'};
  }

  .ant-input-prefix {
    margin-right: 12px;
  }

  .ant-input-search-button {
    height: 100%;
    width: 60px;
    border-radius: 0 8px 8px 0;
    background: linear-gradient(120deg, #1890ff 0%, #0050b3 100%);
    border: none;
    transition: all 0.3s;

    &:hover {
      opacity: 0.9;
      transform: translateY(-1px);
    }

    &:active {
      transform: translateY(1px);
    }
  }
`;

const RippleEffect = styled.div`
  position: absolute;
  border-radius: 50%;
  background: rgba(24, 144, 255, 0.1);
  pointer-events: none;
  animation: ${rippleEffect} 0.6s linear;
`;

const EnhancedSearch = ({ 
  placeholder = '搜索', 
  onSearch, 
  width,
  height,
  fontSize,
  style = {}
}) => {
  const [ripples, setRipples] = useState([]);
  const [rippleCount, setRippleCount] = useState(0);
  const [searchValue, setSearchValue] = useState('');

  const handleClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const newRipple = {
      id: rippleCount,
      x,
      y
    };

    setRipples([...ripples, newRipple]);
    setRippleCount(rippleCount + 1);

    setTimeout(() => {
      setRipples(prevRipples => prevRipples.filter(r => r.id !== newRipple.id));
    }, 600);
  };

  const handleSearch = () => {
    if (onSearch && typeof onSearch === 'function') {
      onSearch(searchValue);
    }
  };

  const handleChange = (e) => {
    setSearchValue(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <SearchContainer 
      width={width} 
      height={height}
      style={style}
      onClick={handleClick}
    >
      {ripples.map(ripple => (
        <RippleEffect
          key={ripple.id}
          style={{
            left: ripple.x,
            top: ripple.y,
            width: '20px',
            height: '20px',
            transform: 'translate(-50%, -50%)'
          }}
        />
      ))}
      <StyledInput
        placeholder={placeholder}
        value={searchValue}
        onChange={handleChange}
        onKeyPress={handleKeyPress}
        fontSize={fontSize}
        prefix={<SearchOutlined style={{ 
          color: '#1890ff',
          fontSize: '18px'
        }} />}
        suffix={
          <SearchOutlined 
            style={{ 
              color: '#1890ff',
              fontSize: '18px',
              cursor: 'pointer'
            }} 
            onClick={handleSearch}
          />
        }
      />
    </SearchContainer>
  );
};

export default EnhancedSearch; 