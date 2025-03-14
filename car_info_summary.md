# 车辆信息提取结果总结

我们使用 SiliconFlow API 中的 deepseek-ai/DeepSeek-R1-Distill-Qwen-7B 模型从 Excel 文件中提取了车辆信息，以下是结果总结：

## 数据来源

- 文件路径：`data/raw/bbs_update_detail_20250307.xlsx`
- 处理字段：`title`, `tags`, `related_tags`, `content`
- 样本数量：前 3 条记录

## 提取结果

### 1. 2024年丰田 RAV4 HYBARD XSE

- **年份**：2024
- **品牌**：丰田
- **型号**：Rav4 HYBARD XSE
- **配置**：全新顶配
- **公里数**：找不到
- **价格**：3000以下（租金）

### 2. 2017年丰田普锐斯

- **年份**：2017
- **品牌**：丰田
- **型号**：普锐斯
- **配置**：无事故 车况好 一加仑跑50多迈超级省油
- **公里数**：6-10万英里
- **价格**：$15,000~$20,000

### 3. 普锐斯出租车

- **年份**：找不到
- **品牌**：丰田
- **型号**：普锐斯
- **配置**：混动
- **公里数**：10万 Mile以上
- **价格**：$6,000~$10,000

## 总结与分析

1. **模型表现**：
   - 基本能够从非结构化文本中提取关键信息
   - 对于品牌和型号准确率较高
   - 对于缺失信息能够明确标注"找不到"

2. **数据特点**：
   - 两辆租赁车辆，一辆出售车辆
   - 都是丰田品牌的车辆
   - 年份范围从找不到到2024年不等
   - 价格区间较大，从租金3000以下到售价$15,000~$20,000不等

3. **优化方向**：
   - 进一步细化价格和公里数的格式统一
   - 更精确地识别配置信息
   - 提高对租赁和销售车辆的区分能力 