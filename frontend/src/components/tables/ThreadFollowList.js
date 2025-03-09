import React, { useState, useEffect } from 'react';
import { Card, Table, Spin, Typography, Timeline, message, Button, Modal, Tabs, Space, Popover } from 'antd';
import axios from 'axios';
import ActionLogs, { HoverActionLogs } from '../ActionLogs';

const { Link } = Typography;
const API_BASE_URL = '/api';

const ThreadFollowList = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    showSizeChanger: true
  });
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedThread, setSelectedThread] = useState(null);
  const [activeTab, setActiveTab] = useState('my_follow');

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async (page = 1, pageSize = 10) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/thread-follows`, {
        params: { 
          type: activeTab,
          page,
          limit: pageSize
        }
      });

      setData(response.data.data);
      setPagination({
        ...pagination,
        current: page,
        pageSize: pageSize,
        total: response.data.total
      });
    } catch (error) {
      console.error('获取关注列表失败:', error);
      message.error('获取关注列表失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleTableChange = (newPagination) => {
    fetchData(newPagination.current, newPagination.pageSize);
  };

  const showActionLogs = (thread) => {
    setSelectedThread(thread);
    setModalVisible(true);
  };

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (text, record) => (
        <Link href={record.url} target="_blank" ellipsis>
          {text}
        </Link>
      )
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: 120,
      render: (text, record) => (
        <Link href={record.author_link} target="_blank">
          {text}
        </Link>
      )
    },
    {
      title: '阅读量',
      dataIndex: 'read_count',
      key: 'read_count',
      width: 100,
    },
    {
      title: '重发',
      dataIndex: 'repost_count',
      key: 'repost_count',
      width: 80,
    },
    {
      title: '回帖',
      dataIndex: 'reply_count',
      key: 'reply_count',
      width: 80,
    },
    {
      title: '删回帖',
      dataIndex: 'delete_count',
      key: 'delete_count',
      width: 80,
    },
    {
      title: '发帖天数',
      dataIndex: 'days_old',
      key: 'days_old',
      width: 100,
      render: (text) => text === 0 ? '未知' : `${text}天`
    },
    {
      title: '最近活跃',
      dataIndex: 'last_active',
      key: 'last_active',
      width: 100,
      render: (text) => `${text || 0}天`
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space>
          <Popover
            content={
              <HoverActionLogs
                threadId={record.thread_id}
                url={record.url}
                onViewMore={() => showActionLogs(record)}
              />
            }
            title="异动记录"
            trigger="hover"
            placement="left"
          >
            <Button 
              type="primary" 
              size="middle"
              onClick={() => showActionLogs(record)}
            >
              查看异动
            </Button>
          </Popover>
        </Space>
      )
    }
  ];

  return (
    <>
      <Card style={{ marginTop: 16 }}>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'my_follow',
              label: '我的关注',
              children: (
                <Spin spinning={loading}>
                  <Table
                    columns={columns}
                    dataSource={data}
                    rowKey="thread_id"
                    pagination={pagination}
                    onChange={handleTableChange}
                    scroll={{ x: 'max-content' }}
                  />
                </Spin>
              )
            },
            {
              key: 'my_thread',
              label: '我的帖子',
              children: (
                <Spin spinning={loading}>
                  <Table
                    columns={columns}
                    dataSource={data}
                    rowKey="thread_id"
                    pagination={pagination}
                    onChange={handleTableChange}
                    scroll={{ x: 'max-content' }}
                  />
                </Spin>
              )
            }
          ]}
        />
      </Card>

      <Modal
        title="异动日志"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        width={1000}
        footer={null}
      >
        {selectedThread && (
          <ActionLogs
            threadId={selectedThread.thread_id}
            url={selectedThread.url}
          />
        )}
      </Modal>
    </>
  );
};

export default ThreadFollowList; 