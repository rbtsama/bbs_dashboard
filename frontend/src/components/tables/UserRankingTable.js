import React, { useState, useEffect } from 'react';
import { Card, Table, Spin, Typography, Badge, ConfigProvider, Popover, Modal, message } from 'antd';
import { UserOutlined, CrownOutlined, HistoryOutlined, ClockCircleOutlined } from '@ant-design/icons';
import axios from 'axios';
import styled from 'styled-components';
import dayjs from 'dayjs';
import PostHistoryLogs, { HoverPostHistoryLogs } from '../PostHistoryLogs';
import { PostHistoryButton } from '../HistoryButton';
import { PostHistoryModal } from '../HistoryModal';
import { HistoryModalTitle } from '../HistoryButton';

const { Link } = Typography;

const API_BASE_URL = '/api';

// 添加容器样式
const Container = styled.div`
  padding: 0;
  width: 100%;
  
  .ant-pagination {
    display: flex;
    justify-content: center;
    margin-top: 12px;
  }
`;

// 样式化卡片组件
const RankingCard = styled(Card)`
  margin: 0;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(114, 46, 209, 0.08);
  transition: all 0.3s;
  border: none;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
  width: 100%;
  
  &:hover {
    box-shadow: 0 10px 28px rgba(114, 46, 209, 0.15);
  }
  
  &:before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 5px;
    background: linear-gradient(90deg, #722ed1, #b37feb);
    z-index: 2;
  }
  
  .ant-card-head {
    background: linear-gradient(135deg, #f9f0ff 0%, #ffffff 100%);
    border-bottom: 1px solid rgba(114, 46, 209, 0.1);
    padding: 0;
    min-height: 64px;
  }
  
  .ant-card-head-title {
    padding: 16px 24px;
    font-size: 18px;
    font-weight: 600;
  }

  .ant-table {
    font-size: 14px;
    background: transparent;
  }
  
  .ant-table-thead > tr > th {
    background: rgba(249, 240, 255, 0.6);
    font-weight: 600;
    font-size: 14px;
    padding: 14px 16px;
    color: #1f1f1f;
    border-bottom: 1px solid rgba(114, 46, 209, 0.1);
    transition: background 0.3s;
  }
  
  .ant-table-tbody > tr > td {
    padding: 14px 16px;
    transition: background-color 0.3s;
    border-bottom: 1px solid rgba(114, 46, 209, 0.05);
  }
  
  .ant-table-tbody > tr:hover > td {
    background-color: rgba(249, 240, 255, 0.4);
  }
  
  .ant-table-row {
    transition: background-color 0.3s;
    cursor: pointer;
  }
  
  .ant-table-pagination {
    margin: 16px;
  }
  
  @media (max-width: 768px) {
    .ant-card-head-title {
      padding: 14px 16px;
      font-size: 16px;
    }
    
    .ant-table-thead > tr > th,
    .ant-table-tbody > tr > td {
      padding: 12px 12px;
      font-size: 13px;
    }
  }
`;

// 表格标题样式
const TableTitle = styled.div`
  display: flex;
  align-items: center;
  
  .icon {
    margin-right: 16px;
    font-size: 24px;
    color: #722ed1;
    background: linear-gradient(135deg, #f9f0ff, #efdbff);
    padding: 10px;
    border-radius: 12px;
    transition: all 0.3s;
    box-shadow: 0 2px 6px rgba(114, 46, 209, 0.15);
    
    &:hover {
      transform: scale(1.08) rotate(-5deg);
      background: linear-gradient(135deg, #efdbff, #d3adf7);
    }
  }
  
  .title-text {
    font-size: 18px;
    font-weight: 600;
    background: linear-gradient(90deg, #722ed1, #b37feb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }
`;

// 排名样式
const RankNumber = styled.div`
  font-size: 16px;
  font-weight: 600;
  padding: 0 10px;
  color: #262626;
  display: inline-flex;
  align-items: center;
  justify-content: center;
`;

// 样式化链接
const StyledLink = styled(Link)`
  font-size: 15px;
  font-weight: 500;
  color: #722ed1;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  padding-bottom: 2px;
  
  &:after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, #722ed1, transparent);
    transform: scaleX(0);
    transition: transform 0.3s ease;
    transform-origin: left;
  }
  
  &:hover {
    color: #9254de;
    text-decoration: none;
    transform: translateX(3px);
    
    &:after {
      transform: scaleX(1);
    }
  }
  
  @media (max-width: 768px) {
    font-size: 14px;
  }
`;

// 徽章样式
const DataBadge = styled(Badge)`
  .ant-badge-count {
    font-size: 14px;
    font-weight: bold;
    padding: 0 8px;
    background: linear-gradient(135deg, #722ed1, #b37feb);
    box-shadow: 0 2px 4px rgba(114, 46, 209, 0.2);
    border-radius: 12px;
    transition: all 0.3s;
    
    &:hover {
      transform: scale(1.05);
    }
  }
`;

// 添加全局样式
const globalStyles = `
  .user-ranking-table .even-row {
    background-color: #ffffff;
  }
  
  .user-ranking-table .odd-row {
    background-color: #fafafa;
  }
  
  .user-ranking-table .ant-table-cell {
    transition: all 0.3s;
  }
  
  @media (max-width: 576px) {
    .user-ranking-table .ant-table-cell {
      padding: 8px 4px !important;
    }
  }
`;

// 悬停弹窗内容样式
const HoverPopoverContent = styled.div`
  width: 350px;
  padding: 12px;
  
  .post-list {
    max-height: 450px;
    overflow-y: auto;
    padding: 0;
  }
  
  .post-item {
    padding: 16px 20px;
    border-bottom: 1px solid #f0f0f0;
    transition: all 0.3s ease;
    
    &:hover {
      background-color: #f9f9ff;
    }
    
    &:last-child {
      border-bottom: none;
    }
  }
  
  .post-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }
  
  .post-title {
    font-size: 16px !important;
    font-weight: 500;
    color: #1890ff;
    white-space: normal;
    word-break: break-all;
    line-height: 1.5;
    flex: 1;
    margin-right: 20px;
    
    &:hover {
      color: #40a9ff;
    }
  }
  
  .post-time {
    font-size: 14px !important;
    color: #666;
    display: flex;
    align-items: center;
    white-space: nowrap;
    
    .time-icon {
      margin-right: 6px;
      font-size: 14px;
      color: #999;
    }
  }
  
  .event-type {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    margin-right: 8px;
    color: white;
    
    &.repost {
      background-color: #2980B9;
    }
    
    &.reply {
      background-color: #27AE60;
    }
    
    &.delete {
      background-color: #E74C3C;
    }
    
    &.post {
      background-color: #8E44AD;
    }
  }
  
  .view-all-button {
    text-align: center;
    padding: 12px;
    background: #f7f7f7;
    color: #1890ff;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    border-top: 1px solid #f0f0f0;
    
    &:hover {
      background: #e6f7ff;
      color: #40a9ff;
    }
  }
`;

const UserRankingTable = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    showSizeChanger: true
  });
  const [sorter, setSorter] = useState({
    field: 'repost_count',
    order: 'descend'
  });
  
  // 添加异动弹窗的状态
  const [postChangesVisible, setPostChangesVisible] = useState(false);
  const [currentAuthor, setCurrentAuthor] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async (page = 1, pageSize = 10, sortField = sorter.field, sortOrder = sorter.order) => {
    setLoading(true);
    try {
      console.log(`正在获取用户排行榜数据: 页码=${page}, 每页=${pageSize}, 排序字段=${sortField}, 排序方式=${sortOrder}`);
      
      // 确保排序参数正确
      const apiSortOrder = sortOrder === 'descend' ? 'desc' : 
                          sortOrder === 'ascend' ? 'asc' : 'desc';
      
      const response = await axios.get(`${API_BASE_URL}/author-rank`, {
        params: { 
          page, 
          limit: pageSize,
          sort_field: sortField,
          sort_order: apiSortOrder
        }
      });
      
      const responseData = response.data;
      console.log('API返回原始数据:', responseData);
      
      // 检查返回的数据结构
      if (!responseData || !responseData.data || !Array.isArray(responseData.data)) {
        console.error('API返回格式错误:', responseData);
        setData([]);
        setPagination(prev => ({
          ...prev,
          current: page,
          pageSize: pageSize,
          total: 0
        }));
        setLoading(false);
        return;
      }
      
      // 只添加key字段，确保每条记录都有唯一key
      const processedData = responseData.data.map(item => ({
        ...item,
        key: item.author || `${Math.random()}`
      }));
      
      console.log('处理后的数据:', processedData);
      console.log(`返回的总记录数: ${responseData.total}`);
      console.log(`当前页码: ${responseData.page}`);
      console.log(`每页大小: ${responseData.limit}`);
      
      // 更新组件状态
      setData(processedData);
      setPagination(prev => ({
        ...prev,
        current: parseInt(responseData.page) || page,
        pageSize: parseInt(responseData.limit) || pageSize,
        total: parseInt(responseData.total) || 0
      }));
    } catch (error) {
      console.error('获取用户排行榜数据失败:', error);
      if (error.response) {
        console.error('错误响应:', error.response.data);
      }
      message.error('获取数据失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleTableChange = (newPagination, filters, newSorter) => {
    console.log('表格变化:', { newPagination, filters, newSorter });
    
    // 更新排序状态
    if (newSorter && newSorter.field) {
      console.log(`排序变更为: ${newSorter.field} ${newSorter.order || 'descend'}`);
      
      // 更新排序状态
      setSorter({
        field: newSorter.field,
        order: newSorter.order || 'descend'
      });
      
      // 重新请求数据
      fetchData(newPagination.current, newPagination.pageSize, newSorter.field, newSorter.order || 'descend');
      return;
    }
    
    // 如果页码或每页数量变化，重新请求数据
    if (newPagination.current !== pagination.current || 
        newPagination.pageSize !== pagination.pageSize) {
      console.log(`分页变更为: 页码=${newPagination.current}, 每页=${newPagination.pageSize}`);
      fetchData(newPagination.current, newPagination.pageSize, sorter.field, sorter.order);
    }
  };

  // 获取徽章颜色
  const getBadgeColor = (value, field) => {
    if (value <= 0) return '#d9d9d9';
    
    switch (field) {
      case 'post_count':
        return '#555555';
      case 'active_post_count':
        return '#8E44AD';  // 紫色背景
      case 'repost_count':
        return '#2980B9';
      case 'reply_count':
        return '#27AE60';
      case 'delete_reply_count':
        return '#E74C3C';
      default:
        return '#1890ff';
    }
  };

  // 处理查看帖子发帖历史
  const handleViewPostChanges = async (author) => {
    setCurrentAuthor(author);
    setPostChangesVisible(true);
  };

  // 渲染数值徽章，确保正确显示数值
  const renderNumberBadge = (value, fieldName) => {
    // 确保值是数字
    const numValue = parseInt(value, 10) || 0;
    
    return (
      <span 
        style={{ 
          backgroundColor: getBadgeColor(numValue, fieldName),
          fontSize: '14px',
          fontWeight: 'bold',
          padding: '4px 8px',
          borderRadius: '10px',
          color: 'white',
          display: 'inline-block',
          minWidth: '30px',
          textAlign: 'center'
        }} 
      >
        {numValue}
      </span>
    );
  };

  // 修改渲染排名的函数，移除特殊样式
  const renderRankColumn = (text, record, index) => {
    const rank = record.rank || index + 1;
    return <RankNumber>{rank}</RankNumber>;
  };

  const columns = [
    {
      title: '发帖历史',
      dataIndex: 'userpost_logs',
      key: 'userpost_logs',
      width: 120,
      align: 'center',
      fixed: 'left',
      render: (_, record) => {
        return (
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <Popover
              content={
                <HoverPopoverContent>
                  <HoverPostHistoryLogs 
                    author={record.author} 
                    onViewMore={() => handleViewPostChanges(record.author)}
                  />
                </HoverPopoverContent>
              }
              title={<span style={{ fontSize: '16px', fontWeight: 'bold', padding: '16px 20px', display: 'block', borderBottom: '1px solid #f0f0f0' }}>发帖历史</span>}
              trigger="hover"
              placement="right"
              styles={{ 
                body: { padding: 0, borderRadius: '8px', overflow: 'hidden', boxShadow: '0 6px 16px rgba(0, 0, 0, 0.08)' }
              }}
              mouseEnterDelay={0.1}
              mouseLeaveDelay={0.3}
              destroyTooltipOnHide={true}
            >
              <span>
                <PostHistoryButton onClick={() => handleViewPostChanges(record.author)} />
              </span>
            </Popover>
          </div>
        );
      }
    },
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      width: 80,
      align: 'center',
      fixed: 'left',
      render: renderRankColumn
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: '25%',
      ellipsis: true,
      fixed: 'left',
      render: (text, record) => (
        <StyledLink href={record.author_link} target="_blank">
          {text}
        </StyledLink>
      )
    },
    {
      title: '历史帖数',
      dataIndex: 'post_count',
      key: 'post_count',
      width: 100,
      align: 'center',
      responsive: ['sm'],
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'post_count' ? sorter.order : null,
      render: (text) => renderNumberBadge(text, 'post_count')
    },
    {
      title: '活跃帖数',
      dataIndex: 'active_posts',
      key: 'active_posts',
      width: 100,
      align: 'center',
      responsive: ['sm'],
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'active_posts' ? sorter.order : null,
      render: (text) => renderNumberBadge(text, 'active_posts')
    },
    {
      title: '重发',
      dataIndex: 'repost_count',
      key: 'repost_count',
      width: 90,
      align: 'center',
      responsive: ['sm'],
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'repost_count' ? sorter.order : 'descend',
      render: (text) => renderNumberBadge(text, 'repost_count')
    },
    {
      title: '回帖',
      dataIndex: 'reply_count',
      key: 'reply_count',
      width: 90,
      align: 'center',
      responsive: ['md'],
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'reply_count' ? sorter.order : null,
      render: (text) => renderNumberBadge(text, 'reply_count')
    },
    {
      title: '删回帖',
      dataIndex: 'delete_reply_count',
      key: 'delete_reply_count',
      width: 90,
      align: 'center',
      responsive: ['md'],
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'delete_reply_count' ? sorter.order : null,
      render: (text) => renderNumberBadge(text, 'delete_reply_count')
    },
    {
      title: '活跃',
      dataIndex: 'last_active',
      key: 'last_active',
      width: 90,
      align: 'center',
      responsive: ['lg'],
      sorter: true,
      sortDirections: ['descend', 'ascend'],
      defaultSortOrder: sorter.field === 'last_active' ? sorter.order : null,
      render: (text) => <span style={{ fontSize: '14px' }}>{text}天前</span>
    }
  ];

  // 自定义标题
  const title = (
    <TableTitle>
      <UserOutlined className="icon" />
      <span className="title-text">作者排行榜</span>
    </TableTitle>
  );

  return (
    <Container>
      <RankingCard 
        title={title} 
        styles={{
          body: { padding: '0' }
        }}
      >
        <ConfigProvider
          theme={{
            components: {
              Table: {
                borderColor: '#f0f0f0',
                headerBg: '#fafafa',
                headerColor: 'rgba(0, 0, 0, 0.85)',
                headerSplitColor: '#f0f0f0',
                rowHoverBg: '#e6f7ff',
                padding: 12,
                paddingXS: 8,
                paddingLG: 16,
              },
              Pagination: {
                colorBgContainer: '#ffffff',
                colorPrimary: '#1890ff',
                colorPrimaryHover: '#40a9ff',
                colorText: 'rgba(0, 0, 0, 0.88)',
                colorTextDisabled: 'rgba(0, 0, 0, 0.25)',
                controlHeight: 32,
                fontSizeSM: 14,
                itemActiveBg: '#1890ff',
                itemSize: 32,
                colorTextItemSelected: '#ffffff',
                colorBgTextHover: '#e6f4ff',
                colorBgTextActive: '#1890ff',
                colorTextActive: '#ffffff'
              },
            },
          }}
        >
          <style>{globalStyles}</style>
          <Spin spinning={loading}>
            <Table
              columns={columns}
              dataSource={data}
              rowKey="author"
              pagination={{
                ...pagination,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条记录`,
                position: ['bottomCenter'],
                responsive: true,
              }}
              onChange={handleTableChange}
              scroll={{ x: 'max-content' }}
              size="middle"
              rowClassName={(record, index) => index % 2 === 0 ? 'even-row' : 'odd-row'}
              tableLayout="fixed"
              className="user-ranking-table"
            />
          </Spin>
        </ConfigProvider>
      </RankingCard>

      {/* 添加发帖历史弹窗 */}
      <PostHistoryModal
        visible={postChangesVisible}
        onCancel={() => setPostChangesVisible(false)}
        title={
          <HistoryModalTitle>
            <ClockCircleOutlined className="icon" />
            <span className="text">{currentAuthor || ''} 的发帖历史</span>
          </HistoryModalTitle>
        }
      >
        <PostHistoryLogs author={currentAuthor} />
      </PostHistoryModal>
    </Container>
  );
};

export default UserRankingTable; 