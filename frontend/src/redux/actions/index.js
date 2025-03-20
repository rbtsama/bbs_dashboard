import { FOLLOW_THREAD, UNFOLLOW_THREAD } from '../reducers/followReducer';

// 关注帖子
export const followThread = (thread) => ({
  type: FOLLOW_THREAD,
  payload: thread,
});

// 取消关注帖子
export const unfollowThread = (threadId) => ({
  type: UNFOLLOW_THREAD,
  payload: threadId,
}); 