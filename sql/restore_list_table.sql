-- 恢复list表
BEGIN TRANSACTION;

-- 如果updates表存在，从updates表创建list表
CREATE TABLE IF NOT EXISTS list AS 
SELECT * FROM updates WHERE 1=0;

-- 如果update_list表存在，从update_list表创建list表
-- CREATE TABLE IF NOT EXISTS list AS 
-- SELECT * FROM update_list WHERE 1=0;

-- 将数据从updates表复制到list表（如果需要）
INSERT INTO list SELECT * FROM updates;

-- 或者从update_list表复制数据（如果需要）
-- INSERT INTO list SELECT * FROM update_list;

COMMIT;
