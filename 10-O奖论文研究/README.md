# 10 O 奖论文实证与 AI Use Report 模板

> 第二轮调研成果（2026-07-12）。核心样本：2024 年 C 题 O 奖论文（队伍 2406324，"Command the Flow"），全文经验证代理实际下载核验（**【已验证】**，3 票确认）。注意样本量为 1，"O 奖普遍如何"的推广要谨慎。

## 1. O 奖论文全文的获取渠道（重要事实先行）

- **官方不免费公开 O 奖论文全文**——"COMAP 已公开 2025 年 O 奖论文未删节版"的说法被 3 票**否决**（0-3）。官方渠道只有付费 UMAP Journal（且只刊摘要/选登）。
- 免费获取靠第三方流传：
  - **GitHub 镜像**（本轮实测可用）：https://reformship.github.io/pages/3competition/4mcm/MCM%20Outstanding/2024/C/2406324.pdf （2024 年 C 题 O 奖全文；该站还有其他年份/题目的合集，长期可用性无保证，**建议尽快下载存档**）
  - 知乎/公众号：搜"美赛 {年份} C题 O奖论文"（公众号「数学模型」「双愚」等，见 07）
  - GitHub 合集：`2004-2020 MCM/ICM Outstanding Papers`（老论文）

## 2. 样本拆解：2024 年 C 题 O 奖论文 2406324

**技术路线**（与"C 题标准工作流"完全吻合）：

```
数据清洗（Data Cleaning）
  → EDA（Data Overview）
  → EWMA 指数加权移动平均：量化"势头"
  → RNN / GRU / LSTM 时序模型比选（LSTM 为主力）
  → XGBoost：因子贡献分析（哪些因素驱动势头转折）
  → PCA + K-means 聚类 + 迁移学习：提升跨比赛泛化精度
  → SHAP 可解释性分析
  → 敏感性分析（Sensitivity Analysis，独立成章）
```

**对你们的直接启示**：
1. O 奖论文确实在用 ML/深度学习——"评委反 ML"是误读；评委反的是**无解释的黑箱**。这篇每一步都配了解释层（XGBoost 因子贡献、SHAP、敏感性分析）。
2. "比选"是套路：不是直接用 LSTM，而是 RNN/GRU/LSTM 对比后论证选择——展示的是判断力，不是调包能力。
3. 章节结构可直接当模板：Introduction → Assumptions → Data Cleaning → Data Overview → 分问建模 → Sensitivity Analysis → Strengths & Weaknesses → 给教练的 memo → References → AI Report。

**技术栈对应的 Python 库**（我的对应整理）：pandas / scikit-learn（PCA、K-means）/ xgboost / shap / PyTorch 或 Keras（LSTM，会用即可）。

## 3. AI Use Report 实战模板（本文件最值钱的部分）

该 O 奖论文在**第 25 页（正文最后一页）**设独立章节 **"10 Report on Use of AI"**，实际写法：

**格式**：工具名 + 版本 + 日期，然后逐条 Query 原文 + Output 全文。实例（原文摘录）：

```
OpenAI ChatGPT (Nov 5, 2023 version, ChatGPT-4)
Query1: Please briefly explain the common usages and main differences
        between RNN, GRU, LSTM
Output: <ChatGPT 的完整回答全文>

Query2: <关于加权平均滤波器的提问>
Output: <完整回答>

Anthropic Claude2 (Feb 2024 version)
Query: ...
Output: ...
```

**三个关键观察**：
1. **披露的是"用 AI 学概念"**（让 ChatGPT 讲解 RNN/GRU/LSTM 区别、滤波器原理），而非"让 AI 替我建模"——披露内容本身就展示了团队的主导地位；
2. **坦然披露不扣分**：这篇披露了 ChatGPT-4 和 Claude2 两个工具，照样拿 O 奖——不敢披露才是风险（DQ）；
3. 他们把 AI Report 放进 25 页内的写法（当年规则理解不一）如今已明确：**现行规则 AI Report 放正文后、不计页数**（见 02），你们可以写得更详尽。

**给你们的操作建议**：备赛期就用这个格式建 AI 交互台账（工具/版本/日期/Query/Output 五列），赛中直接导出成章节。

## 4. 遗留空白（待后续补）

- 2025/2026 年 C 题 O 奖论文的流传链接与其 AI Report 写法演变（AI 政策第 2、3 年，披露深度可能已升级）；
- UMAP Journal 45.4/46.4 评委评论全文（付费墙，见 08）；
- 2025 年 C 题 394 个 DQ 的原因构成（官方未公布）。
