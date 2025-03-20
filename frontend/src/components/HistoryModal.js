import React from 'react';
import styled from 'styled-components';
import { Modal } from 'antd';
import { UserOutlined } from '@ant-design/icons';

// 统一的模态框样式
const StyledModal = styled(Modal)`
  .ant-modal-content {
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  }
  
  .ant-modal-header {
    padding: 22px 24px;
    background: linear-gradient(135deg, var(--primary-color, #4056F4), var(--secondary-color, #01CDFE));
    border-bottom: none;
  }
  
  .ant-modal-title {
    color: white;
    font-size: 20px;
    font-weight: 600;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  }
  
  .ant-modal-close {
    color: rgba(255, 255, 255, 0.85);
    transition: all 0.3s;
    top: 18px;
    right: 20px;
    
    &:hover {
      color: white;
      transform: rotate(90deg);
    }
  }
  
  .ant-modal-body {
    padding: 0;
  }
  
  .ant-modal-footer {
    border-top: none;
    padding: 16px 24px;
  }
`;

// 内容容器样式
const ModalContent = styled.div`
  padding: 0;
`;

// 帖子信息样式
const PostInfoSection = styled.div`
  padding: 18px 24px;
  background-color: #f9faff;
  border-bottom: 1px solid #f0f0f0;
  
  h3 {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 10px;
    color: #262626;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .post-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    color: #666;
    font-size: 14px;
    
    .meta-item {
      display: flex;
      align-items: center;
      margin-right: 18px;
      margin-bottom: 6px;
      
      .anticon {
        margin-right: 6px;
        color: var(--primary-color, #4056F4);
      }
    }
  }
`;

// 更新历史模态框 - 紫色主题
export const UpdateHistoryModal = ({ 
  visible, 
  onCancel, 
  title, 
  postInfo,
  children 
}) => (
  <StyledModal
    open={visible}
    onCancel={onCancel}
    footer={null}
    width={800}
    centered
    title={title}
    style={{ '--primary-color': '#9B5DE5', '--secondary-color': '#7209B7' }}
  >
    <ModalContent>
      {children}
    </ModalContent>
  </StyledModal>
);

// 发帖历史模态框 - 红色主题
export const PostHistoryModal = ({ 
  visible, 
  onCancel, 
  title, 
  children 
}) => (
  <StyledModal
    open={visible}
    onCancel={onCancel}
    footer={null}
    width={800}
    centered
    title={title}
    style={{ '--primary-color': '#E74C3C', '--secondary-color': '#C0392B' }}
  >
    <ModalContent>
      {children}
    </ModalContent>
  </StyledModal>
);

export default {
  UpdateHistoryModal,
  PostHistoryModal
}; 