# 添加发帖记录 - 从post.xlsx获取发帖时间
post_records = post_df[post_df['url'] == url]
if not post_records.empty:
    # 找到最早的发帖时间
    post_time = post_records['post_time'].min()
    title = post_records.iloc[0]['title']
    author = post_records.iloc[0]['author']
    
    results.append({
        'thread_id': thread_id,
        'url': url,
        'title': title,
        'author': author,
        'action_time': post_time,
        'action_type': '新发布',
        'source': 'post.xlsx'
    })

# 添加发帖记录 - 从list.xlsx获取发帖时间
list_records = list_df[list_df['url'] == url]
if not list_records.empty:
    # 找到最早的发帖时间
    list_time = list_records['scraping_time'].min()
    title = list_records.iloc[0]['title']
    author = list_records.iloc[0]['author']
    
    results.append({
        'thread_id': thread_id,
        'url': url,
        'title': title,
        'author': author,
        'action_time': list_time,
        'action_type': list_records.iloc[0]['update_reason'],
        'source': 'list.xlsx'
    })

# 创建DataFrame
if results:
    show_progress("正在整理数据")
    result_df = pd.DataFrame(results)
    
    # 确保action_time是datetime类型
    result_df['action_time'] = pd.to_datetime(result_df['action_time'])
    
    # 按照thread_id和action_time排序
    show_progress("正在排序数据")
    result_df.sort_values(['thread_id', 'action_time'], inplace=True)
    
    # 确保所有列都是字符串格式，避免任何潜在的格式问题
    for col in result_df.columns:
        if col == 'action_time':
            # 格式化日期时间
            result_df[col] = result_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            # 其他列转为字符串
            result_df[col] = result_df[col].astype(str)
    
    # 导出到CSV，确保正确处理中文
    show_progress("正在导出数据到CSV")
    try:
        # 先尝试检查文件是否可以访问
        if os.path.exists(OUTPUT_FILE):
            # 尝试重命名文件测试是否被占用
            temp_file = str(OUTPUT_FILE) + '.temp'
            try:
                os.rename(OUTPUT_FILE, temp_file)
                os.rename(temp_file, OUTPUT_FILE)
            except PermissionError:
                # 文件被占用，使用一个临时文件名
                print(f"{Fore.YELLOW}原CSV文件可能被占用，将使用一个新文件名{Style.RESET_ALL}")
                OUTPUT_FILE = PROCESSED_DIR / f'action_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        # 导出到CSV
        result_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print(f"{Fore.GREEN}已将 {len(result_df)} 条帖子异动数据导出到 {OUTPUT_FILE}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}导出CSV时出错: {e}{Style.RESET_ALL}")
        # 尝试使用不同的文件名
        alt_file = PROCESSED_DIR / f'action_alt_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        try:
            result_df.to_csv(alt_file, index=False, encoding='utf-8-sig')
            print(f"{Fore.GREEN}已将数据导出到备用文件: {alt_file}{Style.RESET_ALL}")
            OUTPUT_FILE = alt_file
        except Exception as e2:
            print(f"{Fore.RED}导出备用CSV也失败: {e2}{Style.RESET_ALL}")
    
    # 显示操作类型的统计
    print(f"\n{Fore.GREEN}异动类型统计:{Style.RESET_ALL}")
    action_counts = result_df['action_type'].value_counts()
    for action, count in action_counts.items():
        print(f"{Fore.CYAN}{action}: {count}{Style.RESET_ALL}") 