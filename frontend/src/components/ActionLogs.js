import React, { useState, useEffect } from 'react';
import { Timeline, Spin, message } from 'antd';
import axios from 'axios';

const API_BASE_URL = '/api';

const ActionLogs = ({ threadId, url }) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const params = {};
      if (threadId) params.thread_id = threadId;
      if (url) params.url = url;
      params.limit = 100; // 获取较多的记录以显示完整历史

      const response = await axios.get(`${API_BASE_URL}/action-logs`, { params });
      
      // 处理数据，简化action字段
      const processedData = response.data.data.map(item => {
        let action = item.action;
        if (action.includes('重发')) action = '重发';
        else if (action.includes('回帖')) action = '回帖';
        else if (action.includes('删回帖')) action = '删回帖';
        else if (action.includes('新发布')) action = '新发帖';
        else return null; // 过滤掉其他类型的动作

        return {
          ...item,
          action
        };
      }).filter(item => item !== null); // 移除null项

      setData(processedData);
    } catch (error) {
      console.error('获取异动日志失败:', error);
      message.error('获取异动日志失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [threadId, url]);

  const getActionColor = (action) => {
    switch (action) {
      case '重发': return 'blue';
      case '回帖': return 'green';
      case '删回帖': return 'red';
      case '新发帖': return 'purple';
      default: return 'gray';
    }
  };

  return (
    <Spin spinning={loading}>
      <Timeline
        style={{ padding: '16px 24px', maxHeight: '60vh', overflowY: 'auto' }}
        items={data.map(item => ({
          color: getActionColor(item.action),
          children: (
            <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
              <span style={{ marginRight: '12px', fontSize: '15px', fontWeight: 500 }}>{item.action}</span>
              <span style={{ color: '#666' }}>
                {new Date(item.action_time).toLocaleString('zh-CN', {
                  year: 'numeric',
                  month: '2-digit',
                  day: '2-digit',
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false
                })}
              </span>
            </div>
          )
        }))}
      />
    </Spin>
  );
};

// 添加新的HoverActionLogs组件
export const HoverActionLogs = ({ threadId, url, onViewMore }) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);

  const fetchData = async () => {
    setLoading(true);
    try {
      const params = {};
      if (threadId) params.thread_id = threadId;
      if (url) params.url = url;
      params.limit = 10; // 只获取最近10条记录
      params.page = 1;

      const response = await axios.get(`${API_BASE_URL}/action-logs`, { params });
      
      // 处理数据，简化action字段
      const processedData = response.data.data.map(item => {
        let action = item.action;
        if (action.includes('重发')) action = '重发';
        else if (action.includes('回帖')) action = '回帖';
        else if (action.includes('删回帖')) action = '删回帖';
        else if (action.includes('新发布')) action = '新发帖';
        else return null;

        return {
          ...item,
          action
        };
      }).filter(item => item !== null);

      setData(processedData);
      setTotal(response.data.total);
    } catch (error) {
      console.error('获取异动日志失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [threadId, url]);

  const getActionColor = (action) => {
    switch (action) {
      case '重发': return 'blue';
      case '回帖': return 'green';
      case '删回帖': return 'red';
      case '新发帖': return 'purple';
      default: return 'gray';
    }
  };

  return (
    <div style={{ width: '300px', padding: '8px' }}>
      <Spin spinning={loading}>
        <Timeline
          style={{ padding: '4px 0' }}
          size="small"
          items={data.map(item => ({
            color: getActionColor(item.action),
            children: (
              <div style={{ lineHeight: '1.2' }}>
                <span style={{ marginRight: '8px', fontSize: '13px' }}>{item.action}</span>
                <span style={{ color: '#999', fontSize: '12px' }}>
                  {new Date(item.action_time).toLocaleString('zh-CN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: false
                  })}
                </span>
              </div>
            )
          }))}
        />
        {total > 10 && (
          <div 
            style={{ 
              color: '#999', 
              fontSize: '12px', 
              textAlign: 'center', 
              marginTop: '4px',
              cursor: 'pointer',
              borderTop: '1px solid #f0f0f0',
              paddingTop: '4px'
            }}
            onClick={onViewMore}
          >
            超过10条记录，点击查看更多
          </div>
        )}
      </Spin>
    </div>
  );
};

export default ActionLogs; 