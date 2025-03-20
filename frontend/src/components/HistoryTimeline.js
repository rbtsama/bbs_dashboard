import styled from 'styled-components';
import { Timeline, Empty, Pagination } from 'antd';

// 统一的时间线基础样式
const BaseTimeline = styled(Timeline)`
  .ant-timeline-item {
    padding-bottom: 18px;
  }
  
  .ant-timeline-item-tail {
    border-inline-start: 2px solid var(--line-color, rgba(5, 5, 5, 0.06));
  }
  
  .ant-timeline-item-head {
    width: 14px;
    height: 14px;
    border-width: 2px;
    background-color: var(--dot-bg-color, white);
  }
  
  .ant-timeline-item-content {
    transition: all 0.3s;
  }
`;

// 完整时间线样式
export const StyledTimeline = styled(BaseTimeline)`
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
  
  .ant-timeline-item-content {
    font-size: 16px;
    line-height: 1.6;
  }
  
  .history-title {
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 6px;
    color: #262626;
    display: flex;
    align-items: center;
    gap: 8px;
    
    a {
      color: #1890ff;
      transition: all 0.3s;
      
      &:hover {
        color: #40a9ff;
        text-decoration: underline;
      }
    }
    
    .icon {
      color: var(--primary-color, #4056F4);
      font-size: 16px;
    }
  }
  
  .history-details {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 4px;
  }
  
  .history-tag {
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 13px;
    background-color: var(--tag-bg-color, #f0f0f0);
    color: var(--tag-text-color, #666);
    
    .tag-icon {
      margin-right: 4px;
      font-size: 14px;
    }
  }
  
  .history-time {
    color: #8c8c8c;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  
  .history-content {
    margin-top: 8px;
    color: #595959;
    font-size: 14px;
    line-height: 1.5;
  }
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.1);
    border-radius: 6px;
    
    &:hover {
      background-color: rgba(0, 0, 0, 0.2);
    }
  }
`;

// 悬停时间线样式
export const HoverTimeline = styled(BaseTimeline)`
  padding: 0;
  margin: 6px 0;
  
  .ant-timeline-item {
    padding-bottom: 14px;
  }
  
  .ant-timeline-item-content {
    font-size: 14px;
    line-height: 1.5;
  }
  
  .history-title {
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
    color: #262626;
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 260px;
    
    a {
      color: #1890ff;
      
      &:hover {
        color: #40a9ff;
      }
    }
  }
  
  .history-details {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .history-tag {
    display: inline-flex;
    align-items: center;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 12px;
    background-color: var(--tag-bg-color, #f0f0f0);
    color: var(--tag-text-color, #666);
    
    .tag-icon {
      margin-right: 3px;
      font-size: 12px;
    }
  }
  
  .history-time {
    color: #8c8c8c;
    font-size: 12px;
  }
`;

// 分页容器样式
export const PaginationContainer = styled.div`
  display: flex;
  justify-content: center;
  padding: 16px;
  border-top: 1px solid #f0f0f0;
`;

// 查看更多按钮样式
export const ViewMoreButton = styled.div`
  color: var(--primary-color, #4056F4);
  font-size: 14px;
  font-weight: 500;
  text-align: center;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s;
  border-top: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  
  &:hover {
    background-color: rgba(var(--primary-color-rgb, 64, 86, 244), 0.05);
    
    .arrow-icon {
      transform: translateX(4px);
    }
  }
  
  .arrow-icon {
    transition: transform 0.3s;
  }
`;

// 空状态样式
export const StyledEmpty = styled(Empty)`
  padding: 40px 0;
  
  .ant-empty-image {
    height: 60px;
  }
  
  .ant-empty-description {
    color: #8c8c8c;
  }
`;

// 自定义分页
export const StyledPagination = styled(Pagination)`
  .ant-pagination-item-active {
    border-color: var(--primary-color, #4056F4);
    
    a {
      color: var(--primary-color, #4056F4);
    }
  }
  
  .ant-pagination-item:hover {
    border-color: var(--primary-color, #4056F4);
    
    a {
      color: var(--primary-color, #4056F4);
    }
  }
  
  .ant-pagination-prev:hover .ant-pagination-item-link,
  .ant-pagination-next:hover .ant-pagination-item-link {
    color: var(--primary-color, #4056F4);
    border-color: var(--primary-color, #4056F4);
  }
`;

export default {
  StyledTimeline,
  HoverTimeline,
  PaginationContainer,
  ViewMoreButton,
  StyledEmpty,
  StyledPagination
}; 