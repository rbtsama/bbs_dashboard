# 词云生成

本文档描述系统的词云生成功能，包括生成流程、任务管理和缓存机制。

## 词云功能概述

系统支持为作者和帖子生成词云，直观展示内容关键词分布。词云生成是一个计算密集型任务，系统采用异步任务处理和缓存机制确保性能。

## 词云相关表结构

系统使用两个表管理词云生成：

1. **wordcloud_job 表**：管理词云生成任务
   ```sql
   CREATE TABLE IF NOT EXISTS wordcloud_job (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       job_type TEXT NOT NULL,           -- 任务类型(author/thread)
       target_id TEXT NOT NULL,          -- 目标ID(作者名或帖子ID)
       status TEXT NOT NULL,             -- 状态(pending/processing/completed/failed)
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
       updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
       error_message TEXT                -- 错误信息
   );
   ```

2. **wordcloud_cache 表**：缓存生成的词云结果
   ```sql
   CREATE TABLE IF NOT EXISTS wordcloud_cache (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       type TEXT,                        -- 缓存类型(wordcloud/author/thread)
       data TEXT NOT NULL,               -- 词云数据(JSON格式)
       created_at TEXT DEFAULT CURRENT_TIMESTAMP, -- 创建时间
       version INTEGER DEFAULT 1         -- 版本号
   );
   ```

## 词云生成流程

### 1. 任务创建

当用户请求生成词云时，系统创建一个任务：

```python
def create_wordcloud_job(job_type, target_id):
    """创建词云生成任务"""
    conn = sqlite3.connect('backend/db/forum_data.db')
    cursor = conn.cursor()
    
    try:
        # 检查是否已有相同任务
        cursor.execute('''
        SELECT id, status FROM wordcloud_job 
        WHERE job_type = ? AND target_id = ? AND status IN ('pending', 'processing')
        ''', (job_type, target_id))
        
        existing_job = cursor.fetchone()
        
        if existing_job:
            job_id = existing_job[0]
            logger.info(f"已存在的{job_type}词云任务 (ID: {job_id}, 目标: {target_id})")
        else:
            # 创建新任务
            cursor.execute('''
            INSERT INTO wordcloud_job (job_type, target_id, status)
            VALUES (?, ?, 'pending')
            ''', (job_type, target_id))
            
            job_id = cursor.lastrowid
            logger.info(f"创建新的{job_type}词云任务 (ID: {job_id}, 目标: {target_id})")
        
        conn.commit()
        return job_id
    except Exception as e:
        logger.error(f"创建词云任务失败: {str(e)}")
        return None
    finally:
        conn.close()
```

### 2. 任务处理

系统定期检查并处理待处理的词云任务：

```python
def process_wordcloud_jobs(max_jobs=5):
    """处理待处理的词云任务"""
    conn = sqlite3.connect('backend/db/forum_data.db')
    cursor = conn.cursor()
    
    try:
        # 获取待处理任务
        cursor.execute('''
        SELECT id, job_type, target_id FROM wordcloud_job 
        WHERE status = 'pending'
        ORDER BY created_at ASC
        LIMIT ?
        ''', (max_jobs,))
        
        pending_jobs = cursor.fetchall()
        
        for job_id, job_type, target_id in pending_jobs:
            # 更新任务状态为处理中
            cursor.execute('''
            UPDATE wordcloud_job 
            SET status = 'processing', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (job_id,))
            conn.commit()
            
            try:
                # 根据任务类型生成词云
                if job_type == 'author':
                    result = generate_author_wordcloud(target_id)
                elif job_type == 'thread':
                    result = generate_thread_wordcloud(target_id)
                else:
                    raise ValueError(f"未知的任务类型: {job_type}")
                
                # 更新任务状态为已完成
                cursor.execute('''
                UPDATE wordcloud_job 
                SET status = 'completed', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (job_id,))
                
                logger.info(f"词云任务完成 (ID: {job_id}, 类型: {job_type}, 目标: {target_id})")
            except Exception as e:
                # 更新任务状态为失败
                cursor.execute('''
                UPDATE wordcloud_job 
                SET status = 'failed', error_message = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (str(e), job_id))
                
                logger.error(f"词云任务失败 (ID: {job_id}): {str(e)}")
            
            conn.commit()
    except Exception as e:
        logger.error(f"处理词云任务时出错: {str(e)}")
    finally:
        conn.close()
```

### 3. 作者词云生成

为特定作者生成词云：

```python
def generate_author_wordcloud(author_name):
    """为作者生成词云"""
    conn = sqlite3.connect('backend/db/forum_data.db')
    cursor = conn.cursor()
    
    try:
        # 获取作者的所有帖子内容
        cursor.execute('''
        SELECT content FROM post 
        WHERE author = ? AND content IS NOT NULL AND content != ''
        ''', (author_name,))
        
        posts = cursor.fetchall()
        
        if not posts:
            raise ValueError(f"未找到作者 '{author_name}' 的帖子内容")
        
        # 合并所有帖子内容
        all_content = ' '.join([post[0] for post in posts])
        
        # 生成词云
        image_path = _generate_wordcloud(all_content, f"author_{author_name}")
        
        # 统计词汇数量
        word_count = len(_count_words(all_content))
        
        # 更新词云缓存
        _update_wordcloud_cache('author', author_name, image_path, word_count)
        
        return image_path
    finally:
        conn.close()
```

### 4. 帖子词云生成

为特定帖子生成词云：

```python
def generate_thread_wordcloud(thread_id):
    """为帖子生成词云"""
    conn = sqlite3.connect('backend/db/forum_data.db')
    cursor = conn.cursor()
    
    try:
        # 获取帖子内容和回复
        cursor.execute('''
        SELECT content FROM post 
        WHERE thread_id = ? AND content IS NOT NULL AND content != ''
        ''', (thread_id,))
        
        posts = cursor.fetchall()
        
        if not posts:
            raise ValueError(f"未找到帖子 '{thread_id}' 的内容")
        
        # 合并所有内容
        all_content = ' '.join([post[0] for post in posts])
        
        # 生成词云
        image_path = _generate_wordcloud(all_content, f"thread_{thread_id}")
        
        # 统计词汇数量
        word_count = len(_count_words(all_content))
        
        # 更新词云缓存
        _update_wordcloud_cache('thread', thread_id, image_path, word_count)
        
        return image_path
    finally:
        conn.close()
```

### 5. 词云图片生成

核心词云生成函数：

```python
def _generate_wordcloud(text, name):
    """生成词云图片"""
    # 文本清洗
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    
    # 分词
    words = jieba.cut(text)
    
    # 过滤停用词
    stopwords = set(_load_stopwords())
    filtered_words = [word for word in words if word not in stopwords and len(word) > 1]
    
    # 统计词频
    word_freq = _count_words(' '.join(filtered_words))
    
    if not word_freq:
        raise ValueError("处理后的文本不包含有效词汇")
    
    # 确保目录存在
    if name.startswith('author_'):
        output_dir = 'data/wordcloud/author'
    else:
        output_dir = 'data/wordcloud/thread'
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成安全的文件名
    safe_name = re.sub(r'[^\w]', '_', name)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"{output_dir}/{safe_name}_{timestamp}.png"
    
    # 设置词云参数
    font_path = 'data/config/fonts/simhei.ttf'  # 确保字体文件存在
    wc = WordCloud(
        font_path=font_path,
        width=800,
        height=400,
        background_color='white',
        max_words=200,
        max_font_size=100,
        random_state=42
    )
    
    # 生成词云
    wc.generate_from_frequencies(word_freq)
    
    # 保存图片
    wc.to_file(output_path)
    
    return output_path
```

### 6. 词云缓存更新

更新词云缓存表：

```python
def _update_wordcloud_cache(cache_type, target_id, image_path, word_count):
    """更新词云缓存"""
    conn = sqlite3.connect('backend/db/forum_data.db')
    cursor = conn.cursor()
    
    try:
        # 检查是否已有缓存
        cursor.execute('''
        SELECT id FROM wordcloud_cache 
        WHERE cache_type = ? AND target_id = ?
        ''', (cache_type, target_id))
        
        existing_cache = cursor.fetchone()
        
        if existing_cache:
            # 更新现有缓存
            cursor.execute('''
            UPDATE wordcloud_cache 
            SET image_path = ?, word_count = ?, updated_at = CURRENT_TIMESTAMP
            WHERE cache_type = ? AND target_id = ?
            ''', (image_path, word_count, cache_type, target_id))
        else:
            # 创建新缓存
            cursor.execute('''
            INSERT INTO wordcloud_cache 
            (cache_type, target_id, image_path, word_count)
            VALUES (?, ?, ?, ?)
            ''', (cache_type, target_id, image_path, word_count))
        
        conn.commit()
    finally:
        conn.close()
```

## 词云任务管理

### 1. 定时任务处理

系统通过计划任务定期处理词云生成：

```powershell
# 每小时处理词云任务
$action = New-ScheduledTaskAction -Execute "python" -Argument "py/process_wordcloud.py"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 60)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "ProcessWordCloudJobs" -Action $action -Trigger $trigger -Settings $settings -Description "处理词云生成任务"
```

### 2. 清理过期任务

定期清理已完成的旧任务：

```python
def clean_old_wordcloud_jobs():
    """清理30天前已完成的词云任务"""
    conn = sqlite3.connect('backend/db/forum_data.db')
    cursor = conn.cursor()
    
    try:
        # 删除30天前已完成或失败的任务
        thirty_days_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        
        cursor.execute(f'''
        DELETE FROM wordcloud_job 
        WHERE status IN ('completed', 'failed') 
        AND updated_at < '{thirty_days_ago}'
        ''')
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        logger.info(f"已清理 {deleted_count} 个过期词云任务")
    finally:
        conn.close()
```

## 词云API接口

系统提供以下API接口用于词云功能：

### 1. 请求生成词云

```python
@app.route('/api/wordcloud/generate', methods=['POST'])
def request_wordcloud_generation():
    data = request.json
    
    if not data or 'type' not in data or 'target_id' not in data:
        return jsonify({'error': '缺少必要参数'}), 400
    
    job_type = data['type']  # 'author' 或 'thread'
    target_id = data['target_id']
    
    if job_type not in ['author', 'thread']:
        return jsonify({'error': '无效的词云类型'}), 400
    
    # 创建词云任务
    job_id = create_wordcloud_job(job_type, target_id)
    
    if job_id:
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': '词云生成任务已创建'
        })
    else:
        return jsonify({'error': '创建词云任务失败'}), 500
```

### 2. 获取词云状态

```python
@app.route('/api/wordcloud/status/<int:job_id>', methods=['GET'])
def get_wordcloud_status(job_id):
    conn = sqlite3.connect('backend/db/forum_data.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        SELECT job_type, target_id, status, error_message, created_at, updated_at
        FROM wordcloud_job 
        WHERE id = ?
        ''', (job_id,))
        
        job = cursor.fetchone()
        
        if not job:
            return jsonify({'error': '任务不存在'}), 404
        
        job_type, target_id, status, error_message, created_at, updated_at = job
        
        # 如果任务已完成，获取缓存信息
        image_path = None
        word_count = None
        
        if status == 'completed':
            cursor.execute('''
            SELECT image_path, word_count
            FROM wordcloud_cache 
            WHERE cache_type = ? AND target_id = ?
            ''', (job_type, target_id))
            
            cache = cursor.fetchone()
            if cache:
                image_path, word_count = cache
        
        return jsonify({
            'job_id': job_id,
            'job_type': job_type,
            'target_id': target_id,
            'status': status,
            'error_message': error_message,
            'created_at': created_at,
            'updated_at': updated_at,
            'image_path': image_path,
            'word_count': word_count
        })
    finally:
        conn.close()
```

### 3. 获取已缓存的词云

```python
@app.route('/api/wordcloud/cache/<cache_type>/<target_id>', methods=['GET'])
def get_wordcloud_cache(cache_type, target_id):
    if cache_type not in ['author', 'thread']:
        return jsonify({'error': '无效的词云类型'}), 400
    
    conn = sqlite3.connect('backend/db/forum_data.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        SELECT image_path, word_count, created_at, updated_at
        FROM wordcloud_cache 
        WHERE cache_type = ? AND target_id = ?
        ''', (cache_type, target_id))
        
        cache = cursor.fetchone()
        
        if not cache:
            # 如果缓存不存在，创建一个生成任务
            job_id = create_wordcloud_job(cache_type, target_id)
            
            return jsonify({
                'cache_exists': False,
                'job_created': True if job_id else False,
                'job_id': job_id
            })
        
        image_path, word_count, created_at, updated_at = cache
        
        return jsonify({
            'cache_exists': True,
            'cache_type': cache_type,
            'target_id': target_id,
            'image_path': image_path,
            'word_count': word_count,
            'created_at': created_at,
            'updated_at': updated_at
        })
    finally:
        conn.close()
```

## 相关文档

- [数据库概览](./db_overview.md)
- [数据表定义](./db_table_definitions.md)
- [增量数据更新](./db_incremental_updates.md)

## 词云在数据更新中的处理

在数据库更新过程中，系统确保词云表结构正确：

```python
# 在update_db.py中确保创建词云表
with sqlite3.connect(updater.temp_db_path) as conn:
    cursor = conn.cursor()
    # 确保词云表结构正确
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wordcloud_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        data TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        version INTEGER DEFAULT 1
    )
    """)
    logger.info("已确保词云表结构正确")

# 数据库更新后，生成新的词云数据
try:
    from generate_wordcloud import update_word_frequencies
    if update_word_frequencies():
        logger.info("成功生成词云数据")
    else:
        logger.warning("生成词云数据失败")
except Exception as e:
    logger.warning(f"生成词云数据过程中出错: {str(e)}")
```

词云生成模块会检查并确保表结构符合要求：

```python
def ensure_table_structure():
    """确保数据库表结构正确"""
    try:
        conn = sqlite3.connect(os.path.join("backend", "db", "forum_data.db"))
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wordcloud_cache'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # 检查表结构
            cursor.execute("PRAGMA table_info(wordcloud_cache)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # 检查是否包含必要的列
            required_columns = {'type', 'data', 'created_at', 'version'}
            missing_columns = required_columns - set(columns)
            
            if missing_columns:
                # 表结构不完整，需要重建
                cursor.execute("DROP TABLE IF EXISTS wordcloud_cache")
                table_exists = False
        
        if not table_exists:
            # 创建新表
            cursor.execute("""
                CREATE TABLE wordcloud_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    version INTEGER DEFAULT 1
                )
            """)
        
        conn.commit()
        conn.close()
        logger.info("数据库表结构已更新")
        return True
    except Exception as e:
        logger.error(f"更新数据库表结构时出错: {e}")
        return False
``` 