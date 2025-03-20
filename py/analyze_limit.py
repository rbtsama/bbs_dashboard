import pandas as pd
import os
from pathlib import Path

# 设置数据路径
BASE_DIR = Path(__file__).parent.parent
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'

# 检查post_ranking.csv文件
post_ranking_file = PROCESSED_DIR / 'post_ranking.csv'
if post_ranking_file.exists():
    print(f"读取post_ranking.csv...")
    try:
        post_df = pd.read_csv(post_ranking_file)
        
        # 检查repost_count列的最大值、分布情况
        if 'repost_count' in post_df.columns:
            max_repost = post_df['repost_count'].max()
            counts = post_df['repost_count'].value_counts().sort_index()
            print(f"post_ranking.csv中repost_count最大值: {max_repost}")
            print(f"repost_count值分布:\n{counts}")
            
            # 统计大于9的值的数量
            gt_9_count = len(post_df[post_df['repost_count'] > 9])
            total_count = len(post_df)
            print(f"repost_count大于9的记录数: {gt_9_count}/{total_count} ({gt_9_count/total_count*100:.2f}%)")
            
            # 查看前10条记录的repost_count
            print("前10条记录的repost_count:")
            for i, (_, row) in enumerate(post_df.head(10).iterrows()):
                print(f"{i+1}. {row['title'][:30]}... : {row['repost_count']}")
        else:
            print("post_ranking.csv中没有repost_count列")
    except Exception as e:
        print(f"读取post_ranking.csv时出错: {str(e)}")
else:
    print(f"找不到post_ranking.csv文件")

# 检查author_ranking.csv文件
author_ranking_file = PROCESSED_DIR / 'author_ranking.csv'
if author_ranking_file.exists():
    print(f"\n读取author_ranking.csv...")
    try:
        author_df = pd.read_csv(author_ranking_file)
        
        # 检查repost_count列的最大值、分布情况
        if 'repost_count' in author_df.columns:
            max_repost = author_df['repost_count'].max()
            counts = author_df['repost_count'].value_counts().sort_index()
            print(f"author_ranking.csv中repost_count最大值: {max_repost}")
            print(f"repost_count值分布:\n{counts}")
            
            # 统计大于9的值的数量
            gt_9_count = len(author_df[author_df['repost_count'] > 9])
            total_count = len(author_df)
            print(f"repost_count大于9的记录数: {gt_9_count}/{total_count} ({gt_9_count/total_count*100:.2f}%)")
            
            # 查看前10条记录的repost_count
            print("前10条记录的repost_count:")
            for i, (_, row) in enumerate(author_df.head(10).iterrows()):
                print(f"{i+1}. {row['author']} : {row['repost_count']}")
        else:
            print("author_ranking.csv中没有repost_count列")
    except Exception as e:
        print(f"读取author_ranking.csv时出错: {str(e)}")
else:
    print(f"找不到author_ranking.csv文件")

# 检查action.csv文件
action_file = PROCESSED_DIR / 'action.csv'
if action_file.exists():
    print(f"\n读取action.csv...")
    try:
        action_df = pd.read_csv(action_file)
        
        # 统计各类action的数量
        if 'action' in action_df.columns:
            action_counts = action_df['action'].value_counts()
            print(f"action统计:\n{action_counts}")
            
            # 检查重发次数最多的几个URL
            if all(col in action_df.columns for col in ['url', 'action']):
                repost_df = action_df[action_df['action'] == '重发']
                repost_counts = repost_df.groupby('url').size().sort_values(ascending=False)
                
                print("\n重发次数最多的5个URL:")
                for i, (url, count) in enumerate(repost_counts.head(5).items()):
                    # 获取标题
                    titles = action_df[action_df['url'] == url]['title'].unique()
                    title = titles[0] if len(titles) > 0 else "无标题"
                    print(f"{i+1}. {title[:30]}... ({url}): {count}次重发")
        else:
            print("action.csv中没有action列")
    except Exception as e:
        print(f"读取action.csv时出错: {str(e)}")
else:
    print(f"找不到action.csv文件") 