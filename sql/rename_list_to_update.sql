-- 开始事务
BEGIN TRANSACTION;

-- 创建一个与list表结构相同的新表，但名称为update
CREATE TABLE update AS SELECT * FROM list;

-- 删除原来的list表
DROP TABLE list;

-- 提交事务
COMMIT;
