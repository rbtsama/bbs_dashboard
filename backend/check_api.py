import json
from modules.rankings import get_post_ranking

# 获取第一页数据，每页1条
result = get_post_ranking(1, 1)
first_post = result['data'][0]

# 打印第一条帖子的详细信息
print("第一条帖子信息:")
print(f"标题: {first_post.get('title', 'N/A')}")
print(f"重发数量: {first_post.get('repost_count', 'N/A')}")
print(f"重发数量类型: {type(first_post.get('repost_count', 'N/A'))}")

# 获取包含"丰田"的帖子
toyota_posts = []
all_posts = get_post_ranking(1, 20)['data']
for post in all_posts:
    if '丰田' in post.get('title', ''):
        toyota_posts.append({
            'title': post.get('title', 'N/A'),
            'repost_count': post.get('repost_count', 'N/A'),
            'repost_count_type': type(post.get('repost_count', 'N/A')).__name__
        })

# 打印包含"丰田"的帖子信息
print("\n包含'丰田'的帖子:")
for i, post in enumerate(toyota_posts, 1):
    print(f"{i}. 标题: {post['title']}")
    print(f"   重发数量: {post['repost_count']} (类型: {post['repost_count_type']})") 