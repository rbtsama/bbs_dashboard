import axios from 'axios';
import { API_BASE_URL } from '../config';

// 获取昨日新帖
export const getNewPosts = async (params) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/new-posts-yesterday`, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching new posts:', error);
    throw error;
  }
};

// 获取帖子趋势数据
export const fetchPostTrend = async (timeType = 'daily') => {
  try {
    const response = await axios.get(`${API_BASE_URL}/post-trend`, {
      params: { type: timeType }
    });
    return response.data;
  } catch (error) {
    console.error('获取帖子趋势数据失败:', error);
    throw error;
  }
};

// 获取更新数据趋势
export const fetchUpdateTrend = async (timeType = 'daily') => {
  try {
    const response = await axios.get(`${API_BASE_URL}/update-trend`, {
      params: { type: timeType }
    });
    return response.data;
  } catch (error) {
    console.error('获取更新数据趋势失败:', error);
    throw error;
  }
};

// 获取浏览数据趋势
export const fetchViewTrend = async (timeType = 'daily') => {
  try {
    const response = await axios.get(`${API_BASE_URL}/view-trend`, {
      params: { type: timeType }
    });
    return response.data;
  } catch (error) {
    console.error('获取浏览数据趋势失败:', error);
    throw error;
  }
};

// 获取帖子排行榜
export const fetchThreadRanking = async (page = 1, pageSize = 10) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/thread-ranking`, {
      params: { page, page_size: pageSize }
    });
    return response.data;
  } catch (error) {
    console.error('获取帖子排行榜失败:', error);
    throw error;
  }
};

// 获取帖子排行榜（从import表）
export const fetchPostRank = async (page = 1, pageSize = 10) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/post-rank`, {
      params: { 
        page, 
        limit: pageSize
      }
    });
    return response.data;
  } catch (error) {
    console.error('获取帖子排行榜失败:', error);
    throw error;
  }
};

// 获取用户排行榜
export const fetchUserRanking = async (page = 1, pageSize = 10) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/user-ranking`, {
      params: { page, page_size: pageSize }
    });
    return response.data;
  } catch (error) {
    console.error('获取用户排行榜失败:', error);
    throw error;
  }
};

// 获取用户排行榜（从import表）
export const fetchAuthorRank = async (page = 1, pageSize = 10) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/author-rank`, {
      params: { 
        page, 
        limit: pageSize
      }
    });
    return response.data;
  } catch (error) {
    console.error('获取用户排行榜失败:', error);
    throw error;
  }
};

// 获取帖子历史
export const fetchThreadHistory = async (threadId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/thread-history/${threadId}`);
    return response.data;
  } catch (error) {
    console.error(`获取帖子历史失败 (ID: ${threadId}):`, error);
    throw error;
  }
};

// 导入数据
export const importData = async (listFile, postFile) => {
  try {
    const formData = new FormData();
    formData.append('list_file', listFile);
    formData.append('post_file', postFile);
    
    const response = await axios.post(`${API_BASE_URL}/import-data`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    console.error('导入数据失败:', error);
    throw error;
  }
};

// 获取数据趋势
export const fetchDataTrends = async (dataType = 'post', timeType = 'daily') => {
  try {
    const response = await axios.get(`${API_BASE_URL}/data-trends`, {
      params: { type: dataType, time_type: timeType }
    });
    return response.data;
  } catch (error) {
    console.error('获取数据趋势失败:', error);
    throw error;
  }
};

// 获取更新类型分布
export const fetchUpdateDistribution = async (timeType = 'daily') => {
  try {
    const response = await axios.get(`${API_BASE_URL}/update-distribution`, {
      params: { time_type: timeType }
    });
    return response.data;
  } catch (error) {
    console.error('获取更新类型分布失败:', error);
    throw error;
  }
};

// 获取用户活跃度排行
export const fetchUserActivity = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/user-activity`);
    return response.data;
  } catch (error) {
    console.error('获取用户活跃度排行失败:', error);
    throw error;
  }
};

// 获取关注列表
export const fetchThreadFollows = async (type = 'my_follow') => {
  try {
    const response = await axios.get(`${API_BASE_URL}/thread-follows`, {
      params: { type }
    });
    return response.data;
  } catch (error) {
    console.error('获取关注列表失败:', error);
    throw error;
  }
};

// 添加关注
export const addThreadFollow = async (threadId, followType) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/thread-follows`, {
      thread_id: threadId,
      follow_type: followType
    });
    return response.data;
  } catch (error) {
    console.error('添加关注失败:', error);
    throw error;
  }
};

// 取消关注
export const deleteThreadFollow = async (params) => {
  try {
    const response = await axios.delete(`${API_BASE_URL}/thread-follows`, {
      data: params
    });
    return response.data;
  } catch (error) {
    console.error('取消关注失败:', error);
    throw error;
  }
}; 