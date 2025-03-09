import React, { useState } from 'react';
import { Table, Button, App } from 'antd';
import { useDispatch } from 'react-redux';
import { followThread } from '../redux/actions';

const NewPostsTable = ({ data = [] }) => {
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10 });
  const dispatch = useDispatch();
  const { message } = App.useApp();
  
  const handleTableChange = (paginationInfo) => {
    setPagination(paginationInfo);
  };
  
  const handleFollow = (record) => {
    // 转换为与 ThreadRankingTable 相同的格式
    const threadData = {
      thread_id: record.thread_id,
      title: record.title,
      author: record.author,
      authorUrl: record.author_url,
      forum: record.forum,
      viewCount: record.views,
      pageNum: record.page_num,
      num: record.num,
      threadUrl: `https://example.com/thread/${record.thread_id}`
    };
    
    dispatch(followThread(threadData));
    message.success(`已关注帖子: ${record.title}`);
  };
  
  const columns = [
    { 
      title: '帖子标题', 
      dataIndex: 'title', 
      key: 'title', 
      ellipsis: true,
      render: (text, record) => (
        <a 
          href={`https://example.com/thread/${record.thread_id}`} 
          target="_blank" 
          rel="noopener noreferrer"
        >
          {text}
        </a>
      )
    },
    { 
      title: '作者', 
      dataIndex: 'author', 
      key: 'author',
      render: (text, record) => (
        <a href={record.author_url} target="_blank" rel="noopener noreferrer">{text}</a>
      )
    },
    { 
      title: '发帖时间', 
      dataIndex: 'post_time', 
      key: 'post_time',
      sorter: (a, b) => new Date(b.post_time) - new Date(a.post_time)
    },
    { title: '板块', dataIndex: 'forum', key: 'forum' },
    { title: '浏览量', dataIndex: 'views', key: 'views' },
    { 
      title: '操作', 
      key: 'action',
      render: (_, record) => (
        <Button type="primary" size="small" onClick={() => handleFollow(record)}>
          关注
        </Button>
      )
    }
  ];
  
  return (
    <div className="new-posts-table">
      <h2>昨日新帖</h2>
      <Table 
        columns={columns} 
        dataSource={data}
        pagination={pagination}
        onChange={handleTableChange}
        rowKey="id"
      />
    </div>
  );
};

export default NewPostsTable; 