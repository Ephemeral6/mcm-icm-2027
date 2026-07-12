# AI Use Report 可直接套用模板

> 依据：COMAP《Use of AI Tools in COMAP Contests》（v102025，PDF 在本目录 `官方文件/`）+ 2024 年 C 题 O 奖论文 2406324 的实际写法（见 [10-O奖论文研究](../10-O奖论文研究/README.md)）。

## 1. 论文末尾的成品格式（照抄改内容即可）

放在 25 页正文之后（不计页数），LaTeX 中新起一节：

```latex
\section*{Report on Use of AI Tools}

\subsection*{OpenAI ChatGPT (Jan 2027 version, GPT-5)}

\textbf{Query 1:} Please briefly explain the common usages and main
differences between ARIMA and LSTM for time series forecasting.

\textbf{Output:} <粘贴 AI 的完整回答，不删节>

\textbf{Query 2:} <第二次提问的原文>

\textbf{Output:} <完整回答>

\subsection*{Anthropic Claude (Jan 2027 version, Claude Fable 5)}

\textbf{Query 1:} <提问原文>

\textbf{Output:} <完整回答>

\subsection*{Translation}
We used DeepL (Jan 2027 version) to assist in translating portions of
our draft from Chinese to English.
% 翻译用途官方豁免：不必附完整输入，一句声明即可
```

同时别忘了正文里的**行内引用**：在用到 AI 帮助的位置标注，参考文献列出条目，格式如：
`OpenAI ChatGPT (Jan 15, 2027 version, GPT-5), https://chat.openai.com/`

## 2. 备赛期就要建的 AI 交互台账（共享表格，五列）

| 日期 | 工具+版本 | Query 原文 | Output 摘要（全文存档链接） | 用在论文哪里 |
|---|---|---|---|---|
| 2027-01-29 | ChatGPT GPT-5 | "解释 ARIMA 和 LSTM 的区别…" | 概念讲解（链接） | §4.1 模型选择依据 |

纪律：
- **当场记录**，赛后凭记忆补写几乎不可能且有遗漏风险（遗漏=未披露=DQ 风险）；
- Output 要存**全文**（官方要求 complete output），台账里放摘要+指向全文存档的链接；
- 指定专人负责（建议 AI 工程师本人，见 [04-三人分工](../04-三人分工/README.md)）。

## 3. 披露内容的"体面写法"（来自 O 奖论文的观察)

O 奖论文披露的用法都属于"AI 当老师/助手"，而非"AI 替我做题"：
- ✅ 让 AI 讲解模型概念、比较方法优劣（2406324 实例：RNN/GRU/LSTM 区别）
- ✅ 代码起草与 Debug 辅助
- ✅ 英文润色、翻译
- ⚠️ 谨慎披露且谨慎使用："AI 直接给出建模方案然后照抄"、"AI 解读结果直接进结论"——官方政策明文对这些用途持保留态度（政策 PDF 原文建议 caution），评委也反感（见 06）
- 核心姿态：披露内容本身应该能展示**团队掌握主导权**——AI 给了输入，判断和验证是你们做的

## 4. 提交前检查清单

- [ ] 正文每处 AI 协助都有行内引用
- [ ] 参考文献含 AI 工具条目（名称+日期+版本+模型）
- [ ] Report on Use of AI Tools 在正文之后、逐条 Query/Output 完整
- [ ] 翻译用途已声明（如有）
- [ ] 在线提交表单勾选 "Yes, AI report included"
- [ ] 正文（不含 AI Report）≤ 25 页
- [ ] AI 给过的参考文献已逐条人工核实存在
