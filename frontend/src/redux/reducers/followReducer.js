const initialState = {
  threads: [],
};

// Action Types
export const FOLLOW_THREAD = 'FOLLOW_THREAD';
export const UNFOLLOW_THREAD = 'UNFOLLOW_THREAD';

// Reducer
const followReducer = (state = initialState, action) => {
  switch (action.type) {
    case FOLLOW_THREAD:
      // 检查是否已经关注了该帖子
      if (state.threads.some(thread => thread.thread_id === action.payload.thread_id)) {
        return state;
      }
      return {
        ...state,
        threads: [
          ...state.threads,
          {
            ...action.payload,
            followedAt: new Date().toISOString(),
          },
        ],
      };
    case UNFOLLOW_THREAD:
      return {
        ...state,
        threads: state.threads.filter(thread => thread.thread_id !== action.payload),
      };
    default:
      return state;
  }
};

export default followReducer; 